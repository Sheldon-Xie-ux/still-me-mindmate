import type {
  ChatResponse,
  EvidenceCard,
  FocusSession,
  Hypothesis,
  ResearchBrief,
  ResearchQuestion,
  ResearchRunCreateResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getHealth() {
  return request<{ status: string }>("/api/health");
}

export function sendChatMessage(message: string) {
  return request<ChatResponse>("/api/chat/message", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export function startFocusSession(taskId: number, durationMinutes: number) {
  return request<FocusSession>("/api/focus/start", {
    method: "POST",
    body: JSON.stringify({
      task_id: taskId,
      duration_minutes: durationMinutes,
    }),
  });
}

export function getResearchQuestions() {
  return request<{ questions: ResearchQuestion[] }>("/api/research/questions");
}

export function startResearchRun(questionId: number) {
  return request<ResearchRunCreateResponse>("/api/research/runs", {
    method: "POST",
    body: JSON.stringify({
      question_id: questionId,
      mode: "fixture",
    }),
  });
}

export function getResearchEvidence(questionId?: number) {
  const query = questionId ? `?question_id=${questionId}` : "";
  return request<{ evidence: EvidenceCard[] }>(`/api/research/evidence${query}`);
}

export function getResearchHypotheses() {
  return request<{ hypotheses: Hypothesis[] }>("/api/research/hypotheses");
}

export function getResearchBrief() {
  return request<ResearchBrief>("/api/research/brief");
}
