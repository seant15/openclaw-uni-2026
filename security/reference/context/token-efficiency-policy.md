# Token Efficiency & Context Budget Policy

Goal: reduce cost/latency by keeping fixed context small, and retrieving details on-demand.

## Budgets
- Trigger threshold (fixed context): **3,888 tokens/turn** (Sean-approved, 2026-03-30)
  - If exceeded: run Context Auditor and produce a report.
  - Target: **3,888 tokens/turn**
  - No requirement to immediately drop below target in a single pass; reduce gradually over multiple passes.

(Definition: fixed context = always-loaded base docs; excludes chat history + tool outputs.)

## Rules
1) Keep `MEMORY.md` as a **thin core**:
   - durable facts, current agent roster, active objectives, critical IDs
   - move historical logs/tables into `/security/reference/memory-archive/`

2) Keep `AGENTS.md` as an **operating contract** (10–30 lines).
   - move long playbooks into `/security/reference/agents/`

3) Prefer on-demand retrieval:
   - use `memory_search`/`memory_get` to pull specific history
   - use `read` for reference docs only when needed

4) Never paste full raw logs into long-term memory.
   - store a pointer (file path) + short summary + timestamp.

## Governance
- Any changes to core context files must be proposed as a patch in `/security/proposals/` and require explicit approval.
