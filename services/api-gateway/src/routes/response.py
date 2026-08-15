"""
Response orchestration routes for AegisForge API Gateway.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user, require_incident_commander, require_admin
from ..database import get_db

router = APIRouter()


class ResponseActionListResponse(BaseModel):
    action_id: str
    incident_id: Optional[str]
    alert_id: Optional[str]
    action_type: str
    status: str
    dry_run: bool
    requested_by: str
    requested_at: datetime
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    target_resource: Dict
    execution_result: Optional[Dict] = None


class ResponseActionDetailResponse(BaseModel):
    action_id: str
    incident_id: Optional[str]
    alert_id: Optional[str]
    action_type: str
    status: str
    dry_run: bool
    require_approval: bool
    requested_by: str
    requested_at: datetime
    approver: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    target_resource: Dict
    parameters: Dict
    dry_run_result: Optional[Dict] = None
    execution_result: Optional[Dict] = None
    execution_error: Optional[str] = None
    rollback_plan: Dict = {}
    rollback_result: Optional[Dict] = None
    rolled_back_at: Optional[datetime] = None
    rolled_back_by: Optional[str] = None
    rollback_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    timeout_seconds: int
    retry_count: int
    max_retries: int
    circuit_breaker_tripped: bool
    namespace: str
    allowed_namespaces: List[str]
    audit_log_id: Optional[str]


class ResponseActionCreateRequest(BaseModel):
    incident_id: Optional[str] = None
    alert_id: Optional[str] = None
    action_type: str
    target_resource: Dict
    parameters: Dict = Field(default_factory=dict)
    dry_run: bool = True
    require_approval: bool = True
    namespace: str = "aegisforge-lab"
    timeout_seconds: int = 300


class ResponseActionApproveRequest(BaseModel):
    reason: Optional[str] = None


class ResponseActionRejectRequest(BaseModel):
    reason: str


class ResponseActionRollbackRequest(BaseModel):
    reason: str


class ResponseActionListResponseWrapper(BaseModel):
    actions: List[ResponseActionListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


router = APIRouter()


@router.get("", response_model=ResponseActionListResponseWrapper)
async def list_response_actions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    action_type: Optional[str] = Query(None),
    incident_id: Optional[str] = Query(None),
    alert_id: Optional[str] = Query(None),
    requested_by: Optional[str] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """List response actions with filtering and pagination."""
    from sqlalchemy import select, func, desc, text
    
    query = """
        SELECT action_id, incident_id, alert_id, action_type, status, dry_run,
               requested_by, requested_at, approved_by, approved_at, target_resource
        FROM response.actions
        WHERE 1=1
    """
    params = {}
    
    if status:
        query += " AND status = :status"
        params["status"] = status
    if action_type:
        query += " AND action_type = :action_type"
        params["action_type"] = action_type
    if incident_id:
        query += " AND incident_id = :incident_id"
        params["incident_id"] = incident_id
    if alert_id:
        query += " AND alert_id = :alert_id"
        params["alert_id"] = alert_id
    if requested_by:
        query += " AND requested_by = :requested_by"
        params["requested_by"] = requested_by
    if start_date:
        query += " AND requested_at >= :start_date"
        params["start_date"] = start_date
    if end_date:
        query += " AND requested_at <= :end_date"
        params["end_date"] = end_date
    
    # Count total
    count_query = f"SELECT COUNT(*) FROM ({query}) AS subq"
    total = await db.execute(select(func.count()).select_from(text(count_query)), params)
    total = total.scalar() or 0
    
    # Pagination
    offset = (page - 1) * page_size
    query += " ORDER BY requested_at DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset
    
    result = await db.execute(text(query), params)
    actions = result.fetchall()
    
    actions_list = [
        ResponseActionListResponse(
            action_id=str(row.action_id),
            incident_id=str(row.incident_id) if row.incident_id else None,
            alert_id=str(row.alert_id) if row.alert_id else None,
            action_type=row.action_type,
            status=row.status,
            dry_run=row.dry_run,
            requested_by=row.requested_by,
            requested_at=row.requested_at,
            approved_by=row.approved_by,
            approved_at=row.approved_at,
            target_resource=row.target_resource,
            execution_result=row.execution_result,
        )
        for row in actions
    ]
    
    return ResponseActionListResponseWrapper(
        actions=actions_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/{action_id}", response_model="ResponseActionDetailResponse")
async def get_response_action(
    action_id: UUID,
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed response action information."""
    result = await db.execute(text("SELECT * FROM response.actions WHERE action_id = :action_id"), {"action_id": str(action_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Response action not found")
    
    action_dict = dict(row._mapping)
    for key, value in action_dict.items():
        if isinstance(value, UUID):
            action_dict[key] = str(value)
    
    # Convert to response model
    return {
        "action_id": str(action_dict["action_id"]),
        "incident_id": str(action_dict["incident_id"]) if action_dict["incident_id"] else None,
        "alert_id": str(action_dict["alert_id"]) if action_dict["alert_id"] else None,
        "action_type": action_dict["action_type"],
        "status": action_dict["status"],
        "dry_run": action_dict["dry_run"],
        "require_approval": action_dict["require_approval"],
        "requested_by": action_dict["requested_by"],
        "requested_at": action_dict["requested_at"],
        "approver": action_dict["approver"],
        "approved_at": action_dict["approved_at"],
        "rejection_reason": action_dict["rejection_reason"],
        "target_resource": action_dict["target_resource"],
        "parameters": action_dict["parameters"],
        "dry_run_result": action_dict["dry_run_result"],
        "execution_result": action_dict["execution_result"],
        "execution_error": action_dict["execution_error"],
        "rollback_plan": action_dict["rollback_plan"],
        "rollback_result": action_dict["rollback_result"],
        "rolled_back_at": action_dict["rolled_back_at"],
        "rolled_back_by": action_dict["rolled_back_by"],
        "rollback_reason": action_dict["rollback_reason"],
        "created_at": action_dict["created_at"],
        "updated_at": action_dict["updated_at"],
        "expires_at": action_dict["expires_at"],
        "timeout_seconds": action_dict["timeout_seconds"],
        "retry_count": action_dict["retry_count"],
        "max_retries": action_dict["max_retries"],
        "circuit_breaker_tripped": action_dict["circuit_breaker_tripped"],
        "namespace": action_dict["namespace"],
        "allowed_namespaces": action_dict["allowed_namespaces"],
        "audit_log_id": action_dict["audit_log_id"],
    }


@router.post("", response_model=dict, status_code=201)
async def create_response_action(
    request: ResponseActionCreateRequest,
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Create a new response action."""
    from uuid import uuid4
    
    action_id = uuid4()
    now = datetime.utcnow()
    
    # Validate incident/alert if provided
    if request.incident_id:
        result = await db.execute(text("SELECT incident_id FROM detection.incidents WHERE incident_id = :id"), {"id": request.incident_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Incident not found")
    
    if request.alert_id:
        result = await db.execute(text("SELECT alert_id FROM detection.alerts WHERE alert_id = :id"), {"id": request.alert_id})
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check namespace allowlist
    if request.namespace not in request.allowed_namespaces:
        raise HTTPException(status_code=400, detail=f"Namespace {request.namespace} not in allowlist")
    
    # Insert action
    result = await db.execute(text("""
        INSERT INTO response.actions (
            action_id, incident_id, alert_id, action_type, status, dry_run,
            require_approval, requested_by, requested_at, target_resource, parameters,
            namespace, allowed_namespaces, timeout_seconds, expires_at, dry_run
        ) VALUES (
            :action_id, :incident_id, :alert_id, :action_type, 
            CASE WHEN :require_approval THEN 'pending_approval' ELSE 'pending' END,
            :dry_run, :require_approval, :requested_by, :requested_at,
            :target_resource, :parameters, :namespace, :allowed_namespaces,
            :timeout_seconds, :expires_at, :dry_run
        ) RETURNING *
    """), {
        "action_id": str(uuid4()),
        "incident_id": request.incident_id,
        "alert_id": request.alert_id,
        "action_type": request.action_type,
        "dry_run": request.dry_run,
        "require_approval": request.require_approval,
        "requested_by": str(current_user.id),
        "requested_at": datetime.utcnow(),
        "target_resource": request.target_resource,
        "parameters": request.parameters,
        "namespace": request.namespace,
        "allowed_namespaces": request.allowed_namespaces,
        "timeout_seconds": request.timeout_seconds,
        "expires_at": datetime.utcnow() + timedelta(seconds=request.timeout_seconds),
    })
    
    await db.commit()
    
    return {"action_id": str(uuid4()), "status": "created"}


@router.post("/{action_id}/approve")
async def approve_response_action(
    action_id: UUID,
    request: "ResponseActionApproveRequest",
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Approve a response action."""
    from sqlalchemy import text
    
    result = await db.execute(text("SELECT * FROM response.actions WHERE action_id = :id"), {"id": str(action_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Response action not found")
    
    if row.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Action not pending approval (status: {row.status})")
    
    # Check if user is in approvers list (if specified)
    # For now, any incident commander can approve
    
    await db.execute(text("""
        UPDATE response.actions 
        SET status = 'approved', approver = :approver, approved_at = NOW()
        WHERE action_id = :action_id
    """), {
        "action_id": str(action_id),
        "approver": str(current_user.id),
    })
    
    await db.commit()
    
    return {"message": "Action approved", "action_id": str(action_id)}


@router.post("/{action_id}/reject")
async def reject_response_action(
    action_id: UUID,
    request: "ResponseActionRejectRequest",
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Reject a response action."""
    from sqlalchemy import text
    
    result = await db.execute(text("SELECT * FROM response.actions WHERE action_id = :id"), {"id": str(action_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Response action not found")
    
    if row.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Action not pending approval (status: {row.status})")
    
    await db.execute(text("""
        UPDATE response.actions 
        SET status = 'rejected', rejection_reason = :reason
        WHERE action_id = :action_id
    """), {
        "action_id": str(action_id),
        "reason": request.reason,
    })
    
    await db.commit()
    
    return {"message": "Action rejected", "action_id": str(action_id)}


@router.post("/{action_id}/execute")
async def execute_response_action(
    action_id: UUID,
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Execute an approved response action."""
    from sqlalchemy import text
    
    result = await db.execute(text("SELECT * FROM response.actions WHERE action_id = :id"), {"id": str(action_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Response action not found")
    
    if row.status not in ["approved", "pending"]:
        raise HTTPException(status_code=400, detail=f"Action cannot be executed (status: {row.status})")
    
    # Check dry_run flag
    dry_run = row.dry_run
    
    # Update status to executing
    await db.execute(text("""
        UPDATE response.actions 
        SET status = 'executing', execution_started_at = NOW()
        WHERE action_id = :action_id
    """), {"action_id": str(action_id)})
    
    await db.commit()
    
    # In real implementation, this would trigger the actual action
    # For now, simulate execution
    import asyncio
    await asyncio.sleep(0.1)
    
    # Simulate execution result
    execution_result = {
        "success": True,
        "message": f"Executed {row.action_type} on {row.target_resource}",
        "details": {},
    }
    
    # Update with result
    await db.execute(text("""
        UPDATE response.actions 
        SET status = 'completed', execution_completed_at = NOW(), 
            execution_result = :result, dry_run = :dry_run
        WHERE action_id = :action_id
    """), {
        "action_id": str(action_id),
        "result": {"success": True, "message": f"Executed {row.action_type}"},
        "dry_run": dry_run,
    })
    
    await db.commit()
    
    return {"message": "Action executed", "action_id": str(action_id), "result": execution_result}


@router.post("/{action_id}/rollback")
async def rollback_response_action(
    action_id: UUID,
    request: "ResponseActionRollbackRequest",
    current_user = Depends(require_incident_commander),
    db: AsyncSession = Depends(get_db),
):
    """Rollback a response action."""
    from sqlalchemy import text
    
    result = await db.execute(text("SELECT * FROM response.actions WHERE action_id = :id"), {"id": str(action_id)})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Response action not found")
    
    if row.status not in ["completed", "executing"]:
        raise HTTPException(status_code=400, detail=f"Action cannot be rolled back (status: {row.status})")
    
    if not row.rollback_plan:
        raise HTTPException(status_code=400, detail="No rollback plan available")
    
    # Simulate rollback
    rollback_result = {
        "success": True,
        "message": f"Rolled back {row.action_type}",
        "details": {},
    }
    
    await db.execute(text("""
        UPDATE response.actions 
        SET status = 'rolled_back', rolled_back_at = NOW(), 
            rolled_back_by = :user, rollback_reason = :reason,
            rollback_result = :result
        WHERE action_id = :action_id
    """), {
        "action_id": str(action_id),
        "user": str(current_user.id),
        "reason": request.reason,
        "result": rollback_result,
    })
    
    await db.commit()
    
    return {"message": "Action rolled back", "action_id": str(action_id), "result": rollback_result}


@router.get("/stats/summary")
async def get_response_summary(
    hours: int = Query(24, ge=1, le=168),
    current_user = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    """Get response action statistics summary."""
    from sqlalchemy import text, func
    
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Total actions
    total = await db.execute(select(func.count()).select_from(text("response.actions")).where(text("requested_at >= :since")), {"since": since})
    total_count = total.scalar() or 0
    
    # By status
    status_result = await db.execute(text("""
        SELECT status, COUNT(*) as count 
        FROM response.actions 
        WHERE requested_at >= :since 
        GROUP BY status
    """), {"since": since})
    by_status = {row.status: row.count for row in status_result.fetchall()}
    
    # By action type
    type_result = await db.execute(text("""
        SELECT action_type, COUNT(*) as count 
        FROM response.actions 
        WHERE requested_at >= :since 
        GROUP BY action_type
    """), {"since": since})
    by_type = {row.action_type: row.count for row in type_result.fetchall()}
    
    # Success rate
    completed = by_status.get("completed", 0)
    failed = by_status.get("failed", 0)
    total_executed = completed + failed
    success_rate = (completed / total_executed * 100) if total_executed > 0 else 0
    
    return {
        "total": total_count,
        "by_status": by_status,
        "by_type": by_type,
        "success_rate_percent": round(success_rate, 2),
        "period_hours": hours,
    }


from datetime import timedelta
from typing import List, Optional, Dict