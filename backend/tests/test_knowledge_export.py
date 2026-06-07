from pathlib import Path

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
from app.services.knowledge_service import export_knowledge_base
from app.services.research_service import list_research_questions, run_fixture_research_cycle


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


def test_export_knowledge_base_writes_obsidian_and_notebooklm_files(tmp_path: Path):
    clear_research_tables()

    with Session(engine) as session:
        question = list_research_questions(session)[0]
        run_fixture_research_cycle(session, question.id or 0)

        result = export_knowledge_base(session, root=tmp_path, today="2026-05-02")

    assert result.root == str(tmp_path)
    assert result.files_written

    daily_brief = tmp_path / "01-Daily-Briefs" / "2026-05-02.md"
    notebook_pack = (
        tmp_path
        / "07-NotebookLM-Packs"
        / "2026-05-02-mindmate-notebooklm-source.md"
    )
    hypothesis_files = list((tmp_path / "03-Hypotheses").glob("*.md"))
    evidence_files = list((tmp_path / "02-Evidence-Cards").glob("*.md"))

    assert daily_brief.exists()
    assert notebook_pack.exists()
    assert hypothesis_files
    assert evidence_files

    daily_text = daily_brief.read_text(encoding="utf-8")
    notebook_text = notebook_pack.read_text(encoding="utf-8")

    assert "MindMate AutoResearch Daily Brief" in daily_text
    assert "Require initial judgment before full AI answers" in notebook_text
    assert "NotebookLM Import Pack" in notebook_text
    assert "How NotebookLM should use this source" in notebook_text
    assert "not a medical, psychological, or educational diagnosis" in notebook_text
    assert "fixture" not in notebook_text.lower()


def test_export_knowledge_base_removes_stale_generated_files_but_keeps_inbox(tmp_path: Path):
    clear_research_tables()

    stale_evidence = tmp_path / "02-Evidence-Cards" / "stale-placeholder.md"
    stale_notebook_docx = tmp_path / "07-NotebookLM-Packs" / "old-source.docx"
    manual_inbox_note = tmp_path / "00-Inbox" / "manual-note.md"
    stale_evidence.parent.mkdir(parents=True)
    stale_notebook_docx.parent.mkdir(parents=True)
    manual_inbox_note.parent.mkdir(parents=True)
    stale_evidence.write_text("old example.org evidence", encoding="utf-8")
    stale_notebook_docx.write_text("old binary placeholder", encoding="utf-8")
    manual_inbox_note.write_text("keep me", encoding="utf-8")

    with Session(engine) as session:
        question = list_research_questions(session)[0]
        run_fixture_research_cycle(session, question.id or 0)

        export_knowledge_base(session, root=tmp_path, today="2026-05-02")

    assert not stale_evidence.exists()
    assert not stale_notebook_docx.exists()
    assert manual_inbox_note.exists()


def test_notebooklm_pack_deduplicates_repeated_evidence_across_questions(tmp_path: Path):
    clear_research_tables()

    with Session(engine) as session:
        questions = list_research_questions(session)[:2]
        for question in questions:
            run_fixture_research_cycle(session, question.id or 0)

        export_knowledge_base(session, root=tmp_path, today="2026-05-02")

    notebook_pack = (
        tmp_path
        / "07-NotebookLM-Packs"
        / "2026-05-02-mindmate-notebooklm-source.md"
    )
    notebook_text = notebook_pack.read_text(encoding="utf-8")

    assert notebook_text.count("### Evidence") == 7
    assert (
        notebook_text.count(
            "Higher confidence in GenAI is associated with lower critical-thinking effort."
        )
        == 1
    )


def test_knowledge_export_endpoint_returns_written_files(tmp_path: Path, monkeypatch):
    clear_research_tables()
    monkeypatch.setenv("MINDMATE_KNOWLEDGE_ROOT", str(tmp_path))

    with TestClient(app) as client:
        question_id = client.get("/api/research/questions").json()["questions"][0]["id"]
        client.post(
            "/api/research/runs",
            json={"question_id": question_id, "mode": "fixture"},
        )
        response = client.post("/api/research/knowledge/export")

    assert response.status_code == 200
    payload = response.json()
    assert payload["root"] == str(tmp_path)
    assert any("07-NotebookLM-Packs" in path for path in payload["files_written"])
