#!/usr/bin/env bash
# OpenClaw Full Backup Script (Enhanced)
# Backs up: .openclaw configs + workspace repos
# Uploads to Google Drive with encryption

set -euo pipefail

CONFIG=/data/.config/rclone/rclone.conf
REMOTE="gdrive-backup:OpenClawBackups"
HOST=$(hostname -s)
TS=$(date -u +%Y%m%dT%H%M%SZ)
TMPDIR=/data/.openclaw/tmp-backup
OUTDIR=/data/.openclaw/backups
LOGDIR=/data/.openclaw/logs

mkdir -p "$TMPDIR" "$OUTDIR" "$LOGDIR" /data/.openclaw/credentials/backup
chmod 700 /data/.openclaw/credentials/backup

LOGFILE="$LOGDIR/openclaw-backup-$TS.log"
exec > >(tee -a "$LOGFILE") 2>&1

# Best-effort Slack alert via OpenClaw CLI
slack_alert() {
  local msg="$1"
  if command -v openclaw >/dev/null 2>&1; then
    openclaw message send --channel slack --target "user:U025H4Q9FPA" --message "$msg" >/dev/null 2>&1 || true
  fi
}

cleanup() { 
  rm -rf "$TMPDIR" >/dev/null 2>&1 || true 
}
trap cleanup EXIT

echo "=========================================="
echo "OpenClaw Full Backup - $TS"
echo "=========================================="

# Age keypair setup
AGE_IDENTITY=/data/.openclaw/credentials/backup/age.key
AGE_RECIPIENT=/data/.openclaw/credentials/backup/age.recipient
if [ ! -f "$AGE_IDENTITY" ] || [ ! -f "$AGE_RECIPIENT" ]; then
  echo "Generating new age keypair..."
  age-keygen -o "$AGE_IDENTITY" >/dev/null
  chmod 600 "$AGE_IDENTITY"
  age-keygen -y "$AGE_IDENTITY" > "$AGE_RECIPIENT"
  chmod 600 "$AGE_RECIPIENT"
fi

run_or_alert() {
  local step="$1"; shift
  echo "[STEP] $step..."
  if ! "$@"; then
    slack_alert "[OpenClaw Backup] FAILED at ${step} on ${HOST} (UTC ${TS}). Check logs: $LOGFILE"
    echo "[ERROR] Failed at $step"
    exit 1
  fi
}

# ==========================================
# PART 1: Backup .openclaw configs
# ==========================================
echo ""
echo "📦 Part 1: Backing up .openclaw configs..."

OPENCLAW_BASE="openclaw-${HOST}-${TS}"
OPENCLAW_TAR="$TMPDIR/${OPENCLAW_BASE}.tar"
OPENCLAW_ZST="$TMPDIR/${OPENCLAW_BASE}.tar.zst"
OPENCLAW_ENC="$OUTDIR/${OPENCLAW_BASE}.tar.zst.age"

# Exclude big/noisy dirs
EXCLUDES=(
  --exclude="./logs/**"
  --exclude="./media/**"
  --exclude="./dashboard-v4/**"
  --exclude="./backups/**"
  --exclude="./tmp-backup/**"
  --exclude="./node_modules/**"
)

run_or_alert "tar_openclaw" tar -C /data/.openclaw -cf "$OPENCLAW_TAR" "${EXCLUDES[@]}" .
run_or_alert "zstd_openclaw" zstd -q -T0 -19 -o "$OPENCLAW_ZST" "$OPENCLAW_TAR"
rm -f "$OPENCLAW_TAR"
run_or_alert "age_openclaw" age -R "$AGE_RECIPIENT" -o "$OPENCLAW_ENC" "$OPENCLAW_ZST"
rm -f "$OPENCLAW_ZST"

# ==========================================
# PART 2: Backup workspace repos
# ==========================================
echo ""
echo "📦 Part 2: Backing up workspace repos..."

WORKSPACE_BASE="workspace-${HOST}-${TS}"
WORKSPACE_TAR="$TMPDIR/${WORKSPACE_BASE}.tar"
WORKSPACE_ZST="$TMPDIR/${WORKSPACE_BASE}.tar.zst"
WORKSPACE_ENC="$OUTDIR/${WORKSPACE_BASE}.tar.zst.age"

# Create temp workspace structure
mkdir -p "$TMPDIR/workspace-backup"

# Copy essential workspace content (excluding node_modules, .git objects, etc.)
run_or_alert "copy_workspace" rsync -a --delete \
  --exclude="node_modules" \
  --exclude=".git/objects" \
  --exclude=".git/logs" \
  --exclude="*.log" \
  --exclude="tmp" \
  --exclude="temp" \
  /data/workspace/ "$TMPDIR/workspace-backup/"

# Create tar
run_or_alert "tar_workspace" tar -C "$TMPDIR" -cf "$WORKSPACE_TAR" workspace-backup/
run_or_alert "zstd_workspace" zstd -q -T0 -19 -o "$WORKSPACE_ZST" "$WORKSPACE_TAR"
rm -f "$WORKSPACE_TAR"
run_or_alert "age_workspace" age -R "$AGE_RECIPIENT" -o "$WORKSPACE_ENC" "$WORKSPACE_ZST"
rm -f "$WORKSPACE_ZST"

# ==========================================
# PART 3: Upload to Google Drive
# ==========================================
echo ""
echo "☁️  Part 3: Uploading to Google Drive..."

run_or_alert "rclone_mkdir" rclone mkdir "$REMOTE/${HOST}" --config "$CONFIG"
run_or_alert "rclone_upload_openclaw" rclone copyto "$OPENCLAW_ENC" "$REMOTE/${HOST}/$(basename "$OPENCLAW_ENC")" --config "$CONFIG" --checksum --transfers 4 --checkers 8
run_or_alert "rclone_upload_workspace" rclone copyto "$WORKSPACE_ENC" "$REMOTE/${HOST}/$(basename "$WORKSPACE_ENC")" --config "$CONFIG" --checksum --transfers 4 --checkers 8

# ==========================================
# PART 4: Cleanup old backups
# ==========================================
echo ""
echo "🧹 Part 4: Cleaning up old backups..."

# Remote retention: 14 days
rclone delete "$REMOTE/${HOST}" --min-age 336h --config "$CONFIG" >/dev/null 2>&1 || true

# Local retention: 7 days
find "$OUTDIR" -type f -name "*.tar.zst.age" -mtime +7 -delete >/dev/null 2>&1 || true

# Log retention: 30 days
find "$LOGDIR" -type f -name "openclaw-backup-*.log" -mtime +30 -delete >/dev/null 2>&1 || true

# ==========================================
# Summary
# ==========================================
echo ""
echo "=========================================="
echo "✅ Backup Complete!"
echo "=========================================="
echo "Files uploaded:"
echo "  - $(basename "$OPENCLAW_ENC")"
echo "  - $(basename "$WORKSPACE_ENC")"
echo ""
echo "Sizes:"
du -h "$OPENCLAW_ENC" "$WORKSPACE_ENC" 2>/dev/null || true
echo ""
echo "Log: $LOGFILE"

# Send success notification
slack_alert "[OpenClaw Backup] ✅ Success on ${HOST} (UTC ${TS}). OpenClaw + Workspace repos backed up to Google Drive."

echo "Done."
