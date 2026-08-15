"""
Knowledge indexer for AI Copilot.
Periodically indexes alerts, incidents, runbooks, and policies into Qdrant.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog

from .config import settings
from .database import get_db_session
from .embedding_service import EmbeddingService
from .retrieval_service import RetrievalService

logger = structlog.get_logger()


class KnowledgeIndexer:
    """Indexes security knowledge into Qdrant for RAG."""
    
    def __init__(self):
        self.embedding_service: Optional = None
        self.retrieval_service: Optional = None
        self.batch_size = settings.INDEX_BATCH_SIZE
        self.interval = settings.INDEX_INTERVAL_SECONDS
        self.running = False
    
    def set_dependencies(self, embedding_service, retrieval_service):
        self.embedding_service = embedding_service
        self.retrieval_service = retrieval_service
    
    async def initialize(self):
        """Initialize the indexer."""
        logger.info("Knowledge indexer initialized")
    
    async def run_periodic_indexing(self):
        """Run periodic indexing loop."""
        self.running = True
        logger.info("Starting periodic indexing", interval_seconds=self.interval)
        
        while self.running:
            try:
                await self.run_indexing_cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Indexing cycle failed", error=str(e))
            
            try:
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
        
        logger.info("Periodic indexing stopped")
    
    async def run_indexing_cycle(self):
        """Run a single indexing cycle."""
        start = time.time()
        logger.info("Starting indexing cycle")
        
        total_indexed = 0
        
        # Index recent alerts
        total_indexed += await self._index_alerts()
        
        # Index recent incidents
        total_indexed += await self._index_incidents()
        
        # Index runbooks
        total_indexed += await self._index_runbooks()
        
        # Index policies
        total_indexed += await self._index_policies()
        
        # Index documentation
        total_indexed += await self._index_documentation()
        
        elapsed = time.time() - start
        logger.info("Indexing cycle completed", 
                   indexed=total_indexed, 
                   elapsed_seconds=elapsed)
    
    async def _index_alerts(self) -> int:
        """Index recent alerts."""
        try:
            async with get_db_session() as session:
                from sqlalchemy import text
                
                query = text("""
                    SELECT alert_id, rule_id, rule_name, title, description, severity,
                           confidence, mitre_techniques, mitre_tactics, affected_asset_ids,
                           affected_namespaces, affected_pods, affected_nodes, evidence,
                           status, first_seen, last_seen
                    FROM detection.alerts
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    AND alert_id NOT IN (
                        SELECT source_id FROM assets.knowledge_base WHERE source_type = 'alert'
                    )
                    LIMIT :limit
                """)
                
                result = await session.execute(text("""
                    SELECT alert_id, rule_id, rule_name, title, description, severity,
                           confidence, mitre_techniques, mitre_tactics, affected_asset_ids,
                           affected_namespaces, affected_pods, affected_nodes, evidence,
                           status, first_seen, last_seen
                    FROM detection.alerts
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    LIMIT :limit
                """), {"limit": self.batch_size})
                
                alerts = result.fetchall()
                
                if not alerts:
                    return 0
                
                documents = []
                for alert in alerts:
                    doc = {
                        "source_type": "alert",
                        "source_id": str(alert.alert_id),
                        "title": f"Alert: {alert.title}",
                        "content": f"{alert.description}\n\nSeverity: {alert.severity}\nConfidence: {alert.confidence}\nMITRE: {alert.mitre_techniques}",
                        "metadata": {
                            "alert_id": str(alert.alert_id),
                            "rule_id": str(alert.rule_id) if alert.rule_id else None,
                            "rule_name": alert.rule_name,
                            "severity": alert.severity,
                            "confidence": float(alert.confidence) if alert.confidence else 0,
                            "mitre_techniques": alert.mitre_techniques or [],
                            "mitre_tactics": alert.mitre_tactics or [],
                            "status": alert.status,
                        },
                        "created_at": alert.first_seen.isoformat() if alert.first_seen else None,
                    }
                    documents.append(doc)
                
                if documents:
                    await self.retrieval_service.index_batch(documents)
                    logger.info("Indexed alerts", count=len(documents))
                    return len(documents)
                
        except Exception as e:
            logger.error("Failed to index alerts", error=str(e))
        
        return 0
    
    async def _index_incidents(self) -> int:
        """Index recent incidents."""
        try:
            async with get_db_session() as session:
                from sqlalchemy import text
                
                result = await session.execute(text("""
                    SELECT incident_id, title, description, severity, status, phase,
                           mitre_techniques, mitre_tactics, alert_ids, alert_count,
                           affected_asset_ids, affected_namespaces, affected_pods,
                           affected_nodes, affected_services, evidence_ids, evidence_count,
                           ai_summary, ai_root_cause, ai_impact_assessment, ai_lessons_learned,
                           created_at, updated_at
                    FROM detection.incidents
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    LIMIT :limit
                """), {"limit": self.batch_size})
                
                incidents = result.fetchall()
                
                if not incidents:
                    return 0
                
                documents = []
                for incident in incidents:
                    doc = {
                        "source_type": "incident",
                        "source_id": str(incident.incident_id),
                        "title": f"Incident: {incident.title}",
                        "content": f"{incident.description}\n\nSeverity: {incident.severity}\nStatus: {incident.status}\nPhase: {incident.phase}\nMITRE: {incident.mitre_techniques}",
                        "metadata": {
                            "incident_id": str(incident.incident_id),
                            "severity": incident.severity,
                            "status": incident.status,
                            "phase": incident.phase,
                            "mitre_techniques": incident.mitre_techniques or [],
                            "mitre_tactics": incident.mitre_tactics or [],
                            "alert_count": incident.alert_count,
                        },
                        "created_at": incident.created_at.isoformat() if incident.created_at else None,
                    }
                    documents.append(doc)
                
                if documents:
                    await self.retrieval_service.index_batch(documents)
                    logger.info("Indexed incidents", count=len(documents))
                    return len(documents)
                
        except Exception as e:
            logger.error("Failed to index incidents", error=str(e))
        
        return 0
    
    async def _index_runbooks(self) -> int:
        """Index runbooks."""
        try:
            async with get_db_session() as session:
                from sqlalchemy import text
                
                result = await session.execute(text("""
                    SELECT id, name, description, trigger_conditions, steps,
                           severity, mitre_techniques, created_at, updated_at
                    FROM assets.runbooks
                    WHERE updated_at > NOW() - INTERVAL '1 hour'
                    LIMIT :limit
                """), {"limit": self.batch_size})
                
                runbooks = result.fetchall()
                
                if not runbooks:
                    return 0
                
                documents = []
                for rb in runbooks:
                    doc = {
                        "source_type": "runbook",
                        "source_id": str(rb.id),
                        "title": f"Runbook: {rb.name}",
                        "content": f"{rb.description}\n\nSteps: {rb.steps}\nSeverity: {rb.severity}\nMITRE: {rb.mitre_techniques}",
                        "metadata": {
                            "runbook_id": str(rb.id),
                            "severity": rb.severity,
                            "mitre_techniques": rb.mitre_techniques or [],
                        },
                        "created_at": rb.created_at.isoformat() if rb.created_at else None,
                    }
                    documents.append(doc)
                
                if documents:
                    await self.retrieval_service.index_batch(documents)
                    logger.info("Indexed runbooks", count=len(documents))
                    return len(documents)
                
        except Exception as e:
            logger.error("Failed to index runbooks", error=str(e))
        
        return 0
    
    async def _index_policies(self) -> int:
        """Index policies."""
        try:
            async with get_db_session() as session:
                from sqlalchemy import text
                
                result = await session.execute(text("""
                    SELECT id, name, description, policy_type, policy_yaml,
                           namespace, enabled, created_at, updated_at
                    FROM assets.policies
                    WHERE updated_at > NOW() - INTERVAL '1 hour'
                    LIMIT :limit
                """), {"limit": self.batch_size})
                
                policies = result.fetchall()
                
                if not policies:
                    return 0
                
                documents = []
                for policy in policies:
                    doc = {
                        "source_type": "policy",
                        "source_id": str(policy.id),
                        "title": f"Policy: {policy.name}",
                        "content": f"{policy.description}\n\nType: {policy.policy_type}\nPolicy: {policy.policy_yaml}",
                        "metadata": {
                            "policy_id": str(policy.id),
                            "policy_type": policy.policy_type,
                            "namespace": policy.namespace,
                        },
                        "created_at": policy.created_at.isoformat() if policy.created_at else None,
                    }
                    documents.append(doc)
                
                if documents:
                    await self.retrieval_service.index_batch(documents)
                    logger.info("Indexed policies", count=len(documents))
                    return len(documents)
                
        except Exception as e:
            logger.error("Failed to index policies", error=str(e))
        
        return 0
    
    async def _index_documentation(self) -> int:
        """Index platform documentation."""
        # This would index markdown files from docs/ directory
        # For now, return 0 as placeholder
        return 0
    
    def stop(self):
        """Stop the indexer."""
        self.running = False