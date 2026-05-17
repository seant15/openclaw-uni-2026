# Agent Registry

## Active Agents (Consolidated)

### Primary Agents (Fully Configured)
| Agent | ID | Role | Model | Status |
|-------|-----|------|-------|--------|
| **Clover** 🍀 | `clover` | Management & Operations | kimi/kimi-k2.5 | ✅ Active (merged with Relay) |
| **Mary** 📡 | `mary` | Communications & Client Relations | kimi/kimi-k2.5 | ✅ Active |
| **OpenClaw** 🛡️ | `openclaw` | Monitoring & Performance Guardian | kimi/kimi-k2.5 | ✅ Active (merged with Sentinel) |
| **Nexus** 🔗 | `nexus` | Integrations & Data Flows | kimi/kimi-k2.5 | ✅ Active |
| **Writer** ✍️ | `writer` | Content Creation | kimi/kimi-k2.5 | ✅ Active |
| **Kimi** 🧪 | `kimi` | Technology & Experiments | kimi/kimi-k2.5 | ✅ Active |
| **Atlas** 🎯 | `atlas` | Strategic Analyst | kimi/kimi-k2.5 | ✅ Active (data access only) |

**Total: 7 Active Agents**

## Agent Consolidation (2026-02-26)

### Merged Agents
| Agent | Merged Into | Base Documents Merged |
|-------|-------------|----------------------|
| **Relay** ⚡ | **Clover** 🍀 | ✅ SOUL.md, TOOLS.md, AGENTS.md |
| **Sentinel** 🛡️ | **OpenClaw** 🛡️ | ✅ SOUL.md, TOOLS.md, AGENTS.md |

### Rationale
- **Relay → Clover:** Operations now under direct management oversight, streamlining task coordination and strategic execution
- **Sentinel → OpenClaw:** Unified monitoring (system + performance) eliminates redundancy and creates single source of truth for alerts

## Agent Configuration Details

### Clover 🍀 (Management & Operations)
- **Primary Role:** Strategic oversight, task coordination, Sean's extension
- **Tools:** Supabase MCP, ClickUp MCP, Slack MCP, Google Calendar
- **Core Functions:**
  - High-stakes decision making
  - Task creation and assignment
  - Deadline tracking
  - Cross-agent coordination
  - Process optimization
- **Merged From:** Relay (operations capabilities)
- **Base Documents:** SOUL.md ✅ | TOOLS.md ✅ | AGENTS.md ✅

### OpenClaw 🛡️ (Monitoring & Performance)
- **Primary Role:** System health, campaign monitoring, alert management
- **Tools:** Supabase MCP, Meta Ads API, Google Ads API, Slack MCP, ClickUp API
- **Core Functions:**
  - Real-time ROAS monitoring
  - Campaign performance alerts
  - System health monitoring
  - Anomaly detection
  - Statistical analysis
  - Predictive alerting
- **Merged From:** Sentinel (performance monitoring capabilities)
- **Base Documents:** SOUL.md ✅ | TOOLS.md ✅ | AGENTS.md ✅

### Mary 📡
- **Primary Role:** Communications & Client Relations
- **Tools:** Slack MCP, Gmail, Fireflies, ClickUp
- **Core Functions:** Client communication, information flow, relationship maintenance
- **Base Documents:** SOUL.md ✅ | TOOLS.md ✅ | AGENTS.md ✅

### Nexus 🔗
- **Primary Role:** Integration Architect & API Hub
- **Tools:** Supabase MCP (Read/Write), All Advertising APIs
- **Core Functions:** API connections, data flows, integration maintenance
- **Base Documents:** SOUL.md ✅ | TOOLS.md ✅ | AGENTS.md ✅

### Writer ✍️
- **Primary Role:** Content Creator
- **Tools:** Fireflies, ClickUp, Superbase
- **Core Functions:** Copywriting, creative content, brand voice
- **Base Documents:** SOUL.md ✅ | TOOLS.md ✅ | AGENTS.md ✅

### Kimi 🧪
- **Primary Role:** Technology & R&D
- **Tools:** All APIs (experimental), Git, Superbase
- **Core Functions:** Innovation, testing, technical exploration
- **Base Documents:** SOUL.md ✅ | TOOLS.md ✅ | AGENTS.md ✅

### Atlas 🎯
- **Primary Role:** Strategic Analyst (legacy, data access only)
- **Tools:** Supabase MCP (Read Only), Email MCP
- **Core Functions:** Performance analysis, strategic insights (read-only access)
- **Base Documents:** SOUL.md ✅ | TOOLS.md ✅ | AGENTS.md ✅

## Model Configuration

### Default Model (All Agents)
- **Primary:** `kimi/kimi-k2.5`
- **Fallbacks:** 
  - `openai/gpt-5.2`
  - `anthropic/claude-sonnet-4-5`
  - `openai/gpt-4o-mini`

### Alias
- `kimi25` → `kimi/kimi-k2.5`

## Removed Agents

### MC Shadow Agents (Removed 2026-02-26)
- `mc-8d52ba56-4c4d-4091-acb0-ab34f93e83ac` (was "Kimi" duplicate)
- `mc-d6bf38aa-6a6f-432b-a074-76b752bb63fc` (was "Clover" duplicate)
- `mc-gateway-392d283e-589a-4394-aacb-d40b514fffb4` (Gateway Agent)

### Merged Agents (Consolidated 2026-02-26)
- **Relay** ⚡ → Merged into Clover 🍀
- **Sentinel** 🛡️ → Merged into OpenClaw 🛡️

## Historical Sub-Agents (Archived)
1. **Becky** — Marketing Sub-Agent (Social Media Strategy)
2. **Casey** — Project Management Sub-Agent
3. **Frank** — Research Sub-Agent (Data Analysis)
4. **David** — Technical Sub-Agent (Software Development)

_Last archived: 2026-02-17_

## Registry Maintenance
- **Created:** 2026-02-17
- **Last Updated:** 2026-02-26
- **Consolidation:** 2026-02-26 (Relay → Clover, Sentinel → OpenClaw)
- **Maintained by:** Clover 🍀

### Update Protocol
1. When adding new agents, update this registry
2. Ensure all agents have complete base documents
3. Verify model configuration matches kimi/kimi-k2.5 standard
4. Document any agent retirements or merges
