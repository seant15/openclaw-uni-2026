# 📋 COMPREHENSIVE FIELD MAPPING AUDIT
**Date:** 2026-03-02

---

## ✅ META ADS - FIELD COVERAGE

### What We're Pulling from Meta API

| Field | Meta API Source | Supabase Destination | Status |
|-------|-----------------|---------------------|--------|
| campaign_id | `campaign.id` | `campaigns.campaign_id` | ✅ |
| campaign_name | `campaign.name` | `campaigns.campaign_name` | ✅ |
| campaign_status | `campaign.status` | `campaigns.status` | ✅ |
| adset_id | `adset.id` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| adset_name | `adset.name` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| ad_id | `ad.id` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| ad_name | `ad.name` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| date | `date_start` | `performance_daily.date` | ✅ |
| impressions | `impressions` | `performance_daily.impressions` | ✅ |
| clicks | `clicks` | `performance_daily.clicks` | ✅ |
| spend | `spend` | `performance_daily.spend` | ✅ |
| purchases | `actions[purchase]` | `performance_daily.conversions` | ✅ |
| purchase_value | `action_values[purchase]` | `performance_daily.conversion_value` | ✅ |

### Meta Data Quality ✅
- **Spend:** Accurate (dollars)
- **Purchases:** Accurate (from actions array)
- **Revenue:** Accurate (from action_values array)
- **ROAS:** Correctly calculated

---

## ⚠️ GOOGLE ADS - FIELD COVERAGE

### What We're Pulling from Google API

| Field | Google API Source | Supabase Destination | Status |
|-------|-------------------|---------------------|--------|
| campaign_id | `campaign.id` | `campaigns.campaign_id` | ✅ |
| campaign_name | `campaign.name` | `campaigns.campaign_name` | ✅ |
| campaign_status | `campaign.status` | `campaigns.status` | ✅ |
| ad_group_id | `ad_group.id` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| ad_group_name | `ad_group.name` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| ad_id | `ad.id` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| ad_name | `ad.name` | Not in schema (NEW FIELD NEEDED) | ⚠️ |
| date | `segments.date` | `performance_daily.date` | ✅ |
| impressions | `metrics.impressions` | `performance_daily.impressions` | ✅ |
| clicks | `metrics.clicks` | `performance_daily.clicks` | ✅ |
| spend | `metrics.cost_micros` / 1M | `performance_daily.spend` | ✅ |
| conversions | `metrics.conversions` | `performance_daily.conversions` | ✅ |
| conversion_value | `metrics.conversions_value` / 1M | `performance_daily.conversion_value` | ⚠️ |

### Google Data Quality ⚠️
- **Spend:** Accurate (micros → dollars)
- **Conversions:** Accurate (but mostly sign-ups, not purchases)
- **Revenue:** **NEAR ZERO** ($1.21 for LEIVIP, $0.69 for PROD in 30 days)
- **Issue:** Website not passing transaction values to Google Tag

---

## 🗄️ SUPABASE SCHEMA - MISSING FIELDS

### Current Tables

| Table | Exists | Fields Complete | Notes |
|-------|--------|-----------------|-------|
| `clients` | ✅ | ✅ | Core client info |
| `ad_accounts` | ✅ | ✅ | Account mapping |
| `campaigns` | ✅ | ✅ | Campaign structure |
| `performance_hourly` | ✅ | ✅ | Hourly metrics |
| `performance_daily` | ✅ | ⚠️ | Missing `platform`, `account_id` |
| `search_terms` | ❌ | - | **NEEDS CREATION** |
| `alerts` | ❌ | - | **NEEDS CREATION** |
| `data_sync_log` | ❌ | - | **NEEDS CREATION** |

### Missing Tables to Create

1. **ad_groups** (for Google Ads ad group level data)
2. **ads** (for ad-level data)
3. **keywords** (for keyword-level data)

### Missing Fields in Existing Tables

#### `performance_daily`
```sql
-- Add these fields
ALTER TABLE performance_daily ADD COLUMN platform TEXT;
ALTER TABLE performance_daily ADD COLUMN account_id TEXT;
ALTER TABLE performance_daily ADD COLUMN campaign_type TEXT;
```

---

## 🔄 HOURLY SYNC - COMPLETE DATA FLOW

### What Gets Synced Hourly

**Meta Ads:**
```
API: /insights
  ↓
Data: campaign_id, adset_id, ad_id, date, hour
       impressions, clicks, spend, 
       purchases (from actions), purchase_value (from action_values)
  ↓
Supabase: 
  - campaigns (structure)
  - performance_hourly (if hourly breakdown needed)
  - performance_daily (aggregated)
```

**Google Ads:**
```
API: GAQL query with segments.date, segments.hour
  ↓
Data: campaign_id, ad_group_id, ad_id, date, hour
       impressions, clicks, cost_micros,
       conversions, conversions_value
  ↓
Supabase:
  - campaigns (structure)
  - performance_hourly (if hourly breakdown needed)
  - performance_daily (aggregated)
```

---

## 📊 DATA QUALITY COMPARISON

| Metric | Meta | Google | Winner |
|--------|------|--------|--------|
| Spend Accuracy | ✅ Perfect | ✅ Perfect | Tie |
| Conversion Tracking | ✅ Purchases | ⚠️ Sign-ups | Meta |
| Revenue Tracking | ✅ Full values | ❌ Near-zero | Meta |
| ROAS Calculation | ✅ Accurate | ❌ Broken | Meta |
| Hourly Granularity | ✅ Available | ✅ Available | Tie |
| Historical Data | ✅ 30 days | ✅ 30 days | Tie |

---

## 🎯 RECOMMENDATIONS

### Immediate (Today)
1. ✅ **Insert Meta data** - Complete and accurate
2. ⚠️ **Fix Google conversion values** - Website needs to pass `value` to gtag
3. 🗄️ **Create missing tables** - ad_groups, ads, keywords, search_terms

### Short-term (This Week)
1. Set up hourly cron for Meta (working perfectly)
2. Set up hourly cron for Google (structure only, values pending fix)
3. Add Shopify data integration
4. Create alert system

### Long-term
1. Fix Google Ads revenue tracking (need GTM/website access)
2. Add cross-device attribution
3. Implement view-through conversion tracking

---

## ✅ CHECKLIST BEFORE HOURLY SYNC

- [x] Meta scripts working
- [x] Google scripts working (structure)
- [ ] Supabase tables created
- [ ] Field mapping verified
- [ ] Insert logic tested
- [ ] Hourly cron configured
- [ ] Alert thresholds set
- [ ] OpenClaw agent briefed

---

## 🚀 READY TO PROCEED?

**Meta:** Ready to insert ✅
**Google:** Ready for structure, revenue pending fix ⚠️
**Supabase:** Needs table creation 🗄️
