from sqlalchemy import delete
from sqlmodel import Session, select

from app.db import engine, init_db
from app.models import Task
from app.services.task_service import upsert_tasks_from_message


def test_upsert_tasks_recovers_from_duplicate_title_integrity_error(monkeypatch):
    init_db()

    title = "今天回复两个投资人"

    with Session(engine) as cleanup_session:
        cleanup_session.exec(delete(Task))
        cleanup_session.commit()

    with Session(engine) as seed_session:
        seed_session.add(Task(title=title, description="旧任务"))
        seed_session.commit()

    with Session(engine) as session:
        real_exec = session.exec
        first_lookup = {"done": False}

        def fake_exec(statement, *args, **kwargs):
            if not first_lookup["done"]:
                first_lookup["done"] = True

                class FakeResult:
                    @staticmethod
                    def first():
                        return None

                return FakeResult()
            return real_exec(statement, *args, **kwargs)

        monkeypatch.setattr(session, "exec", fake_exec)

        tasks = upsert_tasks_from_message(session, title)

    assert len(tasks) == 1
    assert tasks[0].title == title
    assert tasks[0].description == title

    with Session(engine) as verify_session:
        rows = verify_session.exec(select(Task).where(Task.title == title)).all()

    assert len(rows) == 1
    assert rows[0].description == title

    with Session(engine) as cleanup_session:
        cleanup_session.exec(delete(Task))
        cleanup_session.commit()
