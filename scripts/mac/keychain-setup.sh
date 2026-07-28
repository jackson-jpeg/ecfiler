#!/bin/bash
# ECFiler macOS keychain bootstrap — run ON the Mac.
#
# Non-GUI sessions (SSH, cron, launchd) get a fresh macOS security session in
# which every keychain starts locked, so the login keychain is unusable there.
# Same problem the iOS signing pipeline solves with sanger-ci.keychain-db; we
# use the identical pattern with a dedicated, single-purpose keychain:
#
#   ~/Library/Keychains/ecfiler.keychain-db   holds only the PACER credential
#   ~/.ecfiler/keychain-pass (chmod 600)      its randomly generated password
#
# The PACER password is read from stdin (piped, never in argv or on disk).
#
# Usage:  printf '%s' "$PACER_PASSWORD" | bash keychain-setup.sh <pacer-username>
set -euo pipefail

USERNAME="${1:?usage: keychain-setup.sh <pacer-username>}"
KC="$HOME/Library/Keychains/ecfiler.keychain-db"
PASSFILE="$HOME/.ecfiler/keychain-pass"

mkdir -p "$HOME/.ecfiler"

# Create the dedicated keychain on first run.
if [ ! -f "$KC" ]; then
  umask 077
  openssl rand -hex 24 > "$PASSFILE"
  security create-keychain -p "$(cat "$PASSFILE")" "$KC"
  # No auto-lock timeout: survives long filing runs.
  security set-keychain-settings "$KC"
fi

[ -f "$PASSFILE" ] || { echo "missing $PASSFILE for existing keychain" >&2; exit 1; }
security unlock-keychain -p "$(cat "$PASSFILE")" "$KC"

# Make the keychain visible to keychain search (keyring reads search the list;
# writes can't target it directly — keyring ignores alternate keychains, #623).
# It must come FIRST: SecKeychainFindGenericPassword aborts with -25308 when it
# reaches a locked keychain, so the unlocked ecfiler keychain has to win before
# the search touches the locked login keychain. It holds a single item, so
# every other lookup falls through to login as before.
CUR=$(security list-keychains -d user | sed 's/[" ]//g' | { grep -v ecfiler.keychain-db || true; } | tr '\n' ' ')
# Never let the login keychain fall out of the search list.
case " $CUR " in
  *login.keychain*) ;;
  *) CUR="$HOME/Library/Keychains/login.keychain-db $CUR" ;;
esac
# shellcheck disable=SC2086
security list-keychains -d user -s "$KC" $CUR

# Store the credential. Delete-then-add rather than -U: updating an existing
# item rewrites its ACL, which needs GUI interaction; a fresh add with -A
# (reads exempt from per-app ACL prompts) does not.
PW=$(cat)
[ -n "$PW" ] || { echo "no password on stdin" >&2; exit 1; }
security delete-generic-password -a "$USERNAME" -s ecfiler-pacer "$KC" >/dev/null 2>&1 || true
security add-generic-password -a "$USERNAME" -s ecfiler-pacer -w "$PW" -A "$KC"
unset PW

# Verify the read path ecfiler actually uses.
"$HOME/ecfiler/.venv/bin/python" - "$USERNAME" <<'PY'
import sys, keyring
ok = bool(keyring.get_password("ecfiler-pacer", sys.argv[1]))
print("keyring backend:", type(keyring.get_keyring()).__name__)
print("credential readable:", ok)
sys.exit(0 if ok else 1)
PY
echo "keychain-setup: OK"
