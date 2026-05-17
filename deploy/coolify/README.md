# Coolify Deployment Notes (OpenClaw)

This document captures the minimal configuration needed to deploy OpenClaw via **Coolify** in a reproducible way.

## Goal

- Coolify config is the *deployment source of truth* (values live in Coolify)
- `uni-claw-config` repo is the *documentation source of truth* (variable names, required mounts, ports, and recovery procedures)
- No secrets are stored in git.

## Required persistence

The single most important requirement is to persist `/data`.

- Container path: `/data`
- Host path (recommended): `/data`
- Must include runtime state under: `/data/.openclaw`

If `/data` is not persistent, redeploys will appear to “wipe” configuration.

## Ports (typical)

Exact ports depend on your Coolify routing.

- OpenClaw UI / nginx frontend: `:8080`
- OpenClaw Gateway (internal): `:18789`
- Browser sidecar (internal CDP): `:9223` (if enabled)

## Environment variables

Use `OPENCLAW.env.example` as the canonical list of variable names.

In Coolify:
- Add variables via the UI
- Mark secrets as sensitive

## Update policy

- Updates are manual weekly.
- Always run/verify encrypted backup before redeploy.

## Recovery references

- `docs/RECOVERY_PROCEDURE.md`
- `scripts/restore.sh`
- `BACKUP_ARCHITECTURE.md`
