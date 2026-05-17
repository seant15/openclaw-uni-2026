# 📊 DATA FIELD MAPPING - Meta & Google Ads → Supabase

## Overview
This document maps API fields from Meta and Google Ads to Supabase database columns.

---

## 🗄️ SUPABASE TABLE SCHEMA

### 1. `ad_accounts` Table
Stores account-level configuration.

| Supabase Field | Meta Source | Google Source | Notes |
|----------------|-------------|---------------|-------|
| `id` | UUID (auto) | UUID (auto) | Primary key |
| `client_id` | Join to clients table | Join to clients table | FK to clients |
| `platform` | 'meta_ads' | 'google_ads' | Enum value |
| `account_id` | `act_XXXXXXXXX` | `XXXXXXXXXX` (no dashes) | Store raw ID |
| `account_name` | `name` from /me/adaccounts | `customer.descriptive_name` | Display name |
| `mcc_account_id` | NULL | `GOOGLE_ADS_CUSTOMER_ID` | MCC manager ID |
| `status` | `account_status` (1=active) | Always 'active' if accessible | Enum: active/paused/disconnected |
| `daily_budget` | N/A (at campaign level) | N/A (at campaign level) | NULL for account |
| `monthly_budget` | NULL | NULL | Future use |
| `target_cpa` | NULL | NULL | Future use |
| `target_roas` | NULL | NULL | Future use |

---

### 2. `campaigns` Table
Stores campaign structure.

| Supabase Field | Meta Source | Google Source | Notes |
|----------------|-------------|---------------|-------|
| `id` | UUID (auto) | UUID (auto) | Primary key |
| `ad_account_id` | FK to ad_accounts | FK to ad_accounts | From parent account |
| `campaign_id` | `campaign.id` | `campaign.id` | Platform's native ID |
| `campaign_name` | `campaign.name` | `campaign.name` | Display name |
| `campaign_type` | `objective` | `advertising_channel_type` | 'CONVERSIONS', 'PURCHASE' → 'conversion' |
| `status` | `campaign.status` | `campaign.status` | 'ACTIVE'/'PAUSED'/'REMOVED' |
| `daily_budget` | `daily_budget` / 1M | `campaign_budget.amount_micros` / 1M | Convert micros to dollars |
| `bidding_strategy` | NULL | NULL | Future: extract from settings |
| `target_cpa` | NULL | NULL | Future use |
| `target_roas` | NULL | NULL | Future use |

---

### 3. `performance_daily` Table (PRIMARY FOR REPORTING)
Daily aggregated performance metrics.

| Supabase Field | Meta Source | Google Source | Calculation |
|----------------|-------------|---------------|-------------|
| `id` | UUID (auto) | UUID (auto) | Primary key |
| `ad_account_id` | FK | FK | From account lookup |
| `campaign_id` | FK (or NULL for account-level) | FK (or NULL) | From campaign lookup |
| `date` | `date_start` (from insights) | `segments.date` | YYYY-MM-DD format |
| **Core Metrics** | | | |
| `impressions` | `impressions` | `metrics.impressions` | Raw count |
| `clicks` | `clicks` | `metrics.clicks` | Raw count |
| `spend` | `spend` | `metrics.cost_micros` / 1M | Meta = dollars, Google = micros |
| `conversions` | Extract `purchase` from `actions` | `metrics.conversions` | For e-commerce, this is PURCHASES |
| `conversion_value` | Extract `purchase` from `action_values` | `metrics.conversions_value` | Revenue in account currency |
| **Calculated (Auto by DB)** | | | |
| `ctr` | `clicks / impressions` | Same | Stored decimal |
| `cpc` | `spend / clicks` | Same | Stored decimal |
| `cpa` | `spend / conversions` | Same | Cost per purchase |
| `roas` | `conversion_value / spend` | Same | Return on ad spend |
| `budget_utilization` | N/A | `spend / daily_budget` | % of budget used |

