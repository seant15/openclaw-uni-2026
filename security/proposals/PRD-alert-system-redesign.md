# Alert System Redesign - PRD

**Project:** eCommerce Alert System Redesign  
**Date:** 2026-04-04  
**Author:** Clover (AI Operations)  
**Status:** Ready for Development  

---

## 1. Executive Summary

### Problem Statement
Current alert system generates too many low-value "over-pacing" alerts that don't drive business decisions. Media buyers are experiencing alert fatigue with 10+ daily alerts per account, most of which require no action.

### Solution
Redesign alert rules to focus on **ROAS-driven business outcomes** rather than pacing metrics. New system will generate 2-3 actionable alerts per day per account, each with a clear business implication.

### Success Metrics
- Reduce daily alerts per account from 10+ to 2-3
- 100% of alerts have clear action items
- Zero "pacing-only" alerts for eCommerce clients

---

## 2. Database Changes Required

### 2.1 Add Target Columns to `clients` Table

```sql
-- Add target metrics columns
ALTER TABLE clients 
ADD COLUMN target_roas DECIMAL(4,2) DEFAULT NULL,
ADD COLUMN target_cpa DECIMAL(10,2) DEFAULT NULL,
ADD COLUMN alert_config JSONB DEFAULT '{}'::jsonb;

-- Add comment for documentation
COMMENT ON COLUMN clients.target_roas IS 'Target ROAS for eCommerce clients. Alert rules reference this value.';
COMMENT ON COLUMN clients.target_cpa IS 'Target CPA for lead gen clients. Secondary metric for eCommerce.';
COMMENT ON COLUMN clients.alert_config IS 'Per-client alert configuration overrides (JSONB)';
```

### 2.2 Backfill Existing Clients

```sql
-- Set default targets for existing eCommerce clients
UPDATE clients 
SET target_roas = 3.0,
    target_cpa = NULL
WHERE business_type = 'ecommerce' 
  AND target_roas IS NULL;

-- Set default targets for lead gen clients
UPDATE clients 
SET target_cpa = 50.0,
    target_roas = NULL
WHERE business_type = 'leadgen' 
  AND target_cpa IS NULL;
```

### 2.3 Update `alert_rules` Table

```sql
-- Add business_type filter to rules
ALTER TABLE alert_rules 
ADD COLUMN business_type VARCHAR(20) DEFAULT 'all';

-- Add action_suggested field
ALTER TABLE alert_rules 
ADD COLUMN action_suggested TEXT DEFAULT NULL;
```

---

## 3. New Alert Rules Specification

### Rule 1: ROAS Above Target - Scale Opportunity

| Field | Value |
|-------|-------|
| **Rule ID** | `roas_above_target` |
| **Name** | ROAS Above Target - Scale Opportunity |
| **Business Type** | ecommerce |
| **Severity** | medium |
| **Cooldown** | 24 hours |

**Trigger Conditions:**
```json
{
  "metric": "roas",
  "comparison": "target_roas",
  "operator": ">",
  "min_spend": 100,
  "time_window": "today"
}
```

**Alert Message Template:**
```
🟢 {account_name}: ROAS {actual_roas}x (target: {target_roas}x). Scale opportunity! Consider +10% budget. Current spend: ${spend}.
```

**Action Suggested:** Increase budget by 10-20%

---

### Rule 2: ROAS Below Target - Pause Scaling

| Field | Value |
|-------|-------|
| **Rule ID** | `roas_below_target` |
| **Name** | ROAS Below Target - Pause Scaling |
| **Business Type** | ecommerce |
| **Severity** | medium |
| **Cooldown** | 12 hours |

**Trigger Conditions:**
```json
{
  "metric": "roas",
  "comparison": "target_roas",
  "operator": "<",
  "min_spend": 100,
  "time_window": "today"
}
```

**Alert Message Template:**
```
🟡 {account_name}: ROAS {actual_roas}x below target ({target_roas}x). STOP scaling. Monitor performance.
```

