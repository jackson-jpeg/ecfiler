#!/usr/bin/env bash
# [MAC] Production smoke — the check that closes a session.
#
# Hits www.ecfiler.com cookieless from outside the serving infrastructure
# and asserts what an anonymous visitor actually gets:
#
#   1. production serves the commit at HEAD of origin/master (via the
#      ecfiler-commit meta tag baked at build time);
#   2. every advertised free tool renders without an auth bounce;
#   3. the court numbers on /federal-courts match web/lib/data/*.json;
#   4. no phrase the copy lint bans (the register's FALSE-claim purge list)
#      appears in any served page;
#   5. ASPIRATIONAL claims appear only with their "Coming Soon" labeling.
#
# tests/test_web_public_access.py proves a *local build*; session 3 shipped
# a stale production while its local checks were green. This script is the
# outsider's view and is the one that counts. Runs anywhere with curl,
# python3, and git — label commands [MAC] or [VPS] when quoting runs.
#
# Usage: [MAC] bash scripts/verify-production.sh [https://www.ecfiler.com]
set -u

BASE="${1:-https://www.ecfiler.com}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
UA="ecfiler-production-smoke (scripts/verify-production.sh)"

declare -a RESULTS=()
FAILED=0
record() {
  RESULTS+=("$1|$2|${3:-}")
  if [ "$1" = "FAIL" ]; then FAILED=1; fi
}

fetch() { # fetch <path> — cookieless GET, follows no redirects
  curl -sS --max-time 20 -A "$UA" "$BASE$1"
}

echo "== Production smoke: $BASE =="

# -- 1. Commit identity -------------------------------------------------------
MASTER_SHA=$(git -C "$REPO" ls-remote origin master 2>/dev/null | cut -f1)
[ -n "$MASTER_SHA" ] || MASTER_SHA=$(git -C "$REPO" rev-parse master 2>/dev/null)
HOME_HTML=$(fetch /)
SERVED_SHA=$(printf '%s' "$HOME_HTML" | python3 -c "
import re, sys
m = re.search(r'name=\"ecfiler-commit\" content=\"([^\"]+)\"', sys.stdin.read())
print(m.group(1) if m else '')")

if [ -z "$SERVED_SHA" ]; then
  record FAIL "commit meta tag present" "no ecfiler-commit meta tag — pre-pipeline build still live"
elif [ "$SERVED_SHA" = "dev" ]; then
  record FAIL "commit identity" "meta says 'dev' — enable 'Automatically expose System Environment Variables' in the Vercel project settings and redeploy"
elif [ "$SERVED_SHA" = "$MASTER_SHA" ]; then
  record PASS "production serves master HEAD" "${SERVED_SHA:0:12}"
else
  record FAIL "production serves master HEAD" "serves ${SERVED_SHA:0:12}, master is ${MASTER_SHA:0:12}"
fi

# -- 2. Free tools reachable anonymously -------------------------------------
for path in /tools /events /fees /redaction /courts /certificate /validate /federal-courts; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 -A "$UA" "$BASE$path")
  if [ "$code" = "200" ]; then
    record PASS "anonymous GET $path" "200"
  else
    record FAIL "anonymous GET $path" "got $code"
  fi
done

# -- 3. Court numbers match the shipped data ---------------------------------
result=$(fetch /federal-courts | python3 -c "
import json, re, sys
from html import unescape
from pathlib import Path
data = Path('$REPO') / 'web' / 'lib' / 'data'
total = sum(
    len(json.loads((data / f'{n}_courts.json').read_text()))
    for n in ('district', 'bankruptcy', 'appellate')
)
text = re.sub(r'<[^>]+>', ' ', unescape(sys.stdin.read()))
m = re.search(r'(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)', text)
if not m:
    print('FAIL|court decomposition on /federal-courts|sentence not found')
else:
    parts = [int(x) for x in m.groups()]
    ok = sum(parts[:5]) == parts[5] == total
    print(('PASS|' if ok else 'FAIL|') + 'court numbers match courts-data|'
          + f'sums to {parts[5]}, data total {total}')
")
IFS='|' read -r state label detail <<<"$result"
record "$state" "$label" "$detail"

# -- 4. No purged claim reappears; 5. ASPIRATIONAL stays labeled -------------
# The forbidden list is the copy-lint purge list (tests/test_copy_lint.py)
# plus the demo-honesty markers; every entry is a claim the register records
# as deleted-for-falsity.
PAGES="/ /tools /federal-courts /what-is-cmecf /privacy /terms"
for path in $PAGES; do
  bad=$(fetch "$path" | python3 -c "
import sys
html = sys.stdin.read().lower()
forbidden = [
    '3-pass', '3 safety passes', 'three safety passes', 'stripe billing',
    'checkout via stripe', 'hosted cm/ecf filing', 'last updated: march 2026',
    'min saved per filing', 'cancel anytime', 'aes-256',
    'automated cm/ecf filing', 'automated cm/ecf submission',
    'encrypted server-side', 'decrypted at the moment of filing',
    'live demo', 'automatically files your documents',
]
print(';'.join(p for p in forbidden if p in html))
")
  if [ -n "$bad" ]; then
    record FAIL "no purged claims on $path" "$bad"
  else
    record PASS "no purged claims on $path"
  fi
done

home_lower=$(printf '%s' "$HOME_HTML" | tr '[:upper:]' '[:lower:]')
if printf '%s' "$home_lower" | grep -q "scripted demo"; then
  record PASS "walkthrough labeled scripted"
else
  record FAIL "walkthrough labeled scripted" "'scripted demo' missing from homepage"
fi
if printf '%s' "$home_lower" | grep -q "team management"; then
  if printf '%s' "$home_lower" | grep -q "coming soon"; then
    record PASS "aspirational Pro claims carry Coming Soon label"
  else
    record FAIL "aspirational Pro claims carry Coming Soon label" "'team management' without 'coming soon'"
  fi
fi

# -- Results -----------------------------------------------------------------
echo
printf '%-6s %-44s %s\n' "STATE" "CHECK" "DETAIL"
for r in "${RESULTS[@]}"; do
  IFS='|' read -r state label detail <<<"$r"
  printf '%-6s %-44s %s\n' "$state" "$label" "$detail"
done
echo
if [ "$FAILED" = "0" ]; then
  echo "PRODUCTION VERIFIED — record the run in docs/verification-ledger.md."
else
  echo "PRODUCTION SMOKE FAILED — production and the repo disagree."
fi
exit "$FAILED"
