# Context Auditor — Base Spec (v0)

Location of implementation (current):
- Script: `/data/workspace/security/scripts/context_auditor.js`
- Output reports: `/data/workspace/security/proposals/context-audit-<timestamp>.md`

## Purpose
Reduce token cost / latency and reduce risk of sensitive sprawl by preventing **fixed context bloat**.

"Fixed context" here means the always-loaded base documents (e.g., SOUL/USER/AGENTS/MEMORY) that get injected every turn.

## Current Behavior (what it does today)
This auditor is **read-only** and produces a report. It does **not** auto-edit any core files.

### Inputs (audited files)
Reads these files from `/data/workspace/` if present:
- `SOUL.md`
- `USER.md`
- `IDENTITY.md`
- `TOOLS.md`
- `AGENTS.md`
- `MEMORY.md`
- `HEARTBEAT.md`

### Token estimation
- Uses a simple heuristic: `estimated_tokens = ceil(chars / 4)`
- Notes: good enough for trend detection; not a true tokenizer.

### Bloat detection heuristics
Per file:
1) **Top longest sections**
   - Naively splits markdown by headings (`\n(?=#{1,6} )`) and ranks by estimated tokens.
   - Reports top 5 longest chunks with previews.

2) **Repeated lines**
   - Finds lines (>= 20 chars) that repeat >= 2 times.
   - Reports top 10 repeats.

3) **Rule-of-thumb flags**
   - If file estimated tokens > 1500 → flag as large for fixed context.
   - Special notes for `MEMORY.md` and `AGENTS.md`:
     - MEMORY tends to accrete; move history to archive.
     - AGENTS long handbook should be reference-loaded.

### Output
Writes a markdown report containing:
- Summary total fixed-context estimate
- Per-file size + longest sections + repeats + bloat candidates
- Proposed next step (requires approval): move low-frequency text to `/security/reference` and keep thin core

## Governance / Approval (how changes should be made)
1) Auditor generates a report (always safe)
2) Any core-file changes must be proposed as patches under:
   - `/data/workspace/security/proposals/patch-*.diff`
3) Human approval required (YES)
4) Before applying patches:
   - create snapshot under `/data/workspace/snapshots/context-pre-thin-core-<timestamp>/`
5) Apply patches only after approval

## Enablement (what "enabled" means)
### Important: auditor is NOT automatically running every turn
Right now it is "enabled" in the sense that:
- the script exists,
- the policy exists,
- we can run it on-demand,
- the output folder structure is established.

### How to run (manual)
- `node /data/workspace/security/scripts/context_auditor.js`

## Recommended future enablement logic (automation)
Pick one (in increasing aggressiveness):

### Option A — On-demand only (default)
Trigger when Sean asks or before major refactors.

### Option B — Scheduled (cron) audit
Run daily/weekly:
- Generate report
- If total fixed-context > hard limit, post alert in Slack with report summary
- Never auto-apply changes

### Option C — Preflight for "context-changing" operations
When an agent is about to edit any of these:
- `SOUL.md`, `USER.md`, `AGENTS.md`, `MEMORY.md`

Then:
1) run auditor before and after
2) require patch + approval

## Budgets (recommended)
- Trigger threshold: **3,888 tokens/turn** (Sean-approved, 2026-03-30)
- Target: **3,888 tokens/turn**

Notes:
- This threshold is for *fixed context* (base docs / always-loaded files), excluding chat history + tool outputs.

## Known limitations
- Token estimate is heuristic; can be replaced with a real tokenizer later.
- Heading split is naive; large unheaded blocks may be under-analyzed.
- Does not currently classify secrets; secrets redaction is a separate control.

## Next improvements (easy wins)
- Replace chars/4 with real token counts per model (or a standard tokenizer)
- Add section-by-section diff suggestions
- Auto-suggest migration targets under `/security/reference/`
- Add a Slack summary message generator
