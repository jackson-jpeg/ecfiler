#!/usr/bin/env bash
# [VPS] api.ecfiler.com activation — run once, after the DNS records are added.
#
# Collapses three HUMAN-QUEUE rows into one command:
#   1. waits for A/AAAA propagation of api.ecfiler.com,
#   2. runs non-interactive certbot + nginx reload,
#   3. folds ANTHROPIC_API_KEY into /etc/ecfiler/api.env and restarts the API,
#   4. verifies the result from outside the box (public DNS, public TLS —
#      not loopback) and prints a pass/fail table.
#
# Usage:
#   [VPS] ANTHROPIC_API_KEY=sk-ant-... bash scripts/deploy/activate-api.sh
#   [VPS] bash scripts/deploy/activate-api.sh          # skip the key drop
#   [VPS] bash scripts/deploy/activate-api.sh --verify-only
#       (skips DNS/certbot/key/restart; just runs the outside-in checks —
#        ECFILER_API_BASE overrides the target, used by the test suite)
#
# Prerequisite (the one step that needs a human, sandbox-blocked twice):
#   [MAC] vercel dns add ecfiler.com api A 187.77.218.14
#   [MAC] vercel dns add ecfiler.com api AAAA 2a02:4780:4:1c0b::1
set -uo pipefail

DOMAIN="api.ecfiler.com"
EXPECTED_A="187.77.218.14"
EXPECTED_AAAA="2a02:4780:4:1c0b::1"
ENV_FILE="/etc/ecfiler/api.env"
CERT_EMAIL="realjacksons@gmail.com"
DNS_TIMEOUT_S=900

declare -a RESULTS=()
FAILED=0

record() { # record <PASS|FAIL|SKIP> <label> [detail]
  RESULTS+=("$1|$2|${3:-}")
  if [ "$1" = "FAIL" ]; then FAILED=1; fi
}

json() { # json <field> — extract a field from stdin JSON
  python3 -c "import json,sys; print(json.load(sys.stdin).get('$1',''))" 2>/dev/null
}

VERIFY_ONLY=0
[ "${1:-}" = "--verify-only" ] && VERIFY_ONLY=1

if [ "$VERIFY_ONLY" = "0" ]; then
echo "== 1/4 DNS propagation =="
deadline=$(( $(date +%s) + DNS_TIMEOUT_S ))
while :; do
  a=$(dig +short @1.1.1.1 "$DOMAIN" A | tail -1)
  aaaa=$(dig +short @1.1.1.1 "$DOMAIN" AAAA | tail -1)
  [ "$a" = "$EXPECTED_A" ] && [ "$aaaa" = "$EXPECTED_AAAA" ] && break
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "DNS did not propagate within ${DNS_TIMEOUT_S}s (A='$a' AAAA='$aaaa')."
    echo "Add the records first:"
    echo "  [MAC] vercel dns add ecfiler.com api A $EXPECTED_A"
    echo "  [MAC] vercel dns add ecfiler.com api AAAA $EXPECTED_AAAA"
    exit 1
  fi
  echo "  waiting… (A='$a' AAAA='$aaaa')"; sleep 15
done
record PASS "DNS A/AAAA propagated" "$a / $aaaa"

echo "== 2/4 TLS (certbot) =="
if certbot certificates 2>/dev/null | grep -q "$DOMAIN"; then
  record PASS "certificate already present"
else
  if certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$CERT_EMAIL" --redirect; then
    record PASS "certbot issued certificate"
  else
    record FAIL "certbot" "see output above"
  fi
fi
nginx -t && systemctl reload nginx && record PASS "nginx reloaded" || record FAIL "nginx reload"

echo "== 3/4 ANTHROPIC_API_KEY =="
if grep -q "^ANTHROPIC_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  record PASS "API key already in $ENV_FILE"
elif [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  printf 'ANTHROPIC_API_KEY=%s\n' "$ANTHROPIC_API_KEY" >> "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  record PASS "API key written to $ENV_FILE"
else
  record SKIP "API key" "ANTHROPIC_API_KEY not provided — /api/file* stays 503"
fi
systemctl restart ecfiler-api && sleep 2 && record PASS "ecfiler-api restarted" || record FAIL "ecfiler-api restart"
fi  # VERIFY_ONLY

BASE="${ECFILER_API_BASE:-https://$DOMAIN}"
echo "== 4/4 Outside-in verification ($BASE) =="

health=$(curl -sS --max-time 15 "$BASE/api/health")
if [ "$(echo "$health" | json status)" = "ok" ] || echo "$health" | grep -q '"ok"'; then
  record PASS "health endpoint over TLS"
else
  record FAIL "health endpoint" "$health"
fi

if [ "$VERIFY_ONLY" = "0" ] && grep -q "^ANTHROPIC_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  if [ "$(echo "$health" | json has_api_key)" = "True" ]; then
    record PASS "health reports has_api_key"
  else
    record FAIL "has_api_key" "$health"
  fi
fi

courts=$(curl -sS --max-time 15 "$BASE/api/courts" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null)
if [ "$courts" = "207" ]; then
  record PASS "courts loaded" "207"
else
  record FAIL "courts count" "got '$courts', expected 207"
fi

code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 -X POST "$BASE/api/file" -F "document=@/etc/hostname;type=application/pdf")
[ "$code" = "401" ] && record PASS "unauth /api/file -> 401" || record FAIL "unauth /api/file" "got $code"

code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$BASE/api/export")
[ "$code" = "401" ] && record PASS "unauth /api/export -> 401" || record FAIL "unauth /api/export" "got $code"

marker="activation-check-$(date +%s)@ecfiler.com"
before=$(curl -sS --max-time 15 "$BASE/api/waitlist/count" | json count)
post=$(curl -sS --max-time 15 -X POST "$BASE/api/waitlist" -H 'Content-Type: application/json' -d "{\"email\":\"$marker\"}" | json status)
after=$(curl -sS --max-time 15 "$BASE/api/waitlist/count" | json count)
if [ "$post" = "ok" ] && [ -n "$after" ] && [ "$after" -gt "${before:-0}" ] 2>/dev/null; then
  record PASS "waitlist POST round-trip" "count $before -> $after"
else
  record FAIL "waitlist round-trip" "post='$post' count $before -> $after"
fi

badpdf=$(mktemp --suffix=.pdf)
printf '%%PDF-1.4\nthis is not a real pdf body' > "$badpdf"
verdict=$(curl -sS --max-time 30 -X POST "$BASE/api/validate" -F "document=@$badpdf;type=application/pdf" | json valid)
rm -f "$badpdf"
if [ "$verdict" = "False" ]; then
  record PASS "known-bad PDF rejected by /api/validate"
else
  record FAIL "/api/validate bad PDF" "valid='$verdict', expected False"
fi

echo
echo "== Results =="
printf '%-6s %-38s %s\n' "STATE" "CHECK" "DETAIL"
for r in "${RESULTS[@]}"; do
  IFS='|' read -r state label detail <<<"$r"
  printf '%-6s %-38s %s\n' "$state" "$label" "$detail"
done
echo
if [ "$FAILED" = "0" ]; then
  echo "api.ecfiler.com is live. Update HUMAN-QUEUE.md and docs/hosting-topology.md."
else
  echo "ACTIVATION INCOMPLETE — fix the FAIL rows above and re-run."
fi
exit "$FAILED"
