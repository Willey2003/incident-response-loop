"""
AegisForge Emulation Controller
Safe threat emulation lab controller with approval-gated scenario execution.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio
import structlog

from fastapi import FastAPI
from prometheus_client import generate_latest
from fastapi.responses import Response

from .config import settings
from .database import init_db, close_db
from .kafka import init_kafka, close_kafka
from .scheduler import ScenarioScheduler
from .database import init_db as init_db_alias, close_db as close_db_alias

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting Emulation Controller")
    await init_db_alias()
    await init_kafka()
    
    app.state.scheduler = ScenarioScheduler()
    
    app.state.scheduler_task = asyncio.create_task(app.state.scheduler.run())
    logger.info("Emulation Controller started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Emulation Controller")
    if app.state.scheduler_task:
        app.state.scheduler_task.cancel()
        try:
            await app.state.scheduler_task
        except asyncio.CancelledError:
            pass
    await close_db_alias()
    await close_kafka()
    logger.info("Emulation Controller stopped")


app = FastAPI(
    title="AegisForge Emulation Controller",
    description="Safe threat emulation lab controller with approval-gated scenario execution",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "emulation-controller"}


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include routes
from .routes import scenarios, runs, templates

app.include_router(scenarios.router, prefix="/api/v1/emulation", tags=["scenarios"])
app.include_router(runs.router, prefix="/api/v1/emulation", tags=["runs"])
app.include_router(templates.router, prefix="/api/v1/emulation", tags=["templates"])


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