# Alert System Improvement Proposal

## Current Issues

### 1. Over-Pacing Alert Frequency Problem

**Observation from data:**
- Over-pacing alerts trigger at **10:00 AM** every day for multiple accounts
- Threshold seems too sensitive: triggers at 122%-757% of expected spend
- Many alerts are for small absolute amounts (e.g., $10 vs $6 expected)
- **All alerts are unhandled** (status: "new") — indicating alert fatigue

**Root Cause:**
- Current logic likely triggers when `actual_spend > expected_spend * threshold`
- Threshold too low (possibly 120% or lower)
- No minimum spend floor (alerts on $10 spend are not actionable)
- Daily recurring pattern suggests time-based check without cooldown

### 2. Proposed Threshold Adjustments

| Metric | Current (Estimated) | Proposed | Rationale |
|--------|---------------------|----------|-----------|
| Over-pacing % | ~120% | **150%** | Reduce noise, catch real issues |
| Minimum spend floor | $0 | **$50** | Ignore small accounts |
| Under-pacing % | ~70% | **50%** | Only catch serious under-delivery |
| Zero spend hours | 6 hours | **4 hours** | Faster detection of real issues |
| Cooldown between same-type alerts | None | **6 hours** | Prevent spam |

---

## Rule Template System Design

### Template Schema (for `alert_rules.conditions`)

```json
{
  "template_type": "pacing_anomaly",
  "version": "1.0",
  
  // Core threshold
  "threshold": {
    "type": "percentage",        // percentage | absolute | std_dev
    "value": 150,                // 150% = 1.5x
    "direction": "over"          // over | under | both
  },
  
  // Minimum floor to ignore small accounts
  "min_spend_floor": {
    "enabled": true,
    "value": 50,                 // $50 minimum
    "currency": "USD"
  },
  
  // Time-based rules
  "time_constraints": {
    "min_hour_of_day": 8,        // Don't alert before 8 AM
    "max_hour_of_day": 20,       // Don't alert after 8 PM
    "min_day_of_week": 1,        // Monday
    "max_day_of_week": 5         // Friday
  },
  
  // Cooldown to prevent spam
  "cooldown": {
    "enabled": true,
    "duration_hours": 6          // Same alert type per account every 6h max
  },
  
  // Severity escalation based on severity
  "severity_tiers": [
    {"threshold": 200, "severity": "critical"},
    {"threshold": 150, "severity": "high"},
    {"threshold": 120, "severity": "medium"}
  ]
}
```

---

## Proposed Rule Templates

### Template 1: Pacing Anomaly (Over/Under)

```json
{
  "name": "Cost Pacing - Over",
  "template_type": "pacing_anomaly",
  "platform": "all",
  "entity_type": "account",
  "conditions": {
    "threshold": {"type": "percentage", "value": 150, "direction": "over"},
    "min_spend_floor": {"enabled": true, "value": 50},
    "time_constraints": {"min_hour_of_day": 8, "max_hour_of_day": 20},
    "cooldown": {"enabled": true, "duration_hours": 6},
    "severity_tiers": [
      {"threshold": 200, "severity": "critical"},
      {"threshold": 150, "severity": "high"}
    ]
  },
  "severity": "high",
  "is_active": true
}
```

### Template 2: Cost Pacing - Under

```json
{
  "name": "Cost Pacing - Under",
  "template_type": "pacing_anomaly",
  "platform": "all",
  "entity_type": "account",
  "conditions": {
    "threshold": {"type": "percentage", "value": 50, "direction": "under"},
    "min_spend_floor": {"enabled": true, "value": 50},
    "time_constraints": {"min_hour_of_day": 14, "max_hour_of_day": 20},
    "cooldown": {"enabled": true, "duration_hours": 6},
    "severity_tiers": [
      {"threshold": 30, "severity": "critical"},
      {"threshold": 50, "severity": "high"}
    ]
  },
  "severity": "high",
  "is_active": true
}
```

