# Migration: uni-claw-config → openclaw-uni-2026

Date: 2026-05-17 (America/Phoenix)

## What changed

- All unique content from `seant15/uni-claw-config` was merged into `seant15/openclaw-uni-2026`.
- `docs/`, `deploy/`, `migrations/`, `reports/`, `slack-integration/`, and extra `scripts/` were added.
- Root-level markdown/SQL from the old repo live under `docs/legacy-uni-claw-config/`.
- GitHub repo `uni-claw-config` is retired after this merge is pushed.

## VPS action (when you next SSH)

```bash
cd /data/workspace/uni-openclaw-infra
git pull origin main
# If a separate uni-claw-config clone still exists under /data/workspace:
# git -C /data/workspace remote -v   # confirm, then remove stale clone after backup
```

## Local path action

Workspaces moved from `C:\Users\stan8\OPENCLAW_*` to `D:\AI SPACE SANDBOX\workspaces\`. See sandbox root `PATHS.md`.
