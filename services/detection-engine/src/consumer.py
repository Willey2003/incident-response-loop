"""
Event consumer for Detection Engine.
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
from .evaluator import RuleEvaluator
from .publisher import AlertPublisher

logger = structlog.get_logger()


class EventConsumer:
    """Consumes events from Kafka/Redpanda and processes them through the rule evaluator."""
    
    def __init__(self):
        self.consumer: Optional = None
        self.evaluator: Optional = None
        self.publisher: Optional = None
        self.running = False
        self.batch: List[Dict] = []
        self.batch_size = 100
        self.flush_interval = 5  # seconds
        self.last_flush = datetime.utcnow()
    
    def set_dependencies(self, evaluator: 'RuleEvaluator', publisher: 'AlertPublisher'):
        """Set dependencies after initialization."""
        self.evaluator = evaluator
        self.publisher = publisher
    
    async def start(self):
        """Start the consumer."""
        from .kafka import get_consumer
        self.consumer = get_consumer()
        self.running = True
        logger.info("Event consumer started")
    
    async def stop(self):
        """Stop the consumer."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        logger.info("Event consumer stopped")
    
    async def run(self):
        """Main consumer loop."""
        if not self.consumer:
            raise RuntimeError("Consumer not initialized. Call start() first.")
        
        if not self.evaluator or not self.publisher:
            raise RuntimeError("Dependencies not set. Call set_dependencies() first.")
        
        logger.info("Starting event consumption loop")
        
        try:
            async for msg in self.consumer:
                if not self.running:
                    break
                
                try:
                    event = msg.value
                    await self.process_event(event)
                except Exception as e:
                    logger.error("Error processing event", error=str(e), event=msg.value)
                    
                    # Try to commit offset even on error to avoid reprocessing
                    try:
                        await self.consumer.commit()
                    except:
                        pass
                
                # Check if we should flush batch
                await self.maybe_flush_batch()
                    
        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        except KafkaError as e:
            logger.error("Kafka error", error=str(e))
        except Exception as e:
            logger.error("Unexpected error in consumer", error=str(e))
        finally:
            await self.flush_batch()
    
    async def process_event(self, event: Dict[str, Any]):
        """Process a single event through the rule evaluator."""
        start_time = datetime.utcnow()
        
        try:
            # Evaluate rules against event
            results = await self.evaluator.evaluate(event)
            
            # Process matches
            matched_rules = [r for r in results if r.matched]
            
            if matched_rules:
                logger.info("Rules matched", count=len(matched_rules), rule_ids=[r.rule_id for r in matched_rules])
                
                # Generate alerts for matched rules
                for result in matched_rules:
                    if result.matched and result.actions:
                        await self.publisher.publish_alert(
                            rule_id=result.rule_id,
                            rule_name=result.rule_name,
                            event=event,
                            actions=result.actions,
                            matched_conditions=result.matched_conditions,
                        )
            
            # Record metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.debug("Event processed", processing_time_ms=processing_time * 1000)
            
        except Exception as e:
            logger.error("Error evaluating event", error=str(e))
            raise
    
    async def maybe_flush_batch(self):
        """Flush batch if size or time threshold reached."""
        now = datetime.utcnow()
        if len(self.batch) >= self.batch_size or (now - self.last_flush).total_seconds() >= self.flush_interval:
            await self.flush_batch()
    
    async def flush_batch(self):
        """Flush event batch."""
        if not self.batch:
            return
        
        batch = self.batch
        self.batch = []
        self.last_flush = datetime.utcnow()
        
        logger.debug("Flushed event batch", size=len(batch))