# OpenClaw VPS Backup (Drive + Encryption)

## Summary of all backup logic on this VPS
This document consolidates *all* backup-related logic found in the workspace as of 2026-03-29.
It includes legacy/local tar.gz backups and the current encrypted Google Drive pipeline.

## What is backed up (scheduled — full backup)
The daily job should run `scripts/openclaw-full-backup.sh` (on the VPS: `/data/workspace/scripts/openclaw-full-backup.sh`). It produces **two** encrypted artifacts:

1) OpenClaw runtime tree from `/data/.openclaw/` (excludes `logs/`, `media/`, `dashboard-v4/`, `backups/`, `tmp-backup/`, and `node_modules/` for the OpenClaw tar step — see script).

2) Workspace tree from `/data/workspace/` (repos + working files), via `rsync` with excludes — see script.

## Lighter alternative (OpenClaw only)
`scripts/openclaw_backup_to_gdrive.sh` tars **only** `/data/.openclaw/` and uploads a single artifact. Retention is shorter (7 days) — see that script. Use when you do not need the workspace tarball.

## Where it goes (Google Drive)
Shared Drive: `UNI Openclaw Backup 032026`
Folder:
- `OpenClawBackups/<hostname>/openclaw-<hostname>-<UTC_TIMESTAMP>.tar.zst.age`
- `OpenClawBackups/<hostname>/workspace-<hostname>-<UTC_TIMESTAMP>.tar.zst.age`

Docs/keys also stored:
- `OpenClawBackups/OPENCLAW_RESTORE_RUNBOOK.md`
- `OpenClawBackups/age.recipient`
- `OpenClawBackups/keys/openclaw_age_identity.zip.age`

## Schedule
Cron installed at:
- `/etc/cron.d/openclaw-backup` (install from `cron/openclaw-backup.cron`)
Runs:
- daily at **02:15 UTC**
Logs:
- `/data/.openclaw/logs/openclaw-backup-cron.log` (cron wrapper)
- `/data/.openclaw/logs/openclaw-backup-*.log` (per-run detail from full script)

## Scripts (this repo)
- Full backup (scheduled): `scripts/openclaw-full-backup.sh`
- OpenClaw-only backup: `scripts/openclaw_backup_to_gdrive.sh`
- Lightweight config snapshot (manual): `scripts/export-openclaw-snapshot.sh`
- Legacy local tar.gz: `scripts/backup.sh` → `/data/backups/openclaw/`

## Encryption keys
On VPS:
- PRIVATE identity: `/data/.openclaw/credentials/backup/age.key`
- PUBLIC recipient: `/data/.openclaw/credentials/backup/age.recipient`

If `age.key` is lost, backups cannot be decrypted.

## Git deploy
This repo uses GitHub SSH deploy key on the VPS (no HTTPS tokens).

## FAQ (short)
Operational Q&A (local rsync kit vs Git vs Drive, cron vs `git pull`, whether to refresh `openclaw-backup/volumes/` in parallel) is consolidated in **BACKUP_LOGIC_CONSOLIDATED.md §6** (2026-04-15).
