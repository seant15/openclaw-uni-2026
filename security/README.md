# /security

This folder is the single home for all security-related material (including token usage / efficiency guardrails).

## Structure
- `runbooks/` — operational runbooks (backup, restore, update, rollback)
- `scripts/` — safety/guardrail scripts (auditors, preflight checks)
- `proposals/` — generated audit reports and patches awaiting approval
- `reference/` — background references, archived context, policies

## Approval rule
Anything that changes core context files (SOUL/USER/AGENTS/MEMORY) must be proposed as a patch under `proposals/` and requires explicit human approval before applying.
