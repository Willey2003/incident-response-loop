"""
AegisForge Target API
Demo API for lab simulations with authentication endpoints.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import structlog

from fastapi import FastAPI
from prometheus_client import generate_latest
from fastapi.responses import Response

from .config import settings
from .routes import auth, users, health as health_routes
from .kafka import init_kafka, close_kafka

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting Target API")
    await init_kafka()
    logger.info("Target API started")
    
    yield
    
    logger.info("Shutting down Target API")
    await close_kafka()
    logger.info("Target API stopped")


app = FastAPI(
    title="AegisForge Target API",
    description="Demo API for lab simulations with authentication endpoints",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "target-api"}


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include routes
app.include_router(health_routes.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.ENVIRONMENT == "development",
    )