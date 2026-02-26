# OpenClaw Infrastructure Architecture

## Overview

This document explains how the OpenClaw infrastructure is designed, why we made these choices, and how data flows through the system.

---

## System Design Philosophy

**Goal**: Zero-downtime deployments, automatic data persistence, and simple disaster recovery.

**Principles**:
1. **Infrastructure as Code**: All configs in Git
2. **Immutable Deployments**: Docker containers, not native processes
3. **Automatic Recovery**: Backup/restore on every deploy
4. **Layered Persistence**: Hot data in container, warm data in backups, cold data in Git

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      COOLIFY VPS                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           GitHub Actions (CI/CD)                      │  │
│  │  • Push to main → Auto-deploy                        │  │
│  │  • SSH into VPS → Pull configs                       │  │
│  │  • Restart containers                                │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │ SSH                                 │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │              Docker Compose                           │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │    OpenClaw Container (official image)        │    │  │
│  │  │                                                │    │  │
│  │  │  ┌──────────────────────────────────────────┐ │    │  │
│  │  │  │        entrypoint.sh (auto-restore)       │ │    │  │
│  │  │  │  1. Check for backup                      │ │    │  │
│  │  │  │  2. Extract to /home/node/.openclaw      │ │    │  │
│  │  │  │  3. Start gateway                         │ │    │  │
│  │  │  └──────────────────────────────────────────┘ │    │  │
│  │  │                                                │    │  │
│  │  │  Volumes:                                     │    │  │
│  │  │  • openclaw-data → /data/.openclaw (bind)    │    │  │
│  │  │  • config/openclaw.json → config (ro)        │    │  │
│  │  │  • workspace/ → workspace (rw)               │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │              Persistent Storage                       │  │
│  │                                                        │  │
│  │  /data/.openclaw/           (main data)               │  │
│  │  ├── agents/                (sessions, qmd)           │  │
│  │  └── openclaw.json          (runtime config)         │  │
│  │                                                        │  │
│  │  /data/uni-openclaw-infra/    (git-tracked)          │  │
│  │  ├── config/openclaw.json   (source of truth)        │  │
│  │  ├── workspace/agents/      (base docs)              │  │
│  │  └── workspace/memory/      (daily logs)             │  │
│  │                                                        │  │
│  │  /data/backups/openclaw/      (tar.gz archives)      │  │
│  │  └── openclaw_backup_*.tar.gz (daily snapshots)      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Persistence Strategy

### Three-Layer Persistence

| Layer | Location | Purpose | Persistence |
|-------|----------|---------|-------------|
| **Hot** | Container volumes | Runtime state | Survives container restart |
| **Warm** | Backup archives | Disaster recovery | 30 days retention |
| **Cold** | Git repository | Config history | Permanent (Git history) |

### What Gets Persisted Where

```
Git Repository (uni-openclaw-infra)
├── config/openclaw.json          ← Agent definitions, models, channels
├── workspace/agents/*/SOUL.md    ← Agent personalities
├── workspace/agents/*/TOOLS.md   ← Agent capabilities
├── workspace/memory/2026-*.md    ← Daily memory logs (optional)
└── docker-compose.yml            ← Deployment configuration

Backup Archives (/data/backups/openclaw/)
├── agents/*/sessions/*.jsonl     ← Conversation history
├── agents/*/qmd/                 ← Vector embeddings (QMD)
└── workspace/memory/*.md         ← All memory files

Runtime Data (/data/.openclaw/)
├── agents/clover/sessions/       ← Current session data
├── agents/clover/qmd/            ← QMD index (rebuilt from backup)
└── openclaw.json                 ← Runtime config (from Git)
```

---

## Session Management Strategy

### Why Daily Session Resets?

**Problem**: LLM context windows are finite. Unbounded sessions = token bloat = higher costs + slower responses.

**Solution**: Hybrid reset strategy with QMD for long-term memory.

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Lifecycle                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Day 1 (Active Session)                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ User: "Set up Google Ads integration"                │  │
│  │                                                      │  │
│  │ Agent: [Completes task, writes to MEMORY.md]        │  │
│  │                                                      │  │
│  │ QMD: Embeds "Google Ads setup complete"              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         ▼ 4:00 AM UTC                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Session Reset (Automatic)                            │  │
│  │ • Old session archived to .jsonl                     │  │
│  │ • New session starts fresh                           │  │
│  │ • System prompt reinjected                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  Day 2 (New Session)    │                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ User: "How's the Google Ads integration?"            │  │
│  │                                                      │  │
│  │ QMD Search: [Finds "Google Ads setup complete"]      │  │
│  │                                                      │  │
│  │ Agent: "The integration was completed yesterday..."  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Reset Policy by Context

| Context Type | Reset Policy | Rationale |
|--------------|--------------|-----------|
| **Direct Messages** | Daily at 4 AM UTC | Clean slate for daily work |
| **Slack Threads** | Daily at 4 AM UTC | Task threads don't need longevity |
| **Group Chats** | Idle 2 hours | Ephemeral, reduce noise |
| **Short Tasks** | `/new` on demand | One-off = fresh session |
| **Long Projects** | Stay in session | Multi-day work preserved |

