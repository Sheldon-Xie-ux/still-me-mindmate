from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
import re

from sqlmodel import Session

from app.services.research_service import (
    build_research_brief,
    list_evidence_cards,
    list_hypotheses,
)


VAULT_DIRECTORIES = [
    "00-Inbox",
    "01-Daily-Briefs",
    "02-Evidence-Cards",
    "03-Hypotheses",
    "04-Design-Principles",
    "05-Expert-Review",
    "06-Sources",
    "07-NotebookLM-Packs",
    "99-System",
]

MANAGED_EXPORT_DIRECTORIES = [
    "01-Daily-Briefs",
    "02-Evidence-Cards",
    "03-Hypotheses",
    "04-Design-Principles",
    "05-Expert-Review",
    "06-Sources",
    "07-NotebookLM-Packs",
]

MANAGED_EXPORT_PATTERNS = ("*.md", "*.docx")


@dataclass(frozen=True)
class KnowledgeExportResult:
    root: str
    files_written: list[str]


def default_knowledge_root() -> Path:
    configured = os.getenv("MINDMATE_KNOWLEDGE_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[3] / "MindMate-Knowledge"


def export_knowledge_base(
    session: Session,
    root: Path | None = None,
    today: str | None = None,
) -> KnowledgeExportResult:
    export_root = root or default_knowledge_root()
    today_value = today or date.today().isoformat()
    files_written: list[str] = []

    _ensure_vault(export_root)
    _remove_stale_generated_files(export_root)
    files_written.append(str(_write_vault_readme(export_root)))

    brief = build_research_brief(session)
    evidence_rows = list_evidence_cards(session)
    hypotheses = list_hypotheses(session)

    files_written.append(
        str(_write_daily_brief(export_root, today_value, brief, evidence_rows, hypotheses))
    )
    files_written.extend(
        str(path)
        for path in _write_evidence_cards(export_root, evidence_rows)
    )
    files_written.extend(
        str(path)
        for path in _write_hypotheses(export_root, hypotheses)
    )
    files_written.extend(
        str(path)
        for path in _write_design_principles(export_root, hypotheses)
    )
    files_written.append(
        str(_write_expert_review(export_root, today_value, brief))
    )
    files_written.extend(
        str(path)
        for path in _write_sources(export_root, evidence_rows)
    )
    files_written.append(
        str(_write_notebooklm_pack(export_root, today_value, brief, evidence_rows, hypotheses))
    )

    return KnowledgeExportResult(
        root=str(export_root),
        files_written=files_written,
    )


def _ensure_vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for directory in VAULT_DIRECTORIES:
        (root / directory).mkdir(parents=True, exist_ok=True)


def _remove_stale_generated_files(root: Path) -> None:
    for directory in MANAGED_EXPORT_DIRECTORIES:
        target = root / directory
        for pattern in MANAGED_EXPORT_PATTERNS:
            for path in target.glob(pattern):
                if path.is_file():
                    path.unlink()


def _write_vault_readme(root: Path) -> Path:
    path = root / "99-System" / "README.md"
    content = """# MindMate Knowledge

This is the durable Markdown knowledge base for MindMate AutoResearch.

## Workflow

AutoResearch runs bounded research cycles, stores evidence and hypotheses here, and creates NotebookLM import packs for higher-level reading and Q&A.

## Structure

- `01-Daily-Briefs`: daily summaries and research movement
- `02-Evidence-Cards`: source-linked evidence cards
- `03-Hypotheses`: scored research hypotheses
- `04-Design-Principles`: productized cognitive-protection patterns
- `05-Expert-Review`: medically or educationally sensitive claims
- `06-Sources`: source metadata
- `07-NotebookLM-Packs`: curated Markdown source files for NotebookLM

## Boundary

This vault supports research synthesis and product design. It is not a medical, psychological, or educational diagnosis system.
"""
    return _write_text(path, content)


def _write_daily_brief(
    root: Path,
    today: str,
    brief: dict[str, object],
    evidence_rows,
    hypotheses,
) -> Path:
    path = root / "01-Daily-Briefs" / f"{today}.md"
    content = f"""---
type: daily-brief
date: {today}
tags:
  - mindmate
  - autoresearch
  - daily-brief
---

# MindMate AutoResearch Daily Brief - {today}

## Summary

{brief["summary"]}

## Strongest Claims

{_bullet_list(brief["strongest_claims"])}

## Design Implications

{_bullet_list(brief["design_implications"])}

## Expert Review Queue

{_bullet_list(brief["expert_review_queue"])}

## Current Counts

- Evidence cards: {len(evidence_rows)}
- Hypotheses: {len(hypotheses)}

## Boundary

This brief is source-aware research synthesis for product design. It is not a medical, psychological, or educational diagnosis.
"""
    return _write_text(path, content)


def _write_evidence_cards(root: Path, evidence_rows) -> list[Path]:
    paths: list[Path] = []
    for card, source in evidence_rows:
        slug = _slugify(card.claim)
        path = root / "02-Evidence-Cards" / f"evidence-{card.id}-{slug}.md"
        content = f"""---
type: evidence-card
id: {card.id}
question_id: {card.question_id}
source_id: {source.id}
source_type: {source.source_type}
stance: {card.stance}
risk_domain: {card.risk_domain}
tags:
  - mindmate
  - evidence
  - {card.risk_domain}
---

# {card.claim}

## Summary

{card.summary}

## Scores

- Evidence strength: {card.evidence_strength}
- Relevance: {card.relevance_score}
- Source credibility: {source.credibility_score}

## Source

- Title: {source.title}
- Publisher: {source.publisher}
- Authors: {source.authors}
- URL: {source.url}
- Language: {source.language}

## Limitations

{card.limitations}
"""
        paths.append(_write_text(path, content))
    return paths


def _write_hypotheses(root: Path, hypotheses) -> list[Path]:
    paths: list[Path] = []
    for hypothesis in hypotheses:
        slug = _slugify(hypothesis.title)
        path = root / "03-Hypotheses" / f"hypothesis-{hypothesis.id}-{slug}.md"
        content = f"""---
type: hypothesis
id: {hypothesis.id}
status: {hypothesis.status}
theme: {hypothesis.theme}
overall_score: {hypothesis.overall_score}
tags:
  - mindmate
  - hypothesis
  - {hypothesis.theme}
---

# {hypothesis.title}

## Statement

{hypothesis.statement}

## Score Breakdown

- Evidence: {hypothesis.evidence_score}
- Product value: {hypothesis.product_value_score}
- Engineering feasibility: {hypothesis.engineering_feasibility_score}
- Risk sensitivity: {hypothesis.risk_sensitivity_score}
- Overall: {hypothesis.overall_score}

## Rationale

{hypothesis.rationale}
"""
        paths.append(_write_text(path, content))
    return paths


def _write_design_principles(root: Path, hypotheses) -> list[Path]:
    paths: list[Path] = []
    for hypothesis in hypotheses:
        if hypothesis.status not in {"accepted", "promising"}:
            continue

        slug = _slugify(hypothesis.title)
        path = root / "04-Design-Principles" / f"principle-{hypothesis.id}-{slug}.md"
        content = f"""---
type: design-principle
source_hypothesis_id: {hypothesis.id}
status: draft
tags:
  - mindmate
  - design-principle
  - cognitive-protection
---

# {hypothesis.title}

## Principle

{hypothesis.statement}

## Product Pattern

Convert this hypothesis into interface behavior that preserves user judgment before AI output becomes the default frame.

## Applicability

Use for learning, decision support, professional judgment, and other settings where overreliance would be costly.

## Caution

Keep claims source-aware. Do not frame this as a clinical or educational guarantee.
"""
        paths.append(_write_text(path, content))
    return paths


def _write_expert_review(root: Path, today: str, brief: dict[str, object]) -> Path:
    path = root / "05-Expert-Review" / f"{today}-review-queue.md"
    content = f"""---
type: expert-review-queue
date: {today}
tags:
  - mindmate
  - expert-review
---

# Expert Review Queue - {today}

## Needs Review

{_bullet_list(brief["expert_review_queue"])}

## Review Rule

Claims about children, education outcomes, medicine, psychology, cognitive decline, or health must be reviewed before becoming product copy or strong user-facing assertions.
"""
    return _write_text(path, content)


def _write_sources(root: Path, evidence_rows) -> list[Path]:
    paths: list[Path] = []
    seen: set[int] = set()
    for _, source in evidence_rows:
        if source.id in seen:
            continue
        seen.add(source.id)
        slug = _slugify(source.title)
        path = root / "06-Sources" / f"source-{source.id}-{slug}.md"
        content = f"""---
type: source
id: {source.id}
source_type: {source.source_type}
language: {source.language}
credibility_score: {source.credibility_score}
tags:
  - mindmate
  - source
  - {source.source_type}
---

# {source.title}

- Authors: {source.authors}
- Publisher: {source.publisher}
- URL: {source.url}
- Retrieved at: {source.retrieved_at}

## Snippet

{source.snippet}
"""
        paths.append(_write_text(path, content))
    return paths


def _write_notebooklm_pack(
    root: Path,
    today: str,
    brief: dict[str, object],
    evidence_rows,
    hypotheses,
) -> Path:
    path = root / "07-NotebookLM-Packs" / f"{today}-mindmate-notebooklm-source.md"
    unique_evidence_rows = _dedupe_evidence_rows(evidence_rows)
    evidence_section = "\n\n".join(
        f"### Evidence {card.id}: {card.claim}\n\n"
        f"{card.summary}\n\n"
        f"Source: {source.title} ({source.source_type}, {source.url})\n\n"
        f"Limitations: {card.limitations}"
        for card, source in unique_evidence_rows
    )
    hypothesis_section = "\n\n".join(
        f"### {hypothesis.title}\n\n"
        f"{hypothesis.statement}\n\n"
        f"Status: {hypothesis.status}. Overall score: {hypothesis.overall_score}.\n\n"
        f"Rationale: {hypothesis.rationale}"
        for hypothesis in hypotheses
    )
    content = f"""# NotebookLM Import Pack - MindMate AutoResearch - {today}

This pack is designed to be uploaded to NotebookLM as a curated source for Q&A, synthesis, and review.

Boundary: this is not a medical, psychological, or educational diagnosis. It is a source-aware research synthesis for MindMate product design.

## Daily Brief

{brief["summary"]}

## Strongest Claims

{_bullet_list(brief["strongest_claims"])}

## Design Implications

{_bullet_list(brief["design_implications"])}

## Hypotheses

{hypothesis_section}

## Evidence Cards

{evidence_section}

## Expert Review Queue

{_bullet_list(brief["expert_review_queue"])}

## How NotebookLM should use this source

Use this document to answer questions about MindMate AutoResearch, cognitive protection design patterns, human-AI collaboration risks, and research-to-product translation. Keep uncertainty visible and do not convert these notes into medical, psychological, or educational diagnosis claims.
"""
    return _write_text(path, content)


def _dedupe_evidence_rows(evidence_rows) -> list[object]:
    unique_rows: list[object] = []
    seen: set[tuple[str, str]] = set()
    for card, source in evidence_rows:
        key = (source.url, card.claim)
        if key in seen:
            continue
        seen.add(key)
        unique_rows.append((card, source))
    return unique_rows


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return normalized[:80] or "item"


def _bullet_list(items: object) -> str:
    if not items:
        return "- None"
    if not isinstance(items, list):
        return f"- {items}"
    return "\n".join(f"- {item}" for item in items) or "- None"
