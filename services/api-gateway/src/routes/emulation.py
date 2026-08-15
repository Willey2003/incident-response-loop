"""
Emulation controller routes for AegisForge API Gateway.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, require_admin, require_incident_commander, require_emulation_control
from ..database import get_db

router = APIRouter()


class EmulationScenarioListResponse(BaseModel):
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


class EmulationScenarioDetailResponse(BaseModel):
    scenario_id: str
    name: str
    description: str
    version: str
    mitre_techniques: List[str] = []
    mitre_tactics: List[str] = []
    severity: str
    duration_seconds: int
    config: Dict = {}
    simulators: List[str] = []
    namespace: str
    allowed_namespaces: List[str] = []
    require_approval: bool
    max_concurrent_runs: int
    created_by: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
    enabled: bool


class EmulationRunListResponse(BaseModel):
    run_id: str
    scenario_id: str
    scenario_name: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    events_generated: int
    events_sent: int
    events_failed: int
    started_by: Optional[str]
    progress_percent: float


class EmulationRunDetailResponse(BaseModel):
    run_id: str
    scenario_id: str
    scenario_name: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    config_override: Dict = {}
    target_namespace: str
    events_generated: int
    events_sent: int
    events_failed: int
    errors: List[Dict] = []
    last_error: Optional[str]
    status_message: Optional[str]
    progress_percent: float
    created_at: datetime
    updated_at: datetime
    started_by: Optional[str]


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


class EmulationRunRequest(BaseModel):
    scenario_id: str
    config_override: Dict = Field(default_factory=dict)
    target_namespace: str = "aegisforge-lab"
    duration_override: Optional[int] = Field(None, ge=60, le=3600)


class EmulationScenarioListResponseWrapper(BaseModel):
    scenarios: List[EmulationScenarioListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EmulationRunListResponseWrapper(BaseModel):
    runs: List[EmulationRunListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


router = APIRouter()


@router.get("/scenarios", response_model=EmulationScenarioListResponseWrapper)
async def list_scenarios(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    enabled: Optional[bool] = Query(None),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """List emulation scenarios."""
    query = """
        SELECT scenario_id, name, description, version, severity, mitre_techniques, 
               mitre_tactics, duration_seconds, enabled, created_at, updated_at
        FROM emulation.scenarios
        WHERE 1=1
    """
    params = {}
    
    if enabled is not None:
        query += " AND enabled = :enabled"
        params["enabled"] = enabled
    if severity:
        query += " AND severity = :severity"
        params["severity"] = severity
    
    count_query = f"SELECT COUNT(*) FROM ({query}) AS subq"
    total = await db.execute(select(func.count()).select_from(text(count_query)), params)
    total = total.scalar() or 0
    
    offset = (page - 1) * page_size
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset
    
    result = await db.execute(text(query), params)
    scenarios = result.fetchall()
    
    scenarios_list = [
        EmulationScenarioListResponse(
            scenario_id=row.scenario_id,
            name=row.name,
            description=row.description,
            version=row.version,
            severity=row.severity,
            mitre_techniques=row.mitre_techniques or [],
            mitre_tactics=row.mitre_tactics or [],
            duration_seconds=row.duration_seconds,
            enabled=row.enabled,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in scenarios
    ]
    
    return EmulationScenarioListResponseWrapper(
        scenarios=scenarios_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/scenarios/{scenario_id}", response_model=EmulationScenarioDetailResponse)
async def get_scenario(
    scenario_id: str,
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get emulation scenario details."""
    result = await db.execute(text("SELECT * FROM emulation.scenarios WHERE scenario_id = :id"), {"id": scenario_id})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    scenario_dict = dict(row._mapping)
    for key, value in scenario_dict.items():
        if isinstance(value, UUID):
            scenario_dict[key] = str(value)
    
    return EmulationScenarioDetailResponse(**scenario_dict)


