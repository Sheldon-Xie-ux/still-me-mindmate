from collections.abc import Generator
from pathlib import Path

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401


DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parents[1] / 'harmonymind.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_task_title_unique "
                "ON task (title)"
            )
        )
        columns = connection.execute(
            text("PRAGMA table_info(analyticssnapshot)")
        ).fetchall()
        column_names = {column[1] for column in columns}
        if "date_bucket" not in column_names:
            connection.execute(
                text(
                    "ALTER TABLE analyticssnapshot "
                    "ADD COLUMN date_bucket DATE"
                )
            )
            connection.execute(
                text(
                    "UPDATE analyticssnapshot "
                    "SET date_bucket = DATE('now') "
                    "WHERE date_bucket IS NULL"
                )
            )


def get_session() -> Generator[Session, None, None]:
    init_db()
    with Session(engine) as session:
        yield session
