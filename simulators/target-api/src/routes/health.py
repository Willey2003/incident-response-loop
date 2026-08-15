"""
Health routes for Target API.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from ..config import settings
from ..kafka import get_producer

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
    environment: str
    checks: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="target-api",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        environment=settings.ENVIRONMENT,
        checks={
            "api": "healthy",
        }
    )


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    try:
        from ..kafka import get_producer
        producer = get_producer()
        if producer:
            return {"status": "ready"}
        return {"status": "not ready", "reason": "producer not available"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Not ready: {str(e)}")


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}