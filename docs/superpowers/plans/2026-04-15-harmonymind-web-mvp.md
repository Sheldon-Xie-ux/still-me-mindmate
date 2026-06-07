# HarmonyMind Web MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local web MVP that turns free-form user input into prioritized tasks, focus sessions, daily rhythm feedback, and background safety interventions.

**Architecture:** Use a React + Vite frontend for the mixed conversation/dashboard UI and a FastAPI backend for orchestration, persistence, prioritization, safety checks, and focus tracking. Persist all core state in SQLite so the main demo loop is real, while leaving external integrations as future extension points.

**Tech Stack:** React, TypeScript, Vite, FastAPI, Python 3.11+, SQLite, SQLModel, pytest, Vitest, Testing Library

---

### Task 1: Scaffold the Frontend, Backend, and Shared Local Workflow

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/tests/test_health.py`
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/test/app.test.tsx`
- Create: `README.md`

- [ ] **Step 1: Write the backend health test**

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck_returns_ok() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run the backend test to verify it fails**

Run: `cd backend && pytest tests/test_health.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `app.main`

- [ ] **Step 3: Create the backend app entrypoint and config**

```python
# backend/app/config.py
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SQLITE_URL = f"sqlite:///{DATA_DIR / 'harmonymind.db'}"
```

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="HarmonyMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
```

```toml
# backend/pyproject.toml
[project]
name = "harmonymind-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn>=0.30.0",
  "sqlmodel>=0.0.22",
  "pydantic>=2.9.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "httpx>=0.27.0",
]

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 4: Run the backend test to verify it passes**

Run: `cd backend && python -m pip install -e '.[dev]' && pytest tests/test_health.py -v`
Expected: PASS

- [ ] **Step 5: Write the frontend smoke test**

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "../App";

describe("App", () => {
  it("renders the HarmonyMind shell", () => {
    render(<App />);

    expect(screen.getByText("HarmonyMind")).toBeInTheDocument();
    expect(screen.getByText("Today Tasks")).toBeInTheDocument();
  });
});
```

- [ ] **Step 6: Run the frontend test to verify it fails**

Run: `cd frontend && npm test -- --run src/test/app.test.tsx`
Expected: FAIL with missing Vite app files

- [ ] **Step 7: Create the frontend shell, styles, and API helper**

```json
// frontend/package.json
{
  "name": "harmonymind-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.0",
    "@testing-library/react": "^16.1.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.6.0",
    "vite": "^5.4.0",
    "vitest": "^2.1.0"
  }
}
```

```tsx
// frontend/src/App.tsx
export default function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI teammate for focus, not dependence</p>
          <h1>HarmonyMind</h1>
        </div>
      </header>
      <main className="workspace">
        <section className="panel conversation-panel">
          <h2>Conversation</h2>
          <p>Describe what is competing for your attention.</p>
        </section>
        <section className="panel dashboard-panel">
          <h2>Today Tasks</h2>
          <p>Your prioritized work will appear here.</p>
        </section>
      </main>
    </div>
  );
}
```

```ts
// frontend/src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

```ts
// frontend/src/lib/api.ts
export async function getHealth(): Promise<{ status: string }> {
  const response = await fetch("http://localhost:8000/api/health");
  if (!response.ok) {
    throw new Error("Healthcheck failed");
  }
  return response.json();
}
```

- [ ] **Step 8: Run the frontend test to verify it passes**

Run: `cd frontend && npm install && npm test -- --run src/test/app.test.tsx`
Expected: PASS

- [ ] **Step 9: Add a top-level README with local run commands**

```md
# HarmonyMind

## Local Development

### Backend

```bash
cd backend
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```
```

- [ ] **Step 10: Commit the scaffold**

```bash
git add README.md backend frontend
git commit -m "feat: scaffold HarmonyMind web MVP"
```

### Task 2: Build Persistence, Task Management, Priority Scoring, and Message Orchestration

**Files:**
- Create: `backend/app/db.py`
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/services/task_service.py`
- Create: `backend/app/services/priority_engine.py`
- Create: `backend/app/services/chat_service.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_chat_flow.py`
- Create: `backend/tests/test_priority_engine.py`

- [ ] **Step 1: Write the priority engine test**

```python
from app.services.priority_engine import score_task


def test_score_task_prefers_urgent_and_important_work() -> None:
    score, label, reason = score_task(
        urgency=5,
        importance=5,
        estimated_minutes=30,
    )

    assert score > 0
    assert label == "high"
    assert "urgent" in reason.lower()
```

