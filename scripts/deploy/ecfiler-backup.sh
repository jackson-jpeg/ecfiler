#!/usr/bin/env bash
# Nightly ECFiler data backup: VPS → MacBook (offsite), keep 14 days both ends.
#
# SQLite files are copied with `sqlite3 .backup` (consistent snapshot even
# mid-write; the attestation log writes under BEGIN IMMEDIATE); the staged
# packages and archived documents are tarred alongside. Restore procedure and
# verification are in docs/hosting-topology.md.
set -euo pipefail

DATA_DIR="${ECFILER_DATA_DIR:-/var/lib/ecfiler}"
STAMP="$(date +%Y%m%d_%H%M%S)"
WORK="$(mktemp -d /tmp/ecfiler-backup.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/$STAMP"

for db in history.db waitlist.db; do
  if [ -f "$DATA_DIR/$db" ]; then
    sqlite3 "$DATA_DIR/$db" ".backup '$WORK/$STAMP/$db'"
  fi
done

for dir in staged documents receipts; do
  if [ -d "$DATA_DIR/$dir" ]; then
    tar -czf "$WORK/$STAMP/$dir.tar.gz" -C "$DATA_DIR" "$dir"
  fi
done

tar -czf "$WORK/ecfiler-backup-$STAMP.tar.gz" -C "$WORK" "$STAMP"

# Local copy (survives Mac being unreachable), then offsite push.
LOCAL_KEEP=/var/backups/ecfiler
mkdir -p "$LOCAL_KEEP"
cp "$WORK/ecfiler-backup-$STAMP.tar.gz" "$LOCAL_KEEP/"
ls -1t "$LOCAL_KEEP"/ecfiler-backup-*.tar.gz 2>/dev/null | tail -n +15 | xargs -r rm -f

if ssh -o ConnectTimeout=15 -o BatchMode=yes macbook "mkdir -p ~/ecfiler-backups" 2>/dev/null; then
  scp -q "$WORK/ecfiler-backup-$STAMP.tar.gz" "macbook:~/ecfiler-backups/"
  ssh macbook 'ls -1t ~/ecfiler-backups/ecfiler-backup-*.tar.gz 2>/dev/null | tail -n +15 | xargs rm -f' || true
  echo "backup $STAMP: local + offsite ok"
else
  echo "backup $STAMP: local ok, Mac unreachable (offsite skipped)" >&2
fi
