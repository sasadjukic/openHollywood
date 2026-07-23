import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { client } from "@open-hollywood/contracts/client";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { App } from "./App";

const projectId = "11111111-1111-1111-1111-111111111111";
const runId = "22222222-2222-2222-2222-222222222222";
const artifactId = "33333333-3333-3333-3333-333333333333";
const versionId = "44444444-4444-4444-4444-444444444444";
const firstVersionId = "55555555-5555-5555-5555-555555555555";
const now = "2026-07-23T10:00:00Z";
const localProfileId = "00000000-0000-4000-8000-000000000131";

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

function configureWorkspaceApi() {
  const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const request = input instanceof Request ? input : null;
    const url = request?.url ?? requestUrl(input);
    const method = request?.method ?? init?.method ?? "GET";

    if (url.endsWith("/api/v1/health")) {
      return Promise.resolve(
        jsonResponse({
          api_version: "0.1.0",
          service: "open-hollywood-api",
          state: "ok",
        }),
      );
    }
    if (url.endsWith("/api/v1/projects")) {
      return Promise.resolve(
        jsonResponse({
          projects: [
            {
              artifact_count: 1,
              conversation_count: 1,
              description: "A supernatural horror story.",
              id: projectId,
              latest_workflow_run_id: runId,
              latest_workflow_status: "paused",
              name: "The Untouched Stroller",
              status: "active",
              story_format: "short_prose",
              updated_at: now,
            },
          ],
        }),
      );
    }
    if (url.endsWith("/api/v1/model-profiles") && method === "GET") {
      return Promise.resolve(jsonResponse(modelProfilesResponse()));
    }
    if (url.endsWith("/api/v1/models/catalog")) {
      return Promise.resolve(jsonResponse(modelCatalogResponse()));
    }
    if (
      url.endsWith(`/api/v1/model-profiles/${localProfileId}`) &&
      method === "PUT"
    ) {
      return Promise.resolve(
        jsonResponse({
          ...modelProfilesResponse().profiles[0],
          is_complete: true,
          local_model: localModel(),
        }),
      );
    }
    if (
      url.endsWith(`/api/v1/model-profiles/${localProfileId}/activate`) &&
      method === "POST"
    ) {
      return Promise.resolve(
        jsonResponse({
          ...modelProfilesResponse().profiles[0],
          is_complete: true,
          is_default: true,
          local_model: localModel(),
        }),
      );
    }
    if (url.includes(`/api/v1/projects/${projectId}/workspace`)) {
      return Promise.resolve(jsonResponse(workspaceResponse()));
    }
    if (url.includes(`/api/v1/workflow-runs/${runId}/events`)) {
      return Promise.resolve(
        jsonResponse({
          events: [
            {
              event_type: "workflow.awaiting_approval",
              id: 1,
              occurred_at: now,
              payload: {
                checkpoint: "story_blueprint",
                interrupt_id: "interrupt-1",
              },
              schema_version: "1",
              source: "approval",
              workflow_run_id: runId,
            },
          ],
          has_more: false,
          next_after: 1,
        }),
      );
    }
    if (url.includes(`/api/v1/artifact-versions/${versionId}`)) {
      return Promise.resolve(jsonResponse(artifactDetailResponse()));
    }
    if (
      url.includes(`/api/v1/workflow-runs/${runId}/decisions`) &&
      method === "POST"
    ) {
      return Promise.resolve(
        jsonResponse({
          artifacts: [],
          awaiting_approval: false,
          checkpoint_id: "checkpoint-approved",
          interrupt_id: null,
          workflow_run_id: runId,
        }),
      );
    }
    return Promise.resolve(new Response("Not found", { status: 404 }));
  });

  client.setConfig({ baseUrl: "http://api.test", fetch: fetchMock });
  return fetchMock;
}

