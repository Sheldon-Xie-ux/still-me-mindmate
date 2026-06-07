from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    message: str


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    category: str
    priority_score: float
    priority_label: str
    priority_reason: str
    status: str
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class FocusRecommendation(BaseModel):
    recommended_task_id: Optional[int]
    summary: str


class RhythmPayload(BaseModel):
    focus_minutes_today: int
    completed_tasks_today: int
    suggestion: str


class SafetyPayload(BaseModel):
    state: str
    message: Optional[str]


class CurrentPriorityPayload(BaseModel):
    title: Optional[str] = None
    reason: str


class NextActionPayload(BaseModel):
    label: str
    detail: str


class SystemObservationPayload(BaseModel):
    suggestion: str
    safety_state: str
    message: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    tasks: list[TaskOut]
    focus: FocusRecommendation
    rhythm: RhythmPayload
    safety: SafetyPayload
    current_priority: CurrentPriorityPayload
    next_action: NextActionPayload
    system_observation: SystemObservationPayload


class ResearchQuestionOut(BaseModel):
    id: int
    title: str
    theme: str
    description: str
    status: str
    priority: int
    created_at: datetime
    updated_at: datetime


class ResearchQuestionList(BaseModel):
    questions: list[ResearchQuestionOut]


class ResearchRunCreate(BaseModel):
    question_id: int
    mode: str = "fixture"


class ResearchRunOut(BaseModel):
    id: int
    question_id: int
    status: str
    query_plan: str
    sources_examined: int
    evidence_created: int
    hypotheses_created: int
    hypotheses_updated: int
    kept_summary: str
    rejected_summary: str
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class ResearchRunCreateResponse(BaseModel):
    run_id: int
    status: str
    evidence_created: int
    hypotheses_created: int
    hypotheses_updated: int


class SourceDocumentOut(BaseModel):
    id: int
    url: str
    title: str
    authors: str
    publisher: str
    published_at: Optional[datetime] = None
    language: str
    source_type: str
    snippet: str
    credibility_score: float
    retrieved_at: datetime


class EvidenceCardOut(BaseModel):
    id: int
    question_id: int
    source_document_id: int
    source: SourceDocumentOut
    claim: str
    summary: str
    stance: str
    evidence_strength: float
    relevance_score: float
    risk_domain: str
    limitations: str
    created_at: datetime


class EvidenceCardList(BaseModel):
    evidence: list[EvidenceCardOut]


class HypothesisOut(BaseModel):
    id: int
    title: str
    statement: str
    theme: str
    status: str
    evidence_score: float
    product_value_score: float
    engineering_feasibility_score: float
    risk_sensitivity_score: float
    overall_score: float
    rationale: str
    created_at: datetime
    updated_at: datetime


class HypothesisList(BaseModel):
    hypotheses: list[HypothesisOut]


class ResearchBrief(BaseModel):
    title: str
    summary: str
    strongest_claims: list[str]
    open_questions: list[str]
    design_implications: list[str]
    expert_review_queue: list[str]


class KnowledgeExportResponse(BaseModel):
    root: str
    files_written: list[str]
