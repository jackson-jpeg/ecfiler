#!/bin/bash
# EPA Public User Group application-window monitor (rewritten session 7,
# 2026-11-13, from the findings in docs/pacer-engagement-plan.md
# "Changes since July").
#
# The call expected around Aug 2026 has not gone out; the current members'
# terms end 2026-12-31, so a call is overdue rather than missed. In 2024
# uscourts.gov posted the call 17 days before PACER did, so the primary
# trigger is the uscourts.gov news feed:
#
#   1. RSS: a NEW item on https://www.uscourts.gov/news/rss whose title says
#      "user group" (seen item links are remembered; first run only records).
#   2. Keyword: application language on the EPA Public User Group page.
#
# The old version also paged on any change to two whole pages: 22 alerts
# between July and September, every one noise. That trigger is gone.
#
# Quiet by design (Jackson, 2026-11-13: "one quiet alert path, no paging
# storms"). One path, ops-page at default priority, and every alert fires once,
# remembered in STATE_DIR:
#   - new user-group feed items: one page per run, however many items;
#   - application language on the group page: one page, ever;
#   - the monitor itself failing to fetch for 7 days: one page until it recovers;
#   - WATCH_UNTIL passed: one page saying the timer can be removed.
# A fetch failure on any one run logs and exits 1 (systemd shows it); it pages
# nobody.
#
# Installed 2026-11-13 as an approved exception to the VPS retired list
# (/root/CLAUDE.md). Units: deploy/systemd/ecfiler-epa-monitor.{service,timer};
# install steps in deploy/systemd/README-epa-monitor.md.
#
# Run once:  bash scripts/epa-window-monitor.sh
# Test:      bash scripts/epa-window-monitor.sh --test   (fixtures, a temp state
#            dir, pages nothing; exits 1 if any once-only rule is broken)
set -uo pipefail

STATE_DIR="${EPA_STATE_DIR:-/var/lib/ecfiler-epa-monitor}"
WATCH_UNTIL="${EPA_WATCH_UNTIL:-2027-03-31}"
UA="ecfiler-epa-monitor/2.0 (+https://github.com/jackson-jpeg/ecfiler)"
FEED="https://www.uscourts.gov/news/rss"
GROUP_PAGE="https://www.uscourts.gov/court-records/electronic-public-access-public-user-group"
KEYWORDS=("accepting applications" "application period" "apply by" "applications are due"
          "submit an application" "call for applications" "now open")

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*"; }

PAGES=0
page() { # page <tag> <title> <body>   (one path, default priority)
  PAGES=$((PAGES + 1))
  if [ "${MODE:-}" = "test" ]; then
    log "TEST would page [$1]: $2"
    return 0
  fi
  ops-page --tag "$1" "$2" "$3"
}

once() { # once <flag-name>: true the first time only, then remembers it
  local f="$STATE_DIR/fired-$1"
  [ -e "$f" ] && return 1
  date -u +%FT%TZ > "$f"
}

rss_titles() { # stdin: RSS XML -> "link<TAB>title" per item
  python3 -I -c '
import sys, xml.etree.ElementTree as ET
root = ET.fromstring(sys.stdin.read())
for it in root.iter("item"):
    t = (it.findtext("title") or "").strip().replace("\t", " ")
    l = (it.findtext("link") or it.findtext("guid") or t).strip()
    print(f"{l}\t{t}")'
}

check_feed() { # check_feed <xml>: one page per run for all new user-group items
  local seen="$STATE_DIR/rss-seen.txt" first=0 found=""
  [ -f "$seen" ] || { first=1; : > "$seen"; }
  while IFS=$'\t' read -r link title; do
    [ -n "$link" ] || continue
    grep -qxF "$link" "$seen" && continue
    echo "$link" >> "$seen"
    if [ "$first" = "0" ] && printf '%s' "$title" | grep -qi "user group"; then
      found+="$title  $link"$'\n'
    fi
  done < <(printf '%s' "$1" | rss_titles)
  [ "$first" = "1" ] && log "feed: first run, recorded $(wc -l < "$seen") items, no alerts"
  if [ -n "$found" ]; then
    page "epa-rss" "EPA Public User Group: new uscourts.gov item" "$found"
    log "feed: $(printf '%s' "$found" | grep -c .) new user-group item(s), one page"
  else
    log "feed: 0 new user-group items"
  fi
}

