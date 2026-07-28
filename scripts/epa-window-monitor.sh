#!/bin/bash
# EPA Public User Group application-window monitor.
#
# The Electronic Public Access Public User Group opens applications for a short
# window (the last cycle ran about two weeks). A note in a markdown file gets
# missed; this polls the two pages that would announce it and emails on a hit.
#
# Two independent triggers, because either alone would be wrong:
#   1. Content diff — any change at all to the watched pages.
#   2. Keyword hit — application language appearing on either page.
# A keyword hit fires even if the diff is noisy from unrelated edits, and the
# diff catches an opening announced in wording the keyword list didn't predict.
#
# Install:  bash scripts/epa-window-monitor.sh --install
# Test:     bash scripts/epa-window-monitor.sh --test   (forces a positive)
# Run once: bash scripts/epa-window-monitor.sh
set -uo pipefail

STATE_DIR="${EPA_STATE_DIR:-/var/lib/ecfiler-epa-monitor}"
RECIPIENT="${EPA_ALERT_EMAIL:-realjacksons@gmail.com}"
UA="ECFiler-EPA-Monitor/1.0 (+https://github.com/jackson-jpeg/ecfiler; realjacksons@gmail.com)"

PAGES=(
  "https://pacer.uscourts.gov/announcements"
  "https://www.uscourts.gov/court-records/electronic-public-access-public-user-group"
)

# Language that would accompany an open window. Lowercased substring match.
KEYWORDS=(
  "accepting applications"
  "application period"
  "applications are now being accepted"
  "apply to serve"
  "call for applications"
  "nominations are open"
  "now accepting"
  "seeking applicants"
  "seeking members"
  "submit an application"
  "user group application"
)

mkdir -p "$STATE_DIR"

log() { printf '%s %s\n' "$(date -Is)" "$*"; }

# Strip markup and volatile cruft so the diff tracks prose, not build ids.
extract_text() {
  sed -e 's/<script[^>]*>.*<\/script>//g' \
      -e 's/<style[^>]*>.*<\/style>//g' \
      -e 's/<[^>]*>/ /g' \
      -e 's/&nbsp;/ /g' -e 's/&amp;/\&/g' -e 's/&#[0-9]*;//g' \
  | tr -s '[:space:]' ' ' \
  | sed -e 's/[0-9a-f]\{16,\}//g' \
        -e 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T[0-9:.+-]*//g'
}

# Deliver on every channel that works, not the first one that does. A missed
# EPA window costs a year; a duplicate alert costs nothing. The VPS has no MTA
# configured, so email fires only once an SMTP credential exists (msmtp/mail/
# sendmail, whichever is installed) — the dashboard and desktop channels work
# today and are what actually reach Jackson.
notify() {
  local subject="$1" body="$2" delivered=0

  if command -v msmtp >/dev/null 2>&1 && [ -f "$HOME/.msmtprc" ]; then
    printf 'To: %s\nSubject: %s\n\n%s\n' "$RECIPIENT" "$subject" "$body" \
      | msmtp "$RECIPIENT" 2>/dev/null && { delivered=1; log "delivered: email(msmtp)"; }
  elif command -v mail >/dev/null 2>&1; then
    printf '%s\n' "$body" | mail -s "$subject" "$RECIPIENT" 2>/dev/null \
      && { delivered=1; log "delivered: email(mail)"; }
  elif command -v sendmail >/dev/null 2>&1; then
    printf 'To: %s\nSubject: %s\n\n%s\n' "$RECIPIENT" "$subject" "$body" \
      | sendmail -t 2>/dev/null && { delivered=1; log "delivered: email(sendmail)"; }
  fi

  # Sanger dashboard notification (sang3r.com), service-token authenticated.
  # The route checks x-service-token against SANGER_API_SECRET.
  local tok="${SANGER_API_SECRET:-}"
  [ -z "$tok" ] && [ -f /root/.sanger-monitor.env ] && \
    tok=$(sed -n 's/^SANGER_SERVICE_TOKEN=//p' /root/.sanger-monitor.env | head -1)
  if [ -n "$tok" ]; then
    if curl -sS --max-time 20 -X POST https://sang3r.com/api/notifications \
        -H "Content-Type: application/json" \
        -H "x-service-token: $tok" \
        --data "$(python3 -c 'import json,sys; print(json.dumps({"type":"alert","title":sys.argv[1],"message":sys.argv[2],"metadata":{"source":"ecfiler-epa-monitor"}}))' "$subject" "$body")" \
        -o /dev/null -w '%{http_code}' 2>/dev/null | grep -q '^2'; then
      delivered=1; log "delivered: sanger-dashboard"
    fi
  fi

  # macOS desktop notification via the tunnel.
  if command -v mac >/dev/null 2>&1; then
    mac notify "$subject" >/dev/null 2>&1 && { delivered=1; log "delivered: mac-notify"; }
  fi

  # Always leave a durable local record, whatever else happened.
  mkdir -p "$STATE_DIR"
  printf '=== %s\n%s\n%s\n\n' "$(date -Is)" "$subject" "$body" >> "$STATE_DIR/alerts.log"

  if [ "$delivered" = 0 ]; then
    log "NO CHANNEL DELIVERED — alert recorded in $STATE_DIR/alerts.log only:"
    printf '%s\n%s\n' "$subject" "$body"
    return 1
  fi
  return 0
}