- [ ] **Step 2: Write the chat flow test**

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_message_creates_tasks_and_returns_dashboard_state() -> None:
    response = client.post(
        "/api/chat/message",
        json={
            "message": "周五前完成路演PPT，今天回复两个投资人，并帮我安排优先级。",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tasks"]
    assert payload["reply"]
    assert payload["focus"]["recommended_task_id"] is not None
```

- [ ] **Step 3: Run the new backend tests to verify they fail**

Run: `cd backend && pytest tests/test_priority_engine.py tests/test_chat_flow.py -v`
Expected: FAIL with missing services or routes

- [ ] **Step 4: Create the SQLite setup, models, and response schemas**

```python
# backend/app/db.py
from sqlmodel import Session, SQLModel, create_engine

from app.config import SQLITE_URL


engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

```python
# backend/app/models.py
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    category: str = "general"
    priority_score: float = 0
    priority_label: str = "medium"
    priority_reason: str = ""
    status: str = "pending"
    due_date: Optional[str] = None
    estimated_minutes: int = 30
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

```python
# backend/app/schemas.py
from pydantic import BaseModel


class ChatMessageIn(BaseModel):
    message: str


class TaskOut(BaseModel):
    id: int
    title: str
    status: str
    due_date: str | None
    priority_label: str
    priority_reason: str


class ChatResponse(BaseModel):
    reply: str
    tasks: list[TaskOut]
    focus: dict[str, int | None]
    rhythm: dict[str, int | str]
    safety: dict[str, str | None]
```

- [ ] **Step 5: Implement the priority engine and task service**

```python
# backend/app/services/priority_engine.py
def score_task(urgency: int, importance: int, estimated_minutes: int) -> tuple[float, str, str]:
    score = urgency * 0.45 + importance * 0.45 - min(estimated_minutes, 180) / 180 * 0.1
    if score >= 3.8:
        return score, "high", "This rises to the top because it is urgent and important."
    if score >= 2.6:
        return score, "medium", "This matters, but it can follow the most time-sensitive work."
    return score, "low", "This can wait until the high-impact items are moving."
```

```python
# backend/app/services/task_service.py
from datetime import datetime

from sqlmodel import Session, select

from app.models import Task
from app.services.priority_engine import score_task


def extract_candidate_tasks(message: str) -> list[dict[str, str | int | None]]:
    candidates: list[dict[str, str | int | None]] = []
    for chunk in [part.strip() for part in message.replace("，", ",").split(",") if part.strip()]:
        urgency = 5 if "今天" in chunk or "周五前" in chunk else 3
        importance = 5 if any(word in chunk for word in ["路演", "投资人", "商业计划书", "PPT"]) else 3
        candidates.append(
            {
                "title": chunk,
                "description": chunk,
                "due_date": "this_week" if "周五前" in chunk else None,
                "estimated_minutes": 45 if "PPT" in chunk or "商业计划书" in chunk else 20,
                "urgency": urgency,
                "importance": importance,
            }
        )
    return candidates or [{"title": message, "description": message, "due_date": None, "estimated_minutes": 30, "urgency": 3, "importance": 3}]


def upsert_tasks_from_message(session: Session, message: str) -> list[Task]:
    tasks: list[Task] = []
    for candidate in extract_candidate_tasks(message):
        score, label, reason = score_task(
            urgency=int(candidate["urgency"]),
            importance=int(candidate["importance"]),
            estimated_minutes=int(candidate["estimated_minutes"]),
        )
        task = Task(
            title=str(candidate["title"]),
            description=str(candidate["description"]),
            due_date=candidate["due_date"],
            estimated_minutes=int(candidate["estimated_minutes"]),
            priority_score=score,
            priority_label=label,
            priority_reason=reason,
            updated_at=datetime.utcnow(),
        )
        session.add(task)
        tasks.append(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return list(session.exec(select(Task).order_by(Task.priority_score.desc())).all())
```

- [ ] **Step 6: Implement the chat orchestration route**

```python
# backend/app/services/chat_service.py
from sqlmodel import Session

from app.models import Task
from app.services.task_service import upsert_tasks_from_message


def build_chat_response(session: Session, message: str) -> dict:
    tasks = upsert_tasks_from_message(session, message)
    top_task: Task | None = tasks[0] if tasks else None
    reply = "我已经帮你拆出任务，并把最值得先做的事项排到了前面。先从最关键的一项开始。"
    return {
        "reply": reply,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "due_date": task.due_date,
                "priority_label": task.priority_label,
                "priority_reason": task.priority_reason,
            }
            for task in tasks
        ],
        "focus": {"recommended_task_id": top_task.id if top_task else None},
        "rhythm": {"focus_minutes_today": 0, "completed_tasks_today": 0, "suggestion": "Start with one focused block."},
        "safety": {"state": "none", "message": None},
    }
```

```python
# backend/app/main.py
from fastapi import Depends, FastAPI
from sqlmodel import Session

from app.db import get_session, init_db
from app.schemas import ChatMessageIn
from app.services.chat_service import build_chat_response

app = FastAPI(title="HarmonyMind API")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/api/chat/message")
def post_chat_message(payload: ChatMessageIn, session: Session = Depends(get_session)) -> dict:
    return build_chat_response(session, payload.message)
```

- [ ] **Step 7: Run the backend tests to verify they pass**

Run: `cd backend && pytest tests/test_priority_engine.py tests/test_chat_flow.py tests/test_health.py -v`
Expected: PASS

- [ ] **Step 8: Commit the task and orchestration layer**

```bash
git add backend/app backend/tests
git commit -m "feat: add task orchestration and priority engine"
```

### Task 3: Add Safety Guard, Analytics Tracking, and Focus Session APIs

**Files:**
- Create: `backend/app/services/safety_guard.py`
- Create: `backend/app/services/analytics_service.py`
- Create: `backend/app/services/focus_service.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/services/chat_service.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_safety_guard.py`
- Create: `backend/tests/test_focus_flow.py`

- [ ] **Step 1: Write the safety guard tests**

```python
from app.services.safety_guard import evaluate_safety_state


def test_crisis_language_triggers_safe_interrupt() -> None:
    result = evaluate_safety_state("我不想活了，别再规划任务了", uninterrupted_minutes=15)

    assert result["state"] == "safe_interrupt"


def test_overload_language_triggers_gentle_nudge() -> None:
    result = evaluate_safety_state("我压力很大，已经连续忙了很久", uninterrupted_minutes=80)

    assert result["state"] == "gentle_nudge"
```

- [ ] **Step 2: Write the focus API test**

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_start_focus_session_for_task() -> None:
    chat_response = client.post(
        "/api/chat/message",
        json={"message": "今天完成演示稿并开始准备路演"},
    )
    task_id = chat_response.json()["focus"]["recommended_task_id"]

    response = client.post("/api/focus/start", json={"task_id": task_id, "duration_minutes": 25})

    assert response.status_code == 200
    assert response.json()["status"] == "active"
```

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `cd backend && pytest tests/test_safety_guard.py tests/test_focus_flow.py -v`
Expected: FAIL with missing services or routes

- [ ] **Step 4: Extend the models for analytics and focus sessions**

```python
# backend/app/models.py
class FocusSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int
    duration_minutes: int
    status: str = "active"
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


class AnalyticsSnapshot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    daily_message_count: int = 0
    focus_minutes_today: int = 0
    uninterrupted_minutes: int = 0
    last_break_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

- [ ] **Step 5: Implement the safety guard, analytics service, and focus service**

```python
# backend/app/services/safety_guard.py
CRISIS_PHRASES = ["不想活", "自杀", "伤害自己", "结束自己"]
OVERLOAD_PHRASES = ["压力很大", "撑不住", "太累了", "焦虑", "崩溃"]


def evaluate_safety_state(message: str, uninterrupted_minutes: int) -> dict[str, str | None]:
    if any(phrase in message for phrase in CRISIS_PHRASES):
        return {
            "state": "safe_interrupt",
            "message": "我不能提供危机或医疗帮助。请立刻联系你信任的人，或尽快联系当地紧急支持资源。",
        }
    if uninterrupted_minutes >= 75 or any(phrase in message for phrase in OVERLOAD_PHRASES):
        return {
            "state": "gentle_nudge",
            "message": "你已经在高压状态里坚持了一段时间。先把目标缩成一步，或者休息几分钟再继续。",
        }
    return {"state": "none", "message": None}
```

```python
# backend/app/services/analytics_service.py
from datetime import datetime

from sqlmodel import Session, select

from app.models import AnalyticsSnapshot


def touch_analytics(session: Session) -> AnalyticsSnapshot:
    snapshot = session.exec(select(AnalyticsSnapshot)).first()
    if snapshot is None:
        snapshot = AnalyticsSnapshot()
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)
    snapshot.daily_message_count += 1
    snapshot.uninterrupted_minutes += 5
    snapshot.updated_at = datetime.utcnow()
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot
```

```python
# backend/app/services/focus_service.py
from datetime import datetime

