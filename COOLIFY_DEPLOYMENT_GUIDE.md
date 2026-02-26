# OpenClaw Coolify Deployment Guide

Complete step-by-step guide to deploy OpenClaw on Coolify with automatic persistence.

---

## Prerequisites

- VPS with Coolify installed
- Domain/subdomain pointed to VPS (optional but recommended)
- GitHub account
- SSH access to VPS

---

## Phase 1: Repository Setup (5 minutes)

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Name: `uni-openclaw-infra` (or your preferred name)
3. Visibility: Private (recommended)
4. ✅ Initialize with README
5. Click **Create repository**

### Step 2: Push Local Code

```bash
# On your VPS
cd /data/workspace/uni-openclaw-infra

# Initialize git
git init
git add .
git commit -m "Initial OpenClaw infrastructure setup"

# Connect to GitHub (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/uni-openclaw-infra.git

# Push
git branch -M main
git push -u origin main
```

---

## Phase 2: GitHub Secrets Configuration (3 minutes)

### Step 1: Add Repository Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `VPS_HOST` | `194.238.31.45` | Your VPS IP |
| `VPS_USER` | `root` | Your SSH username |
| `VPS_SSH_KEY` | (private key) | `cat ~/.ssh/id_rsa` |

**Important**: The SSH key must:
- Be added to VPS `~/.ssh/authorized_keys`
- Have no passphrase (or use ssh-agent)
- Start with `-----BEGIN OPENSSH PRIVATE KEY-----`

### Step 2: Test SSH Connection

```bash
# From your local machine
ssh -i ~/.ssh/your_key root@194.238.31.45

# Should log in without password
```

---

## Phase 3: Coolify Service Setup (10 minutes)

### Step 1: Move Infrastructure Code

```bash
# On VPS
mv /data/workspace/uni-openclaw-infra /data/uni-openclaw-infra
```

### Step 2: Create New Service in Coolify

1. Log into Coolify dashboard: `https://your-coolify-domain.com`
2. Click **New Resource** → **Docker Compose**
3. Name: `openclaw-gateway`
4. Select your server

### Step 3: Configure Docker Compose

Paste this into Coolify's Docker Compose editor:

```yaml
version: '3.8'

services:
  openclaw-gateway:
    image: openclaw/openclaw:latest
    container_name: openclaw-gateway
    restart: unless-stopped
    
    environment:
      HOME: /home/node
      OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN}
      KIMI_API_KEY: ${KIMI_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      SLACK_BOT_TOKEN: ${SLACK_BOT_TOKEN}
      SLACK_APP_TOKEN: ${SLACK_APP_TOKEN}
      SLACK_SIGNING_SECRET: ${SLACK_SIGNING_SECRET}
      
    volumes:
      - openclaw-data:/home/node/.openclaw
      - /data/uni-openclaw-infra/config/openclaw.json:/home/node/.openclaw/openclaw.json:ro
      - /data/uni-openclaw-infra/workspace:/home/node/.openclaw/workspace:rw
      - /data/uni-openclaw-infra/scripts:/opt/openclaw/scripts:ro
      
    ports:
      - "18789:18789"
      - "18790:18790"
      
    entrypoint: ["/opt/openclaw/scripts/entrypoint.sh"]
    command: >
      node dist/index.js gateway
      --bind lan
      --port 18789

volumes:
  openclaw-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/.openclaw
```

### Step 4: Add Environment Variables

In Coolify, go to **Environment Variables** and add:

**Required:**
```
OPENCLAW_GATEWAY_TOKEN=uni-random-token
KIMI_API_KEY=sk-your-kimi-key
```

**Slack Integration (if using):**
```
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
```

**Other Models (optional):**
```
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
```

### Step 5: Deploy

1. Click **Deploy** in Coolify
2. Wait for build (2-3 minutes)
3. Check logs for "OpenClaw Gateway Startup"

---

## Phase 4: Initial Backup & Validation (5 minutes)

### Step 1: Create Backup Directory

```bash
mkdir -p /data/backups/openclaw
```

### Step 2: Backup Current State

```bash
cd /data/uni-openclaw-infra
./scripts/backup.sh
```

Should see:
```
📦 Creating OpenClaw backup...
✅ Backup complete
   Size: 15M
   Total backups: 1
```

### Step 3: Verify Gateway is Running

```bash
# Check container
docker ps | grep openclaw

# Check logs
docker logs openclaw-gateway --tail 50

# Test OpenClaw
openclaw status
```

### Step 4: Test Auto-Restore

