export interface User {
  id: string
  username: string
  email: string
  roles: string[]
  permissions: string[]
}

export interface Alert {
  alert_id: string
  rule_id: string
  rule_name: string
  title: string
  description: string
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  mitre_techniques: string[]
  mitre_tactics: string[]
  affected_asset_ids: string[]
  affected_namespaces: string[]
  affected_pods: string[]
  affected_nodes: string[]
  evidence: AlertEvidence[]
  correlated_alert_ids: string[]
  correlation_rule_id: string
  event_count: number
  status: 'open' | 'investigating' | 'acknowledged' | 'false_positive' | 'closed' | 'suppressed'
  assignee: string | null
  acknowledged_at: string | null
  acknowledged_by: string | null
  closed_at: string | null
  closed_by: string | null
  close_reason: string | null
  first_seen: string
  last_seen: string
  mitre_technique_details: Record<string, any>
  recommended_actions: string[]
  recommended_runbooks: string[]
  ai_summary: string | null
  ai_triage: any
  ai_confidence: number | null
}

export interface AlertEvidence {
  evidence_id: string
  evidence_type: string
  source: string
  description: string
  data: Record<string, any>
  timestamp: string
  hash_sha256: string | null
  size_bytes: number | null
  minio_bucket: string | null
  minio_object: string | null
}

export interface Incident {
  incident_id: string
  title: string
  description: string
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'investigating' | 'contained' | 'eradicated' | 'recovered' | 'resolved' | 'closed'
  phase: 'preparation' | 'detection' | 'analysis' | 'containment' | 'eradication' | 'recovery' | 'post_incident'
  mitre_techniques: string[]
  mitre_tactics: string[]
  alert_ids: string[]
  alert_count: number
  affected_asset_ids: string[]
  affected_namespaces: string[]
  affected_pods: string[]
  affected_nodes: string[]
  affected_services: string[]
  commander: string | null
  assignees: string[]
  team: string | null
  created_at: string
  updated_at: string
  detected_at: string | null
  contained_at: string | null
  resolved_at: string | null
  closed_at: string | null
  mttr_seconds: number | null
  mttr_detection_seconds: number | null
  mttr_containment_seconds: number | null
  evidence_ids: string[]
  evidence_count: number
  response_action_ids: string[]
  response_actions_count: number
  successful_actions: number
  failed_actions: number
  ai_summary: string | null
  ai_root_cause: string | null
  ai_impact_assessment: string | null
  ai_lessons_learned: string | null
  report_generated: boolean
  report_url: string | null
  report_generated_at: string | null
  closure_reason: string | null
  lessons_learned: string | null
  preventive_measures: string[]
  tags: string[]
  labels: Record<string, string>
}

export interface ResponseAction {
  action_id: string
  incident_id: string | null
  alert_id: string | null
  action_type: string
  status: string
  dry_run: boolean
  require_approval: boolean
  requested_by: string
  requested_at: string
  approver: string | null
  approved_at: string | null
  rejection_reason: string | null
  target_resource: Record<string, any>
  parameters: Record<string, any>
  dry_run_result: Record<string, any> | null
  execution_result: Record<string, any> | null
  execution_error: string | null
  rollback_plan: Record<string, any>
  rollback_result: Record<string, any> | null
  rolled_back_at: string | null
  rolled_back_by: string | null
  rollback_reason: string | null
  created_at: string
  updated_at: string
  expires_at: string | null
  timeout_seconds: number
  retry_count: number
  max_retries: number
  circuit_breaker_tripped: boolean
  namespace: string
  allowed_namespaces: string[]
  audit_log_id: string | null
}

export interface EmulationScenario {
  scenario_id: string
  name: string
  description: string
  version: string
  mitre_techniques: string[]
  mitre_tactics: string[]
  severity: string
  duration_seconds: number
  config: Record<string, any>
  simulators: string[]
  namespace: string
  allowed_namespaces: string[]
  require_approval: boolean
  max_concurrent_runs: number
  created_by: string
  created_at: string
  updated_at: string
  tags: string[]
  enabled: boolean
}

export interface EmulationRun {
  run_id: string
  scenario_id: string
  scenario_name: string
  status: string
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
  events_generated: number
  events_sent: number
  events_failed: number
  started_by: string | null
  progress_percent: number
}

export interface AIAnalysisRequest {
  request_id: string
  analysis_type: string
  incident_id?: string
  alert_id?: string
  query?: string
  max_tokens: number
  temperature: number
  include_citations: boolean
}

export interface AIAnalysisResponse {
  request_id: string
  response_id: string
  summary: string
  details: string
  recommendations: string[]
  confidence: 'high' | 'medium' | 'low' | 'insufficient_evidence'
  confidence_score: number | null
  citations: Array<{
    citation_id: string
    source_type: string
    source_id: string
    title: string
    excerpt: string
    timestamp: string
    relevance_score: number
  }>
  evidence_used: string[]
  structured_data: Record<string, any>
  mitre_techniques: string[]
  mitre_tactics: string[]
  model_used: string
  processing_time_ms: number
  tokens_input: number
  tokens_output: number
  tokens_total: number
  redacted: boolean
  redaction_count: number
  insufficient_evidence: boolean
  safety_warnings: string[]
}

export interface RetrievalResult {
  document_id: string
  content: string
  metadata: Record<string, any>
  score: float
  citation: {
    source_type: string
    source_id: string
    title: string
    excerpt: string
    timestamp: string
  }
}

export interface EmulationScenarioTemplate {
  template_id: string
  name: string
  description: string
  category: string
  mitre_techniques: string[]
  mitre_tactics: string[]
  severity: string
  duration_seconds: number
  config: Record<string, any>
}

export interface HealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy'
  service: string
  version: string
  timestamp: string
  checks: Record<string, {
    status: 'healthy' | 'degraded' | 'unhealthy'
    message?: string
  }>
}