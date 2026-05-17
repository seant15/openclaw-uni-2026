# 📊 COMPLETE DATA ANALYSIS - LEIVIP & PROD
**Date:** 2026-03-01  
**Period:** Last 30 Days

---

## ✅ SYNC SUMMARY - ALL ACCOUNTS

### Meta Ads (4 Accounts) - ✅ FULL DATA

| Client | Account | Spend | Purchases | Revenue | ROAS | CPA |
|--------|---------|-------|-----------|---------|------|-----|
| LEIVIP | Primary | $3,200.23 | 131 | $46,398.21 | **14.50x** | $24.43 |
| LEIVIP | Top of Funnel | $2,133.16 | 19 | $5,658.18 | 2.65x | $112.27 |
| **LEIVIP Total** | | **$5,333.39** | **150** | **$52,056.39** | **9.76x** | **$35.56** |
| PROD | Primary | $17,433.06 | 349 | $58,424.62 | 3.35x | $49.95 |
| PROD | Backup | $2,526.24 | 52 | $7,565.89 | 2.99x | $48.58 |
| **PROD Total** | | **$19,959.30** | **401** | **$65,990.51** | **3.31x** | **$49.77** |
| **META TOTAL** | | **$25,292.69** | **551** | **$118,046.90** | **4.67x** | **$45.90** |

**Status:** ✅ Complete - Purchase value tracking correctly

---

### Google Ads (2 Accounts) - ⚠️ REVENUE DATA MISSING

| Client | Account | Spend | Conversions | Revenue | ROAS | CPA |
|--------|---------|-------|-------------|---------|------|-----|
| LEIVIP | 6218858846 | $95,116.28 | 10,919 | $1.21 | 0.00x | $8.71 |
| PROD | 4135435047 | $160,134.33 | 6,157 | $0.69 | 0.00x | $26.01 |
| **GOOGLE TOTAL** | | **$255,250.61** | **17,076** | **$1.90** | **0.00x** | **$14.95** |

**Status:** ⚠️ Partial - Conversions tracked, but **purchase value not captured**

---

## 🚨 CRITICAL ISSUE: Google Ads Revenue Tracking

### Problem
Google Ads accounts are capturing **conversion counts** but **NOT conversion values**:
- LEIVIP: 10,919 conversions, only $1.21 revenue reported
- PROD: 6,157 conversions, only $0.69 revenue reported

### Root Cause Analysis
**Possible causes:**

1. **Conversion Action Not Set to Track Value**
   - Google Ads conversion action might be configured for "Count" only
   - Need to enable "Use different values for each conversion"

2. **Wrong Conversion Action Type**
   - Currently tracking: Form fills, sign-ups, page views
   - Should be tracking: Purchase events with value

3. **Missing Value Parameter**
   - Google Tag (gtag.js) or GTM not passing `value` parameter
   - Need: `gtag('event', 'purchase', { value: 99.99, currency: 'USD' })`

4. **Delayed Attribution**
   - Google Ads has longer attribution window than Meta
   - But 30 days should capture most conversions

---

## 📋 DATA FIELD MAPPING - WHAT WE'RE PULLING

### Meta Ads API → Supabase

| Supabase Field | Meta API Field | Extraction Logic | Status |
|----------------|----------------|------------------|--------|
| `date` | `date_start` | Direct | ✅ Working |
| `impressions` | `impressions` | `int()` | ✅ Working |
| `clicks` | `clicks` | `int()` | ✅ Working |
| `spend` | `spend` | `float()` (dollars) | ✅ Working |
| `conversions` | `actions[].value` | Find `action_type='purchase'` | ✅ Working |
| `conversion_value` | `action_values[].value` | Find `action_type='purchase'` | ✅ Working |

**Meta Result:** All e-commerce metrics correctly captured.

---

### Google Ads API → Supabase

| Supabase Field | Google API Field | Conversion | Status |
|----------------|------------------|------------|--------|
| `date` | `segments.date` | Direct | ✅ Working |
| `impressions` | `metrics.impressions` | Direct | ✅ Working |
| `clicks` | `metrics.clicks` | Direct | ✅ Working |
| `spend` | `metrics.cost_micros` | `/ 1,000,000` | ✅ Working |
| `conversions` | `metrics.conversions` | Direct | ✅ Working |
| `conversion_value` | `metrics.conversions_value` | `/ 1,000,000` | ❌ **NOT WORKING** |

**Google Result:** Spend and conversions captured, but **revenue = $0**.

---

## 🔍 GOOGLE ADS CONVERSION ANALYSIS

### LEIVIP Google Ads (6218858846)

**Top Campaigns by Spend:**
| Campaign | Spend | Conversions | CPA | Issue |
|----------|-------|-------------|-----|-------|
| IT \| Search \| Brand | $8,469 | 1,591 | $5.32 | No revenue tracked |
| Italy \| Search \| Sign up | $7,917 | 914 | $8.66 | "Sign up" = not purchase |
| EU \| Search \| Brand | $7,526 | 1,822 | $4.13 | Brand = awareness |
| UNI PMAX | $4,780 | 412 | $11.60 | No value passed |