---

### 4. `performance_hourly` Table (REAL-TIME MONITORING)
Hourly granularity for live dashboards.

| Supabase Field | Meta Source | Google Source | Notes |
|----------------|-------------|---------------|-------|
| `id` | UUID (auto) | UUID (auto) | Primary key |
| `ad_account_id` | FK | FK | From account |
| `campaign_id` | FK | FK | From campaign |
| `timestamp` | NOW() - hour offset | NOW() - hour offset | Build from date + hour |
| `date` | Same as daily | Same as daily | YYYY-MM-DD |
| `hour` | Extract from breakdown | Extract from segments | 0-23 |
| `day_of_week` | EXTRACT(DOW FROM date) | Same | 0=Sunday |
| `impressions` | Same as daily | Same as daily | Hourly aggregate |
| `clicks` | Same as daily | Same as daily | Hourly aggregate |
| `spend` | Same as daily | Same as daily | Hourly aggregate |
| `conversions` | Same as daily | Same as daily | Hourly aggregate |
| `conversion_value` | Same as daily | Same as daily | Hourly aggregate |
| *Calculated fields same as daily* | | | |

---

## 🔍 META ADS → SUPABASE MAPPING

### Meta Insights API Fields

```python
# API Response Structure
{
  "campaign_id": "120233414633640749",
  "campaign_name": "BOF | SOUTH EUR | CBO | Purchase",
  "date_start": "2026-01-31",
  "date_stop": "2026-03-01",
  "impressions": "10000",
  "clicks": "500",
  "spend": "687.21",
  "actions": [
    {"action_type": "purchase", "value": "24"},
    {"action_type": "add_to_cart", "value": "3575"}
  ],
  "action_values": [
    {"action_type": "purchase", "value": "9198.50"}
  ]
}
```

### Mapping Logic

| Supabase Column | Meta Field | Extraction Logic |
|-----------------|------------|------------------|
| `date` | `date_start` | Parse YYYY-MM-DD |
| `impressions` | `impressions` | `int(impressions)` |
| `clicks` | `clicks` | `int(clicks)` |
| `spend` | `spend` | `float(spend)` |
| `conversions` | `actions` | Find action_type='purchase', get value |
| `conversion_value` | `action_values` | Find action_type='purchase', get value |

### Critical: Purchase vs Conversion
- Meta has MANY action types (purchase, add_to_cart, initiate_checkout, etc.)
- For e-commerce, we want **purchase** specifically
- NOT just generic "conversions" which could be leads
- Always extract from `actions` array where `action_type == 'purchase'`

---

## 🔍 GOOGLE ADS → SUPABASE MAPPING

### Google Ads API Fields

```python
# API Response Structure (GAQL)
{
  "campaign": {
    "id": "1234567890",
    "name": "Brand Search",
    "status": "ENABLED"
  },
  "metrics": {
    "impressions": 10000,
    "clicks": 500,
    "cost_micros": 687210000,  # $687.21
    "conversions": 24,  # These ARE purchases for e-commerce
    "conversions_value": 9198500000  # $9,198.50
  },
  "segments": {
    "date": "2026-03-01"
  }
}
```

### Mapping Logic

| Supabase Column | Google Field | Conversion |
|-----------------|--------------|------------|
| `date` | `segments.date` | YYYY-MM-DD |
| `impressions` | `metrics.impressions` | Direct |
| `clicks` | `metrics.clicks` | Direct |
| `spend` | `metrics.cost_micros` | `cost_micros / 1_000_000` |
| `conversions` | `metrics.conversions` | Direct (these ARE purchases) |
| `conversion_value` | `metrics.conversions_value` | `conversions_value / 1_000_000` |

### Critical: Micros Conversion
- Google Ads uses **micros** (millionths of currency unit)
- `cost_micros`: Divide by 1,000,000 to get dollars
- `conversions_value`: Divide by 1,000,000 to get dollars
- Example: `687210000` micros = `$687.21`

