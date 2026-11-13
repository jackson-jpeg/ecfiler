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
# Alerts go through ops-page (the one paging path on the VPS), deduped by tag.
# Stops by itself after WATCH_UNTIL. NOT INSTALLED: the VPS timer was retired
# with ECFiler on 2026-09-24 and comes back only with Jackson's okay.
#
# Run once:  bash scripts/epa-window-monitor.sh
# Test:      bash scripts/epa-window-monitor.sh --test   (forces both triggers
#            against a fixture, pages nothing unless EPA_TEST_PAGE=1)
set -uo pipefail

STATE_DIR="${EPA_STATE_DIR:-/var/lib/ecfiler-epa-monitor}"
WATCH_UNTIL="${EPA_WATCH_UNTIL:-2027-03-31}"
UA="ecfiler-epa-monitor/2.0 (+https://github.com/jackson-jpeg/ecfiler)"
FEED="https://www.uscourts.gov/news/rss"
GROUP_PAGE="https://www.uscourts.gov/court-records/electronic-public-access-public-user-group"
KEYWORDS=("accepting applications" "application period" "apply by" "applications are due"
          "submit an application" "call for applications" "now open")

log() { printf '%s %s\n' "$(date -u +%FT%TZ)" "$*"; }

page() { # page <tag> <title> <body>
  if [ "${MODE:-}" = "test" ] && [ "${EPA_TEST_PAGE:-0}" != "1" ]; then
    log "TEST would page [$1]: $2"
    return 0
  fi
  ops-page --priority high --tag "$1" "$2" "$3"
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

check_feed() { # check_feed <xml>
  local seen="$STATE_DIR/rss-seen.txt" first=0 hits=0
  [ -f "$seen" ] || { first=1; : > "$seen"; }
  while IFS=$'\t' read -r link title; do
    [ -n "$link" ] || continue
    grep -qxF "$link" "$seen" && continue
    echo "$link" >> "$seen"
    if [ "$first" = "0" ] && printf '%s' "$title" | grep -qi "user group"; then
      hits=$((hits + 1))
      page "epa-rss-$(printf '%s' "$link" | md5sum | cut -c1-10)" \
        "EPA Public User Group: new uscourts.gov item" "$title  $link"
    fi
  done < <(printf '%s' "$1" | rss_titles)
  [ "$first" = "1" ] && log "feed: first run, recorded $(wc -l < "$seen") items, no alerts"
  log "feed: $hits new user-group item(s)"
}

check_group_page() { # check_group_page <html>
  local text kw
  text=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  for kw in "${KEYWORDS[@]}"; do
    if printf '%s' "$text" | grep -qF "$kw"; then
      page "epa-group-keyword" "EPA Public User Group page: \"$kw\"" "$GROUP_PAGE"
      log "group page: keyword hit '$kw'"
      return 0
    fi
  done
  log "group page: no application language"
}

main() {
  if [[ "$(date -u +%F)" > "$WATCH_UNTIL" ]]; then
    log "past WATCH_UNTIL=$WATCH_UNTIL; nothing to do (remove the timer)"
    return 0
  fi
  mkdir -p "$STATE_DIR"
  local xml html
  xml=$(curl -sS --fail --max-time 45 --retry 2 -A "$UA" "$FEED") || { log "feed fetch failed"; return 1; }
  html=$(curl -sS --fail --max-time 45 --retry 2 -A "$UA" "$GROUP_PAGE") || { log "group page fetch failed"; return 1; }
  check_feed "$xml"
  check_group_page "$html"
}

if [ "${1:-}" = "--test" ]; then
  MODE=test
  STATE_DIR=$(mktemp -d)
  trap 'rm -rf "$STATE_DIR"' EXIT
  item() { printf '<item><title>%s</title><link>%s</link></item>' "$1" "$2"; }
  base="<rss><channel>$(item 'Judiciary budget update' https://x/1)</channel></rss>"
  check_feed "$base"                                     # first run: records only
  check_feed "<rss><channel>$(item 'Judiciary budget update' https://x/1)$(item 'Courts seek members for EPA Public User Group' https://x/2)</channel></rss>"
  check_group_page "<p>The group is now ACCEPTING APPLICATIONS through March.</p>"
  check_group_page "<p>2025-2026 Membership</p>"
  exit 0
fi

main
