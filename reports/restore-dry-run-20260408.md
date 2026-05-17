# Restore Dry Run (Staging) — 2026-04-08

## Purpose
Verify that the latest encrypted OpenClaw backup stored in Google Drive is:
- downloadable
- decryptable with the current `age` identity key
- extractable
- contains expected critical paths

## Staging directory
- `/tmp/restore-test-20260408T074536Z`

## Remote selection
Remote:
- `gdrive-backup:OpenClawBackups/{host}`

Latest selected backup:
- `openclaw-751ea0b467fc-20260408T074226Z.tar.zst.age`

## Result
✅ Success

### Key paths present after extraction
- `openclaw.json`
- `agents/`
- `devices/`
- `memory/`
- `cron/`
- `credentials/`

## Notes
- This was a staging restore only.
- No live paths (e.g. `/data/.openclaw`) were overwritten.
- If a real restore is needed, follow `docs/RECOVERY_PROCEDURE.md` and use `scripts/restore.sh`.
