# UNI Marketing Multi-Agent System

## Agent Fleet Overview (Consolidated)

| Agent | Role | Primary Function | Model |
|-------|------|-----------------|-------|
| **Clover** 🍀 | Management & Operations | Strategic oversight, task coordination, Sean's extension | kimi-k2.5 |
| **Mary** 📡 | Communications | Internal & client communications | kimi-k2.5 |
| **OpenClaw** 🛡️ | Monitoring & Performance | System health, campaign alerts, performance guardian | kimi-k2.5 |
| **Nexus** 🔗 | Integrations | API connections, data flows | kimi-k2.5 |
| **Writer** ✍️ | Content | Copywriting, creative content | kimi-k2.5 |
| **Kimi** 🧪 | Technology | Experiments, R&D, BD support | kimi-k2.5 |
| **Atlas** 🎯 | Strategic Analysis | Performance analysis (read-only) | kimi-k2.5 |

## Directory Structure

Each agent folder contains base documents:
- `SOUL.md` — Identity, personality, operating principles
- `TOOLS.md` — API keys and tool access  
- `AGENTS.md` — Multi-agent coordination guidelines

## Runtime Locations

- `agents/{agent}/qmd/` — Vector memory storage (OpenClaw managed)
- `agents/{agent}/sessions/` — Session history (OpenClaw managed)
- `workspace-{agent}/memory/` — MEMORY.md daily files (OpenClaw managed)

## Note

Base documents are now stored in `/data/.openclaw/workspace-{agent}/` as per OpenClaw defaults.
This folder contains copies for reference.

_Last updated: 2026-02-26_