### QMD: The Memory Bridge

QMD (Queryable Memory Database) vectorizes your workspace files:

```
User Query
    │
    ▼
┌─────────────────┐
│  memory_search  │  ← Searches MEMORY.md + memory/*.md
│  (vector + FTS) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Relevant       │  ← Top 6 matches injected into context
│  Context        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Response   │  ← Informed by long-term memory
└─────────────────┘
```

---

## Redeployment Flow

### Normal Deployment (Config Change)

```
Developer
    │ git push
    ▼
GitHub Actions
    │ SSH + docker-compose up
    ▼
Coolify VPS
    │
    ├── Pull new configs ──────┐
    │                           │
    └── Restart container       │
            │                   │
            ▼                   │
    ┌───────────────┐           │
    │ entrypoint.sh │           │
    │ • No backup   │           │
    │   needed      │           │
    │ • Start fresh │           │
    └───────┬───────┘           │
            │                   │
            ▼                   │
    ┌───────────────┐           │
    │ Load configs  │◄──────────┘
    │ from Git      │
    └───────┬───────┘
            │
            ▼
    OpenClaw Gateway Ready
```

### Disaster Recovery (Data Loss)

```
VPS Reboot / Container Failure
    │
    ▼
Coolify Restarts Container
    │
    ▼
┌─────────────────────────┐
│    entrypoint.sh        │
│                         │
│  1. Check /data/.openclaw│
│     → Empty or missing   │
│                         │
│  2. Find latest backup   │
│     → /data/backups/...  │
│                         │
│  3. Extract backup       │
│     → Restore sessions   │
│     → Restore QMD        │
│                         │
│  4. Start gateway        │
└───────────┬─────────────┘
            │
            ▼
    Sessions Restored
    Memory Preserved
```

---

## Security Model

### Data Protection

| Layer | Protection |
|-------|------------|
| **Git Repository** | Private repo, no secrets committed |
| **API Keys** | Coolify environment variables only |
| **Backups** | Stored on VPS disk (not cloud) |
| **SSH Keys** | GitHub Secrets, VPS authorized_keys |
| **Gateway Token** | Environment variable, not in Git |

### What NOT to Commit to Git

```
# .gitignore
.env
.openclaw/
/data/
/backups/
*.key
*.pem
node_modules/
```

### Secrets Flow

```
GitHub Secrets ──► GitHub Actions ──► SSH to VPS ──► Coolify Env ──► Container
     │                                                            │
     │ (Never in code)                                            │
     └────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting Architecture

### If Auto-Restore Fails

```bash
# Check if backup exists
ls -la /data/backups/openclaw/

# Check container logs
docker logs openclaw-gateway

# Manual restore
./scripts/restore.sh

# Verify data
ls -la /data/.openclaw/agents/
```

### If QMD Search Fails

```bash
# Check QMD index
ls -la /data/.openclaw/agents/clover/qmd/

# Rebuild QMD manually
qmd update /data/workspace

# Check QMD config in openclaw.json
```

### If Sessions Don't Reset

```bash
# Check session config
grep -A 10 '"session"' /data/uni-openclaw-infra/config/openclaw.json

# Check current sessions
openclaw sessions --json

# Force reset
/new
```

---

## Future Considerations

### Scaling Horizontally

If you need multiple VPS instances:

```
                    Load Balancer
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ VPS #1  │    │ VPS #2  │    │ VPS #3  │
    │ OpenClaw│    │ OpenClaw│    │ OpenClaw│
    └────┬────┘    └────┬────┘    └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────┐
              │ Shared Storage  │
              │ (NFS/EFS)       │
              │ /data/.openclaw │
              └─────────────────┘
```

### Monitoring & Alerting

Future additions:
- Prometheus metrics from OpenClaw
- Grafana dashboard for token usage
- PagerDuty for backup failures
- Uptime monitoring for gateway

---

## Glossary

| Term | Meaning |
|------|---------|
| **QMD** | Queryable Memory Database — vector search for workspace files |
| **Session** | A conversation context between user and agent |
| **Reset** | Starting a new session (clears short-term context) |
| **Compaction** | Summarizing old session context to save tokens |
| **Pruning** | Removing old tool results from context |
| **Coolify** | Self-hosted PaaS for Docker deployments |
| **Entrypoint** | Script that runs when container starts |

---

## Contact & Resources

- **OpenClaw Docs**: https://docs.openclaw.ai
- **Coolify Docs**: https://coolify.io/docs
- **This Repo**: `uni-openclaw-infra`
- **Backup Location**: `/data/backups/openclaw/`
- **Live Config**: `/data/uni-openclaw-infra/config/openclaw.json`

---

*Last updated: 2026-02-26*  
*Maintained by: UNI Marketing Agency*