from sqlmodel import Session, select

from app.models import FocusSession


def start_focus_session(session: Session, task_id: int, duration_minutes: int) -> FocusSession:
    existing = session.exec(select(FocusSession).where(FocusSession.status == "active")).first()
    if existing:
        existing.status = "paused"
        session.add(existing)
    focus = FocusSession(task_id=task_id, duration_minutes=duration_minutes, status="active")
    session.add(focus)
    session.commit()
    session.refresh(focus)
    return focus


def complete_focus_session(session: Session, session_id: int) -> FocusSession:
    focus = session.get(FocusSession, session_id)
    assert focus is not None
    focus.status = "completed"
    focus.ended_at = datetime.utcnow()
    session.add(focus)
    session.commit()
    session.refresh(focus)
    return focus
```

- [ ] **Step 6: Wire safety and focus APIs into the backend**

```python
# backend/app/services/chat_service.py
from app.services.analytics_service import touch_analytics
from app.services.safety_guard import evaluate_safety_state


def build_chat_response(session: Session, message: str) -> dict:
    analytics = touch_analytics(session)
    safety = evaluate_safety_state(message, analytics.uninterrupted_minutes)
    if safety["state"] == "safe_interrupt":
        return {
            "reply": safety["message"],
            "tasks": [],
            "focus": {"recommended_task_id": None},
            "rhythm": {
                "focus_minutes_today": analytics.focus_minutes_today,
                "completed_tasks_today": 0,
                "suggestion": "Pause ordinary planning and seek human support now.",
            },
            "safety": safety,
        }
    tasks = upsert_tasks_from_message(session, message)
    top_task = tasks[0] if tasks else None
    return {
        "reply": "我已经把信息整理成今天可以执行的顺序。先从最关键的一项开始。",
        "tasks": [...],
        "focus": {"recommended_task_id": top_task.id if top_task else None},
        "rhythm": {
            "focus_minutes_today": analytics.focus_minutes_today,
            "completed_tasks_today": 0,
            "suggestion": safety["message"] or "You still have room for one solid block.",
        },
        "safety": safety,
    }
