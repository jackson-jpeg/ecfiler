#!/bin/bash
# [MAC] QA day, one command: `make qa-day [MODE=live] [STAGE=code]`.
#
# dry  — run the full staged→pull→file→NEF→attestation round trip against
#        the mock CM/ECF (the proof that everything below the QA account
#        works). Runs anywhere the venv exists, including the VPS.
# live — the real QA run. Refuses to start unless every precondition is
#        green; with a STAGE code it pulls the package and hands off to the
#        attended filing workflow (CONFIRM + YES gates stay human).
#
# Preconditions checked for live (each maps to a HUMAN-QUEUE row when red):
#   1. running on macOS with the repo at ~/ecfiler
#   2. PACER credential present in ecfiler.keychain-db and readable
#   3. headed Chromium profile exists with a live persisted session (--qa)
#   4. sandbox allow-rules present in .claude/settings.json (VPS sessions
#      drive these commands over the tunnel; without the rules the run
#      stalls at `session login` — see docs/nef-roundtrip-runbook.md)
#   5. receipts dir writable
#   6. attestation chain verifies
set -u

MODE="${1:-dry}"
STAGE="${2:-}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
ECFILER_MAC="$REPO/scripts/mac/ecfiler-mac"

FAILED=0
check() { # check <label> <command...>
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf 'PASS  %s\n' "$label"
  else
    printf 'FAIL  %s\n' "$label"
    FAILED=1
  fi
}

if [ "$MODE" = "dry" ]; then
  echo "== QA day dry run: mock-court NEF round trip =="
  cd "$REPO"
  exec .venv/bin/python -m pytest "tests/test_browser_e2e.py::TestStagedToNefRoundTrip" -q
fi

[ "$MODE" = "live" ] || { echo "usage: qa-day.sh [dry|live] [stage-code]" >&2; exit 2; }

echo "== QA day live preflight =="

check "running on macOS" test "$(uname)" = "Darwin"
check "repo venv present" test -x "$REPO/.venv/bin/ecfiler"

KC="$HOME/Library/Keychains/ecfiler.keychain-db"
check "ecfiler keychain exists" test -f "$KC"
check "keychain password file present" test -f "$HOME/.ecfiler/keychain-pass"
check "keychain unlocks" security unlock-keychain -p "$(cat "$HOME/.ecfiler/keychain-pass" 2>/dev/null)" "$KC"
check "PACER credential stored" security find-generic-password -s ecfiler-pacer "$KC"

check "Chromium profile exists" test -d "$HOME/.ecfiler/pacer-profile"
if "$ECFILER_MAC" session status --qa 2>/dev/null | grep -qi "live"; then
  printf 'PASS  persisted QA session is live\n'
else
  printf 'FAIL  persisted QA session is live (run: %s session login --qa)\n' "$ECFILER_MAC"
  FAILED=1
fi

check "sandbox allow-rules present" python3 - "$REPO/.claude/settings.json" <<'PY'
import json, sys
try:
    rules = json.load(open(sys.argv[1]))["permissions"]["allow"]
except Exception:
    sys.exit(1)
sys.exit(0 if any(r.startswith("Bash(ssh macbook") for r in rules) else 1)
PY

mkdir -p "$HOME/.ecfiler/receipts"
check "receipts dir writable" touch "$HOME/.ecfiler/receipts/.qa-day-probe"
rm -f "$HOME/.ecfiler/receipts/.qa-day-probe"

check "attestation chain verifies" "$ECFILER_MAC" audit verify

if [ "$FAILED" != "0" ]; then
  echo
  echo "PREFLIGHT RED — live run refused. Every FAIL above maps to a"
  echo "HUMAN-QUEUE row or a runbook step (docs/nef-roundtrip-runbook.md)."
  exit 1
fi

echo
echo "Preflight green."
if [ -z "$STAGE" ]; then
  echo "No STAGE code given. Stage a filing at www.ecfiler.com/file, then:"
  echo "  [MAC] make qa-day MODE=live STAGE=<code>"
  exit 0
fi

echo "== Pulling staged package $STAGE =="
"$ECFILER_MAC" stage-pull "$STAGE" || exit 1

echo "== Handing off to the attended filing workflow (CONFIRM + YES are yours) =="
"$ECFILER_MAC" || exit 1

echo "== Proof =="
"$ECFILER_MAC" audit verify
ls -la "$HOME/.ecfiler/receipts/" | tail -5
ls -la "$HOME/.ecfiler/traces/" 2>/dev/null | tail -3
echo
echo "Copy the receipt, audit output, and trace into docs/qa-roundtrip/ and"
echo "update docs/filing-topology.md §4 — its first bullet just stopped being true."
