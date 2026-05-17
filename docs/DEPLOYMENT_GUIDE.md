# 🚀 STEP-BY-STEP DEPLOYMENT GUIDE
**Ad Data Sync System - Meta & Google Ads**

---

## STEP 1: Run Database Migration (5 minutes)

### 1.1 Open Supabase SQL Editor
1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **"SQL Editor"** in left sidebar
4. Click **"New Query"**

### 1.2 Copy and Run Migration SQL
1. Open this file on the server:
   ```bash
   cat /data/workspace/supabase/complete_schema.sql
   ```

2. Copy the entire contents

3. Paste into Supabase SQL Editor

4. Click **"Run"**

### 1.3 Verify Tables Created
Run this query in SQL Editor:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

**Expected tables:**
- `ad_accounts` ✅
- `ad_groups` ✅
- `ads` ✅
- `alerts` ✅
- `campaigns` ✅
- `clients` ✅
- `data_sync_log` ✅
- `keywords` ✅
- `performance_daily` ✅
- `performance_hourly` ✅
- `search_terms` ✅

---

## STEP 2: Insert Meta Data (2 minutes)

### 2.1 Check Data Files Exist
```bash
ls -la /tmp/meta_ads_*.json
```

**Should show:**
- `meta_ads_281592916520074_20260301_231608.json` (LEIVIP Primary)
- `meta_ads_1627505121562961_20260301_231946.json` (LEIVIP TOF)
- `meta_ads_175918763181986_20260301_231820.json` (PROD Primary)
- `meta_ads_113440162763180_20260301_231900.json` (PROD Backup)

### 2.2 Insert to Supabase
```bash
cd /data/workspace

# Insert all Meta data
python3 scripts/insert_to_supabase.py /tmp/meta_ads_281592916520074_20260301_231608.json
python3 scripts/insert_to_supabase.py /tmp/meta_ads_1627505121562961_20260301_231946.json
python3 scripts/insert_to_supabase.py /tmp/meta_ads_175918763181986_20260301_231820.json
python3 scripts/insert_to_supabase.py /tmp/meta_ads_113440162763180_20260301_231900.json
```

### 2.3 Verify Data in Supabase
Run this query in SQL Editor:
```sql
SELECT 
  aa.account_name,
  pd.date,
  pd.spend,
  pd.conversions,
  pd.conversion_value,
  pd.roas
FROM performance_daily pd
JOIN ad_accounts aa ON pd.ad_account_id = aa.id
ORDER BY pd.date DESC, pd.spend DESC
LIMIT 20;
```

**Should show:** Meta data with spend, purchases, revenue, ROAS

---

## STEP 3: Set Up Hourly Cron (2 minutes)

### 3.1 Add Cron Job
```bash
# Option A: Using OpenClaw cron (recommended)
openclaw cron add \
  --name="ad-sync-hourly" \
  --schedule="15 * * * *" \
  --command="cd /data/workspace && python3 scripts/sync_all_accounts.py >> /var/log/ad_sync.log 2>&1"
```

### 3.2 Verify Cron Added
```bash
openclaw cron list
```

**Should show:** `ad-sync-hourly` with schedule `15 * * * *`

### 3.3 Create Log File
```bash
touch /var/log/ad_sync.log
chmod 666 /var/log/ad_sync.log
```

---

## STEP 4: Test Manual Sync (3 minutes)

### 4.1 Run Sync Manually
```bash
cd /data/workspace
python3 scripts/sync_all_accounts.py
```

### 4.2 Check Output
**Expected:**
```
🚀 FULL AD DATA SYNC
Started: 2026-03-02Txx:xx:xx
...
✅ LEIVIP - Meta Primary: X campaigns synced
✅ LEIVIP - Meta TOF: X campaigns synced
✅ PROD - Meta Primary: X campaigns synced
✅ PROD - Meta Backup: X campaigns synced
✅ LEIVIP - Google: X campaigns synced
✅ PROD - Google: X campaigns synced
```

