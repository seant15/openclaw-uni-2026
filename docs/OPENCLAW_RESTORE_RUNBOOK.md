# OpenClaw Restore Runbook (Encrypted Backup)

## What this restores
This backup captures **/data/.openclaw** (OpenClaw runtime data) excluding large/noisy folders:
- excluded: `logs/`, `media/`, `dashboard-v4/`, `backups/`, `tmp-backup/`

It includes:
- `openclaw.json`
- `agents/` + `workspace-*` (agent workspaces + memory)
- `credentials/` (sensitive)
- `cron/`
- `memory/` (incl. sqlite)

## Where backups live
Google Drive (Shared Drive) folder:
- `OpenClawBackups/<hostname>/openclaw-<hostname>-<UTC_TIMESTAMP>.tar.zst.age`

## On the VPS: required tools
- `age`
- `zstd`
- `tar`

## Locate the decryption key on the VPS
- Identity key (PRIVATE): `/data/.openclaw/credentials/backup/age.key`
- Recipient (PUBLIC): `/data/.openclaw/credentials/backup/age.recipient`

## Restore procedure (safe)
1) **Stop OpenClaw services** (so files aren’t changing during restore)
   - If you manage via systemd/docker, stop the service/container first.

2) Download the latest backup file from Drive to the VPS, e.g.:
   - `/root/restore/openclaw-....tar.zst.age`

3) Decrypt:
   - `mkdir -p /root/restore/out`
   - `age -d -i /data/.openclaw/credentials/backup/age.key -o /root/restore/out/openclaw.tar.zst /root/restore/openclaw-*.tar.zst.age`

4) Decompress:
   - `zstd -d /root/restore/out/openclaw.tar.zst -o /root/restore/out/openclaw.tar`

5) Extract to a staging directory (recommended):
   - `mkdir -p /root/restore/staging`
   - `tar -xf /root/restore/out/openclaw.tar -C /root/restore/staging`

6) Review staging contents:
   - `ls -la /root/restore/staging`
   - Confirm it looks like the expected `/data/.openclaw` tree.

7) Restore into place:
   - **Option A (safer):** move current aside, then copy in
     - `mv /data/.openclaw /data/.openclaw.bak.$(date -u +%Y%m%dT%H%M%SZ)`
     - `mkdir -p /data/.openclaw`
     - `rsync -aHAX /root/restore/staging/ /data/.openclaw/`
   - Ensure permissions remain strict on `credentials/`.

8) Start OpenClaw services again.

## Verification checklist
- OpenClaw starts without errors
- Agent memories appear intact
- Latest backups continue to run (cron log updates)

## Notes
- If you lose `/data/.openclaw/credentials/backup/age.key`, you cannot decrypt backups.
- Keep the private key offline in a separate secure location.
