# Backup & Git Protocol
**Last Updated:** 2026-04-06
**Maintained by:** UNI Marketing / Sean Tan
**Status:** Verified and audited

---

## The Golden Rule

> **One source of truth per type of file. Know where it lives. Commit it there.**

---

## Repo Map (Verified 2026-04-06)

| Repo | GitHub | VPS Path | Local Path | Purpose |
|------|--------|----------|------------|---------|
| `openclaw-uni-2026` | `seant15/openclaw-uni-2026` | `/data/workspace/uni-openclaw-infra/` | `OPENCLAW_LOCAL_032026/openclaw-uni-2026/` | **Infra + agent configs** — Coolify deploys this. Source of truth for SOUL.md, IDENTITY.md, docker-compose. |
| `openclaw-sean-fork` | `seant15/openclaw` | `/data/workspace/openclaw-sean-fork/` | `openclaw-backup/volumes/workspace/openclaw-sean-fork/` | **OpenClaw platform code** — fork of official openclaw. Don't put agent configs here. |
| `uni-mission-control` | `seant15/uni-mission-control` | `/data/workspace/mission-control/` | `openclaw-backup/volumes/workspace/mission-control/` | **Mission Control UI** — the web dashboard. |

> ⚠️ **Common mistake:** VPS doc previously listed mission-control as `TianyiDataScience/openclaw-control-center`. This was wrong. Actual remote is `seant15/uni-mission-control`.

---

## Where Agent Files Live (Source of Truth)

```
openclaw-uni-2026/
├── workspace/
│   ├── clover/          ← Clover's SOUL.md, IDENTITY.md, etc.
│   ├── mary/            ← Mary's SOUL.md, IDENTITY.md, etc.
│   ├── kimi/            ← Kimi's files
│   ├── datie/           ← Datie's files
│   └── writer/          ← Writer's files
├── agents/              ← Runtime agent metadata (HEARTBEAT, MARY.md, etc.)
│   ├── clover/
│   ├── mary/
│   └── ...
└── config/
    └── openclaw.json    ← Main OpenClaw config (models, channels, agents)
```

> ⚠️ `workspace/agents/` is an **empty placeholder** (`.gitkeep` only). The agent files are at `workspace/{agent-name}/` — NOT `workspace/agents/{agent-name}/`. The docker-compose mount needs updating to reflect this (see Known Issues).

---

## Three-Layer Backup System

### Layer 1 — Git (Code & Configs)
**What:** All agent SOUL.md, IDENTITY.md, docker-compose, openclaw.json
**Where:** `seant15/openclaw-uni-2026`
**When to commit:** Any time you change agent behavior, add an agent, change models, update docker config
**Trigger:** Manual — you push
**Recovery:** `git clone → docker-compose up`

### Layer 2 — Google Drive (Encrypted Daily Backup)
**What:** Full VPS state — `/data/.openclaw/` + `/data/workspace/`
**When:** Automatically at 02:15 UTC daily via cron
**Location:** `Google Drive → OpenClawBackups/{hostname}/`
**Recovery:** Download → decrypt (age) → restore to `/data/` → restart
**Last verified:** 2026-04-06

### Layer 3 — Local rsync Backup (This Folder)
**What:** Full VPS rsync snapshot
**Where:** `OPENCLAW_LOCAL_032026/openclaw-backup/volumes/`
**When:** Run `openclaw-backup/scripts/backup.sh` manually or on schedule
**Purpose:** Offline access, AI-assisted debugging, disaster recovery
**NOT a git backup** — this is a filesystem snapshot, not version history

---

## What Triggers a Commit

| Action | Commit to | Notes |
|--------|-----------|-------|
| Change agent SOUL.md or IDENTITY.md | `openclaw-uni-2026` (`workspace/{agent}/`) | Most common |
| Add new agent | `openclaw-uni-2026` (`workspace/` + `config/openclaw.json`) | Update both |
| Change model assignments | `openclaw-uni-2026` (`config/openclaw.json`) | |
| Change docker ports / services | `openclaw-uni-2026` (`docker-compose.yml`) | Coolify auto-deploys on push |
| Fix platform code / OpenClaw core | `openclaw-sean-fork` | Rare |
| Update Mission Control UI | `uni-mission-control` | |
| Change secrets / .env | ❌ Never commit | VPS-local only |

