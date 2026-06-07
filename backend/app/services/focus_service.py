from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models import FocusSession, Task
from app.services.analytics_service import get_analytics_snapshot


def start_focus_session(
    session: Session,
    task_id: int,
    duration_minutes: int,
) -> FocusSession:
    if duration_minutes <= 0:
        raise HTTPException(status_code=400, detail="duration_minutes must be positive")

    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    active_sessions = session.exec(
        select(FocusSession).where(FocusSession.status == "active")
    ).all()

    now = datetime.utcnow()
    for active_session in active_sessions:
        active_session.status = "paused"
        active_session.ended_at = now
        session.add(active_session)

    focus_session = FocusSession(
        task_id=task_id,
        duration_minutes=duration_minutes,
        status="active",
        started_at=now,
    )
    session.add(focus_session)
    session.commit()
    session.refresh(focus_session)
    return focus_session


def complete_focus_session(session: Session, session_id: int) -> FocusSession:
    focus_session = session.get(FocusSession, session_id)
    if focus_session is None:
        raise HTTPException(status_code=404, detail="Focus session not found")

    if focus_session.status == "completed":
        return focus_session

    focus_session.status = "completed"
    focus_session.ended_at = datetime.utcnow()
    session.add(focus_session)

    snapshot = get_analytics_snapshot(session)
    snapshot.focus_minutes_today += focus_session.duration_minutes
    snapshot.last_break_at = focus_session.ended_at
    snapshot.uninterrupted_minutes = 0
    snapshot.updated_at = focus_session.ended_at
    session.add(snapshot)

    session.commit()
    session.refresh(focus_session)
    return focus_session
