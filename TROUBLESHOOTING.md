# OpenClaw Troubleshooting Guide

**For Future Colleagues & On-Call Engineers**

This guide covers common issues and their solutions. When something breaks, start here.

---

## Quick Diagnostic Commands

```bash
# Check if OpenClaw is running
openclaw status

# Check Docker containers
docker ps | grep openclaw
docker-compose -f /data/uni-openclaw-infra/docker-compose.yml ps

# View recent logs
docker logs openclaw-gateway --tail 100

# Check backup status
ls -lth /data/backups/openclaw/ | head -5

# Check disk space
df -h /data

# Check session status
openclaw sessions --json 2>/dev/null | head -20
```

---

## Issue Categories

### 🔴 Critical: Service Down

#### Symptom: "OpenClaw not responding" or Slack bot offline

**Step 1: Check if container is running**
```bash
docker ps | grep openclaw
```

**If not running:**
```bash
cd /data/uni-openclaw-infra
docker-compose up -d
docker-compose logs -f
```

**Step 2: Check for port conflicts**
```bash
netstat -tlnp | grep 18789
# If something else is using port 18789, kill it or change port
```

**Step 3: Check entrypoint logs**
```bash
docker logs openclaw-gateway 2>&1 | grep -E "(entrypoint|restore|error)"
```

---

### 🟠 High: Data Loss / Sessions Missing

#### Symptom: "I can't see yesterday's conversations" or "Agents don't remember"

**Step 1: Check if backup exists**
```bash
ls -la /data/backups/openclaw/
```

**If no backups:**
```bash
# Emergency backup now
cd /data/uni-openclaw-infra
./scripts/backup.sh
```

**Step 2: Check if data restored on boot**
```bash
docker logs openclaw-gateway | grep -i "restore"
# Should see: "✅ Restore complete" or "ℹ️ No backup found"
```

**Step 3: Manual restore**
```bash
# List available backups
ls -t /data/backups/openclaw/openclaw_backup_*.tar.gz

# Restore specific backup
./scripts/restore.sh /data/backups/openclaw/openclaw_backup_20260226_120000.tar.gz

# Or restore latest
./scripts/restore.sh
```

**Step 4: Verify sessions restored**
```bash
ls -la /data/.openclaw/agents/clover/sessions/
```

---

### 🟡 Medium: QMD Search Not Working

#### Symptom: "Agent doesn't remember what we discussed" or memory_search returns nothing

**Step 1: Check QMD index exists**
```bash
ls -la /data/.openclaw/agents/clover/qmd/
# Should see xdg-cache/ and xdg-config/
```

**Step 2: Check QMD is enabled in config**
```bash
grep -A 5 '"qmd"' /data/uni-openclaw-infra/config/openclaw.json
```

**Step 3: Rebuild QMD index**
```bash
# Stop OpenClaw
docker-compose down

# Rebuild index
qmd update /data/workspace

# Restart
docker-compose up -d
```

**Step 4: Verify QMD in new session**
```bash
# Start a fresh session
/new

# Ask: "Search for Google Ads setup"
# Should return results from MEMORY.md
```

---

### 🟡 Medium: Sessions Not Resetting

#### Symptom: "Session is getting too long" or tokens exceeding limit

**Step 1: Check current session size**
```bash
openclaw sessions --json 2>/dev/null | grep -E "(totalTokens|sessionKey)"
```

**Step 2: Check reset configuration**
```bash
grep -A 10 '"session"' /data/uni-openclaw-infra/config/openclaw.json
```

**Should see:**
```json
"resetByType": {
  "direct": { "mode": "daily", "atHour": 4 },
  "thread": { "mode": "daily", "atHour": 4 },
  "group": { "mode": "idle", "idleMinutes": 120 }
}
```

**Step 3: Manual reset**
```bash
# In any chat, type:
/new

# Or force reset with model change
/new kimi25
```

**Step 4: Verify reset worked**
```bash
openclaw status
# Should show: "Context: 0/32k (0%)"
```

---

