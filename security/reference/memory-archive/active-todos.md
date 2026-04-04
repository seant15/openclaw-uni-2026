# Active TODOs (Ops Hardening)

## Open questions
- Decide final Kimi provider wiring + exact model id used in OpenClaw.
- Add weekly memory compactor cron (Fri 07:00, tz TBD) that posts to both chat + Slack.

## TODO (Ops hardening)
- Secret management: move away from local plaintext `.env` storage; evaluate Doppler or 1Password CLI.
- Monitoring + alerting: add real-time resource monitoring (RAM/CPU/disk) with alerts (Grafana stack or simple Discord/Slack webhook).
- Silent failure prevention: add verification + alerting for backups/sync (pg_dump validation + periodic restore test; rsync exit-code checks + webhook alerts).
- Agent execution audit log: write who/when/what for every agent invocation to Supabase `agent_executions` (traceability for mis-ops).
- Quarterly restore drill: run full restore rehearsal in staging; calendar reminder is sufficient ("backups untested = backups worthless").
- Versioning for MEMORY + configs: ensure `MEMORY.md` + `openclaw.json` changes are recoverable (git tags like `vYYYY.M.DD` after updates; pair with auto_sync).
- QMD health dashboard: Datie weekly system health brief (Mon/Thu): backup status, QMD index freshness, API token expiry, agent activity → post to Slack.
- Cross-agent knowledge broadcast: when an agent finds important items, write a "cross-agent notice" entry that others read on startup.
- Known Mistakes list: start filling real entries so failures become reusable lessons.
- Backup health check + DM alerts: daily (04:00 MST) check "successful backup in last 24h" (Drive via `rclone ls`); if missing, DM Sean + Clover (cron + openclaw message).
- Disaster-recovery completeness: include scheduler tables in DB dumps/restores (overwrite `scheduled_tasks` + `scheduled_task_executions`) so all scheduled automations + execution history return automatically after a VPS rebuild.
