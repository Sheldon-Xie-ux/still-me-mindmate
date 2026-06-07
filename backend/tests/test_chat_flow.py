from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session

from app.db import engine, init_db
from app.main import app
from app.models import AnalyticsSnapshot, FocusSession, Task


def test_chat_message_creates_tasks_and_focus():
    init_db()
    with Session(engine) as session:
        session.exec(delete(FocusSession))
        session.exec(delete(AnalyticsSnapshot))
        session.exec(delete(Task))
        session.commit()

    with TestClient(app) as client:
        first_response = client.post(
            "/api/chat/message",
            json={"message": "明天整理合同"},
        )
        assert first_response.status_code == 200

        response = client.post(
            "/api/chat/message",
            json={
                "message": "周五前完成路演PPT，今天回复两个投资人，并帮我安排优先级。"
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["tasks"]
    assert payload["reply"]
    assert len(payload["tasks"]) == 2
    assert {task["title"] for task in payload["tasks"]} == {
        "周五前完成路演PPT",
        "今天回复两个投资人",
    }
    assert payload["focus"]["recommended_task_id"] is not None
    assert payload["focus"]["recommended_task_id"] in {
        task["id"] for task in payload["tasks"]
    }
    assert set(payload["rhythm"]) == {
        "focus_minutes_today",
        "completed_tasks_today",
        "suggestion",
    }
