# HarmonyMind Agentic Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Shift HarmonyMind from a visible task-sorting interface to an agent-style workspace that internally prioritizes and presents one current priority, one next action, and one system observation surface.

**Architecture:** Keep the existing backend judgment engine and persistence in place, but change the UI presentation first so the product feels agentic immediately. Then evolve the backend contract from `tasks/focus/rhythm/safety` toward `current_priority/next_action/system_observation/supporting_items` without breaking the working demo path.

**Tech Stack:** React, TypeScript, Vite, FastAPI, Python, SQLModel, pytest, Vitest, Testing Library

---

### Task 1: Reframe the Existing UI Around Agent Judgment

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/ConversationPanel.tsx`
- Create: `frontend/src/components/CurrentPriorityCard.tsx`
- Create: `frontend/src/components/NextActionCard.tsx`
- Create: `frontend/src/components/SystemObservationCard.tsx`
- Modify: `frontend/src/components/TodayTasks.tsx`
- Modify: `frontend/src/components/SafetyNotice.tsx`
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/test/app.test.tsx`
- Modify: `frontend/src/test/dashboard.test.tsx`

- [ ] **Step 1: Write the failing UI expectation update**

```tsx
import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "../App";

describe("App", () => {
  it("renders the agent-oriented Chinese shell", () => {
    vi.stubGlobal("fetch", vi.fn(async () =>
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    ) as typeof fetch);

    render(<App />);

    expect(screen.getByRole("heading", { name: "HarmonyMind" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "当前最重要的一件事" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "现在就开始" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "系统观察" })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run the frontend test to verify it fails**

Run: `cd frontend && npm test -- --run src/test/app.test.tsx`
Expected: FAIL because the current UI still renders `今日任务 / 专注模式 / 今日节奏`

- [ ] **Step 3: Create agent-oriented cards and rewire App layout**

```tsx
// frontend/src/components/CurrentPriorityCard.tsx
import type { ChatResponse } from "../types";

interface CurrentPriorityCardProps {
  dashboard: ChatResponse | null;
}

export function CurrentPriorityCard({ dashboard }: CurrentPriorityCardProps) {
  const topTask = dashboard?.tasks?.[0] ?? null;

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">判断</p>
          <h2>当前最重要的一件事</h2>
        </div>
      </div>

      {topTask ? (
        <>
          <p className="priority-headline">{topTask.title}</p>
          <p className="priority-reason">{topTask.priority_reason}</p>
        </>
      ) : (
        <div className="empty-state">
          <p>我还没有形成当前判断。</p>
          <span>告诉我你现在的近况、目标或限制，我会先判断最值得推进的一件事。</span>
        </div>
      )}
    </section>
  );
}
```

```tsx
// frontend/src/components/NextActionCard.tsx
import type { ChatResponse } from "../types";

interface NextActionCardProps {
  dashboard: ChatResponse | null;
}

export function NextActionCard({ dashboard }: NextActionCardProps) {
  const topTask = dashboard?.tasks?.[0] ?? null;

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">行动</p>
          <h2>现在就开始</h2>
        </div>
      </div>

      {topTask ? (
        <p className="next-action-copy">
          先从“{topTask.title}”开始，把第一步缩小到 5 分钟内就能启动的动作。
        </p>
      ) : (
        <div className="empty-state">
          <p>还没有可执行的第一步。</p>
          <span>一旦我判断出当前最重要事项，这里会直接告诉你怎么开始。</span>
        </div>
      )}
    </section>
  );
}
```

```tsx
// frontend/src/components/SystemObservationCard.tsx
import type { ChatResponse } from "../types";

interface SystemObservationCardProps {
  dashboard: ChatResponse | null;
}

