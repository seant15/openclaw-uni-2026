# OpenClaw VPS Backup (Drive + Encryption)

## What is backed up
Daily encrypted backup of OpenClaw runtime state from:
- `/data/.openclaw/` (excluding `logs/`, `media/`, `dashboard-v4/`, `backups/`, `tmp-backup/`)

Includes:
- `openclaw.json`, `agents/`, `workspace-*`, `memory/`, `cron/`, `credentials/`

## Where it goes (Google Drive)
Shared Drive: `UNI Openclaw Backup 032026`
Folder:
- `OpenClawBackups/<hostname>/openclaw-<hostname>-<UTC_TIMESTAMP>.tar.zst.age`

Docs/keys also stored:
- `OpenClawBackups/OPENCLAW_RESTORE_RUNBOOK.md`
- `OpenClawBackups/age.recipient`
- `OpenClawBackups/keys/openclaw_age_identity.zip.age`

## Schedule
Cron installed at:
- `/etc/cron.d/openclaw-backup`
Runs:
- daily at **02:15 UTC**
Logs:
- `/data/.openclaw/logs/openclaw-backup.log`

## Scripts
- Backup script: `/data/workspace/scripts/openclaw_backup_to_gdrive.sh`

## Encryption keys
On VPS:
- PRIVATE identity: `/data/.openclaw/credentials/backup/age.key`
- PUBLIC recipient: `/data/.openclaw/credentials/backup/age.recipient`

If `age.key` is lost, backups cannot be decrypted.

## Git deploy
This repo uses GitHub SSH deploy key on the VPS (no HTTPS tokens).
