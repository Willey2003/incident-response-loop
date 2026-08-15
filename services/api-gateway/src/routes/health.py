"""
Health check routes for API Gateway.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

from ..config import settings
from ..database import get_db
from ..redis import get_redis

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
    environment: str
    checks: Dict[str, Any]


class DetailedHealthResponse(HealthResponse):
    database: Dict[str, Any]
    redis: Dict[str, Any]
    services: Dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="api-gateway",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        environment=settings.ENVIRONMENT,
        checks={
            "api": "healthy",
        }
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Detailed health check with dependency checks."""
    checks = {}
    overall_healthy = True
    
    # Database check
    db_healthy = True
    try:
        from ..database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        db_healthy = False
        overall_healthy = False
    
    checks["database"] = db_status
    
    # Redis check
    redis_healthy = True
    try:
        from ..redis import get_redis
        redis_client = get_redis()
        if redis_client:
            await redis_client.ping()
            redis_status = "healthy"
        else:
            redis_status = "unhealthy: not initialized"
            redis_healthy = False
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
        redis_healthy = False
    
    checks["redis"] = redis_status
    
    # Services check (placeholder)
    checks["api_gateway"] = "healthy"
    
    # Determine overall status
    if not (db_healthy and redis_healthy):
        overall_healthy = False
    
    return DetailedHealthResponse(
        status="healthy" if overall_healthy else "degraded",
        service="api-gateway",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        environment=settings.ENVIRONMENT,
        checks=checks,
        database={"status": db_status},
        redis={"status": redis_status},
        services={
            "api_gateway": "healthy",
        }
    )


@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    # Check critical dependencies
    try:
        from ..database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        
        from ..redis import get_redis
        redis_client = get_redis()
        if redis_client:
            await redis_client.ping()
        
        return {"status": "ready"}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=f"Not ready: {str(e)}")


@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}