**Action Suggested:** Do NOT increase budget. Monitor closely.

---

### Rule 3: ROAS Critical Drop - Immediate Action

| Field | Value |
|-------|-------|
| **Rule ID** | `roas_critical_drop` |
| **Name** | ROAS Critical Drop - Immediate Action |
| **Business Type** | ecommerce |
| **Severity** | critical |
| **Cooldown** | 6 hours |

**Trigger Conditions:**
```json
{
  "metric": "roas",
  "comparison": "target_roas",
  "operator": "<",
  "threshold_ratio": 0.5,
  "min_spend": 50,
  "time_window": "today"
}
```

**Alert Message Template:**
```
🔴 {account_name}: ROAS CRITICAL {actual_roas}x (50% below target {target_roas}x). IMMEDIATE ACTION REQUIRED!
```

**Action Suggested:** Immediate review needed. Check campaigns, offers, landing pages.

---

### Rule 4: CPA Above Target - Lead Gen Alert

| Field | Value |
|-------|-------|
| **Rule ID** | `cpa_above_target` |
| **Name** | CPA Above Target - Lead Gen |
| **Business Type** | leadgen |
| **Severity** | high |
| **Cooldown** | 12 hours |

**Trigger Conditions:**
```json
{
  "metric": "cpa",
  "comparison": "target_cpa",
  "operator": ">",
  "min_conversions": 3,
  "time_window": "today"
}
```

**Alert Message Template:**
```
🟡 {account_name}: CPA ${actual_cpa} above target (${target_cpa}). Lead cost increasing. Review targeting.
```

---

### Rule 5: Zero Spend 6+ Hours - Technical Issue

| Field | Value |
|-------|-------|
| **Rule ID** | `zero_spend_technical` |
| **Name** | Zero Spend 6+ Hours - Technical Issue |
| **Business Type** | all |
| **Severity** | high |
| **Cooldown** | 12 hours |

**Trigger Conditions:**
```json
{
  "metric": "spend",
  "operator": "=",
  "value": 0,
  "duration_hours": 6,
  "min_expected_daily_spend": 20,
  "time_constraints": {
    "min_hour_of_day": 8,
    "max_hour_of_day": 20
  }
}
```

**Alert Message Template:**
```
🔴 {account_name}: ZERO spend for 6+ hours ({platform}). Check account/billing/campaign status! Expected daily: ${expected_daily}.
```

**Action Suggested:** Check account status, billing, campaign status

---

### Rule 6: Metrics Anomaly - Media Buyer FYI

| Field | Value |
|-------|-------|
| **Rule ID** | `metrics_anomaly` |
| **Name** | Metrics Anomaly - Media Buyer FYI |
| **Business Type** | all |
| **Severity** | low |
| **Cooldown** | 8 hours |

**Trigger Conditions:**
```json
{
  "metrics": [
    {"metric": "ctr", "threshold": 30, "comparison": "7d_average"},
    {"metric": "cpc", "threshold": 40, "comparison": "7d_average"},
    {"metric": "cpm", "threshold": 50, "comparison": "7d_average", "direction": "over"}
  ],
  "min_impressions": 1000
}
```

**Alert Message Template:**
```
📊 {account_name}: {metric} {change_direction} {change_pct}% ({metric_value} vs avg {metric_avg}). FYI for optimization.
```

---

## 4. Data Cleanup Required

### 4.1 Delete Old Over-Pacing Alerts

```sql
-- Delete all existing over_pacing and under_pacing alerts
DELETE FROM alerts 
WHERE alert_type IN ('over_pacing', 'under_pacing');

-- Verify deletion count
SELECT COUNT(*) as deleted_count 
FROM alerts 
WHERE alert_type IN ('over_pacing', 'under_pacing');
```

### 4.2 Archive Old Alert Rules

