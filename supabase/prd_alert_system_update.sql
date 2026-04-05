-- =========================================================================
-- PRD: Alert System Redesign - Corrected Migration Script
-- =========================================================================

-- 1. 清理旧数据以防止约束冲突
DELETE FROM alerts WHERE alert_type IN ('over_pacing', 'under_pacing');

-- 2. 重新定义 alerts 表的约束 (CHECK Constraints)
-- 完全丢弃 alert_type 的强枚举约束，让 Python 规则引擎具有动态创建不同警戒类型的灵活性
ALTER TABLE alerts DROP CONSTRAINT IF EXISTS alerts_alert_type_check;

-- 拓展 severity 支持低、中、高等选项
ALTER TABLE alerts DROP CONSTRAINT IF EXISTS alerts_severity_check;
ALTER TABLE alerts ADD CONSTRAINT alerts_severity_check 
  CHECK (severity IN ('info', 'low', 'medium', 'high', 'warning', 'critical'));

-- =========================================================================

-- 3. 更新 clients 表
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS target_roas DECIMAL(4,2) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS target_cpa DECIMAL(10,2) DEFAULT NULL;

-- Backfill eCommerce clients
UPDATE clients SET target_roas = 3.0 
WHERE business_type = 'ecommerce' AND target_roas IS NULL;

-- Backfill lead_gen clients
UPDATE clients SET target_cpa = 50.0 
WHERE business_type = 'lead_gen' AND target_cpa IS NULL;

-- =========================================================================

-- 4. 创建及配置 alert_rules 表
CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    template_type TEXT NOT NULL,
    platform TEXT DEFAULT 'all',
    entity_type TEXT DEFAULT 'account',
    business_type TEXT DEFAULT 'all',
    conditions JSONB NOT NULL DEFAULT '{}',
    severity TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    action_suggested TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 安全网：如果 alert_rules 在系统中原本就已经存在，CREATE TABLE IF NOT EXISTS 会跳过执行，
-- 导致业务需要的新列无法自动补齐。因此必须加上显式的 ALTER TABLE 来拓展。
ALTER TABLE alert_rules 
ADD COLUMN IF NOT EXISTS business_type VARCHAR(20) DEFAULT 'all',
ADD COLUMN IF NOT EXISTS action_suggested TEXT DEFAULT NULL;

-- 极度重要：和 alerts 表一样，原有的 alert_rules 表也被旧业务逻辑施加了 template_type 约束。
-- 必须彻底移除该约束，否则后续插入的新变种 template_type (如 roas_above_target) 都会触发约束报错。
ALTER TABLE alert_rules DROP CONSTRAINT IF EXISTS alert_rules_template_type_check;

-- =========================================================================

-- 5. 停用废弃的旧策略
UPDATE alert_rules SET is_active = false 
WHERE template_type IN ('pacing_anomaly', 'spend_pacing');

-- =========================================================================

-- 6. 插入最新 PRD 规则
INSERT INTO alert_rules (name, template_type, platform, entity_type, business_type, conditions, severity, is_active, display_order, action_suggested, created_at, updated_at) VALUES

-- Rule 1: ROAS Above Target (eCommerce)
('ROAS Above Target - Scale Opportunity', 'roas_above_target', 'all', 'account', 'ecommerce',
 '{"metric": "roas", "comparison": "target_roas", "operator": ">", "min_spend": 100, "time_window": "today", "cooldown_hours": 24}'::jsonb,
 'medium', true, 1, 'Increase budget by 10-20%', NOW(), NOW()),

-- Rule 2: ROAS Below Target (eCommerce)
('ROAS Below Target - Pause Scaling', 'roas_below_target', 'all', 'account', 'ecommerce',
 '{"metric": "roas", "comparison": "target_roas", "operator": "<", "min_spend": 100, "time_window": "today", "cooldown_hours": 12}'::jsonb,
 'medium', true, 2, 'Do NOT increase budget. Monitor closely.', NOW(), NOW()),

-- Rule 3: ROAS Critical Drop (eCommerce)
('ROAS Critical Drop - Immediate Action', 'roas_critical_drop', 'all', 'account', 'ecommerce',
 '{"metric": "roas", "comparison": "target_roas", "operator": "<", "threshold_ratio": 0.5, "min_spend": 50, "time_window": "today", "cooldown_hours": 6}'::jsonb,
 'critical', true, 0, 'Immediate review needed. Check campaigns, offers, landing pages.', NOW(), NOW()),

-- Rule 4: CPA Above Target (Lead Gen)
('CPA Above Target - Lead Gen', 'cpa_above_target', 'all', 'account', 'lead_gen',
 '{"metric": "cpa", "comparison": "target_cpa", "operator": ">", "min_conversions": 3, "time_window": "today", "cooldown_hours": 12}'::jsonb,
 'high', true, 3, 'Review targeting and creative performance.', NOW(), NOW()),

-- Rule 5: Zero Spend 6+ Hours (All)
('Zero Spend 6+ Hours - Technical Issue', 'zero_spend_technical', 'all', 'account', 'all',
 '{"metric": "spend", "operator": "=", "value": 0, "duration_hours": 6, "min_expected_daily_spend": 20, "time_constraints": {"min_hour_of_day": 8, "max_hour_of_day": 20}, "cooldown_hours": 12}'::jsonb,
 'high', true, 0, 'Check account status, billing, campaign status', NOW(), NOW()),

-- Rule 6: Metrics Anomaly (All)
('Metrics Anomaly - Media Buyer FYI', 'metrics_anomaly', 'all', 'account', 'all',
 '{"metrics": [{"metric": "ctr", "threshold": 30, "comparison": "7d_average"}, {"metric": "cpc", "threshold": 40, "comparison": "7d_average"}, {"metric": "cpm", "threshold": 50, "comparison": "7d_average", "direction": "over"}], "min_impressions": 1000, "cooldown_hours": 8}'::jsonb,
 'low', true, 10, 'Review for optimization opportunities', NOW(), NOW());