```bash
# Simulate redeploy
docker-compose down
docker-compose up -d

# Check that data restored
docker logs openclaw-gateway | grep "Restore complete"
```

---

## Phase 5: Setup Backup Automation (2 minutes)

### Step 1: Edit Crontab

```bash
crontab -e
```

### Step 2: Add Backup Job

```cron
# OpenClaw daily backup at 3 AM UTC (before 4 AM session reset)
0 3 * * * /data/uni-openclaw-infra/scripts/backup.sh >> /var/log/openclaw-backup.log 2>&1

# Cleanup old backups weekly
0 4 * * 0 find /data/backups/openclaw -name "openclaw_backup_*.tar.gz" -mtime +30 -delete
```

### Step 3: Verify Cron

```bash
crontab -l | grep openclaw
```

---

## Phase 6: Configure Domain (Optional, 5 minutes)

### Step 1: Add Domain in Coolify

1. In Coolify service settings, go to **Domains**
2. Add: `openclaw.yourdomain.com`
3. Enable HTTPS (Let's Encrypt)

### Step 2: Update Allowed Origins

Edit `/data/uni-openclaw-infra/config/openclaw.json`:

```json
{
  "gateway": {
    "controlUi": {
      "allowedOrigins": [
        "https://openclaw.yourdomain.com",
        "http://194.238.31.45:9090"
      ]
    }
  }
}
```

### Step 3: Commit & Deploy

```bash
git add .
git commit -m "Add custom domain"
git push origin main

# Coolify will auto-deploy
```

---

## Phase 7: Slack Integration (Optional, 5 minutes)

### Step 1: Create Slack App

1. Go to https://api.slack.com/apps
2. Click **Create New App** → **From scratch**
3. Name: `UNI OpenClaw`
4. Select your workspace

### Step 2: Add Bot Token Scopes

Go to **OAuth & Permissions** → **Scopes**:

**Bot Token Scopes:**
- `app_mentions:read`
- `channels:history`
- `chat:write`
- `files:read`
- `groups:history`
- `im:history`
- `im:write`
- `mpim:history`

### Step 3: Install App & Get Tokens

1. Click **Install to Workspace**
2. Copy **Bot User OAuth Token** (starts with `xoxb-`)
3. Go to **Basic Information** → **App-Level Tokens**
4. Generate token with `connections:write` scope (starts with `xapp-`)

### Step 4: Enable Events

Go to **Event Subscriptions**:
1. Enable Events
2. Request URL: `https://your-vps/webhook/slack`
3. Subscribe to bot events:
   - `app_mention`
   - `message.im`

### Step 5: Add to Coolify Env

Add to Coolify environment variables:
```
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
SLACK_SIGNING_SECRET=...
```

Redeploy.

---

## Daily Workflow

### Making Configuration Changes

```bash
cd /data/uni-openclaw-infra

# Edit configs
vim config/openclaw.json

# Commit and push
git add .
git commit -m "Update agent configurations"
git push origin main

# GitHub Actions auto-deploys to Coolify
```

### Monitoring

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Check backup status
ls -lh /data/backups/openclaw/
```

---

## Redeployment Scenarios

### Scenario 1: Config Change

1. Edit files locally or on VPS
2. `git commit` and `git push`
3. GitHub Actions deploys automatically
4. Zero downtime (rolling update)

### Scenario 2: VPS Restart

1. VPS boots up
2. Coolify starts containers
3. `entrypoint.sh` auto-restores from backup
4. Service online in ~2 minutes

### Scenario 3: Manual Coolify Redeploy

1. Click "Redeploy" in Coolify
2. New container starts
3. `entrypoint.sh` restores data
4. Old sessions preserved

### Scenario 4: Complete Data Loss

```bash
# Restore from backup
cd /data/uni-openclaw-infra
./scripts/restore.sh /data/backups/openclaw/openclaw_backup_20260226_120000.tar.gz

# Or latest
./scripts/restore.sh
```

---

## Verification Checklist

After setup, verify:

- [ ] GitHub repo created and pushed
- [ ] GitHub secrets configured
- [ ] Coolify service deployed
- [ ] Environment variables set
- [ ] Backup script runs manually
- [ ] Cron job scheduled
- [ ] Auto-restore tested
- [ ] Slack integration working (if used)
- [ ] Domain configured (if used)

---

## Next Steps

1. **Test the setup**: Send a message to your agent
2. **Verify backups**: Check `/data/backups/openclaw/` daily
3. **Monitor logs**: Set up log alerting if needed
4. **Document customizations**: Add notes to repo README

---

**Need Help?**

See `TROUBLESHOOTING.md` for common issues and solutions.
