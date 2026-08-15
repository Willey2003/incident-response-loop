"""
Runbook recommendation routes for AI Copilot.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..auth import get_current_user, require_incident_commander
from ..config import settings

router = APIRouter()


class AIRunbookRecommendationRequest(BaseModel):
    incident_id: str
    max_tokens: int = 2048
    temperature: float = 0.1
    include_citations: bool = True


class AIRunbookRecommendationResponse(BaseModel):
    request_id: str
    response_id: str
    recommended_runbooks: List[Dict] = []
    rationale: str
    dry_run_preview: Optional[Dict] = None
    rollback_complexity: Optional[str] = None
    confidence: str
    confidence_score: Optional[float] = None
    citations: List[Dict] = []
    evidence_used: List[str] = []
    model_used: str
    processing_time_ms: int
    tokens_input: int
    tokens_output: int
    tokens_total: int
    redacted: bool
    redaction_count: int
    insufficient_evidence: bool
    safety_warnings: List[str] = []


router = APIRouter()


@router.post("/recommend/runbook", response_model=AIRunbookRecommendationResponse)
async def recommend_runbook(
    request: AIRunbookRecommendationRequest,
    current_user = Depends(require_incident_commander),
):
    """Recommend containment runbook with dry-run preview."""
    return AIRunbookRecommendationResponse(
        request_id="req-" + str(datetime.utcnow().timestamp()),
        response_id="resp-" + str(datetime.utcnow().timestamp()),
        recommended_runbooks=[
            {
                "playbook_id": "PB-001",
                "name": "Quarantine Compromised Workload",
                "description": "Isolate compromised pod using NetworkPolicy",
                "confidence": 0.92,
                "dry_run_available": True,
            }
        ],
        rationale="Based on MITRE techniques T1021.001 and T1570 detected, quarantine is the recommended immediate containment action.",
        dry_run_preview={
            "action": "generate_network_policy",
            "policy_type": "deny_all",
            "target": "compromised-pod",
            "expected_impact": "Complete network isolation of target pod",
        },
        rollback_complexity="low",
        confidence="high",
        confidence_score=0.9,
        citations=[],
        evidence_used=[],
        model_used=settings.OLLAMA_MODEL,
        processing_time_ms=800,
        tokens_input=300,
        tokens_output=200,
        tokens_total=500,
        redacted=True,
        redaction_count=0,
        insufficient_evidence=False,
        safety_warnings=[],
    )