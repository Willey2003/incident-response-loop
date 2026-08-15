"""
Incident routes for AegisForge API Gateway.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, require_analyst, require_incident_commander
from ..database import get_db

router = APIRouter()


class IncidentListResponse(BaseModel):
    incident_id: str
    title: str
    description: str
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


class IncidentDetailResponse(BaseModel):
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    phase: str
    mitre_techniques: List[str] = []
    mitre_tactics: List[str] = []
    alert_ids: List[str] = []
    alert_count: int
    affected_asset_ids: List[str] = []
    affected_namespaces: List[str] = []
    affected_pods: List[str] = []
    affected_nodes: List[str] = []
    affected_services: List[str] = []
    commander: Optional[str]
    assignees: List[str] = []
    team: Optional[str]
    created_at: datetime
    updated_at: datetime
    detected_at: Optional[datetime]
    contained_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    mttr_seconds: Optional[int]
    mttr_detection_seconds: Optional[int]
    mttr_containment_seconds: Optional[int]
    evidence_ids: List[str] = []
    evidence_count: int
    response_action_ids: List[str] = []
    response_actions_count: int
    successful_actions: int
    failed_actions: int
    ai_summary: Optional[str]
    ai_root_cause: Optional[str]
    ai_impact_assessment: Optional[str]
    ai_lessons_learned: Optional[str]
    report_generated: bool
    report_url: Optional[str]
    report_generated_at: Optional[datetime]
    closure_reason: Optional[str]
    lessons_learned: Optional[str]
    preventive_measures: List[str] = []
    tags: List[str] = []
    labels: Dict[str, str] = {}


class IncidentCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    severity: str = Field(..., pattern="^(info|low|medium|high|critical)$")
    alert_ids: List[str] = Field(default_factory=list)
    affected_asset_ids: List[str] = Field(default_factory=list)
    affected_namespaces: List[str] = Field(default_factory=list)
    affected_pods: List[str] = Field(default_factory=list)
    affected_nodes: List[str] = Field(default_factory=list)
    affected_services: List[str] = Field(default_factory=list)
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)


class IncidentUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    phase: Optional[str] = None
    commander: Optional[str] = None
    assignees: Optional[List[str]] = None
    team: Optional[str] = None
    tags: Optional[List[str]] = None
    labels: Optional[Dict[str, str]] = None


class IncidentListResponseWrapper(BaseModel):
    incidents: List[IncidentListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


router = APIRouter()


@router.get("", response_model=IncidentListResponseWrapper)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    phase: Optional[str] = Query(None),
    commander: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """List incidents with filtering and pagination."""
    query = """
        SELECT incident_id, title, description, severity, status, phase,
               alert_count, affected_asset_count, created_at, updated_at,
               commander, mttr_seconds, mitre_techniques
        FROM detection.incidents
        WHERE 1=1
    """
    params = {}
    
    if severity:
        query += " AND severity = :severity"
        params["severity"] = severity
    if status:
        query += " AND status = :status"
        params["status"] = status
    if phase:
        query += " AND phase = :phase"
        params["phase"] = phase
    if commander:
        query += " AND commander = :commander"
        params["commander"] = commander
    if namespace:
        query += " AND :namespace = ANY(affected_namespaces)"
        params["namespace"] = namespace
    if start_date:
        query += " AND created_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND created_at <= :end_date"
        params["end_date"] = end_date
    
    # Count total
    count_query = f"SELECT COUNT(*) FROM ({query}) AS subq"
    total = await db.execute(select(func.count()).select_from(text(count_query)), params)
    total = total.scalar() or 0
    
    # Pagination
    offset = (page - 1) * page_size
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset
    
    result = await db.execute(text(query), params)
    incidents = result.fetchall()
    
    incidents_list = [
        IncidentListResponse(
            incident_id=str(row.incident_id),
            title=row.title,
            description=row.description,
            severity=row.severity,
            status=row.status,
            phase=row.phase,
            alert_count=row.alert_count,
            affected_asset_count=row.affected_asset_count,
            created_at=row.created_at,
            updated_at=row.updated_at,
            commander=row.commander,
            mttr_seconds=row.mttr_seconds,
            mitre_techniques=row.mitre_techniques or [],
        )
        for row in incidents
    ]
    
    return IncidentListResponseWrapper(
        incidents=incidents_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident(
    incident_id: UUID,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed incident information."""
    query = text("SELECT * FROM detection.incidents WHERE incident_id = :incident_id")
    result = await db.execute(text("SELECT * FROM detection.incidents WHERE incident_id = :incident_id"), {"incident_id": str(incident_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident_dict = dict(row._mapping)
    for key, value in incident_dict.items():
        if isinstance(value, UUID):
            incident_dict[key] = str(value)
    
    return IncidentDetailResponse(**incident_dict)


@router.post("", response_model=IncidentDetailResponse, status_code=201)
async def create_incident(
    request: IncidentCreateRequest,
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Create a new incident."""
    from uuid import uuid4
    
    incident_id = uuid4()
    now = datetime.utcnow()
    
    alert_count = len(request.alert_ids)
    affected_asset_count = len(request.affected_asset_ids)
    
    result = await db.execute(text("""
        INSERT INTO detection.incidents (
            incident_id, title, description, severity, status, phase,
            alert_ids, alert_count, affected_asset_ids, affected_asset_count,
            affected_namespaces, affected_pods, affected_nodes, affected_services,
            mitre_techniques, mitre_tactics, commander, assignees, team,
            created_at, updated_at, tags, labels
        ) VALUES (
            :incident_id, :title, :description, :severity, 'open', 'detection',
            :alert_ids, :alert_count, :affected_asset_ids, :affected_asset_count,
            :affected_namespaces, :affected_pods, :affected_nodes, :affected_services,
            :mitre_techniques, :mitre_tactics, :commander, :assignees, :team,
            :created_at, :updated_at, :tags, :labels
        ) RETURNING *
    """), {
        "incident_id": str(incident_id),
        "title": request.title,
        "description": request.description,
        "severity": request.severity,
        "alert_ids": request.alert_ids,
        "alert_count": alert_count,
        "affected_asset_ids": request.affected_asset_ids,
        "affected_asset_count": affected_asset_count,
        "affected_namespaces": request.affected_namespaces,
        "affected_pods": request.affected_pods,
        "affected_nodes": request.affected_nodes,
        "affected_services": request.affected_services,
        "mitre_techniques": request.mitre_techniques,
        "mitre_tactics": request.mitre_tactics,
        "commander": str(current_user.id),
        "assignees": [],
        "team": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "tags": request.tags,
        "labels": request.labels,
    })
    
    row = result.fetchone()
    await db.commit()
    
    incident_dict = dict(row._mapping)
    for key, value in incident_dict.items():
        if isinstance(value, UUID):
            incident_dict[key] = str(value)
    
    return IncidentDetailResponse(**incident_dict)


@router.patch("/{incident_id}")
async def update_incident(
    incident_id: UUID,
    request: "IncidentUpdateRequest",
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Update an incident."""
    from sqlalchemy import text
    
    result = await db.execute(text("SELECT incident_id FROM detection.incidents WHERE incident_id = :id"), {"id": str(incident_id)})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Incident not found")
    
    updates = []
    params = {"incident_id": str(incident_id), "updated_at": datetime.utcnow()}
    
    if request.title is not None:
        updates.append("title = :title")
        params["title"] = request.title
    if request.description is not None:
        updates.append("description = :description")
        params["description"] = request.description
    if request.severity is not None:
        updates.append("severity = :severity")
        params["severity"] = request.severity
    if request.status is not None:
        updates.append("status = :status")
        params["status"] = request.status
        if request.status in ["resolved", "closed"]:
            params["resolved_at"] = datetime.utcnow()
            updates.append("resolved_at = :resolved_at")
            params["resolved_at"] = datetime.utcnow()
    if request.phase is not None:
        updates.append("phase = :phase")
        params["phase"] = request.phase
        if request.phase == "containment":
            params["contained_at"] = datetime.utcnow()
            updates.append("contained_at = :contained_at")
    if request.commander is not None:
        updates.append("commander = :commander")
        params["commander"] = request.commander
    if request.assignees is not None:
        updates.append("assignees = :assignees")
        params["assignees"] = request.assignees
    if request.team is not None:
        updates.append("team = :team")
        params["team"] = request.team
    if request.tags is not None:
        updates.append("tags = :tags")
        params["tags"] = request.tags
    if request.labels is not None:
        updates.append("labels = :labels")
        params["labels"] = request.labels
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    updates.append("updated_at = :updated_at")
    
    query = f"UPDATE detection.incidents SET {', '.join(updates)} WHERE incident_id = :incident_id"
    await db.execute(text(query), params)
    await db.commit()
    
    return {"message": "Incident updated", "incident_id": str(incident_id)}


@router.post("/{incident_id}/close")
async def close_incident(
    incident_id: UUID,
    reason: str = Query(..., min_length=10),
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Close an incident."""
    from sqlalchemy import text
    
    result = await db.execute(text("SELECT incident_id FROM detection.incidents WHERE incident_id = :id"), {"id": str(incident_id)})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Incident not found")
    
    await db.execute(text("""
        UPDATE detection.incidents 
        SET status = 'closed', phase = 'post_incident', closed_at = NOW(), 
            closure_reason = :reason, updated_at = NOW()
        WHERE incident_id = :incident_id
    """), {
        "incident_id": str(incident_id),
        "reason": reason,
    })
    
    await db.commit()
    
    return {"message": "Incident closed", "incident_id": str(incident_id)}


@router.get("/{incident_id}/timeline")
async def get_incident_timeline(
    incident_id: UUID,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Get incident timeline events."""
    query = text("""
        SELECT * FROM detection.timeline_events 
        WHERE incident_id = :incident_id 
        ORDER BY event_time ASC
    """)
    result = await db.execute(text("SELECT * FROM detection.timeline_events WHERE incident_id = :incident_id ORDER BY event_time ASC"), {"incident_id": str(incident_id)})
    events = result.fetchall()
    
    return [dict(row._mapping) for row in events]


@router.post("/{incident_id}/timeline")
async def add_timeline_event(
    incident_id: UUID,
    event_type: str,
    title: str,
    description: str,
    actor: Optional[str] = None,
    phase: Optional[str] = None,
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Add a timeline event to an incident."""
    from uuid import uuid4
    
    result = await db.execute(text("""
        INSERT INTO detection.timeline_events (
            event_id, incident_id, event_time, event_type, title, description, actor, phase, source
        ) VALUES (
            :event_id, :incident_id, NOW(), :event_type, :title, :description, :actor, :phase, 'manual'
        ) RETURNING *
    """), {
        "event_id": str(uuid4()),
        "incident_id": str(incident_id),
        "event_type": event_type,
        "title": title,
        "description": description,
        "actor": str(current_user.id),
        "phase": phase,
    })
    
    await db.commit()
    return {"message": "Timeline event added"}


# Import for type hints
from typing import List, Optional, Dict