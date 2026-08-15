"""
Embedding service for AI Copilot.
Generates embeddings using sentence-transformers.
"""

import asyncio
import time
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import structlog

from .config import settings

logger = structlog.get_logger()


class EmbeddingService:
    """Generates embeddings using sentence-transformers models."""
    
    def __init__(self):
        self.model: Optional = None
        self.model_name = settings.EMBEDDING_MODEL
        self.batch_size = settings.EMBEDDING_BATCH_SIZE
        self.normalize = True
    
    async def initialize(self):
        """Load the embedding model."""
        logger.info("Loading embedding model", model=self.model_name)
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        self.model = await loop.run_in_executor(
            None, 
            lambda: SentenceTransformer(self.model_name)
        )
        # Set max sequence length
        self.model.max_seq_length = 512
        logger.info("Embedding model loaded", model=self.model_name)
    
    async def embed_texts(self, texts: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not self.model:
            raise RuntimeError("Embedding model not initialized")
        
        batch_size = batch_size or self.batch_size
        
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=self.normalize,
            )
        )
        
        return embeddings.tolist()
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        embeddings = await self.embed_texts([query])
        return embeddings[0]
    
    async def embed_documents(self, documents: List[dict]) -> List[List[float]]:
        """Generate embeddings for documents with metadata."""
        texts = [self._prepare_document_text(doc) for doc in documents]
        return await self.embed_texts(texts)
    
    def _prepare_document_text(self, doc: dict) -> str:
        """Prepare document text for embedding."""
        parts = []
        if doc.get("title"):
            parts.append(doc["title"])
        if doc.get("content"):
            parts.append(doc["content"])
        if doc.get("metadata"):
            import json
            parts.append(json.dumps(doc["metadata"], sort_keys=True))
        return " | ".join(parts)
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions."""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 384  # Default for all-MiniLM-L6-v2