### Template 3: Zero Spend Detection

```json
{
  "name": "Zero Spend Detection",
  "template_type": "zero_spend",
  "platform": "all",
  "entity_type": "account",
  "conditions": {
    "consecutive_zero_hours": 4,
    "min_expected_daily_spend": 20,
    "time_constraints": {"min_hour_of_day": 10},
    "cooldown": {"enabled": true, "duration_hours": 12}
  },
  "severity": "critical",
  "is_active": true
}
```

### Template 4: ROAS Drop (Daily Performance)

```json
{
  "name": "ROAS Drop - Daily",
  "template_type": "metric_threshold",
  "platform": "all",
  "entity_type": "account",
  "conditions": {
    "metric": "roas",
    "threshold": {"type": "percentage", "value": 70, "direction": "under"},
    "comparison": "7d_average",     // Compare to 7-day average
    "min_spend_floor": {"enabled": true, "value": 100},
    "cooldown": {"enabled": true, "duration_hours": 24}
  },
  "severity": "high",
  "is_active": true
}
```

### Template 5: CPA Spike (Daily Performance)

```json
{
  "name": "CPA Spike - Daily",
  "template_type": "metric_threshold",
  "platform": "all",
  "entity_type": "account",
  "conditions": {
    "metric": "cpa",
    "threshold": {"type": "percentage", "value": 150, "direction": "over"},
    "comparison": "7d_average",
    "min_conversions": 3,            // Need at least 3 conversions
    "cooldown": {"enabled": true, "duration_hours": 24}
  },
  "severity": "high",
  "is_active": true
}
```

### Template 6: CTR Drop (Hourly Performance)

```json
{
  "name": "CTR Drop - Hourly",
  "template_type": "metric_threshold",
  "platform": "all",
  "entity_type": "campaign",
  "conditions": {
    "metric": "ctr",
    "threshold": {"type": "percentage", "value": 50, "direction": "under"},
    "comparison": "24h_average",
    "min_impressions": 1000,
    "cooldown": {"enabled": true, "duration_hours": 4}
  },
  "severity": "medium",
  "is_active": true
}
```

---

## Implementation Plan

### Phase 1: Fix Over-Pacing (Immediate)

1. Update current alert generation logic to use new thresholds:
   - Over-pacing: 150% (was ~120%)
   - Min spend floor: $50
   - Cooldown: 6 hours

2. SQL to update existing rules:
```sql
-- Update existing rules with new conditions
UPDATE alert_rules 
SET conditions = jsonb_set(
  conditions,
  '{threshold}',
  '{"type": "percentage", "value": 150, "direction": "over"}'::jsonb
),
updated_at = NOW()
WHERE template_type = 'pacing_anomaly';
```

### Phase 2: Template System (Short-term)

1. Create `alert_rule_templates` table
2. Build rule creation UI/API using templates
3. Migrate existing rules to template format

### Phase 3: Advanced Rules (Medium-term)

1. Add ROAS/CPA alerts based on daily_performance
2. Add CTR/CPC alerts based on hourly_performance
3. Add anomaly detection (std dev based)

---

## Quick Fix SQL (for immediate relief)

```sql
-- Add cooldown check to alert generation query
-- Only create alert if no same-type alert exists in last 6 hours

INSERT INTO alerts (...)
SELECT ...
WHERE NOT EXISTS (
  SELECT 1 FROM alerts a2
  WHERE a2.client_id = NEW.client_id
    AND a2.platform = NEW.platform
    AND a2.alert_type = 'over_pacing'
    AND a2.created_at > NOW() - INTERVAL '6 hours'
)
AND actual_spend > expected_spend * 1.5  -- 150% threshold
AND actual_spend > 50;  -- $50 minimum
```

---

*Generated: 2026-04-04*
*Purpose: Reduce alert fatigue while maintaining actionable insights*
