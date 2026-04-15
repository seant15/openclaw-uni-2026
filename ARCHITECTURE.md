# OpenClaw System Architecture

**For:** Future team members and troubleshooting reference
**Last Updated:** 2026-04-06 (repo map corrected + backup protocol added)
**Maintained by:** UNI Marketing / Sean Tan

---

## Executive Summary

We run **OpenClaw** (AI agent system) on a VPS via **Coolify** (PaaS). This document explains:
1. How the system is structured
2. Where data lives
3. How we prevent data loss
4. How memory/conversations persist across sessions

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        COOLIFY VPS                              │
│                   (194.238.31.45)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐      ┌─────────────────────────────┐     │
│  │   Docker Compose  │      │   Persistent Volume         │     │
│  │   (Coolify)       │      │   /data/.openclaw           │     │
│  │                   │      │                             │     │
│  │  ┌─────────────┐  │      │  • Agent configs            │     │
│  │  │ OpenClaw    │  │      │  • Session history          │     │
│  │  │ Container   │──┼──────│  • QMD embeddings           │     │
│  │  │             │  │      │  • Memory files             │     │
│  │  └─────────────┘  │      │                             │     │
│  └──────────────────┘      └─────────────────────────────┘     │
│           │                                                      │
│           │  Auto-restore on boot                                 │
│           ▼                                                      │
│  ┌──────────────────┐      ┌─────────────────────────────┐     │
│  │   Git Repo        │      │   Backup Storage            │     │
│  │   (GitHub)        │      │   /data/backups/openclaw    │     │
│  │                   │      │                             │     │
│  │  • Configs        │◄─────│  • Daily backups            │     │
│  │  • Workspace      │      │  • Pre-deploy snapshots     │     │
│  │  • Scripts        │      │                             │     │
│  └──────────────────┘      └─────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │  GitHub Actions
                              ▼
                    ┌──────────────────┐
                    │  Auto-deploy     │
                    │  on git push     │
                    └──────────────────┘
```

---

## Data Flow: How It All Connects

### 1. Configuration Flow

```
GitHub Repo ──► VPS (/data/uni-openclaw-infra/) ──► Coolify ──► Container
     │                                                    │
     │                                                    ▼
     │                                            Mounted as read-only
     │                                            or read-write volumes
     │                                                    │
     └────────────────────────────────────────────────────┘
              Changes trigger auto-deploy via GitHub Actions
