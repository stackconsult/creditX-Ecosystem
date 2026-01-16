-- ============================================================================
-- CreditX Ecosystem - Initial Database Schema
-- PostgreSQL 17 with extensions: pgcrypto, pg_trgm, btree_gin
-- Multi-tenant architecture with schema isolation
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================================================
-- CORE TABLES (public schema - shared across tenants)
-- ============================================================================

-- Tenants table
CREATE TABLE IF NOT EXISTS public.tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    schema_name VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tenants_slug ON public.tenants(slug);
CREATE INDEX idx_tenants_status ON public.tenants(status);

-- Users table (authentication)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'manager', 'user', 'viewer')),
    face VARCHAR(50) DEFAULT 'consumer' CHECK (face IN ('consumer', 'partner', 'internal')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    profile JSONB DEFAULT '{}',
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant ON public.users(tenant_id);
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_face ON public.users(face);

-- API Keys table
CREATE TABLE IF NOT EXISTS public.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    key_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    permissions JSONB DEFAULT '[]',
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_api_keys_tenant ON public.api_keys(tenant_id);
CREATE INDEX idx_api_keys_hash ON public.api_keys(key_hash);

-- Audit log table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE SET NULL,
    user_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    metadata JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant ON public.audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_entity ON public.audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON public.audit_logs(created_at DESC);

-- Agent registry table
CREATE TABLE IF NOT EXISTS public.agent_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    engine VARCHAR(50) NOT NULL CHECK (engine IN ('outcome', 'rights_trust', 'risk_security', 'market_capital', 'cross')),
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('assistant', 'operator', 'ambassador')),
    faces VARCHAR(50)[] NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'disabled', 'deprecated')),
    config JSONB DEFAULT '{}',
    version VARCHAR(20) DEFAULT '1.0.0',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_registry_engine ON public.agent_registry(engine);
CREATE INDEX idx_agent_registry_faces ON public.agent_registry USING GIN(faces);

-- ============================================================================
-- CREDITX COMPLIANCE MODULE TABLES
-- ============================================================================

-- Compliance documents
CREATE TABLE IF NOT EXISTS public.compliance_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'approved', 'rejected', 'expired')),
    sanctions_status VARCHAR(50) DEFAULT 'pending' CHECK (sanctions_status IN ('pending', 'clear', 'flagged', 'blocked')),
    compliance_score INTEGER CHECK (compliance_score >= 0 AND compliance_score <= 100),
    payload JSONB NOT NULL,
    kyc_document_url TEXT,
    reviewed_by UUID REFERENCES public.users(id),
    reviewed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_docs_tenant ON public.compliance_documents(tenant_id);
CREATE INDEX idx_compliance_docs_customer ON public.compliance_documents(customer_id);
CREATE INDEX idx_compliance_docs_status ON public.compliance_documents(status);
CREATE INDEX idx_compliance_docs_sanctions ON public.compliance_documents(sanctions_status);

-- Compliance transactions
CREATE TABLE IF NOT EXISTS public.compliance_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    document_id UUID REFERENCES public.compliance_documents(id) ON DELETE CASCADE,
    transaction_date TIMESTAMPTZ NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    counterparty VARCHAR(255),
    sanctions_status VARCHAR(50) DEFAULT 'pending',
    compliance_score INTEGER,
    risk_flags JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_tx_tenant ON public.compliance_transactions(tenant_id);
CREATE INDEX idx_compliance_tx_document ON public.compliance_transactions(document_id);
CREATE INDEX idx_compliance_tx_date ON public.compliance_transactions(transaction_date DESC);

-- ============================================================================
-- GLOBAL AI ALERT MODULE TABLES
-- ============================================================================

-- Threat alerts
CREATE TABLE IF NOT EXISTS public.threat_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive')),
    source VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    affected_entities JSONB DEFAULT '[]',
    indicators JSONB DEFAULT '{}',
    remediation_steps JSONB DEFAULT '[]',
    assigned_to UUID REFERENCES public.users(id),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_threat_alerts_tenant ON public.threat_alerts(tenant_id);
