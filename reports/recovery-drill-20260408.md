# Recovery Drill Report — 2026-04-08

## Objectives
- Complete P0 items:
  1) Fix OpenClaw config file permissions (CRITICAL)
  2) Document Coolify deployment variables & required persistence (no secrets)
  3) Run a real encrypted backup as a recovery prerequisite

## Results

### P0-1: Security audit CRITICAL fix
- File: `/data/.openclaw/openclaw.json`
- Before: mode `644` (world-readable)
- After:  mode `600`
- Timestamp (UTC): 2026-04-08 07:41

### P0-2: Coolify deployment documentation
Added to `uni-claw-config`:
- `deploy/coolify/OPENCLAW.env.example`
- `deploy/coolify/README.md`

Notes:
- Variable names only; values must live in Coolify UI.
- Confirms the critical persistence requirement: host `/data` -> container `/data`.

### P0-3: Backup run (encrypted) — executed
Backup script executed:
- `/data/workspace/scripts/openclaw-full-backup.sh`

Run timestamp (UTC): 2026-04-08T07:42:26Z

Artifacts created (local):
- `/data/.openclaw/backups/openclaw-751ea0b467fc-20260408T074226Z.tar.zst.age` (~42MB)
- `/data/.openclaw/backups/workspace-751ea0b467fc-20260408T074226Z.tar.zst.age` (~628KB)

Upload:
- Uploaded to Google Drive via rclone remote: `gdrive-backup:OpenClawBackups/{host}/...`

Log:
- `/data/.openclaw/logs/openclaw-backup-20260408T074226Z.log`

## Follow-ups
- (Recommended) Perform a dry restore to a staging directory (do not overwrite live `/data/.openclaw`):
  - download one backup
  - decrypt
  - extract to `/tmp/restore-test/`
  - confirm expected paths exist