```

### 2. Conversation & Memory Flow

```
User Message ──► OpenClaw Gateway ──► LLM (Kimi/OpenAI/Anthropic)
                      │
                      ▼
              Session JSONL file
              (ephemeral, resets daily)
                      │
                      ▼
              QMD Vector Search
              (persistent embeddings)
                      │
                      ▼
              MEMORY.md / memory/*.md
              (persistent files)
```

**Key Point:** Sessions reset daily, but **QMD embeddings** and **memory files** persist forever.

---

## Storage Locations (Critical for Troubleshooting)

### Persistent Data (Survives Restarts)

| Data Type | Location | Backup? | Notes |
|-----------|----------|---------|-------|
| **Agent configs** | `/data/.openclaw/agents/` | ✅ Yes | Agent definitions, auth |
| **Session history** | `/data/.openclaw/agents/*/sessions/` | ✅ Yes | JSONL conversation logs |
| **QMD embeddings** | `/data/.openclaw/agents/*/qmd/` | ✅ Yes | Vector memory index |
| **OpenClaw config** | `/data/.openclaw/openclaw.json` | ✅ Yes | Main configuration |
| **Memory files** | `/data/workspace/memory/` | ✅ Yes | Daily logs |
| **Base documents** | `/data/workspace/agents/` | ✅ Yes | SOUL.md, etc. |

### Ephemeral Data (Lost on Container Restart)

| Data Type | Location | Backup? | Notes |
|-----------|----------|---------|-------|
| **Runtime sessions** | Container memory | ❌ No | Auto-reset daily anyway |
| **Temp files** | `/tmp/` | ❌ No | Not needed |

### Git-Tracked Configs (Source of Truth)

| Data Type | Git Location | Repo | Notes |
|-----------|-------------|------|-------|
| **Config** | `config/openclaw.json` | `openclaw-uni-2026` | Agent definitions, models, channels |
| **Agent SOUL/IDENTITY** | `workspace/{agent-name}/` | `openclaw-uni-2026` | e.g. `workspace/mary/SOUL.md` |
| **Memory** | `workspace/memory/` | `openclaw-uni-2026` | Daily logs, curated memories |
| **Scripts** | `scripts/` | `openclaw-uni-2026` | Backup/restore automation |
| **Platform code** | repo root | `openclaw-sean-fork` | OpenClaw core — rarely touched |
| **Mission Control UI** | repo root | `uni-mission-control` | Web dashboard |

> ⚠️ `workspace/agents/` in this repo is an **empty placeholder**. Agent files are at `workspace/{agent-name}/` (e.g. `workspace/mary/`). The docker-compose mount needs updating to match — see BACKUP_PROTOCOL.md.

### Repo Map (Verified 2026-04-06)

| Repo | GitHub Remote | VPS Path | Local Backup Path |
|------|--------------|----------|-------------------|
| `openclaw-uni-2026` | `seant15/openclaw-uni-2026` | `/data/workspace/uni-openclaw-infra/` | `openclaw-uni-2026/` |
| `openclaw-sean-fork` | `seant15/openclaw` | `/data/workspace/openclaw-sean-fork/` | `openclaw-backup/volumes/workspace/openclaw-sean-fork/` |
| `uni-mission-control` | `seant15/uni-mission-control` | `/data/workspace/mission-control/` | `openclaw-backup/volumes/workspace/mission-control/` |

---

## Session Management Strategy

### The Problem

LLMs have limited context windows. Without management:
- Sessions grow indefinitely
- Token costs explode
- Context becomes noisy

### Our Solution: Hybrid Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION LIFECYCLE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User sends message ──► Check session age                    │
│                              │                               │
│                              ▼                               │
│                    ┌─────────────────┐                      │
│                    │  Is it after    │                      │
│                    │  4 AM UTC?      │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│              ┌──────────────┼──────────────┐               │
│              │                              │               │
│              ▼                              ▼               │
│        ┌───────────┐                 ┌───────────┐         │
│        │  YES      │                 │    NO     │         │
│        │           │                 │           │         │
│        ▼           │                 ▼           │         │
│  ┌─────────────┐   │           ┌─────────────┐  │         │
│  │ Reset to    │   │           │ Continue    │  │         │
│  │ new session │   │           │ existing    │  │         │
│  │ (fresh ID)  │   │           │ session     │  │         │
│  └──────┬──────┘   │           └──────┬──────┘  │         │
│         │          │                  │         │         │
│         └──────────┴──────────────────┘         │         │
│                    │                            │         │
│                    ▼                            │         │
│         ┌─────────────────────┐                │         │
│         │ QMD Search Enabled  │                │         │
│         │ (Vector Memory)     │                │         │
│         └──────────┬──────────┘                │         │
│                    │                           │         │
│                    ▼                           │         │
│         ┌─────────────────────┐               │         │
│         │ Search across ALL   │               │         │
│         │ prior sessions      │               │         │
│         └──────────┬──────────┘               │         │
│                    │                          │         │
│                    ▼                          │         │
│         ┌─────────────────────┐              │         │
│         │ Inject relevant     │              │         │
│         │ memories into       │              │         │
│         │ context             │              │         │
│         └──────────┬──────────┘              │         │
│                    │                         │         │
│                    ▼                         │         │
│         ┌─────────────────────┐             │         │
│         │ Respond with        │             │         │
│         │ context + memory    │             │         │
│         └─────────────────────┘             │         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Session Types

| Type | Reset Policy | Use Case |
|------|--------------|----------|
| **Direct messages** | Daily 4 AM UTC | Main work with agents |
| **Slack threads** | Daily 4 AM UTC | Task-specific discussions |
| **Group chats** | Idle 2h | Ephemeral team chat |
| **Cron jobs** | Per-run | Scheduled tasks (always fresh) |

### Memory Persistence Across Sessions

Even when a session resets, we maintain continuity via:

1. **QMD Vector Search** (automatic)
   - Embeddings of all conversations
   - Semantic search across history
   - Injected into context when relevant

2. **MEMORY.md** (manual)
   - Curated long-term memory
   - You tell us what to remember
   - Loaded on every session start

3. **memory/*.md** (daily logs)
   - Automatic daily summaries
   - Raw conversation logs
   - Searchable via `memory_search` tool

---

## Security & Data Protection

### How We Prevent Data Loss

#### Layer 1: Persistent Storage
- `/data` is on a separate disk (`/dev/sda1`)
- Not affected by container restarts
- Survives OS reinstalls (if `/data` preserved)

#### Layer 2: Daily Backups
```
Schedule: Every day at 3:00 AM UTC
Location: /data/backups/openclaw/
Retention: Last 10 backups
Format: Compressed tar.gz
Contents: Everything in /data/.openclaw + workspace
```

#### Layer 3: Git Version Control
- All configs tracked in git
- Changes are auditable
- Rollback to any previous version

#### Layer 4: Auto-Restore on Boot
```
Container Starts
      │
      ▼
entrypoint.sh runs
      │
      ▼
Check for backup ──► Restore if exists ──► Start OpenClaw
```

### What Gets Backed Up

```bash
# Backup includes:
/data/.openclaw/agents/        # All agent data
/data/.openclaw/openclaw.json  # Main config
/data/workspace/MEMORY.md      # Long-term memory
/data/workspace/memory/        # Daily logs
/data/workspace/agents/        # Agent base docs
```

### What Does NOT Get Backed Up

- Runtime session state (intentional — ephemeral)
- Temporary files
- Logs (separate log rotation)

---

## Redeployment Scenarios

### Scenario 1: Config Change (Git Push)

```
You: Edit file → git commit → git push
          │
          ▼
GitHub Actions: Deploy to VPS
          │
          ▼
Coolify: Rolling update (zero downtime)
          │
          ▼
New container: Starts with new config
          │
          ▼
OpenClaw: Running with updated config
```

**Data Status:** ✅ No data loss (config only change)

### Scenario 2: VPS Restart

```
VPS: Reboot
  │
  ▼
Coolify: Auto-start services
  │
  ▼
OpenClaw Container: Start
  │
  ▼
entrypoint.sh: Check for backup
  │
  ▼
Restore: From /data/backups/openclaw/latest.tar.gz
  │
  ▼
OpenClaw: Running with restored data
```

**Data Status:** ✅ Fully restored from backup

### Scenario 3: Complete Data Loss (Worst Case)

```
Disaster: /data partition corrupted
  │
  ▼
Restore from backup:
  cd /data/uni-openclaw-infra
  ./scripts/restore.sh /data/backups/openclaw/openclaw_backup_20260226_120000.tar.gz
  │
  ▼
Restart: docker-compose restart
  │
  ▼
OpenClaw: Running with restored data
```

**Data Status:** ✅ Restored to last backup (max 24h loss)

### Scenario 4: Git Repo Corruption

```
Problem: Accidental git reset or repo corruption
  │
  ▼
Solution: Clone fresh from GitHub
  git clone https://github.com/YOUR_REPO/uni-openclaw-infra.git
  │
  ▼
Restore data: ./scripts/restore.sh
  │
  ▼
System: Back online with configs + data
```

**Data Status:** ✅ Configs from git, data from backup

---

## Troubleshooting Quick Reference

### "Agent doesn't remember our conversation"

**Check:**
1. Is QMD enabled? `openclaw config get memory.backend`
2. Are embeddings updating? Check `/data/.openclaw/agents/clover/qmd/`
3. Try manual search: Use `memory_search` tool with your query

**Fix:**
- QMD re-indexes every 15 minutes
- Force update: Restart container

### "Sessions not resetting daily"

**Check:**
1. Config loaded? `openclaw config get session.resetByType`
2. Timezone correct? Check VPS time: `date`
3. Gateway restarted after config change?

**Fix:**
```bash
# Restart to reload config
docker-compose restart
```

### "Lost all data after redeploy"

**Check:**
1. Was backup created? `ls -la /data/backups/openclaw/`
2. Did entrypoint.sh run? `docker logs openclaw-gateway | head -20`
3. Volume mounted correctly? `docker inspect openclaw-gateway | grep -A5 Mounts`

**Fix:**
```bash
# Manual restore
cd /data/uni-openclaw-infra
./scripts/restore.sh
```

### "Can't access OpenClaw gateway"

**Check:**
1. Container running? `docker ps | grep openclaw`
2. Port accessible? `curl http://localhost:18789/status`
3. Firewall blocking? `ufw status` or `iptables -L`

**Fix:**
```bash
# Check logs
docker-compose logs -f

# Restart
docker-compose down
docker-compose up -d
```

---

## Commands Reference

### Daily Operations

```bash
# Check status
openclaw status
docker-compose ps

# View logs
docker-compose logs -f

# Manual backup
./scripts/backup.sh

# Check backup list
ls -lth /data/backups/openclaw/
```

### Emergency Operations

```bash
# Restore from backup
./scripts/restore.sh [backup-file.tar.gz]

# Full reset (dangerous)
docker-compose down
rm -rf /data/.openclaw
./scripts/restore.sh

# Complete rebuild
rm -rf /data/uni-openclaw-infra
git clone <repo> /data/uni-openclaw-infra
./scripts/restore.sh
```

---

## Contact & Escalation

| Issue | Contact | Notes |
|-------|---------|-------|
| System down | Sean Tan | Primary owner |
| Config changes | GitHub PR | Review before merge |
| Data loss | Restore from backup | Last backup max 24h old |
| OpenClaw bugs | OpenClaw Discord | Community support |

---

## Document Maintenance

**Update this doc when:**
- Architecture changes
- New agents added
- Backup strategy changes
- New failure modes discovered

**Review schedule:** Quarterly

---

*This document ensures that even if the entire team changes, the next person can understand and troubleshoot the system within 30 minutes.*
