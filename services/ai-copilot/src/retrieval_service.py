"""
Retrieval service for AI Copilot.
Handles vector search and retrieval from Qdrant.
"""

import time
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchRequest

from .config import settings
from .embedding_service import EmbeddingService

import structlog

logger = structlog.get_logger()


class RetrievalService:
    """Handles vector search and retrieval from Qdrant."""
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.embedding_service: Optional[EmbeddingService] = None
        self.collection = settings.QDRANT_COLLECTION
        self.vector_size = settings.QDRANT_VECTOR_SIZE
    
    def set_embedding_service(self, service: EmbeddingService):
        """Set the embedding service dependency."""
        self.embedding_service = service
    
    async def initialize(self):
        """Initialize Qdrant client and collection."""
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=30,
        )
        
        # Ensure collection exists
        await self._ensure_collection()
        logger.info("Retrieval service initialized", collection=self.collection)
    
    async def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection not in collection_names:
            from qdrant_client.models import VectorParams, Distance
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection", collection=self.collection)
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict] = None,
        score_threshold: float = 0.7,
    ) -> List[Dict]:
        """Search for relevant documents."""
        if not self.embedding_service:
            raise RuntimeError("Embedding service not set")
        
        # Embed query
        query_vector = await self.embedding_service.embed_query(query)
        
        # Build filter
        query_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, list):
                    for v in value:
                        conditions.append(FieldCondition(key=key, match=MatchValue(value=v)))
                else:
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            if conditions:
                from qdrant_client.models import Filter
                query_filter = Filter(must=conditions)
        
        # Search
        start = time.time()
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )
        
        elapsed = (time.time() - start) * 1000
        logger.debug("Qdrant search completed", results=len(results), time_ms=elapsed)
        
        # Format results
        results_list = []
        for hit in results:
            results_list.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
                "citation": self._format_citation(hit.payload),
            })
        
        return results_list
    
    def _format_citation(self, payload: Dict) -> Dict:
        """Format payload as citation."""
        return {
            "source_type": payload.get("source_type", "unknown"),
            "source_id": payload.get("source_id", "unknown"),
            "title": payload.get("title", "Untitled"),
            "excerpt": payload.get("content", "")[:200] + "...",
            "timestamp": payload.get("created_at"),
        }
    
    async def index_document(self, document: Dict) -> str:
        """Index a single document."""
        if not self.embedding_service:
            raise RuntimeError("Embedding service not set")
        
        # Prepare text for embedding
        text = self._prepare_document_text(document)
        
        # Generate embedding
        vector = await self.embedding_service.embed_query(text)
        
        # Prepare point
        point_id = document.get("id") or document.get("source_id")
        if not point_id:
            raise ValueError("Document must have an id or source_id")
        
        from qdrant_client.models import PointStruct
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={
                "source_type": document.get("source_type", "unknown"),
                "source_id": document.get("source_id", ""),
                "title": document.get("title", ""),
                "content": document.get("content", "")[:1000],
                "created_at": document.get("created_at"),
                "metadata": document.get("metadata", {}),
            },
        )
        
        # Upsert
        self.client.upsert(
            collection_name=self.collection,
            points=[point],
        )
        
        return point_id
    
    async def index_batch(self, documents: List[Dict]) -> List[str]:
        """Index multiple documents in batch."""
        if not documents:
            return []
        
        # Prepare texts
        texts = [self._prepare_document_text(doc) for doc in documents]
        
        # Generate embeddings
        vectors = await self.embedding_service.embed_texts(texts)
        
        # Prepare points
        from qdrant_client.models import PointStruct
        points = []
        for doc, vector in zip(documents, vectors):
            point_id = doc.get("id") or doc.get("source_id")
            if not point_id:
                continue
            
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "source_type": doc.get("source_type", "unknown"),
                    "source_id": doc.get("source_id", ""),
                    "title": doc.get("title", ""),
                    "content": doc.get("content", "")[:1000],
                    "created_at": doc.get("created_at"),
                    "metadata": doc.get("metadata", {}),
                },
            )
            points.append(point)
        
        # Batch upsert
        self.client.upsert(
            collection_name=self.collection,
            points=points,
        )
        
        return [p.id for p in points]
    
    def _prepare_document_text(self, doc: Dict) -> str:
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
    
    def set_embedding_service(self, service):
        """Set the embedding service."""
        self.embedding_service = service