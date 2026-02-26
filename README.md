# UNI OpenClaw Infrastructure

**Production-ready OpenClaw deployment on Coolify with automatic persistence and backup management.**

---

## 🎯 What This Is

This repository contains infrastructure-as-code for deploying OpenClaw (AI agent system) on a VPS using Coolify + Docker.

**Key Features:**
- ✅ **Git-tracked configs** — version control for all agent settings
- ✅ **Auto-restore on deploy** — backups automatically restore on redeploy
- ✅ **Daily session resets** — prevents token bloat, maintains performance
- ✅ **QMD memory persistence** — long-term memory survives session resets
- ✅ **One-command setup** — get running in minutes

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[COOLIFY_DEPLOYMENT_GUIDE.md](COOLIFY_DEPLOYMENT_GUIDE.md)** | Step-by-step deployment instructions |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design, data flow, why we made these choices |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Common issues and solutions for on-call engineers |

---

## 🚀 Quick Start

### Prerequisites

- VPS with Coolify installed
- GitHub account
- SSH access to VPS

### 1. Clone & Setup

```bash
# On your VPS
git clone https://github.com/YOUR_USERNAME/uni-openclaw-infra.git /data/uni-openclaw-infra
cd /data/uni-openclaw-infra

# Run automated setup
./setup.sh
```

### 2. Configure Environment

```bash
# Edit environment variables
vim .env

# Required:
# - OPENCLAW_GATEWAY_TOKEN
# - KIMI_API_KEY (or other model keys)
# - Slack tokens (if using Slack)
```

### 3. Deploy

```bash
# Start services
docker-compose up -d

# Verify
docker-compose ps
openclaw status
```

---

## 📁 Repository Structure

```
uni-openclaw-infra/
├── config/
│   └── openclaw.json          # Agent configs, models, channels (tracked in Git)
├── workspace/
│   ├── agents/                # Agent base documents (SOUL.md, TOOLS.md, etc.)
│   ├── memory/                # Daily memory logs
│   └── skills/                # Custom skills (optional)
├── scripts/
│   ├── entrypoint.sh          # Auto-restore on container boot
│   ├── backup.sh              # Manual backup
│   └── restore.sh             # Manual restore
├── .github/workflows/
│   └── deploy.yml             # Auto-deploy on push to main
├── docker-compose.yml         # Coolify service definition
├── setup.sh                   # One-command setup script
├── .env.example               # Environment template
└── docs/
    ├── COOLIFY_DEPLOYMENT_GUIDE.md  # Full deployment guide
    ├── ARCHITECTURE.md              # System architecture
    └── TROUBLESHOOTING.md           # On-call troubleshooting
```

---

## 🔄 Daily Workflow

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

### Short Task (Fresh Session)

```
/new
"Analyze this API endpoint"
→ Clean session, no history clutter
```

### Long-Term Work

Just chat normally. Sessions auto-reset at 4 AM UTC, but **QMD maintains long-term memory** across resets.

---

## 🛡️ Data Persistence

### How It Works

| Scenario | What Happens | Data Status |
|----------|--------------|-------------|
| **Config change pushed** | GitHub Actions auto-deploys | ✅ Preserved |
| **VPS restart** | Container restarts, auto-restore | ✅ Auto-restored |
| **Manual redeploy** | New container, auto-restore | ✅ Auto-restored |
| **Complete data loss** | Restore from backup | ✅ Manual restore |

### Backup Strategy

- **Automatic**: Daily at 3 AM UTC (cron job)
- **Retention**: Last 10 backups kept
- **Location**: `/data/backups/openclaw/`
- **Format**: `openclaw_backup_YYYYMMDD_HHMMSS.tar.gz`

### Manual Backup/Restore

```bash
# Create backup
./scripts/backup.sh

# Restore from latest
./scripts/restore.sh

# Restore specific backup
./scripts/restore.sh /data/backups/openclaw/openclaw_backup_20260226_120000.tar.gz
```

---

## 🧠 Session Management

### Why Daily Resets?

LLM context windows are finite. Unbounded sessions = token bloat = higher costs + slower responses.

### Reset Policy

| Context | Reset Policy | Rationale |
|---------|--------------|-----------|
| Direct messages | Daily 4 AM UTC | Clean daily slate |
| Slack threads | Daily 4 AM UTC | Task-specific, ephemeral |
| Group chats | Idle 2 hours | Ephemeral chatter |
| Short tasks | `/new` on demand | One-off = fresh session |

### QMD: Long-Term Memory

QMD (Queryable Memory Database) vectorizes workspace files. Even after session reset, I can search across all prior conversations.

```
User: "How's the Google Ads integration?"
        ↓
QMD Search: [Finds "Google Ads setup complete" from yesterday]
        ↓
Agent: "The integration was completed yesterday..."
```

---

## 🔧 Troubleshooting

**Quick diagnostic:**
```bash
# Check if running
docker-compose ps

# View logs
docker-compose logs -f

# Check backup status
./scripts/backup.sh
ls -lh /data/backups/openclaw/
```

**See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for:**
- Service down scenarios
- Data loss recovery
- Slack integration issues
- API key problems
- Backup failures
- Complete rebuild procedures

---

## 🔐 Security

- **API Keys**: Stored in Coolify environment variables, never in Git
- **Gateway Token**: Environment variable, rotates manually
- **Backups**: Local VPS storage (not cloud)
- **SSH**: Key-based auth only

**What NOT to commit:**
```
.env
.openclaw/
/data/
/backups/
*.key
*.pem
```

---

## 📊 Monitoring

### Health Checks

```bash
# Service status
openclaw status

# Container status
docker-compose ps

# Recent logs
docker-compose logs --tail 50

# Backup log
tail -f /var/log/openclaw-backup.log
```

### Aliases (add to `~/.bashrc`)

```bash
alias oc='cd /data/uni-openclaw-infra'
alias ocl='docker-compose logs -f'
alias ocs='openclaw status'
alias ocb='./scripts/backup.sh'
alias ocr='./scripts/restore.sh'
alias ocp='docker-compose ps'
```

---

## 🤝 For Future Colleagues

**New to this system?** Start here:

1. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** — understand how it works
2. **Skim [COOLIFY_DEPLOYMENT_GUIDE.md](COOLIFY_DEPLOYMENT_GUIDE.md)** — deployment steps
3. **Bookmark [TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — when things break

**Emergency contacts:**
- System owner: Sean Tan
- Infrastructure repo: `uni-openclaw-infra`
- Backup location: `/data/backups/openclaw/`

---

## 📝 Changelog

| Date | Change |
|------|--------|
| 2026-02-26 | Initial infrastructure setup |
| 2026-02-26 | Hybrid session strategy implemented (daily resets + QMD) |
| 2026-02-26 | Auto-restore on deployment |
| 2026-02-26 | Comprehensive documentation |

---

## 🔗 Resources

- **OpenClaw Docs**: https://docs.openclaw.ai
- **Coolify Docs**: https://coolify.io/docs
- **OpenClaw Discord**: https://discord.com/invite/clawd

---

**Maintained by:** UNI Marketing Agency  
**Last updated:** 2026-02-26  
**Questions?** Check the docs or ask in Slack.
