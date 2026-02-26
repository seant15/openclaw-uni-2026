#!/bin/bash
# OpenClaw Backup Script
# Creates timestamped backups of all OpenClaw data

set -e

BACKUP_DIR="/data/backups/openclaw"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/openclaw_backup_$TIMESTAMP.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📦 Creating OpenClaw backup..."
echo "   Destination: $BACKUP_FILE"

# Create backup
tar -czf "$BACKUP_FILE" \
  -C /data \
  .openclaw/agents \
  .openclaw/openclaw.json \
  workspace/MEMORY.md \
  workspace/memory \
  workspace/agents \
  2>/dev/null || {
    echo "❌ Backup failed"
    exit 1
  }

# Create symlink to latest
ln -sf "$BACKUP_FILE" "$BACKUP_DIR/latest.tar.gz"

# Keep only last 10 backups
ls -t "$BACKUP_DIR"/openclaw_backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm -f

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/openclaw_backup_*.tar.gz 2>/dev/null | wc -l)

echo "✅ Backup complete"
echo "   Size: $BACKUP_SIZE"
echo "   Total backups: $BACKUP_COUNT"
