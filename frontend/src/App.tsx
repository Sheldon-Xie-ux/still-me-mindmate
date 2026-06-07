import { useEffect, useState } from "react";

import { ConversationPanel } from "./components/ConversationPanel";
import { CurrentPriorityCard } from "./components/CurrentPriorityCard";
import { NextActionCard } from "./components/NextActionCard";
import { ResearchLab } from "./components/ResearchLab";
import { SafetyNotice } from "./components/SafetyNotice";
import { SystemObservationCard } from "./components/SystemObservationCard";
import { TodayTasks } from "./components/TodayTasks";
import { getHealth, sendChatMessage, startFocusSession } from "./lib/api";
import type { ChatResponse, FocusSession } from "./types";

export default function App() {
  const [healthStatus, setHealthStatus] = useState("Backend not checked yet.");
  const [draft, setDraft] = useState("");
  const [dashboard, setDashboard] = useState<ChatResponse | null>(null);
  const [activeSession, setActiveSession] = useState<FocusSession | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isStartingFocus, setIsStartingFocus] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [activeView, setActiveView] = useState<"workspace" | "research">("workspace");

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

    if (!message) {
      return;
    }

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

  async function handleStartFocus(taskId: number) {
    setIsStartingFocus(true);
    setErrorMessage("");

    try {
      const session = await startFocusSession(taskId, 25);
      setActiveSession(session);
    } catch {
      setErrorMessage("专注模式暂时无法启动，请稍后再试。");
    } finally {
      setIsStartingFocus(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">以判断为先的代理工作台</p>
          <h1>HarmonyMind</h1>
        </div>
        <p className="status">{healthStatus}</p>
        <div className="view-switcher" aria-label="Primary view">
          <button
            type="button"
            className={activeView === "workspace" ? "switch-active" : ""}
            onClick={() => setActiveView("workspace")}
          >
            Agent Workspace
          </button>
          <button
            type="button"
            className={activeView === "research" ? "switch-active" : ""}
            onClick={() => setActiveView("research")}
          >
            Research Lab
          </button>
        </div>
      </header>

      {errorMessage ? (
        <section className="inline-error" aria-live="polite">
          {errorMessage}
        </section>
      ) : null}

      {activeView === "workspace" ? (
        <section className="workspace">
          <ConversationPanel
            draft={draft}
            reply={dashboard?.reply ?? ""}
            loading={isSubmitting}
            onDraftChange={setDraft}
            onSubmit={handleSubmit}
          />

          <section className="right-rail">
            <CurrentPriorityCard
              currentPriority={dashboard?.current_priority ?? null}
              tasks={dashboard?.tasks ?? []}
              focus={dashboard?.focus ?? null}
            />
            <NextActionCard
              focus={dashboard?.focus ?? null}
              nextAction={dashboard?.next_action ?? null}
              tasks={dashboard?.tasks ?? []}
              activeSession={activeSession}
              starting={isStartingFocus}
              onStartFocus={handleStartFocus}
            />
            <SystemObservationCard
              systemObservation={dashboard?.system_observation ?? null}
              rhythm={dashboard?.rhythm ?? null}
            />
            <SafetyNotice safety={dashboard?.safety ?? null} />
            <TodayTasks tasks={dashboard?.tasks ?? []} />
          </section>
        </section>
      ) : (
        <ResearchLab />
      )}
    </main>
  );
}
