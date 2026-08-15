"""
Incident models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

from .base import EventSeverity


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentPhase(str, Enum):
    """Incident response phases."""
    PREPARATION = "preparation"
    DETECTION = "detection"
    ANALYSIS = "analysis"
    CONTAINMENT = "containment"
    ERADICATION = "eradication"
    RECOVERY = "recovery"
    POST_INCIDENT = "post_incident"


class Incident(BaseModel):
    """Security incident with full lifecycle tracking."""
    model_config = ConfigDict(extra="allow")
    
    incident_id: UUID
    title: str
    description: str
    
    # Classification
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    phase: IncidentPhase = IncidentPhase.DETECTION
    
    # MITRE ATT&CK
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    
    # Related alerts
    alert_ids: List[str] = Field(default_factory=list)
    alert_count: int = 0
    
    # Affected assets
    affected_asset_ids: List[str] = Field(default_factory=list)
    affected_namespaces: List[str] = Field(default_factory=list)
    affected_pods: List[str] = Field(default_factory=list)
    affected_nodes: List[str] = Field(default_factory=list)
    affected_services: List[str] = Field(default_factory=list)
    
    # Assignment
    commander: Optional[str] = None
    assignees: List[str] = Field(default_factory=list)
    team: Optional[str] = None
    
    # Timeline
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    detected_at: Optional[datetime] = None
    contained_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Metrics
    mttr_seconds: Optional[int] = None  # Mean time to resolve
    mttr_detection_seconds: Optional[int] = None
    mttr_containment_seconds: Optional[int] = None
    
    # Evidence
    evidence_ids: List[str] = Field(default_factory=list)
    evidence_count: int = 0
    
    # Response actions
    response_action_ids: List[str] = Field(default_factory=list)
    response_actions_count: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    
    # AI enrichment
    ai_summary: Optional[str] = None
    ai_root_cause: Optional[str] = None
    ai_impact_assessment: Optional[str] = None
    ai_lessons_learned: Optional[str] = None
    
    # Reporting
    report_generated: bool = False
    report_url: Optional[str] = None
    report_generated_at: Optional[datetime] = None
    
    # Closure
    closure_reason: Optional[str] = None
    lessons_learned: Optional[str] = None
    preventive_measures: List[str] = Field(default_factory=list)
    
    # Tags and labels
    tags: List[str] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)


class IncidentTimelineEvent(BaseModel):
    """Timeline event for incident tracking."""
    event_id: str
    incident_id: str
    timestamp: datetime
    event_type: str
    title: str
    description: str
    actor: Optional[str] = None
    phase: Optional[IncidentPhase] = None
    data: Dict[str, any] = {}
    source: str
    is_milestone: bool = False


class IncidentSummary(BaseModel):
    """Summary view of incident for listings."""
    incident_id: str
    title: str
    severity: str
    status: str
    phase: str
    alert_count: int
    affected_asset_count: int
    created_at: datetime
    updated_at: datetime
    commander: Optional[str]
    mttr_seconds: Optional[int]
    mitre_techniques: List[str] = []