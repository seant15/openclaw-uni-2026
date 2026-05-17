#!/bin/bash

# Agent Persistence Backup Script

BACKUP_DIR="/data/agent_backups"
WORKSPACE_DIR="/data/workspace"
MEMORY_DIR="/data/workspace/memory"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Timestamp for unique backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="agent_backup_$TIMESTAMP"

# Backup workspace
tar -czvf "$BACKUP_DIR/$BACKUP_NAME_workspace.tar.gz" "$WORKSPACE_DIR"

# Backup memory files
tar -czvf "$BACKUP_DIR/$BACKUP_NAME_memory.tar.gz" "$MEMORY_DIR"

# Optional: Keep only last 5 backups
cd "$BACKUP_DIR"
ls -t *_workspace.tar.gz | tail -n +6 | xargs -d '\n' rm
ls -t *_memory.tar.gz | tail -n +6 | xargs -d '\n' rm

echo "Backup completed: $BACKUP_NAME"