@router.post("/scenarios", response_model=EmulationScenarioDetailResponse, status_code=201)
async def create_scenario(
    request: "EmulationScenarioCreateRequest",
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new emulation scenario."""
    from uuid import uuid4
    
    scenario_id = str(uuid4())
    now = datetime.utcnow()
    
    result = await db.execute(text("""
        INSERT INTO emulation.scenarios (
            scenario_id, name, description, version, mitre_techniques, mitre_tactics,
            severity, duration_seconds, config, simulators, namespace, allowed_namespaces,
            require_approval, max_concurrent_runs, created_by, created_at, updated_at, tags, enabled
        ) VALUES (
            :scenario_id, :name, :description, :version, :mitre_techniques, :mitre_tactics,
            :severity, :duration_seconds, :config, :simulators, :namespace, :allowed_namespaces,
            :require_approval, :max_concurrent_runs, :created_by, :created_at, :updated_at, :tags, true
        ) RETURNING *
    """), {
        "scenario_id": scenario_id,
        "name": request.name,
        "description": request.description,
        "version": request.version,
        "mitre_techniques": request.mitre_techniques,
        "mitre_tactics": request.mitre_tactics,
        "severity": request.severity,
        "duration_seconds": request.duration_seconds,
        "config": request.config,
        "simulators": request.simulators,
        "namespace": request.namespace,
        "allowed_namespaces": request.allowed_namespaces,
        "require_approval": request.require_approval,
        "max_concurrent_runs": request.max_concurrent_runs,
        "created_by": str(current_user.id),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "tags": request.tags,
    })
    
    row = result.fetchone()
    await db.commit()
    
    scenario_dict = dict(row._mapping)
    for key, value in scenario_dict.items():
        if isinstance(value, UUID):
            scenario_dict[key] = str(value)
    
    return EmulationScenarioDetailResponse(**scenario_dict)


@router.post("/runs", response_model=dict, status_code=201)
async def start_emulation_run(
    request: "EmulationRunRequest",
    current_user = Depends(require_emulation_control),
    db: AsyncSession = Depends(get_db),
):
    """Start an emulation run."""
    from uuid import uuid4
    
    # Verify scenario exists
    result = await db.execute(text("SELECT * FROM emulation.scenarios WHERE scenario_id = :id AND enabled = true"), {"id": request.scenario_id})
    scenario = result.fetchone()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found or disabled")
    
    # Check approval requirement
    if scenario.require_approval:
        # In real implementation, check for approval
        pass
    
    run_id = str(uuid4())
    now = datetime.utcnow()
    
    result = await db.execute(text("""
        INSERT INTO emulation.runs (
            run_id, scenario_id, status, config_override, target_namespace,
            created_at, updated_at, started_by
        ) VALUES (
            :run_id, :scenario_id, :status, :config_override, :target_namespace,
            :created_at, :updated_at, :started_by
        ) RETURNING run_id
    """), {
        "run_id": run_id,
        "scenario_id": request.scenario_id,
        "status": "pending",
        "config_override": request.config_override,
        "target_namespace": request.target_namespace,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "started_by": str(current_user.id),
    })
    
    await db.commit()
    
    return {"run_id": run_id, "status": "pending", "message": "Emulation run started"}


@router.get("/runs", response_model=dict)
async def list_runs(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    scenario_id: Optional[str] = None,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """List emulation runs."""
    query = """
        SELECT r.run_id, r.scenario_id, s.name as scenario_name, r.status,
               r.started_at, r.completed_at, r.duration_seconds,
               r.events_generated, r.events_sent, r.events_failed,
               r.started_by, r.progress_percent
        FROM emulation.runs r
        JOIN emulation.scenarios s ON r.scenario_id = s.scenario_id
        WHERE 1=1
    """
    params = {}
    
    if status:
        query += " AND r.status = :status"
        params["status"] = status
    if scenario_id:
        query += " AND r.scenario_id = :scenario_id"
        params["scenario_id"] = scenario_id
    
    count_query = f"SELECT COUNT(*) FROM ({query}) AS subq"
    total = await db.execute(select(func.count()).select_from(text(count_query)), params)
    total = total.scalar() or 0
    
    offset = (page - 1) * page_size
    query += " ORDER BY r.created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset
    
    result = await db.execute(text(query), params)
    runs = result.fetchall()
    
    runs_list = [
        EmulationRunListResponse(
            run_id=str(row.run_id),
            scenario_id=str(row.scenario_id),
            scenario_name=row.scenario_name,
            status=row.status,
            started_at=row.started_at,
            completed_at=row.completed_at,
            duration_seconds=row.duration_seconds,
            events_generated=row.events_generated,
            events_sent=row.events_sent,
            events_failed=row.events_failed,
            started_by=row.started_by,
            progress_percent=row.progress_percent,
        )
        for row in runs
    ]
    
    return {
        "runs": runs_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/runs/{run_id}", response_model=dict)
async def get_run(
    run_id: UUID,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Get emulation run details."""
    result = await db.execute(text("""
        SELECT r.*, s.name as scenario_name
        FROM emulation.runs r
        JOIN emulation.scenarios s ON r.scenario_id = s.scenario_id
        WHERE r.run_id = :run_id
    """), {"run_id": str(run_id)})
    
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    
    run_dict = dict(row._mapping)
    for key, value in run_dict.items():
        if isinstance(value, UUID):
            run_dict[key] = str(value)
    
    return run_dict


@router.post("/runs/{run_id}/cancel")
async def cancel_run(
    run_id: UUID,
    reason: str = Query(..., min_length=1),
    current_user = Depends(require_emulation_control),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a running emulation."""
    result = await db.execute(text("SELECT * FROM emulation.runs WHERE run_id = :id"), {"id": str(run_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if row.status not in ["pending", "running", "paused"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel run with status: {row.status}")
    
    await db.execute(text("""
        UPDATE emulation.runs 
        SET status = 'cancelled', completed_at = NOW(), status_message = :reason
        WHERE run_id = :run_id
    """), {"run_id": str(run_id), "reason": reason})
    
    await db.commit()
    
    return {"message": "Run cancelled", "run_id": str(run_id)}


@router.get("/templates", response_model=List[Dict])
async def list_templates(
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """List built-in scenario templates."""
    # Return built-in templates from the emulation module
    return [
        {
            "template_id": "auth-brute-force",
            "name": "Authentication Brute Force",
            "description": "Simulates repeated failed login attempts from single source",
            "category": "authentication",
            "mitre_techniques": ["T1110.001", "T1110.003"],
            "mitre_tactics": ["TA0006"],
            "severity": "high",
        },
        {
            "template_id": "dns-tunneling",
            "name": "DNS Tunneling Exfiltration",
            "description": "Simulates DNS tunneling for data exfiltration",
            "category": "dns",
            "mitre_techniques": ["T1048.003", "T1572"],
            "mitre_tactics": ["TA0010", "TA0011"],
            "severity": "high",
        },
        {
            "template_id": "traffic-beaconing",
            "name": "C2 Beaconing Pattern",
            "description": "Simulates regular C2 beaconing traffic",
            "category": "traffic",
            "mitre_techniques": ["T1071.001", "T1573.001"],
            "mitre_tactics": ["TA0011"],
            "severity": "high",
        },
        {
            "template_id": "traffic-port-scan",
            "name": "Internal Port Scan",
            "description": "Simulates internal network reconnaissance",
            "category": "traffic",
            "mitre_techniques": ["T1046", "T1590.005"],
            "mitre_tactics": ["TA0007"],
            "severity": "medium",
        },
        {
            "template_id": "workload-privilege-escalation",
            "name": "Container Privilege Escalation",
            "description": "Simulates container escape and privilege escalation attempts",
            "category": "workload",
            "mitre_techniques": ["T1611", "T1610", "T1609"],
            "mitre_tactics": ["TA0004"],
            "severity": "critical",
        },
        {
            "template_id": "crypto-mining",
            "name": "Cryptocurrency Mining",
            "description": "Simulates cryptominer process execution",
            "category": "workload",
            "mitre_techniques": ["T1496"],
            "mitre_tactics": ["TA0005"],
            "severity": "high",
        },
        {
            "template_id": "data-exfiltration",
            "name": "Data Exfiltration Simulation",
            "description": "Simulates large data transfer to external destination",
            "category": "traffic",
            "mitre_techniques": ["T1041", "T1048.003"],
            "mitre_tactics": ["TA0010"],
            "severity": "critical",
        },
    ]


from typing import List, Optional, Dict