```sql
-- Deactivate old pacing-based rules (don't delete for history)
UPDATE alert_rules 
SET is_active = false,
    updated_at = NOW()
WHERE template_type IN ('pacing_anomaly', 'spend_pacing')
   OR name ILIKE '%pacing%';
```

---

## 5. SQL Insert Statements for New Rules

```sql
-- Insert new alert rules
INSERT INTO alert_rules (
  name, 
  template_type, 
  platform, 
  entity_type, 
  business_type,
  conditions, 
  severity, 
  is_active, 
  display_order,
  action_suggested,
  created_at,
  updated_at
) VALUES 

-- Rule 1: ROAS Above Target
(
  'ROAS Above Target - Scale Opportunity',
  'roas_above_target',
  'all',
  'account',
  'ecommerce',
  '{
    "metric": "roas",
    "comparison": "target_roas",
    "operator": ">",
    "min_spend": 100,
    "time_window": "today",
    "cooldown_hours": 24
  }'::jsonb,
  'medium',
  true,
  1,
  'Increase budget by 10-20%',
  NOW(),
  NOW()
),

-- Rule 2: ROAS Below Target
(
  'ROAS Below Target - Pause Scaling',
  'roas_below_target',
  'all',
  'account',
  'ecommerce',
  '{
    "metric": "roas",
    "comparison": "target_roas",
    "operator": "<",
    "min_spend": 100,
    "time_window": "today",
    "cooldown_hours": 12
  }'::jsonb,
  'medium',
  true,
  2,
  'Do NOT increase budget. Monitor closely.',
  NOW(),
  NOW()
),

-- Rule 3: ROAS Critical Drop
(
  'ROAS Critical Drop - Immediate Action',
  'roas_critical_drop',
  'all',
  'account',
  'ecommerce',
  '{
    "metric": "roas",
    "comparison": "target_roas",
    "operator": "<",
    "threshold_ratio": 0.5,
    "min_spend": 50,
    "time_window": "today",
    "cooldown_hours": 6
  }'::jsonb,
  'critical',
  true,
  0,
  'Immediate review needed. Check campaigns, offers, landing pages.',
  NOW(),
  NOW()
),

-- Rule 4: CPA Above Target (Lead Gen)
(
  'CPA Above Target - Lead Gen',
  'cpa_above_target',
  'all',
  'account',
  'leadgen',
  '{
    "metric": "cpa",
    "comparison": "target_cpa",
    "operator": ">",
    "min_conversions": 3,
    "time_window": "today",
    "cooldown_hours": 12
  }'::jsonb,
  'high',
  true,
  3,
  'Review targeting and creative performance.',
  NOW(),
  NOW()
),

-- Rule 5: Zero Spend Technical
(
  'Zero Spend 6+ Hours - Technical Issue',
  'zero_spend_technical',
  'all',
  'account',
  'all',
  '{
    "metric": "spend",
    "operator": "=",
    "value": 0,
    "duration_hours": 6,
    "min_expected_daily_spend": 20,
    "time_constraints": {
      "min_hour_of_day": 8,
      "max_hour_of_day": 20
    },
    "cooldown_hours": 12
  }'::jsonb,
  'high',
  true,
  0,
  'Check account status, billing, campaign status',
  NOW(),
  NOW()
),

-- Rule 6: Metrics Anomaly
(
  'Metrics Anomaly - Media Buyer FYI',
  'metrics_anomaly',
  'all',
  'account',
  'all',
  '{
    "metrics": [
      {"metric": "ctr", "threshold": 30, "comparison": "7d_average"},
      {"metric": "cpc", "threshold": 40, "comparison": "7d_average"},
      {"metric": "cpm", "threshold": 50, "comparison": "7d_average", "direction": "over"}
    ],
    "min_impressions": 1000,
    "cooldown_hours": 8
  }'::jsonb,
  'low',
  true,
  10,
  'Review for optimization opportunities',
  NOW(),
  NOW()
);
```

---

## 6. Alert Generation Logic (Pseudocode)

