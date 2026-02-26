#!/bin/bash
# OpenClaw Restore Script
# Restores from latest backup or specified backup file

set -e

BACKUP_DIR="/data/backups/openclaw"

# Get backup file (argument or latest)
if [ -n "$1" ]; then
    BACKUP_FILE="$1"
else
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/openclaw_backup_*.tar.gz 2>/dev/null | head -1 || true)
fi

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ No backup found"
    echo "Usage: $0 [backup-file.tar.gz]"
    echo ""
    echo "Available backups:"
    ls -1 "$BACKUP_DIR"/openclaw_backup_*.tar.gz 2>/dev/null | xargs -n1 basename || echo "  (none)"
    exit 1
fi

echo "🔄 Restoring from: $(basename $BACKUP_FILE)"
echo "⚠️  This will overwrite current OpenClaw data"
read -p "Continue? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

# Stop OpenClaw if running
echo "🛑 Stopping OpenClaw..."
pkill -f "openclaw-gateway" 2>/dev/null || true
sleep 2

# Restore
echo "📦 Extracting backup..."
tar -xzf "$BACKUP_FILE" -C /

# Restart
echo "🚀 Restarting OpenClaw..."
openclaw gateway start &

echo "✅ Restore complete"
echo "   Gateway restarting..."
