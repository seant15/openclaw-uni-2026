# Backup Logic (Consolidated) — OpenClaw VPS

Last updated: 2026-04-15 (UTC)

## 0) Goals
- Preserve OpenClaw runtime state (configuration + interaction/memory data).
- Keep offsite copies (Google Drive) encrypted.
- Maintain a simple restore playbook.

## 1) Current primary backup pipeline (ACTIVE — scheduled)
The script checked into **this repository** (mirrors what should exist on the VPS at `/data/workspace/scripts/`):

- `scripts/openclaw-full-backup.sh`

Reference cron snippet (install to `/etc/cron.d/openclaw-backup` or root crontab on the VPS):

- `15 2 * * * root /data/workspace/scripts/openclaw-full-backup.sh >> /data/.openclaw/logs/openclaw-backup-cron.log 2>&1`

Checked-in template (copy to `/etc/cron.d/openclaw-backup` after review):

- `cron/openclaw-backup.cron`

### 1.1 What is backed up (full script — two encrypted artifacts)
**Part A — OpenClaw runtime tree**

- Source: `/data/.openclaw/`
- Packaged from that directory with exclusions (see script `EXCLUDES` in `scripts/openclaw-full-backup.sh`), including extra exclusion of `./node_modules/**` for the OpenClaw tar step.

**Part B — Workspace tree (repos + working files)**

- Source: `/data/workspace/` copied via `rsync` into a temp folder, then tarred.
- Excludes (high level): `node_modules`, `.git/objects`, `.git/logs`, `*.log`, `tmp`, `temp` (see script).

### 1.2 Lighter alternative script (NOT the scheduled full backup)
This repo also contains a **smaller** pipeline that only tars `/data/.openclaw` and uploads one artifact:

- `/data/workspace/scripts/openclaw_backup_to_gdrive.sh`

Use it when you intentionally want “OpenClaw state only” without the workspace tarball. Retention in that script is **7 days** remote + local (see script).

### 1.3 How the full script works (summary)
1) Tar `/data/.openclaw` (with exclusions) → zstd → age → artifact in `/data/.openclaw/backups/`
2) Rsync `/data/workspace/` to temp → tar → zstd → age → second artifact in `/data/.openclaw/backups/`
3) `rclone copyto` both artifacts to `gdrive-backup:OpenClawBackups/<hostname>/`
4) Retention (full script): remote **14 days** (`336h`), local encrypted files **7 days**, per-run log files **30 days** (see script)

Output artifact names (full script):

- `openclaw-<hostname>-<YYYYMMDDTHHMMSSZ>.tar.zst.age`
- `workspace-<hostname>-<YYYYMMDDTHHMMSSZ>.tar.zst.age`

Local output directory:

- `/data/.openclaw/backups/`

Per-run detailed log (full script):

- `/data/.openclaw/logs/openclaw-backup-<YYYYMMDDTHHMMSSZ>.log`

Cron wrapper log (stdout/stderr from cron line above):

- `/data/.openclaw/logs/openclaw-backup-cron.log`

### 1.4 Encryption keys (age)
On VPS:
- PRIVATE identity: `/data/.openclaw/credentials/backup/age.key`
- PUBLIC recipient: `/data/.openclaw/credentials/backup/age.recipient`

Offsite (Drive):
- Public recipient: `OpenClawBackups/age.recipient`
- Encrypted export of private identity: `OpenClawBackups/keys/openclaw_age_identity.zip.age`

Security note:
- If `age.key` is lost, backups cannot be decrypted.

### 1.5 Google Drive target
- Uses a **Shared Drive** (Team Drive) to avoid service account quota limitations.
- rclone remote: `gdrive-backup`
- Root folder: `OpenClawBackups/`
- Per-host folder: `OpenClawBackups/<hostname>/`

rclone config:
- `/data/.config/rclone/rclone.conf`

Service account key:
- `/data/.openclaw/credentials/gdrive/sa.json`

### 1.6 Schedule (cron)
Installed at:
- `/etc/cron.d/openclaw-backup` (after copying from `cron/openclaw-backup.cron`)

Runs:
- Daily at **02:15 UTC**

Logs:
- `/data/.openclaw/logs/openclaw-backup-cron.log` (cron wrapper)
- `/data/.openclaw/logs/openclaw-backup-*.log` (per run, full script)

### 1.7 Restore documentation (ACTIVE)
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


## 6) FAQ & decisions (consolidated 2026-04-15)

Chinese summary for future readers (same answers as discussed in ops review).

**Q1:本机 `openclaw-backup/scripts/backup.sh`（第三条线）这样设对不对？OpenClaw 的 config 是不是主要在 `uni-claw` 里就备份够了？**

- 第三条线做的是：SSH 到 VPS → `pg_dump`（Coolify DB）→ 按脚本里的 `OPENCLAW_DATA_PATH`（默认 `/opt/openclaw/data`）rsync 到本机 `openclaw-backup/volumes/`。是否「对」以 **VPS 上容器实际 bind mount** 为准；若以后部署改了数据目录，必须同步改脚本里的 `OPENCLAW_DATA_PATH`，否则会出现少备或备错路径。建议在 VPS 上对 OpenClaw 容器做一次 `docker inspect`，核对挂载路径与变量一致。
- **配置分两层，不能互相替代：**
  - **Git（本机 `uni-claw` /远端 `openclaw-uni-2026`）**：版本化的「源」——`config/openclaw.json`、`workspace/*/SOUL.md` 等，协作与回滚以这里为准。
  - **线上磁盘（通常对应 `/data/.openclaw/` 等）**：实际运行态、cron、`jobs.json`、凭证布局等，**不一定**与 Git 逐字一致。
  - **`openclaw-backup/volumes/`**：是 `OPENCLAW_DATA_PATH` 下 **现场磁盘快照**，不是「只备份 uni-claw」。因此：**uni-claw = 已提交的配置与设计；volumes = 线上真实状态**，两条线角色不同。

**Q2: 文档/脚本合并到 Git 后，VPS `git pull` 是否就等于「优化完成」？**

- **否。** `git pull` 只更新工作区里的文件。
- **加密定时备份** 还要求系统 cron 已安装且指向 `openclaw-full-backup.sh`（例如将 `cron/openclaw-backup.cron` 安装到 `/etc/cron.d/openclaw-backup`）。**Pull 代码不会自动安装或修改 cron**，需单独验收（见 `openclaw-backup/volumes/workspace/BACKUP_ANALYSIS_AND_COORDINATION.md` 中的诊断思路，但以当前机器为准）。

**Q3: 是否需要「并行」维护本机 `uni-claw` 与 `openclaw-backup/volumes/`？**

- **不必**当成同一类重复全量备份。
- **推荐分工：** 日常开发与提交走 `uni-claw`（Git）；需要对照线上真实文件、大范围 IDE 检索、或做恢复演练时，再运行本机 `openclaw-backup/scripts/backup.sh` 刷新 `volumes/`（可按周或发版前，不必每次提交都跟跑）。
- 若从不查线上磁盘，可弱化 rsync；一旦要查 cron、凭证路径或与仓库不一致的现场差异，**没有 volumes 镜像会很不方便**。

**Windows 工作区总览** 见 `D:\AI SPACE SANDBOX\PATHS.md` 与 `openclaw-ops\LOCAL_BACKUP_ARCHIVE.md`；Git 真源为 `repos/openclaw-uni-2026`，VPS 镜像为 `mirrors/vps-openclaw`。
