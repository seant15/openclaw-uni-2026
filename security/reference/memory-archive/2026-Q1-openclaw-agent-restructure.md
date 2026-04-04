# 2026 Q1 — OpenClaw Agent Restructure (Archive)

This file contains historical restructuring notes moved out of `MEMORY.md` to keep fixed context thin.

## Systems & config decisions (OpenClaw)
- Default Model: `kimi/kimi-k2.5` (configured 2026-02-26)
- Fallback Chain: `openai/gpt-5.2` → `anthropic/claude-sonnet-4-5` → `openai/gpt-4o-mini`
- Multi-model strategy: default primary should not depend on a single provider's quota.
- Use provider-diverse fallbacks (e.g., OpenAI ↔ Anthropic ↔ Kimi).
- Prefer dedicated "lanes" via agent IDs (planner/executor/verifier, writer, etc.) instead of one agent doing everything.

## Agent Configuration (2026-02-26 Fixes)
### Issues Resolved
1. Default model changed from `claude-3-5-haiku` to `kimi/kimi-k2.5`
2. Removed MC shadow agents that were duplicating existing agents:
   - `mc-8d52ba56-4c4d-4091-acb0-ab34f93e83ac` (was "Kimi" duplicate)
   - `mc-d6bf38aa-6a6f-432b-a074-76b752bb63fc` (was "Clover" duplicate)
   - `mc-gateway-392d283e-589a-4394-aacb-d40b514fffb4` (Gateway Agent)
3. Fixed broken agents directory — removed malformed `{strategist,ops_bot,watchdog,gatekeeper}` folder
4. Migrated legacy agents to kimi/kimi-k2.5 and added base documents:
   - Atlas 🎯 — Strategic Analyst
   - Relay ⚡ — Operations Manager
   - Sentinel 🛡️ — Performance Monitor
5. Added Clover SOUL.md — was missing
6. Updated AGENT_REGISTRY.md — reflects current active agents

## Agent Consolidation (2026-02-26)
### Merged Agents
- Relay ⚡ → Clover 🍀 (operations under management oversight)
- Sentinel 🛡️ → OpenClaw 🛡️ (unified monitoring)

### Merge Process
1. ✅ Merged Relay's SOUL.md → Clover
2. ✅ Merged Relay's TOOLS.md → Clover
3. ✅ Merged Relay's AGENTS.md → Clover
4. ✅ Merged Sentinel's SOUL.md → OpenClaw
5. ✅ Merged Sentinel's TOOLS.md → OpenClaw
6. ✅ Merged Sentinel's AGENTS.md → OpenClaw
7. ✅ Removed relay/sentinel from config
8. ✅ Deleted relay/sentinel directories

### Current Active Agents (historical snapshot)
| Agent | Role | Model | Base Docs |
|------|------|-------|-----------|
| Clover 🍀 | Management & Operations | kimi/kimi-k2.5 | ✅ |
| Mary 📡 | Communications | kimi/kimi-k2.5 | ✅ |
| OpenClaw 🛡️ | Monitoring & Performance | kimi/kimi-k2.5 | ✅ |
| Nexus 🔗 | Integrations | kimi/kimi-k2.5 | ✅ |
| Writer ✍️ | Content | kimi/kimi-k2.5 | ✅ |
| Kimi 🧪 | Technology | kimi/kimi-k2.5 | ✅ |
| Atlas 🎯 | Strategic Analysis | kimi/kimi-k2.5 | ✅ |

## Directory Structure Alignment (2026-02-26)
- `/data/.openclaw/workspace-{agent}/` — base documents
- `/data/.openclaw/agents/{agent}/qmd/` — vector memory
- `/data/.openclaw/agents/{agent}/sessions/` — session history
- `/data/.openclaw/workspace-{agent}/memory/` — daily logs

## Complete Base Document Set (2026-02-26)
Per-agent docs: SOUL.md, IDENTITY.md, USER.md, TOOLS.md, AGENTS.md, SESSION_NAMING.md

## Agent Restructure (2026-03-18)
- OpenClaw → Datie 🛡️ (monitoring/data/ads/reporting)
- Removed Writer ✍️ (content handled by Clover)
- Removed Nexus 🔗 (integrations handled by Kimi)
- Removed Atlas 🎯 (not deployed)

## Final 3-Agent Core (2026-03-19)
Merged Mary into Clover; final 3-agent core:
- Clover 🍀 — management + ops + comms
- Kimi 🧪 — tech + R&D + audit
- Datie 🛡️ — monitoring + data + ads + reports

(Archive note: this is historical; keep `MEMORY.md` focused on current state.)
