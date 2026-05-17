# Workspace Resolution (Runtime Persona File Loading)

This document explains **where OpenClaw loads persona / workspace files from at runtime**.

## Why this matters

When troubleshooting persona/config drift, it is easy to confuse:
- an upstream repo checkout (e.g., a fork under `/data/uni-claw/...`), vs.
- the **runtime workspace root** that OpenClaw actually uses to load files like `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, etc.

OpenClaw loads persona/workspace files from the resolved **workspaceRoot**, not from arbitrary repo directories.

## Resolution rules (conceptual)

### Main agent (defaults)
`workspaceRoot` is resolved as:
1. `agents.defaults.workspace` if explicitly set in config, else
2. `<openclaw_home>/workspace` (implementation default)

### Non-main agents (clover/mary/...) 
Each agent can have `workspace` overrides:
1. `agents.list[i].workspace` if set, else
2. `workspaceRoot + /agents/<agentId>`

## Current VPS configuration (authoritative)

Source: `/data/.openclaw/openclaw.json` (and `openclaw config get agents`).

### Defaults
- `agents.defaults.workspace` = `/data/workspace`

### Agent overrides
- `kimi.workspace` = `/data/workspace/agents/kimi`
- `clover` = no override (inherits defaults)
- `mary` = no override (inherits defaults)
- `datie` = no override (inherits defaults)

## Practical implications

- The runtime `AGENTS.md` used for the default workspace is:
  - `/data/workspace/AGENTS.md`

- Kimi loads workspace/persona files from:
  - `/data/workspace/agents/kimi/...`

- A directory like `/data/uni-claw/agents/<agent>/AGENTS.md` (if it exists) is most likely:
  - a repo template/example, **not** the runtime persona path

## Debug tips

- Print current config:

```bash
openclaw config get agents
```

- Confirm file existence:

```bash
ls -la /data/workspace/AGENTS.md
ls -la /data/workspace/agents/kimi/
```

- When in doubt, treat `/data/.openclaw/openclaw.json` as the source of truth for runtime resolution.
