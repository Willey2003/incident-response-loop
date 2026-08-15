"""
Ollama client for AI Copilot.
Handles LLM inference via Ollama API.
"""

import asyncio
import time
import json
import httpx
from typing import List, Dict, Any, Optional, AsyncGenerator

from .config import settings

import structlog

logger = structlog.get_logger()


class OllamaClient:
    """Client for Ollama LLM inference."""
    
    def __init__(self):
        self.base_url = f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}"
        self.model = settings.OLLAMA_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.client: Optional[httpx.AsyncClient] = None
        self.num_parallel = settings.OLLAMA_NUM_PARALLEL
        self.num_thread = settings.OLLAMA_NUM_THREAD
    
    async def initialize(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(300.0),
            limits=httpx.Limits(max_connections=self.num_parallel, max_keepalive_connections=self.num_parallel),
        )
        
        # Check if model is available
        await self._ensure_model()
        logger.info("Ollama client initialized", model=self.model)
    
    async def _ensure_model(self):
        """Check if model is available, pull if needed."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            if self.model not in model_names:
                logger.info("Pulling model", model=self.model)
                await self.pull_model(self.model)
            else:
                logger.info("Model already available", model=self.model)
        except Exception as e:
            logger.warning("Could not check model availability", error=str(e))
    
    async def pull_model(self, model_name: str):
        """Pull a model from Ollama registry."""
        async with self.client.stream("POST", "/api/pull", json={"name": model_name}) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "status" in data:
                            logger.debug("Pull progress", status=data["status"])
                    except:
                        pass
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        stop: Optional[List[str]] = None,
        stream: bool = False,
    ) -> str:
        """Generate text completion."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "num_thread": self.num_thread,
                "num_ctx": 4096,
            },
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if stop:
            payload["stop"] = stop
        
        start = time.time()
        
        try:
            response = await self.client.post(
                "/api/generate",
                json=payload,
                timeout=300.0,
            )
            response.raise_for_status()
            result = response.json()
            
            elapsed = (time.time() - start) * 1000
            logger.debug("Ollama generation completed", time_ms=elapsed)
            
            return result.get("response", "")
            
        except Exception as e:
            logger.error("Ollama generation failed", error=str(e))
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming completion."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "num_thread": self.num_thread,
            },
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        async with self.client.stream("POST", "/api/generate", json=payload, timeout=300.0) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        if data.get("done", False):
                            break
                    except:
                        pass
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> str:
        """Chat completion with message history."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "num_thread": self.num_thread,
            },
        }
        
        try:
            response = await self.client.post("/api/chat", json=payload, timeout=300.0)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except Exception as e:
            logger.error("Ollama chat failed", error=str(e))
            raise
    
    async def embed(self, texts: List[str], model: Optional[str] = None) -> List[List[float]]:
        """Generate embeddings using Ollama."""
        model = model or self.embedding_model
        embeddings = []
        
        for text in texts:
            payload = {
                "model": model,
                "prompt": text,
            }
            try:
                response = await self.client.post("/api/embeddings", json=payload, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                embeddings.append(result.get("embedding", []))
            except Exception as e:
                logger.error("Embedding generation failed", error=str(e))
                raise
        
        return embeddings
    
    async def list_models(self) -> List[Dict]:
        """List available models."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except Exception as e:
            logger.error("Failed to list models", error=str(e))
            return []
    
    async def pull_model(self, model_name: str):
        """Pull a model from Ollama registry."""
        async with self.client.stream("POST", "/api/pull", json={"name": model_name}) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "status" in data:
                            logger.debug("Pull progress", status=data["status"])
                    except:
                        pass
    
    async def close(self):
        """Close the client."""
        if self.client:
            await self.client.aclose()
    
    async def health_check(self) -> Dict:
        """Check Ollama health."""
        try:
            response = await self.client.get("/api/tags", timeout=10.0)
            response.raise_for_status()
            return {"status": "healthy", "models": len(response.json().get("models", []))}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}