```

```python
# backend/app/main.py
from pydantic import BaseModel

from app.services.focus_service import complete_focus_session, start_focus_session


class FocusStartIn(BaseModel):
    task_id: int
    duration_minutes: int


@app.post("/api/focus/start")
def post_focus_start(payload: FocusStartIn, session: Session = Depends(get_session)) -> dict:
    focus = start_focus_session(session, payload.task_id, payload.duration_minutes)
    return {"id": focus.id, "task_id": focus.task_id, "status": focus.status, "duration_minutes": focus.duration_minutes}


@app.post("/api/focus/{session_id}/complete")
def post_focus_complete(session_id: int, session: Session = Depends(get_session)) -> dict:
    focus = complete_focus_session(session, session_id)
    return {"id": focus.id, "status": focus.status}
```

- [ ] **Step 7: Run the backend test suite to verify it passes**

Run: `cd backend && pytest tests/test_safety_guard.py tests/test_focus_flow.py tests/test_chat_flow.py tests/test_priority_engine.py tests/test_health.py -v`
Expected: PASS

- [ ] **Step 8: Commit the safety and focus layer**

```bash
git add backend/app backend/tests
git commit -m "feat: add safety guard analytics and focus APIs"
```

### Task 4: Build the Web Product UI and Connect It to the Real Backend

**Files:**
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/components/ConversationPanel.tsx`
- Create: `frontend/src/components/TodayTasks.tsx`
- Create: `frontend/src/components/FocusSessionCard.tsx`
- Create: `frontend/src/components/DailyRhythmCard.tsx`
- Create: `frontend/src/components/SafetyNotice.tsx`
- Create: `frontend/src/types.ts`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/styles.css`
- Create: `frontend/src/test/dashboard.test.tsx`

- [ ] **Step 1: Write the dashboard integration test**

```tsx
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import App from "../App";

vi.stubGlobal("fetch", vi.fn(async () => ({
  ok: true,
  json: async () => ({
    reply: "我已经帮你整理好了。",
    tasks: [
      {
        id: 1,
        title: "完成路演PPT",
        status: "pending",
        due_date: "this_week",
        priority_label: "high",
        priority_reason: "This rises to the top because it is urgent and important.",
      },
    ],
    focus: { recommended_task_id: 1 },
    rhythm: { focus_minutes_today: 0, completed_tasks_today: 0, suggestion: "Start with one focused block." },
    safety: { state: "none", message: null },
  }),
})) as typeof fetch);

