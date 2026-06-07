import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

describe("safety notice", () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);

    fetchMock.mockImplementation(async (input) => {
      const url = String(input);

      if (url.endsWith("/api/health")) {
        return new Response(JSON.stringify({ status: "ok" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }

      throw new Error(`Unexpected fetch call to ${url}`);
    });
  });

  it("does not show the safety notice by default", () => {
    render(<App />);

    expect(screen.queryByText("温和提醒")).not.toBeInTheDocument();
  });
});
