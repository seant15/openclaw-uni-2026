#!/bin/bash
# init-security-hooks.sh
# Docker init script for OpenClaw container
# Starts the Context Hook Server in the background
# 
# Usage: Set OPENCLAW_DOCKER_INIT_SCRIPT=/app/scripts/init-security-hooks.sh in Coolify

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/context-hook-server.log"
PID_FILE="/var/run/context-hook-server.pid"

echo "[$(date -Iseconds)] Initializing security hooks..."

# Check if audit is enabled
if [[ "${SEC_CONTEXT_AUDIT_ENABLED:-true}" != "true" ]]; then
    echo "[$(date -Iseconds)] Context audit disabled via SEC_CONTEXT_AUDIT_ENABLED"
    exit 0
fi

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Check if server is already running
if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "[$(date -Iseconds)] Hook server already running (PID: $(cat "$PID_FILE"))"
    exit 0
fi

# Start the hook server
echo "[$(date -Iseconds)] Starting Context Hook Server..."
echo "[$(date -Iseconds)] Threshold: ${SEC_CONTEXT_AUDIT_THRESHOLD:-3500} tokens"
echo "[$(date -Iseconds)] Cooldown: ${SEC_CONTEXT_AUDIT_COOLDOWN_MIN:-60} minutes"

nohup node "$SCRIPT_DIR/context-hook-server.js" >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Wait a moment and verify it started
sleep 2
if kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "[$(date -Iseconds)] Hook server started successfully (PID: $SERVER_PID)"
    echo "[$(date -Iseconds)] Health check: http://localhost:33123/health"
else
    echo "[$(date -Iseconds)] ERROR: Hook server failed to start"
    echo "[$(date -Iseconds)] Check logs: $LOG_FILE"
    exit 1
fi

# Verify health endpoint
if command -v curl &> /dev/null; then
    HEALTH=$(curl -s http://localhost:33123/health || echo '{"status":"error"}')
    echo "[$(date -Iseconds)] Health response: $HEALTH"
fi

echo "[$(date -Iseconds)] Security hooks initialization complete"
