# MindMate AutoResearch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first working MindMate AutoResearch loop: seeded research questions, fixture-backed research runs, source-linked evidence cards, scored hypotheses, a research brief endpoint, and a Research Lab UI inside the existing HarmonyMind app.

**Architecture:** Add focused SQLModel tables and Pydantic schemas for research artifacts, then implement a deterministic fixture-backed research service before adding any live search. Expose a small FastAPI surface for questions, runs, evidence, hypotheses, and brief data. Add a React Research Lab panel that can run one research cycle and inspect the generated artifacts.

**Tech Stack:** FastAPI, SQLModel, SQLite, pytest, React, TypeScript, Vite, Vitest, Testing Library

---

## File Structure

- Create `backend/app/services/research_fixtures.py`
  - Owns deterministic seed questions and fixture source/evidence/hypothesis data.
- Create `backend/app/services/research_service.py`
  - Owns research question seeding, run orchestration, evidence creation, hypothesis scoring, and brief assembly.
- Modify `backend/app/models.py`
  - Adds `ResearchQuestion`, `SourceDocument`, `EvidenceCard`, `Hypothesis`, `ResearchRun`, and `DesignPrinciple`.
- Modify `backend/app/schemas.py`
  - Adds API input/output schemas for Research Lab.
- Modify `backend/app/main.py`
  - Adds `/api/research/*` endpoints.
- Create `backend/tests/test_research_flow.py`
  - Covers seeded questions, fixture run, evidence cards, ranked hypotheses, and brief output.
- Modify `frontend/src/types.ts`
  - Adds Research Lab TypeScript types.
- Modify `frontend/src/lib/api.ts`
  - Adds Research Lab API functions.
- Create `frontend/src/components/ResearchLab.tsx`
  - Owns the full Research Lab UI surface.
- Modify `frontend/src/App.tsx`
  - Adds a simple product mode switch between Agent Workspace and Research Lab.
- Modify `frontend/src/styles.css`
  - Adds dense Research Lab layout and card styling.
- Create `frontend/src/test/research-lab.test.tsx`
  - Covers rendering the lab, starting a fixture run, and displaying evidence/hypotheses/brief.

This workspace is not a git repository. Commit steps are replaced by checkpoint notes and verification commands.

---

### Task 1: Backend Research Models and Schemas

**Files:**
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Create: `backend/tests/test_research_flow.py`

- [ ] **Step 1: Write the failing backend schema/model test**

Add this test file:

```python
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session

from app.db import engine, init_db
from app.main import app
from app.models import (
    DesignPrinciple,
    EvidenceCard,
    Hypothesis,
    ResearchQuestion,
    ResearchRun,
    SourceDocument,
)


def clear_research_tables() -> None:
    init_db()
    with Session(engine) as session:
        for model in (
            DesignPrinciple,
            EvidenceCard,
            Hypothesis,
            ResearchRun,
            SourceDocument,
            ResearchQuestion,
        ):
            session.exec(delete(model))
        session.commit()


def test_research_questions_are_seeded_and_listed():
    clear_research_tables()

    with TestClient(app) as client:
        response = client.get("/api/research/questions")

    assert response.status_code == 200
    payload = response.json()

    assert len(payload["questions"]) >= 10
    first_question = payload["questions"][0]
    assert set(first_question) == {
        "id",
        "title",
        "theme",
        "description",
        "status",
        "priority",
        "created_at",
        "updated_at",
    }
    assert first_question["status"] == "queued"
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_research_flow.py::test_research_questions_are_seeded_and_listed -v
```

Expected: FAIL because `ResearchQuestion` and `/api/research/questions` do not exist.

- [ ] **Step 3: Add research models**

Add these classes to `backend/app/models.py` after `AnalyticsSnapshot`:

```python
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
```

- [ ] **Step 4: Add research schemas**

Add these classes to `backend/app/schemas.py` after `ChatResponse`:

```python
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
```

- [ ] **Step 5: Run test to verify it still fails at missing route**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_research_flow.py::test_research_questions_are_seeded_and_listed -v
```

Expected: FAIL with 404 for `/api/research/questions`.

---

### Task 2: Seed Questions and List Endpoint

**Files:**
- Create: `backend/app/services/research_fixtures.py`
- Create: `backend/app/services/research_service.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_research_flow.py`

- [ ] **Step 1: Add seed fixture data**

Create `backend/app/services/research_fixtures.py`:

```python
SEED_RESEARCH_QUESTIONS = [
    {
        "title": "Does AI writing assistance reduce independent argument formation in students?",
        "theme": "education",
        "description": "Study whether AI-generated drafts change how students form claims, evidence, and reasoning.",
        "priority": 5,
    },
    {
        "title": "When does AI summarization improve learning, and when does it reduce deep reading?",
        "theme": "attention",
        "description": "Compare productive summarization support with shallow reading and skipped source inspection.",
        "priority": 5,
    },
    {
        "title": "How does automation bias appear in LLM-assisted decision-making?",
        "theme": "judgment",
        "description": "Track evidence about users over-trusting fluent AI recommendations in decisions.",
        "priority": 5,
    },
    {
        "title": "What product patterns preserve human oversight without creating rubber-stamp approval?",
        "theme": "agency",
        "description": "Find interface patterns that make human review meaningful rather than ceremonial.",
        "priority": 4,
    },
    {
        "title": "How should AI tools protect children from answer dependence while still supporting learning?",
        "theme": "education",
        "description": "Study child-sensitive patterns for scaffolding, reflection, and delayed answers.",
        "priority": 5,
    },
    {
        "title": "Can reflective prompts reduce overreliance on AI recommendations?",
        "theme": "judgment",
        "description": "Evaluate whether asking users to state assumptions or criteria protects independent judgment.",
        "priority": 4,
    },
    {
        "title": "What signs indicate that AI collaboration is causing skill atrophy rather than skill amplification?",
        "theme": "skill",
        "description": "Identify measurable signals that distinguish productive augmentation from capability loss.",
        "priority": 4,
    },
    {
        "title": "How should AI copilots expose uncertainty so users remain actively critical?",
        "theme": "agency",
        "description": "Study uncertainty displays, calibration cues, and source-grounded UI patterns.",
        "priority": 4,
    },
    {
        "title": "What does research say about cognitive offloading and memory formation in digital tools?",
        "theme": "cognitive_offloading",
        "description": "Use cognitive offloading literature as a baseline for AI-native memory and reasoning questions.",
        "priority": 3,
    },
    {
        "title": "Which interface frictions improve learning without making AI tools feel punitive?",
        "theme": "engineering_patterns",
        "description": "Find useful friction patterns that protect cognition while preserving flow.",
        "priority": 4,
    },
]
```

- [ ] **Step 2: Implement seeding and question listing**

Create `backend/app/services/research_service.py`:

```python
from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.models import ResearchQuestion
from app.services.research_fixtures import SEED_RESEARCH_QUESTIONS


