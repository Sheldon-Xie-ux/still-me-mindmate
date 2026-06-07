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


def test_research_run_uses_real_source_domains_not_placeholder_sources():
    clear_research_tables()

    with TestClient(app) as client:
        question_id = client.get("/api/research/questions").json()["questions"][0]["id"]
        client.post(
            "/api/research/runs",
            json={"question_id": question_id, "mode": "fixture"},
        )
        evidence_response = client.get(f"/api/research/evidence?question_id={question_id}")

    assert evidence_response.status_code == 200
    evidence = evidence_response.json()["evidence"]
    urls = {card["source"]["url"] for card in evidence}
    source_titles = {card["source"]["title"] for card in evidence}

    assert len(evidence) >= 4
    assert all("example." not in url for url in urls)
    assert any("microsoft.com" in url for url in urls)
    assert any("unesco.org" in url for url in urls)
    assert any("eur-lex.europa.eu" in url for url in urls)
    assert any("Generative AI" in title or "Human oversight" in title for title in source_titles)
    assert all(card["limitations"] for card in evidence)
