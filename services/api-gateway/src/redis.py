"""
Redis connection and client management for API Gateway.
"""

import redis.asyncio as redis
from typing import Optional
from contextlib import asynccontextmanager

from .config import settings

_redis_client: Optional[redis.Redis] = None
_redis_pool: Optional[redis.ConnectionPool] = None


async def init_redis() -> None:
    """Initialize Redis connection pool."""
    global _redis_client, _redis_pool
    
    _redis_pool = redis.ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        decode_responses=True,
    )
    _redis_client = redis.Redis(connection_pool=_redis_pool)
    
    # Test connection
    await _redis_client.ping()


async def close_redis() -> None:
    """Close Redis connections."""
    global _redis_client, _redis_pool
    
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
    
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None


def get_redis() -> Optional[redis.Redis]:
    """Get Redis client instance."""
    return _redis_client


@asynccontextmanager
async def get_redis_client():
    """Get Redis client for dependency injection."""
    client = get_redis()
    if client is None:
        raise RuntimeError("Redis not initialized")
    try:
        yield client
    finally:
        pass