CREATE INDEX idx_threat_alerts_severity ON public.threat_alerts(severity);
CREATE INDEX idx_threat_alerts_status ON public.threat_alerts(status);
CREATE INDEX idx_threat_alerts_created ON public.threat_alerts(created_at DESC);

-- Threat intelligence feeds
CREATE TABLE IF NOT EXISTS public.threat_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feed_source VARCHAR(100) NOT NULL,
    indicator_type VARCHAR(50) NOT NULL,
    indicator_value TEXT NOT NULL,
    threat_type VARCHAR(100),
    confidence INTEGER CHECK (confidence >= 0 AND confidence <= 100),
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_threat_intel_indicator ON public.threat_intelligence(indicator_type, indicator_value);
CREATE INDEX idx_threat_intel_source ON public.threat_intelligence(feed_source);

-- ============================================================================
-- GUARDIAN AI ENDPOINT SECURITY TABLES
-- ============================================================================

-- Protected endpoints
CREATE TABLE IF NOT EXISTS public.guardian_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    device_id VARCHAR(255) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    hostname VARCHAR(255),
    os_type VARCHAR(50),
    os_version VARCHAR(50),
    agent_version VARCHAR(20),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'compromised', 'quarantined')),
    last_seen TIMESTAMPTZ,
    last_scan TIMESTAMPTZ,
    security_score INTEGER CHECK (security_score >= 0 AND security_score <= 100),
    policies JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tenant_id, device_id)
);

CREATE INDEX idx_guardian_endpoints_tenant ON public.guardian_endpoints(tenant_id);
CREATE INDEX idx_guardian_endpoints_status ON public.guardian_endpoints(status);

-- Security incidents
CREATE TABLE IF NOT EXISTS public.guardian_incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    endpoint_id UUID REFERENCES public.guardian_endpoints(id) ON DELETE CASCADE,
    incident_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'detected',
    details JSONB NOT NULL,
    remediation_actions JSONB DEFAULT '[]',
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_guardian_incidents_endpoint ON public.guardian_incidents(endpoint_id);
CREATE INDEX idx_guardian_incidents_severity ON public.guardian_incidents(severity);

-- ============================================================================
-- 91 APPS AUTOMATION TABLES
-- ============================================================================

-- Workflows
CREATE TABLE IF NOT EXISTS public.automation_workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL,
    trigger_config JSONB NOT NULL,
    steps JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'disabled')),
    last_run TIMESTAMPTZ,
    run_count INTEGER DEFAULT 0,
    created_by UUID REFERENCES public.users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_automation_workflows_tenant ON public.automation_workflows(tenant_id);
CREATE INDEX idx_automation_workflows_status ON public.automation_workflows(status);

-- Workflow executions
CREATE TABLE IF NOT EXISTS public.automation_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID REFERENCES public.automation_workflows(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed', 'cancelled')),
    trigger_data JSONB,
    step_results JSONB DEFAULT '[]',
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_automation_executions_workflow ON public.automation_executions(workflow_id);
CREATE INDEX idx_automation_executions_status ON public.automation_executions(status);

-- ============================================================================
-- STOLEN/LOST PHONES TABLES
-- ============================================================================

-- Registered devices
CREATE TABLE IF NOT EXISTS public.registered_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES public.tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    imei VARCHAR(20) NOT NULL,
    device_model VARCHAR(100),
    carrier VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'lost', 'stolen', 'recovered', 'deactivated')),
    last_known_location JSONB,
    last_seen TIMESTAMPTZ,
    reported_at TIMESTAMPTZ,
    recovered_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_registered_devices_imei ON public.registered_devices(imei);
CREATE INDEX idx_registered_devices_status ON public.registered_devices(status);
CREATE INDEX idx_registered_devices_user ON public.registered_devices(user_id);

-- Device reports
CREATE TABLE IF NOT EXISTS public.device_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id UUID REFERENCES public.registered_devices(id) ON DELETE CASCADE,
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN ('lost', 'stolen', 'found', 'sighting')),
    location JSONB,
    description TEXT,
    police_report_number VARCHAR(100),
    reported_by UUID REFERENCES public.users(id),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_device_reports_device ON public.device_reports(device_id);
