# Git Repository Audit Report

**Date:** 2026-04-04  
**Auditor:** Clover  
**Scope:** `/data/workspace` vs GitHub `openclaw-uni-2026`

---

## Executive Summary

| Metric | Count |
|--------|-------|
| **Modified files** | 45 |
| **Deleted files** | 25 |
| **Untracked (new) files** | 151 |
| **Total changes** | 221 |

**Status:** Local workspace has significant drift from Git repository. A full sync is recommended.

---

## 1. Agent Directory Changes

### 1.1 Modified Agents (5 agents)

| Agent | Modified Files | Notes |
|-------|---------------|-------|
| **clover** | AGENTS.md, TOOLS.md | Updated to thin-core pattern |
| **kimi** | AGENTS.md, IDENTITY.md, SOUL.md, TOOLS.md, USER.md | Major refactor |
| **mary** | AGENTS.md, IDENTITY.md | Restructured |
| **datie** | *(no changes)* | Stable |
| **nexus** | *(deleted)* | Agent removed |

### 1.2 Deleted Agents (Complete Removal)

| Agent | Deleted Files | Reason |
|-------|--------------|--------|
| **nexus** | 6 files | Agent deprecated |
| **openclaw** | 6 files | Agent deprecated |
| **writer** | 6 files | Agent deprecated |
| **mary** | 5 files | Partial deletion (restructured) |

**Deleted Files Detail:**
```
agents/mary/SESSION_NAMING.md
agents/mary/SOUL.md
agents/mary/TOOLS.md
agents/mary/USER.md
agents/nexus/AGENTS.md
agents/nexus/IDENTITY.md
agents/nexus/SESSION_NAMING.md
agents/nexus/SOUL.md
agents/nexus/TOOLS.md
agents/nexus/USER.md
agents/openclaw/AGENTS.md
agents/openclaw/IDENTITY.md
agents/openclaw/SESSION_NAMING.md
agents/openclaw/SOUL.md
agents/openclaw/TOOLS.md
agents/openclaw/USER.md
agents/writer/AGENTS.md
agents/writer/IDENTITY.md
agents/writer/SESSION_NAMING.md
agents/writer/SOUL.md
agents/writer/TOOLS.md
agents/writer/USER.md
```

---

## 2. Core Configuration Changes

### 2.1 Root Directory Files

| File | Status | Change Type | Summary |
|------|--------|-------------|---------|
| `AGENTS.md` | Modified | Content update | Thin-core refactor |
| `AGENT_REGISTRY.md` | Modified | Content update | Agent list updated |
| `IDENTITY.md` | Modified | Content update | Clover identity |
| `MEMORY.md` | Modified | Content update | Operational memory |
| `SOUL.md` | Modified | Content update | Clover soul |
| `openclaw.json` | **Deleted** | File removal | Moved to infra/ |
| `mission-control` | **Deleted** | Directory removal | Deprecated |

### 2.2 Infrastructure Directory (`uni-openclaw-infra/`)

| File | Status | Change Type | Summary |
|------|--------|-------------|---------|
| `config/openclaw.json` | Modified | Config update | Agent config changes |
| `docker-compose.yml` | Modified | Service update | Container config |
| `scripts/entrypoint.sh` | Modified | Script update | Startup logic |
| `.env.example` | Modified | Template update | Env vars |
| `ARCHITECTURE.md` | Modified | Documentation | System design |
| `README.md` | Modified | Documentation | Setup guide |
| `TROUBLESHOOTING.md` | Modified | Documentation | Debug guide |

---

## 3. New Untracked Content (151 files)

### 3.1 Scripts Directory (`scripts/`)

**New Files:** 20+ scripts for ad data sync

```
scripts/fetch-google-ads-da.sh
scripts/fetch_google_ads.py
scripts/fetch_google_ads.sh
scripts/fetch_google_ads_full.py
scripts/fetch_meta_ads.py
scripts/format_report.py
scripts/generate_google_ads_token.sh
scripts/generate_report.py
scripts/generate_weekly_report.sh
scripts/google_ads_hourly_sync.sh
scripts/google_ads_reporter.py
scripts/google_ads_reporter.sh
scripts/insert_to_supabase.py
scripts/inspect_conversion_actions.py
scripts/interactive_report.py
scripts/mary_nightly_sync.sh
scripts/meta_ads_hourly_sync.sh
scripts/openclaw_backup_to_gdrive.sh
scripts/setup_google_ads_config.py
scripts/sync_all_accounts.py
scripts/test_google_ads_api.sh
scripts/test_google_ads_token.py
scripts/test_meta_token.py
scripts/troubleshoot_google_ads.sh
scripts/upsert_client_ad_accounts.py
scripts/view_ad_data.py
```

**Purpose:** Google Ads & Meta Ads data synchronization infrastructure

### 3.2 Security Directory (`security/`)

**New Files:** Context Auditor system

```
security/proposals/PRD-alert-system-redesign.md
security/proposals/alert-system-improvement.md
security/proposals/ecommerce-alert-rules-design.md
security/reference/notion-learning-swipe-system.md
security/scripts/context-hook-server.js
security/scripts/context_auditor.js
security/scripts/init-security-hooks.sh
security/scripts/security-context-audit-trigger.sh
```

**Purpose:** Token efficiency monitoring and security hardening

### 3.3 Skills Directory (`skills/`)

**New Files:** Agent capabilities

```
skills/proactive-agent/SKILL.md
skills/summarize-pro/SKILL.md
skills/swipe-manager/SKILL.md
skills/uni-reporting/SKILL.md
skills/writing-plans/SKILL.md
```

**Purpose:** Modular agent skills system

### 3.4 Memory System (`memory/`)

**New Files:** Daily memory logs