export function SystemObservationCard({ dashboard }: SystemObservationCardProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">观察</p>
          <h2>系统观察</h2>
        </div>
      </div>

      {dashboard ? (
        <>
          <p className="rhythm-suggestion">{dashboard.rhythm.suggestion}</p>
          <div className="rhythm-stats">
            <article>
              <strong>{dashboard.rhythm.focus_minutes_today} 分钟</strong>
              <span>今日专注时长</span>
            </article>
            <article>
              <strong>{dashboard.rhythm.completed_tasks_today}</strong>
              <span>今日完成任务</span>
            </article>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p>系统还没有足够信息形成观察。</p>
          <span>收到你的上下文后，我会在这里给出节奏和负载上的温和建议。</span>
        </div>
      )}
    </section>
  );
}
```

- [ ] **Step 4: Rephrase the conversation side so it invites context, not task entry**

```tsx
// frontend/src/components/ConversationPanel.tsx
interface ConversationPanelProps {
  draft: string;
  reply: string;
  loading: boolean;
  onDraftChange: (value: string) => void;
  onSubmit: () => void;
}

export function ConversationPanel({
  draft,
  reply,
  loading,
  onDraftChange,
  onSubmit,
}: ConversationPanelProps) {
  return (
    <section className="panel panel-conversation">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">工作台</p>
          <h2>告诉我现在发生了什么</h2>
        </div>
      </div>

      <div className="assistant-reply" aria-live="polite">
        <p className="assistant-label">系统判断</p>
        <p>
          {reply ||
            "你可以直接说近况、目标、限制，或者当前最卡的一件事。我会先判断现在最重要的事情，再给你一个可立即开始的动作。"}
        </p>
      </div>

      <label className="composer">
        <span className="sr-only">上下文输入</span>
        <textarea
          value={draft}
          onChange={(event) => onDraftChange(event.target.value)}
          placeholder="你可以直接说近况、目标、限制，或者当前最卡的一件事"
          rows={6}
        />
      </label>

      <div className="composer-actions">
        <p className="composer-hint">系统会把优先级判断内化在后台，只把当前结论和下一步动作呈现给你。</p>
        <button type="button" onClick={onSubmit} disabled={loading || draft.trim().length === 0}>
          {loading ? "分析中..." : "开始判断"}
        </button>
      </div>
    </section>
  );
}
```

- [ ] **Step 5: Demote the visible task list into a supporting section**

```tsx
// frontend/src/components/TodayTasks.tsx
import type { TaskItem } from "../types";

interface TodayTasksProps {
  tasks: TaskItem[];
}

