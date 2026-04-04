#!/usr/bin/env bash
set -euo pipefail

CONFIG=/data/.config/rclone/rclone.conf
REMOTE="gdrive-backup:OpenClawBackups"
HOST=$(hostname -s)
TS=$(date -u +%Y%m%dT%H%M%SZ)
TMPDIR=/data/.openclaw/tmp-backup
OUTDIR=/data/.openclaw/backups

# Best-effort Slack alert (DM Sean) via OpenClaw CLI if available.
slack_alert() {
  local msg="$1"
  if command -v openclaw >/dev/null 2>&1; then
    openclaw message send --channel slack --target "user:U025H4Q9FPA" --message "$msg" >/dev/null 2>&1 || true
  fi
}

cleanup() { rm -rf "$TMPDIR" >/dev/null 2>&1 || true; }
trap cleanup EXIT

mkdir -p "$TMPDIR" "$OUTDIR" /data/.openclaw/credentials/backup
chmod 700 /data/.openclaw/credentials/backup

# Exclude big/noisy dirs
EXCLUDES=(
  --exclude="./logs/**"
  --exclude="./media/**"
  --exclude="./dashboard-v4/**"
  --exclude="./backups/**"
  --exclude="./tmp-backup/**"
)

ARCHIVE_BASE="openclaw-${HOST}-${TS}"
TAR_PATH="$OUTDIR/${ARCHIVE_BASE}.tar"
ZST_PATH="$OUTDIR/${ARCHIVE_BASE}.tar.zst"
ENC_PATH="$OUTDIR/${ARCHIVE_BASE}.tar.zst.age"

# Age keypair (root-only). If the identity key is lost, backups are unrecoverable.
AGE_IDENTITY=/data/.openclaw/credentials/backup/age.key
AGE_RECIPIENT=/data/.openclaw/credentials/backup/age.recipient
if [ ! -f "$AGE_IDENTITY" ] || [ ! -f "$AGE_RECIPIENT" ]; then
  age-keygen -o "$AGE_IDENTITY" >/dev/null
  chmod 600 "$AGE_IDENTITY"
  age-keygen -y "$AGE_IDENTITY" > "$AGE_RECIPIENT"
  chmod 600 "$AGE_RECIPIENT"
fi

run_or_alert() {
  local step="$1"; shift
  if ! "$@"; then
    slack_alert "[OpenClaw Backup] FAILED at ${step} on ${HOST} (UTC ${TS}). Check logs on VPS."
    exit 1
  fi
}

# 0) Ensure remote host folder exists
run_or_alert "rclone_mkdir" rclone mkdir "$REMOTE/${HOST}" --config "$CONFIG"

# 1) Create tar from /data/.openclaw
run_or_alert "tar" tar -C /data/.openclaw -cf "$TAR_PATH" "${EXCLUDES[@]}" .

# 2) Compress
run_or_alert "zstd" zstd -q -T0 -19 -o "$ZST_PATH" "$TAR_PATH"
rm -f "$TAR_PATH"

# 3) Encrypt (age, non-interactive)
run_or_alert "age_encrypt" age -R "$AGE_RECIPIENT" -o "$ENC_PATH" "$ZST_PATH"
rm -f "$ZST_PATH"

# 4) Upload
run_or_alert "rclone_upload" rclone copyto "$ENC_PATH" "$REMOTE/${HOST}/$(basename "$ENC_PATH")" --config "$CONFIG" --checksum --transfers 4 --checkers 8

# 5) Retention: keep 7 days remote + local
rclone delete "$REMOTE/${HOST}" --min-age 168h --config "$CONFIG" >/dev/null 2>&1 || true
find "$OUTDIR" -type f -name "openclaw-${HOST}-*.age" -mtime +7 -delete >/dev/null 2>&1 || true

echo "OK: uploaded $(basename "$ENC_PATH")"
