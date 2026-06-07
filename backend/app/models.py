from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, unique=True)
    description: Optional[str] = None
    category: str = "general"
    priority_score: float = 0
    priority_label: str = "medium"
    priority_reason: str = ""
    status: str = "pending"
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class FocusSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(index=True, nullable=False)
    duration_minutes: int = Field(nullable=False)
    status: str = Field(default="active", nullable=False)
    started_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    ended_at: Optional[datetime] = None


class AnalyticsSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date_bucket: date = Field(default_factory=date.today, nullable=False)
    daily_message_count: int = Field(default=0, nullable=False)
    focus_minutes_today: int = Field(default=0, nullable=False)
    uninterrupted_minutes: int = Field(default=0, nullable=False)
    last_break_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ResearchQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, unique=True)
    theme: str = Field(index=True, nullable=False)
    description: str = ""
    status: str = Field(default="queued", index=True, nullable=False)
    priority: int = Field(default=3, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class SourceDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True, unique=True)
    title: str
    authors: str = ""
    publisher: str = ""
    published_at: Optional[datetime] = None
    language: str = Field(default="en", nullable=False)
    source_type: str = Field(default="unknown", nullable=False)
    snippet: str = ""
    credibility_score: float = Field(default=50, nullable=False)
    retrieved_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ResearchRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(index=True, nullable=False)
    status: str = Field(default="pending", index=True, nullable=False)
    query_plan: str = ""
    sources_examined: int = 0
    evidence_created: int = 0
    hypotheses_created: int = 0
    hypotheses_updated: int = 0
    kept_summary: str = ""
    rejected_summary: str = ""
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = None


class EvidenceCard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(index=True, nullable=False)
    source_document_id: int = Field(index=True, nullable=False)
    claim: str
    summary: str
    stance: str = Field(default="context", nullable=False)
    evidence_strength: float = Field(default=50, nullable=False)
    relevance_score: float = Field(default=50, nullable=False)
    risk_domain: str = Field(default="judgment", nullable=False)
    limitations: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Hypothesis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, unique=True)
    statement: str
    theme: str = Field(index=True, nullable=False)
    status: str = Field(default="candidate", index=True, nullable=False)
    evidence_score: float = Field(default=0, nullable=False)
    product_value_score: float = Field(default=0, nullable=False)
    engineering_feasibility_score: float = Field(default=0, nullable=False)
    risk_sensitivity_score: float = Field(default=0, nullable=False)
    overall_score: float = Field(default=0, nullable=False)
    rationale: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class DesignPrinciple(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hypothesis_id: int = Field(index=True, nullable=False)
    title: str
    principle: str
    product_pattern: str
    applicability: str
    evidence_summary: str
    caution: str
    status: str = Field(default="draft", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
