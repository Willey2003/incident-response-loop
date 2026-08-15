"""
AegisForge Event Schema Package
Shared event definitions for the AegisForge platform.
"""

from .base import BaseEvent, EventMetadata, EventSeverity
from .security_events import (
    SecurityEvent,
    AuthEvent,
    NetworkEvent,
    ProcessEvent,
    FileEvent,
    ContainerEvent,
    KubernetesEvent,
    DNSEvent,
    TrafficEvent,
)
from .alerts import Alert, AlertEvidence, AlertStatus
from .incidents import Incident, IncidentStatus, IncidentSeverity
from .response import ResponseAction, ResponseStatus, Approval, ApprovalStatus
from .emulation import EmulationScenario, EmulationRun, EmulationStatus
from .ai import AIAnalysisRequest, AIAnalysisResponse, Citation, RetrievalResult

__all__ = [
    # Base
    "BaseEvent",
    "EventMetadata",
    "EventSeverity",
    # Security Events
    "SecurityEvent",
    "AuthEvent",
    "NetworkEvent",
    "ProcessEvent",
    "FileEvent",
    "ContainerEvent",
    "KubernetesEvent",
    "DNSEvent",
    "TrafficEvent",
    # Alerts
    "Alert",
    "AlertEvidence",
    "AlertStatus",
    # Incidents
    "Incident",
    "IncidentStatus",
    "IncidentSeverity",
    # Response
    "ResponseAction",
    "ResponseStatus",
    "Approval",
    "ApprovalStatus",
    # Emulation
    "EmulationScenario",
    "EmulationRun",
    "EmulationStatus",
    # AI
    "AIAnalysisRequest",
    "AIAnalysisResponse",
    "Citation",
    "RetrievalResult",
]