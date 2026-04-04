# eCommerce Alert Rules - Business Logic Design

## Core Philosophy
- **ROAS is king** — everything revolves around ROAS performance
- **Action-oriented alerts** — each alert implies a specific action
- **Reduce noise** — only alert when human intervention is needed
- **Ignore minor pacing issues** — focus on business outcomes

---

## Alert Rule Set for eCommerce Clients

### Rule 1: ROAS Above Target — Scale Opportunity 🟢

**Business Logic:**
- ROAS > target means we can scale budget
- Missing this = leaving money on the table

**Trigger Conditions:**
```json
{
  "name": "ROAS Above Target - Scale Opportunity",
  "template_type": "roas_scale_opportunity",
  "business_type": "ecommerce",
  "conditions": {
    "metric": "roas",
    "comparison": "target_roas",
    "threshold_operator": ">",
    "threshold_value": 1.0,
    "min_spend": 100,
    "time_window": "today",
    "cooldown_hours": 24
  },
  "severity": "medium",
  "action_suggested": "Increase budget by 10-20%",
  "message_template": "🟢 {account_name}: ROAS {actual_roas}x (target: {target_roas}x). Scale opportunity! Consider +10% budget."
}
```

**Alert Message Example:**
> 🟢 UB+ Meta: ROAS 4.2x (target: 3.0x). Scale opportunity! Consider +10% budget. Current spend: $1,245.

---

### Rule 2: ROAS Below Target — Stop Scaling 🟡

**Business Logic:**
- ROAS < target = don't increase budget
- This is a warning, not critical yet

**Trigger Conditions:**
```json
{
  "name": "ROAS Below Target - Pause Scaling",
  "template_type": "roas_below_target",
  "business_type": "ecommerce",
  "conditions": {
    "metric": "roas",
    "comparison": "target_roas",
    "threshold_operator": "<",
    "threshold_value": 1.0,
    "min_spend": 100,
    "time_window": "today",
    "cooldown_hours": 12
  },
  "severity": "medium",
  "action_suggested": "Do NOT increase budget. Monitor closely.",
  "message_template": "🟡 {account_name}: ROAS {actual_roas}x below target ({target_roas}x). STOP scaling. Monitor performance."
}
```

---

### Rule 3: ROAS Critical Drop — Immediate Attention 🔴

**Business Logic:**
- ROAS < 50% of target = something is seriously wrong
- Needs immediate investigation

**Trigger Conditions:**
```json
{
  "name": "ROAS Critical Drop - Immediate Action",
  "template_type": "roas_critical_drop",
  "business_type": "ecommerce",
  "conditions": {
    "metric": "roas",
    "comparison": "target_roas",
    "threshold_operator": "<",
    "threshold_value": 0.5,
    "min_spend": 50,
    "time_window": "today",
    "cooldown_hours": 6
  },
  "severity": "critical",
  "action_suggested": "Immediate review needed. Check campaigns, offers, landing pages.",
  "message_template": "🔴 {account_name}: ROAS CRITICAL {actual_roas}x (50% below target {target_roas}x). IMMEDIATE ACTION REQUIRED!"
}
```

**Alert Message Example:**
> 🔴 PROD Google: ROAS CRITICAL 0.8x (50% below target 2.5x). IMMEDIATE ACTION REQUIRED! Check campaigns immediately.

---

### Rule 4: Zero Spend > 6 Hours — Technical Issue 🔴

**Business Logic:**
- 6+ hours zero spend = account/billing/campaign issue
- Not about pacing — about technical problems
- Only alert when there's truly NO spend

**Trigger Conditions:**
```json
{
  "name": "Zero Spend 6+ Hours - Technical Issue",
  "template_type": "zero_spend_technical",
  "business_type": "all",
  "conditions": {
    "metric": "spend",
    "threshold_operator": "=",
    "threshold_value": 0,
    "duration_hours": 6,
    "min_expected_daily_spend": 20,
    "time_constraints": {
      "min_hour_of_day": 8,
      "max_hour_of_day": 20
    },
    "cooldown_hours": 12
  },
  "severity": "high",
  "action_suggested": "Check account status, billing, campaign status",
  "message_template": "🔴 {account_name}: ZERO spend for 6+ hours ({platform}). Check account/billing/campaign status!"
}
```

**Alert Message Example:**
> 🔴 SESUNG Google: ZERO spend for 6+ hours. Check account/billing/campaign status! Expected daily: $350.

---

### Rule 5: Other Metrics Anomaly — FYI for Media Buyers 📊

