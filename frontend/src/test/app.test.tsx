import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "../App";

describe("App", () => {
  it("renders the HarmonyMind shell", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "HarmonyMind" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "当前最重要的一件事" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "现在就开始" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "系统观察" })).toBeInTheDocument();
  });
});