describe("App", () => {
  it("renders the persisted three-panel story workspace", async () => {
    configureWorkspaceApi();

    renderApp();

    expect(
      await screen.findByRole("heading", { name: "The Untouched Stroller" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "A pristine stroller waits outside an abandoned building.",
      ),
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Story Blueprint ready for review"),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", {
        name: "A woman follows an immaculate stroller into a concrete ruin.",
      }),
    ).toBeInTheDocument();
    expect(screen.getByText("88.50/100")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        name: "The Story Blueprint needs your decision.",
      }),
    ).toBeInTheDocument();
  });

  it("requires guidance for revision and submits approval without it", async () => {
    const user = userEvent.setup();
    const fetchMock = configureWorkspaceApi();

    renderApp();

    const reviseButton = await screen.findByRole("button", { name: "Revise" });
    expect(reviseButton).toBeDisabled();

    await user.type(
      screen.getByPlaceholderText(/Describe a change/),
      "Make the ending less supernatural.",
    );
    expect(reviseButton).toBeEnabled();

    await user.click(screen.getByRole("button", { name: "Approve blueprint" }));

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.find(([input]) =>
          requestUrl(input).includes(`/workflow-runs/${runId}/decisions`),
        ),
      ).toBeDefined();
    });
    const decisionRequest = fetchMock.mock.calls.find(([input]) =>
      requestUrl(input).includes(`/workflow-runs/${runId}/decisions`),
    );
    const request = decisionRequest?.[0];
    expect(request).toBeInstanceOf(Request);
    await expect((request as Request).clone().json()).resolves.toMatchObject({
      action: "approve",
      interrupt_id: "interrupt-1",
    });
  });

  it("keeps the local-library recovery state when the API is unavailable", async () => {
    client.setConfig({
      baseUrl: "http://api.test",
      fetch: vi.fn((input: RequestInfo | URL) => {
        if (requestUrl(input).endsWith("/health")) {
          return Promise.resolve(
            jsonResponse({
              api_version: "0.1.0",
              service: "open-hollywood-api",
              state: "ok",
            }),
          );
        }
        return Promise.reject(new TypeError("Network unavailable"));
      }),
    });

    renderApp();

    expect(
      await screen.findByRole("heading", {
        name: "Your story library is still safely stored on this device.",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Retry connection" }),
    ).toBeInTheDocument();
  });

  it("configures and activates a discovered Local model preset", async () => {
    const user = userEvent.setup();
    const fetchMock = configureWorkspaceApi();
    renderApp();

    await user.click(
      await screen.findByRole("button", { name: "Model setup" }),
    );
    expect(
      await screen.findByRole("heading", {
        name: "Choose how the studio thinks.",
      }),
    ).toBeInTheDocument();
    expect(screen.getByText("2 models discovered")).toBeInTheDocument();

    const localCard = screen
      .getByRole("heading", { name: "Local" })
      .closest("article");
    if (!(localCard instanceof HTMLElement)) {
      throw new Error("Local preset card was not rendered.");
    }
    const localControls = within(localCard);
    const action = localControls.getByRole("button", {
      name: "Use Local",
    });
    expect(action).toBeDisabled();

    await user.selectOptions(
      localControls.getByRole("combobox", { name: "Local model" }),
      "ollama:local:qwen3:8b",
    );
    await user.click(action);

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(([input, init]) => {
          const request = input instanceof Request ? input : null;
          return (
            requestUrl(input).endsWith(
              `/model-profiles/${localProfileId}/activate`,
            ) && (request?.method ?? init?.method) === "POST"
          );
        }),
      ).toBe(true);
    });
  });
});

function workspaceResponse() {
  return {
    artifacts: [
      {
        active_version_id: versionId,
        artifact_key: "story-blueprint",
        artifact_type: "story_blueprint",
        id: artifactId,
        status: "draft",
        title: "Story Blueprint",
        versions: [
          {
            change_summary: "Sharpened the ending",
            created_at: now,
            id: versionId,
            model_identifier: "creative-model",
            parent_version_id: firstVersionId,
            provider: "ollama",
            schema_version: "1",
            specialist_role: "blueprint_integrator",
            version_number: 2,
          },
          {
            change_summary: "Initial blueprint",
            created_at: now,
            id: firstVersionId,
            model_identifier: "creative-model",
            parent_version_id: null,
            provider: "ollama",
            schema_version: "1",
            specialist_role: "blueprint_integrator",
            version_number: 1,
          },
        ],
      },
    ],
    conversations: [
      {
        id: "66666666-6666-6666-6666-666666666666",
        messages: [
          {
            content: "A pristine stroller waits outside an abandoned building.",
            created_at: "2026-07-23T09:55:00Z",
            id: "77777777-7777-7777-7777-777777777777",
            role: "user",
            sequence_number: 1,
            workflow_run_id: runId,
          },
          {
            content: "The Story Blueprint is ready for your review.",
            created_at: "2026-07-23T09:58:00Z",
            id: "88888888-8888-8888-8888-888888888888",
            role: "assistant",
            sequence_number: 2,
            workflow_run_id: runId,
          },
        ],
        status: "active",
        title: "Blueprint development",
      },
    ],
    project: {
      artifact_count: 1,
      conversation_count: 1,
      description: "A supernatural horror story.",
      id: projectId,
      latest_workflow_run_id: runId,
      latest_workflow_status: "paused",
      name: "The Untouched Stroller",
      status: "active",
      story_format: "short_prose",
      updated_at: now,
    },
    workflow_runs: [
      {
        active_interrupt_id: "interrupt-1",
        completed_at: null,
        current_node: "approval",
        error_code: null,
        error_message: null,
        graph_version: "2",
        id: runId,
        parent_workflow_run_id: null,
        started_at: "2026-07-23T09:54:00Z",
        status: "paused",
        updated_at: now,
        workflow_name: "story_blueprint",
      },
    ],
  };
}

