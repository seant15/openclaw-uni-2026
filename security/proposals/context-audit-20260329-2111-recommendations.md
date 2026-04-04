# Context Audit Recommendations (draft)
Generated (UTC): 2026-03-29

## Target
Reduce fixed context from ~5.8k tokens/turn to <=2.0k tokens/turn by moving low-frequency material into `/security/reference/` and keeping a thin core in place.

## What to move (high-confidence)
### 1) MEMORY.md → archive historical operational logs
Move sections that are **historical change logs** (agent consolidation history, tables of past agents, resolved issues) into:
- `/security/reference/memory-archive/2026-Q1-agent-restructure.md`

Keep in MEMORY.md:
- Working principles
- Preferences/output style
- Current active agent roster (current 3-agent core only)
- Any durable IDs that are actively used (ad accounts table is likely durable)
- Open questions/TODO

### 2) AGENTS.md → split “operating contract” vs “long handbook”
Move long guidance blocks (heartbeat vs cron, react like a human, extended memory maintenance, etc.) into:
- `/security/reference/agents-handbook.md`

Keep in AGENTS.md:
- The 5–10 rules that materially affect behavior/safety
- The mandatory file-reading order
- The “ask first” external actions rule

### 3) Token/Efficiency guardrails (new)
Create:
- `/security/reference/token-efficiency-policy.md`

Include:
- Fixed-context budget target
- When to trigger context audit
- Prohibit pasting large logs into long-term memory
- Prefer on-demand retrieval (memory_search/memory_get) for long docs

## Approval flow (proposed)
1) Generate patch + new reference files under `/security/reference/...`
2) Produce a diff for:
   - MEMORY.md
   - AGENTS.md
3) Write a snapshot to `/data/workspace/snapshots/context-pre-thin-core-<timestamp>/`
4) Only apply after explicit YES.

## Expected savings (rough)
- MEMORY.md: save ~800–1400 tokens
- AGENTS.md: save ~700–1200 tokens
Total likely save: ~1.5k–2.6k tokens/turn
