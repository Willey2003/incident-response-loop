"""
AegisForge Detection Engine
Consumes events from Redpanda, evaluates detection rules, generates alerts.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Dict, Any, Optional
import asyncio
import json
import structlog

from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

from .config import settings
from .consumer import EventConsumer
from .evaluator import RuleEvaluator
from .publisher import AlertPublisher
from .rules_loader import load_rules
from .database import init_db, close_db
from .kafka import init_kafka, close_kafka

logger = structlog.get_logger()

# Prometheus metrics
events_processed = Counter("detection_events_processed_total", "Total events processed", ["status"])
rules_evaluated = Counter("detection_rules_evaluated_total", "Total rules evaluated", ["result"])
alerts_generated = Counter("detection_alerts_generated_total", "Total alerts generated", ["severity"])
processing_latency = Histogram("detection_processing_latency_seconds", "Event processing latency", ["stage"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting Detection Engine")
    await init_db()
    await init_kafka()
    await load_rules()
    
    # Start consumer
    app.state.consumer = EventConsumer()
    app.state.evaluator = RuleEvaluator()
    app.state.publisher = AlertPublisher()
    
    app.state.consumer_task = asyncio.create_task(app.state.consumer.run())
    logger.info("Detection Engine started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Detection Engine")
    if app.state.consumer_task:
        app.state.consumer_task.cancel()
        try:
            await app.state.consumer_task
        except asyncio.CancelledError:
            pass
    await close_db()
    await close_kafka()
    logger.info("Detection Engine stopped")


app = FastAPI(
    title="AegisForge Detection Engine",
    description="Event consumption, rule evaluation, and alert generation",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "detection-engine"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/stats")
async def stats():
    return {
        "events_processed": events_processed._value._value if hasattr(events_processed, '_value') else 0,
        "rules_evaluated": rules_evaluated._value._value if hasattr(rules_evaluated, '_value') else 0,
        "alerts_generated": alerts_generated._value._value if hasattr(alerts_generated, '_value') else 0,
    }


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