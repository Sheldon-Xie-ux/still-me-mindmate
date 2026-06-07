from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from app.models import EvidenceCard, Hypothesis, ResearchQuestion, ResearchRun, SourceDocument
from app.services.research_fixtures import (
    FIXTURE_EVIDENCE_CARDS,
    FIXTURE_HYPOTHESES,
    FIXTURE_SOURCE_DOCUMENTS,
    SEED_RESEARCH_QUESTIONS,
)


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
        existing.engineering_feasibility_score = item[
            "engineering_feasibility_score"
        ]
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


def get_research_run(session: Session, run_id: int) -> ResearchRun | None:
    return session.get(ResearchRun, run_id)


def list_evidence_cards(
    session: Session,
    question_id: int | None = None,
) -> list[tuple[EvidenceCard, SourceDocument]]:
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


def build_research_brief(session: Session) -> dict[str, object]:
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
            f"The current curated-source research base contains {evidence_count} evidence cards "
            f"and {len(hypotheses)} scored hypotheses. The strongest signal is to preserve "
            "human judgment before complete AI answers."
        ),
        "strongest_claims": strongest,
        "open_questions": [
            "Which findings remain stable after the curated baseline is expanded with live literature search?",
            "Which intervention patterns protect cognition without creating punitive friction?",
        ],
        "design_implications": design_implications,
        "expert_review_queue": expert_review,
    }
