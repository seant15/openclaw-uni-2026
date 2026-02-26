# OpenClaw Troubleshooting Guide

**For:** Future team members, DevOps, and emergency situations  
**When to use:** Something broke and you need to fix it fast  
**Start here:** Check `ARCHITECTURE.md` if you don't understand the system layout

---

## 🚨 Critical Issues (Fix First)

### 1. OpenClaw Completely Down

**Symptoms:**
- No responses in Slack
- `openclaw status` fails
- Gateway unreachable

**Quick Fix:**
```bash
cd /data/uni-openclaw-infra

# 1. Check if container is running
docker-compose ps

# 2. If not running, start it
docker-compose up -d

# 3. Check logs for errors
docker-compose logs --tail 100

# 4. If stuck, force restart
docker-compose down
docker-compose up -d
```

**Still down?** Check [Deep Diagnostics](#deep-diagnostics)

---

### 2. Lost All Data After Redeploy

**Symptoms:**
- Agents don't remember previous conversations
- MEMORY.md empty or missing
- Session history gone

**Immediate Action:**
```bash
# Check if backups exist
ls -lth /data/backups/openclaw/

# If backups exist, restore latest
cd /data/uni-openclaw-infra
./scripts/restore.sh

# If specific backup needed
./scripts/restore.sh /data/backups/openclaw/openclaw_backup_20260226_120000.tar.gz

# Restart to apply
docker-compose restart
```

**No backups?** Check if data exists elsewhere:
```bash
# Check persistent volume
ls -la /data/.openclaw/

# If data exists but not loaded, check volume mounts
docker inspect openclaw-gateway | grep -A20 Mounts
```

---

### 3. Can't Connect to Gateway

**Symptoms:**
- `openclaw status` hangs
- Browser can't access control UI
- Connection refused

**Diagnostic Steps:**
```bash
# 1. Check if process is listening
netstat -tlnp | grep 18789

# 2. Check container port mapping
docker port openclaw-gateway

# 3. Test locally
curl http://localhost:18789/status

# 4. Check firewall
ufw status
iptables -L | grep 18789
```

**Common Fixes:**
```bash
# Restart container
docker-compose restart

# If port conflict, kill existing process
lsof -ti:18789 | xargs kill -9
docker-compose up -d
```

---

## 🔧 Configuration Issues

### Config Changes Not Applied

**Symptoms:**
- Changed openclaw.json but behavior same
- New agents not showing up
- Old settings persist

**Root Cause:** Config cached or not reloaded

**Fix:**
```bash
# 1. Verify file was updated
cat /data/uni-openclaw-infra/config/openclaw.json | grep -A5 "your-change"

# 2. Restart container to reload
docker-compose restart

# 3. Verify inside container
docker exec openclaw-gateway cat /home/node/.openclaw/openclaw.json

# 4. Check gateway picked it up
openclaw status
```

**Git sync issues?**
```bash
# Force pull latest
cd /data/uni-openclaw-infra
git fetch origin
git reset --hard origin/main

# Then restart
docker-compose restart
```

---

### Environment Variables Not Working

**Symptoms:**
- API keys not recognized
- Slack not connecting
- Model falling back to wrong provider

**Diagnostic:**
```bash
# Check env vars in container
docker exec openclaw-gateway env | grep -i api

# Compare with Coolify dashboard
# Go to Coolify > Service > Environment Variables
```

**Fix:**
```bash
# If missing in container but set in Coolify:
# 1. Redeploy from Coolify UI
# 2. Or restart container
docker-compose down
docker-compose up -d
```

---

## 💬 Agent & Conversation Issues

### Agent Doesn't Remember Context

**Symptoms:**
- Asking same questions repeatedly
- No continuity from yesterday
- "As an AI, I don't have memory of..."

**Diagnostic:**
```bash
# 1. Check session state
openclaw sessions --json

# 2. Check if QMD working
ls -la /data/.openclaw/agents/clover/qmd/

# 3. Check memory files
ls -la /data/workspace/memory/
cat /data/workspace/MEMORY.md
```

**Fixes:**

If QMD not updating:
```bash
# Force QMD re-index
docker exec openclaw-gateway qmd update

# Or restart container
docker-compose restart
```

If sessions too long:
```bash
# Reset manually
# In chat, type: /new
```

If memory not loading:
```bash
# Check file permissions
ls -la /data/workspace/MEMORY.md

# Should be readable by container
chmod 644 /data/workspace/MEMORY.md
```

---

### Wrong Agent Responding

**Symptoms:**
- Asking Clover but Mary responds
- Agent behavior doesn't match personality
- Wrong model being used

**Diagnostic:**
```bash
# Check agent bindings
openclaw config get bindings

# Check current session agent
openclaw status | grep agent

# Check session file
cat /data/.openclaw/agents/clover/sessions/sessions.json
```

**Fix:**
```bash
# If wrong agent bound to channel, edit config
vim /data/uni-openclaw-infra/config/openclaw.json

# Then commit and push
git commit -am "Fix agent binding"
git push

# Or manually restart
docker-compose restart
```

---

### Session Not Resetting Daily

**Symptoms:**
- Same session ID for days
- Context growing too large
- No clean slate at 4 AM

**Diagnostic:**
```bash
# Check current session age
openclaw sessions --json | grep updatedAt

# Check timezone
date
cat /etc/timezone

# Check config
grep -A10 "resetByType" /data/.openclaw/openclaw.json
```

**Fix:**
```bash
# If config not loaded, restart
docker-compose restart

# If timezone wrong, set it
timedatectl set-timezone UTC

# Manual reset for now
# In chat: /new
```

---

## 🔐 Security & Auth Issues

### Gateway Token Invalid

**Symptoms:**
- "Unauthorized" errors
- Can't access control UI
- API calls rejected

**Fix:**
```bash
# 1. Check current token
openclaw config get gateway.auth.token

# 2. Generate new token
NEW_TOKEN=$(openssl rand -hex 32)
openclaw config set gateway.auth.token "$NEW_TOKEN"

# 3. Update Coolify env var
# Go to Coolify dashboard > Service > Environment
# Update OPENCLAW_GATEWAY_TOKEN

# 4. Redeploy
docker-compose down
docker-compose up -d
```

---

### Slack Integration Broken

**Symptoms:**
- Messages not received
- "Url verification failed" in Slack
- No responses in Slack channels

**Diagnostic:**
```bash
# Check webhook is accessible
curl -X POST http://your-vps/webhook/slack \
  -H "Content-Type: application/json" \
  -d '{"type":"url_verification","challenge":"test"}'

# Should return: {"challenge":"test"}
```

**Common Fixes:**

1. **Webhook URL wrong:**
   - Update in Slack app settings
   - Must match: `http://your-vps/webhook/slack`

2. **Signing secret incorrect:**
   ```bash
   # Verify in config
   openclaw config get channels.slack.signingSecret
   
   # Should match Slack app > Basic Info > Signing Secret
   ```

3. **Tokens expired:**
   - Regenerate in Slack app settings
   - Update in Coolify environment variables
   - Redeploy

---

## 💾 Backup & Restore Issues

### Backup Script Failing

**Symptoms:**
- No new backups in /data/backups/openclaw/
- Cron errors in /var/log/openclaw-backup.log
- Disk space issues

**Diagnostic:**
```bash
# Check disk space
df -h /data

# Check backup script manually
cd /data/uni-openclaw-infra
./scripts/backup.sh

# Check permissions
ls -la /data/backups/
```

**Fix:**
```bash
# Create directory if missing
mkdir -p /data/backups/openclaw

# Fix permissions
chmod +x /data/uni-openclaw-infra/scripts/*.sh

# Clean old backups manually if disk full
find /data/backups/openclaw -name "*.tar.gz" -mtime +7 -delete
```

---

### Restore Failing

**Symptoms:**
- `restore.sh` gives errors
- Data not restored after running
- Permission denied errors

**Diagnostic:**
```bash
# Check backup file integrity
tar -tzf /data/backups/openclaw/latest.tar.gz | head

# Check if backup exists
ls -la /data/backups/openclaw/
```

**Fix:**
```bash
# Stop container first
docker-compose down

# Manual restore
cd /
tar -xzf /data/backups/openclaw/latest.tar.gz

# Fix permissions
chown -R 1000:1000 /data/.openclaw

# Restart
cd /data/uni-openclaw-infra
docker-compose up -d
```

---

## 🔍 Deep Diagnostics

### Get Full System State

```bash
# 1. System overview
echo "=== SYSTEM ==="
uname -a
date
uptime

echo "=== DISK ==="
df -h
du -sh /data/.openclaw /data/backups

echo "=== CONTAINER ==="
docker ps -a | grep openclaw
docker stats --no-stream openclaw-gateway

echo "=== PROCESSES ==="
ps aux | grep openclaw

echo "=== PORTS ==="
netstat -tlnp | grep 18789

echo "=== LOGS (last 50) ==="
docker logs openclaw-gateway --tail 50

echo "=== CONFIG ==="
openclaw config get

echo "=== SESSIONS ==="
openclaw sessions --json

echo "=== BACKUPS ==="
ls -lth /data/backups/openclaw/ | head -5
```

---

### Network Connectivity Test

```bash
# Test outbound connections (APIs)
curl -s https://api.moonshot.cn/v1/models | head

# Test Slack connectivity
curl -s https://slack.com/api/api.test

# Check DNS resolution
nslookup api.moonshot.cn
```

---

### Container Debug Shell

```bash
# Get shell inside container
docker exec -it openclaw-gateway /bin/sh

# Inside container, check:
ls -la /home/node/.openclaw/
cat /home/node/.openclaw/openclaw.json
env | grep -i token
ps aux
```

---

## 🆘 Emergency Recovery

### Complete Rebuild from Scratch

**Use when:** Everything is broken and you need to start fresh

```bash
# 1. Stop everything
cd /data/uni-openclaw-infra
docker-compose down

# 2. Backup current state (just in case)
tar -czf /tmp/emergency-backup-$(date +%s).tar.gz /data/.openclaw /data/workspace

# 3. Clone fresh repo
rm -rf /data/uni-openclaw-infra
mkdir -p /data/uni-openclaw-infra
cd /data/uni-openclaw-infra
git clone https://github.com/YOUR_USERNAME/uni-openclaw-infra.git .

# 4. Restore data
./scripts/restore.sh

# 5. Start
chmod +x scripts/*.sh
docker-compose up -d

# 6. Verify
sleep 10
openclaw status
docker-compose ps
```

---

### Rollback to Previous Version

```bash
cd /data/uni-openclaw-infra

# Check git history
git log --oneline -10

# Rollback to specific commit
git checkout <commit-hash>

# Or rollback one step
git checkout HEAD~1

# Restart
docker-compose restart

# If working, commit the rollback
git checkout -b rollback-$(date +%Y%m%d)
git checkout main
git reset --hard <working-commit>
git push -f origin main  # Careful! Forces push
```

---

## 📞 Escalation Path

### Level 1: Self-Service (You)
- Check this troubleshooting guide
- Check logs with `docker-compose logs`
- Try restarting: `docker-compose restart`

### Level 2: Team Lead (Sean)
- If data loss suspected
- If security issue
- If multiple systems affected

### Level 3: OpenClaw Community
- Discord: https://discord.com/invite/clawd
- GitHub Issues: https://github.com/openclaw/openclaw

### Level 4: Infrastructure Provider
- Coolify support: https://coolify.io/docs
- VPS provider: Check server status

---

## 📝 Log Locations

| Log | Location | Rotation |
|-----|----------|----------|
| OpenClaw gateway | `docker logs openclaw-gateway` | Docker managed |
| Backup script | `/var/log/openclaw-backup.log` | Manual |
| Cron jobs | `/var/log/syslog` or `/var/log/cron` | System managed |
| System | `journalctl -u docker` | System managed |

---

## 🎯 Quick Fixes Cheat Sheet

| Problem | Command |
|---------|---------|
| No response | `docker-compose restart` |
| Wrong config | `git pull && docker-compose restart` |
| Session stuck | Type `/new` in chat |
| Memory not loading | `docker-compose restart` |
| Backup failing | `./scripts/backup.sh` (run manually) |
| Restore needed | `./scripts/restore.sh` |
| Full reset | `docker-compose down && docker-compose up -d` |
| Check status | `docker-compose ps && openclaw status` |
| View logs | `docker-compose logs -f` |

---

## ⚠️ Common Mistakes

1. **Editing files directly on VPS without git**
   - Changes lost on next deploy
   - Always: edit → commit → push

2. **Forgetting to restart after config change**
   - Config only loads on start
   - Always restart container

3. **Running backup while container is down**
   - Backup will fail
   - Always check container status first

4. **Manual edits to /data/.openclaw/**
   - Will be overwritten on restore
   - Edit files in git repo instead

5. **Not checking disk space**
   - Backups fail silently when disk full
   - Monitor with `df -h`

---

*Remember: When in doubt, check the logs. Logs tell the truth.*