def seed_research_questions(session: Session) -> None:
    for item in SEED_RESEARCH_QUESTIONS:
        existing = session.exec(
            select(ResearchQuestion).where(ResearchQuestion.title == item["title"])
        ).first()
        if existing is not None:
            continue

        session.add(
            ResearchQuestion(
                title=item["title"],
                theme=item["theme"],
                description=item["description"],
                priority=item["priority"],
            )
        )

    session.commit()


def list_research_questions(session: Session) -> list[ResearchQuestion]:
    seed_research_questions(session)
    return list(
        session.exec(
            select(ResearchQuestion).order_by(
                ResearchQuestion.priority.desc(),
                ResearchQuestion.created_at.asc(),
            )
        ).all()
    )
```

- [ ] **Step 3: Add the question route**

Modify imports in `backend/app/main.py`:

```python
from app.schemas import ChatMessageIn, ChatResponse, ResearchQuestionList, ResearchQuestionOut
from app.services.research_service import list_research_questions
```

Add this route after `/api/health`:

```python
@app.get("/api/research/questions", response_model=ResearchQuestionList)
def get_research_questions(
    session: Session = Depends(get_session),
) -> ResearchQuestionList:
    questions = list_research_questions(session)
    return ResearchQuestionList(
        questions=[
            ResearchQuestionOut.model_validate(question, from_attributes=True)
            for question in questions
        ]
    )
```

- [ ] **Step 4: Run the question test**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_research_flow.py::test_research_questions_are_seeded_and_listed -v
```

Expected: PASS.

---

### Task 3: Fixture Research Run, Evidence, Hypotheses, and Brief

**Files:**
- Modify: `backend/app/services/research_fixtures.py`
- Modify: `backend/app/services/research_service.py`
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_research_flow.py`

- [ ] **Step 1: Add failing end-to-end research run test**

Append to `backend/tests/test_research_flow.py`:

```python
def test_fixture_research_run_creates_evidence_hypotheses_and_brief():
    clear_research_tables()

    with TestClient(app) as client:
        questions_response = client.get("/api/research/questions")
        question_id = questions_response.json()["questions"][0]["id"]

        run_response = client.post(
            "/api/research/runs",
            json={"question_id": question_id, "mode": "fixture"},
        )

        evidence_response = client.get(f"/api/research/evidence?question_id={question_id}")
        hypotheses_response = client.get("/api/research/hypotheses")
        brief_response = client.get("/api/research/brief")

    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["status"] == "completed"
    assert run_payload["evidence_created"] >= 3
    assert run_payload["hypotheses_created"] >= 1

    assert evidence_response.status_code == 200
    evidence_payload = evidence_response.json()
    assert len(evidence_payload["evidence"]) >= 3
    first_evidence = evidence_payload["evidence"][0]
    assert first_evidence["source"]["url"].startswith("https://")
    assert first_evidence["source"]["source_type"] in {"paper", "report", "policy", "blog"}
    assert first_evidence["limitations"]

    assert hypotheses_response.status_code == 200
    hypotheses_payload = hypotheses_response.json()
    assert hypotheses_payload["hypotheses"]
    top_hypothesis = hypotheses_payload["hypotheses"][0]
    assert top_hypothesis["overall_score"] >= top_hypothesis["engineering_feasibility_score"]
    assert top_hypothesis["status"] in {
        "promising",
        "accepted",
        "needs_expert_review",
    }

    assert brief_response.status_code == 200
    brief_payload = brief_response.json()
    assert brief_payload["title"] == "MindMate AutoResearch Brief"
    assert brief_payload["strongest_claims"]
    assert brief_payload["design_implications"]
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_research_flow.py::test_fixture_research_run_creates_evidence_hypotheses_and_brief -v
```

Expected: FAIL with missing `/api/research/runs`.

- [ ] **Step 3: Add deterministic research fixtures**

Append to `backend/app/services/research_fixtures.py`:

```python
FIXTURE_SOURCE_DOCUMENTS = [
    {
        "url": "https://example.org/research/cognitive-offloading-ai-writing",
        "title": "Cognitive Offloading and Generative Writing Assistance",
        "authors": "Research Synthesis Fixture",
        "publisher": "MindMate Fixture Library",
        "language": "en",
        "source_type": "paper",
        "snippet": "Frequent use of generated drafts can reduce planning effort unless learners are asked to form claims first.",
        "credibility_score": 82,
    },
    {
        "url": "https://example.org/reports/human-ai-overreliance",
        "title": "Human Oversight and Overreliance in AI Decision Support",
        "authors": "Policy Fixture Group",
        "publisher": "MindMate Fixture Library",
        "language": "en",
        "source_type": "report",
        "snippet": "Human oversight is more meaningful when reviewers must record their own criteria before seeing recommendations.",
        "credibility_score": 76,
    },
    {
        "url": "https://example.cn/ai-education/reflective-prompts",
        "title": "生成式AI学习场景中的反思提示",
        "authors": "中文教育研究夹具",
        "publisher": "MindMate Fixture Library",
        "language": "zh",
        "source_type": "policy",
        "snippet": "在学习任务中，先让学生表达判断，再展示AI答案，有助于减少直接抄用。",
        "credibility_score": 72,
    },
]


