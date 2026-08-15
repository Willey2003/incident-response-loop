"""
Incident investigation routes for AI Copilot.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from ..auth import get_current_user, require_analyst
from ..config import settings

router = APIRouter()


class AIIncidentSummaryRequest(BaseModel):
    incident_id: str
    max_tokens: int = 2048
    temperature: float = 0.1
    include_citations: bool = True


class AIIncidentSummaryResponse(BaseModel):
    request_id: str
    response_id: str
    summary: str
    details: str
    recommendations: List[str] = []
    confidence: str
    confidence_score: Optional[float] = None
    citations: List[Dict] = []
    evidence_used: List[str] = []
    structured_data: Dict = {}
    mitre_techniques: List[str] = []
    mitre_tactics: List[str] = []
    model_used: str
    processing_time_ms: int
    tokens_input: int
    tokens_output: int
    tokens_total: int
    redacted: bool
    redaction_count: int
    insufficient_evidence: bool
    safety_warnings: List[str] = []


@router.post("/investigate/incident", response_model=AIIncidentSummaryResponse)
async def investigate_incident(
    request: AIIncidentSummaryRequest,
    current_user = Depends(require_analyst),
):
    """Full incident investigation with AI analysis."""
    # In real implementation, this would call the AI Copilot service
    return AIIncidentSummaryResponse(
        request_id="req-" + str(datetime.utcnow().timestamp()),
        response_id="resp-" + str(datetime.utcnow().timestamp()),
        summary=f"AI-generated summary for incident {request.incident_id}",
        details=f"Detailed analysis of incident {request.incident_id} based on available evidence.",
        recommendations=[
            "Review associated alerts for common patterns",
            "Check for lateral movement indicators",
            "Verify containment actions taken",
        ],
        confidence="high",
        confidence_score=0.85,
        citations=[],
        evidence_used=[],
        structured_data={},
        mitre_techniques=["T1021.001", "T1048.003"],
        mitre_tactics=["TA0008", "TA0010"],
        model_used=settings.OLLAMA_MODEL,
        processing_time_ms=1500,
        tokens_input=500,
        tokens_output=300,
        tokens_total=800,
        redacted=True,
        redaction_count=2,
        insufficient_evidence=False,
        safety_warnings=[],
    )