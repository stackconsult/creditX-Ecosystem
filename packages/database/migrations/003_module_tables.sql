-- ============================================================================
-- CreditX Ecosystem - Module-Specific Database Tables
-- Complete schema for all 5 modules
-- ============================================================================

-- ============================================================================
-- MODULE 1: CREDITX COMPLIANCE
-- ============================================================================

CREATE TABLE IF NOT EXISTS compliance_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    transaction_date TIMESTAMPTZ NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    counterparty VARCHAR(255),
    counterparty_country VARCHAR(2),
    transaction_type VARCHAR(50),
    sanctions_status VARCHAR(50) DEFAULT 'pending',
    compliance_score INTEGER,
    risk_factors JSONB DEFAULT '[]',
    kyc_document_url TEXT,
    audit_log_id UUID,
    reviewed_by UUID,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_compliance_tx_tenant ON compliance_transactions(tenant_id);
CREATE INDEX idx_compliance_tx_status ON compliance_transactions(sanctions_status);
CREATE INDEX idx_compliance_tx_date ON compliance_transactions(transaction_date);

CREATE TABLE IF NOT EXISTS sanctions_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES compliance_transactions(id),
    tenant_id INTEGER,
    check_type VARCHAR(50),
    provider VARCHAR(50),
    query_data JSONB,
    response_data JSONB,
    match_score DECIMAL(5,2),
    match_details JSONB,
    status VARCHAR(20),
    checked_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kyc_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    entity_type VARCHAR(20),
    entity_id UUID,
    document_type VARCHAR(50),
    title VARCHAR(255),
    file_url TEXT,
    file_hash VARCHAR(64),
    extracted_data JSONB,
    verification_status VARCHAR(20) DEFAULT 'pending',
    verified_by UUID,
    verified_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS regulatory_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    report_type VARCHAR(50),
    period_start DATE,
    period_end DATE,
    status VARCHAR(20) DEFAULT 'draft',
    data JSONB,
    file_url TEXT,
    submitted_at TIMESTAMPTZ,
    submitted_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MODULE 2: 91 APPS BUSINESS AUTOMATION
-- ============================================================================

CREATE TABLE IF NOT EXISTS automation_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    external_id VARCHAR(255),
    source VARCHAR(50),
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    title VARCHAR(255),
    status VARCHAR(50) DEFAULT 'new',
    score INTEGER,
    score_factors JSONB,
    assigned_to UUID,
    last_activity_at TIMESTAMPTZ,
    converted_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_leads_tenant ON automation_leads(tenant_id);
CREATE INDEX idx_leads_status ON automation_leads(status);
CREATE INDEX idx_leads_score ON automation_leads(score);

CREATE TABLE IF NOT EXISTS automation_workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50),
    trigger_type VARCHAR(50),
    trigger_config JSONB,
    steps JSONB NOT NULL,
    conditions JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'draft',
    version INTEGER DEFAULT 1,
    execution_count INTEGER DEFAULT 0,
    last_executed_at TIMESTAMPTZ,
    created_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES automation_workflows(id),
    tenant_id INTEGER,
    trigger_event JSONB,
    input_data JSONB,
    output_data JSONB,
    steps_completed INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    error_step INTEGER,
    duration_ms INTEGER,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    po_number VARCHAR(50) UNIQUE,
    supplier_id UUID,
    supplier_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'draft',
    line_items JSONB NOT NULL,
    subtotal DECIMAL(15,2),
    tax DECIMAL(15,2),
    total DECIMAL(15,2),
    currency VARCHAR(3) DEFAULT 'USD',
    requested_by UUID,
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MODULE 3: GLOBAL AI ALERT (THREAT DETECTION)
-- ============================================================================

