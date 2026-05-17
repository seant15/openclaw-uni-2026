# OpenClaw VPS Persistence Guide

## The Problem

When your VPS redeploys/restarts, you may lose:
- Session history (conversations)
- Agent configurations
- QMD embeddings (vector memory)
- Cron job definitions

## Why This Happens

Your current setup stores data in `/data/.openclaw` which is on a persistent disk (`/dev/sda1`). **However**, depending on your deployment method:

### If using Coolify/Docker:
- Container volumes may not be properly bound to host paths
- Environment variables might reset to defaults
- The `/data` mount might not be automatically reattached

### If using systemd/native:
- Service might start before `/data` is mounted
- Config files could be overwritten by deployment scripts

## Current Data Locations (Persistent)

| Data | Location | Persistent? |
|------|----------|-------------|
| Agent configs & sessions | `/data/.openclaw/agents/` | ✅ Yes (on /dev/sda1) |
| OpenClaw config | `/data/.openclaw/openclaw.json` | ✅ Yes |
| QMD embeddings | `/data/.openclaw/agents/*/qmd/` | ✅ Yes |
| Workspace files | `/data/workspace/` | ✅ Yes |
| Memory files | `/data/workspace/memory/` | ✅ Yes |

## Solution: Hybrid Approach

### 1. Pre-Deploy Backup (Automated)

Add to crontab (runs daily at 3 AM):
```bash
0 3 * * * /data/workspace/backup-openclaw.sh >> /var/log/openclaw-backup.log 2>&1
```

### 2. Post-Deploy Recovery

After VPS redeploy, run:
```bash
# Restore from latest backup
LATEST=$(ls -t /data/backups/openclaw/openclaw_backup_*.tar.gz | head -1)
tar -xzf "$LATEST" -C /

# Restart OpenClaw gateway
openclaw gateway restart
```

### 3. Git-Based Config Sync (Recommended)

Track your OpenClaw config in git:
```bash
cd /data/workspace
git add .openclaw/openclaw.json
# Add other critical configs
git commit -m "OpenClaw config backup"
git push
```

## Session Strategy (Now Implemented)

With QMD enabled, daily sessions work perfectly:

| Session Type | Reset Policy | Rationale |
|--------------|--------------|-----------|
| Direct messages | Daily at 4 AM | Clean slate each day |
| Slack threads | Daily at 4 AM | Task-specific, ephemeral |
| Group chats | Idle 2h | Ephemeral chatter |
| Short tasks | `/new` on demand | Use for one-off tasks |
| Long conversations | Stay in session | Multi-day projects |

**Memory persistence**: QMD vector search maintains long-term memory across sessions.

## Quick Commands

```bash
# Manual backup
/data/workspace/backup-openclaw.sh

# Start fresh session
/new

# Check session status
/status

# Compact current session
/compact

# Search memory across sessions
# (Automatic via QMD on every query)
```

## Migration to Localhost (If Needed)

If VPS persistence remains problematic:

1. **Export data**:
   ```bash
   tar -czf openclaw_export.tar.gz /data/.openclaw /data/workspace
   ```

2. **On localhost**:
   ```bash
   # Install OpenClaw
   npm install -g openclaw
   
   # Import data
   tar -xzf openclaw_export.tar.gz -C ~
   mv ~/data/.openclaw ~/.openclaw
   mv ~/data/workspace ~/openclaw-workspace
   ```

3. **Update config**:
   ```bash
   openclaw config set agents.defaults.workspace ~/openclaw-workspace
   ```

## Monitoring

Check backup health:
```bash
ls -lh /data/backups/openclaw/
df -h /data
```

---

**Summary**: Your data IS on persistent storage. The issue is likely deployment-specific. Use the backup script + git sync for peace of mind.
