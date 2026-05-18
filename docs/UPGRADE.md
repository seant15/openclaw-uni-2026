# OpenClaw upgrade runbook (Coolify + coollabsio images)

Track A: application binary comes from **Docker Hub** `coollabsio/openclaw:<tag>`.  
This repo (`openclaw-uni-2026`) only owns compose, agents, and `config/openclaw.json` — not `openclaw/openclaw` source.

## Before every upgrade

1. Confirm encrypted backup (see `BACKUP_ARCHITECTURE.md` / `scripts/openclaw-full-backup.sh`).
2. Note current version:
   ```bash
   docker exec openclaw-<app-id> openclaw --version
   ```
3. Check new tag on Docker Hub: `coollabsio/openclaw` (or coollabsio GitHub releases).

## Upgrade steps

1. In Coolify **Environment**, set `OPENCLAW_IMAGE_TAG` to a tag that exists on Docker Hub (e.g. `2026.5.12`; for Paperclip use `2026.5.7` — there is no `2026.5.10`),  
   or edit `deploy/coolify/docker-compose.yml` `image:` line and push to `main`.
2. Coolify: enable **Pull latest image** → **Redeploy** (recreate containers).
3. Verify on VPS:
   ```bash
   docker exec openclaw-<container> openclaw --version
   docker inspect openclaw-<container> --format '{{.Image}}'
   curl -sI -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9090/
   curl -sI -o /dev/null -w '%{http_code}\n' https://open.uni-agency.com/
   ```
4. Smoke: Slack socket, one agent DM, Control UI if used.
5. Optional: `docker exec openclaw-<container> openclaw doctor` (updates config meta).

## Rollback

1. Set `OPENCLAW_IMAGE_TAG` back to the previous working tag.
2. Redeploy with pull.
3. `/opt/openclaw/data` is unchanged; no git rollback of app source required.

## What we do not do for routine upgrades

- `git pull` on `openclaw/openclaw` on the VPS
- Merge `seant15/openclaw` (coollabsio fork) unless reviving custom GHCR builds (Track B)
- Rely on `:latest` without verifying digest after pull

## Traefik / HTTPS

- UI must listen on **9090** inside the container; domain must route to **9090** (see `docker-compose.yml`).
- If HTTPS returns 502 but `curl http://<vps-ip>:9090` is 200, check Traefik labels on the openclaw container:

  ```bash
  docker inspect openclaw-<id> --format '{{json .Config.Labels}}' | jq -r 'to_entries[] | select(.key | test("loadbalancer.server.port"))'
  ```

  Should show `9090`. Root compose includes explicit labels; after redeploy run `docker restart coolify-proxy` if needed.
