import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TimeSeriesDisplay from "../components/TimeSeriesDisplay";

global.IntersectionObserver = class {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
};

global.fetch = vi.fn(() =>
  Promise.resolve({
    json: () =>
      Promise.resolve({
        "Tweet 1": {
          class: "Positive",
          date: "2024-01-01",
          title: "Great News",
          description: "Tesla stock surges.",
        },
        "Tweet 2": {
          class: "Neutral",
          date: "2024-01-02",
          title: "Market Update",
          description: "No major changes.",
        },
        "Tweet 3": {
          class: "Negative",
          date: "2024-01-03",
          title: "Bad News",
          description: "Stock drops slightly.",
        },
      }),
  })
);

describe("TimeSeriesDisplay", () => {
  it("renders the timeline with correct data", async () => {
    render(<TimeSeriesDisplay />);

    // Warte, bis die Daten geladen wurden
    await waitFor(() => expect(fetch).toHaveBeenCalled());

    // Debug-Ausgabe des DOMs
    console.log(screen.debug());

    expect(screen.getByText("Great News")).toBeInTheDocument();
    expect(screen.getByText("Market Update")).toBeInTheDocument();
    expect(screen.getByText("Bad News")).toBeInTheDocument();
  });

  it("handles fetch error gracefully", async () => {
    fetch.mockRejectedValueOnce(new Error("Network Error"));

    render(<TimeSeriesDisplay />);

    await waitFor(() => {
      expect(screen.queryByText("Great News")).not.toBeInTheDocument();
    });
  });
});
