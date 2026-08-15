"""
AI Security Copilot models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class AIAnalysisType(str, Enum):
    """Types of AI analysis requests."""
    INCIDENT_SUMMARY = "incident_summary"
    ALERT_TRIAGE = "alert_triage"
    RUNBOOK_RECOMMENDATION = "runbook_recommendation"
    REPORT_GENERATION = "report_generation"
    TIMELINE_SUMMARY = "timeline_summary"
    NATURAL_LANGUAGE_SEARCH = "natural_language_search"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    IMPACT_ASSESSMENT = "impact_assessment"
    THREAT_HUNTING = "threat_hunting"
    COMPLIANCE_CHECK = "compliance_check"


class ConfidenceLevel(str, Enum):
    """AI confidence levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient_evidence"


class Citation(BaseModel):
    """Citation referencing source evidence."""
    model_config = ConfigDict(extra="allow")
    
    citation_id: str
    source_type: str  # alert, incident, evidence, runbook, policy, documentation
    source_id: str
    title: str
    excerpt: str
    timestamp: Optional[str] = None
    relevance_score: Optional[float] = None
    url: Optional[str] = None


class RetrievalResult(BaseModel):
    """Result from vector search retrieval."""
    model_config = ConfigDict(extra="allow")
    
    document_id: str
    content: str
    metadata: Dict[str, any] = Field(default_factory=dict)
    score: float
    citation: Citation


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis."""
    model_config = ConfigDict(extra="allow")
    
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    analysis_type: AIAnalysisType
    
    # Context
    incident_id: Optional[str] = None
    alert_id: Optional[str] = None
    query: Optional[str] = None
    
    # Context data
    context: Dict[str, any] = Field(default_factory=dict)
    evidence_ids: List[str] = Field(default_factory=list)
    
    # Retrieval parameters
    retrieval_limit: int = 10
    retrieval_filters: Dict[str, any] = Field(default_factory=dict)
    rerank: bool = True
    
    # Generation parameters
    max_tokens: int = 2048
    temperature: float = 0.1
    system_prompt_override: Optional[str] = None
    
    # Output format
    output_format: str = "markdown"  # markdown, json, structured
    include_citations: bool = True
    include_confidence: bool = True
    
    # Safety
    require_citations: bool = True
    redact_output: bool = True
    
    # Metadata
    requested_by: str
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None


class AIAnalysisResponse(BaseModel):
    """Response from AI analysis."""
    model_config = ConfigDict(extra="allow")
    
    request_id: str
    response_id: str = Field(default_factory=lambda: str(uuid4()))
    
    # Core response
    analysis_type: AIAnalysisType
    summary: str
    details: str
    recommendations: List[str] = Field(default_factory=list)
    
    # Confidence and evidence
    confidence: ConfidenceLevel = ConfidenceLevel.LOW
    confidence_score: Optional[float] = None
    citations: List[Citation] = Field(default_factory=list)
    evidence_used: List[str] = Field(default_factory=list)
    
    # Structured output
    structured_data: Dict[str, any] = Field(default_factory=dict)
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    
    # Specific fields per analysis type
    triage_assessment: Optional[str] = None  # alert_triage
    investigation_priority: Optional[str] = None  # alert_triage
    investigation_questions: List[str] = Field(default_factory=list)  # alert_triage
    recommended_runbooks: List[Dict[str, any]] = Field(default_factory=list)  # runbook_recommendation
    dry_run_preview: Optional[Dict[str, any]] = None  # runbook_recommendation
    rollback_complexity: Optional[str] = None  # runbook_recommendation
    timeline_events: List[Dict[str, any]] = Field(default_factory=list)  # timeline_summary
    root_cause: Optional[str] = None  # root_cause_analysis
    contributing_factors: List[str] = Field(default_factory=list)  # root_cause_analysis
    impact_scope: Optional[str] = None  # impact_assessment
    affected_systems: List[str] = Field(default_factory=list)  # impact_assessment
    search_results: List[Dict[str, any]] = Field(default_factory=list)  # nl_search
    threat_hypotheses: List[Dict[str, any]] = Field(default_factory=list)  # threat_hunting
    compliance_findings: List[Dict[str, any]] = Field(default_factory=list)  # compliance_check
    
    # Report generation
    report_format: Optional[str] = None
    report_sections: List[str] = Field(default_factory=list)
    
    # Metadata
    model_used: str
    processing_time_ms: int
    tokens_input: int
    tokens_output: int
    tokens_total: int
    
    # Safety
    redacted: bool = True
    redaction_count: int = 0
    insufficient_evidence: bool = False
    safety_warnings: List[str] = Field(default_factory=list)
    
    # Timing
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: int = 0
    
    # Version
    model_version: str
    prompt_version: str


class RetrievalRequest(BaseModel):
    """Request for vector search retrieval."""
    model_config = ConfigDict(extra="allow")
    
    query: str
    collection: str = "security-knowledge"
    limit: int = 10
    filters: Dict[str, any] = Field(default_factory=dict)
    score_threshold: float = 0.7
    with_vectors: bool = False
    with_payload: bool = True


class RetrievalResponse(BaseModel):
    """Response from vector search retrieval."""
    model_config = ConfigDict(extra="allow")
    
    results: List[RetrievalResult] = Field(default_factory=list)
    total_found: int = 0
    query_time_ms: int = 0


class EmbeddingRequest(BaseModel):
    """Request for text embedding generation."""
    model_config = ConfigDict(extra="allow")
    
    texts: List[str]
    model: str = "all-MiniLM-L6-v2"
    batch_size: int = 32
    normalize: bool = True


class EmbeddingResponse(BaseModel):
    """Response with generated embeddings."""
    model_config = ConfigDict(extra="allow")
    
    embeddings: List[List[float]] = Field(default_factory=list)
    model: str
    dimensions: int
    processing_time_ms: int = 0
    token_count: int = 0


class RedactionRequest(BaseModel):
    """Request for text redaction."""
    model_config = ConfigDict(extra="allow")
    
    text: str
    patterns: Optional[List[str]] = None  # custom patterns
    redact_secrets: bool = True
    redact_pii: bool = True
    redact_ips: bool = True
    redact_tokens: bool = True
    custom_patterns: Dict[str, str] = Field(default_factory=dict)


class RedactionResponse(BaseModel):
    """Response with redacted text."""
    model_config = ConfigDict(extra="allow")
    
    original_text: str
    redacted_text: str
    redactions: List[Dict[str, any]] = Field(default_factory=list)
    redaction_count: int = 0