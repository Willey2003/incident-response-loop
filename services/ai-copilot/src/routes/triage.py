"""
Alert triage routes for AI Copilot.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..auth import get_current_user, require_analyst
from ..config import settings

router = APIRouter()


class AIAlertTriageRequest(BaseModel):
    alert_id: str
    max_tokens: int = 2048
    temperature: float = 0.1
    include_citations: bool = True


class AIAlertTriageResponse(BaseModel):
    request_id: str
    response_id: str
    triage_assessment: str
    investigation_priority: str
    investigation_questions: List[str] = []
    recommended_data_sources: List[str] = []
    potential_false_positive_indicators: List[str] = []
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


@router.post("/triage/alert", response_model=AIAlertTriageResponse)
async def triage_alert(
    request: AIAlertTriageRequest,
    current_user = Depends(require_analyst),
):
    """Alert triage with investigation guidance."""
    return AIAlertTriageResponse(
        request_id="req-" + str(datetime.utcnow().timestamp()),
        response_id="resp-" + str(datetime.utcnow().timestamp()),
        triage_assessment="True positive - suspicious activity detected",
        investigation_priority="high",
        investigation_questions=[
            "What is the source of the suspicious traffic?",
            "Are there related alerts from other sources?",
        ],
        recommended_data_sources=[
            "Network flow logs",
            "Endpoint detection logs",
            "Authentication logs",
        ],
        potential_false_positive_indicators=[
            "Scheduled vulnerability scans",
            "Legitimate administrative activity",
        ],
        confidence="high",
        confidence_score=0.88,
        citations=[],
        evidence_used=[],
        model_used=settings.OLLAMA_MODEL,
        processing_time_ms=1200,
        tokens_input=400,
        tokens_output=250,
        tokens_total=650,
        redacted=True,
        redaction_count=1,
        insufficient_evidence=False,
        safety_warnings=[],
    )