"""
AegisForge Response Orchestrator
Approval-gated response playbooks with dry-run, rollback, and audit logging.
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
from .consumer import AlertConsumer
from .executor import ActionExecutor
from .database import init_db as init_db_alias, close_db as close_db_alias

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting Response Orchestrator")
    await init_db_alias()
    await init_kafka()
    
    app.state.consumer = AlertConsumer()
    app.state.executor = ActionExecutor()
    
    app.state.consumer_task = asyncio.create_task(app.state.consumer.run())
    logger.info("Response Orchestrator started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Response Orchestrator")
    if app.state.consumer_task:
        app.state.consumer_task.cancel()
        try:
            await app.state.consumer_task
        except asyncio.CancelledError:
            pass
    await close_db_alias()
    await close_kafka()
    logger.info("Response Orchestrator stopped")


app = FastAPI(
    title="AegisForge Response Orchestrator",
    description="Approval-gated response playbooks with dry-run, rollback, and audit logging",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "response-orchestrator"}


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


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