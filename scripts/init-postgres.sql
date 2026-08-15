-- AegisForge PostgreSQL Initialization Script
-- Creates databases, users, and initial schema

-- Create databases
CREATE DATABASE aegisforge;
CREATE DATABASE keycloak;

-- Create users
CREATE USER aegisforge WITH PASSWORD 'changeme_dev_only';
CREATE USER keycloak WITH PASSWORD 'keycloak';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE aegisforge TO aegisforge;
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;

-- Connect to aegisforge database
\c aegisforge;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS aegisforge;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS detection;
CREATE SCHEMA IF NOT EXISTS response;
CREATE SCHEMA IF NOT EXISTS emulation;
CREATE SCHEMA IF NOT EXISTS assets;

-- Set search path
ALTER DATABASE aegisforge SET search_path TO aegisforge, audit, detection, response, emulation, assets, public;

-- Grant schema permissions
GRANT ALL ON SCHEMA aegisforge TO aegisforge;
GRANT ALL ON SCHEMA audit TO aegisforge;
GRANT ALL ON SCHEMA detection TO aegisforge;
GRANT ALL ON SCHEMA response TO aegisforge;
GRANT ALL ON SCHEMA emulation TO aegisforge;
GRANT ALL ON SCHEMA assets TO aegisforge;

-- Create tables (Alembic will manage these, but we create base tables here)

-- Assets table
CREATE TABLE IF NOT EXISTS assets.assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- workload, service, node, namespace, pod
    namespace VARCHAR(255),
    labels JSONB DEFAULT '{}',
    annotations JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_assets_namespace ON assets.assets(namespace);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets.assets(type);
CREATE INDEX IF NOT EXISTS idx_assets_labels ON assets.assets USING GIN(labels);

-- Detection rules table
CREATE TABLE IF NOT EXISTS detection.rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_yaml TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low, info
    enabled BOOLEAN DEFAULT true,
    mitre_techniques TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    version INTEGER DEFAULT 1,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_detection_rules_enabled ON detection.rules(enabled);
CREATE INDEX IF NOT EXISTS idx_detection_rules_severity ON detection.rules(severity);

-- Alerts table
CREATE TABLE IF NOT EXISTS detection.alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_id UUID REFERENCES detection.rules(id),
    event_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    evidence JSONB DEFAULT '{}',
    affected_asset_id UUID REFERENCES assets.assets(id),
    mitre_techniques TEXT[] DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'open', -- open, investigating, acknowledged, closed
    assignee VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_detection_alerts_status ON detection.alerts(status);
CREATE INDEX IF NOT EXISTS idx_detection_alerts_severity ON detection.alerts(severity);
CREATE INDEX IF NOT EXISTS idx_detection_alerts_created_at ON detection.alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_detection_alerts_rule_id ON detection.alerts(rule_id);

-- Incidents table
CREATE TABLE IF NOT EXISTS detection.incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, investigating, contained, resolved, closed
    alert_ids UUID[] DEFAULT '{}',
    assignee VARCHAR(255),
    commander VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    mttr_seconds INTEGER
);

CREATE INDEX IF NOT EXISTS idx_detection_incidents_status ON detection.incidents(status);
CREATE INDEX IF NOT EXISTS idx_detection_incidents_severity ON detection.incidents(severity);
CREATE INDEX IF NOT EXISTS idx_detection_incidents_created_at ON detection.incidents(created_at DESC);

