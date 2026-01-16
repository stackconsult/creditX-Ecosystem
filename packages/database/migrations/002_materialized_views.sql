-- ============================================================================
-- CreditX Ecosystem - Materialized Views for Semantic Entities
-- Provides pre-computed views for agent consumption
-- ============================================================================

-- Consumer Snapshot View
-- Aggregates consumer financial state for Outcome Engine
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_consumer_snapshot_v1 AS
SELECT 
    c.id AS consumer_id,
    c.tenant_id,
    c.email,
    c.name,
    cr.score AS credit_score,
    cr.score_change_30d,
    cr.utilization_ratio,
    cr.total_accounts,
    cr.derogatory_marks,
    cr.hard_inquiries_12m,
    cr.oldest_account_age_months,
    COALESCE(SUM(d.balance), 0) AS total_debt,
    COALESCE(SUM(CASE WHEN d.type = 'credit_card' THEN d.balance END), 0) AS revolving_debt,
    COALESCE(SUM(CASE WHEN d.type = 'installment' THEN d.balance END), 0) AS installment_debt,
    c.annual_income,
    CASE 
        WHEN c.annual_income > 0 THEN COALESCE(SUM(d.monthly_payment), 0) / (c.annual_income / 12)
        ELSE 0
    END AS debt_to_income_ratio,
    c.created_at,
    cr.updated_at AS credit_updated_at
FROM consumers c
LEFT JOIN credit_reports cr ON c.id = cr.consumer_id AND cr.is_current = true
LEFT JOIN debts d ON c.id = d.consumer_id AND d.status = 'active'
GROUP BY c.id, c.tenant_id, c.email, c.name, cr.score, cr.score_change_30d,
         cr.utilization_ratio, cr.total_accounts, cr.derogatory_marks,
         cr.hard_inquiries_12m, cr.oldest_account_age_months, c.annual_income,
         c.created_at, cr.updated_at;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_consumer_snapshot_id 
ON mv_consumer_snapshot_v1 (consumer_id);

CREATE INDEX IF NOT EXISTS idx_mv_consumer_snapshot_tenant 
ON mv_consumer_snapshot_v1 (tenant_id);

-- Consumer Plan Summary View
-- Tracks active plans and campaign progress
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_consumer_plan_summary_v1 AS
SELECT 
    p.id AS plan_id,
    p.consumer_id,
    p.tenant_id,
    p.plan_type,
    p.status,
    p.target_score,
    p.target_date,
    p.net_advantage_projected,
    p.net_advantage_actual,
    p.confidence_score,
    COUNT(DISTINCT c.id) AS active_campaigns,
    COUNT(DISTINCT CASE WHEN c.status = 'completed' THEN c.id END) AS completed_campaigns,
    COALESCE(AVG(c.progress_pct), 0) AS avg_progress_pct,
    COUNT(DISTINCT a.id) AS total_actions,
    COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) AS completed_actions,
    p.created_at,
    p.updated_at
FROM savings_plans p
LEFT JOIN campaigns c ON p.id = c.plan_id
LEFT JOIN action_items a ON c.id = a.campaign_id
WHERE p.status IN ('active', 'in_progress')
GROUP BY p.id, p.consumer_id, p.tenant_id, p.plan_type, p.status,
         p.target_score, p.target_date, p.net_advantage_projected,
         p.net_advantage_actual, p.confidence_score, p.created_at, p.updated_at;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_consumer_plan_id 
ON mv_consumer_plan_summary_v1 (plan_id);

CREATE INDEX IF NOT EXISTS idx_mv_consumer_plan_consumer 
ON mv_consumer_plan_summary_v1 (consumer_id);

-- Dispute Summary View
-- Tracks dispute status and outcomes for Rights & Trust Engine
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_dispute_summary_v1 AS
SELECT 
    d.id AS dispute_id,
    d.consumer_id,
    d.tenant_id,
    d.bureau,
    d.dispute_type,
    d.status,
    d.items_disputed,
    d.items_resolved,
    d.items_removed,
    d.score_impact_actual,
    d.submitted_at,
    d.response_due_at,
    d.resolved_at,
    EXTRACT(DAY FROM (COALESCE(d.resolved_at, NOW()) - d.submitted_at)) AS days_to_resolution,
    d.fcra_compliant,
    d.advocacy_letter_id,
    d.created_at
FROM disputes d
WHERE d.status != 'draft';

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_dispute_id 
ON mv_dispute_summary_v1 (dispute_id);

