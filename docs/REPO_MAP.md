# Repo Map (UNI OpenClaw System)

Canonical as of 2026-05-17. The former `seant15/uni-claw-config` repository was merged into this repo and archived on GitHub.

## 1) OpenClaw infra + agent config (this repo)

- GitHub: `seant15/openclaw-uni-2026`
- Local clone (Windows): `D:\AI SPACE SANDBOX\workspaces\openclaw-ops\repos\openclaw-uni-2026`
- VPS path: `/data/workspace/uni-openclaw-infra/`
- Purpose: Coolify/docker, `config/openclaw.json`, agent `workspace/{agent}/`, backup scripts under `scripts/`, ops docs under `docs/`

## 2) OpenClaw runtime (Docker image)

- Upstream: `coollabsio/openclaw`
- Runtime state on VPS: `/data/.openclaw` (encrypted Drive backups via `scripts/openclaw-full-backup.sh`)

## 3) Platform fork (rare changes)

- GitHub: `seant15/openclaw`
- VPS: `/data/workspace/openclaw-sean-fork/`

## 4) Mission Control (dashboard)

- GitHub: `seant15/uni-mission-control`
- Local: `D:\AI SPACE SANDBOX\workspaces\marketing-stack\repos\mission-control`
- VPS: `/data/workspace/mission-control/`

## 5) Ads / warehouse sync

- GitHub: `seant15/ads_data_sync_v1`
- Local: `D:\AI SPACE SANDBOX\workspaces\marketing-stack\repos\ads-data-sync`
- VPS: `/root/openclaw/execution` or `/data/workspace/` (see `ads-data-sync/docs/AGENT_HANDOFF.md`)

## 6) Local VPS mirror (not git)

- Path: `D:\AI SPACE SANDBOX\workspaces\openclaw-ops\mirrors\vps-openclaw`
- Script: `mirrors/vps-openclaw/scripts/backup.sh` (rsync + pg_dump from VPS)

## Legacy

- `docs/legacy-uni-claw-config/` — files imported from the deleted `uni-claw-config` repo (2026-05-17).
- Historical references to `uni-claw-config` in old runbooks mean **this repo**.
