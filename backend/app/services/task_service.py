from __future__ import annotations

from datetime import datetime, timedelta
import re

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models import Task
from app.services.priority_engine import score_task


def extract_candidate_tasks(message: str) -> list[dict]:
    normalized = re.sub(r"[。；;]", "，", message)
    chunks = [chunk.strip("，,. ") for chunk in normalized.split("，")]
    candidates: list[dict] = []

    for chunk in chunks:
        if not chunk:
            continue
        if any(token in chunk for token in ("安排优先级", "优先级")):
            continue

        urgency = 3
        importance = 3
        estimated_minutes = 60
        due_date = None
        category = "general"

        if "今天" in chunk:
            urgency = 5
            due_date = datetime.utcnow() + timedelta(hours=12)
        elif any(token in chunk for token in ("明天", "周五前", "本周", "尽快")):
            urgency = 4
            due_date = datetime.utcnow() + timedelta(days=2)

        if any(token in chunk for token in ("投资人", "路演", "PPT", "汇报")):
            importance = 5
            category = "work"

        if any(token in chunk for token in ("回复", "回", "确认")):
            estimated_minutes = 30
        elif "PPT" in chunk:
            estimated_minutes = 90

        candidates.append(
            {
                "title": chunk,
                "description": chunk,
                "category": category,
                "urgency": urgency,
                "importance": importance,
                "estimated_minutes": estimated_minutes,
                "due_date": due_date,
            }
        )

    return candidates


def upsert_tasks_from_message(session: Session, message: str) -> list[Task]:
    candidates = extract_candidate_tasks(message)
    touched_titles: list[str] = []

    for candidate in candidates:
        touched_titles.append(candidate["title"])
        score, label, reason = score_task(
            urgency=candidate["urgency"],
            importance=candidate["importance"],
            estimated_minutes=candidate["estimated_minutes"],
        )

        existing = session.exec(
            select(Task).where(Task.title == candidate["title"])
        ).first()

        if existing is None:
            task = Task(
                title=candidate["title"],
                description=candidate["description"],
                category=candidate["category"],
                due_date=candidate["due_date"],
                estimated_minutes=candidate["estimated_minutes"],
                priority_score=score,
                priority_label=label,
                priority_reason=reason,
            )
            session.add(task)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                existing = session.exec(
                    select(Task).where(Task.title == candidate["title"])
                ).first()
                if existing is None:
                    raise
                _update_task(existing, candidate, score, label, reason)
                session.add(existing)
                session.commit()
            continue

        _update_task(existing, candidate, score, label, reason)
        session.add(existing)
        session.commit()

    if not touched_titles:
        return []

    tasks = session.exec(
        select(Task)
        .where(Task.title.in_(touched_titles))
        .order_by(Task.priority_score.desc(), Task.created_at.asc())
    ).all()

    return list(tasks)


def _update_task(
    task: Task,
    candidate: dict,
    score: float,
    label: str,
    reason: str,
) -> None:
    task.description = candidate["description"]
    task.category = candidate["category"]
    task.due_date = candidate["due_date"]
    task.estimated_minutes = candidate["estimated_minutes"]
    task.priority_score = score
    task.priority_label = label
    task.priority_reason = reason
    task.updated_at = datetime.utcnow()