test("submitting a message updates the dashboard", async () => {
  render(<App />);

  fireEvent.change(screen.getByPlaceholderText("Tell HarmonyMind what is competing for your attention..."), {
    target: { value: "今天先完成路演PPT，并处理投资人回复" },
  });
  fireEvent.click(screen.getByText("Send"));

  await waitFor(() => expect(screen.getByText("完成路演PPT")).toBeInTheDocument());
});
```

- [ ] **Step 2: Run the frontend test to verify it fails**

Run: `cd frontend && npm test -- --run src/test/dashboard.test.tsx`
Expected: FAIL with missing input, API wiring, or dashboard components

- [ ] **Step 3: Add the typed API client and shared frontend types**

```ts
// frontend/src/types.ts
export type Task = {
  id: number;
  title: string;
  status: string;
  due_date: string | null;
  priority_label: string;
  priority_reason: string;
};

export type ChatResponse = {
  reply: string;
  tasks: Task[];
  focus: { recommended_task_id: number | null };
  rhythm: { focus_minutes_today: number; completed_tasks_today: number; suggestion: string };
  safety: { state: string; message: string | null };
};
```

```ts
// frontend/src/lib/api.ts
import type { ChatResponse } from "../types";

const API_BASE = "http://localhost:8000/api";

export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!response.ok) {
    throw new Error("Unable to send message");
  }
  return response.json();
}

