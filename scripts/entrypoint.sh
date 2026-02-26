#!/bin/bash
# OpenClaw Entrypoint Script
# Runs before OpenClaw starts - handles backup restore on redeploy

set -e

echo "🦞 OpenClaw Gateway Startup"
echo "=========================="

# Check if we have a backup to restore
BACKUP_DIR="/data/backups/openclaw"
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/openclaw_backup_*.tar.gz 2>/dev/null | head -1 || true)

if [ -n "$LATEST_BACKUP" ] && [ -f "$LATEST_BACKUP" ]; then
    echo "📦 Found backup: $(basename $LATEST_BACKUP)"
    echo "🔄 Restoring..."
    
    # Extract backup to temp location first
    TMP_DIR=$(mktemp -d)
    tar -xzf "$LATEST_BACKUP" -C "$TMP_DIR"
    
    # Merge restored data with current (don't overwrite tracked configs)
    if [ -d "$TMP_DIR/data/.openclaw/agents" ]; then
        cp -r "$TMP_DIR"/data/.openclaw/agents/* /home/node/.openclaw/agents/ 2>/dev/null || true
    fi
    
    if [ -d "$TMP_DIR/data/workspace/memory" ]; then
        cp -r "$TMP_DIR"/data/workspace/memory/* /home/node/.openclaw/workspace/memory/ 2>/dev/null || true
    fi
    
    # Cleanup
    rm -rf "$TMP_DIR"
    echo "✅ Restore complete"
else
    echo "ℹ️  No backup found, starting fresh"
fi

# Ensure directories exist
mkdir -p /home/node/.openclaw/{agents,workspace/{agents,memory}}

# Set proper permissions
chown -R node:node /home/node/.openclaw

echo "🚀 Starting OpenClaw Gateway..."
exec "$@"
