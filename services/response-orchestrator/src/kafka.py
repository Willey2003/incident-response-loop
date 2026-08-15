"""
Kafka/Redpanda consumer and producer for Response Orchestrator.
"""

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from typing import Optional
import json
import structlog

from .config import settings

logger = structlog.get_logger()

_consumer: Optional = None
_producer: Optional = None


async def init_kafka() -> None:
    """Initialize Kafka consumer and producer."""
    global _consumer, _producer
    
    # Consumer for alerts and incidents
    _consumer = AIOKafkaConsumer(
        "security-alerts",
        "security-incidents",
        bootstrap_servers=settings.REDPANDA_BOOTSTRAP_SERVERS,
        group_id="response-orchestrator",
        auto_offset_reset="latest",
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=True,
        auto_commit_interval_ms=5000,
    )
    
    await _consumer.start()
    logger.info("Kafka consumer started")
    
    # Producer for audit logs
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
    global _consumer, _producer
    
    if _consumer:
        await _consumer.stop()
    
    if _producer:
        await _producer.stop()


def get_consumer():
    return _consumer


def get_producer():
    return _producer