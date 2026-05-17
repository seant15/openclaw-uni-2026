# Ad Data Extraction Setup Guide

## What We've Built

### Scripts
| Script | Purpose |
|--------|---------|
| `fetch_meta_ads.py` | Pulls Meta Ads data (campaign, adset, ad levels) |
| `fetch_google_ads_full.py` | Pulls Google Ads data (campaign, ad group, ad, keyword, search term levels) |
| `insert_to_supabase.py` | Inserts fetched data into Supabase tables |
| `sync_all_accounts.py` | Orchestrates full sync for all configured accounts |
| `view_ad_data.py` | Displays fetched data in readable format |

### Configuration
- `/data/workspace/config/ad_accounts.yaml` - Account IDs and settings

### Documentation
- `/data/workspace/docs/ad_extraction_architecture.md` - Architecture comparison (Cron vs n8n vs Windsor.ai)

---

## What You Need to Provide

### 1. Meta Ad Account IDs (act_XXXXXXXXX format)

For **LEIVIP** (2 accounts):
- Account 1: `act_`___
- Account 2: `act_`___

For **PROD** (2 accounts):
- Account 1: `act_`___
- Account 2: `act_`___

### 2. Google Ads Customer IDs (10-digit format)

For **LEIVIP** (1 account):
- Customer ID: ___

For **PROD** (1 account):
- Customer ID: ___

### 3. Meta Access Token

Add to `.env`:
```bash
META_ACCESS_TOKEN=your_token_here
```

**How to get it:**
1. Go to https://developers.facebook.com/tools/explorer
2. Select your app
3. Get User Access Token
4. Grant permissions: `ads_read`, `ads_management`
5. Token should start with `EAA...`

---

## Quick Test (After Providing IDs)

### Test Meta Sync
```bash
cd /data/workspace
python3 scripts/fetch_meta_ads.py act_YOUR_ACCOUNT_ID LEIVIP
```

### Test Google Sync
```bash
cd /data/workspace
python3 scripts/fetch_google_ads_full.py YOUR_CUSTOMER_ID LEIVIP
```

### View the Data
```bash
python3 scripts/view_ad_data.py /tmp/meta_ads_xxxx.json
python3 scripts/view_ad_data.py /tmp/google_ads_xxxx.json
```

---

## Full Sync (All Accounts)

Once config is populated:
```bash
cd /data/workspace
python3 scripts/sync_all_accounts.py
```

This will:
1. Fetch data for all configured accounts
2. Insert into Supabase
3. Show summary of results

---

## Scheduling Options

### Option A: System Cron (Traditional)
```bash
# Edit crontab
crontab -e

# Add the jobs from /data/workspace/cron/ad_sync_cron.txt
```

### Option B: OpenClaw Cron (Recommended)
```bash
# Add to OpenClaw cron (already built-in)
openclaw cron add --name="ad-sync-hourly" --schedule="15 * * * *" \
  --command="python3 /data/workspace/scripts/sync_all_accounts.py"
```

---

## Data Retention Strategy

| Table | Retention | Purpose |
|-------|-----------|---------|
| `performance_hourly` | 72 hours | Real-time monitoring |
| `performance_daily` | 365 days | Reporting & analysis |
| `campaigns` | Forever | Structure reference |
| `search_terms` | 90 days | Search query analysis |
| `alerts` | 30 days | Alert history |
| `data_sync_log` | 90 days | Sync tracking |

---

## Alert Triggers (Coming Next)

Once data is flowing, we'll add:

1. **CPA Spike Alert** - CPA > 200% of 7-day average
2. **Zero Conversion Alert** - 4+ hours with spend but no conversions
3. **Budget Alert** - 80% of daily budget spent before 6 PM
4. **CTR Drop Alert** - CTR < 50% of yesterday same hour
5. **API Delay Alert** - Data not synced for 2+ hours

---

## Architecture Recommendation

**Use Cron + Python** (what we've built) over n8n or Windsor.ai because:

1. ✅ **Free** - No monthly fees
2. ✅ **Flexible** - Handle any API edge case
3. ✅ **Fast** - Hourly syncs, not daily
4. ✅ **Yours** - No vendor lock-in
5. ✅ **Scalable** - Add accounts via config

See full comparison: `/data/workspace/docs/ad_extraction_architecture.md`

---

## Next Steps

1. ⏳ **Provide account IDs** for LEIVIP and PROD
2. ⏳ **Add Meta access token** to `.env`
3. ✅ Run test sync
4. ✅ Verify data in Supabase
5. ✅ Schedule cron jobs
6. ⏳ Build alert rules
7. ⏳ Create Canvas dashboard

---

## Troubleshooting

### Meta API Errors
- **Token expired**: Regenerate at https://developers.facebook.com/tools/explorer
- **Rate limit**: Wait 5-10 minutes, retry
- **Permission denied**: Ensure `ads_read` permission granted

### Google API Errors
- **Authentication failed**: Check `GOOGLE_ADS_REFRESH_TOKEN` in `.env`
- **Customer ID invalid**: Ensure 10 digits, no dashes
- **MCC required**: Set `GOOGLE_ADS_CUSTOMER_ID` (MCC ID) in `.env`

### Supabase Errors
- **Connection failed**: Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- **Insert errors**: Check table schema matches expected format

---

## Support

Run diagnostics:
```bash
cd /data/workspace
python3 scripts/test_google_ads_api.sh  # Test Google connectivity
```

View logs:
```bash
tail -f /var/log/ad_sync_hourly.log
tail -f /var/log/ad_sync_daily.log
```
