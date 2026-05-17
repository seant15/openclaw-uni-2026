# Agent Communication Options Research
## OpenClaw Native Capabilities + Alternatives

**Requested by:** Sean  
**Researched by:** Clover  
**Date:** 2026-02-27

---

## OPTION 1: OpenClaw Native Subagents (RECOMMENDED)

### How It Works
Uses OpenClaw's built-in `sessions_spawn` and `subagents` tools:

```
Clover (main) → sessions_spawn → OpenClaw (subagent)
                      ↓
               OpenClaw works → announces result back
                      ↓
               Clover receives completion
```

### Configuration Required

**1. Update `~/.openclaw/openclaw.json`:**

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["*"],  // Allow spawning any agent
        maxSpawnDepth: 2,    // Enable orchestrator pattern
        maxChildrenPerAgent: 5,
        maxConcurrent: 8,
      },
    },
    list: [
      {
        id: "clover",
        subagents: { allowAgents: ["openclaw", "nexus", "writer"] }
      },
      {
        id: "kimi",
        subagents: { allowAgents: ["*"] }  // Full R&D access
      },
      {
        id: "mary",
        subagents: { allowAgents: ["*"] }  // Full comms access
      },
      {
        id: "openclaw",
        subagents: { allowAgents: ["openclaw"] }  // Self-spawn only
      }
    ]
  },
  
  // Enable session tools for orchestrators
  tools: {
    allow: ["group:sessions", "subagents"]
  }
}
```

### Usage Example

```javascript
// Clover spawns OpenClaw for Google Ads report
sessions_spawn({
  agentId: "openclaw",
  task: "Generate weekly Google Ads report for Dental Artistry (6329354566)",
  mode: "run",
  runTimeoutSeconds: 300
})

// OpenClaw runs, then announces completion back to Clover's session
```

### Pros
- ✅ Native to OpenClaw (no external dependencies)
- ✅ Built-in result announcement back to requester
- ✅ Thread-bound sessions (Discord) for persistent routing
- ✅ Nested orchestration (depth-2 subagents)
- ✅ Auto-archive after completion

### Cons
- ⚠️ Requires Gateway config update
- ⚠️ Tool policy must allow `sessions_spawn`

---

## OPTION 2: Superbase Task Queue (Kimi's Proposal)

### How It Works
Shared database table for task distribution:

```
Kimi → INSERT task into Superbase
              ↓
OpenClaw → Poll/query for pending tasks
              ↓
OpenClaw → UPDATE task with result
              ↓
Kimi → Query result by task ID
```

### Schema (Already Created by Kimi)
```sql
CREATE TABLE agent_tasks (
    id UUID PRIMARY KEY,
    from_agent TEXT,
    to_agent TEXT,
    task_type TEXT,
    priority TEXT,
    payload JSONB,
    status TEXT,  -- pending/claimed/completed/failed
    result JSONB,
    created_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
```

### Usage Example
```python
# Kimi creates task
supabase.table('agent_tasks').insert({
    'from_agent': 'kimi',
    'to_agent': 'openclaw',
    'task_type': 'google_ads_report',
    'payload': {...},
    'status': 'pending'
})

# OpenClaw claims and completes
task = supabase.table('agent_tasks')
    .update({'status': 'claimed'})
    .eq('to_agent', 'openclaw')
    .eq('status', 'pending')
    .execute()

# Do work...

supabase.table('agent_tasks')
    .update({'status': 'completed', 'result': {...}})
    .eq('id', task_id)
    .execute()
```

### Pros
- ✅ Persistent (survives restarts)
- ✅ Audit trail in database
- ✅ Can add real-time subscriptions
- ✅ No Gateway config changes needed

### Cons
- ⚠️ Requires polling or WebSocket setup
- ⚠️ No built-in result routing (manual query)
- ⚠️ External dependency (Superbase)

---

## OPTION 3: Slack as Message Bus (Current Workaround)

### How It Works
Use Slack channels with @mentions:

```
Clover posts: "@openclaw [AGENT_TASK] type: report, account: 6329354566"
              ↓
OpenClaw monitors channel, parses message
              ↓
OpenClaw replies: "Task complete. Results: ..."
```

### Usage
Already working today — we just used this for the Google Ads reports.

### Pros
- ✅ Works immediately (no setup)
- ✅ Human-readable
- ✅ Audit trail in Slack history

### Cons
- ⚠️ Not programmatic (parsing required)
- ⚠️ No type safety
- ⚠️ Depends on Slack connectivity
- ⚠️ Not scalable for complex workflows

---

## OPTION 4: HTTP API + Webhooks

### How It Works
Each agent exposes HTTP endpoints:

```
Clover → POST http://openclaw-agent:8080/task
              ↓
OpenClaw processes, returns job ID
              ↓
OpenClaw → POST webhook to Clover when done
```

### Implementation
Would require building custom agent wrappers or using OpenClaw Gateway's `/tools/invoke` endpoint.

### Pros
- ✅ Language agnostic
- ✅ Standard HTTP patterns
- ✅ Async by design

### Cons
- ⚠️ Complex to implement
- ⚠️ Need auth/rate limiting
- ⚠️ Custom infrastructure

---

## RECOMMENDATION

### Tier 1: OpenClaw Native (Primary)
Use `sessions_spawn` + `subagents` for all agent-to-agent communication.

**Why:** Purpose-built, result routing, no external deps.

### Tier 2: Superbase (Audit/Backup)
Use Superbase `agent_tasks` table as audit log and fallback.

**Why:** Persistent record, can query history.

### Tier 3: Slack (Human Override)
Keep Slack as manual override and notification channel.

**Why:** Visibility, human intervention when needed.

---

## Implementation Steps

### Phase 1: Native Subagents (Today)
1. ✅ Nexus deploying Superbase schema (in progress)
2. ⏳ Update Gateway config with `subagents.allowAgents`
3. ⏳ Test `sessions_spawn` from Clover to OpenClaw
4. ⏳ Migrate Google Ads workflow to native spawning

### Phase 2: Hybrid (Next Week)
1. Use Superbase for audit logging
2. Use Slack for notifications only
3. Full native agent communication

---

## Gateway Config Update Needed

File: `~/.openclaw/openclaw.json`

```json5
{
  agents: {
    list: [
      { id: "clover", subagents: { allowAgents: ["openclaw", "nexus", "writer"] } },
      { id: "kimi", subagents: { allowAgents: ["*"] } },
      { id: "mary", subagents: { allowAgents: ["*"] } },
      { id: "openclaw", subagents: { allowAgents: ["openclaw"] } },
      { id: "nexus", subagents: { allowAgents: ["nexus"] } },
      { id: "writer", subagents: { allowAgents: ["writer"] } }
    ]
  }
}
```

**Who can update:** Sean (Gateway admin) or Nexus (if has access)

---

## My Recommendation

**Go with Option 1 (Native) as primary, Option 2 (Superbase) as audit trail.**

This gives us:
- Clean programmatic agent communication
- Persistent audit log
- No Slack dependency for automation
- Proper orchestrator/worker hierarchy

**Ready to implement?** Need Sean or Nexus to update the Gateway config.
