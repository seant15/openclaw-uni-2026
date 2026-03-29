# Backup Logic (Consolidated) — OpenClaw VPS

Last updated: 2026-03-29 (UTC)

## 0) Goals
- Preserve OpenClaw runtime state (configuration + interaction/memory data).
- Keep offsite copies (Google Drive) encrypted.
- Maintain a simple restore playbook.

## 1) Current primary backup pipeline (ACTIVE)
### 1.1 What is backed up
Source: `/data/.openclaw/`

Included (implicitly):
- `openclaw.json`
- `agents/` + `workspace-*` (agent workspaces and memory)
- `memory/` (incl. sqlite)
- `credentials/` (sensitive)
- `cron/`

Excluded (to avoid noise/size):
- `logs/`
- `media/`
- `dashboard-v4/` (large static assets)
- `backups/` (to avoid self-inclusion)
- `tmp-backup/`

Implementation: `/data/workspace/scripts/openclaw_backup_to_gdrive.sh`

### 1.2 How it works
1) Tar `/data/.openclaw` with exclusions
2) Compress with zstd
3) Encrypt with age using a local keypair (non-interactive)
4) Upload encrypted artifact to Google Drive via rclone
5) Retention: delete remote + local artifacts older than 7 days

Output artifact name:
- `openclaw-<hostname>-<YYYYMMDDTHHMMSSZ>.tar.zst.age`

Local output directory:
- `/data/.openclaw/backups/`

### 1.3 Encryption keys (age)
On VPS:
- PRIVATE identity: `/data/.openclaw/credentials/backup/age.key`
- PUBLIC recipient: `/data/.openclaw/credentials/backup/age.recipient`

Offsite (Drive):
- Public recipient: `OpenClawBackups/age.recipient`
- Encrypted export of private identity: `OpenClawBackups/keys/openclaw_age_identity.zip.age`

Security note:
- If `age.key` is lost, backups cannot be decrypted.

### 1.4 Google Drive target
- Uses a **Shared Drive** (Team Drive) to avoid service account quota limitations.
- rclone remote: `gdrive-backup`
- Root folder: `OpenClawBackups/`
- Per-host folder: `OpenClawBackups/<hostname>/`

rclone config:
- `/data/.config/rclone/rclone.conf`

Service account key:
- `/data/.openclaw/credentials/gdrive/sa.json`

### 1.5 Schedule (cron)
Installed at:
- `/etc/cron.d/openclaw-backup`

Runs:
- Daily at **02:15 UTC**

Logs:
- `/data/.openclaw/logs/openclaw-backup.log`

### 1.6 Restore documentation (ACTIVE)
- Runbook file: `/data/workspace/docs/OPENCLAW_RESTORE_RUNBOOK.md`
- Uploaded to Drive: `OpenClawBackups/OPENCLAW_RESTORE_RUNBOOK.md`


## 2) Snapshot export (AUXILIARY)
Script:
- `/data/workspace/scripts/export-openclaw-snapshot.sh`

Purpose:
- Exports a lightweight snapshot of config + agent configs into:
  - `/data/workspace/snapshots/openclaw/<YYYY-MM-DD>/...`
- Produces a `MANIFEST.txt` with SHA256 hashes for auditability.

Note:
- This is not currently scheduled by cron.


## 3) Legacy/local backups (PRESENT but not the primary path)
These scripts exist and create local tar.gz backups. They are useful for quick pre-redeploy backups but are not encrypted/offsite by default.

### 3.1 Local OpenClaw tar.gz backup
- `/data/workspace/backup-openclaw.sh`
- `/data/workspace/uni-openclaw-infra/scripts/backup.sh`

Behavior:
- Creates: `/data/backups/openclaw/openclaw_backup_<timestamp>.tar.gz`
- Keeps last 10 backups (local)

### 3.2 Local workspace/memory backups
- `/data/workspace/agent_backup.sh`

Behavior:
- Creates:
  - `/data/agent_backups/agent_backup_<timestamp>_workspace.tar.gz`
  - `/data/agent_backups/agent_backup_<timestamp>_memory.tar.gz`
- Keeps last 5 (local)

### 3.3 Legacy restore helper
- `/data/workspace/uni-openclaw-infra/scripts/restore.sh`

Behavior:
- Restores from `/data/backups/openclaw/*.tar.gz`
- Stops gateway via `pkill -f openclaw-gateway` then extracts to `/`


## 4) Git backup (CONFIG / CODE)
- No cron-based auto-commit is configured.
- Infra repo uses SSH deploy key on VPS (no HTTPS tokens).


## 5) Recommended next hardening steps (optional)
- Decide whether to include/exclude `dashboard-v4/` in the encrypted Drive backup.
- Add a health check: verify a successful backup exists in the last 24h and DM on failure.
- Rotate and securely archive the age identity key offline (separate from Drive).