**Business Logic:**
- CTR, CPC, CPM anomalies don't need immediate action
- But media buyers should be aware
- Send to Slack channel for visibility, not urgent

**Metrics to Monitor:**
- CTR change > ±30% vs 7-day average
- CPC change > ±40% vs 7-day average
- CPM spike > +50% vs 7-day average

**Trigger Conditions:**
```json
{
  "name": "Metrics Anomaly - Media Buyer FYI",
  "template_type": "metrics_anomaly",
  "business_type": "all",
  "conditions": {
    "metrics": [
      {
        "metric": "ctr",
        "threshold": 30,
        "comparison": "7d_average"
      },
      {
        "metric": "cpc",
        "threshold": 40,
        "comparison": "7d_average"
      },
      {
        "metric": "cpm",
        "threshold": 50,
        "comparison": "7d_average",
        "direction": "over"
      }
    ],
    "min_impressions": 1000,
    "cooldown_hours": 8
  },
  "severity": "low",
  "action_suggested": "Review for optimization opportunities",
  "message_template": "📊 {account_name}: {metric} {change_direction} {change_pct}% ({metric_value} vs avg {metric_avg}). FYI for optimization.",
  "delivery_channel": "slack_channel"
}
```

**Alert Message Example:**
> 📊 UB+ Meta: CTR down 35% (0.8% vs avg 1.2%). CPC up 42%. FYI for optimization.

---

## Alert Priority Matrix

| Priority | Alert Type | Response Time | Action |
|----------|-----------|---------------|--------|
| P0 | ROAS Critical Drop | Immediate | Stop campaigns, investigate |
| P1 | Zero Spend 6h+ | 1 hour | Check account status |
| P2 | ROAS Above Target | Same day | Scale budget |
| P2 | ROAS Below Target | Same day | Stop scaling |
| P3 | Metrics Anomaly | Within 24h | Review & optimize |

---

## What We DON'T Alert On (Intentionally)

| Scenario | Reason |
|----------|--------|
| Over-pacing | If ROAS is good, over-pacing is fine |
| Under-pacing | If ROAS is bad, under-pacing is actually good |
| Small spend accounts (< $50/day) | Not worth the noise |
| Pacing within 50-150% | ROAS matters more than pacing |
| Weekend/holiday anomalies | Business hours only |

---

## Database Schema for New Rules

```sql
-- Add new template types
INSERT INTO alert_rules (name, template_type, platform, entity_type, conditions, severity, is_active, display_order) VALUES

-- Rule 1: ROAS Above Target
('ROAS Above Target - Scale Opportunity', 'roas_scale_opportunity', 'all', 'account', 
 '{
   "metric": "roas",
   "comparison": "target_roas",
   "operator": ">",
   "min_spend": 100,
   "cooldown_hours": 24
 }'::jsonb, 'medium', true, 1),

-- Rule 2: ROAS Below Target  
('ROAS Below Target - Pause Scaling', 'roas_below_target', 'all', 'account',
 '{
   "metric": "roas", 
   "comparison": "target_roas",
   "operator": "<",
   "min_spend": 100,
   "cooldown_hours": 12
 }'::jsonb, 'medium', true, 2),

-- Rule 3: ROAS Critical Drop
('ROAS Critical Drop - Immediate Action', 'roas_critical_drop', 'all', 'account',
 '{
   "metric": "roas",
   "comparison": "target_roas", 
   "operator": "<",
   "threshold_ratio": 0.5,
   "min_spend": 50,
   "cooldown_hours": 6
 }'::jsonb, 'critical', true, 0),

-- Rule 4: Zero Spend Technical
('Zero Spend 6+ Hours - Technical Issue', 'zero_spend_technical', 'all', 'account',
 '{
   "metric": "spend",
   "operator": "=",
   "value": 0,
   "duration_hours": 6,
   "min_expected_daily": 20,
   "cooldown_hours": 12
 }'::jsonb, 'high', true, 0);
```

---

## Implementation Notes

### Target ROAS Source
Need to determine where target ROAS is stored:
- Option A: Add `target_roas` column to `clients` table
- Option B: Add `target_roas` to `account_daily_baselines` 
- Option C: Hardcode in alert_rules.conditions per client

### Recommended: Add to clients table
```sql
ALTER TABLE clients ADD COLUMN target_roas DECIMAL(4,2) DEFAULT 3.0;
ALTER TABLE clients ADD COLUMN target_cpa DECIMAL(10,2);
```

---

*Design based on: Sean's business requirements, 2026-04-04*
*Focus: Actionable alerts that drive revenue decisions*