---

## ⚠️ IMPORTANT DIFFERENCES

### 1. Currency Units
| Platform | Spend Field | Conversion |
|----------|-------------|------------|
| Meta | `spend` | Direct dollars (string) |
| Google | `cost_micros` | Divide by 1,000,000 |

### 2. Conversion Definition
| Platform | Purchase Field | Notes |
|----------|----------------|-------|
| Meta | `actions[].value` where `action_type='purchase'` | Must extract from array |
| Google | `metrics.conversions` | Direct field (for e-commerce accounts) |

### 3. Date Handling
| Platform | Date Field | Format |
|----------|------------|--------|
| Meta | `date_start` | YYYY-MM-DD |
| Google | `segments.date` | YYYY-MM-DD |

### 4. Campaign Budget
| Platform | Budget Field | Conversion |
|----------|--------------|------------|
| Meta | `daily_budget` | Divide by 1 (already dollars) |
| Google | `campaign_budget.amount_micros` | Divide by 1,000,000 |

---

## 📋 FIELD TYPE SUMMARY

### Integer Fields (Count metrics)
- `impressions`
- `clicks`
- `conversions` (stored as DECIMAL for fractional conversions)

### Decimal Fields (Currency metrics)
- `spend` - DECIMAL(12,4)
- `conversion_value` - DECIMAL(12,4)
- `daily_budget` - DECIMAL(12,2)

### Generated Fields (Auto-calculated by DB)
- `ctr` = clicks / impressions
- `cpc` = spend / clicks
- `cpa` = spend / conversions
- `roas` = conversion_value / spend
- `budget_utilization` = spend / daily_budget

---

## 🔄 HOURLY SYNC STRATEGY

### What Data to Pull Hourly
1. **Last 3 hours** of data (to catch delayed attribution)
2. **Yesterday complete** (once per day for final numbers)
3. **Today-so-far** (current day's partial data)

### API Calls Per Account
```
Hourly Sync:
  Meta: /insights?date_preset=today&time_increment=1
  Google: GAQL with segments.date = TODAY

Daily Re-sync (once per day for 3am-6am attribution window):
  Meta: /insights?date_preset=yesterday&time_increment=1
  Google: GAQL with segments.date = YESTERDAY
```

### Deduplication Strategy
Use `UPSERT` (INSERT ... ON CONFLICT UPDATE) with unique constraint:
- `performance_daily`: UNIQUE(ad_account_id, campaign_id, date)
- `performance_hourly`: UNIQUE(ad_account_id, campaign_id, timestamp)

---

## ✅ VALIDATION CHECKLIST

Before inserting data, verify:
- [ ] Spend values are in dollars (not micros for Google)
- [ ] Conversions = purchases (not leads)
- [ ] Dates are YYYY-MM-DD format
- [ ] Account IDs match format in ad_accounts table
- [ ] No NULL values in required fields
- [ ] ROAS/CPA calculated correctly (spot check)

---

## 🧪 TEST QUERIES

### Validate Meta Data
```sql
SELECT 
  date,
  spend,
  conversions,
  conversion_value,
  roas,
  cpa
FROM performance_daily
WHERE ad_account_id = 'act_281592916520074'
ORDER BY date DESC
LIMIT 10;
```

### Validate Google Data
```sql
SELECT 
  date,
  spend,
  conversions,
  conversion_value,
  roas,
  cpa
FROM performance_daily
WHERE ad_account_id = '6218858846'
ORDER BY date DESC
LIMIT 10;
```

### Cross-Platform Comparison
```sql
SELECT 
  platform,
  SUM(spend) as total_spend,
  SUM(conversions) as total_purchases,
  AVG(roas) as avg_roas
FROM performance_daily pd
JOIN ad_accounts aa ON pd.ad_account_id = aa.id
WHERE date >= CURRENT_DATE - 7
GROUP BY platform;
```