CREATE TABLE IF NOT EXISTS threat_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    source_ip INET,
    dest_ip INET,
    source_port INTEGER,
    dest_port INTEGER,
    protocol VARCHAR(10),
    dns_query TEXT,
    packet_metadata JSONB,
    threat_type VARCHAR(50),
    threat_score INTEGER,
    severity VARCHAR(20),
    indicators JSONB DEFAULT '[]',
    detection_method VARCHAR(50),
    model_version VARCHAR(20),
    status VARCHAR(20) DEFAULT 'new',
    resolved_at TIMESTAMPTZ,
    resolution VARCHAR(100),
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_threat_tenant ON threat_events(tenant_id);
CREATE INDEX idx_threat_severity ON threat_events(severity);
CREATE INDEX idx_threat_status ON threat_events(status);
CREATE INDEX idx_threat_detected ON threat_events(detected_at);

CREATE TABLE IF NOT EXISTS network_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    device_id VARCHAR(255) UNIQUE,
    device_type VARCHAR(50),
    mac_address MACADDR,
    ip_address INET,
    hostname VARCHAR(255),
    os_type VARCHAR(50),
    os_version VARCHAR(100),
    agent_version VARCHAR(20),
    baseline_profile JSONB,
    baseline_established_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS threat_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type VARCHAR(50),
    indicator_value TEXT NOT NULL,
    threat_type VARCHAR(50),
    severity VARCHAR(20),
    confidence DECIMAL(3,2),
    source VARCHAR(100),
    first_seen_at TIMESTAMPTZ,
    last_seen_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ioc_type ON threat_indicators(indicator_type);
CREATE INDEX idx_ioc_value ON threat_indicators(indicator_value);

-- ============================================================================
-- MODULE 4: GUARDIAN AI (ENDPOINT SECURITY)
-- ============================================================================

CREATE TABLE IF NOT EXISTS endpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    device_id VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(50),
    os_type VARCHAR(50),
    os_version VARCHAR(100),
    agent_version VARCHAR(20),
    agent_status VARCHAR(20) DEFAULT 'active',
    last_checkin_at TIMESTAMPTZ,
    ip_address INET,
    mac_address MACADDR,
    user_id UUID,
    baseline_established BOOLEAN DEFAULT FALSE,
    baseline_data JSONB,
    policy_id UUID,
    status VARCHAR(20) DEFAULT 'online',
    isolated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_endpoints_tenant ON endpoints(tenant_id);
CREATE INDEX idx_endpoints_status ON endpoints(status);

CREATE TABLE IF NOT EXISTS endpoint_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_id UUID REFERENCES endpoints(id),
    tenant_id INTEGER,
    event_type VARCHAR(50),
    event_subtype VARCHAR(50),
    event_data JSONB NOT NULL,
    process_name VARCHAR(255),
    process_path TEXT,
    process_hash VARCHAR(64),
    user_context VARCHAR(255),
    anomaly_score INTEGER,
    flagged BOOLEAN DEFAULT FALSE,
    investigated BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_endpoint_events_endpoint ON endpoint_events(endpoint_id);
CREATE INDEX idx_endpoint_events_type ON endpoint_events(event_type);
CREATE INDEX idx_endpoint_events_flagged ON endpoint_events(flagged) WHERE flagged = TRUE;

CREATE TABLE IF NOT EXISTS endpoint_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_id UUID REFERENCES endpoints(id),
    tenant_id INTEGER,
    incident_type VARCHAR(50),
    severity VARCHAR(20),
    title VARCHAR(255),
    description TEXT,
    indicators JSONB DEFAULT '[]',
    affected_files JSONB DEFAULT '[]',
    affected_processes JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'open',
    containment_status VARCHAR(20),
    isolated_at TIMESTAMPTZ,
    investigated_by UUID,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    playbook_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- MODULE 5: STOLEN/LOST PHONES (DEVICE RECOVERY)
-- ============================================================================

