from __future__ import annotations

from datetime import date, datetime

from sqlmodel import Session, select

from app.models import AnalyticsSnapshot


def touch_analytics(session: Session) -> AnalyticsSnapshot:
    snapshot = get_analytics_snapshot(session)
    snapshot.daily_message_count += 1
    snapshot.uninterrupted_minutes += 5
    snapshot.updated_at = datetime.utcnow()
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot


def get_analytics_snapshot(session: Session) -> AnalyticsSnapshot:
    snapshot = session.exec(
        select(AnalyticsSnapshot).order_by(AnalyticsSnapshot.id.asc())
    ).first()

    now = datetime.utcnow()
    today = date.today()
    if snapshot is None:
        snapshot = AnalyticsSnapshot(
            date_bucket=today,
            daily_message_count=0,
            uninterrupted_minutes=0,
            last_break_at=now,
            updated_at=now,
        )
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)
        return snapshot

    if snapshot.date_bucket != today:
        snapshot.date_bucket = today
        snapshot.daily_message_count = 0
        snapshot.focus_minutes_today = 0
        snapshot.uninterrupted_minutes = 0
        snapshot.last_break_at = now
        snapshot.updated_at = now
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)

    return snapshot
