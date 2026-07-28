#!/usr/bin/env bash
# One-shot ECFiler setup for this VPS.
# Fixes the three things `ecfiler check` flags: Anthropic key, keyring backend,
# PDF/A tooling. Run:  bash scripts/setup-vps.sh
set -euo pipefail

cd /root/ecfiler
VENV=/root/ecfiler/.venv

echo "==> 1/4  Anthropic API key"
if [ -f /root/.sanger-monitor.env ]; then
  KEY=$(grep -E '^ANTHROPIC_API_KEY=' /root/.sanger-monitor.env | head -1 | cut -d= -f2- | tr -d '"'"'"'')
  if [ -n "$KEY" ]; then
    grep -q 'ANTHROPIC_API_KEY' /root/.bashrc || echo "export ANTHROPIC_API_KEY='$KEY'" >> /root/.bashrc
    export ANTHROPIC_API_KEY="$KEY"
    echo "    reused the key already on this box (added to ~/.bashrc)"
  fi
fi
[ -n "${ANTHROPIC_API_KEY:-}" ] || { echo "    !! no key found — export ANTHROPIC_API_KEY yourself"; }

echo "==> 2/4  keyring backend (Linux has none by default — this is why PACER auth fails)"
"$VENV/bin/pip" install -q keyrings.alt
mkdir -p /root/.config/python_keyring
cat > /root/.config/python_keyring/keyringrc.cfg <<'CFG'
[backend]
default-keyring=keyrings.alt.file.EncryptedKeyring
CFG
echo "    installed. EncryptedKeyring asks for a passphrase the first time."

echo "==> 3/4  PACER password -> keyring"
if [ -t 0 ]; then
  echo "    Typed here, straight into the keyring. Not logged, not stored by ECFiler."
  read -rsp "    PACER password for jmsanger: " PW; echo
  PW="$PW" "$VENV/bin/python" - <<'PY'
import os, keyring
keyring.set_password("ecfiler-pacer", "jmsanger", os.environ["PW"])
print("    stored for jmsanger")
PY
  unset PW
else
  echo "    SKIPPED (no terminal attached). Finish later with: ecfiler setup"
fi

echo "==> 4/4  PDF/A tooling (optional; only needed for scanned-PDF conversion)"
apt-get install -y -qq ghostscript tesseract-ocr >/dev/null 2>&1 && echo "    system deps ok" || echo "    skipped (apt failed — non-fatal)"
"$VENV/bin/pip" install -q 'ocrmypdf' 2>/dev/null && echo "    ocrmypdf ok" || echo "    skipped (non-fatal)"

echo
echo "==> verifying"
ECFILER_DEV_AUTH=1 "$VENV/bin/ecfiler" check
