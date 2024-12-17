import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TimeSeriesDisplay from "../components/timeSeriesDisplay.jsx";

global.IntersectionObserver = class {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
};

global.fetch = vi.fn(() =>
  Promise.resolve({
    json: () =>
      // Promise.resolve([{Class: "Positive"}, {Class: "Neutral"}])
      Promise.resolve([
        // "Tweet 1": {
        {
          Class: "Positive",
          Date: "2024-01-01",
          Title: "Great News",
          Text: "Tesla stock surges.",
        },
        // "Tweet 2": {
        {
          Class: "Neutral",
          Date: "2024-01-02",
          Title: "Market Update",
          Text: "No major changes.",
        },
        // "Tweet 3": {
        {
          Class: "Negative",
          Date: "2024-01-03",
          Title: "Bad News",
          Text: "Stock drops slightly.",
        },
      ]),
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
