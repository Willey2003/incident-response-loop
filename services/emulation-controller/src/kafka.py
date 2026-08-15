"""
Kafka/Redpanda producer for Emulation Controller.
"""

from aiokafka import AIOKafkaProducer
from typing import Optional
import json
import structlog

from .config import settings

logger = structlog.get_logger()

_producer: Optional = None


async def init_kafka() -> None:
    """Initialize Kafka producer."""
    global _producer
    
    _producer = AIOKafkaProducer(
        bootstrap_servers=settings.REDPANDA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
        compression_type="gzip",
        acks="all",
    )
    
    await _producer.start()
    logger.info("Kafka producer started")


async def close_kafka() -> None:
    """Close Kafka connections."""
    global _producer
    
    if _producer:
        await _producer.stop()


def get_producer():
    return _producer