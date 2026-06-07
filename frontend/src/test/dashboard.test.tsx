import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

const healthResponse = { status: "ok" };
const chatResponse = {
  reply: "I turned that into a focused plan for today.",
  current_priority: {
    title: "先稳住续费用户沟通",
    reason: "这是今天最容易直接影响留存结果的一步，越早推进越有回旋空间。",
  },
  next_action: {
    label: "给三位高风险用户各发一条确认消息",
    detail: "先发出第一轮确认，再根据回复决定是否安排跟进电话。",
  },
  system_observation: {
    suggestion: "你现在更适合先做闭环动作，而不是继续整理更多素材。",
    safety_state: "gentle_nudge",
    message: "别再扩写计划了，先把最关键的外部信号拿回来。",
  },
  tasks: [
    {
      id: 101,
      title: "Send investor update",
      description: "Summarize milestones and blockers.",
      category: "communication",
      priority_score: 0.95,
      priority_label: "high",
      priority_reason: "Deadline is today and stakeholders are waiting.",
      status: "todo",
      due_date: null,
      estimated_minutes: 30,
      created_at: "2026-04-15T09:00:00Z",
      updated_at: "2026-04-15T09:00:00Z",
    },
  ],
  focus: {
    recommended_task_id: 101,
    summary: "Start with the investor update while the details are fresh.",
  },
  rhythm: {
    focus_minutes_today: 25,
    completed_tasks_today: 0,
    suggestion: "Protect one clean block before lunch.",
  },
  safety: {
    state: "none",
    message: null,
  },
};

describe("dashboard flow", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);

    fetchMock.mockImplementation(async (input, init) => {
      const url = String(input);

      if (url.endsWith("/api/health")) {
        return new Response(JSON.stringify(healthResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/chat/message")) {
        expect(init?.method).toBe("POST");
        expect(init?.body).toBe(JSON.stringify({ message: "Plan my top priority for today" }));

        return new Response(JSON.stringify(chatResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      throw new Error(`Unexpected fetch call to ${url}`);
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("submits context and updates the judgment-first dashboard", async () => {
    render(<App />);

    fireEvent.change(screen.getByPlaceholderText(/最近发生的情况、你想推进的目标/i), {
      target: { value: "Plan my top priority for today" },
    });
    fireEvent.click(screen.getByRole("button", { name: "开始判断" }));

    expect(await screen.findByText(chatResponse.reply)).toBeInTheDocument();
    const priorityPanel = screen
      .getByRole("heading", { name: "当前最重要的一件事" })
      .closest("section");

    expect(priorityPanel).not.toBeNull();
    expect(
      await within(priorityPanel as HTMLElement).findByRole("heading", {
        name: chatResponse.current_priority.title,
      }),
    ).toBeInTheDocument();
    expect(
      within(priorityPanel as HTMLElement).getByText(chatResponse.current_priority.reason),
    ).toBeInTheDocument();

    const nextActionPanel = screen.getByRole("heading", { name: "现在就开始" }).closest("section");

    expect(nextActionPanel).not.toBeNull();
    expect(within(nextActionPanel as HTMLElement).getByRole("heading", { name: chatResponse.next_action.label })).toBeInTheDocument();
    expect(within(nextActionPanel as HTMLElement).getByText(chatResponse.next_action.detail)).toBeInTheDocument();
    expect(within(nextActionPanel as HTMLElement).getByRole("button", { name: "开始专注" })).toBeInTheDocument();

    const observationPanel = screen.getByRole("heading", { name: "系统观察" }).closest("section");

    expect(observationPanel).not.toBeNull();
    expect(
      within(observationPanel as HTMLElement).getByText(chatResponse.system_observation.suggestion),
    ).toBeInTheDocument();
    expect(within(observationPanel as HTMLElement).getByText(chatResponse.system_observation.message)).toBeInTheDocument();
    expect(within(observationPanel as HTMLElement).getByText("25 分钟")).toBeInTheDocument();
    expect(within(observationPanel as HTMLElement).getByText("今日专注时长")).toBeInTheDocument();

    const tasksPanel = screen.getByRole("heading", { name: "任务全貌" }).closest("section");

    expect(tasksPanel).not.toBeNull();
    expect(within(tasksPanel as HTMLElement).getByText("作为判断依据保留，方便你随时核对。")).toBeInTheDocument();

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/chat\/message$/),
        expect.objectContaining({
          method: "POST",
        }),
      );
    });
  });
});
