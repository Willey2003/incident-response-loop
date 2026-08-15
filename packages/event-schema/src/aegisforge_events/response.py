"""
Response orchestration models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class ResponseActionType(str, Enum):
    """Types of response actions."""
    QUARANTINE_WORKLOAD = "quarantine_workload"          # NetworkPolicy deny-all
    SCALE_DEPLOYMENT = "scale_deployment"                # Scale to zero
    REVOKE_SERVICE_ACCOUNT = "revoke_service_account"    # Remove SA binding
    CREATE_INCIDENT_TICKET = "create_incident_ticket"    # External ticketing
    BLOCK_NETWORK_TRAFFIC = "block_network_traffic"      # NetworkPolicy allow/deny
    ISOLATE_NAMESPACE = "isolate_namespace"              # Namespace-wide isolation
    CAPTURE_MEMORY_DUMP = "capture_memory_dump"          # Forensic capture
    CAPTURE_DISK_IMAGE = "capture_disk_image"            # Forensic capture
    REVOKE_TOKEN = "revoke_token"                        # Revoke API token
    DISABLE_USER = "disable_user"                        # Disable user account
    ROTATE_CREDENTIALS = "rotate_credentials"            # Rotate secrets
    APPLY_NETWORK_POLICY = "apply_network_policy"        # Custom NetworkPolicy
    PATCH_WORKLOAD = "patch_workload"                    # Patch deployment/daemonset


class ResponseStatus(str, Enum):
    """Response action lifecycle status."""
    PENDING = "pending"
    DRY_RUN = "dry_run"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    EXPIRED = "expired"


class ApprovalStatus(str, Enum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ResponseAction(BaseModel):
    """Response action with approval workflow."""
    model_config = ConfigDict(extra="allow")
    
    action_id: UUID = Field(default_factory=uuid4)
    incident_id: Optional[str] = None
    alert_id: Optional[str] = None
    
    # Action details
    action_type: ResponseActionType
    target_resource: Dict[str, any]  # Resource identifier
    parameters: Dict[str, any] = Field(default_factory=dict)
    
    # Execution control
    dry_run: bool = True
    require_approval: bool = True
    allowlist_check: bool = True
    
    # Status tracking
    status: ResponseStatus = ResponseStatus.PENDING
    requested_by: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Approval workflow
    approval_id: Optional[UUID] = None
    approver: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Execution
    execution_started_at: Optional[datetime] = None
    execution_completed_at: Optional[datetime] = None
    execution_result: Optional[Dict[str, any]] = None
    execution_error: Optional[str] = None
    
    # Dry-run results
    dry_run_result: Optional[Dict[str, any]] = None
    dry_run_completed_at: Optional[datetime] = None
    
    # Rollback
    rollback_plan: Dict[str, any] = Field(default_factory=dict)
    rollback_result: Optional[Dict[str, any]] = None
    rolled_back_at: Optional[datetime] = None
    rolled_back_by: Optional[str] = None
    rollback_reason: Optional[str] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    timeout_seconds: int = 300
    
    # Retry and circuit breaker
    retry_count: int = 0
    max_retries: int = 3
    circuit_breaker_tripped: bool = False
    
    # Idempotency
    idempotency_key: Optional[str] = None
    
    # Namespace restriction
    namespace: str = "aegisforge-lab"
    allowed_namespaces: List[str] = Field(default_factory=lambda: ["aegisforge-lab"])
    
    # Audit
    audit_log_id: Optional[str] = None


class Approval(BaseModel):
    """Approval request for response actions."""
    model_config = ConfigDict(extra="allow")
    
    approval_id: UUID = Field(default_factory=uuid4)
    action_id: UUID
    
    # Request details
    requested_by: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    action_type: str
    target_resource: Dict[str, any]
    dry_run_result: Optional[Dict[str, any]] = None
    rollback_plan: Dict[str, any] = Field(default_factory=dict)
    
    # Approval details
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: Optional[str] = None
    decided_at: Optional[datetime] = None
    decision_reason: Optional[str] = None
    
    # Expiration
    expires_at: datetime
    expired: bool = False
    
    # Notifications
    notified_approvers: List[str] = Field(default_factory=list)
    notification_sent_at: Optional[datetime] = None
    
    # Audit
    audit_log_id: Optional[str] = None


class ResponsePlaybook(BaseModel):
    """Pre-defined response playbook."""
    model_config = ConfigDict(extra="allow")
    
    playbook_id: str
    name: str
    description: str
    version: str
    
    # Trigger conditions
    trigger_conditions: Dict[str, any] = Field(default_factory=dict)
    severity_threshold: List[str] = Field(default_factory=lambda: ["critical", "high"])
    mitre_techniques: List[str] = Field(default_factory=list)
    
    # Actions sequence
    actions: List[Dict[str, any]] = Field(default_factory=list)
    
    # Approval requirements
    requires_approval: bool = True
    approvers: List[str] = Field(default_factory=list)
    min_approvers: int = 1
    
    # Safety
    dry_run_first: bool = True
    max_concurrent: int = 1
    timeout_seconds: int = 300
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True


class ResponseAuditLog(BaseModel):
    """Audit log for response actions."""
    model_config = ConfigDict(extra="allow")
    
    audit_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Actor
    actor: str
    actor_type: str  # user, system, api
    actor_ip: Optional[str] = None
    
    # Action
    action: str
    action_type: str
    
    # Resource
    resource_type: str
    resource_id: str
    namespace: str
    
    # Outcome
    outcome: str  # success, failure, partial
    details: Dict[str, any] = Field(default_factory=dict)
    
    # Context
    incident_id: Optional[str] = None
    alert_id: Optional[str] = None
    action_id: Optional[str] = None
    approval_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Timing
    duration_ms: Optional[int] = None
    
    # Error
    error: Optional[str] = None