```python
def generate_alerts():
    """Main alert generation function - to be implemented by developer"""
    
    for client in get_active_clients():
        for rule in get_active_rules(client.business_type):
            
            # Check cooldown
            if was_alert_sent_recently(client, rule, rule.conditions.cooldown_hours):
                continue
            
            # Evaluate rule conditions
            if rule.template_type == 'roas_above_target':
                if check_roas_above_target(client, rule.conditions):
                    create_alert(client, rule)
                    
            elif rule.template_type == 'roas_below_target':
                if check_roas_below_target(client, rule.conditions):
                    create_alert(client, rule)
                    
            elif rule.template_type == 'roas_critical_drop':
                if check_roas_critical_drop(client, rule.conditions):
                    create_alert(client, rule)
                    
            elif rule.template_type == 'cpa_above_target':
                if check_cpa_above_target(client, rule.conditions):
                    create_alert(client, rule)
                    
            elif rule.template_type == 'zero_spend_technical':
                if check_zero_spend(client, rule.conditions):
                    create_alert(client, rule)
                    
            elif rule.template_type == 'metrics_anomaly':
                if check_metrics_anomaly(client, rule.conditions):
                    create_alert(client, rule)


def check_roas_above_target(client, conditions):
    """Check if ROAS is above target"""
    today_performance = get_today_performance(client.id)
    
    if today_performance.spend < conditions.min_spend:
        return False
        
    if today_performance.roas > client.target_roas:
        return True
        
    return False


def check_roas_critical_drop(client, conditions):
    """Check if ROAS is below 50% of target"""
    today_performance = get_today_performance(client.id)
    
    if today_performance.spend < conditions.min_spend:
        return False
        
    critical_threshold = client.target_roas * conditions.threshold_ratio
    
    if today_performance.roas < critical_threshold:
        return True
        
    return False


def check_zero_spend(client, conditions):
    """Check if account has zero spend for 6+ hours"""
    recent_hours = get_hourly_performance_last_n_hours(client.id, conditions.duration_hours)
    
    # Check if within business hours
    current_hour = get_current_hour(client.timezone)
    if current_hour < conditions.time_constraints.min_hour_of_day:
        return False
    if current_hour > conditions.time_constraints.max_hour_of_day:
        return False
    
    # Check expected daily spend
    baseline = get_account_baseline(client.id)
    if baseline.avg_daily_spend < conditions.min_expected_daily_spend:
        return False
    
    # Check if all recent hours have zero spend
    if all(hour.spend == 0 for hour in recent_hours):
        return True
        
    return False
```

---

## 7. Acceptance Criteria

### Functional Requirements
- [ ] `clients` table has `target_roas` and `target_cpa` columns
- [ ] All existing eCommerce clients have `target_roas` backfilled
- [ ] All existing lead gen clients have `target_cpa` backfilled
- [ ] 6 new alert rules are active in `alert_rules` table
- [ ] Old pacing alerts (over_pacing, under_pacing) are deleted
- [ ] Old pacing rules are deactivated
- [ ] New alerts generate with correct severity and cooldown
- [ ] Alert messages include action suggestions

### Non-Functional Requirements
- [ ] Alert generation completes within 5 minutes for all accounts
- [ ] No duplicate alerts within cooldown period
- [ ] Alert frequency reduced by 70%+ (from 10+/day to 2-3/day per account)

---

## 8. Rollout Plan

### Phase 1: Database Changes (Day 1)
1. Add columns to `clients` table
2. Backfill target values
3. Deactivate old rules

### Phase 2: Data Cleanup (Day 1)
1. Delete old over-pacing alerts
2. Insert new alert rules

### Phase 3: Logic Implementation (Day 2-3)
1. Implement new alert generation logic
2. Test with staging data

### Phase 4: Production Deploy (Day 4)
1. Deploy to production
2. Monitor alert generation for 24 hours

---

**End of PRD**
