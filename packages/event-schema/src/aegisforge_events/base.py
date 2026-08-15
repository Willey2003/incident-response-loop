"""
Base event models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class EventSeverity(str, Enum):
    """Event severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class EventMetadata(BaseModel):
    """Metadata for all events."""
    model_config = ConfigDict(extra="allow")
    
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Source component/service name")
    source_type: str = Field(..., description="Type of source: simulator, collector, detector, etc.")
    correlation_id: Optional[UUID] = None
    causation_id: Optional[UUID] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)


class BaseEvent(BaseModel):
    """Base class for all AegisForge events."""
    model_config = ConfigDict(extra="allow")
    
    metadata: EventMetadata
    severity: EventSeverity = EventSeverity.INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode="json")
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseEvent":
        """Create event from dictionary."""
        return cls.model_validate(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "BaseEvent":
        """Create event from JSON string."""
        return cls.model_validate_json(json_str)