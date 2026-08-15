"""
Rule evaluator for Detection Engine.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config import settings
from .rules_loader import load_rules
from .database import get_db_session
from .kafka import get_producer

from aegisforge_policy.rules import DetectionRule, RuleSet
from aegisforge_policy.engine import PolicyEngine

import structlog

logger = structlog.get_logger()


class RuleEvaluator:
    """Evaluates detection rules against events."""
    
    def __init__(self):
        self.engine: Optional[PolicyEngine] = None
        self.rule_cache: Dict[str, dict] = {}
        self.last_reload = datetime.utcnow()
        self.reload_interval = settings.DETECTION_RULE_RELOAD_INTERVAL
    
    async def initialize(self):
        """Initialize the evaluator with rules."""
        self.engine = PolicyEngine()
        await self.reload_rules()
        logger.info("Rule evaluator initialized")
    
    async def reload_rules(self):
        """Reload rules from disk/database."""
        start = time.time()
        
        try:
            rule_set = await load_rules()
            engine = PolicyEngine()
            engine.register_rule_set(rule_set)
            self.engine = engine
            self.last_reload = datetime.utcnow()
            
            logger.info("Rules reloaded", rule_count=len(rule_set.rules), duration_ms=(time.time() - start) * 1000)
        except Exception as e:
            logger.error("Failed to reload rules", error=str(e))
            raise
    
    async def evaluate(self, event: Dict[str, Any]) -> List[dict]:
        """Evaluate event against all rules."""
        if not self.engine:
            raise RuntimeError("Evaluator not initialized")
        
        # Check if reload needed
        if (datetime.utcnow() - self.last_reload).total_seconds() > self.reload_interval:
            await self.reload_rules()
        
        start_time = time.time()
        
        try:
            # Create evaluation context
            context = {
                "event": event,
                "timestamp": datetime.utcnow(),
            }
            
            # Evaluate
            results = self.engine.evaluate_event(event)
            
            # Convert to standardized format
            results_list = []
            for result in results:
                rule = self.engine.rule_sets.get("default", None)
                if rule:
                    rule_obj = next((r for r in rule.rules if r.rule_id == result.rule_id), None)
                    if rule_obj:
                        results_list.append({
                            "rule_id": result.rule_id,
                            "rule_name": result.rule_name,
                            "matched": result.matched,
                            "matched_conditions": result.matched_conditions,
                            "actions": result.actions,
                            "execution_time_ms": result.execution_time_ms,
                        })
            
            elapsed = (time.time() - start_time) * 1000
            logger.debug("Rule evaluation completed", 
                        event_type=event.get("event_type", "unknown"),
                        results_count=len(results_list),
                        duration_ms=elapsed)
            
            return results_list
            
        except Exception as e:
            logger.error("Rule evaluation failed", error=str(e))
            raise
    
    async def check_reload_needed(self):
        """Check if rules need to be reloaded."""
        if (datetime.utcnow() - self.last_reload).total_seconds() > self.reload_interval:
            await self.reload_rules()


class StreamingRuleEvaluator(RuleEvaluator):
    """Extended evaluator with streaming/batch support."""
    
    def __init__(self):
        super().__init__()
        self.pending_evaluations: asyncio.Queue = asyncio.Queue()
        self.results_future: Dict[str, asyncio.Future] = {}
    
    async def evaluate_batch(self, events: List[Dict]) -> List[List[dict]]:
        """Evaluate a batch of events concurrently."""
        tasks = [self.evaluate(event) for event in events]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        results_list = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("Batch evaluation error", error=str(result))
                results_list.append([])
            else:
                results_list.append(result)
        
        return results_list
    
    async def evaluate_async(self, event: Dict) -> asyncio.Future:
        """Submit event for async evaluation."""
        future = asyncio.Future()
        eval_id = f"{time.time()}:{id(event)}"
        self.results_future[eval_id] = future
        await self.pending_evaluations.put((eval_id, event))
        return future
    
    async def process_queue(self):
        """Process evaluation queue."""
        while True:
            try:
                eval_id, event = await self.pending_evaluations.get()
                future = self.results_future.pop(eval_id, None)
                
                try:
                    result = await self.evaluate(event)
                    if future:
                        future.set_result(result)
                except Exception as e:
                    if future:
                        future.set_exception(e)
            except Exception as e:
                logger.error("Queue processing error", error=str(e))