export function TodayTasks({ tasks }: TodayTasksProps) {
  if (tasks.length === 0) {
    return null;
  }

  return (
    <section className="panel supporting-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">支撑信息</p>
          <h2>提取到的事项</h2>
        </div>
        <span className="pill">{tasks.length} 项</span>
      </div>

      <div className="task-list compact">
        {tasks.map((task) => (
          <article key={task.id} className="task-card">
            <div className="task-card-top">
              <h3>{task.title}</h3>
              <span className={`priority-chip priority-${task.priority_label.toLowerCase()}`}>
                {task.priority_label.toUpperCase()}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
```

- [ ] **Step 6: Update `App.tsx` to render the new cards**

```tsx
// frontend/src/App.tsx
import { useEffect, useState } from "react";

import { ConversationPanel } from "./components/ConversationPanel";
import { CurrentPriorityCard } from "./components/CurrentPriorityCard";
import { NextActionCard } from "./components/NextActionCard";
import { SafetyNotice } from "./components/SafetyNotice";
import { SystemObservationCard } from "./components/SystemObservationCard";
import { TodayTasks } from "./components/TodayTasks";
import { getHealth, sendChatMessage } from "./lib/api";
import type { ChatResponse } from "./types";

export default function App() {
  const [healthStatus, setHealthStatus] = useState("后端状态：检测中");
  const [draft, setDraft] = useState("");
  const [dashboard, setDashboard] = useState<ChatResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let active = true;

    getHealth()
      .then((response) => {
        if (active) {
          setHealthStatus(response.status === "ok" ? "后端状态：正常" : `后端状态：${response.status}`);
        }
      })
      .catch(() => {
        if (active) {
          setHealthStatus("后端状态：不可用");
        }
      });

    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit() {
    const message = draft.trim();
    if (!message) return;

    setIsSubmitting(true);
    setErrorMessage("");

    try {
      const response = await sendChatMessage(message);
      setDashboard(response);
      setDraft("");
    } catch {
      setErrorMessage("当前无法连接后端服务，请稍后再试。");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">专注优先的效率助手</p>
          <h1>HarmonyMind</h1>
        </div>
        <p className="status">{healthStatus}</p>
      </header>

      <SafetyNotice safety={dashboard?.safety ?? null} />

      {errorMessage ? <section className="inline-error">{errorMessage}</section> : null}

      <section className="workspace">
        <ConversationPanel
          draft={draft}
          reply={dashboard?.reply ?? ""}
          loading={isSubmitting}
          onDraftChange={setDraft}
          onSubmit={handleSubmit}
        />

        <section className="right-rail">
          <CurrentPriorityCard dashboard={dashboard} />
          <NextActionCard dashboard={dashboard} />
          <SystemObservationCard dashboard={dashboard} />
          <TodayTasks tasks={dashboard?.tasks ?? []} />
        </section>
      </section>
    </main>
  );
}
```

- [ ] **Step 7: Run frontend tests and build to verify the redesign passes**

Run: `cd frontend && npm test -- --run src/test/app.test.tsx src/test/dashboard.test.tsx src/test/safety-notice.test.tsx && npm run build`
Expected: PASS

- [ ] **Step 8: Commit the UI reframing work**

```bash
git add frontend/src frontend/package.json frontend/package-lock.json
git commit -m "feat: reframe HarmonyMind as an agent workspace"
```

### Task 2: Add Explicit Agent-Centered Backend Fields Without Breaking the Current Frontend

**Files:**
- Modify: `backend/app/schemas.py`
- Modify: `backend/app/services/chat_service.py`
- Create: `backend/tests/test_agent_response_shape.py`

- [ ] **Step 1: Write the failing response-shape test**

```python
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_response_includes_agent_centered_fields() -> None:
    response = client.post(
        "/api/chat/message",
        json={"message": "周五前要路演，这两天消息很多，我有点乱。"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_priority"]["title"]
    assert payload["current_priority"]["reason"]
    assert payload["next_action"]["label"]
    assert payload["system_observation"]["suggestion"]
```

- [ ] **Step 2: Run the backend test to verify it fails**

Run: `cd backend && ./.venv/bin/python -m pytest backend/tests/test_agent_response_shape.py -v`
Expected: FAIL because the current chat response does not include these fields

- [ ] **Step 3: Extend the backend response schema with transitional agent fields**

```python
# backend/app/schemas.py
from pydantic import BaseModel


class CurrentPriorityPayload(BaseModel):
    title: str | None
    reason: str | None


class NextActionPayload(BaseModel):
    label: str | None
    detail: str | None


class SystemObservationPayload(BaseModel):
    suggestion: str
    safety_state: str
    message: str | None


class ChatResponse(BaseModel):
    reply: str
    tasks: list[TaskOut]
    focus: FocusRecommendation
    rhythm: RhythmPayload
    safety: SafetyPayload
    current_priority: CurrentPriorityPayload
    next_action: NextActionPayload
    system_observation: SystemObservationPayload
```

- [ ] **Step 4: Populate the new fields in `chat_service.py`**

```python
# backend/app/services/chat_service.py
from app.schemas import (
    ChatResponse,
    CurrentPriorityPayload,
    FocusRecommendation,
    NextActionPayload,
    RhythmPayload,
    SafetyPayload,
    SystemObservationPayload,
    TaskOut,
)


def build_chat_response(session: Session, message: str) -> ChatResponse:
    analytics = touch_analytics(session)
    safety_result = evaluate_safety_state(message, analytics.uninterrupted_minutes)

    if safety_result["state"] == "safe_interrupt":
        return ChatResponse(
            reply=safety_result["message"] or "我先陪你停一下。",
            tasks=[],
            focus=FocusRecommendation(recommended_task_id=None, summary="现在先不安排焦点任务。"),
            rhythm=RhythmPayload(focus_minutes_today=analytics.focus_minutes_today, completed_tasks_today=0, suggestion="先暂停普通规划。"),
            safety=SafetyPayload(state="safe_interrupt", message=safety_result["message"]),
            current_priority=CurrentPriorityPayload(title=None, reason="当前先以安全响应为先。"),
            next_action=NextActionPayload(label="先联系现实中的支持", detail="请联系你信任的人，或尽快联系当地紧急援助与心理支持资源。"),
            system_observation=SystemObservationPayload(
                suggestion="系统已暂停普通任务判断。",
                safety_state="safe_interrupt",
                message=safety_result["message"],
            ),
        )

    tasks = upsert_tasks_from_message(session, message)
    top_task = tasks[0] if tasks else None
    top_reason = top_task.priority_reason if top_task else None
    next_action_label = f"先推进“{top_task.title}”" if top_task else None
    next_action_detail = (
        f"先把“{top_task.title}”缩成一个 5 分钟内就能开始的动作。"
        if top_task
        else "先补充一点上下文，我再给出更稳的下一步。"
    )
    suggestion = safety_result["message"] or "先收窄范围，只推进当前判断最重要的一件事。"

    return ChatResponse(
        reply=(
            f"我判断你现在最该先推进的是“{top_task.title}”。"
            if top_task
            else "我已经收到你的情况，但还需要更多上下文来判断当前最重要的一件事。"
        ),
        tasks=[TaskOut.model_validate(task, from_attributes=True) for task in tasks],
        focus=FocusRecommendation(
            recommended_task_id=top_task.id if top_task else None,
            summary=f"建议先处理：{top_task.title}" if top_task else "暂时没有推荐焦点任务。",
        ),
        rhythm=RhythmPayload(
            focus_minutes_today=analytics.focus_minutes_today,
            completed_tasks_today=0,
            suggestion=suggestion,
        ),
        safety=SafetyPayload(
            state=safety_result["state"],
            message=safety_result["message"],
        ),
        current_priority=CurrentPriorityPayload(
            title=top_task.title if top_task else None,
            reason=top_reason,
        ),
        next_action=NextActionPayload(
            label=next_action_label,
            detail=next_action_detail,
        ),
        system_observation=SystemObservationPayload(
            suggestion=suggestion,
            safety_state=safety_result["state"],
            message=safety_result["message"],
        ),
    )
```

- [ ] **Step 5: Run the backend tests to verify the new contract passes**

Run: `cd backend && ./.venv/bin/python -m pytest backend/tests/test_agent_response_shape.py backend/tests`
Expected: PASS

- [ ] **Step 6: Commit the backend contract evolution**

```bash
git add backend/app backend/tests
git commit -m "feat: add agent-centered HarmonyMind response fields"
```

### Task 3: Make the Frontend Use the New Agent-Centered Fields First

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/components/CurrentPriorityCard.tsx`
- Modify: `frontend/src/components/NextActionCard.tsx`
- Modify: `frontend/src/components/SystemObservationCard.tsx`
- Modify: `frontend/src/test/dashboard.test.tsx`

- [ ] **Step 1: Write the failing dashboard expectation for the new fields**

```tsx
expect(screen.getByText("当前最重要的一件事")).toBeInTheDocument();
expect(screen.getByText("现在就开始")).toBeInTheDocument();
expect(screen.getByText("系统观察")).toBeInTheDocument();
expect(screen.getByText("发送投资人更新")).toBeInTheDocument();
expect(screen.getByText("先打开邮件草稿，把进展摘要写成三句")).toBeInTheDocument();
```

- [ ] **Step 2: Run the dashboard test to verify it fails**

Run: `cd frontend && npm test -- --run src/test/dashboard.test.tsx`
Expected: FAIL because the current cards still infer content from `tasks` and `rhythm`

- [ ] **Step 3: Extend `types.ts` with the new response fields**

```ts
// frontend/src/types.ts
export interface CurrentPriorityPayload {
  title: string | null;
  reason: string | null;
}

export interface NextActionPayload {
  label: string | null;
  detail: string | null;
}

export interface SystemObservationPayload {
  suggestion: string;
  safety_state: string;
  message: string | null;
}

export interface ChatResponse {
  reply: string;
  tasks: TaskItem[];
  focus: FocusRecommendation;
  rhythm: RhythmPayload;
  safety: SafetyPayload;
  current_priority: CurrentPriorityPayload;
  next_action: NextActionPayload;
  system_observation: SystemObservationPayload;
}
```

- [ ] **Step 4: Refactor the agent cards to use explicit fields**

```tsx
// frontend/src/components/CurrentPriorityCard.tsx
import type { ChatResponse } from "../types";

interface CurrentPriorityCardProps {
  dashboard: ChatResponse | null;
}

export function CurrentPriorityCard({ dashboard }: CurrentPriorityCardProps) {
  const currentPriority = dashboard?.current_priority ?? null;

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">判断</p>
          <h2>当前最重要的一件事</h2>
        </div>
      </div>

      {currentPriority?.title ? (
        <>
          <p className="priority-headline">{currentPriority.title}</p>
          <p className="priority-reason">{currentPriority.reason}</p>
        </>
      ) : (
        <div className="empty-state">
          <p>我还没有形成当前判断。</p>
          <span>告诉我你现在的近况、目标或限制，我会先判断最值得推进的一件事。</span>
        </div>
      )}
    </section>
  );
}
```

```tsx
// frontend/src/components/NextActionCard.tsx
import type { ChatResponse } from "../types";

interface NextActionCardProps {
  dashboard: ChatResponse | null;
}

export function NextActionCard({ dashboard }: NextActionCardProps) {
  const nextAction = dashboard?.next_action ?? null;

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">行动</p>
          <h2>现在就开始</h2>
        </div>
      </div>

      {nextAction?.label ? (
        <>
          <p className="next-action-label">{nextAction.label}</p>
          <p className="next-action-copy">{nextAction.detail}</p>
        </>
      ) : (
        <div className="empty-state">
          <p>还没有可执行的第一步。</p>
          <span>一旦我判断出当前最重要事项，这里会直接告诉你怎么开始。</span>
        </div>
      )}
    </section>
  );
}
```

```tsx
// frontend/src/components/SystemObservationCard.tsx
import type { ChatResponse } from "../types";

interface SystemObservationCardProps {
  dashboard: ChatResponse | null;
}

export function SystemObservationCard({ dashboard }: SystemObservationCardProps) {
  const observation = dashboard?.system_observation ?? null;
  const rhythm = dashboard?.rhythm ?? null;

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">观察</p>
          <h2>系统观察</h2>
        </div>
      </div>

      {observation && rhythm ? (
        <>
          <p className="rhythm-suggestion">{observation.suggestion}</p>
          <div className="rhythm-stats">
            <article>
              <strong>{rhythm.focus_minutes_today} 分钟</strong>
              <span>今日专注时长</span>
            </article>
            <article>
              <strong>{rhythm.completed_tasks_today}</strong>
              <span>今日完成任务</span>
            </article>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <p>系统还没有足够信息形成观察。</p>
          <span>收到你的上下文后，我会在这里给出节奏和负载上的温和建议。</span>
        </div>
      )}
    </section>
  );
}
```

- [ ] **Step 5: Run the frontend tests and build to verify the explicit agent contract works**

Run: `cd frontend && npm test -- --run && npm run build`
Expected: PASS

- [ ] **Step 6: Commit the frontend contract shift**

```bash
git add frontend/src
git commit -m "feat: surface agent judgment first in HarmonyMind UI"
```

## Self-Review

### Spec Coverage

- Right-side information architecture is addressed in Task 1.
- Left-side input reframing is addressed in Task 1.
- Backend transition from task-centered to agent-centered contract is addressed in Task 2.
- Frontend adoption of the new contract is addressed in Task 3.

### Placeholder Scan

No placeholder markers remain in the actionable steps. Transitional behavior is explicit and intentionally staged.

### Type Consistency

- The new backend fields in Task 2 match the frontend types in Task 3.
- The staged UI still tolerates retained `tasks`, `rhythm`, and `safety` fields while shifting emphasis to the new agent-centered payload.