### 🟡 Medium: Slack Integration Broken

#### Symptom: "Slack bot not responding" or "Messages not going through"

**Step 1: Check Slack tokens**
```bash
# In Coolify dashboard, verify these are set:
echo $SLACK_BOT_TOKEN      # Should start with xoxb-
echo $SLACK_APP_TOKEN      # Should start with xapp-
echo $SLACK_SIGNING_SECRET # Should be 32 chars
```

**Step 2: Test Slack connectivity**
```bash
curl -X POST https://slack.com/api/auth.test \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN"
# Should return: "ok": true
```

**Step 3: Check webhook URL**
```bash
# In Slack app settings, verify Request URL:
# https://your-vps/webhook/slack

# Test webhook:
curl -X POST https://your-vps/webhook/slack \
  -H "Content-Type: application/json" \
  -d '{"type":"url_verification","challenge":"test"}'
```

**Step 4: Regenerate tokens if needed**
1. Go to https://api.slack.com/apps
2. Select your app
3. Regenerate tokens
4. Update Coolify environment variables
5. Redeploy

---

### 🟢 Low: Backup Failures

#### Symptom: "Backups not being created" or "Cron job not running"

**Step 1: Check cron job**
```bash
crontab -l | grep openclaw
```

**Should see:**
```
0 3 * * * /data/uni-openclaw-infra/scripts/backup.sh >> /var/log/openclaw-backup.log 2>&1
```

**Step 2: Check backup log**
```bash
tail -50 /var/log/openclaw-backup.log
```

**Step 3: Run manual backup**
```bash
cd /data/uni-openclaw-infra
./scripts/backup.sh
```

**Step 4: Check disk space**
```bash
df -h /data
# If >90% full, clean old backups:
find /data/backups/openclaw -name "*.tar.gz" -mtime +7 -delete
```

---

### 🟢 Low: GitHub Actions Failing

#### Symptom: "Auto-deploy not working" or "GitHub Actions red X"

**Step 1: Check GitHub Actions logs**
1. Go to GitHub repo → Actions tab
2. Click failed workflow
3. Read error message

**Common errors:**

**SSH connection failed:**
```
Error: ssh: connect to host 194.238.31.45 port 22: Connection refused
```
→ Check VPS is running, SSH port is 22, firewall rules

**Permission denied:**
```
Error: Permission denied (publickey)
```
→ Check VPS_SSH_KEY secret is correct, key is in authorized_keys

**Docker not found:**
```
bash: docker-compose: command not found
```
→ SSH user doesn't have docker access, add to docker group

**Step 2: Test manually**
```bash
# On VPS, run the same commands as GitHub Actions
cd /data/uni-openclaw-infra
docker-compose pull
docker-compose up -d
```

---

### 🟢 Low: Model API Errors

#### Symptom: "Model not responding" or "API key invalid"

**Step 1: Check API keys in Coolify**
```bash
# Verify these are set:
echo $KIMI_API_KEY
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

**Step 2: Test API connectivity**
```bash
# Test Kimi
curl https://api.moonshot.ai/v1/models \
  -H "Authorization: Bearer $KIMI_API_KEY"

# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Step 3: Check fallback chain**
```bash
# In openclaw.json, verify fallbacks are configured:
grep -A 5 '"fallbacks"' /data/uni-openclaw-infra/config/openclaw.json
```

**Step 4: Switch model temporarily**
```bash
# In chat, type:
/model openai/gpt-4o-mini

# Or start fresh with different model:
/new openai/gpt-4o-mini
```

---

## Recovery Procedures

### Complete OpenClaw Rebuild

If everything is broken and you need to start fresh:

```bash
# 1. Backup current state (just in case)
cd /data/uni-openclaw-infra
cp -r /data/.openclaw /data/.openclaw.broken.$(date +%Y%m%d)

# 2. Stop and remove containers
docker-compose down -v

# 3. Remove old data (WARNING: destroys sessions)
# Only do this if you're sure!
rm -rf /data/.openclaw/*

# 4. Restore from latest backup
./scripts/restore.sh

# 5. Start fresh
docker-compose up -d

# 6. Verify
openclaw status
```