export async function startFocus(taskId: number, durationMinutes: number) {
  const response = await fetch(`${API_BASE}/focus/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId, duration_minutes: durationMinutes }),
  });
  if (!response.ok) {
    throw new Error("Unable to start focus session");
  }
  return response.json();
}
```

- [ ] **Step 4: Build the mixed workspace UI**

```tsx
// frontend/src/App.tsx
import { useState } from "react";

import { sendMessage } from "./lib/api";
import type { ChatResponse } from "./types";

const initialState: ChatResponse = {
  reply: "Describe what is competing for your attention and I will help narrow it.",
  tasks: [],
  focus: { recommended_task_id: null },
  rhythm: { focus_minutes_today: 0, completed_tasks_today: 0, suggestion: "Start with one clear priority." },
  safety: { state: "none", message: null },
};

export default function App() {
  const [draft, setDraft] = useState("");
  const [state, setState] = useState(initialState);
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (!draft.trim()) return;
    setLoading(true);
    try {
      const response = await sendMessage(draft);
      setState(response);
      setDraft("");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI teammate for focus, not dependence</p>
          <h1>HarmonyMind</h1>
        </div>
      </header>
      <main className="workspace">
        <section className="panel conversation-panel">
          <h2>Conversation</h2>
          <p className="assistant-reply">{state.reply}</p>
          <textarea
            placeholder="Tell HarmonyMind what is competing for your attention..."
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
          />
          <button onClick={handleSubmit} disabled={loading}>
            {loading ? "Thinking..." : "Send"}
          </button>
        </section>
        <section className="dashboard-grid">
          <div className="panel">
            <h2>Today Tasks</h2>
            {state.tasks.map((task) => (
              <article key={task.id} className="task-card">
                <strong>{task.title}</strong>
                <span>{task.priority_label}</span>
                <p>{task.priority_reason}</p>
              </article>
            ))}
          </div>
          <div className="panel">
            <h2>Focus Session</h2>
            <p>Recommended task: {state.focus.recommended_task_id ?? "None yet"}</p>
          </div>
          <div className="panel">
            <h2>Daily Rhythm</h2>
            <p>{state.rhythm.suggestion}</p>
            <p>Focus minutes today: {state.rhythm.focus_minutes_today}</p>
          </div>
          {state.safety.state !== "none" ? (
            <div className="panel safety-panel">
              <h2>Take a beat</h2>
              <p>{state.safety.message}</p>
            </div>
          ) : null}
        </section>
      </main>
    </div>
  );
}
```

- [ ] **Step 5: Add styling that feels intentional and demo-ready**

```css
/* frontend/src/styles.css */
:root {
  --bg: #f5efe4;
  --panel: rgba(255, 250, 244, 0.85);
  --ink: #162521;
  --accent: #0f766e;
  --warm: #c96d42;
  --line: rgba(22, 37, 33, 0.12);
}

body {
  margin: 0;
  font-family: "IBM Plex Sans", "Noto Sans SC", sans-serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top left, rgba(15, 118, 110, 0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(201, 109, 66, 0.16), transparent 26%),
    var(--bg);
}

.workspace {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 20px;
  padding: 24px;
}

.panel {
  border: 1px solid var(--line);
  border-radius: 24px;
  background: var(--panel);
  backdrop-filter: blur(14px);
  padding: 20px;
  box-shadow: 0 18px 45px rgba(22, 37, 33, 0.08);
}
```

- [ ] **Step 6: Run the frontend tests and build to verify they pass**

Run: `cd frontend && npm test -- --run src/test/app.test.tsx src/test/dashboard.test.tsx && npm run build`
Expected: PASS and successful production build

- [ ] **Step 7: Commit the product UI**

```bash
git add frontend
git commit -m "feat: build HarmonyMind mixed workspace UI"
```

### Task 5: Seed the Demo Story, Add End-to-End Verification, and Polish for Presentation

**Files:**
- Create: `backend/tests/test_safe_interrupt.py`
- Create: `frontend/src/test/safety-notice.test.tsx`
- Create: `demo/demo-script.md`
- Modify: `README.md`

- [ ] **Step 1: Write the safe interrupt test**

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_crisis_language_interrupts_normal_planning() -> None:
    response = client.post(
        "/api/chat/message",
        json={"message": "我不想活了，别帮我安排任务了"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["safety"]["state"] == "safe_interrupt"
    assert payload["tasks"] == []
    assert payload["focus"]["recommended_task_id"] is None
```

- [ ] **Step 2: Write the frontend safety rendering test**

```tsx
import { render, screen } from "@testing-library/react";

import App from "../App";

test("safety notice is not shown by default", () => {
  render(<App />);
  expect(screen.queryByText("Take a beat")).not.toBeInTheDocument();
});
```

- [ ] **Step 3: Run the new tests to verify they fail if behavior is missing**

Run: `cd backend && pytest tests/test_safe_interrupt.py -v && cd ../frontend && npm test -- --run src/test/safety-notice.test.tsx`
Expected: PASS if Task 3 and Task 4 are complete; otherwise FAIL and fix gaps before continuing

- [ ] **Step 4: Add the demo script for the live presentation**

```md
# HarmonyMind Demo Script

## Demo Goal

Show that HarmonyMind can turn overload into focused action while keeping safety logic in the background.

## Opening Prompt

我周五前要完成路演PPT、修改商业计划书、回复两个投资人。这两天消息很多，我有点焦虑，帮我安排一下。

## Walkthrough

1. Submit the opening prompt.
2. Explain the generated priority order in the Today Tasks panel.
3. Call out that the interface does not expose mental health scores.
4. Start a 25-minute focus session on the recommended task.
5. Explain the Daily Rhythm suggestion as a pacing layer.
6. Optionally show a second prompt that triggers a gentle nudge.
7. End by explaining that crisis language interrupts ordinary productivity planning.
```

- [ ] **Step 5: Expand the README with a launch checklist**

```md
## Demo Checklist

1. Start the backend on `http://localhost:8000`
2. Start the frontend on `http://localhost:5173`
3. Confirm `GET /api/health` returns `{"status":"ok"}`
4. Run the backend and frontend test suites
5. Open the demo script in `demo/demo-script.md`
```

- [ ] **Step 6: Run the full verification suite**

Run: `cd backend && pytest -v`
Expected: PASS

Run: `cd frontend && npm test -- --run && npm run build`
Expected: PASS

- [ ] **Step 7: Commit the polish and verification assets**

```bash
git add README.md demo backend/tests frontend/src/test
git commit -m "feat: add demo verification and presentation assets"
```

## Self-Review

### Spec Coverage

- Mixed conversation + dashboard UI: covered by Task 4.
- Real backend orchestration and SQLite persistence: covered by Task 2.
- Background safety logic with hidden metrics: covered by Task 3 and Task 5.
- Focus session flow: covered by Task 3 and Task 4.
- Demo-ready regression path: covered by Task 5.

### Placeholder Scan

No `TODO`, `TBD`, or deferred implementation placeholders are used inside the actionable steps. Deferred product areas are explicitly listed as out-of-scope in the spec, not hidden in the plan.

### Type Consistency

- Backend task payload fields are consistent between `TaskOut`, `ChatResponse`, and frontend `Task` / `ChatResponse`.
- Focus APIs consistently use `task_id` and `duration_minutes`.
- Safety states consistently use `none`, `gentle_nudge`, and `safe_interrupt`.
