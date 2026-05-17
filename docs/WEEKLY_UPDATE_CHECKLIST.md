# Weekly Update Checklist (Manual)

This checklist defines a safe weekly update rhythm for the UNI OpenClaw system.

**Principle:** update intentionally, with a rollback path.

## 0) Decide update scope

- OpenClaw runtime (coollabsio/openclaw image / compose)
- UNI Claw Config repo (this repo)
- Mission Control / Control Center apps (separate repos)

Do **not** update everything at once unless necessary.

## 1) Pre-flight snapshot (required)

1. Confirm the system is healthy.
2. Run/verify the encrypted backup.

Suggested commands (examples):

```bash
# Check current OpenClaw status
openclaw status

# Optional: run a fresh backup (if not already scheduled)
/data/workspace/scripts/openclaw-full-backup.sh
```

## 2) Update UNI Claw Config (git)

```bash
cd /data/workspace

git status
# Ensure no accidental local edits exist before pulling

git pull --ff-only
```

## 3) Update OpenClaw Docker runtime (Coolify)

In Coolify:
- Pull latest image (or rebuild) for the OpenClaw app.
- Redeploy.

If you pin versions, update the pin deliberately (e.g., only move to a known-good tag).

## 4) Post-update validation (smoke tests)

- Web UI loads.
- Slack DM replies work.
- Critical cron jobs still run.
- No new security audit critical warnings.

Suggested:

```bash
openclaw status
openclaw security audit || true
```

## 5) Rollback plan

If anything breaks:
1. Roll back the Coolify deployment (previous image / previous build).
2. If runtime state is corrupted, restore `/data/.openclaw` from encrypted backup.
3. Document what changed (commit message + short incident note).

## 6) Document the update

Add a short note under `reports/` (date + what was updated + outcome).
