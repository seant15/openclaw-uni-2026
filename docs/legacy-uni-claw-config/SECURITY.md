# SECURITY.md - Security & Context Governance

*The third pillar of our configuration system (alongside MEMORY.md and BACKUP.md).*

---

## 1. Context Auditor System

### Purpose
Reduce token cost/latency and prevent sensitive data sprawl by monitoring and controlling **fixed context bloat**.

### What is Fixed Context?
The always-loaded base documents injected every turn:
- `SOUL.md` — Agent identity & voice
- `USER.md` — User profile & preferences
- `IDENTITY.md` — Agent character definition
- `TOOLS.md` — Environment-specific tool notes
- `AGENTS.md` — Operating contract & session rules
- `MEMORY.md` — Long-term memory (thin core)
- `HEARTBEAT.md` — Periodic task definitions

### Current Token Budget
- **Trigger threshold:** 3,888 tokens/turn (Sean-approved, 2026-03-30)
- **Target:** ≤ 3,888 tokens/turn
- **Current estimate:** ~3,011 tokens/turn (as of 2026-03-30)

---

## 2. Implementation Files

### Core Scripts
| File | Purpose |
|------|---------|
| `/data/workspace/security/scripts/context_auditor.js` | Read-only auditor that analyzes context files and generates reports |
| `/data/workspace/security/scripts/context-hook-server.js` | HTTP server (:33123) for automated audit triggers |
| `/data/workspace/security/scripts/init-security-hooks.sh` | Docker init script to start hook server |
| `/data/workspace/security/scripts/security-context-audit-trigger.sh` | Manual trigger script for on-demand audits |

### Configuration (Environment Variables)
```bash
# Enable/disable audit
SEC_CONTEXT_AUDIT_ENABLED=true

# Token threshold for alerts (Sean-approved: 3,888)
SEC_CONTEXT_AUDIT_THRESHOLD=3888

# Cooldown between alerts (minutes)
SEC_CONTEXT_AUDIT_COOLDOWN_MIN=60

# Slack Bot Token for DM alerts (required)
SLACK_BOT_TOKEN=xoxb-...

# Target user for DM alerts (default: Sean)
SLACK_DM_USER_ID=U025H4Q9FPA
```

**Note:** Webhook URL (`SEC_SLACK_WEBHOOK_URL`) is deprecated. Use `SLACK_BOT_TOKEN` instead for DM alerts.

### Output Locations
- **Audit reports:** `/data/workspace/security/proposals/context-audit-<timestamp>.md`
- **Snapshots (pre-change):** `/data/workspace/snapshots/context-pre-thin-core-<timestamp>/`
- **Reference docs:** `/data/workspace/security/reference/`

---

## 3. Governance Policy

### The Thin Core Principle
Keep fixed context files minimal; move low-frequency content to reference.

| File | Keep (Thin Core) | Move to Reference |
|------|------------------|-------------------|
| `MEMORY.md` | Durable facts, active objectives, critical IDs | Historical logs, resolved issues, old agent tables |
| `AGENTS.md` | 10-30 line operating contract | Long playbooks, coordination docs |
| `SOUL.md` | Core identity & voice | Extended explanations, examples |

### Change Approval Flow
1. **Generate** — Auditor produces report (always safe, read-only)
2. **Propose** — Create patch under `/security/proposals/patch-*.diff`
3. **Snapshot** — Backup current state to `/snapshots/`
4. **Approve** — Explicit YES required from Sean
5. **Apply** — Execute patch only after approval

### Never Auto-Apply
The auditor is **read-only by design**. No automatic edits to core context files.

---

## 4. Reference Documentation

### Token Efficiency Policy
- Location: `/data/workspace/security/reference/context/token-efficiency-policy.md`
- Rules for keeping context small and retrieving on-demand

### Context Auditor Base Spec
- Location: `/data/workspace/security/reference/context/CONTEXT_AUDITOR_BASE.md`
- Full technical specification of the auditor system

### Agents Handbook
- Location: `/data/workspace/security/reference/agents/agents-handbook.md`
- Long-form guidance moved out of AGENTS.md

### Memory Archive
- Location: `/data/workspace/security/reference/memory-archive/`
- Historical restructuring notes, old agent tables, resolved issues

---

## 5. How to Use

### Run Manual Audit
```bash
# Via trigger script (checks hook server first)
/data/workspace/security/scripts/security-context-audit-trigger.sh

# Or run auditor directly
node /data/workspace/security/scripts/context_auditor.js
```

### Check Hook Server Health
```bash
curl http://localhost:33123/health
```

### Trigger Audit via HTTP
```bash
curl -X POST http://localhost:33123/context-audit
```

---

## 6. Audit Report History

| Timestamp | Total Tokens | Status | Report |
|-----------|--------------|--------|--------|
| 2026-03-30 03:33 | ~3,011 | ✅ Within budget (3,888) | `context-audit-20260330-0333.md` |
| 2026-03-30 03:25 | ~3,011 | ✅ Within budget (3,888) | `context-audit-20260330-0325.md` |
| 2026-03-29 21:37 | ~5,800 | ⚠️ Pre-thin-core baseline | `context-audit-20260329-2137.md` |

---

## 7. Change Log

**2026-03-30 — v2 Update**
- Replaced Webhook-based alerts with Slack Bot API DM alerts
- Updated threshold to 3,888 tokens (Sean-approved)
- Fixed alert delivery to use `SLACK_BOT_TOKEN` instead of deprecated `SEC_SLACK_WEBHOOK_URL`
- Verified DM delivery to Sean (test message sent successfully at 2026-03-30 04:14 UTC)

- Token estimate uses `chars/4` heuristic (not a real tokenizer)
- Heading split is naive; unheaded blocks may be under-analyzed
- Does not classify secrets (secrets redaction is a separate control)

---

## 8. Future Improvements

- [ ] Replace chars/4 with real tokenizer
- [ ] Add section-by-section diff suggestions
- [ ] Auto-suggest migration targets
- [ ] Slack summary message generator
- [ ] Scheduled (cron) daily/weekly audits
- [ ] Preflight checks before context-changing operations

---

_Last updated: 2026-03-30_
