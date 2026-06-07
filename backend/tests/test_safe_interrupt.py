from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlmodel import Session

from app.db import engine, init_db
from app.main import app
from app.models import AnalyticsSnapshot, FocusSession, Task


def test_crisis_language_interrupts_planning():
    init_db()
    with Session(engine) as session:
        session.exec(delete(FocusSession))
        session.exec(delete(AnalyticsSnapshot))
        session.exec(delete(Task))
        session.commit()

    with TestClient(app) as client:
        response = client.post(
            "/api/chat/message",
            json={"message": "我不想活了，别再规划任务了"},
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["safety"]["state"] == "safe_interrupt"
    assert payload["tasks"] == []
    assert payload["focus"]["recommended_task_id"] is None
