"""
Alert and Incident consumer for Response Orchestrator.
"""

import asyncio
import json
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from .config import settings
from .kafka import get_consumer, get_producer

logger = structlog.get_logger()


class AlertConsumer:
    """Consumes alerts and incidents from Kafka/Redpanda and processes them."""
    
    def __init__(self):
        self.consumer: Optional = None
        self.running = False
    
    async def start(self):
        """Start the consumer."""
        from .kafka import get_consumer
        self.consumer = get_consumer()
        self.running = True
        logger.info("Alert consumer started")
    
    async def stop(self):
        """Stop the consumer."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("Alert consumer stopped")
    
    async def run(self):
        """Main consumer loop."""
        if not self.consumer:
            raise RuntimeError("Consumer not initialized. Call start() first.")
        
        logger.info("Starting alert/incident consumption loop")
        
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                
                try:
                    event = msg.value
                    await self.process_event(event, msg.topic)
                except Exception as e:
                    logger.error("Error processing event", error=str(e), topic=msg.topic)
                    
                    # Try to commit offset even on error to avoid reprocessing
                    try:
                        await self.consumer.commit()
                    except:
                        pass
                    
        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        except Exception as e:
            logger.error("Unexpected error in consumer", error=str(e))
        finally:
            logger.info("Consumer loop ended")
    
    async def process_event(self, event: Dict[str, Any], topic: str):
        """Process a single event (alert or incident)."""
        logger.debug("Processing event", topic=topic, event_id=event.get("alert_id") or event.get("incident_id"))
        
        # In a real implementation, this would:
        # 1. Parse the event
        # 2. Match against playbook triggers
        # 3. Create response actions if triggers match
        # 4. Store in database for approval workflow
        
        logger.debug("Event processed", topic=topic)