-- Cases table (for case management)
CREATE TABLE IF NOT EXISTS detection.cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES detection.incidents(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    owner VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_detection_cases_incident_id ON detection.cases(incident_id);
CREATE INDEX IF NOT EXISTS idx_detection_cases_status ON detection.cases(status);

-- Evidence table
CREATE TABLE IF NOT EXISTS detection.evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES detection.incidents(id),
    alert_id UUID REFERENCES detection.alerts(id),
    type VARCHAR(50) NOT NULL, -- log, metric, trace, artifact, screenshot
    source VARCHAR(255) NOT NULL,
    minio_bucket VARCHAR(255),
    minio_object VARCHAR(500),
    hash_sha256 VARCHAR(64),
    size_bytes BIGINT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_detection_evidence_incident_id ON detection.evidence(incident_id);
CREATE INDEX IF NOT EXISTS idx_detection_evidence_alert_id ON detection.evidence(alert_id);

-- Timeline events
CREATE TABLE IF NOT EXISTS detection.timeline_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES detection.incidents(id),
    event_time TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    actor VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_detection_timeline_incident_id ON detection.timeline_events(incident_id);
CREATE INDEX IF NOT EXISTS idx_detection_timeline_event_time ON detection.timeline_events(event_time);

-- Response actions
CREATE TABLE IF NOT EXISTS response.actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES detection.incidents(id),
    alert_id UUID REFERENCES detection.alerts(id),
    action_type VARCHAR(50) NOT NULL, -- quarantine, scale_down, revoke_sa, create_ticket
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, executing, completed, failed, rolled_back
    dry_run BOOLEAN DEFAULT true,
    requested_by VARCHAR(255) NOT NULL,
    approved_by VARCHAR(255),
    approval_id UUID,
    target_resource JSONB NOT NULL,
    parameters JSONB DEFAULT '{}',
    dry_run_result JSONB,
    execution_result JSONB,
    rollback_plan JSONB,
    rollback_result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_response_actions_incident_id ON response.actions(incident_id);
CREATE INDEX IF NOT EXISTS idx_response_actions_status ON response.actions(status);

-- Approvals table
CREATE TABLE IF NOT EXISTS response.approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_id UUID REFERENCES response.actions(id),
    requester VARCHAR(255) NOT NULL,
    approver VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, expired
    reason TEXT,
    dry_run_result JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    decided_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_response_approvals_action_id ON response.approvals(action_id);
CREATE INDEX IF NOT EXISTS idx_response_approvals_status ON response.approvals(status);

-- Audit logs
CREATE TABLE IF NOT EXISTS audit.logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(100) NOT NULL,
    actor VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    namespace VARCHAR(255),
    outcome VARCHAR(20) NOT NULL, -- success, failure, partial
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    correlation_id UUID
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit.logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor ON audit.logs(actor);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit.logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation_id ON audit.logs(correlation_id);

-- Emulation scenarios
CREATE TABLE IF NOT EXISTS emulation.scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    mitre_techniques TEXT[] DEFAULT '{}',
    severity VARCHAR(20) NOT NULL,
    duration_seconds INTEGER DEFAULT 300,
    enabled BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}',
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_emulation_scenarios_enabled ON emulation.scenarios(enabled);

-- Emulation runs
CREATE TABLE IF NOT EXISTS emulation.runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_id UUID REFERENCES emulation.scenarios(id),
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    started_by VARCHAR(255),
    approved_by VARCHAR(255),
    approval_id UUID,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    events_generated INTEGER DEFAULT 0,
    events_sent INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_emulation_runs_status ON emulation.runs(status);
CREATE INDEX IF NOT EXISTS idx_emulation_runs_scenario_id ON emulation.runs(scenario_id);

-- AI knowledge base
CREATE TABLE IF NOT EXISTS assets.knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(50) NOT NULL, -- runbook, policy, documentation, incident, alert
    source_id VARCHAR(255),
    tags TEXT[] DEFAULT '{}',
    embedding_id VARCHAR(255), -- Qdrant point ID
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_base_source_type ON assets.knowledge_base(source_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_tags ON assets.knowledge_base USING GIN(tags);

-- Policies table
CREATE TABLE IF NOT EXISTS assets.policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    policy_type VARCHAR(50) NOT NULL, -- network, admission, runtime, compliance
    policy_yaml TEXT NOT NULL,
    namespace VARCHAR(255),
    enabled BOOLEAN DEFAULT true,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_policies_enabled ON assets.policies(enabled);
CREATE INDEX IF NOT EXISTS idx_policies_type ON assets.policies(policy_type);

-- Runbooks table
CREATE TABLE IF NOT EXISTS assets.runbooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    trigger_conditions JSONB DEFAULT '{}',
    steps JSONB NOT NULL,
    severity VARCHAR(20) NOT NULL,
    mitre_techniques TEXT[] DEFAULT '{}',
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_runbooks_severity ON assets.runbooks(severity);

-- Grant all privileges on all tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aegisforge TO aegisforge;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO aegisforge;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA detection TO aegisforge;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA response TO aegisforge;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA emulation TO aegisforge;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA assets TO aegisforge;

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA aegisforge TO aegisforge;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO aegisforge;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA detection TO aegisforge;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA response TO aegisforge;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA emulation TO aegisforge;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA assets TO aegisforge;

-- Default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA aegisforge GRANT ALL ON TABLES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT ALL ON TABLES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA detection GRANT ALL ON TABLES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA response GRANT ALL ON TABLES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA emulation GRANT ALL ON TABLES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA assets GRANT ALL ON TABLES TO aegisforge;

ALTER DEFAULT PRIVILEGES IN SCHEMA aegisforge GRANT USAGE, SELECT ON SEQUENCES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT USAGE, SELECT ON SEQUENCES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA detection GRANT USAGE, SELECT ON SEQUENCES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA response GRANT USAGE, SELECT ON SEQUENCES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA emulation GRANT USAGE, SELECT ON SEQUENCES TO aegisforge;
ALTER DEFAULT PRIVILEGES IN SCHEMA assets GRANT USAGE, SELECT ON SEQUENCES TO aegisforge;