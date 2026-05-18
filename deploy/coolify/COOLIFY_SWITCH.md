# Switch Coolify from coollabsio/openclaw Git → this repo

One-time migration so compose ports and volumes are under UNI control.  
OpenClaw app updates remain **image tag bumps**, not merges of upstream Git.

## 1. Push this repo

Ensure `main` includes `deploy/coolify/docker-compose.yml`.

## 2. Coolify application settings

| Field | Value |
|-------|--------|
| Repository | `seant15/openclaw-uni-2026` (or your fork) |
| Branch | `main` |
| Build Pack | Docker Compose |
| Docker Compose Location | `/docker-compose.yml` |
| Base Directory | `/` |

Coolify copies **only** the root compose file into `/data/coolify/applications/<uuid>/`. Do **not** use `include:` — subpaths are not copied (`no service selected`).

If deploy fails with `openclaw-gateway` / `driver_opts`, pull latest `main` and redeploy.

Keep existing **Environment Variables** from the old app (secrets are not in git).

## 3. Required Coolify environment variables

Add if missing:

| Variable | Example | Notes |
|----------|---------|--------|
| `OPENCLAW_IMAGE_TAG` | `2026.5.12` | Pin; avoid floating `latest` in production |
| `OPENCLAW_CONFIG_HOST_PATH` | `/data/coolify/applications/ug0g8cs4kkw0040cwsswk40c/openclaw.json` | Host path to mounted gateway JSON |
| `OPENCLAW_GATEWAY_TOKEN` | (secret) | |
| `OPENCLAW_ALLOWED_ORIGINS` | `https://open.uni-agency.com` | |
| `OPENCODE_API_KEY` | (secret) | |
| `AUTH_USERNAME` / `AUTH_PASSWORD` | | nginx basic auth (recommended on public URL) |

Copy names from `deploy/coolify/OPENCLAW.env.example`.

## 4. Domains (unchanged)

- `https://open.uni-agency.com` → openclaw service (Traefik → container **9090**)
- Browser sslip domain can stay on browser service if Coolify created one

## 5. Persistent storage (unchanged)

Confirm host binds still apply after redeploy:

- `/opt/openclaw/data` → `/data`
- `/opt/openclaw/browser-config` → browser `/config`
- `OPENCLAW_CONFIG_HOST_PATH` → `/app/config/openclaw.json`

Redeploy does **not** wipe `/opt/openclaw/data`.

## 6. Deploy and verify

```bash
docker exec openclaw-<id> openclaw --version
docker inspect openclaw-<id> --format '{{json .Config.Labels}}' | jq -r 'to_entries[] | select(.key | test("loadbalancer.server.port"))'
curl -sI -o /dev/null -w '%{http_code}\n' https://open.uni-agency.com/
```

Expect version **2026.5.12+**, `loadbalancer.server.port` = **9090**, HTTPS not **502**.

## 7. Decommission old Git source

After smoke test, stop pointing Coolify at `coollabsio/openclaw` for this resource.  
Archive `seant15/openclaw` fork unless you need Track B (custom GHCR build).

See `docs/UPGRADE.md` for weekly image upgrades.
