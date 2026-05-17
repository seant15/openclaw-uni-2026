# 03292026 UNI MAS Memory V1

Owner: Sean Tan (UNI Marketing)
Last updated: 2026-03-29

## 0) Objective
Build a self-improving, low-noise memory system for MAS V1 that:
- Preserves daily context (high recall)
- Distills weekly into long-term rules (high precision)
- Prunes stale/bad data on a schedule
- Enforces hard safety guardrails
- Is portable to other projects (tech-first)

## 1) System Components & Boundaries
### 1.1 QMD (Memory Orchestration)
Role: Ingest conversations/files → write daily/weekly notes → update long-term rules.

### 1.2 LanceDB (Vector Store)
Role: Semantic retrieval over memory artifacts.
Stores: embeddings + minimal metadata (source path, timestamp, client_id, topic).
Does NOT store: secrets, config, certificates, backups, or authoritative business facts.

### 1.3 Supabase (Structured Truth)
Role: Source-of-truth for structured facts (clients, ad accounts, metrics, tasks, change logs).
Principle: mutable facts and anything needing querying/auditing → Supabase.

## 2) Memory Layers (3-tier model)
We implement the "hot / context / archive" concept using Markdown under /memory.

### 2.1 Hot Rules (Global, <=10)
Location: MEMORY.md (Hot Rules section)
Definition: items corrected 3+ times; global safety/output/execution constraints.

### 2.2 Context Rules (Domain/Project/Client)
Location: memory/weekly/ and (optional) memory/projects/
Definition: rules that apply to a specific domain (ads/reporting), project, or client.

### 2.3 Archive (Deprecated)
Location: memory/archive/
Definition: outdated rules/preferences kept only for historical reference.
Not applied as active guidance.

## 3) Daily → Weekly → Monthly/Quarterly Operating Cadence
### 3.1 Daily (log everything; allow noise)
File: memory/YYYY-MM-DD.md
Template sections:
- Wins / Progress
- Decisions (with rationale)
- Open Loops (owner, next step)
- Mistakes / Lessons
- New Facts (minimize sensitive data)
- Tags: client_id (if applicable), topic

### 3.2 Weekly Distill (precision pass)
Schedule: Saturday 5:00am MST via cron
Files:
- memory/weekly/YYYY-Www.md (weekly digest)
- Update MEMORY.md (only durable rules & guardrails)
Actions:
- Extract repeat issues → convert to rules
- Deduplicate rules
- Move stale rules → archive
- Produce a short "what changed" digest (new/updated/deprecated rules)

### 3.3 Monthly Prune
Schedule: monthly (exact date TBD)
Actions:
- Merge duplicate rules
- Remove stale facts from MEMORY.md
- Tighten wording (shorter, stricter)

### 3.4 Quarterly Rebase
Schedule: quarterly (exact date TBD)
Actions:
- Restructure MEMORY.md like a README
- Delete rules that are now default behavior
- Remove anything proven wrong

## 4) Learning Policy (Self-improving mechanism)
### 4.1 What we learn from
ONLY learn from explicit user corrections/preferences:
- "No, do it this way"
- "I prefer X"
- "Always do Y"
Do NOT infer from silence.

### 4.2 3× Correction → Promotion
Track correction counts. When the same correction occurs 3 times:
- Ask Sean: promote to permanent rule?
- Classify: Hot (global) vs Context (domain/project/client)
- If promoted: write rule + source reference.

### 4.3 Transparency
When applying a learned rule, cite where it came from (file + date; ideally line ref).

## 5) client_id Concept (for retrieval precision)
Add client_id as a required tag for any client-related memory entry.
- Used as metadata for LanceDB indexing
- Used in daily/weekly templates
- Authoritative client facts remain in Supabase

client_id guidelines:
- Stable, lowercase, snake_case (e.g., dental_artistry, lumiere_dental)
- Avoid PII; do not embed emails/phone numbers

## 6) Hard Safety Guardrails (must-follow)
### 6.1 Never store in memory (any tier)
- Passwords, API keys, tokens
- SSL certificates / private keys
- Backup contents
- Financial/health data
- Private info about other people

### 6.2 Protected assets (do not touch without Sean)
- Config files (.env, openclaw.json, gateway config)
- backup/ directories
- SSL/cert/key material

### 6.3 Destructive actions require confirmation
Before any destructive action (DB drops/truncates, bulk deletes, irreversible migrations):
- Must ask Sean first
- Must include scope + rollback plan

## 7) Repository Layout (All memory under /memory)
All memory artifacts live under /data/workspace/memory:
- memory/YYYY-MM-DD.md
- memory/weekly/YYYY-Www.md
- memory/archive/YYYY-MM.md
- memory/templates/
- (optional) memory/projects/

NOTE: Existing paths should not be moved until we inventory current locations and update references in one controlled change.

## 8) Implementation Plan (Safe rollout)
Phase 1 (non-destructive):
- Create templates + directories under /memory
- Start writing new daily/weekly there
- No migrations yet

Phase 2 (inventory):
- Inventory existing memory-related locations/paths
- Identify references that must be updated (scripts, prompts, agent startup)

Phase 3 (controlled migration):
- Move legacy artifacts into /memory (if any)
- Update references
- Validate retrieval still works

Phase 4 (cron automation):
- Add cron jobs for weekly/monthly/quarterly routines
- Ensure jobs only write within /memory and update MEMORY.md

---
## Changelog
- 2026-03-29: Created OpenClaw cron job `uni-mas-memory-weekly-distill` (Sat 05:00 MST / America/Phoenix) as the single weekly memory authority.
- 2026-03-29: Disabled legacy cron job `Weekly memory compactor (chat)` (job id: 7c89613b-bfd4-4b53-846c-a6967c56b4f9) to avoid dual-track weekly promotion logic.

Pending decisions:
- Monthly prune schedule (day/time)
- Quarterly rebase schedule (day/time)
