# Coolify Deployment Notes (OpenClaw)

This document captures the minimal configuration needed to deploy OpenClaw via **Coolify** in a reproducible way.

## Goal

- Coolify config is the *deployment source of truth* (values live in Coolify)
- `openclaw-uni-2026` repo is the *documentation source of truth* (variable names, required mounts, ports, and recovery procedures)
- No secrets are stored in git.

## Required persistence

The single most important requirement is to persist `/data`.

- Container path: `/data`
- Host path (recommended): `/data`
- Must include runtime state under: `/data/.openclaw`

If `/data` is not persistent, redeploys will appear to “wipe” configuration.

## Compose file (source of truth)

Production stack: [`deploy/coolify/docker-compose.yml`](docker-compose.yml)  
Coolify should use this repo path, not `coollabsio/openclaw` (see [`COOLIFY_SWITCH.md`](COOLIFY_SWITCH.md)).

## Ports (production)

- OpenClaw UI / nginx (Traefik upstream): **`:9090`**
- Control Center dashboard: `:9091`
- Gateway (loopback inside container): `:18789`
- Browser CDP (sidecar, internal): `:9223`

## Environment variables

Use `OPENCLAW.env.example` as the canonical list of variable names.

In Coolify:
- Add variables via the UI
- Mark secrets as sensitive

## Update policy

- Image upgrades: `docs/UPGRADE.md` (change `OPENCLAW_IMAGE_TAG`, redeploy).
- Updates are manual weekly.
- Always run/verify encrypted backup before redeploy.

## Recovery references

- `docs/RECOVERY_PROCEDURE.md`
- `scripts/restore.sh`
- `BACKUP_ARCHITECTURE.md`
