import "@testing-library/jest-dom/vitest";

import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

const questionsResponse = {
  questions: [
    {
      id: 1,
      title: "Does AI writing assistance reduce independent argument formation in students?",
      theme: "education",
      description: "Study student reasoning under AI writing assistance.",
      status: "queued",
      priority: 5,
      created_at: "2026-05-02T00:00:00Z",
      updated_at: "2026-05-02T00:00:00Z",
    },
  ],
};

const runResponse = {
  run_id: 7,
  status: "completed",
  evidence_created: 3,
  hypotheses_created: 2,
  hypotheses_updated: 0,
};

const evidenceResponse = {
  evidence: [
    {
      id: 11,
      question_id: 1,
      source_document_id: 21,
      claim: "AI-generated drafts can shift effort away from independent planning.",
      summary: "Learners benefit when they form an initial claim before seeing a complete AI draft.",
      stance: "supports",
      evidence_strength: 78,
      relevance_score: 88,
      risk_domain: "education",
      limitations: "Needs live literature before external claims.",
      created_at: "2026-05-02T00:00:00Z",
      source: {
        id: 21,
        url: "https://example.org/research/cognitive-offloading-ai-writing",
        title: "Cognitive Offloading and Generative Writing Assistance",
        authors: "Research Fixture",
        publisher: "MindMate Fixture Library",
        published_at: null,
        language: "en",
        source_type: "paper",
        snippet: "Generated drafts can reduce planning effort.",
        credibility_score: 82,
        retrieved_at: "2026-05-02T00:00:00Z",
      },
    },
  ],
};

const hypothesesResponse = {
  hypotheses: [
    {
      id: 31,
      title: "Require initial judgment before full AI answers",
      statement:
        "MindMate should ask users to state an initial judgment before revealing a complete AI recommendation.",
      theme: "judgment",
      status: "accepted",
      evidence_score: 76,
      product_value_score: 92,
      engineering_feasibility_score: 84,
      risk_sensitivity_score: 88,
      overall_score: 83.4,
      rationale: "Reflection-before-answer is a buildable cognitive protection pattern.",
      created_at: "2026-05-02T00:00:00Z",
      updated_at: "2026-05-02T00:00:00Z",
    },
  ],
};

const briefResponse = {
  title: "MindMate AutoResearch Brief",
  summary: "The strongest signal is to preserve human judgment before complete AI answers.",
  strongest_claims: ["Initial judgment before full answers protects agency."],
  open_questions: ["Which findings remain stable with live search?"],
  design_implications: ["Ask users for an initial judgment before full AI recommendations."],
  expert_review_queue: ["Mark child education claims for expert review"],
};

describe("Research Lab", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);

    fetchMock.mockImplementation(async (input, init) => {
      const url = String(input);

      if (url.endsWith("/api/health")) {
        return new Response(JSON.stringify({ status: "ok" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/questions")) {
        return new Response(JSON.stringify(questionsResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/runs")) {
        expect(init?.method).toBe("POST");
        return new Response(JSON.stringify(runResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.includes("/api/research/evidence")) {
        return new Response(JSON.stringify(evidenceResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/hypotheses")) {
        return new Response(JSON.stringify(hypothesesResponse), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      if (url.endsWith("/api/research/brief")) {
        return new Response(JSON.stringify(briefResponse), {
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

  it("runs a fixture research cycle and displays evidence, hypotheses, and brief", async () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Research Lab" }));

    expect(await screen.findByRole("heading", { name: "Research Lab" })).toBeInTheDocument();
    expect(await screen.findByText(questionsResponse.questions[0].title)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "运行研究" }));

    expect(await screen.findByText("本次新增证据 3 条")).toBeInTheDocument();

    const evidencePanel = screen.getByRole("heading", { name: "证据卡片" }).closest("section");
    expect(evidencePanel).not.toBeNull();
    expect(
      within(evidencePanel as HTMLElement).getByText(evidenceResponse.evidence[0].claim),
    ).toBeInTheDocument();
    expect(within(evidencePanel as HTMLElement).getByText("paper")).toBeInTheDocument();

    const hypothesisPanel = screen.getByRole("heading", { name: "高分假设" }).closest("section");
    expect(hypothesisPanel).not.toBeNull();
    expect(
      within(hypothesisPanel as HTMLElement).getByText(hypothesesResponse.hypotheses[0].title),
    ).toBeInTheDocument();
    expect(within(hypothesisPanel as HTMLElement).getByText("83.4")).toBeInTheDocument();

    expect(screen.getByText(briefResponse.summary)).toBeInTheDocument();

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/research\/runs$/),
        expect.objectContaining({ method: "POST" }),
      );
    });
  });
});