```
memory/2026-03-29.md
memory/2026-03-30.md
memory/templates/
memory/weekly/
```

### 3.5 Other New Directories

| Directory | File Count | Purpose |
|-----------|-----------|---------|
| `docs/` | Multiple | Documentation |
| `config/` | Multiple | Configuration files |
| `cron/` | 4 files | Cron job definitions |
| `migrations/` | Multiple | Database migrations |
| `reports/` | Multiple | Generated reports |
| `supabase/` | Multiple | Supabase integration |
| `supabase-project/` | Multiple | Supabase project files |
| `_trash/` | Multiple | Deleted files backup |

---

## 4. Detailed Diff Analysis

### 4.1 `uni-openclaw-infra/config/openclaw.json` Changes

**Key Differences:**

| Aspect | Git Version | Local Version | Impact |
|--------|-------------|---------------|--------|
| **Clover default** | Not set | `default: true` | Critical |
| **Kimi default** | `default: true` | Not set | Critical |
| **Kimi model** | `claude-opus-4-6` | `claude-opus-4-6` | Same |
| **Kimi binding** | Missing | `#kimi-test` | Missing in Git |
| **Mary bindings** | 1 channel | 2 channels | Incomplete in Git |
| **Trusted proxies** | Present | Removed | Security change |
| **Model providers** | Full config | Simplified | Config drift |

### 4.2 Line Count Changes (Stat Summary)

```
45 files changed, 1775 insertions(+), 4213 deletions(-)
```

**Interpretation:** Major refactoring with significant content reduction (thin-core pattern).

---

## 5. Risk Assessment

### 5.1 High Risk Items

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Data Loss** | 25 files deleted | Verify in `_trash/` before permanent deletion |
| **Config Drift** | openclaw.json differs | Manual merge required |
| **Agent Removal** | 3 agents removed | Ensure no dependencies |

### 5.2 Medium Risk Items

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Untracked Scripts** | 20+ new scripts | Review before commit |
| **Security Files** | New security infrastructure | Verify secrets not committed |
| **Database Migrations** | New migration files | Test before applying |

---

## 6. Recommendations

### Option A: Force Push Local to Git (Recommended for Speed)

```bash
cd /data/workspace/uni-openclaw-infra

# Backup Git version first
git branch backup-$(date +%Y%m%d)

# Add all new files
git add scripts/ security/ skills/ memory/ docs/ config/ cron/ 
git add migrations/ reports/ supabase/ supabase-project/
git add uni-openclaw-infra/

# Remove deleted files
git rm -r agents/nexus/ agents/openclaw/ agents/writer/
git rm openclaw.json mission-control

# Commit everything
git add -A
git commit -m "sync: major refactor - thin core, security, ad sync infrastructure

- Remove nexus, openclaw, writer agents
- Refactor clover, kimi, mary to thin-core pattern
- Add security/ with Context Auditor
- Add scripts/ for Google/Meta Ads sync
- Add skills/ for modular capabilities
- Add memory/ system for daily logs
- Update uni-openclaw-infra/ configuration
- Set clover as default agent"

git push origin master --force
```

### Option B: Manual Merge (Recommended for Safety)

1. Review each modified file individually
2. Resolve conflicts in `openclaw.json` manually
3. Stage changes incrementally
4. Test before push

### Option C: Selective Sync

1. Only sync critical changes (agents, config)
2. Defer non-essential changes (docs, scripts)
3. Incremental commits

---

## 7. Pre-Push Checklist

- [ ] Verify no secrets in `.env` files
- [ ] Verify `_trash/` contains deleted files backup
- [ ] Test `openclaw.json` syntax: `openclaw doctor`
- [ ] Verify agent configurations load correctly
- [ ] Confirm Kimi agent uses `claude-opus-4-6`
- [ ] Confirm Clover is `default: true`
- [ ] Review all 151 untracked files for sensitive data

---

## Appendix A: Full File List

### Modified (45 files)
```
AGENTS.md
AGENT_REGISTRY.md
IDENTITY.md
MEMORY.md
SOUL.md
agents/clover/AGENTS.md
agents/clover/TOOLS.md
agents/kimi/AGENTS.md
agents/kimi/IDENTITY.md
agents/kimi/SOUL.md
agents/kimi/TOOLS.md
agents/kimi/USER.md
agents/mary/AGENTS.md
agents/mary/IDENTITY.md
uni-openclaw-infra/.env.example
uni-openclaw-infra/ARCHITECTURE.md
uni-openclaw-infra/README.md
uni-openclaw-infra/TROUBLESHOOTING.md
uni-openclaw-infra/config/openclaw.json
uni-openclaw-infra/docker-compose.yml
uni-openclaw-infra/scripts/entrypoint.sh
```

### Deleted (25 files)
```
agents/mary/SESSION_NAMING.md
agents/mary/SOUL.md
agents/mary/TOOLS.md
agents/mary/USER.md
agents/nexus/AGENTS.md
agents/nexus/IDENTITY.md
agents/nexus/SESSION_NAMING.md
agents/nexus/SOUL.md
agents/nexus/TOOLS.md
agents/nexus/USER.md
agents/openclaw/AGENTS.md
agents/openclaw/IDENTITY.md
agents/openclaw/SESSION_NAMING.md
agents/openclaw/SOUL.md
agents/openclaw/TOOLS.md
agents/openclaw/USER.md
agents/writer/AGENTS.md
agents/writer/IDENTITY.md
agents/writer/SESSION_NAMING.md
agents/writer/SOUL.md
agents/writer/TOOLS.md
agents/writer/USER.md
mission-control
openclaw.json
```

### Untracked (151 files)
See sections 3.1-3.5 above for categorized list.

---

**End of Audit Report**
