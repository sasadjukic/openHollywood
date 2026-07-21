import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { client } from "@open-hollywood/contracts/client";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { App } from "./App";

function renderApp() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, retryDelay: 0 } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>,
  );
}

describe("App", () => {
  it("renders service metadata returned through the generated client", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          api_version: "0.1.0",
          service: "open-hollywood-api",
          state: "ok",
        }),
        { headers: { "Content-Type": "application/json" }, status: 200 },
      ),
    );
    client.setConfig({ baseUrl: "http://api.test", fetch: fetchMock });

    renderApp();

    expect(
      await screen.findByRole("heading", { name: "API connected" }),
    ).toBeInTheDocument();
    expect(screen.getByText("open-hollywood-api")).toBeInTheDocument();
    expect(screen.getByText("v0.1.0")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it("offers a retry when the local API cannot be reached", async () => {
    client.setConfig({
      baseUrl: "http://api.test",
      fetch: vi.fn().mockRejectedValue(new TypeError("Network unavailable")),
    });

    renderApp();

    expect(
      await screen.findByRole("heading", { name: "API unavailable" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Retry connection" }),
    ).toBeInTheDocument();
  });
});
