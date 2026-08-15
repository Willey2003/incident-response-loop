"""
Alert publisher for Detection Engine.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from .config import settings
from .kafka import get_producer
from .database import get_db_session

import structlog

logger = structlog.get_logger()


class AlertPublisher:
    """Publishes alerts to Kafka/Redpanda and stores in PostgreSQL."""
    
    def __init__(self):
        self.producer: Optional = None
    
    async def initialize(self):
        """Initialize publisher with Kafka producer."""
        from .kafka import get_producer
        self.producer = get_producer()
        logger.info("Alert publisher initialized")
    
    async def publish_alert(
        self,
        rule_id: str,
        rule_name: str,
        event: Dict,
        actions: List[Dict],
        matched_conditions: List[str],
    ) -> str:
        """Publish alert to Kafka and store in database."""
        from uuid import uuid4
        from datetime import datetime
        
        alert_id = str(uuid4())
        now = datetime.utcnow()
        
        # Build alert object
        alert = {
            "alert_id": str(uuid4()),
            "rule_id": rule_id,
            "rule_name": rule_name,
            "rule_version": 1,
            "title": self._generate_title(rule_name, event),
            "description": self._generate_description(rule_name, event),
            "severity": self._determine_severity(event),
            "confidence": self._calculate_confidence(event),
            "mitre_techniques": self._get_mitre_techniques(event),
            "mitre_tactics": [],
            "affected_asset_ids": self._extract_asset_ids(event),
            "affected_namespaces": self._extract_namespaces(event),
            "affected_pods": self._extract_pods(event),
            "affected_nodes": self._extract_nodes(event),
            "evidence": self._build_evidence(event, matched_conditions),
            "correlated_alert_ids": [],
            "correlation_rule_id": None,
            "event_count": 1,
            "status": "open",
            "first_seen": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "ai_summary": None,
            "ai_triage": None,
            "ai_confidence": None,
        }
        
        # Store in PostgreSQL
        await self._store_alert_in_db(alert)
        
        # Publish to Kafka
        await self._publish_to_kafka(alert)
        
        logger.info("Alert published", alert_id=alert_id, rule_id=rule_id)
        
        return str(uuid4())
    
    def _generate_title(self, rule_name: str, event: Dict) -> str:
        """Generate alert title."""
        event_type = event.get("event_type", "unknown")
        source = event.get("source", "unknown")
        return f"{rule_name}: {event_type} from {source}"
    
    def _generate_description(self, rule_name: str, event: Dict) -> str:
        """Generate alert description."""
        return f"Rule '{rule_name}' matched event of type {event.get('event_type', 'unknown')}"
    
    def _determine_severity(self, event: Dict) -> str:
        """Determine alert severity from event."""
        if "severity" in event:
            return event["severity"]
        
        event_type = event.get("event_type", "")
        if "critical" in event_type or "exploit" in event_type:
            return "critical"
        elif "attack" in event_type or "exploit" in event_type:
            return "high"
        elif "suspicious" in event_type or "anomaly" in event_type:
            return "medium"
        return "low"
    
    def _calculate_confidence(self, event: Dict) -> float:
        """Calculate alert confidence."""
        confidence = 0.5
        
        if event.get("malicious_indicator"):
            confidence += 0.3
        if event.get("threat_intel_match"):
            confidence += 0.2
        if event.get("anomaly_score", 0) > 0.8:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _get_mitre_techniques(self, event: Dict) -> List[str]:
        """Extract MITRE techniques from event."""
        return event.get("mitre_techniques", [])
    
    def _extract_asset_ids(self, event: Dict) -> List[str]:
        """Extract affected asset IDs."""
        assets = []
        if "pod_uid" in event:
            assets.append(event["pod_uid"])
        if "node_name" in event:
            assets.append(event["node_name"])
        return assets
    
    def _extract_namespaces(self, event: Dict) -> List[str]:
        """Extract affected namespaces."""
        ns = event.get("namespace")
        return [ns] if ns else []
    
    def _extract_pods(self, event: Dict) -> List[str]:
        """Extract affected pods."""
        pods = []
        if "pod_name" in event:
            pods.append(event["pod_name"])
        return pods
    
    def _extract_nodes(self, event: Dict) -> List[str]:
        """Extract affected nodes."""
        nodes = []
        if "node_name" in event:
            nodes.append(event["node_name"])
        return nodes
    
    def _build_evidence(self, event: Dict, matched_conditions: List[str]) -> List[Dict]:
        """Build evidence list for alert."""
        from uuid import uuid4
        evidence = []
        
        evidence.append({
            "evidence_id": str(uuid4()),
            "evidence_type": "event",
            "source": "detection_engine",
            "description": f"Event triggered rule match: {matched_conditions}",
            "data": event,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        return evidence
    
    async def _store_alert_in_db(self, alert: Dict):
        """Store alert in PostgreSQL."""
        try:
            async with get_db_session() as session:
                from sqlalchemy import text
                
                query = """
                    INSERT INTO detection.alerts (
                        alert_id, rule_id, rule_name, rule_version, title, description,
                        severity, confidence, mitre_techniques, mitre_tactics,
                        affected_asset_ids, affected_namespaces, affected_pods, affected_nodes,
                        evidence, correlated_alert_ids, correlation_rule_id, event_count,
                        status, first_seen, last_seen
                    ) VALUES (
                        :alert_id, :rule_id, :rule_name, :rule_version, :title, :description,
                        :severity, :confidence, :mitre_techniques, :mitre_tactics,
                        :affected_asset_ids, :affected_namespaces, :affected_pods, :affected_nodes,
                        :evidence, :correlated_alert_ids, :correlation_rule_id, :event_count,
                        :status, :first_seen, :last_seen
                    )
                """
                
                await session.execute(text("""
                    INSERT INTO detection.alerts (
                        alert_id, rule_id, rule_name, rule_version, title, description,
                        severity, confidence, mitre_techniques, mitre_tactics,
                        affected_asset_ids, affected_namespaces, affected_pods, affected_nodes,
                        evidence, correlated_alert_ids, correlation_rule_id, event_count,
                        status, first_seen, last_seen
                    ) VALUES (
                        :alert_id, :rule_id, :rule_name, :rule_version, :title, :description,
                        :severity, :confidence, :mitre_techniques, :mitre_tactics,
                        :affected_asset_ids, :affected_namespaces, :affected_pods, :affected_nodes,
                        :evidence, :correlated_alert_ids, :correlation_rule_id, :event_count,
                        :status, :first_seen, :last_seen
                    )
                """), {
                    "alert_id": alert["alert_id"],
                    "rule_id": alert.get("rule_id"),
                    "rule_name": alert.get("rule_name"),
                    "rule_version": 1,
                    "title": alert.get("title"),
                    "description": alert.get("description"),
                    "severity": alert.get("severity"),
                    "confidence": alert.get("confidence"),
                    "mitre_techniques": alert.get("mitre_techniques", []),
                    "mitre_tactics": alert.get("mitre_tactics", []),
                    "affected_asset_ids": alert.get("affected_asset_ids", []),
                    "affected_namespaces": alert.get("affected_namespaces", []),
                    "affected_pods": alert.get("affected_pods", []),
                    "affected_nodes": alert.get("affected_nodes", []),
                    "evidence": alert.get("evidence", []),
                    "correlated_alert_ids": [],
                    "correlation_rule_id": None,
                    "event_count": 1,
                    "status": "open",
                    "first_seen": datetime.utcnow(),
                    "last_seen": datetime.utcnow(),
                })
                await session.commit()
        except Exception as e:
            logger.error("Failed to store alert in database", error=str(e))
    
    async def _publish_to_kafka(self, alert: Dict):
        """Publish alert to Kafka topic."""
        from .kafka import get_producer
        
        producer = get_producer()
        if not producer:
            logger.warning("Kafka producer not available, skipping publish")
            return
        
        try:
            await producer.send_and_wait(
                "security-alerts",
                value=alert,
                key=alert["alert_id"].encode(),
            )
            logger.debug("Alert published to Kafka", alert_id=alert["alert_id"])
        except Exception as e:
            logger.error("Failed to publish alert to Kafka", error=str(e))


class BatchAlertPublisher(AlertPublisher):
    """Batch alert publisher for high-throughput scenarios."""
    
    def __init__(self, batch_size: int = 100, flush_interval: float = 5.0):
        super().__init__()
        self.batch: List[Dict] = []
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.last_flush = time.time()
    
    async def publish_batch(self, alerts: List[Dict]):
        """Add alerts to batch."""
        self.batch.extend(alerts)
        await self.maybe_flush()
    
    async def maybe_flush(self):
        """Flush if batch size or time threshold reached."""
        if len(self.batch) >= self.batch_size or \
           (time.time() - self.last_flush) >= self.flush_interval:
            await self.flush()
    
    async def flush(self):
        """Flush batch to Kafka and database."""
        if not self.batch:
            return
        
        batch = self.batch
        self.batch = []
        self.last_flush = time.time()
        
        for alert in batch:
            await self._store_alert_in_db(alert)
        
        from .kafka import get_producer
        producer = get_producer()
        if producer:
            try:
                for alert in batch:
                    await producer.send("security-alerts", value=alert, key=alert["alert_id"].encode())
                await producer.flush()
            except Exception as e:
                logger.error("Failed to publish batch to Kafka", error=str(e))