CREATE TABLE IF NOT EXISTS tracked_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    device_id VARCHAR(255) UNIQUE NOT NULL,
    owner_user_id UUID,
    device_type VARCHAR(50),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    os_type VARCHAR(50),
    os_version VARCHAR(100),
    imei VARCHAR(20),
    serial_number VARCHAR(100),
    phone_number VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    last_location GEOGRAPHY(POINT, 4326),
    last_location_at TIMESTAMPTZ,
    last_location_accuracy INTEGER,
    stolen_at TIMESTAMPTZ,
    recovered_at TIMESTAMPTZ,
    wiped_at TIMESTAMPTZ,
    insurance_claim_id VARCHAR(100),
    mdm_enrolled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tracked_devices_tenant ON tracked_devices(tenant_id);
CREATE INDEX idx_tracked_devices_status ON tracked_devices(status);
CREATE INDEX idx_tracked_devices_owner ON tracked_devices(owner_user_id);

CREATE TABLE IF NOT EXISTS device_location_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES tracked_devices(id),
    tenant_id INTEGER,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    accuracy_meters INTEGER,
    altitude DECIMAL(10,2),
    speed DECIMAL(10,2),
    heading DECIMAL(5,2),
    location_method VARCHAR(50),
    battery_level INTEGER,
    network_type VARCHAR(20),
    cell_info JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_location_device ON device_location_history(device_id);
CREATE INDEX idx_location_timestamp ON device_location_history(timestamp);

CREATE TABLE IF NOT EXISTS recovery_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES tracked_devices(id),
    tenant_id INTEGER,
    case_number VARCHAR(50) UNIQUE,
    status VARCHAR(50) DEFAULT 'reported',
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    reported_by UUID,
    incident_description TEXT,
    police_report_number VARCHAR(100),
    police_report_filed BOOLEAN DEFAULT FALSE,
    authorities_notified BOOLEAN DEFAULT FALSE,
    authorities_notified_at TIMESTAMPTZ,
    insurance_claim_filed BOOLEAN DEFAULT FALSE,
    insurance_claim_number VARCHAR(100),
    recovery_actions JSONB DEFAULT '[]',
    chain_of_custody JSONB DEFAULT '[]',
    recovered_at TIMESTAMPTZ,
    recovered_by VARCHAR(255),
    recovery_location GEOGRAPHY(POINT, 4326),
    closed_at TIMESTAMPTZ,
    closed_reason VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES tracked_devices(id),
    tenant_id INTEGER,
    command_type VARCHAR(50) NOT NULL,
    command_data JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending',
    issued_by UUID,
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ,
    executed_at TIMESTAMPTZ,
    result JSONB,
    error_message TEXT
);

