# MEMORY.md - Long-Term Memory (Sean Tan Collaboration)

## Working principles (how we work)
- Prioritize systems over ad-hoc solutions
- Always provide clear, actionable insights
- Anticipate problems before they occur
- Maintain high-signal, low-noise communication
- Focus on compounding advantages and scalability

## Preferences / output style
- Direct, structured responses
- Bullets + frameworks
- Explicit trade-offs
- 2-3 concrete options when uncertain
- Intellectual honesty (don't hide uncertainty)

## Focus areas (what we're building)
1. AI-powered marketing automation
2. Operational system design
3. Performance marketing optimization
4. Team workflow efficiency

## Ongoing objectives
- Reduce manual intervention in agency processes
- Create repeatable, scalable systems
- Leverage AI for strategic + tactical improvements

## Systems & config decisions (OpenClaw)
- **Default Model:** `kimi/kimi-k2.5` (configured 2026-02-26)
- **Fallback Chain:** `openai/gpt-5.2` → `anthropic/claude-sonnet-4-5` → `openai/gpt-4o-mini`

Historical restructuring / migration notes moved to:
- `/data/workspace/security/reference/memory-archive/2026-Q1-openclaw-agent-restructure.md`

Rule: keep `MEMORY.md` as a thin, current, operational core.

## Client Ad Accounts (2026-03-05)

### Google Ads Accounts

| Client | Customer ID | Status |
|--------|-------------|--------|
| Dental Artistry | 632-935-4566 | ✅ Active |
| Lumiere Dental | 714-522-2813 | ✅ Active |
| SESUNG | 310-859-4803 | ✅ Active |
| Travorio | 849-262-0446 | ✅ Active |

### Meta Ads Accounts

| Client | Primary Account | Secondary Account | Notes |
|--------|-----------------|-------------------|-------|
| LEIVIP | act_281592916520074 | act_1627505121562961 | TOF account |
| PROD | act_175918763181986 | act_113440162763180 | Backup account |
| UB+ | act_841938383288943 | act_1130410831752833 | Mini account |
| Windie.pro | act_924797519996193 | — | Single account |
| StateofGratitude | act_628003337822332 | — | Single account |

### Database Schema
- **Table:** `clients`
- **New Columns Added:**
  - `google_ads_customer_id` (VARCHAR 20) - Google Ads Customer ID
  - `meta_ad_account_id` (VARCHAR 50) - Primary Meta/Facebook Ad Account
  - `meta_ad_account_id_2` (VARCHAR 50) - Secondary Meta account (if applicable)

## Known Mistakes Checklist (Don't Repeat)

Full checklist moved to: `/data/workspace/security/reference/memory-archive/known-mistakes-checklist.md`

Key rule: Model ref must match `{provider}/{model-id}` from `models.providers` config.

## Open questions / TODO

Active TODOs moved to: `/data/workspace/security/reference/memory-archive/active-todos.md`

---
_Last updated: 2026-03-30_
