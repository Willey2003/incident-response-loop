"""
Alert routes for AegisForge API Gateway.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, require_analyst, require_admin, require_alert_manage
from ..database import get_db
from ..config import settings

router = APIRouter()


class AlertListResponse(BaseModel):
    alert_id: str
    rule_id: Optional[str]
    rule_name: Optional[str]
    title: str
    severity: str
    confidence: float
    status: str
    affected_asset_count: int
    first_seen: datetime
    last_seen: datetime
    assignee: Optional[str]
    mitre_techniques: List[str] = []


class AlertDetailResponse(BaseModel):
    alert_id: str
    rule_id: Optional[str]
    rule_name: Optional[str]
    rule_version: Optional[int]
    title: str
    description: str
    severity: str
    confidence: float
    mitre_techniques: List[str] = []
    mitre_tactics: List[str] = []
    affected_asset_ids: List[str] = []
    affected_namespaces: List[str] = []
    affected_pods: List[str] = []
    affected_nodes: List[str] = []
    evidence_count: int
    correlated_alert_ids: List[str] = []
    correlation_rule_id: Optional[str]
    event_count: int
    status: str
    assignee: Optional[str]
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    closed_at: Optional[datetime] = None
    closed_by: Optional[str] = None
    close_reason: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    mitre_technique_details: dict = {}
    recommended_actions: List[str] = []
    recommended_runbooks: List[str] = []
    ai_summary: Optional[str] = None
    ai_triage: Optional[dict] = None
    ai_confidence: Optional[float] = None


class AlertAcknowledgeRequest(BaseModel):
    assignee: Optional[str] = None


class AlertCloseRequest(BaseModel):
    reason: str


class AlertListResponseWrapper(BaseModel):
    alerts: List[AlertListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("", response_model=AlertListResponseWrapper)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    assignee: Optional[str] = Query(None),
    rule_id: Optional[str] = Query(None),
    namespace: Optional[str] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """List alerts with filtering and pagination."""
    # Build query
    query = """
        SELECT alert_id, rule_id, rule_name, title, severity, confidence, 
               status, affected_asset_count, first_seen, last_seen, assignee, mitre_techniques
        FROM detection.alerts
        WHERE 1=1
    """
    params = {}
    
    if severity:
        query += " AND severity = :severity"
        params["severity"] = severity
    if status:
        query += " AND status = :status"
        params["status"] = status
    if assignee:
        query += " AND assignee = :assignee"
        params["assignee"] = assignee
    if rule_id:
        query += " AND rule_id = :rule_id"
        params["rule_id"] = rule_id
    if namespace:
        query += " AND :namespace = ANY(affected_namespaces)"
        params["namespace"] = namespace
    if start_date:
        query += " AND first_seen >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND first_seen <= :end_date"
        params["end_date"] = end_date
    
    # Count total
    count_query = f"SELECT COUNT(*) FROM ({query}) AS subq"
    total = await db.execute(select(func.count()).select_from(text(count_query)), params)
    total = total.scalar() or 0
    
    # Pagination
    offset = (page - 1) * page_size
    query += " ORDER BY first_seen DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset
    
    result = await db.execute(text(query), params)
    alerts = result.fetchall()
    
    alerts_list = [
        AlertListResponse(
            alert_id=str(row.alert_id),
            rule_id=str(row.rule_id) if row.rule_id else None,
            rule_name=row.rule_name,
            title=row.title,
            severity=row.severity,
            confidence=float(row.confidence),
            status=row.status,
            affected_asset_count=row.affected_asset_count,
            first_seen=row.first_seen,
            last_seen=row.last_seen,
            assignee=row.assignee,
            mitre_techniques=row.mitre_techniques or [],
        )
        for row in alerts
    ]
    
    return AlertListResponseWrapper(
        alerts=alerts_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{alert_id}", response_model=AlertDetailResponse)
async def get_alert(
    alert_id: UUID,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed alert information."""
    from sqlalchemy import text
    
    query = text("SELECT * FROM detection.alerts WHERE alert_id = :alert_id")
    result = await db.execute(text("SELECT * FROM detection.alerts WHERE alert_id = :alert_id"), {"alert_id": str(alert_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Convert row to dict
    alert_dict = dict(row._mapping)
    
    # Convert UUIDs to strings
    for key, value in alert_dict.items():
        if isinstance(value, UUID):
            alert_dict[key] = str(value)
    
    return AlertDetailResponse(**alert_dict)


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: UUID,
    request: "AlertAcknowledgeRequest",
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Acknowledge an alert."""
    from sqlalchemy import text
    
    # Check if alert exists
    result = await db.execute(text("SELECT alert_id FROM detection.alerts WHERE alert_id = :id"), {"id": str(alert_id)})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Update alert
    assignee = request.assignee or str(current_user.id)
    await db.execute(text("""
        UPDATE detection.alerts 
        SET status = 'acknowledged', assignee = :assignee, acknowledged_at = NOW(), acknowledged_by = :acknowledged_by
        WHERE alert_id = :alert_id
    """), {
        "alert_id": str(alert_id),
        "assignee": assignee,
        "acknowledged_by": str(current_user.id),
    })
    
    await db.commit()
    
    return {"message": "Alert acknowledged", "alert_id": str(alert_id)}


@router.post("/{alert_id}/close")
async def close_alert(
    alert_id: UUID,
    request: "AlertCloseRequest",
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Close an alert."""
    from sqlalchemy import text
    
    # Check if alert exists
    result = await db.execute(text("SELECT alert_id FROM detection.alerts WHERE alert_id = :id"), {"id": str(alert_id)})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Update alert
    await db.execute(text("""
        UPDATE detection.alerts 
        SET status = 'closed', closed_at = NOW(), closed_by = :closed_by, close_reason = :reason
        WHERE alert_id = :alert_id
    """), {
        "alert_id": str(alert_id),
        "closed_by": str(current_user.id),
        "reason": request.reason,
    })
    
    await db.commit()
    
    return {"message": "Alert closed", "alert_id": str(alert_id)}


@router.post("/{alert_id}/suppress")
async def suppress_alert(
    alert_id: UUID,
    rule_id: str = Query(...),
    duration_seconds: int = Query(3600, ge=60, le=86400),
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create suppression rule for alert."""
    # Implementation would create a suppression rule
    return {"message": "Suppression rule created", "alert_id": str(alert_id), "rule_id": rule_id}


@router.get("/stats/summary")
async def get_alert_summary(
    hours: int = Query(24, ge=1, le=168),
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Get alert statistics summary."""
    from sqlalchemy import text, func
    
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total alerts
    total = await db.execute(select(func.count()).select_from(text("detection.alerts")).where(text("first_seen >= :since")), {"since": since})
    total_count = total.scalar() or 0
    
    # By severity
    severity_result = await db.execute(text("""
        SELECT severity, COUNT(*) as count 
        FROM detection.alerts 
        WHERE first_seen >= :since 
        GROUP BY severity
    """), {"since": since})
    by_severity = {row.severity: row.count for row in severity_result.fetchall()}
    
    # By status
    status_result = await db.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM detection.alerts 
        WHERE first_seen >= :since 
        GROUP BY status
    """), {"since": since})
    by_status = {row.status: row.count for row in status_result.fetchall()}
    
    # Top rules
    rules_result = await db.execute(text("""
        SELECT rule_id, rule_name, COUNT(*) as count 
        FROM detection.alerts 
        WHERE first_seen >= :since 
        GROUP BY rule_id, rule_name 
        ORDER BY count DESC 
        LIMIT 10
    """), {"since": since})
    top_rules = [{"rule_id": str(row.rule_id), "rule_name": row.rule_name, "count": row.count} 
                 for row in rules_result.fetchall()]
    
    return {
        "total": total_count,
        "by_severity": by_severity,
        "by_status": by_status,
        "top_rules": top_rules,
        "period_hours": hours,
    }


# Import for datetime operations
from datetime import timedelta
from typing import List, Optional