-- ============================================================================
-- SHARED: CONSUMER & OUTCOME TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS consumers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    email VARCHAR(255),
    name VARCHAR(255),
    phone VARCHAR(50),
    date_of_birth DATE,
    ssn_hash VARCHAR(64),
    address JSONB,
    annual_income DECIMAL(15,2),
    employment_status VARCHAR(50),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    last_password_change TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS credit_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID REFERENCES consumers(id),
    tenant_id INTEGER,
    bureau VARCHAR(20),
    score INTEGER,
    score_model VARCHAR(50),
    score_change_30d INTEGER,
    utilization_ratio DECIMAL(5,2),
    total_accounts INTEGER,
    open_accounts INTEGER,
    derogatory_marks INTEGER,
    hard_inquiries_12m INTEGER,
    oldest_account_age_months INTEGER,
    total_balance DECIMAL(15,2),
    is_current BOOLEAN DEFAULT TRUE,
    raw_data JSONB,
    pulled_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS savings_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID REFERENCES consumers(id),
    tenant_id INTEGER,
    plan_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    target_score INTEGER,
    target_date DATE,
    net_advantage_projected DECIMAL(15,2),
    net_advantage_actual DECIMAL(15,2),
    confidence_score DECIMAL(3,2),
    milestones JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES savings_plans(id),
    consumer_id UUID,
    tenant_id INTEGER,
    campaign_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    target VARCHAR(255),
    horizon_days INTEGER,
    progress_pct DECIMAL(5,2) DEFAULT 0,
    duration_days INTEGER,
    net_advantage_achieved DECIMAL(15,2),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS action_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    consumer_id UUID,
    tenant_id INTEGER,
    action_type VARCHAR(50),
    title VARCHAR(255),
    description TEXT,
    effort_level VARCHAR(20),
    impact_level VARCHAR(20),
    automated BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'pending',
    due_date DATE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID REFERENCES consumers(id),
    tenant_id INTEGER,
    creditor_name VARCHAR(255),
    account_number_hash VARCHAR(64),
    type VARCHAR(50),
    original_balance DECIMAL(15,2),
    balance DECIMAL(15,2),
    credit_limit DECIMAL(15,2),
    monthly_payment DECIMAL(15,2),
    interest_rate DECIMAL(5,2),
    status VARCHAR(20) DEFAULT 'active',
    opened_at DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SHARED: DISPUTES & RIGHTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS disputes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID REFERENCES consumers(id),
    tenant_id INTEGER,
    bureau VARCHAR(20),
    dispute_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'draft',
    items_disputed INTEGER DEFAULT 0,
    items_resolved INTEGER DEFAULT 0,
    items_removed INTEGER DEFAULT 0,
    score_impact_projected INTEGER,
    score_impact_actual INTEGER,
    advocacy_letter_id UUID,
    submission_method VARCHAR(50),
    submission_reference VARCHAR(100),
    fcra_compliant BOOLEAN DEFAULT TRUE,
    submitted_at TIMESTAMPTZ,
    response_due_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dispute_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dispute_id UUID REFERENCES disputes(id),
    item_type VARCHAR(50),
    account_name VARCHAR(255),
    reason VARCHAR(255),
    evidence JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'pending',
    resolution VARCHAR(100),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS consent_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID REFERENCES consumers(id),
    tenant_id INTEGER,
    partner_id UUID,
    purpose VARCHAR(255),
    data_types JSONB NOT NULL,
    legal_basis VARCHAR(50),
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    revocation_reason TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rights_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID REFERENCES consumers(id),
    tenant_id INTEGER,
    request_type VARCHAR(50),
    scope JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    verified_at TIMESTAMPTZ,
    processing_started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    result JSONB,
    export_url TEXT,
    audit_trail_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SHARED: SECURITY ALERTS & INCIDENTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID,
    tenant_id INTEGER,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    title VARCHAR(255),
    description TEXT,
    source VARCHAR(100),
    indicators JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'active',
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID,
    resolved_at TIMESTAMPTZ,
    resolution VARCHAR(255),
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS security_incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    consumer_id UUID,
    tenant_id INTEGER,
    incident_type VARCHAR(50),
    severity VARCHAR(20),
    title VARCHAR(255),
    description TEXT,
    affected_assets JSONB DEFAULT '[]',
    status VARCHAR(20) DEFAULT 'open',
    containment_status VARCHAR(20),
    playbook_id UUID,
    assigned_to UUID,
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    contained_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    postmortem_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SHARED: PARTNERS & UNDERWRITING
-- ============================================================================

CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    external_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    partner_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    api_key_hash VARCHAR(64),
    webhook_url TEXT,
    fairness_score INTEGER,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS underwriting_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id INTEGER REFERENCES tenants(id),
    applicant_id UUID,
    partner_id UUID REFERENCES partners(id),
    product_type VARCHAR(50),
    loan_amount DECIMAL(15,2),
    loan_term_months INTEGER,
    purpose VARCHAR(255),
    applicant_data JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS underwriting_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID REFERENCES underwriting_applications(id),
    tenant_id INTEGER,
    decision VARCHAR(20),
    risk_score INTEGER,
    risk_tier VARCHAR(20),
    risk_factors JSONB DEFAULT '[]',
    apr_offered DECIMAL(5,2),
    monthly_payment DECIMAL(15,2),
    conditions JSONB DEFAULT '[]',
    model_version VARCHAR(20),
    human_override BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    decided_by UUID,
    decision_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on all new tables
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT IN ('tenants', 'schema_migrations')
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
    END LOOP;
END $$;
