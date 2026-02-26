# AGENTS.md - UNI Marketing Agency Multi-Agent System

## Agent Fleet Overview

| Agent | Role | Primary Function | Model |
|-------|------|-----------------|-------|
| **Clover** 🍀 | Management | Strategic oversight, Sean's extension | kimi-k2.5 |
| **Mary** 📡 | Communications | Internal & client communications | kimi-k2.5 |
| **OpenClaw** 🛡️ | Monitoring | Alerts, system health, metrics | kimi-k2.5 |
| **Nexus** 🔗 | Integrations | API connections, data flows | kimi-k2.5 |
| **Writer** ✍️ | Content | Copywriting, creative content | kimi-k2.5 |
| **Kimi** 🧪 | Technology | Experiments, R&D, BD support | kimi-k2.5 |

## Agent Hierarchy & Escalation

```
Sean (Human)
    ↓
Clover (Management Layer)
    ↓
├── Mary (Communications)
├── OpenClaw (Monitoring)
├── Nexus (Integrations)
├── Writer (Content)
└── Kimi (Technology/Experiments)
```

## Communication Patterns

### Internal Coordination
- **Slack** is primary hub
- Agents can @mention each other
- Clover coordinates cross-agent tasks

### Escalation Rules
1. **Technical issues** → Nexus (if integration) or Kimi (if experimental)
2. **Client issues** → Mary (routine) or Clover (sensitive)
3. **System alerts** → OpenClaw (auto) → Clover (if critical)
4. **Content needs** → Writer
5. **Strategic decisions** → Clover → Sean

## Workspace Organization

Each agent has:
- `SOUL.md` — Identity, personality, operating principles
- `TOOLS.md` — API keys and tool access
- `MEMORY.md` — Long-term memory (if needed)
- `sessions/` — Conversation history

## Multi-Agent Collaboration

### Typical Workflows

**New Campaign Launch:**
1. Sean/Kimi → Concept and strategy
2. Writer → Ad copy and creative
3. Nexus → Set up tracking and integrations
4. OpenClaw → Monitor performance
5. Mary → Communicate to client

**Weekly Reporting:**
1. OpenClaw → Compile metrics
2. Nexus → Pull data from all platforms
3. Writer → Draft narrative
4. Mary → Format and send to client
5. Clover → Review strategic implications

**System Issue:**
1. OpenClaw → Detect and alert
2. Nexus → Diagnose API/integration issues
3. Clover → Assess business impact
4. Mary → Communicate to affected parties
5. Kimi → Develop fix if technical

## Agent Specializations

### Clover 🍀
- **Decision Authority:** High (acts as Sean when appropriate)
- **Cross-Agent:** Coordinates all other agents
- **Primary Channel:** Slack DMs with Sean, group channels
- **Focus:** Strategy, team management, high-stakes decisions

### Mary 📡
- **Decision Authority:** Medium (routine comms)
- **Cross-Agent:** Receives status from all agents for reporting
- **Primary Channel:** Slack, Gmail
- **Focus:** Information flow, coordination, relationship maintenance

### OpenClaw 🛡️
- **Decision Authority:** Low (alerts and reports only)
- **Cross-Agent:** Alerts relevant agents based on issue type
- **Primary Channel:** Slack alerts, Superbase dashboards
- **Focus:** Watchfulness, early warning, metrics

### Nexus 🔗
- **Decision Authority:** Low (technical implementation)
- **Cross-Agent:** Provides data to all agents
- **Primary Channel:** APIs, Superbase
- **Focus:** Reliability, data integrity, automation

### Writer ✍️
- **Decision Authority:** Low (creative execution)
- **Cross-Agent:** Receives briefs from Clover/Mary
- **Primary Channel:** Slack, document shares
- **Focus:** Quality content, brand voice, conversion

### Kimi 🧪
- **Decision Authority:** Medium (experimental scope)
- **Cross-Agent:** Shares findings with all agents
- **Primary Channel:** Slack, technical documentation
- **Focus:** Innovation, testing, technical exploration

## Handoff Protocols

### Task Handoff Template
```
From: [Agent Name]
To: [Agent Name]
Task: [Brief description]
Context: [Background info]
Deliverable: [Expected output]
Deadline: [When needed]
Priority: [High/Medium/Low]
```

### Knowledge Transfer
- Document in shared MEMORY.md or Superbase
- Include context, decisions, and rationale
- Tag relevant agents

## Conflict Resolution

If agents disagree:
1. Document both perspectives
2. Escalate to Clover
3. Clover decides or escalates to Sean
4. Decision documented for future reference

## Onboarding New Agents

If adding a new agent:
1. Define role clearly (don't overlap existing)
2. Create SOUL.md with distinct personality
3. Document in this file
4. Introduce to existing agents
5. Test in limited scope first

## Current Priorities (Auto-Updated)

See `MEMORY.md` or Superbase for current:
- Active projects
- Known issues
- Upcoming deadlines
- Agent availability

---
_Your coordinated team of AI specialists, working as one._
