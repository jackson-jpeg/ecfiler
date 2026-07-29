#!/usr/bin/env bash
# [VPS] Verify the web build as an anonymous outsider.
#
# Builds the Next.js site, serves it on a scratch port, and runs
# tests/test_web_public_access.py against it with a fresh (cookieless)
# Playwright context. This is the check that would have caught session 3's
# /courts-behind-sign-in bug: no session, no cookie, no auth header.
#
# Usage: [VPS] bash scripts/deploy/verify-web-anon.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
PORT="${ECFILER_WEB_PORT:-3100}"

cd "$REPO/web"
# The Clerk edge middleware inlines its secret at build time; a placeholder
# is fine for anonymous verification (no session is ever verified).
export CLERK_SECRET_KEY="${CLERK_SECRET_KEY:-sk_test_placeholder_for_anon_verification}"
npm run build

npx next start -p "$PORT" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  curl -sf -o /dev/null "http://127.0.0.1:$PORT/tools" && break
  sleep 1
done

cd "$REPO"
ECFILER_WEB_URL="http://127.0.0.1:$PORT" \
  .venv/bin/python -m pytest tests/test_web_public_access.py -q
