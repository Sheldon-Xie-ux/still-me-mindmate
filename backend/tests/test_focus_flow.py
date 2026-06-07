from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session

from app.db import engine, init_db
from app.main import app
from app.models import AnalyticsSnapshot, FocusSession, Task
from app.services.analytics_service import touch_analytics


def test_focus_start_flow_from_chat_recommendation():
    init_db()
    with Session(engine) as session:
        session.exec(delete(FocusSession))
        session.exec(delete(AnalyticsSnapshot))
        session.exec(delete(Task))
        session.commit()

    with TestClient(app) as client:
        chat_response = client.post(
            "/api/chat/message",
            json={"message": "今天完成项目复盘并整理下周计划"},
        )

        assert chat_response.status_code == 200

        recommended_task_id = chat_response.json()["focus"]["recommended_task_id"]

        response = client.post(
            "/api/focus/start",
            json={"task_id": recommended_task_id, "duration_minutes": 25},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "active"


def test_focus_start_rejects_invalid_duration_and_missing_task():
    init_db()
    with Session(engine) as session:
        session.exec(delete(FocusSession))
        session.exec(delete(AnalyticsSnapshot))
        session.exec(delete(Task))
        session.commit()

    with TestClient(app) as client:
        invalid_duration = client.post(
            "/api/focus/start",
            json={"task_id": 9999, "duration_minutes": 0},
        )
        missing_task = client.post(
            "/api/focus/start",
            json={"task_id": 9999, "duration_minutes": 25},
        )

    assert invalid_duration.status_code == 400
    assert missing_task.status_code == 404


def test_focus_completion_is_idempotent_for_daily_analytics():
    init_db()
    with Session(engine) as session:
        session.exec(delete(FocusSession))
        session.exec(delete(AnalyticsSnapshot))
        session.exec(delete(Task))
        session.commit()

    with TestClient(app) as client:
        chat_response = client.post(
            "/api/chat/message",
            json={"message": "今天完成项目复盘并整理下周计划"},
        )
        task_id = chat_response.json()["focus"]["recommended_task_id"]

        start_response = client.post(
            "/api/focus/start",
            json={"task_id": task_id, "duration_minutes": 25},
        )
        session_id = start_response.json()["id"]

        first_complete = client.post(f"/api/focus/{session_id}/complete")
        second_complete = client.post(f"/api/focus/{session_id}/complete")

    assert first_complete.status_code == 200
    assert second_complete.status_code == 200
    assert second_complete.json()["status"] == "completed"

    with Session(engine) as session:
        snapshot = touch_analytics(session)

    assert snapshot.focus_minutes_today == 25


def test_touch_analytics_resets_when_day_changes():
    init_db()
    with Session(engine) as session:
        session.exec(delete(FocusSession))
        session.exec(delete(AnalyticsSnapshot))
        session.exec(delete(Task))
        session.commit()

        snapshot = touch_analytics(session)
        snapshot.date_bucket = snapshot.date_bucket.fromordinal(
            snapshot.date_bucket.toordinal() - 1
        )
        snapshot.daily_message_count = 7
        snapshot.focus_minutes_today = 50
        snapshot.uninterrupted_minutes = 40
        session.add(snapshot)
        session.commit()

        refreshed = touch_analytics(session)

    assert refreshed.daily_message_count == 1
    assert refreshed.focus_minutes_today == 0
    assert refreshed.uninterrupted_minutes == 5