### Migrate to New VPS

```bash
# On old VPS:
# 1. Create backup
cd /data/uni-openclaw-infra
./scripts/backup.sh

# 2. Copy backup to new VPS
scp /data/backups/openclaw/latest.tar.gz root@new-vps:/tmp/
scp -r /data/uni-openclaw-infra root@new-vps:/data/

# On new VPS:
# 3. Restore
cd /data/uni-openclaw-infra
mkdir -p /data/backups/openclaw
cp /tmp/latest.tar.gz /data/backups/openclaw/
./scripts/restore.sh

# 4. Install Docker/Coolify if needed
# 5. Deploy
docker-compose up -d
```

---

## Prevention Checklist

Daily:
- [ ] Check `/var/log/openclaw-backup.log` for errors
- [ ] Verify Slack bot responds to test message

Weekly:
- [ ] Review disk usage: `df -h /data`
- [ ] Check backup count: `ls /data/backups/openclaw/ | wc -l`
- [ ] Review GitHub Actions for failed deploys

Monthly:
- [ ] Test restore procedure on staging
- [ ] Rotate API keys if needed
- [ ] Review and prune old session files

---

## Escalation Path

**Level 1 (Self-Service):**
- Check this troubleshooting guide
- Run diagnostic commands above
- Try manual restart

**Level 2 (Team Lead):**
- Slack #ops channel
- Share: `openclaw status` output
- Share: relevant logs

**Level 3 (External):**
- OpenClaw Discord: https://discord.com/invite/clawd
- OpenClaw GitHub Issues
- Coolify Discord for deployment issues

---

## Useful Aliases

Add to `~/.bashrc` for quick access:

```bash
# OpenClaw shortcuts
alias oc='cd /data/uni-openclaw-infra'
alias ocl='docker logs openclaw-gateway --tail 50'
alias ocs='openclaw status'
alias ocb='./scripts/backup.sh'
alias ocr='./scripts/restore.sh'
alias ocp='docker-compose ps'
alias ocrst='docker-compose restart'

# Quick session check
alias oc-sessions='openclaw sessions --json 2>/dev/null | grep -E "(sessionKey|totalTokens)"'

# Quick backup check
alias oc-backups='ls -lth /data/backups/openclaw/ | head -5'
```

---

## Log Locations

| Log | Location | Purpose |
|-----|----------|---------|
| Backup log | `/var/log/openclaw-backup.log` | Backup job output |
| Container logs | `docker logs openclaw-gateway` | OpenClaw runtime |
| System logs | `/var/log/syslog` | System-level issues |
| Coolify logs | Coolify dashboard | Deployment issues |

---

## Common File Paths

| File | Path |
|------|------|
| Main config | `/data/uni-openclaw-infra/config/openclaw.json` |
| Docker compose | `/data/uni-openclaw-infra/docker-compose.yml` |
| Backup script | `/data/uni-openclaw-infra/scripts/backup.sh` |
| Restore script | `/data/uni-openclaw-infra/scripts/restore.sh` |
| Backup storage | `/data/backups/openclaw/` |
| Runtime data | `/data/.openclaw/` |
| Agent sessions | `/data/.openclaw/agents/*/sessions/` |
| QMD index | `/data/.openclaw/agents/*/qmd/` |

---

## Quick Reference Card

**Service Status:**
```bash
docker-compose ps
openclaw status
```

**Restart:**
```bash
docker-compose restart
```

**View Logs:**
```bash
docker-compose logs -f
```

**Backup:**
```bash
./scripts/backup.sh
```

**Restore:**
```bash
./scripts/restore.sh
```

**Force New Session:**
```
/new
```

**Check Sessions:**
```bash
openclaw sessions --json
```

---

**Last Updated:** 2026-02-26  
**Maintained by:** UNI Marketing Agency  
**Questions?** Check ARCHITECTURE.md for system design details
