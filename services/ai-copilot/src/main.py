"""
AegisForge AI Security Copilot
CPU-only AI with Ollama + Qdrant for incident analysis, alert triage, runbook recommendation.
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
from .embedding_service import EmbeddingService
from .retrieval_service import RetrievalService
from .ollama_client import OllamaClient
from .redaction import RedactionPipeline
from .indexer import KnowledgeIndexer

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting AI Security Copilot")
    await init_db()
    
    app.state.embedding_service = EmbeddingService()
    app.state.retrieval_service = RetrievalService()
    app.state.ollama_client = OllamaClient()
    app.state.redaction_pipeline = RedactionPipeline()
    app.state.indexer = KnowledgeIndexer()
    
    # Initialize services
    await app.state.embedding_service.initialize()
    await app.state.retrieval_service.initialize()
    await app.state.ollama_client.initialize()
    await app.state.indexer.initialize()
    
    # Start background indexer
    app.state.indexer_task = asyncio.create_task(app.state.indexer.run_periodic_indexing())
    
    logger.info("AI Security Copilot started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Security Copilot")
    if app.state.indexer_task:
        app.state.indexer_task.cancel()
        try:
            await app.state.indexer_task
        except asyncio.CancelledError:
            pass
    await close_db()
    logger.info("AI Security Copilot stopped")


app = FastAPI(
    title="AegisForge AI Security Copilot",
    description="CPU-only AI with Ollama + Qdrant for security analysis",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "ai-copilot",
        "model": settings.OLLAMA_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
    }


@app.get("/metrics")
async def metrics():
    from fastapi.responses import Response
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Include routes
from .routes import investigate, triage, runbook, report, timeline, search, embeddings, redact

app.include_router(investigate.router, prefix="/api/v1/ai", tags=["investigate"])
app.include_router(triage.router, prefix="/api/v1/ai", tags=["triage"])
app.include_router(runbook.router, prefix="/api/v1/ai", tags=["runbook"])
app.include_router(report.router, prefix="/api/v1/ai", tags=["report"])
app.include_router(timeline.router, prefix="/api/v1/ai", tags=["timeline"])
app.include_router(search.router, prefix="/api/v1/ai", tags=["search"])
app.include_router(embeddings.router, prefix="/api/v1/ai", tags=["embeddings"])
app.include_router(redact.router, prefix="/api/v1/ai", tags=["redact"])


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