FIXTURE_EVIDENCE_CARDS = [
    {
        "source_url": "https://example.org/research/cognitive-offloading-ai-writing",
        "claim": "AI-generated drafts can shift effort away from independent planning.",
        "summary": "The source suggests learners benefit when they must produce an initial outline or claim before viewing a complete AI draft.",
        "stance": "supports",
        "evidence_strength": 78,
        "relevance_score": 88,
        "risk_domain": "education",
        "limitations": "Fixture source for deterministic MVP behavior; replace with live literature before external claims.",
    },
    {
        "source_url": "https://example.org/reports/human-ai-overreliance",
        "claim": "Human oversight becomes weaker when users only approve an already-formed AI recommendation.",
        "summary": "The report argues that oversight should require criteria or disagreement opportunities before final acceptance.",
        "stance": "supports",
        "evidence_strength": 74,
        "relevance_score": 91,
        "risk_domain": "agency",
        "limitations": "Policy-style evidence is useful for design patterns but does not prove causal learning outcomes.",
    },
    {
        "source_url": "https://example.cn/ai-education/reflective-prompts",
        "claim": "Reflective prompts may reduce direct copying in AI-assisted learning.",
        "summary": "The Chinese fixture emphasizes asking students to state their reasoning before receiving AI-generated answers.",
        "stance": "weakly_supports",
        "evidence_strength": 68,
        "relevance_score": 86,
        "risk_domain": "education",
        "limitations": "Needs expert review before being used for child education claims.",
    },
]


FIXTURE_HYPOTHESES = [
    {
        "title": "Require initial judgment before full AI answers",
        "statement": "For learning and high-stakes reasoning tasks, MindMate should ask users to state an initial judgment or criteria before revealing a complete AI recommendation.",
        "theme": "judgment",
        "evidence_score": 76,
        "product_value_score": 92,
        "engineering_feasibility_score": 84,
        "risk_sensitivity_score": 88,
        "rationale": "Multiple fixture evidence cards point toward reflection-before-answer as a buildable cognitive protection pattern.",
    },
    {
        "title": "Mark child education claims for expert review",
        "statement": "Claims about children, students, and learning outcomes should enter expert review before becoming product copy or strong UX claims.",
        "theme": "education",
        "evidence_score": 68,
        "product_value_score": 86,
        "engineering_feasibility_score": 78,
        "risk_sensitivity_score": 96,
        "rationale": "The topic is central to MindMate but sensitive enough to require careful wording and advisor review.",
    },
]
```

- [ ] **Step 4: Implement research run service**

Append these imports and functions to `backend/app/services/research_service.py`:

```python
from app.models import EvidenceCard, Hypothesis, ResearchRun, SourceDocument
from app.services.research_fixtures import (
    FIXTURE_EVIDENCE_CARDS,
    FIXTURE_HYPOTHESES,
    FIXTURE_SOURCE_DOCUMENTS,
)