check_group_page() { # check_group_page <html>: one page, ever
  local text kw
  text=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  for kw in "${KEYWORDS[@]}"; do
    if printf '%s' "$text" | grep -qF "$kw"; then
      if once group-keyword; then
        page "epa-group-keyword" "EPA Public User Group page: \"$kw\"" "$GROUP_PAGE"
        log "group page: keyword '$kw', paged once"
      else
        log "group page: keyword '$kw' (already paged on $(cat "$STATE_DIR/fired-group-keyword"))"
      fi
      return 0
    fi
  done
  log "group page: no application language"
}

fetch_failed() { # fetch_failed <what>: log; page once if nothing has worked for 7 days
  log "$1 fetch failed"
  local ok="$STATE_DIR/last-ok" age
  [ -f "$ok" ] || date -u +%s > "$ok"   # first run ever: start the clock now
  age=$(( ($(date -u +%s) - $(cat "$ok")) / 86400 ))
  if [ "$age" -ge 7 ] && once stale; then
    page "epa-monitor-stale" "EPA monitor: no successful check in $age days" \
      "uscourts.gov fetches have failed since $(date -u -d "@$(cat "$ok")" +%F). journalctl -u ecfiler-epa-monitor"
  fi
  return 1
}

main() {
  mkdir -p "$STATE_DIR"
  if [[ "$(date -u +%F)" > "$WATCH_UNTIL" ]]; then
    log "past WATCH_UNTIL=$WATCH_UNTIL; nothing to do"
    if once watch-ended; then
      page "epa-monitor-ended" "EPA monitor: watch ended ($WATCH_UNTIL)" \
        "Approved exception in /root/CLAUDE.md. Remove: systemctl disable --now ecfiler-epa-monitor.timer"
    fi
    return 0
  fi
  local xml html
  xml=$(curl -sS --fail --max-time 45 --retry 2 -A "$UA" "$FEED") || { fetch_failed feed; return 1; }
  html=$(curl -sS --fail --max-time 45 --retry 2 -A "$UA" "$GROUP_PAGE") || { fetch_failed "group page"; return 1; }
  date -u +%s > "$STATE_DIR/last-ok"
  rm -f "$STATE_DIR/fired-stale"          # recovered: a later outage may page once again
  check_feed "$xml"
  check_group_page "$html"
}

if [ "${1:-}" = "--test" ]; then
  MODE=test
  STATE_DIR=$(mktemp -d)
  trap 'rm -rf "$STATE_DIR"' EXIT
  bad=0
  expect() { # expect <pages> <label>
    if [ "$PAGES" = "$1" ]; then log "ok: $2 (pages so far $PAGES)"; else log "FAIL: $2: $PAGES pages, want $1"; bad=1; fi
  }
  item() { printf '<item><title>%s</title><link>%s</link></item>' "$1" "$2"; }
  base=$(item 'Judiciary budget update' https://x/1)
  check_feed "<rss><channel>$base</channel></rss>";                    expect 0 "first feed run records only"
  check_feed "<rss><channel>$base$(item 'Courts seek members for EPA Public User Group' https://x/2)$(item 'EPA user group: apply by Jan 31' https://x/3)</channel></rss>"
  expect 1 "two new items, one page"
  check_feed "<rss><channel>$base$(item 'Courts seek members for EPA Public User Group' https://x/2)</channel></rss>"
  expect 1 "seen items do not page again"
  check_group_page "<p>The group is now ACCEPTING APPLICATIONS through March.</p>"; expect 2 "keyword pages the first time"
  check_group_page "<p>Apply by March 1.</p>";                          expect 2 "keyword never pages twice"
  check_group_page "<p>2025-2026 Membership</p>";                      expect 2 "no keyword, no page"
  fetch_failed feed;                                                  expect 2 "one failed fetch pages nobody"
  echo $(( $(date -u +%s) - 8*86400 )) > "$STATE_DIR/last-ok"
  fetch_failed feed;                                                  expect 3 "7 days of failures page once"
  fetch_failed feed;                                                  expect 3 "and only once"
  WATCH_UNTIL=2000-01-01 main;                                        expect 4 "watch end pages once"
  WATCH_UNTIL=2000-01-01 main;                                        expect 4 "and only once"
  [ "$bad" = 0 ] && log "self-test passed" || log "self-test FAILED"
  exit "$bad"
fi

main