CREATE INDEX IF NOT EXISTS idx_mv_dispute_consumer 
ON mv_dispute_summary_v1 (consumer_id);

CREATE INDEX IF NOT EXISTS idx_mv_dispute_status 
ON mv_dispute_summary_v1 (status);

-- Consumer Security Summary View
-- Security posture for Risk & Security Engine
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_consumer_security_summary_v1 AS
SELECT 
    c.id AS consumer_id,
    c.tenant_id,
    COUNT(DISTINCT sa.id) AS total_alerts,
    COUNT(DISTINCT CASE WHEN sa.severity = 'critical' THEN sa.id END) AS critical_alerts,
    COUNT(DISTINCT CASE WHEN sa.severity = 'high' THEN sa.id END) AS high_alerts,
    COUNT(DISTINCT CASE WHEN sa.status = 'active' THEN sa.id END) AS active_alerts,
    COUNT(DISTINCT si.id) AS total_incidents,
    COUNT(DISTINCT CASE WHEN si.status = 'open' THEN si.id END) AS open_incidents,
    MAX(sa.detected_at) AS last_alert_at,
    CASE 
        WHEN COUNT(DISTINCT CASE WHEN sa.severity IN ('critical', 'high') AND sa.status = 'active' THEN sa.id END) > 0 THEN 'compromised'
        WHEN COUNT(DISTINCT CASE WHEN sa.status = 'active' THEN sa.id END) > 0 THEN 'at_risk'
        ELSE 'secure'
    END AS security_posture,
    c.mfa_enabled,
    c.last_password_change,
    c.created_at
FROM consumers c
LEFT JOIN security_alerts sa ON c.id = sa.consumer_id
LEFT JOIN security_incidents si ON c.id = si.consumer_id
GROUP BY c.id, c.tenant_id, c.mfa_enabled, c.last_password_change, c.created_at;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_security_consumer 
ON mv_consumer_security_summary_v1 (consumer_id);

-- Underwriting Summary View
-- Application and decision data for Market & Capital Engine
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_underwriting_summary_v1 AS
SELECT 
    ua.id AS application_id,
    ua.tenant_id,
    ua.applicant_id,
    ua.partner_id,
    ua.product_type,
    ua.loan_amount,
    ua.loan_term_months,
    ua.status,
    ud.decision,
    ud.risk_score,
    ud.risk_tier,
    ud.apr_offered,
    ud.monthly_payment,
    ud.conditions,
    ud.decision_at,
    ud.decided_by,
    ud.model_version,
    ua.submitted_at,
    EXTRACT(EPOCH FROM (ud.decision_at - ua.submitted_at)) / 3600 AS hours_to_decision,
    ua.created_at
FROM underwriting_applications ua
LEFT JOIN underwriting_decisions ud ON ua.id = ud.application_id;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_underwriting_app 
ON mv_underwriting_summary_v1 (application_id);

CREATE INDEX IF NOT EXISTS idx_mv_underwriting_partner 
ON mv_underwriting_summary_v1 (partner_id);

CREATE INDEX IF NOT EXISTS idx_mv_underwriting_status 
ON mv_underwriting_summary_v1 (status);

-- Partner Outcome Summary View
-- Partner performance metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_partner_outcome_summary_v1 AS
SELECT 
    p.id AS partner_id,
    p.tenant_id,
    p.name AS partner_name,
    p.partner_type,
    COUNT(DISTINCT ua.id) AS total_applications,
    COUNT(DISTINCT CASE WHEN ud.decision = 'approved' THEN ua.id END) AS approved_count,
    COUNT(DISTINCT CASE WHEN ud.decision = 'declined' THEN ua.id END) AS declined_count,
    CASE 
        WHEN COUNT(DISTINCT ua.id) > 0 
        THEN COUNT(DISTINCT CASE WHEN ud.decision = 'approved' THEN ua.id END)::FLOAT / COUNT(DISTINCT ua.id)
        ELSE 0
    END AS approval_rate,
    COALESCE(SUM(CASE WHEN ud.decision = 'approved' THEN ua.loan_amount END), 0) AS total_approved_volume,
    COALESCE(AVG(CASE WHEN ud.decision = 'approved' THEN ud.apr_offered END), 0) AS avg_apr,
    COALESCE(AVG(ud.risk_score), 0) AS avg_risk_score,
    p.fairness_score,
    p.created_at