def run_fixture_research_cycle(session: Session, question_id: int) -> ResearchRun:
    seed_research_questions(session)
    question = session.get(ResearchQuestion, question_id)
    if question is None:
        raise ValueError("Research question not found.")

    run = ResearchRun(
        question_id=question_id,
        status="running",
        query_plan=_build_query_plan(question),
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    source_by_url = _upsert_fixture_sources(session)
    evidence_created = _create_fixture_evidence(session, question_id, source_by_url)
    hypotheses_created, hypotheses_updated = _upsert_fixture_hypotheses(session)

    run.status = "completed"
    run.sources_examined = len(source_by_url)
    run.evidence_created = evidence_created
    run.hypotheses_created = hypotheses_created
    run.hypotheses_updated = hypotheses_updated
    run.kept_summary = "Kept reflection-before-answer and expert-review hypotheses as high-value MindMate design candidates."
    run.rejected_summary = "Rejected unbounded medical or child-development claims until stronger sources and expert review exist."
    run.completed_at = datetime.utcnow()
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def _build_query_plan(question: ResearchQuestion) -> str:
    return "\n".join(
        [
            f"EN: {question.title} AI cognition study",
            f"EN: {question.theme} human AI collaboration overreliance",
            f"ZH: 生成式AI {question.theme} 人机协同 研究",
            f"ZH: {question.title} 认知保护 产品设计",
        ]
    )


def _upsert_fixture_sources(session: Session) -> dict[str, SourceDocument]:
    source_by_url: dict[str, SourceDocument] = {}
    for item in FIXTURE_SOURCE_DOCUMENTS:
        source = session.exec(
            select(SourceDocument).where(SourceDocument.url == item["url"])
        ).first()
        if source is None:
            source = SourceDocument(**item)
            session.add(source)
            session.commit()
            session.refresh(source)
        source_by_url[source.url] = source
    return source_by_url


def _create_fixture_evidence(
    session: Session,
    question_id: int,
    source_by_url: dict[str, SourceDocument],
) -> int:
    created = 0
    for item in FIXTURE_EVIDENCE_CARDS:
        source = source_by_url[item["source_url"]]
        existing = session.exec(
            select(EvidenceCard).where(
                EvidenceCard.question_id == question_id,
                EvidenceCard.source_document_id == source.id,
                EvidenceCard.claim == item["claim"],
            )
        ).first()
        if existing is not None:
            continue

        evidence = EvidenceCard(
            question_id=question_id,
            source_document_id=source.id or 0,
            claim=item["claim"],
            summary=item["summary"],
            stance=item["stance"],
            evidence_strength=item["evidence_strength"],
            relevance_score=item["relevance_score"],
            risk_domain=item["risk_domain"],
            limitations=item["limitations"],
        )
        session.add(evidence)
        created += 1

    session.commit()
    return created


def _upsert_fixture_hypotheses(session: Session) -> tuple[int, int]:
    created = 0
    updated = 0
    for item in FIXTURE_HYPOTHESES:
        overall_score = score_hypothesis(
            evidence=item["evidence_score"],
            relevance=item["product_value_score"],
            product_value=item["product_value_score"],
            feasibility=item["engineering_feasibility_score"],
            risk_sensitivity=item["risk_sensitivity_score"],
        )
        status = classify_hypothesis(overall_score, item["risk_sensitivity_score"])
        existing = session.exec(
            select(Hypothesis).where(Hypothesis.title == item["title"])
        ).first()

        if existing is None:
            session.add(
                Hypothesis(
                    **item,
                    overall_score=overall_score,
                    status=status,
                )
            )
            created += 1
            continue

        existing.statement = item["statement"]
        existing.theme = item["theme"]
        existing.evidence_score = item["evidence_score"]
        existing.product_value_score = item["product_value_score"]
        existing.engineering_feasibility_score = item["engineering_feasibility_score"]
        existing.risk_sensitivity_score = item["risk_sensitivity_score"]
        existing.overall_score = overall_score
        existing.status = status
        existing.rationale = item["rationale"]
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        updated += 1

    session.commit()
    return created, updated


def score_hypothesis(
    evidence: float,
    relevance: float,
    product_value: float,
    feasibility: float,
    risk_sensitivity: float,
) -> float:
    return round(
        evidence * 0.35
        + relevance * 0.25
        + product_value * 0.20
        + feasibility * 0.10
        + risk_sensitivity * 0.10,
        2,
    )


def classify_hypothesis(overall_score: float, risk_sensitivity: float) -> str:
    if risk_sensitivity >= 94:
        return "needs_expert_review"
    if overall_score >= 82:
        return "accepted"
    if overall_score >= 68:
        return "promising"
    return "candidate"
```

- [ ] **Step 5: Add query helpers**

Append to `backend/app/services/research_service.py`:

```python
def get_research_run(session: Session, run_id: int) -> ResearchRun | None:
    return session.get(ResearchRun, run_id)


def list_evidence_cards(session: Session, question_id: int | None = None) -> list[tuple[EvidenceCard, SourceDocument]]:
    statement = select(EvidenceCard, SourceDocument).where(
        EvidenceCard.source_document_id == SourceDocument.id
    )
    if question_id is not None:
        statement = statement.where(EvidenceCard.question_id == question_id)

    statement = statement.order_by(
        EvidenceCard.evidence_strength.desc(),
        EvidenceCard.created_at.desc(),
    )
    return list(session.exec(statement).all())


def list_hypotheses(session: Session) -> list[Hypothesis]:
    return list(
        session.exec(
            select(Hypothesis).order_by(
                Hypothesis.overall_score.desc(),
                Hypothesis.updated_at.desc(),
            )
        ).all()
    )


def build_research_brief(session: Session):
    hypotheses = list_hypotheses(session)
    evidence_count = len(list_evidence_cards(session))
    strongest = [hypothesis.statement for hypothesis in hypotheses[:3]]
    expert_review = [
        hypothesis.title
        for hypothesis in hypotheses
        if hypothesis.status == "needs_expert_review"
    ]
    design_implications = [
        "Ask users for an initial judgment before full AI recommendations in learning and decision contexts.",
        "Keep source quality, limitations, and uncertainty visible in research outputs.",
        "Route child education and health-adjacent claims into expert review before product copy.",
    ]

    return {
        "title": "MindMate AutoResearch Brief",
        "summary": (
            f"The current fixture-backed research base contains {evidence_count} evidence cards "
            f"and {len(hypotheses)} scored hypotheses. The strongest signal is to preserve "
            "human judgment before complete AI answers."
        ),
        "strongest_claims": strongest,
        "open_questions": [
            "Which findings remain stable after replacing fixture sources with live literature search?",
            "Which intervention patterns protect cognition without creating punitive friction?",
        ],
        "design_implications": design_implications,
        "expert_review_queue": expert_review,
    }
```

- [ ] **Step 6: Add API routes**

Modify imports in `backend/app/main.py`:

```python
from app.schemas import (
    ChatMessageIn,
    ChatResponse,
    EvidenceCardList,
    EvidenceCardOut,
    HypothesisList,
    HypothesisOut,
    ResearchBrief,
    ResearchQuestionList,
    ResearchQuestionOut,
    ResearchRunCreate,
    ResearchRunCreateResponse,
    ResearchRunOut,
    SourceDocumentOut,
)
from app.services.research_service import (
    build_research_brief,
    get_research_run,
    list_evidence_cards,
    list_hypotheses,
    list_research_questions,
    run_fixture_research_cycle,
)
```

Add these routes after `get_research_questions`:

```python
@app.post("/api/research/runs", response_model=ResearchRunCreateResponse)
def post_research_run(
    payload: ResearchRunCreate,
    session: Session = Depends(get_session),
) -> ResearchRunCreateResponse:
    research_run = run_fixture_research_cycle(session, payload.question_id)
    return ResearchRunCreateResponse(
        run_id=research_run.id or 0,
        status=research_run.status,
        evidence_created=research_run.evidence_created,
        hypotheses_created=research_run.hypotheses_created,
        hypotheses_updated=research_run.hypotheses_updated,
    )


@app.get("/api/research/runs/{run_id}", response_model=ResearchRunOut)
def get_research_run_detail(
    run_id: int,
    session: Session = Depends(get_session),
) -> ResearchRunOut:
    research_run = get_research_run(session, run_id)
    if research_run is None:
        raise ValueError("Research run not found.")
    return ResearchRunOut.model_validate(research_run, from_attributes=True)


@app.get("/api/research/evidence", response_model=EvidenceCardList)
def get_research_evidence(
    question_id: int | None = None,
    session: Session = Depends(get_session),
) -> EvidenceCardList:
    evidence = [
        EvidenceCardOut(
            **card.model_dump(),
            source=SourceDocumentOut.model_validate(source, from_attributes=True),
        )
        for card, source in list_evidence_cards(session, question_id)
    ]
    return EvidenceCardList(evidence=evidence)


@app.get("/api/research/hypotheses", response_model=HypothesisList)
def get_research_hypotheses(
    session: Session = Depends(get_session),
) -> HypothesisList:
    hypotheses = [
        HypothesisOut.model_validate(hypothesis, from_attributes=True)
        for hypothesis in list_hypotheses(session)
    ]
    return HypothesisList(hypotheses=hypotheses)


@app.get("/api/research/brief", response_model=ResearchBrief)
def get_research_brief(
    session: Session = Depends(get_session),
) -> ResearchBrief:
    return ResearchBrief(**build_research_brief(session))
```

- [ ] **Step 7: Run backend research tests**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_research_flow.py -v
```

Expected: PASS.

---

### Task 4: Frontend Research Lab UI

**Files:**
- Create: `frontend/src/test/research-lab.test.tsx`
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/ResearchLab.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Write failing Research Lab test**

Create `frontend/src/test/research-lab.test.tsx`:

```tsx
import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

const questionsResponse = {
  questions: [
    {
      id: 1,
      title: "Does AI writing assistance reduce independent argument formation in students?",
      theme: "education",
      description: "Study student reasoning under AI writing assistance.",
      status: "queued",
      priority: 5,
      created_at: "2026-05-02T00:00:00Z",
      updated_at: "2026-05-02T00:00:00Z",
    },
  ],
};

const runResponse = {
  run_id: 7,
  status: "completed",
  evidence_created: 3,
  hypotheses_created: 2,
  hypotheses_updated: 0,
};

const evidenceResponse = {
  evidence: [
    {
      id: 11,
      question_id: 1,
      source_document_id: 21,
      claim: "AI-generated drafts can shift effort away from independent planning.",
      summary: "Learners benefit when they form an initial claim before seeing a complete AI draft.",
      stance: "supports",
      evidence_strength: 78,
      relevance_score: 88,
      risk_domain: "education",
      limitations: "Needs live literature before external claims.",
      created_at: "2026-05-02T00:00:00Z",
      source: {
        id: 21,
        url: "https://example.org/research/cognitive-offloading-ai-writing",
        title: "Cognitive Offloading and Generative Writing Assistance",
        authors: "Research Fixture",
        publisher: "MindMate Fixture Library",
        published_at: null,
        language: "en",
        source_type: "paper",
        snippet: "Generated drafts can reduce planning effort.",
        credibility_score: 82,
        retrieved_at: "2026-05-02T00:00:00Z",
      },
    },
  ],
};

const hypothesesResponse = {
  hypotheses: [
    {
      id: 31,
      title: "Require initial judgment before full AI answers",
      statement: "MindMate should ask users to state an initial judgment before revealing a complete AI recommendation.",
      theme: "judgment",
      status: "accepted",
      evidence_score: 76,
      product_value_score: 92,
      engineering_feasibility_score: 84,
      risk_sensitivity_score: 88,
      overall_score: 83.4,
      rationale: "Reflection-before-answer is a buildable cognitive protection pattern.",
      created_at: "2026-05-02T00:00:00Z",
      updated_at: "2026-05-02T00:00:00Z",
    },
  ],
};

const briefResponse = {
  title: "MindMate AutoResearch Brief",
  summary: "The strongest signal is to preserve human judgment before complete AI answers.",
  strongest_claims: ["Initial judgment before full answers protects agency."],
  open_questions: ["Which findings remain stable with live search?"],
  design_implications: ["Ask users for an initial judgment before full AI recommendations."],
  expert_review_queue: ["Mark child education claims for expert review"],
};

describe("Research Lab", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);

    fetchMock.mockImplementation(async (input, init) => {
      const url = String(input);

      if (url.endsWith("/api/health")) {
        return new Response(JSON.stringify({ status: "ok" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/questions")) {
        return new Response(JSON.stringify(questionsResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/runs")) {
        expect(init?.method).toBe("POST");
        return new Response(JSON.stringify(runResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.includes("/api/research/evidence")) {
        return new Response(JSON.stringify(evidenceResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/hypotheses")) {
        return new Response(JSON.stringify(hypothesesResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/brief")) {
        return new Response(JSON.stringify(briefResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      throw new Error(`Unexpected fetch call to ${url}`);
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("runs a fixture research cycle and displays evidence, hypotheses, and brief", async () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Research Lab" }));

    expect(await screen.findByRole("heading", { name: "Research Lab" })).toBeInTheDocument();
    expect(await screen.findByText(questionsResponse.questions[0].title)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "运行研究" }));

    expect(await screen.findByText("本次新增证据 3 条")).toBeInTheDocument();

    const evidencePanel = screen.getByRole("heading", { name: "证据卡片" }).closest("section");
    expect(evidencePanel).not.toBeNull();
    expect(within(evidencePanel as HTMLElement).getByText(evidenceResponse.evidence[0].claim)).toBeInTheDocument();
    expect(within(evidencePanel as HTMLElement).getByText("paper")).toBeInTheDocument();

    const hypothesisPanel = screen.getByRole("heading", { name: "高分假设" }).closest("section");
    expect(hypothesisPanel).not.toBeNull();
    expect(within(hypothesisPanel as HTMLElement).getByText(hypothesesResponse.hypotheses[0].title)).toBeInTheDocument();
    expect(within(hypothesisPanel as HTMLElement).getByText("83.4")).toBeInTheDocument();

    expect(screen.getByText(briefResponse.summary)).toBeInTheDocument();

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/research\/runs$/),
        expect.objectContaining({ method: "POST" }),
      );
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd frontend && npm test -- --run src/test/research-lab.test.tsx
```

Expected: FAIL because Research Lab UI and API functions do not exist.

- [ ] **Step 3: Add frontend research types**

Append to `frontend/src/types.ts`:

```ts
export interface ResearchQuestion {
  id: number;
  title: string;
  theme: string;
  description: string;
  status: string;
  priority: number;
  created_at: string;
  updated_at: string;
}

export interface ResearchRunCreateResponse {
  run_id: number;
  status: string;
  evidence_created: number;
  hypotheses_created: number;
  hypotheses_updated: number;
}

export interface SourceDocument {
  id: number;
  url: string;
  title: string;
  authors: string;
  publisher: string;
  published_at: string | null;
  language: string;
  source_type: string;
  snippet: string;
  credibility_score: number;
  retrieved_at: string;
}

export interface EvidenceCard {
  id: number;
  question_id: number;
  source_document_id: number;
  source: SourceDocument;
  claim: string;
  summary: string;
  stance: string;
  evidence_strength: number;
  relevance_score: number;
  risk_domain: string;
  limitations: string;
  created_at: string;
}

export interface Hypothesis {
  id: number;
  title: string;
  statement: string;
  theme: string;
  status: string;
  evidence_score: number;
  product_value_score: number;
  engineering_feasibility_score: number;
  risk_sensitivity_score: number;
  overall_score: number;
  rationale: string;
  created_at: string;
  updated_at: string;
}

export interface ResearchBrief {
  title: string;
  summary: string;
  strongest_claims: string[];
  open_questions: string[];
  design_implications: string[];
  expert_review_queue: string[];
}
```

- [ ] **Step 4: Add Research Lab API functions**

Modify import in `frontend/src/lib/api.ts`:

```ts
import type {
  ChatResponse,
  EvidenceCard,
  FocusSession,
  Hypothesis,
  ResearchBrief,
  ResearchQuestion,
  ResearchRunCreateResponse,
} from "../types";
```

Append:

```ts
export function getResearchQuestions() {
  return request<{ questions: ResearchQuestion[] }>("/api/research/questions");
}

export function startResearchRun(questionId: number) {
  return request<ResearchRunCreateResponse>("/api/research/runs", {
    method: "POST",
    body: JSON.stringify({
      question_id: questionId,
      mode: "fixture",
    }),
  });
}

export function getResearchEvidence(questionId?: number) {
  const query = questionId ? `?question_id=${questionId}` : "";
  return request<{ evidence: EvidenceCard[] }>(`/api/research/evidence${query}`);
}

export function getResearchHypotheses() {
  return request<{ hypotheses: Hypothesis[] }>("/api/research/hypotheses");
}

export function getResearchBrief() {
  return request<ResearchBrief>("/api/research/brief");
}
```

- [ ] **Step 5: Create ResearchLab component**

Create `frontend/src/components/ResearchLab.tsx`:

```tsx
import { useEffect, useMemo, useState } from "react";

import {
  getResearchBrief,
  getResearchEvidence,
  getResearchHypotheses,
  getResearchQuestions,
  startResearchRun,
} from "../lib/api";
import type {
  EvidenceCard,
  Hypothesis,
  ResearchBrief,
  ResearchQuestion,
  ResearchRunCreateResponse,
} from "../types";

export function ResearchLab() {
  const [questions, setQuestions] = useState<ResearchQuestion[]>([]);
  const [selectedQuestionId, setSelectedQuestionId] = useState<number | null>(null);
  const [runResult, setRunResult] = useState<ResearchRunCreateResponse | null>(null);
  const [evidence, setEvidence] = useState<EvidenceCard[]>([]);
  const [hypotheses, setHypotheses] = useState<Hypothesis[]>([]);
  const [brief, setBrief] = useState<ResearchBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadResearchLab() {
      try {
        const questionPayload = await getResearchQuestions();
        if (!active) {
          return;
        }
        setQuestions(questionPayload.questions);
        setSelectedQuestionId(questionPayload.questions[0]?.id ?? null);
      } catch {
        if (active) {
          setError("研究问题队列暂时无法加载。");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadResearchLab();

    return () => {
      active = false;
    };
  }, []);

  const selectedQuestion = useMemo(
    () => questions.find((question) => question.id === selectedQuestionId) ?? questions[0] ?? null,
    [questions, selectedQuestionId],
  );

  async function handleRunResearch() {
    if (!selectedQuestion) {
      return;
    }

    setRunning(true);
    setError("");

    try {
      const result = await startResearchRun(selectedQuestion.id);
      const [evidencePayload, hypothesesPayload, briefPayload] = await Promise.all([
        getResearchEvidence(selectedQuestion.id),
        getResearchHypotheses(),
        getResearchBrief(),
      ]);
      setRunResult(result);
      setEvidence(evidencePayload.evidence);
      setHypotheses(hypothesesPayload.hypotheses);
      setBrief(briefPayload);
    } catch {
      setError("这次研究循环没有跑通，请稍后再试。");
    } finally {
      setRunning(false);
    }
  }

  return (
    <section className="research-lab">
      <div className="research-header panel">
        <div>
          <p className="eyebrow">MindMate AutoResearch</p>
          <h2>Research Lab</h2>
          <p>
            自动提出问题、整理证据、保留高价值假设；只把高敏感或低可信结论交给人类判断。
          </p>
        </div>
        <button type="button" onClick={handleRunResearch} disabled={loading || running || !selectedQuestion}>
          {running ? "研究中..." : "运行研究"}
        </button>
      </div>

      {error ? <section className="inline-error">{error}</section> : null}

      {runResult ? (
        <section className="research-run-summary panel" aria-live="polite">
          <span>运行 #{runResult.run_id}</span>
          <strong>状态：{runResult.status}</strong>
          <span>本次新增证据 {runResult.evidence_created} 条</span>
          <span>新增假设 {runResult.hypotheses_created} 条</span>
        </section>
      ) : null}

      <div className="research-grid">
        <section className="panel research-queue">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Queue</p>
              <h2>研究问题队列</h2>
            </div>
            <span className="pill">{questions.length} 个问题</span>
          </div>

          <div className="research-question-list">
            {questions.map((question) => (
              <button
                className={`question-row ${question.id === selectedQuestion?.id ? "question-row-active" : ""}`}
                key={question.id}
                type="button"
                onClick={() => setSelectedQuestionId(question.id)}
              >
                <strong>{question.title}</strong>
                <span>{question.theme} · priority {question.priority}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="panel evidence-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Evidence</p>
              <h2>证据卡片</h2>
            </div>
            <span className="pill">{evidence.length} 条</span>
          </div>

          {evidence.length ? (
            <div className="evidence-list">
              {evidence.map((card) => (
                <article className="evidence-card" key={card.id}>
                  <div className="card-topline">
                    <span>{card.source.source_type}</span>
                    <span>{card.stance}</span>
                  </div>
                  <h3>{card.claim}</h3>
                  <p>{card.summary}</p>
                  <p className="card-meta">
                    强度 {card.evidence_strength} · 相关性 {card.relevance_score} · {card.risk_domain}
                  </p>
                  <a href={card.source.url}>{card.source.title}</a>
                  <p className="limitations">{card.limitations}</p>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>还没有证据卡片。</p>
              <span>运行一次研究后，这里会显示来源、立场、强度和限制。</span>
            </div>
          )}
        </section>

        <section className="panel hypothesis-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Hypotheses</p>
              <h2>高分假设</h2>
            </div>
            <span className="pill">{hypotheses.length} 条</span>
          </div>

          {hypotheses.length ? (
            <div className="hypothesis-list">
              {hypotheses.map((hypothesis) => (
                <article className="hypothesis-card" key={hypothesis.id}>
                  <div className="score-ring">{hypothesis.overall_score}</div>
                  <div>
                    <h3>{hypothesis.title}</h3>
                    <p>{hypothesis.statement}</p>
                    <p className="card-meta">
                      {hypothesis.status} · 证据 {hypothesis.evidence_score} · 产品价值 {hypothesis.product_value_score} · 可实现 {hypothesis.engineering_feasibility_score}
                    </p>
                    <p className="limitations">{hypothesis.rationale}</p>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>还没有形成假设。</p>
              <span>研究循环会把证据沉淀成可产品化的认知保护原则。</span>
            </div>
          )}
        </section>

        <section className="panel brief-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Brief</p>
              <h2>关键报告</h2>
            </div>
          </div>

          {brief ? (
            <>
              <h3>{brief.title}</h3>
              <p>{brief.summary}</p>
              <div className="brief-columns">
                <BriefList title="设计启发" items={brief.design_implications} />
                <BriefList title="需要人类复核" items={brief.expert_review_queue} />
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>关键报告等待生成。</p>
              <span>每次研究完成后，我会把关键变化整理成可读摘要。</span>
            </div>
          )}
        </section>
      </div>
    </section>
  );
}

function BriefList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
```

- [ ] **Step 6: Wire Research Lab into App**

Modify `frontend/src/App.tsx`:

```tsx
import { ResearchLab } from "./components/ResearchLab";
```

Add state near the existing state declarations:

```tsx
const [activeView, setActiveView] = useState<"workspace" | "research">("workspace");
```

Add mode buttons inside the topbar after the status paragraph:

```tsx
<div className="view-switcher" aria-label="Primary view">
  <button
    type="button"
    className={activeView === "workspace" ? "switch-active" : ""}
    onClick={() => setActiveView("workspace")}
  >
    Agent Workspace
  </button>
  <button
    type="button"
    className={activeView === "research" ? "switch-active" : ""}
    onClick={() => setActiveView("research")}
  >
    Research Lab
  </button>
</div>
```

Wrap the current workspace section:

```tsx
{activeView === "workspace" ? (
  <section className="workspace">
    ...
  </section>
) : (
  <ResearchLab />
)}
```

- [ ] **Step 7: Add Research Lab styles**

Append to `frontend/src/styles.css`:

```css
.view-switcher {
  display: inline-flex;
  gap: 8px;
  padding: 6px;
  border-radius: 999px;
  background: rgba(17, 38, 61, 0.06);
}

.view-switcher button {
  box-shadow: none;
  background: transparent;
  color: #395673;
  padding: 9px 14px;
}

.view-switcher .switch-active {
  background: linear-gradient(135deg, #0f766e, #0f5fa8);
  color: white;
  box-shadow: 0 10px 22px rgba(15, 95, 168, 0.18);
}

.research-lab {
  width: min(1200px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 18px;
}

.research-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.research-header h2 {
  font-size: 1.9rem;
}

.research-header p:last-child {
  max-width: 44rem;
  margin: 8px 0 0;
  color: #44607d;
}

.research-run-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.research-run-summary span,
.research-run-summary strong {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(17, 38, 61, 0.06);
}

.research-grid {
  display: grid;
  grid-template-columns: minmax(280px, 0.85fr) minmax(0, 1.15fr);
  gap: 18px;
  align-items: start;
}

.research-question-list,
.evidence-list,
.hypothesis-list {
  display: grid;
  gap: 12px;
}

.question-row {
  width: 100%;
  display: grid;
  gap: 6px;
  text-align: left;
  border-radius: 18px;
  padding: 14px;
  background: rgba(248, 251, 253, 0.92);
  color: #17324f;
  box-shadow: none;
}

.question-row span {
  color: #5a748f;
  font-size: 0.9rem;
}

.question-row-active {
  outline: 2px solid rgba(15, 118, 110, 0.32);
  background: rgba(237, 247, 245, 0.96);
}

.evidence-card,
.hypothesis-card {
  padding: 16px;
  border-radius: 18px;
  background: rgba(248, 251, 253, 0.92);
  border: 1px solid rgba(17, 38, 61, 0.08);
}

.evidence-card h3,
.hypothesis-card h3,
.brief-panel h3 {
  margin: 0;
  font-size: 1rem;
}

.evidence-card p,
.hypothesis-card p,
.brief-panel p {
  color: #44607d;
}

.card-topline,
.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #5a748f;
  font-size: 0.88rem;
}

.card-topline span {
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(17, 38, 61, 0.06);
}

.limitations {
  font-size: 0.9rem;
}

.hypothesis-card {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 14px;
}

.score-ring {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #17324f;
  color: white;
  font-weight: 800;
}

.brief-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.brief-columns ul {
  margin: 8px 0 0;
  padding-left: 20px;
  color: #44607d;
}

@media (max-width: 720px) {
  .research-header,
  .topbar {
    align-items: stretch;
  }

  .view-switcher,
  .research-header {
    flex-direction: column;
  }

  .research-grid,
  .brief-columns {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 8: Run frontend Research Lab test**

Run:

```bash
cd frontend && npm test -- --run src/test/research-lab.test.tsx
```

Expected: PASS.

---

### Task 5: Full Verification

**Files:**
- No new files.

- [ ] **Step 1: Run backend test suite**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_health.py tests/test_safety_guard.py tests/test_safe_interrupt.py tests/test_chat_flow.py tests/test_agent_response_shape.py tests/test_research_flow.py -v
```

Expected: PASS.

- [ ] **Step 2: Run frontend tests**

Run:

```bash
cd frontend && npm test -- --run src/test/app.test.tsx src/test/dashboard.test.tsx src/test/safety-notice.test.tsx src/test/research-lab.test.tsx
```

Expected: PASS.

- [ ] **Step 3: Build frontend**

Run:

```bash
cd frontend && npm run build
```

Expected: PASS with Vite build output and no TypeScript errors.

- [ ] **Step 4: Run backend research endpoint smoke check**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_research_flow.py -v
```

Expected: PASS and deterministic fixture-backed research output.

- [ ] **Step 5: Checkpoint**

Because the workspace is not a git repository, record changed files with:

```bash
find backend/app backend/tests frontend/src docs/superpowers -type f -newer docs/superpowers/specs/2026-05-02-mindmate-autoresearch-design.md | sort
```

Expected: Lists the plan, backend research files, frontend Research Lab files, and tests.

---

## Self-Review

Spec coverage:

- Research question queue: Task 2 backend, Task 4 frontend.
- Manual fixture-backed run: Task 3 backend, Task 4 frontend.
- Evidence cards with sources and limitations: Task 3 backend, Task 4 frontend.
- Ranked hypotheses with scores: Task 3 backend, Task 4 frontend.
- Research brief: Task 3 backend, Task 4 frontend.
- Testing and manual verification: Task 5.
- Automation-first direction: implemented by deterministic fixture loop now; scheduled runs are left for post-MVP because the spec excludes cron jobs from first pass.

Known boundary:

- Live web search is intentionally not included in this first implementation. The fixture adapter creates a reliable harness first, matching the Karpathy-style discipline of a small bounded loop before adding broader autonomy.
