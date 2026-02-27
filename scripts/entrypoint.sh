#!/bin/sh
# OpenClaw Container Entrypoint
# Handles auto-restore from backup on container start

set -e

echo "=========================================="
echo "OpenClaw Container Starting..."
echo "=========================================="

# Ensure directories exist
mkdir -p /home/openclaw/.openclaw/workspace/agents
mkdir -p /home/openclaw/.openclaw/workspace/memory
mkdir -p /data/backups/openclaw

# Check for backup to restore
BACKUP_FILE="/data/backups/openclaw/latest.tar.gz"

if [ -f "$BACKUP_FILE" ]; then
    echo "Found backup: $BACKUP_FILE"
    echo "Restoring data..."
    
    # Extract backup to temp location first
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
    
    # Copy data files (preserve git-tracked configs)
    if [ -d "$TEMP_DIR/data/.openclaw/agents" ]; then
        cp -r "$TEMP_DIR/data/.openclaw/agents"/* /home/openclaw/.openclaw/workspace/agents/ 2>/dev/null || true
    fi
    
    if [ -d "$TEMP_DIR/data/.openclaw/memory" ]; then
        cp -r "$TEMP_DIR/data/.openclaw/memory"/* /home/openclaw/.openclaw/workspace/memory/ 2>/dev/null || true
    fi
    
    # Copy qmd (vector memory) if exists
    if [ -d "$TEMP_DIR/data/.openclaw/qmd" ]; then
        cp -r "$TEMP_DIR/data/.openclaw/qmd" /home/openclaw/.openclaw/ 2>/dev/null || true
    fi
    
    # Copy sessions if exists
    if [ -d "$TEMP_DIR/data/.openclaw/sessions" ]; then
        cp -r "$TEMP_DIR/data/.openclaw/sessions" /home/openclaw/.openclaw/ 2>/dev/null || true
    fi
    
    # Cleanup
    rm -rf "$TEMP_DIR"
    
    echo "Restore complete!"
else
    echo "No backup found at $BACKUP_FILE"
    echo "Starting with fresh data directory..."
fi

# Set proper ownership
chown -R openclaw:openclaw /home/openclaw/.openclaw

echo "=========================================="
echo "Starting OpenClaw Gateway..."
echo "=========================================="

# Execute the main command
exec "$@"
