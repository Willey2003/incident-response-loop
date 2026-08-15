"""
AegisForge DNS Simulator
Generates synthetic DNS anomaly events.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio
import structlog

from fastapi import FastAPI
from prometheus_client import generate_latest
from fastapi.responses import Response

from .config import settings
from .generator import DNSEventGenerator
from .kafka import init_kafka, close_kafka

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting DNS Simulator")
    await init_kafka()
    
    app.state.generator = DNSEventGenerator()
    app.state.generator_task = asyncio.create_task(app.state.generator.run())
    logger.info("DNS Simulator started")
    
    yield
    
    logger.info("Shutting down DNS Simulator")
    if app.state.generator_task:
        app.state.generator_task.cancel()
        try:
            await app.state.generator_task
        except asyncio.CancelledError:
            pass
    await close_kafka()
    logger.info("DNS Simulator stopped")


app = FastAPI(
    title="AegisForge DNS Simulator",
    description="Generates synthetic DNS anomaly events",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dns-simulator"}


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