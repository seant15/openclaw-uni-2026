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
- **Context Management:** Smart Optimizer v3 (2026-04-07) — auto-detect, analyze, propose, approve workflow

**Quick Reference:** See `SYSTEM_STATUS.md` for active systems, cron jobs, and current state.

Historical restructuring / migration notes moved to:
- `/data/workspace/security/reference/memory-archive/2026-Q1-openclaw-agent-restructure.md`
- `/data/workspace/security/reference/context/context-management-system-v3.md`

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

### Format
- **场景**: 发生了什么
- **后果**: 造成了什么问题
- **解决方案/未来约束**: 如何避免重复

### Entries

- **场景**: OpenClaw 配置中 `agents.defaults.model.primary` 设置为 `opencode/kimi-k2.5`，但 `models.providers` 中只有 `kimi` 和 `kimi-coding` 两个 provider，导致引用不存在的 provider。
- **后果**: 未显式配置 model 的 agent 无法找到对应的 provider，模型调用失败。
- **解决方案/未来约束**: 
  - 修改 model 配置时，必须以 `models.providers` 中定义的 provider ID 为基准
  - Model ref 格式: `{provider}/{model-id}`，必须与 `models.providers.{provider}.models[].id` 匹配
  - 修改后执行 `/model status` 验证当前 session 使用的模型
  - 添加新 provider 时，同步更新所有 agent 的 model 引用

- [占位] 等待填充...

## Open questions / TODO
- Decide final Kimi provider wiring + exact model id used in OpenClaw.
- Add weekly memory compactor cron (Fri 07:00, tz TBD) that posts to both chat + Slack.

## TODO (Ops hardening)
📦 **Full list archived:** See `reference/MEMORY_archive.md#todo-ops-hardening`

Key items:
- Secret management: evaluate Doppler or 1Password CLI
- Monitoring: real-time resource monitoring with alerts
- Backup verification: daily health check + DM alerts
- Disaster recovery: include scheduler tables in DB dumps

## Daily Work Log (Selected)

### 2026-04-07 — Agent System Restructure Complete
📦 **Details archived:** See `reference/MEMORY_archive.md#2026-04-07-agent-restructure`

**Summary:**
- Git repo synced to commit `ebb4a0b`
- Agent roster finalized: Clover, Mary, Kimi, Datie
- Writer & Nexus permanently removed
- Per-agent volume mounts fixed

### 2026-03-30 — Context Auditor System Deployed
📦 **Details archived:** See `reference/MEMORY_archive.md#2026-03-30-context-auditor`

**Summary:**
- Context Auditor + Hook Server deployed
- Threshold: 3,888 tokens
- Auto-trigger on each OpenClaw turn

---
_Last updated: 2026-04-07 (optimized)_