### 4.3 Check Logs
```bash
tail -20 /var/log/ad_sync.log
```

---

## STEP 5: Verify Data Flow (2 minutes)

### 5.1 Check Latest Data in Supabase
```sql
-- Check today's data
SELECT 
  aa.account_name,
  COUNT(*) as records,
  SUM(pd.spend) as total_spend,
  SUM(pd.conversions) as total_conversions
FROM performance_daily pd
JOIN ad_accounts aa ON pd.ad_account_id = aa.id
WHERE pd.date = CURRENT_DATE
GROUP BY aa.account_name;
```

### 5.2 Check Sync Log
```sql
SELECT 
  platform,
  sync_type,
  last_sync_at,
  status,
  records_synced
FROM data_sync_log
ORDER BY last_sync_at DESC
LIMIT 10;
```

---

## STEP 6: Set Up Alerts (Optional - 5 minutes)

### 6.1 Create Alert Rules
Add to `/data/workspace/config/ad_accounts.yaml`:
```yaml
alert_thresholds:
  cpa_spike_percent: 200          # Alert if CPA > 200% of avg
  roas_drop_threshold: 0.5        # Alert if ROAS < 0.5x
  zero_conversion_hours: 4        # Alert if no conversions for 4h
  budget_threshold_percent: 80    # Alert if 80% budget spent
```

### 6.2 Create Alert Script
```bash
# Create alert checker
python3 /data/workspace/scripts/check_alerts.py
```

### 6.3 Add Alert Cron
```bash
openclaw cron add \
  --name="ad-alerts" \
  --schedule="0 * * * *" \
  --command="cd /data/workspace && python3 scripts/check_alerts.py"
```

---

## 📋 QUICK REFERENCE COMMANDS

### Check Sync Status
```bash
# View logs
tail -f /var/log/ad_sync.log

# Check last sync
openclaw cron list

# Manual sync
cd /data/workspace && python3 scripts/sync_all_accounts.py
```

### Check Data in Supabase
```sql
-- Daily summary
SELECT 
  date,
  SUM(spend) as total_spend,
  SUM(conversions) as total_conversions,
  AVG(roas) as avg_roas
FROM performance_daily
GROUP BY date
ORDER BY date DESC
LIMIT 7;

-- Account breakdown
SELECT 
  aa.account_name,
  SUM(pd.spend) as spend,
  SUM(pd.conversions) as conv,
  AVG(pd.roas) as roas
FROM performance_daily pd
JOIN ad_accounts aa ON pd.ad_account_id = aa.id
WHERE pd.date >= CURRENT_DATE - 7
GROUP BY aa.account_name;
```

### Troubleshooting
```bash
# Test Meta token
python3 scripts/test_meta_token.py

# Test Google token
python3 scripts/test_google_ads_token.py

# Test single account
cd /data/workspace
python3 scripts/fetch_meta_ads.py act_281592916520074 LEIVIP
```

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Database migration run (Supabase SQL Editor)
- [ ] Tables verified (11 tables created)
- [ ] Meta data inserted (4 accounts)
- [ ] Data verified in Supabase
- [ ] Hourly cron configured
- [ ] Manual sync tested
- [ ] Log file created
- [ ] Alerts configured (optional)

---

## 🚨 TROUBLESHOOTING

### Issue: "Could not find table 'campaigns'"
**Fix:** Run database migration (Step 1)

### Issue: "ModuleNotFoundError: No module named 'supabase'"
**Fix:** 
```bash
pip3 install supabase --break-system-packages
```

### Issue: Meta token expired
**Fix:** Generate new System User token

### Issue: Google data showing $0 revenue
**Expected:** Website not passing values - needs GTM fix

---

## 📞 SUPPORT

**Files Location:** `/data/workspace/`
**Logs:** `/var/log/ad_sync.log`
**Config:** `/data/workspace/config/ad_accounts.yaml`
**Scripts:** `/data/workspace/scripts/`

---

**Estimated Total Time:** 15 minutes
**Ready for Production:** ✅