**Insight:** Campaign names suggest tracking sign-ups/registration, not purchases.

---

### PROD Google Ads (4135435047)

| Metric | Value |
|--------|-------|
| Total Spend | $160,134 |
| Conversions | 6,157 |
| CPA | $26.01 |
| Revenue | $0.69 |

**Issue:** Same pattern - conversions counted without value.

---

## 🛠️ RECOMMENDED FIXES

### Option 1: Fix Google Ads Conversion Tracking (Recommended)

**Step 1: Verify Conversion Action Settings**
```
Google Ads → Tools → Conversions → [Your Action]
→ Check "Use different values for each conversion"
→ Check "Include in 'Conversions'"
```

**Step 2: Update Google Tag / GTM**
```javascript
// Ensure value is passed
gtag('event', 'purchase', {
  transaction_id: 'ORDER_123',
  value: 199.99,
  currency: 'USD',
  items: [...]
});
```

**Step 3: Create New Purchase-Specific Conversion Action**
- Action name: "Purchase (With Value)"
- Count: One
- Value: Use different values
- Include in conversions: Yes

---

### Option 2: Work Without Google Revenue (Temporary)

If Google Ads revenue can't be fixed immediately:

1. **Pull conversion data only** from Google Ads
2. **Use Meta for ROAS/CPC reporting** (complete data)
3. **Estimate Google revenue** using Meta's average order value
4. **Set up alerts** on Google CPA (not ROAS)

---

### Option 3: Hybrid Attribution (Advanced)

Use Google Analytics 4 (GA4) as single source of truth:

```
Meta Ads → GA4 (via pixel)
Google Ads → GA4 (via gtag)
Shopify → GA4 (via GTM)

Supabase pulls from GA4 API
```

**Pros:** Unified attribution, complete data
**Cons:** Requires GA4 setup, data delay

---

## 📊 SUPABASE SCHEMA - FINAL FIELD MAPPING

### `performance_daily` Table

| Column | Type | Meta Source | Google Source | Notes |
|--------|------|-------------|---------------|-------|
| `id` | UUID | Auto | Auto | PK |
| `ad_account_id` | UUID | FK | FK | Join to ad_accounts |
| `campaign_id` | UUID | FK | FK | Join to campaigns |
| `date` | DATE | `date_start` | `segments.date` | YYYY-MM-DD |
| `impressions` | INTEGER | `impressions` | `metrics.impressions` | Raw count |
| `clicks` | INTEGER | `clicks` | `metrics.clicks` | Raw count |
| `spend` | DECIMAL(12,4) | `spend` | `cost_micros/1M` | Dollars |
| `conversions` | DECIMAL(10,4) | `actions[purchase]` | `metrics.conversions` | Purchases |
| `conversion_value` | DECIMAL(12,4) | `action_values[purchase]` | `conversions_value/1M` | Revenue |
| `ctr` | DECIMAL(8,4) | **Calculated** | **Calculated** | clicks/impressions |
| `cpc` | DECIMAL(10,4) | **Calculated** | **Calculated** | spend/clicks |
| `cpa` | DECIMAL(10,4) | **Calculated** | **Calculated** | spend/conversions |
| `roas` | DECIMAL(8,4) | **Calculated** | **Calculated** | value/spend |

---

## 🔄 HOURLY SYNC STRATEGY

### What to Pull Each Hour

**Meta Ads:**
```
/insights?date_preset=today&time_increment=1
- Last 3 hours (attribution delay)
- Breakdown by campaign
- Actions: purchase, action_values: purchase
```

**Google Ads:**
```sql
SELECT 
  segments.date,
  campaign.id,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM campaign
WHERE segments.date = TODAY
```

### Deduplication
Use UPSERT with unique constraint:
```sql
UNIQUE(ad_account_id, campaign_id, date)
```

---

## ⚠️ DATA QUALITY ALERTS TO SET UP

1. **Zero Revenue Alert**
   - If Google Ads conversions > 0 AND revenue = 0 for 24h
   - Indicates tracking issue

2. **ROAS Drop Alert**
   - If ROAS < 1.0x for 3 consecutive days
   - Unprofitable campaigns

3. **CPA Spike Alert**
   - If CPA > 200% of 7-day average
   - Campaign performance issue

4. **Spend Without Conversions**
   - If spend > $500 AND conversions = 0 for 24h
   - Broken tracking or bad traffic

---

## ✅ INSERT TO SUPABASE - CHECKLIST

Before inserting:
- [x] Meta data: Complete (spend, purchases, revenue)
- [ ] Google data: **Revenue tracking needs fixing**
- [x] All accounts mapped correctly
- [x] Field types validated
- [ ] Decide: Insert Google as-is OR fix first?

---

## 🎯 RECOMMENDATION

**Do NOT insert Google Ads data yet.**

Instead:
1. **Fix Google Ads conversion tracking** (1-2 days)
2. **Re-sync Google Ads** with proper revenue
3. **Insert complete data** to Supabase
4. **Set up hourly sync** with correct metrics

**Meta data is ready to insert now** (complete and accurate).

---

**Report Generated:** 2026-03-01  
**Next Action:** Fix Google Ads revenue tracking