check_page() {
  local url="$1"
  local key; key=$(printf '%s' "$url" | md5sum | cut -c1-12)
  local snapshot="$STATE_DIR/$key.txt"
  local body text

  body=$(curl -sS --max-time 45 --retry 2 --retry-delay 5 -A "$UA" "$url" 2>/dev/null)
  if [ -z "$body" ]; then
    log "WARN unreachable: $url"
    return 0
  fi
  text=$(printf '%s' "$body" | extract_text)
  # --test appends application language to the fetched text so the keyword
  # path is exercised against a real fetch, not a hand-built fixture.
  [ -n "${EPA_TEST_INJECT:-}" ] && text="$text ${EPA_TEST_INJECT}"

  local hits=""
  local lower; lower=$(printf '%s' "$text" | tr '[:upper:]' '[:lower:]')
  for kw in "${KEYWORDS[@]}"; do
    case "$lower" in *"$kw"*) hits="$hits\n  - \"$kw\"" ;; esac
  done

  local changed=0
  if [ -f "$snapshot" ]; then
    if ! printf '%s' "$text" | diff -q "$snapshot" - >/dev/null 2>&1; then
      changed=1
    fi
  else
    log "baseline captured: $url"
  fi
  printf '%s' "$text" > "$snapshot"

  # Keyword hits alert every run while present; only a *new* keyword is news.
  local seen="$STATE_DIR/$key.keywords"
  local prev_hits=""; [ -f "$seen" ] && prev_hits=$(cat "$seen")
  printf '%s' "$hits" > "$seen"

  if [ -n "$hits" ] && [ "$hits" != "$prev_hits" ]; then
    notify "[ECFiler] EPA user-group application language detected" \
"Application-window language appeared on:

  $url

Matched:$(printf "$hits")

Next step: docs/outreach/c3-epa-application.md is submit-ready. Open the page,
confirm the window is genuinely open, and paste the prepared answers.

(Detected $(date -Is) by epa-window-monitor on the VPS.)"
    log "ALERT keyword $url"
  elif [ "$changed" = 1 ]; then
    notify "[ECFiler] EPA watch page changed" \
"The content changed on:

  $url

No application keywords matched, so this may be unrelated. Worth a look if the
window is expected soon (last cycle: ~2 weeks, expected ~Aug 2026).

(Detected $(date -Is) by epa-window-monitor on the VPS.)"
    log "ALERT diff $url"
  else
    log "no change: $url"
  fi
}

case "${1:-}" in
  --install)
    install -m 755 "$(readlink -f "$0")" /usr/local/bin/ecfiler-epa-monitor
    cat > /etc/systemd/system/ecfiler-epa-monitor.service <<'UNIT'
[Unit]
Description=ECFiler EPA user-group application window monitor
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/ecfiler-epa-monitor
UNIT
    cat > /etc/systemd/system/ecfiler-epa-monitor.timer <<'UNIT'
[Unit]
Description=Daily EPA application window check

[Timer]
OnCalendar=*-*-* 13:17:00
Persistent=true

[Install]
WantedBy=timers.target
UNIT
    systemctl daemon-reload
    systemctl enable --now ecfiler-epa-monitor.timer
    log "installed; next run:"
    systemctl list-timers ecfiler-epa-monitor.timer --no-pager
    ;;
  --test)
    # Force a positive against real fetches, proving detection AND delivery.
    # Two runs: the first establishes baselines so the diff path is quiet, the
    # second injects application language so the KEYWORD path is what fires.
    log "FORCED POSITIVE TEST"
    tmp_state=$(mktemp -d)
    log "  pass 1/2: capturing baselines (expect: no change)"
    EPA_STATE_DIR="$tmp_state" "$0" 2>&1 | sed 's/^/    /'
    log "  pass 2/2: injecting application language (expect: ALERT keyword)"
    EPA_STATE_DIR="$tmp_state" EPA_TEST_INJECT="The user group is now accepting applications." \
      "$0" 2>&1 | sed 's/^/    /'
    log "  alerts recorded: $(grep -c '^=== ' "$tmp_state/alerts.log" 2>/dev/null || echo 0)"
    rm -rf "$tmp_state"
    ;;
  *)
    for url in "${PAGES[@]}"; do check_page "$url"; done
    ;;
esac