function artifactDetailResponse() {
  const artifact = workspaceResponse().artifacts[0];
  if (!artifact) {
    throw new Error("The workspace fixture requires an artifact.");
  }
  return {
    artifact,
    content: {
      central_conflict:
        "She must decide whether the stroller is an invitation or a warning.",
      creative_brief: {
        genres: ["Supernatural horror"],
        maturity: "standard_fiction",
        tone: ["Uncanny", "Intimate"],
      },
      logline: "A woman follows an immaculate stroller into a concrete ruin.",
      proposed_ending: "She leaves the stroller untouched at sunrise.",
      story_arc: "A search for answers becomes an act of release.",
      thematic_thesis: "Grief makes ordinary objects into impossible doors.",
    },
    content_sha256: "2".repeat(64),
    evaluations: [
      {
        created_at: now,
        id: "99999999-9999-9999-9999-999999999999",
        rubric_name: "blueprint-quality",
        rubric_version: "1",
        scores: { originality: 5 },
        summary: "The central image and ending reinforce each other.",
        weighted_score: "88.50",
      },
    ],
    selected_version: artifact.versions[0],
  };
}

function modelProfilesResponse() {
  const roleAssignments = {
    blueprint_critic: "local",
    blueprint_integrator: "local",
    brief_architect: "local",
    character_architect: "local",
    premise_architect: "local",
    world_builder: "local",
  };
  return {
    profiles: [
      {
        cloud_model: null,
        created_at: now,
        description: "Keep every specialist on this device through Ollama.",
        id: localProfileId,
        is_complete: false,
        is_default: false,
        local_model: null,
        mode: "local",
        name: "Local",
        required_deployments: ["local"],
        role_assignments: roleAssignments,
        updated_at: now,
      },
      {
        cloud_model: null,
        created_at: now,
        description: "Use the selected cloud model for every specialist.",
        id: "00000000-0000-4000-8000-000000000132",
        is_complete: false,
        is_default: false,
        local_model: null,
        mode: "cloud",
        name: "Cloud",
        required_deployments: ["cloud"],
        role_assignments: Object.fromEntries(
          Object.keys(roleAssignments).map((role) => [role, "cloud"]),
        ),
        updated_at: now,
      },
      {
        cloud_model: null,
        created_at: now,
        description: "Keep routine work local and creative reasoning in cloud.",
        id: "00000000-0000-4000-8000-000000000133",
        is_complete: false,
        is_default: false,
        local_model: null,
        mode: "hybrid",
        name: "Hybrid",
        required_deployments: ["local", "cloud"],
        role_assignments: {
          ...roleAssignments,
          blueprint_integrator: "cloud",
          character_architect: "cloud",
          premise_architect: "cloud",
          world_builder: "cloud",
        },
        updated_at: now,
      },
    ],
  };
}

function modelCatalogResponse() {
  return {
    models: [
      {
        deployment: "local",
        digest: "local-digest",
        model_identifier: "qwen3:8b",
        parameter_size: "8.2B",
        provider: "ollama",
        quantization_level: "Q4_K_M",
        size_bytes: 5_000_000_000,
      },
      {
        deployment: "cloud",
        digest: null,
        model_identifier: "creative-cloud",
        parameter_size: null,
        provider: "ollama",
        quantization_level: null,
        size_bytes: null,
      },
    ],
    sources: [
      {
        detail: null,
        key: "ollama_local",
        label: "Ollama on this device",
        provider: "ollama",
        status: "available",
      },
    ],
  };
}

function localModel() {
  return {
    deployment: "local",
    model_identifier: "qwen3:8b",
    provider: "ollama",
  };
}

function jsonResponse(body: unknown) {
  return new Response(JSON.stringify(body), {
    headers: { "Content-Type": "application/json" },
    status: 200,
  });
}

function requestUrl(input: RequestInfo | URL) {
  if (typeof input === "string") {
    return input;
  }
  return input instanceof URL ? input.href : input.url;
}