CREATE INDEX idx_device_reports_type ON public.device_reports(report_type);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'updated_at' 
        AND table_schema = 'public'
    LOOP
        EXECUTE format('
            DROP TRIGGER IF EXISTS update_%I_updated_at ON public.%I;
            CREATE TRIGGER update_%I_updated_at
            BEFORE UPDATE ON public.%I
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        ', t, t, t, t);
    END LOOP;
END $$;

-- ============================================================================
-- DEFAULT DATA
-- ============================================================================

-- Insert default tenant
INSERT INTO public.tenants (id, name, slug, schema_name, status)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Default Tenant',
    'default',
    'tenant_default',
    'active'
) ON CONFLICT (slug) DO NOTHING;

-- Insert core agents into registry
INSERT INTO public.agent_registry (agent_id, name, engine, agent_type, faces, risk_level, status) VALUES
    ('outcome.plan_generation.v1', 'Plan Generation Agent', 'outcome', 'ambassador', ARRAY['consumer'], 'high', 'active'),
    ('outcome.outcome_evaluation.v1', 'Outcome Evaluation Agent', 'outcome', 'operator', ARRAY['internal'], 'low', 'active'),
    ('outcome.campaign_tuning.v1', 'Campaign Tuning Agent', 'outcome', 'operator', ARRAY['internal'], 'medium', 'active'),
    ('outcome.referral_impact.v1', 'Referral Impact Agent', 'outcome', 'operator', ARRAY['internal', 'partner'], 'low', 'active'),
    ('rights_trust.consent_scope.v1', 'Consent & Scope Assistant', 'rights_trust', 'assistant', ARRAY['consumer', 'partner'], 'high', 'active'),
    ('rights_trust.rights_request.v1', 'Rights Request Orchestrator', 'rights_trust', 'ambassador', ARRAY['consumer', 'internal'], 'high', 'active'),
    ('rights_trust.dispute_advocacy.v1', 'Dispute & Advocacy Agent', 'rights_trust', 'ambassador', ARRAY['consumer', 'internal'], 'high', 'active'),
    ('rights_trust.fairness_analysis.v1', 'Fairness Analysis Agent', 'rights_trust', 'operator', ARRAY['internal'], 'medium', 'active'),
    ('rights_trust.audit_compliance.v1', 'Audit & Compliance Reporting Agent', 'rights_trust', 'operator', ARRAY['internal'], 'medium', 'active'),
    ('risk_security.alert_aggregator.v1', 'Security Alert Aggregator', 'risk_security', 'operator', ARRAY['internal'], 'medium', 'active'),
    ('risk_security.remediation.v1', 'Security Remediation Agent', 'risk_security', 'ambassador', ARRAY['consumer'], 'high', 'active'),
    ('risk_security.risk_integration.v1', 'Risk Integration Agent', 'risk_security', 'operator', ARRAY['internal'], 'low', 'active'),
    ('risk_security.threat_intel.v1', 'Threat Intelligence Agent', 'risk_security', 'operator', ARRAY['internal'], 'low', 'active'),
    ('market_capital.ingestion_mapping.v1', 'Ingestion Mapping Agent', 'market_capital', 'operator', ARRAY['internal'], 'medium', 'active'),
    ('market_capital.underwriting.v1', 'Underwriting Decision Agent', 'market_capital', 'ambassador', ARRAY['internal', 'partner'], 'high', 'active'),
    ('market_capital.qc_review.v1', 'QC Review Scheduler Agent', 'market_capital', 'operator', ARRAY['internal'], 'medium', 'active'),
    ('market_capital.packaging.v1', 'Packaging Optimization Agent', 'market_capital', 'operator', ARRAY['internal'], 'high', 'active'),
    ('market_capital.portfolio_risk.v1', 'Portfolio Risk Monitor Agent', 'market_capital', 'operator', ARRAY['internal'], 'medium', 'active'),
    ('cross.explainer.v1', 'Explainer Agent', 'cross', 'assistant', ARRAY['consumer', 'partner', 'internal'], 'low', 'active'),
    ('cross.notification.v1', 'Notification Agent', 'cross', 'operator', ARRAY['consumer', 'partner', 'internal'], 'low', 'active')
ON CONFLICT (agent_id) DO NOTHING;
