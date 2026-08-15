"""
Response playbook models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator


class PlaybookTriggerType(str, Enum):
    """Types of playbook triggers."""
    ALERT_MATCH = "alert_match"
    INCIDENT_CREATED = "incident_created"
    INCIDENT_SEVERITY_CHANGE = "incident_severity_change"
    INCIDENT_STATUS_CHANGE = "incident_status_change"
    CORRELATION_MATCH = "correlation_match"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"


class PlaybookStepType(str, Enum):
    """Types of playbook steps."""
    EXECUTE_ACTION = "execute_action"
    WAIT = "wait"
    CONDITION = "condition"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    ENRICHMENT = "enrichment"
    CUSTOM = "custom"


class ApprovalType(str, Enum):
    """Types of approval requirements."""
    SINGLE = "single"  # One approver
    MAJORITY = "majority"  # Majority of approvers
    UNANIMOUS = "unanimous"  # All approvers
    ROLE_BASED = "role_based"  # Specific role required


class PlaybookTrigger(BaseModel):
    """Trigger condition for playbook execution."""
    model_config = ConfigDict(extra="allow")
    
    trigger_type: PlaybookTriggerType
    conditions: Dict[str, any] = Field(default_factory=dict)
    severity_threshold: List[str] = Field(default_factory=lambda: ["high", "critical"])
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    alert_names: List[str] = Field(default_factory=list)
    alert_tags: List[str] = Field(default_factory=list)
    namespaces: List[str] = Field(default_factory=list)
    asset_types: List[str] = Field(default_factory=list)
    
    # Scheduled triggers
    cron_expression: Optional[str] = None
    timezone: str = "UTC"
    
    # Threshold triggers
    metric_name: Optional[str] = None
    threshold_value: Optional[float] = None
    threshold_operator: str = "gt"  # gt, gte, lt, lte, eq
    evaluation_window_seconds: int = 300
    
    # Rate limiting
    cooldown_seconds: int = 300
    max_executions_per_hour: int = 10


class PlaybookStep(BaseModel):
    """Single step in a playbook."""
    model_config = ConfigDict(extra="allow")
    
    step_id: str
    name: str
    description: str
    step_type: PlaybookStepType
    
    # Execution control
    order: int = 0
    depends_on: List[str] = Field(default_factory=list)  # step_ids this depends on
    parallel_group: Optional[str] = None
    
    # Action step
    action_type: Optional[str] = None
    action_parameters: Dict[str, any] = Field(default_factory=dict)
    action_timeout_seconds: int = 300
    action_retry_count: int = 3
    action_retry_delay_seconds: int = 10
    
    # Conditional execution
    condition: Optional[str] = None  # Jinja2 expression
    condition_true_step: Optional[str] = None
    condition_false_step: Optional[str] = None
    
    # Wait step
    wait_seconds: Optional[int] = None
    wait_until: Optional[str] = None  # timestamp or condition
    
    # Parallel execution
    parallel_steps: List[str] = Field(default_factory=list)  # step_ids to run in parallel
    
    # Approval step
    approval_required: bool = False
    approval_type: ApprovalType = ApprovalType.SINGLE
    approvers: List[str] = Field(default_factory=list)
    approval_timeout_seconds: int = 3600
    approval_message: Optional[str] = None
    
    # Notification step
    notification_channels: List[str] = Field(default_factory=list)
    notification_template: Optional[str] = None
    notification_recipients: List[str] = Field(default_factory=list)
    
    # Retry and error handling
    retry_count: int = 3
    retry_delay_seconds: int = 10
    retry_exponential_backoff: bool = True
    max_retry_delay_seconds: int = 300
    continue_on_failure: bool = False
    failure_step: Optional[str] = None
    
    # Timeout
    timeout_seconds: int = 300
    
    # Dry-run support
    dry_run_supported: bool = True
    
    # Rollback
    rollback_step: Optional[str] = None
    rollback_on_failure: bool = True
    
    # Circuit breaker
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 300


class ResponsePlaybook(BaseModel):
    """Complete response playbook definition."""
    model_config = ConfigDict(extra="allow")
    
    # Identification
    playbook_id: str
    name: str
    description: str
    version: str
    
    # Triggers
    triggers: List[PlaybookTrigger] = Field(default_factory=list)
    
    # Steps
    steps: List[PlaybookStep] = Field(default_factory=list)
    
    # Configuration
    enabled: bool = True
    priority: int = 0
    
    # Safety
    dry_run_first: bool = True
    max_concurrent_executions: int = 1
    max_concurrent_per_incident: int = 1
    execution_timeout_seconds: int = 3600
    
    # Approval requirements
    requires_approval: bool = True
    default_approvers: List[str] = Field(default_factory=list)
    min_approvers: int = 1
    approval_timeout_seconds: int = 3600
    
    # Safety constraints
    namespace: str = "aegisforge-lab"
    allowed_namespaces: List[str] = Field(default_factory=lambda: ["aegisforge-lab"])
    require_allowlist: bool = True
    max_concurrent_actions: int = 5
    
    # Circuit breaker
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 300
    
    # Retry policy
    global_retry_count: int = 3
    global_retry_delay_seconds: int = 10
    
    # Dry-run and rollback
    dry_run_first: bool = True
    auto_rollback_on_failure: bool = True
    rollback_timeout_seconds: int = 300
    
    # Metadata
    author: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    tags_mitre: List[str] = Field(default_factory=list)
    
    # Version control
    version: str = "1.0.0"
    changelog: List[Dict[str, str]] = Field(default_factory=list)
    
    # Testing
    test_cases: List[Dict[str, any]] = Field(default_factory=list)
    
    # Deprecation
    deprecated: bool = False
    deprecated_at: Optional[datetime] = None
    replacement_playbook_id: Optional[str] = None
    
    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: List[PlaybookStep]) -> List[PlaybookStep]:
        # Check for circular dependencies
        step_ids = {s.step_id for s in v}
        for step in v:
            for dep in step.depends_on:
                if dep not in step_ids:
                    raise ValueError(f"Step {step.step_id} depends on unknown step {dep}")
        return v
    
    def get_step(self, step_id: str) -> Optional[PlaybookStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_executable_steps(self) -> List[PlaybookStep]:
        """Get steps that are ready to execute (no unmet dependencies)."""
        executable = []
        for step in self.steps:
            if all(self.get_step(dep) and self.get_step(dep).status == "completed" for dep in step.depends_on):
                executable.append(step)
        return executable
    
    def to_yaml(self) -> str:
        import yaml
        return yaml.dump(self.model_dump(mode="json"), sort_keys=False)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> "ResponsePlaybook":
        import yaml
        data = yaml.safe_load(yaml_str)
        return cls.model_validate(data)


class PlaybookExecution(BaseModel):
    """Runtime execution of a playbook."""
    model_config = ConfigDict(extra="allow")
    
    execution_id: UUID
    playbook_id: str
    playbook_version: str
    
    # Trigger context
    trigger_type: str
    trigger_data: Dict[str, any] = Field(default_factory=dict)
    incident_id: Optional[str] = None
    alert_id: Optional[str] = None
    
    # Execution state
    status: str = "pending"  # pending, running, paused, completed, failed, cancelled
    current_step: Optional[str] = None
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    
    # Execution context
    variables: Dict[str, any] = Field(default_factory=dict)
    incident_id: Optional[str] = None
    alert_ids: List[str] = Field(default_factory=list)
    
    # Approvals
    pending_approvals: List[str] = Field(default_factory=list)
    completed_approvals: List[str] = Field(default_factory=list)
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Execution details
    step_results: Dict[str, Dict[str, any]] = Field(default_factory=dict)
    error: Optional[str] = None
    error_step: Optional[str] = None
    
    # Dry-run
    dry_run: bool = False
    
    # Circuit breaker
    circuit_breaker_tripped: bool = False
    circuit_breaker_tripped_at: Optional[datetime] = None
    
    # Progress
    progress_percent: float = 0.0
    current_step_index: int = 0
    total_steps: int = 0