"""
Emulation runs routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..auth import get_current_user, require_emulation_control, require_analyst
from ..config import settings
from ..database import get_db_session

router = APIRouter()


class EmulationRunRequest(BaseModel):
    scenario_id: str
    config_override: Dict = Field(default_factory=dict)
    target_namespace: str = "aegisforge-lab"
    duration_override: Optional[int] = Field(None, ge=60, le=3600)


class EmulationRunResponse(BaseModel):
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


router = APIRouter()


@router.get("/runs", response_model=dict)
async def list_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    scenario_id: Optional[str] = Query(None),
    current_user = Depends(require_analyst),
):
    """List emulation runs."""
    return {
        "runs": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "total_pages": 0,
    }


@router.post("/runs", response_model=dict, status_code=201)
async def start_emulation_run(
    request: EmulationRunRequest,
    current_user = Depends(require_emulation_control),
):
    """Start an emulation run."""
    return {
        "run_id": "new-run-id",
        "status": "pending",
        "message": "Emulation run started (demo mode)"
    }


@router.post("/runs/{run_id}/cancel")
async def cancel_run(
    run_id: str,
    reason: str = Query(..., min_length=1),
    current_user = Depends(require_emulation_control),
):
    """Cancel a running emulation."""
    return {"message": "Run cancelled", "run_id": run_id}