FROM partners p
LEFT JOIN underwriting_applications ua ON p.id = ua.partner_id
LEFT JOIN underwriting_decisions ud ON ua.id = ud.application_id
GROUP BY p.id, p.tenant_id, p.name, p.partner_type, p.fairness_score, p.created_at;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_partner_outcome_id 
ON mv_partner_outcome_summary_v1 (partner_id);

-- Campaign Performance View
-- Aggregate campaign metrics for tuning
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_campaign_performance_v1 AS
SELECT 
    c.campaign_type,
    c.tenant_id,
    COUNT(DISTINCT c.id) AS total_campaigns,
    COUNT(DISTINCT CASE WHEN c.status = 'completed' THEN c.id END) AS completed_campaigns,
    COUNT(DISTINCT CASE WHEN c.status = 'active' THEN c.id END) AS active_campaigns,
    AVG(c.progress_pct) AS avg_progress_pct,
    AVG(c.duration_days) AS avg_duration_days,
    AVG(c.net_advantage_achieved) AS avg_net_advantage,
    COUNT(DISTINCT c.consumer_id) AS unique_consumers,
    SUM(c.net_advantage_achieved) AS total_net_advantage,
    DATE_TRUNC('month', c.created_at) AS cohort_month
FROM campaigns c
GROUP BY c.campaign_type, c.tenant_id, DATE_TRUNC('month', c.created_at);

CREATE INDEX IF NOT EXISTS idx_mv_campaign_perf_type 
ON mv_campaign_performance_v1 (campaign_type);

CREATE INDEX IF NOT EXISTS idx_mv_campaign_perf_tenant 
ON mv_campaign_performance_v1 (tenant_id);

-- Audit Activity Summary View
-- Compliance audit metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_audit_activity_v1 AS
SELECT 
    DATE_TRUNC('day', ae.timestamp) AS activity_date,
    ae.tenant_id,
    ae.action_type,
    COUNT(*) AS action_count,
    COUNT(DISTINCT ae.user_id) AS unique_users,
    COUNT(DISTINCT ae.resource_id) AS unique_resources,
    COUNT(DISTINCT CASE WHEN ae.action_type LIKE '%delete%' THEN ae.id END) AS delete_actions,
    COUNT(DISTINCT CASE WHEN ae.action_type LIKE '%export%' THEN ae.id END) AS export_actions,
    COUNT(DISTINCT CASE WHEN ae.requires_review THEN ae.id END) AS pending_review
FROM audit_events ae
WHERE ae.timestamp > NOW() - INTERVAL '90 days'
GROUP BY DATE_TRUNC('day', ae.timestamp), ae.tenant_id, ae.action_type;

CREATE INDEX IF NOT EXISTS idx_mv_audit_date 
ON mv_audit_activity_v1 (activity_date);

CREATE INDEX IF NOT EXISTS idx_mv_audit_tenant 
ON mv_audit_activity_v1 (tenant_id);

-- Fairness Metrics View
-- Algorithmic fairness tracking
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_fairness_summary_v1 AS
SELECT 
    DATE_TRUNC('week', ud.decision_at) AS week_start,
    ua.tenant_id,
    ua.product_type,
    COUNT(*) AS total_decisions,
    AVG(CASE WHEN ud.decision = 'approved' THEN 1 ELSE 0 END) AS overall_approval_rate,
    STDDEV(ud.risk_score) AS risk_score_stddev,
    MIN(ud.risk_score) AS min_risk_score,
    MAX(ud.risk_score) AS max_risk_score,
    AVG(ud.risk_score) AS avg_risk_score,
    COUNT(DISTINCT CASE WHEN ud.human_override THEN ud.id END) AS human_overrides,
    COUNT(DISTINCT CASE WHEN ud.human_override THEN ud.id END)::FLOAT / NULLIF(COUNT(*), 0) AS override_rate
FROM underwriting_decisions ud
JOIN underwriting_applications ua ON ud.application_id = ua.id
WHERE ud.decision_at > NOW() - INTERVAL '90 days'
GROUP BY DATE_TRUNC('week', ud.decision_at), ua.tenant_id, ua.product_type;

CREATE INDEX IF NOT EXISTS idx_mv_fairness_week 
ON mv_fairness_summary_v1 (week_start);

-- Refresh function for all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_consumer_snapshot_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_consumer_plan_summary_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_dispute_summary_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_consumer_security_summary_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_underwriting_summary_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_partner_outcome_summary_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_campaign_performance_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_audit_activity_v1;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_fairness_summary_v1;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh (requires pg_cron extension)
-- SELECT cron.schedule('refresh_views', '*/15 * * * *', 'SELECT refresh_all_materialized_views()');
