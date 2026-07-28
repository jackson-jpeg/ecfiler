#!/usr/bin/env bash
# Run after a VPS reboot to verify everything came back. Exit 0 = all good.
# (Reboot survival is configured — units enabled, WantedBy=multi-user.target,
# crash-restart proven — but only an actual reboot proves the boot path.)
set -u

fail=0
check() {
  local desc="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "ok   $desc"
  else
    echo "FAIL $desc"
    fail=1
  fi
}

check "ecfiler-api active"        systemctl is-active --quiet ecfiler-api
check "ecfiler-backup.timer"      systemctl is-active --quiet ecfiler-backup.timer
check "ecfiler-compress.timer"    systemctl is-active --quiet ecfiler-compress.timer
check "nginx active"              systemctl is-active --quiet nginx
check "API health endpoint"       curl -sf --max-time 10 http://127.0.0.1:8001/api/health
check "API rejects unauth /file"  bash -c '[ "$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 -X POST http://127.0.0.1:8001/api/file)" = 401 ]'

# Everything else that was running before the reboot should be back too.
echo
echo "Other services not yet back (empty is good):"
systemctl list-units --type=service --state=failed --no-legend | sed 's/^/  /'

exit $fail
