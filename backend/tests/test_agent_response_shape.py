from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session

from app.db import engine, init_db
from app.main import app
from app.models import AnalyticsSnapshot, FocusSession, Task


def test_chat_message_returns_agent_centered_fields():
    init_db()
    with Session(engine) as session:
        session.exec(delete(FocusSession))
        session.exec(delete(AnalyticsSnapshot))
        session.exec(delete(Task))
        session.commit()

    with TestClient(app) as client:
        response = client.post(
            "/api/chat/message",
            json={
                "message": "这周内完成续费方案，今天先给客户发中文确认邮件，并提醒我下一步最该推进什么。"
            },
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["current_priority"]["title"]
    assert payload["current_priority"]["reason"]
    assert payload["next_action"]["label"]
    assert payload["system_observation"]["suggestion"]
