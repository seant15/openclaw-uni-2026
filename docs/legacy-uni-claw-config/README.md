# UNI Claw Config

This repository is the **configuration + operational runbook** for **UNI Marketing Agency's** OpenClaw deployment.

- Owner/Operator: **seant15 (Sean)**
- Purpose: provide a *recoverable*, *auditable*, and *upgrade-friendly* baseline for our AI central system (OpenClaw) running on a Coolify VPS.

> English only (per team convention).

## What this repo is (and is not)

### This repo **IS**
- The canonical place for:
  - Agent identity + operating principles (e.g. `SOUL.md`, `AGENTS.md`, `MEMORY.md`)
  - Ops docs / runbooks (restore, security, architecture)
  - Automation scripts (backup, secret tooling, reporting automation)
  - Schemas / migrations / infra notes that are part of the UNI system

### This repo **IS NOT**
- The OpenClaw upstream source code repository.
- A place to store secrets.

## High-level architecture

### GitHub repos (logical)

1. **OpenClaw runtime (Docker image + compose wrappers)**
   - Upstream: `coollabsio/openclaw`
   - Used because we operate via **Coolify** and want containerized deployment.

2. **UNI Claw Config (this repo)**
   - `seant15/uni-claw-config`
   - Holds configuration, scripts, and runbooks.

3. **Mission Control (data dashboard)**
   - Repo: `seant15/uni-mission-control`
   - Local path: `/data/workspace/mission-control`

4. **Monitoring UI ("Control Center")**
   - Not found at `/data/workspace/openclaw-control-center` on this VPS.
   - Found instead:
     - Local path: `/data/.openclaw/dashboard-v4`
     - Remote: `seant15/uni-dashboard-v3`
   - See `docs/REPO_MAP.md` for the authoritative mapping and next actions.

### VPS filesystem layout (physical)

- Base workspace root: `/data/workspace`
  - This repo is cloned/managed here.

- OpenClaw runtime data (NOT in git; backed up encrypted): `/data/.openclaw`
  - Contains runtime state, devices, logs, delivery queue, etc.
  - Credentials are **never committed**.

## Coolify/Docker runtime layout (summary)

The OpenClaw runtime is deployed via Coolify using Docker. The critical concept is **persistent storage**:

- The container must mount a persistent host path or volume to `/data` in the container.
- On the VPS, our durable runtime state lives under `/data/.openclaw` (encrypted backups).
- This repo (`/data/workspace`) contains scripts and runbooks, not secrets.

If `/data` is not persisted correctly, redeploys will appear to "lose" configuration.

## Backup & recovery principles

### Secrets policy
- **No secrets in git**, even private repos.
- Secrets/credentials live in runtime locations and are backed up via **encrypted backups**.

### What must be recoverable
- Worst-case recovery goal: a fresh VPS can be restored by:
  1) pulling this repo
  2) deploying the Dockerized OpenClaw stack via Coolify
  3) restoring encrypted backups for runtime state

## Repository boundaries (important)

We intentionally keep major subsystems in separate repos:
- `mission-control/` belongs to `seant15/uni-mission-control`
- `uni-marketing/` belongs to `seant15/uni-marketing`

This repo should not absorb those histories.

## Local development notes

### Git hygiene
- `.gitignore` intentionally excludes:
  - `/data/.openclaw` runtime state
  - `snapshots/`
  - `openclaw.json.backup.*`
  - any `.env*` files

### Weekly upstream update
We do **manual weekly** updates (no auto-merge) to reduce risk.

---

## Appendix: key documents

- Recovery procedure (Coolify/Docker): `docs/RECOVERY_PROCEDURE.md`
- Restore helper script: `scripts/restore.sh`
- Backup architecture: `BACKUP_ARCHITECTURE.md`
- Workspace resolution (persona file loading): `docs/WORKSPACE_RESOLUTION.md`
- Repo map: `docs/REPO_MAP.md`
- Weekly update checklist: `docs/WEEKLY_UPDATE_CHECKLIST.md`
