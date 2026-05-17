# 🔥 URGENT: OpenClaw Agent Handoff - Ad Data Infrastructure

**From:** Clover 🍀  
**Date:** 2026-03-01  
**Priority:** HIGH - Token refresh required

---

## ✅ COMPLETED BY CLOVER

### 1. Account Configuration (UPDATED)

**LEIVIP (B2B Fashion)**
| Platform | Account ID | Type | Status |
|----------|-----------|------|--------|
| Meta | act_281592916520074 | Primary | ✅ Known |
| Meta | act_1627505121562961 | Top of Funnel | ✅ NEW |
| Google | 621-885-8846 (6218858846) | Primary | ✅ VERIFIED |

**PROD (E-Commerce)**
| Platform | Account ID | Type | Status |
|----------|-----------|------|--------|
| Meta | act_175918763181986 | Primary | ✅ Known |
| Meta | act_113440162763180 | Backup | ✅ NEW |
| Google | 413-543-5047 (4135435047) | Primary | ✅ VERIFIED |

### 2. Google Ads - FULLY OPERATIONAL ✅

**Status:** All tokens working, access confirmed

**Test Results:**
```
✓ API access successful
✓ 18 accessible customers
✓ LEIVIP (6218858846): Access confirmed
✓ PROD (4135435047): Access confirmed
```

**Scripts Ready:**
- `scripts/fetch_google_ads_full.py` - Multi-level fetcher
- `scripts/test_google_ads_token.py` - Auth diagnostics
- `scripts/sync_all_accounts.py` - Orchestrator

### 3. Database Schema Updated

**Migration:** `supabase/add_ad_accounts_table.sql`

New `ad_accounts` table:
- Supports multiple accounts per client
- Account types: primary, backup, top_of_funnel
- Tracks status and timezone

### 4. E-Commerce Metrics Configured

**Meta:**
- Purchases (not conversions)
- Purchase Value (revenue)
- Cost Per Purchase (CPA)
- ROAS (return on ad spend)

**Google:**
- Conversions (purchases)
- Conversion Value
- Cost Per Conversion (CPA)
- Conversion Value Per Cost (ROAS)

---

## ⚠️ BLOCKER: Meta Token EXPIRED

**Current Status:** ❌ INVALID

```
Error 190: Error validating access token
Message: The session is invalid because the user logged out.
```

### SOLUTION REQUIRED

**Recommended (Permanent Fix):**
1. Generate **System User Token**
   - Go to: business.facebook.com
   - Settings → Users → System Users
   - Create: "UNI Data Sync"
   - Assign ad accounts:
     * act_281592916520074 (LEIVIP Primary)
     * act_1627505121562961 (LEIVIP Top of Funnel)
     * act_175918763181986 (PROD Primary)
     * act_113440162763180 (PROD Backup)
   - Generate token with `ads_read` permission
   - Update .env: `META_ACCESS_TOKEN=new_token`

**Alternative (Quick Fix):**
- https://developers.facebook.com/tools/explorer
- Get User Access Token (expires in 1-60 days)

---

## 📋 READY TO EXECUTE (After Token Fix)

### 1. Run 30-Day Sync Test
```bash
cd /data/workspace

# Test Meta (after token fix)
python3 scripts/fetch_meta_ads.py act_281592916520074 LEIVIP
python3 scripts/fetch_meta_ads.py act_1627505121562961 LEIVIP
python3 scripts/fetch_meta_ads.py act_175918763181986 PROD
python3 scripts/fetch_meta_ads.py act_113440162763180 PROD

# Test Google (ready now)
python3 scripts/fetch_google_ads_full.py 6218858846 LEIVIP
python3 scripts/fetch_google_ads_full.py 4135435047 PROD

# Full sync all accounts
python3 scripts/sync_all_accounts.py
```

### 2. Verify Data in Supabase
```sql
SELECT client_id, platform, account_id, status 
FROM ad_accounts 
WHERE client_id IN ('LEIVIP', 'PROD');

SELECT * FROM performance_daily 
WHERE account_id LIKE '%6218858846%' 
ORDER BY date DESC LIMIT 10;
```

### 3. Set Up Hourly Cron
```bash
# Add to crontab or OpenClaw cron
15 * * * * python3 /data/workspace/scripts/sync_all_accounts.py
```

---

## 📁 KEY FILES

| File | Purpose | Status |
|------|---------|--------|
| `config/ad_accounts.yaml` | Account mapping | ✅ Complete |
| `scripts/fetch_meta_ads.py` | Meta fetcher | ✅ Ready (needs token) |
| `scripts/fetch_google_ads_full.py` | Google fetcher | ✅ Ready |
| `scripts/sync_all_accounts.py` | Orchestrator | ✅ Ready |
| `scripts/insert_to_supabase.py` | Data persistence | ✅ Ready |
| `scripts/view_ad_data.py` | Data viewer | ✅ Ready |
| `supabase/add_ad_accounts_table.sql` | DB migration | ✅ Ready |
| `docs/API_ACCESS_GUIDE.md` | Auth documentation | ✅ Complete |

---

## 🎯 YOUR MISSION, OPENCLAW

1. **🔥 URGENT:** Get fresh Meta token (System User recommended)
2. **Run full sync** for all 6 accounts (4 Meta + 2 Google)
3. **Verify data** appears in Supabase correctly
4. **Set up hourly cron** for ongoing sync
5. **Build alert rules** for:
   - CPA spike > 200%
   - ROAS drop < 0.5x
   - Zero purchases for 4+ hours
   - Budget threshold 80%
6. **Monitor** first few syncs for errors

---

## 📚 REFERENCES

- API Access Guide: `/data/workspace/docs/API_ACCESS_GUIDE.md`
- Setup Guide: `/data/workspace/docs/AD_SETUP_GUIDE.md`
- Database Schema: `/data/workspace/supabase/schema.sql`

---

## 💬 NOTES FROM SEAN

> "I can meet all your request as long as you can plan to finish that clover"
> 
> Translation: Do the planning/thinking, then execute efficiently.

**Planning Complete ✅**
**Execution: IN PROGRESS**

---

**Clover 🍀**
*Management & Operations*
*2026-03-01*