**Rule of thumb:** If you changed a file inside `openclaw-uni-2026/`, commit it. Everything else is either a secret (don't commit) or platform code (different repo).

---

## Git Workflow (Daily Use)

### Making a change to an agent
```bash
# 1. Edit the file locally in OPENCLAW_LOCAL_032026/openclaw-uni-2026/
#    e.g. workspace/mary/SOUL.md

# 2. Commit
cd OPENCLAW_LOCAL_032026/openclaw-uni-2026
git add workspace/mary/SOUL.md
git commit -m "refactor(mary): [what changed and why]"

# 3. Before push, check what's on remote
git fetch origin
git log HEAD..origin/main --oneline   # what remote has that we don't
git log origin/main..HEAD --oneline   # what we have that remote doesn't

# 4. If remote has new commits, rebase (not merge)
git pull --rebase origin main

# 5. Push
git push origin main
```

### Checking sync status
```bash
# Are we behind remote?
git fetch origin && git log HEAD..origin/main --oneline
# Empty = we're up to date

# Do we have uncommitted changes?
git status --short | grep "^[AM]"
```

---

## Known Issues (As of 2026-04-06)

### 1. docker-compose mount mismatch
**Problem:** docker-compose.yml mounts `./workspace/agents` but that folder is empty. Agent files are at `./workspace/{agent-name}/`.
**Impact:** Agent configs from this repo are NOT being injected into the container at deploy time. Agents currently read from the persistent volume instead.
**Fix needed (VPS):**
```yaml
# Replace in docker-compose.yml:
# - ./workspace/agents:/home/openclaw/.openclaw/workspace/agents:ro
# With individual mounts:
- ./workspace/clover:/home/openclaw/.openclaw/workspace/agents/clover:ro
- ./workspace/mary:/home/openclaw/.openclaw/workspace/agents/mary:ro
- ./workspace/kimi:/home/openclaw/.openclaw/workspace/agents/kimi:ro
- ./workspace/datie:/home/openclaw/.openclaw/workspace/agents/datie:ro
- ./workspace/writer:/home/openclaw/.openclaw/workspace/agents/writer:ro
```

### 2. VPS workspace root has no GitHub remote
**Problem:** `/data/workspace/` root is a local git repo with no remote. Changes made directly on VPS (outside the 3 sub-repos) are not backed up to GitHub.
**Fix needed (VPS):** Either migrate workspace-root agent files into `openclaw-uni-2026`, or add a remote.

### 3. Git index.lock files persist on Windows-mounted folders
**Problem:** When running git from the Linux sandbox (Cowork/Claude), lock files can't be deleted due to NTFS filesystem restrictions.
**Workaround:** Delete from Windows PowerShell: `Remove-Item "repo\.git\index.lock" -Force`

---

## Security Rules

1. **Never embed tokens in git remote URLs.** Use credential store or SSH.
   ```bash
   # Wrong:
   git remote add origin https://ghp_TOKEN@github.com/user/repo.git

   # Right:
   git remote add origin https://github.com/user/repo.git
   git config --global credential.helper store
   # Or use SSH:
   git remote add origin git@github.com:user/repo.git
   ```

2. **Never commit .env files.** All secrets stay on VPS only.

3. **Rotate tokens if they appear in git history or config.** Go to https://github.com/settings/tokens immediately.

---

## Disaster Recovery Order

```
VPS completely lost
        │
        ▼
1. Spin up new VPS
        │
        ▼
2. git clone seant15/openclaw-uni-2026 → /data/uni-openclaw-infra/
        │
        ▼
3. Download latest backup from Google Drive → decrypt → restore /data/.openclaw/
        │
        ▼
4. Copy .env file (stored separately, never in git)
        │
        ▼
5. docker-compose up -d
        │
        ▼
6. Verify at http://VPS_IP:18789/status
```

Estimated recovery time: 30–60 minutes.

---

## For AI Assistants Reading This

When helping with this system:
- **Agent config files** (SOUL.md, IDENTITY.md) → commit to `openclaw-uni-2026`, path `workspace/{agent-name}/`
- **Do not touch** `.env` files or secrets
- **Always check** `git log HEAD..origin/main` before pushing
- **Use** `git pull --rebase origin main` not `git merge` when behind remote
- **Lock files** on Windows-mounted repos: tell user to run `Remove-Item "repo\.git\index.lock" -Force` from PowerShell
- **Source of truth** for who's running what: `config/openclaw.json`
