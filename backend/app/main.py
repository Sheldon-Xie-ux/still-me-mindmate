from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session

from app.config import get_settings
from app.db import get_session, init_db
from app.schemas import (
    ChatMessageIn,
    ChatResponse,
    EvidenceCardList,
    EvidenceCardOut,
    HypothesisList,
    HypothesisOut,
    KnowledgeExportResponse,
    ResearchBrief,
    ResearchQuestionList,
    ResearchQuestionOut,
    ResearchRunCreate,
    ResearchRunCreateResponse,
    ResearchRunOut,
    SourceDocumentOut,
)
from app.services.chat_service import build_chat_response
from app.services.focus_service import complete_focus_session, start_focus_session
from app.services.knowledge_service import export_knowledge_base
from app.services.research_service import (
    build_research_brief,
    get_research_run,
    list_evidence_cards,
    list_hypotheses,
    list_research_questions,
    run_fixture_research_cycle,
)


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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


@app.post("/api/research/runs", response_model=ResearchRunCreateResponse)
def post_research_run(
    payload: ResearchRunCreate,
    session: Session = Depends(get_session),
) -> ResearchRunCreateResponse:
    try:
        research_run = run_fixture_research_cycle(session, payload.question_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

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
        raise HTTPException(status_code=404, detail="Research run not found.")
    return ResearchRunOut.model_validate(research_run, from_attributes=True)


@app.get("/api/research/evidence", response_model=EvidenceCardList)
def get_research_evidence(
    question_id: Optional[int] = None,
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


@app.post("/api/research/knowledge/export", response_model=KnowledgeExportResponse)
def post_research_knowledge_export(
    session: Session = Depends(get_session),
) -> KnowledgeExportResponse:
    result = export_knowledge_base(session)
    return KnowledgeExportResponse(
        root=result.root,
        files_written=result.files_written,
    )


@app.post("/api/chat/message", response_model=ChatResponse)
def post_chat_message(
    payload: ChatMessageIn,
    session: Session = Depends(get_session),
) -> ChatResponse:
    return build_chat_response(session, payload.message)


class FocusStartIn(BaseModel):
    task_id: int
    duration_minutes: int


@app.post("/api/focus/start")
def post_focus_start(
    payload: FocusStartIn,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    focus_session = start_focus_session(
        session,
        task_id=payload.task_id,
        duration_minutes=payload.duration_minutes,
    )
    return {
        "id": focus_session.id,
        "task_id": focus_session.task_id,
        "duration_minutes": focus_session.duration_minutes,
        "status": focus_session.status,
        "started_at": focus_session.started_at,
        "ended_at": focus_session.ended_at,
    }


@app.post("/api/focus/{session_id}/complete")
def post_focus_complete(
    session_id: int,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    focus_session = complete_focus_session(session, session_id)
    return {
        "id": focus_session.id,
        "task_id": focus_session.task_id,
        "duration_minutes": focus_session.duration_minutes,
        "status": focus_session.status,
        "started_at": focus_session.started_at,
        "ended_at": focus_session.ended_at,
    }
