"""
Emulation scenarios routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..auth import get_current_user, require_admin
from ..config import settings
from ..database import get_db_session

router = APIRouter()


class EmulationScenarioResponse(BaseModel):
    scenario_id: str
    name: str
    description: str
    version: str
    severity: str
    mitre_techniques: List[str] = []
    mitre_tactics: List[str] = []
    duration_seconds: int
    enabled: bool
    created_at: datetime
    updated_at: datetime


class EmulationScenarioCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str
    version: str = "1.0.0"
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    duration_seconds: int = Field(default=300, ge=60, le=3600)
    config: Dict = Field(default_factory=dict)
    simulators: List[str] = Field(default_factory=list)
    namespace: str = "aegisforge-lab"
    allowed_namespaces: List[str] = Field(default_factory=lambda: ["aegisforge-lab"])
    require_approval: bool = True
    max_concurrent_runs: int = 3
    tags: List[str] = Field(default_factory=list)


router = APIRouter()


@router.get("/scenarios", response_model=List[dict])
async def list_scenarios(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    enabled: Optional[bool] = Query(None),
    severity: Optional[str] = Query(None),
    current_user = Depends(require_admin),
):
    """List emulation scenarios."""
    # Return built-in scenarios
    return [
        {
            "scenario_id": "auth-brute-force",
            "name": "Authentication Brute Force",
            "description": "Simulates repeated failed login attempts from single source",
            "version": "1.0.0",
            "severity": "high",
            "mitre_techniques": ["T1110.001", "T1110.003"],
            "mitre_tactics": ["TA0006"],
            "duration_seconds": 300,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "scenario_id": "dns-tunneling",
            "name": "DNS Tunneling Exfiltration",
            "description": "Simulates DNS tunneling for data exfiltration",
            "version": "1.0.0",
            "severity": "high",
            "mitre_techniques": ["T1048.003", "T1572"],
            "mitre_tactics": ["TA0010", "TA0011"],
            "duration_seconds": 300,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "scenario_id": "traffic-beaconing",
            "name": "C2 Beaconing Pattern",
            "description": "Simulates regular C2 beaconing traffic",
            "version": "1.0.0",
            "severity": "high",
            "mitre_techniques": ["T1071.001", "T1573.001"],
            "mitre_tactics": ["TA0011"],
            "duration_seconds": 300,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "scenario_id": "traffic-port-scan",
            "name": "Internal Port Scan",
            "description": "Simulates internal network reconnaissance",
            "version": "1.0.0",
            "severity": "medium",
            "mitre_techniques": ["T1046", "T1590.005"],
            "mitre_tactics": ["TA0007"],
            "duration_seconds": 300,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "scenario_id": "workload-privilege-escalation",
            "name": "Container Privilege Escalation",
            "description": "Simulates container escape and privilege escalation attempts",
            "version": "1.0.0",
            "severity": "critical",
            "mitre_techniques": ["T1611", "T1610", "T1609"],
            "mitre_tactics": ["TA0004"],
            "duration_seconds": 300,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "scenario_id": "crypto-mining",
            "name": "Cryptocurrency Mining",
            "description": "Simulates cryptominer process execution",
            "version": "1.0.0",
            "severity": "high",
            "mitre_techniques": ["T1496"],
            "mitre_tactics": ["TA0005"],
            "duration_seconds": 300,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
        {
            "scenario_id": "data-exfiltration",
            "name": "Data Exfiltration Simulation",
            "description": "Simulates large data transfer to external destination",
            "version": "1.0.0",
            "severity": "critical",
            "mitre_techniques": ["T1041", "T1048.003"],
            "mitre_tactics": ["TA0010"],
            "duration_seconds": 300,
            "enabled": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
    ]


@router.post("/scenarios", status_code=201)
async def create_scenario(
    request: dict,
    current_user = Depends(require_admin),
):
    """Create a new emulation scenario."""
    return {"message": "Scenario creation not implemented in demo", "scenario_id": "new-scenario"}