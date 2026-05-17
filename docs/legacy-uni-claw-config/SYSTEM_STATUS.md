# SYSTEM_STATUS.md - Active Systems Quick Reference

> ⚠️ **CRITICAL:** This file is for session startup reference. Always check here before assuming system state.
> 
> **Last Updated:** 2026-04-07

---

## 🔐 Secret Management

**Status:** ✅ Active (Supabase + Self-Encrypted)

**Components:**
| Component | Path | Purpose |
|-----------|------|---------|
| CLI Tool | `scripts/secret-cli.js` | Manage secrets |
| Health Check | `scripts/secret-health-cron.js` | Daily monitoring |
| Backup Script | `scripts/backup-secrets.sh` | Weekly backups |
| SDK | `lib/secret-manager.js` | Secret access SDK |

**Cron Jobs:**
| Job ID | Schedule | Status |
|--------|----------|--------|
| `secret-health-daily-001` | Daily 01:00 UTC | ✅ Running |
| `secret-stats-daily-001` | Daily 02:00 UTC | ⚠️ Last run timeout |
| `secret-backup-weekly-001` | Sun 03:00 UTC | ✅ Configured |

---

## 💾 Backup Systems

**Status:** ✅ Active

| System | Script | Schedule | Destination |
|--------|--------|----------|-------------|
| OpenClaw Full Backup | `scripts/openclaw-full-backup.sh` | Via system cron | Google Drive |
| Secret Management Backup | `scripts/backup-secrets.sh` | Weekly (cron job) | Local + Manual upload |

**Retention:**
- Remote (Google Drive): 14 days
- Local: 7 days
- Logs: 30 days

---

## 📊 Monitoring Systems

**Status:** ✅ Active

| System | Component | Alert Channel |
|--------|-----------|---------------|
| Context Optimizer v3 | `security/scripts/context_optimizer.js` | Slack DM |
| Secret Health | `scripts/secret-health-cron.js` | Slack #alerts |
| Daily Usage Reports | Multiple cron jobs | Slack #data-ops-run-report |

**Context Optimizer:**
- Threshold: 3,888 tokens
- Auto-trigger: Every OpenClaw turn
- Strategies: ARCHIVE 🟢 / COMPRESS 🟡 / SPLIT 🟡

---

## 🤖 Active Cron Jobs Summary

**Daily Jobs:**
| Job ID | Agent | Purpose | Time (AZ) |
|--------|-------|---------|-----------|
| `daily-usage-report-all` | Clover | All agents usage report | 04:00 |
| `daily-usage-report-clover` | Clover | Clover usage report | 05:00 |
| `daily-feedback-summary` | Clover | Feedback summary | 06:30 |
| `daily-usage-report-datie` | Datie | Datie usage report | 00:00 |
| `secret-health-daily-001` | Clover | Secret health check | 18:00 |

**Weekly Jobs:**
| Job ID | Agent | Purpose | Time (AZ) |
|--------|-------|---------|-----------|
| `weekly-context-report-001` | Clover | Context optimization report | Sun 09:00 |
| `secret-backup-weekly-001` | Clover | Secret backup | Sat 20:00 |
| `google-ads-weekly-ld` | Datie | Lumiere Dental report | Thu 05:00 |
| `google-ads-weekly-da` | Datie | Dental Artistry report | Thu 05:00 |
| `uni-mas-memory-weekly-distill` | Clover | Memory weekly distill | Sat 05:00 |
| `Swipe Manager Weekly - Mary` | Clover | Mary task reminder | Mon 09:00 |

---

## ⚙️ Model Configuration

**Primary Model:** `kimi/kimi-k2.5`

**Fallback Chain:**
1. `openai/gpt-5.2`
2. `anthropic/claude-sonnet-4-5`
3. `openai/gpt-4o-mini`

**Provider Config:**
```json
{
  "kimi": {
    "baseUrl": "https://api.moonshot.ai/anthropic",
    "model": "kimi-k2.5"
  }
}
```

---

## 📝 Context Management

**Current Status:**
- Threshold: 3,888 tokens
- Current: Check via `security/scripts/context_auditor.js`
- Optimizer: v3 (auto-trigger on each turn)

**Archived Files:**
- `security/reference/memory-archive/MEMORY_archive.md`
- `security/reference/memory-archive/AGENTS_detailed.md`

---

## 🔍 Quick Commands Reference

**Check cron job status:**
```bash
openclaw cron list
```

**Check secret health:**
```bash
cd /data/workspace && node scripts/secret-health-cron.js
```

**List all secrets:**
```bash
cd /data/workspace && node scripts/secret-cli.js list
```

**Manual backup:**
```bash
cd /data/workspace && ./scripts/openclaw-full-backup.sh
```

---

## 🚨 Known Issues

| Issue | Status | Notes |
|-------|--------|-------|
| `secret-stats-daily-001` timeout | ⚠️ Monitoring | Last run timed out, needs investigation |

---

*This file is updated manually when system configuration changes.*
