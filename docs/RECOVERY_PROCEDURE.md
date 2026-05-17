# Recovery Procedure (Coolify + Docker)

This document describes how to recover the UNI OpenClaw system on a fresh VPS or after a major failure.

**Goal:** with minimal manual steps, we can restore the system by (1) pulling code/config from git, (2) deploying via Coolify, and (3) restoring encrypted runtime backups.

## Scope

### In scope
- OpenClaw runtime state under `/data/.openclaw` (restored from encrypted backup)
- OpenClaw uni infra repo (`seant15/openclaw-uni-2026`) (runbooks + scripts + infra notes; merged former uni-claw-config)
- Coolify-managed services (OpenClaw container stack, Mission Control, Control Center)

### Out of scope
- Provider-side recovery (Slack app recreation, Supabase project recreation) unless explicitly required.

## Preconditions / assumptions

- You have SSH access to the VPS.
- You can access Coolify admin UI for redeploy.
- You have access to the encrypted backup store (Google Drive via rclone).
- You have the `age` private key required to decrypt backups.

## System components (what exists)

### 1) UNI Claw Config (this repo)
- Holds configuration documents and scripts.
- **No secrets are stored in git.**

### 2) OpenClaw runtime data (encrypted backup)
- Path: `/data/.openclaw`
- Contains runtime state (paired devices, delivery queue, logs, etc.)
- **Credentials are not committed to git** and must be recovered from encrypted backups.

### 3) Coolify services (Docker)
Typical pattern:
- One or more Coolify applications running Docker containers.
- OpenClaw service uses a persistent volume mounted to `/data` (or binds `/data` from the host).

## Recovery checklist (high-level)

1. **Provision VPS** (OS + networking) and install Docker.
2. **Install / restore backup tooling** (rclone + age + zstd).
3. **Restore encrypted backup** to recover `/data/.openclaw` and relevant workspace paths.
4. **Deploy containers via Coolify**.
5. **Validate** (web UI, Slack, cron jobs, health signals).

## Step-by-step

### Step 0 — Confirm what failed
- Determine whether the failure is:
  - (A) container-level (Coolify redeploy fixes it)
  - (B) runtime data corruption under `/data/.openclaw`
  - (C) infra/networking issue (DNS, TLS, reverse proxy)

### Step 1 — Pull configuration repo
On the VPS:

```bash
cd /data/workspace
# If the directory is missing, create it
mkdir -p /data/workspace
cd /data/workspace

# Clone openclaw-uni-2026 (read-only is fine for recovery)
# (Use SSH if deploy keys are configured)
# git clone git@github.com:seant15/openclaw-uni-2026.git .
```

If the repo already exists:

```bash
git pull --ff-only
```

### Step 2 — Restore encrypted backups
**Source of truth:** see `BACKUP_ARCHITECTURE.md` and `scripts/openclaw-full-backup.sh`.

Typical restore sequence:

```bash
# 1) list backups
# rclone ls <remote>:

# 2) download backup
# rclone copy <remote>:<path>/<file>.age /tmp/

# 3) decrypt
# age -d -i /data/.openclaw/credentials/backup/age.key -o /tmp/backup.tar.zst /tmp/<file>.age

# 4) unpack
# zstd -d /tmp/backup.tar.zst -o /tmp/backup.tar
# tar -xf /tmp/backup.tar -C /
```

**Important:** do not overwrite working data unless you intend to roll back. Prefer restoring to a staging directory first if the system is partially functional.

### Step 3 — Redeploy via Coolify
In Coolify UI:

- Redeploy the OpenClaw application.
- Confirm the service mounts persistent storage (volume or bind mount) correctly.
- Confirm required environment variables are present (but not stored in git).

### Step 4 — Validate
Validation checklist:

- OpenClaw web UI loads.
- Slack DM replies work.
- Pairing / allowlist behavior is correct.
- Cron jobs / scheduled scripts still run.

## Notes / gotchas

- `openclaw.json.backup.*` files contain historical secrets/tokens and are intentionally ignored by git.
- `mission-control/execution/.env*` may contain Supabase service role keys; never commit.

## Next improvements

- Add a single `scripts/restore.sh` wrapper that:
  - fetches latest backup
  - restores to the correct locations
  - performs post-restore sanity checks
