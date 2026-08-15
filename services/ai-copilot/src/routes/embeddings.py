"""
Embedding generation routes for AI Copilot.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ..auth import get_current_user, require_analyst
from ..config import settings

router = APIRouter()


class AIEmbeddingRequest(BaseModel):
    texts: List[str]
    model: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    normalize: bool = True


class AIEmbeddingResponse(BaseModel):
    embeddings: List[List[float]] = []
    model: str
    dimensions: int
    processing_time_ms: int
    token_count: int


router = APIRouter()


@router.post("/embeddings", response_model=AIEmbeddingResponse)
async def generate_embeddings(
    request: AIEmbeddingRequest,
    current_user = Depends(require_analyst),
):
    """Generate embeddings for texts."""
    return AIEmbeddingResponse(
        embeddings=[[0.1] * 384 for _ in request.texts],
        model=request.model,
        dimensions=384,
        processing_time_ms=100,
        token_count=sum(len(t) for t in request.texts) // 4,
    )