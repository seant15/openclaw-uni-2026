# SESSION_NAMING.md - Session Naming Rules

## Overview
All sessions must follow standardized naming conventions to ensure traceability, organization, and proper routing. Unidentified or misnamed sessions create confusion and operational overhead.

---

## Session Key Format

### Standard Pattern
```
agent:{agent_id}:{context}:{modifier}
```

### Components
| Component | Description | Examples |
|-----------|-------------|----------|
| `agent` | Fixed prefix | `agent` |
| `{agent_id}` | Agent identifier | `clover`, `writer`, `mary`, `openclaw`, `nexus`, `kimi`, `atlas` |
| `{context}` | Session context | `main`, `slack`, `cron`, `thread` |
| `{modifier}` | Optional modifier | thread ID, channel ID, cron job ID |

---

## Context Types

### 1. `main` - Primary Direct Sessions
**Format:** `agent:{agent_id}:main`

Used for:
- Direct user interactions
- Primary agent sessions
- Default fallback context

**Examples:**
- `agent:clover:main` - Clover's primary session
- `agent:writer:main` - Writer's primary session
- `agent:openclaw:main` - OpenClaw's primary session

---

### 2. `slack` - Slack Channel Sessions
**Format:** `agent:{agent_id}:slack:channel:{channel_id}`

Used for:
- Group channel participation
- Channel-specific context
- Team coordination

**Examples:**
- `agent:clover:slack:channel:C0AGZLUBYP4` - Clover in #kimi-test
- `agent:mary:slack:channel:C0AGBGSBMJ9` - Mary in specific channel

**Channel ID Lookup:**
- Use Slack's channel ID (starts with C)
- Never use channel names (they can change)

---

### 3. `thread` - Thread Continuations
**Format:** `agent:{agent_id}:main:thread:{thread_id}`

Used for:
- Continuing thread conversations
- Maintaining context across messages
- Slack thread replies

**Examples:**
- `agent:clover:main:thread:1771996784.636849`
- `agent:writer:main:thread:abc123def456`

---

### 4. `cron` - Scheduled Job Sessions
**Format:** `agent:{agent_id}:cron:{job_id}`

Used for:
- Scheduled automation tasks
- Periodic checks and reports
- Background jobs

**Examples:**
- `agent:openclaw:cron:daily-report`
- `agent:clover:cron:weekly-review`

**Job ID Standards:**
- Use descriptive, kebab-case names
- Include frequency if relevant: `daily`, `weekly`, `hourly`
- Unique across all agents

---

## Prohibited Patterns

The following patterns are NOT allowed:

| Bad Pattern | Why | Fix |
|-------------|-----|-----|
| `agent:kimi_test:main` | Underscores in agent ID | Use hyphens: `kimi-test` |
| `agent:clover` | Missing context | Add `:main` |
| `clover:main` | Missing `agent:` prefix | Add `agent:` |
| `agent:Clover:main` | Uppercase agent ID | Use lowercase: `clover` |
| `agent:clover:slack:#general` | Channel name instead of ID | Use channel ID |
| Random UUID without context | Unidentifiable | Use structured format |

---

## Agent ID Registry

| Agent ID | Full Name | Emoji | Primary Function |
|----------|-----------|-------|------------------|
| `clover` | Clover 🍀 | 🍀 | Management & Operations |
| `writer` | Writer ✍️ | ✍️ | Content Creation |
| `mary` | Mary 📡 | 📡 | Communications |
| `openclaw` | OpenClaw 🛡️ | 🛡️ | Monitoring & Performance |
| `nexus` | Nexus 🔗 | 🔗 | Integrations |
| `kimi` | Kimi 🧪 | 🧪 | Technology & R&D |
| `atlas` | Atlas 🎯 | 🎯 | Strategic Analysis |

**Deprecated Agent IDs (Do Not Use):**
- `relay` → Merged into `clover`
- `sentinel` → Merged into `openclaw`
- `kimi_test` → Use `kimi` instead

---

## Session Lifecycle

### Creation
1. Determine agent responsible
2. Identify context type (`main`, `slack`, `thread`, `cron`)
3. Add appropriate modifiers (channel ID, thread ID, job ID)
4. Verify uniqueness

### Continuation
- Maintain same session key across related messages
- Use `thread:` modifier for continuations
- Don't create new sessions for same context

### Cleanup
- Sessions auto-expire based on activity
- Mark inactive sessions appropriately
- Archive important session data

---

## Troubleshooting

### Unidentified Sessions
If you encounter `unknown` or malformed session keys:

1. **Check agent ID** - Must match registry exactly
2. **Verify context** - Must be one of: `main`, `slack`, `thread`, `cron`
3. **Validate modifiers** - Channel IDs start with C, thread IDs are numeric
4. **Report to Clover** - For systematic issues

### Migration
When migrating sessions:
1. Document old session key
2. Create new properly-named session
3. Link old to new in documentation
4. Archive old session data

---

## Enforcement

### Automatic Validation
- Session keys validated on creation
- Invalid patterns rejected
- Suggestions provided for corrections

### Manual Review
- Clover reviews session naming monthly
- Non-compliant sessions flagged
- Corrections applied as needed

---

_Last updated: 2026-02-26_
_Maintained by: Clover 🍀_
