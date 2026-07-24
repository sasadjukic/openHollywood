import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  BlueprintDecisionAction,
  ModelProfileSummary,
  ModelSelectionInput,
  RunBudgetPatch,
  RunControlAction,
  WorkspaceArtifact,
  WorkspaceRun,
} from "@open-hollywood/contracts";
import { useState } from "react";

import {
  fetchArtifactVersion,
  fetchModelCatalog,
  fetchModelProfiles,
  fetchProjects,
  fetchProjectWorkspace,
  fetchServiceStatus,
  fetchWorkflowEvents,
  controlRun,
  saveModelProfile,
  selectModelProfile,
  submitDecision,
} from "./api";
import { ArtifactInspector } from "./components/ArtifactInspector";
import { ModelSettings } from "./components/ModelSettings";
import { Timeline } from "./components/Timeline";

const serviceQueryKey = ["service-status"] as const;
const projectsQueryKey = ["projects"] as const;

export function App() {
  const queryClient = useQueryClient();
  const [requestedProjectId, setRequestedProjectId] = useState<string | null>(
    null,
  );
  const [requestedArtifactId, setRequestedArtifactId] = useState<string | null>(
    null,
  );
  const [requestedVersionId, setRequestedVersionId] = useState<string | null>(
    null,
  );
  const [instruction, setInstruction] = useState("");
  const [retryNode, setRetryNode] = useState("");
  const [isNavigationOpen, setNavigationOpen] = useState(false);
  const [isInspectorOpen, setInspectorOpen] = useState(false);
  const [isSettingsOpen, setSettingsOpen] = useState(false);

  const serviceStatus = useQuery({
    queryFn: fetchServiceStatus,
    queryKey: serviceQueryKey,
    retry: 1,
  });
  const projectsQuery = useQuery({
    queryFn: fetchProjects,
    queryKey: projectsQueryKey,
    retry: 1,
  });
  const modelProfilesQuery = useQuery({
    enabled: isSettingsOpen,
    queryFn: fetchModelProfiles,
    queryKey: ["model-profiles"],
  });
  const modelCatalogQuery = useQuery({
    enabled: isSettingsOpen,
    queryFn: fetchModelCatalog,
    queryKey: ["model-catalog"],
  });

  const projects = projectsQuery.data?.projects ?? [];
  const selectedProjectId =
    projects.find((project) => project.id === requestedProjectId)?.id ??
    projects[0]?.id ??
    null;

  const workspaceQuery = useQuery({
    enabled: selectedProjectId !== null,
    queryFn: () => {
      if (!selectedProjectId) {
        throw new Error("Select a project before loading its workspace.");
      }
      return fetchProjectWorkspace(selectedProjectId);
    },
    queryKey: ["workspace", selectedProjectId],
  });
  const workspace = workspaceQuery.data;
  const activeRun = workspace?.workflow_runs[0];
  const activeRunId = activeRun?.id ?? null;

  const eventsQuery = useQuery({
    enabled: activeRunId !== null,
    queryFn: () => {
      if (!activeRunId) {
        throw new Error("A workflow run is required to load events.");
      }
      return fetchWorkflowEvents(activeRunId);
    },
    queryKey: ["workflow-events", activeRunId],
    refetchInterval:
      activeRun?.status === "running" || activeRun?.status === "paused"
        ? 3_000
        : false,
  });

  const selectedArtifact =
    workspace?.artifacts.find(
      (artifact) => artifact.id === requestedArtifactId,
    ) ??
    workspace?.artifacts[0] ??
    null;
  const selectedArtifactId = selectedArtifact?.id ?? null;
  const selectedVersion =
    selectedArtifact?.versions.find(
      (version) => version.id === requestedVersionId,
    ) ??
    selectedArtifact?.versions.find(
      (version) => version.id === selectedArtifact.active_version_id,
    ) ??
    selectedArtifact?.versions[0] ??
    null;
  const selectedVersionId = selectedVersion?.id ?? null;

  const artifactDetailQuery = useQuery({
    enabled: selectedVersionId !== null,
    queryFn: () => {
      if (!selectedVersionId) {
        throw new Error("Select an artifact version before loading it.");
      }
      return fetchArtifactVersion(selectedVersionId);
    },
    queryKey: ["artifact-version", selectedVersionId],
  });

  const decisionMutation = useMutation({
    mutationFn: (action: BlueprintDecisionAction) => {
      if (!activeRun?.active_interrupt_id) {
        throw new Error("This run is not waiting for a human decision.");
      }
      const trimmedInstruction = instruction.trim();
      return submitDecision({
        action,
        decisionId: crypto.randomUUID(),
        instruction: action === "approve" ? undefined : trimmedInstruction,
        interruptId: activeRun.active_interrupt_id,
        workflowRunId: activeRun.id,
      });
    },
    onSuccess: async () => {
      setInstruction("");
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: projectsQueryKey }),
        queryClient.invalidateQueries({
          queryKey: ["workspace", selectedProjectId],
        }),
        queryClient.invalidateQueries({
          queryKey: ["workflow-events", activeRunId],
        }),
      ]);
    },
  });
  const runControlMutation = useMutation({
    mutationFn: ({
      action,
      budget,
      targetNode,
    }: {
      action: RunControlAction;
      budget?: RunBudgetPatch;
      targetNode?: string;
    }) => {
      if (!activeRun) {
        throw new Error("Select a workflow run before using run controls.");
      }
      return controlRun({
        action,
        budget,
        commandId: crypto.randomUUID(),
        targetNode,
        workflowRunId: activeRun.id,
      });
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: projectsQueryKey }),
        queryClient.invalidateQueries({
          queryKey: ["workspace", selectedProjectId],
        }),
        queryClient.invalidateQueries({
          queryKey: ["workflow-events", activeRunId],
        }),
      ]);
    },
  });
  const profileMutation = useMutation({
    mutationFn: async ({
      cloudModel,
      localModel,
      profile,
    }: {
      cloudModel: ModelSelectionInput | null;
      localModel: ModelSelectionInput | null;
      profile: ModelProfileSummary;
    }) => {
      await saveModelProfile(profile.id, {
        cloud_model: cloudModel,
        local_model: localModel,
      });
      return selectModelProfile(profile.id);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["model-profiles"] });
    },
  });

  const connectionState = serviceStatus.isPending
    ? "connecting"
    : serviceStatus.isError
      ? "unavailable"
      : "connected";

  if (projectsQuery.isPending) {
    return <WorkspaceLoading connectionState={connectionState} />;
  }

  if (projectsQuery.isError) {
    return (
      <WorkspaceUnavailable
        connectionState={connectionState}
        onRetry={() => void projectsQuery.refetch()}
      />
    );
  }

  if (projectsQuery.data.projects.length === 0) {
    return <EmptyLibrary connectionState={connectionState} />;
  }

  return (
    <div className="workspace-app">
      <Topbar
        connectionState={connectionState}
        onOpenNavigation={() => {
          setNavigationOpen(true);
        }}
        onOpenSettings={() => {
          setSettingsOpen(true);
        }}
      />

      <div className="workspace-grid">
        <nav
          className={`workspace-nav ${isNavigationOpen ? "workspace-nav--open" : ""}`}
          aria-label="Story projects and artifacts"
        >
          <div className="mobile-panel-header">
            <span>Story library</span>
            <button
              className="icon-button"
              type="button"
              onClick={() => {
                setNavigationOpen(false);
              }}
              aria-label="Close story navigation"
            >
              ×
            </button>
          </div>

          <section className="nav-section">
            <div className="nav-heading">
              <span>Stories</span>
              <span>{projectsQuery.data.projects.length}</span>
            </div>
            <div className="project-list">
              {projectsQuery.data.projects.map((project) => (
                <button
                  className={`project-button ${
                    project.id === selectedProjectId
                      ? "project-button--active"
                      : ""
                  }`}
                  key={project.id}
                  type="button"
                  onClick={() => {
                    setRequestedProjectId(project.id);
                    setRequestedArtifactId(null);
                    setRequestedVersionId(null);
                    setNavigationOpen(false);
                  }}
                >
                  <span
                    className={`project-status project-status--${
                      project.latest_workflow_status ?? "idle"
                    }`}
                    aria-hidden="true"
                  />
                  <span>
                    <strong>{project.name}</strong>
                    <small>
                      {project.artifact_count} artifacts ·{" "}
                      {humanize(
                        project.latest_workflow_status ?? "Not started",
                      )}
                    </small>
                  </span>
                </button>
              ))}
            </div>
          </section>

          <section className="nav-section nav-section--artifacts">
            <div className="nav-heading">
              <span>Story artifacts</span>
              <span>{workspace?.artifacts.length ?? 0}</span>
            </div>
            <div className="artifact-list">
              {workspace?.artifacts.map((artifact) => (
                <ArtifactButton
                  artifact={artifact}
                  isActive={artifact.id === selectedArtifactId}
                  key={artifact.id}
                  onClick={() => {
                    setRequestedArtifactId(artifact.id);
                    setRequestedVersionId(null);
                    setInspectorOpen(true);
                    setNavigationOpen(false);
                  }}
                />
              ))}
            </div>
          </section>

          <footer className="nav-footer">
            <span className="local-mark" aria-hidden="true">
              ●
            </span>
            <div>
              <strong>Stored on this device</strong>
              <span>SQLite · short prose</span>
            </div>
          </footer>
        </nav>

        <main className="story-workspace">
          {workspaceQuery.isPending && <StoryLoading />}
          {workspaceQuery.isError && (
            <section className="story-error">
              <p className="eyebrow">Workspace unavailable</p>
              <h1>The story could not be opened.</h1>
              <button
                type="button"
                onClick={() => void workspaceQuery.refetch()}
              >
                Try again
              </button>
            </section>
          )}
          {workspace && (
            <>
              <header className="story-header">
                <div>
                  <p className="story-kicker">
                    {humanize(workspace.project.story_format)}
                  </p>
                  <h1>{workspace.project.name}</h1>
                  <p>{workspace.project.description}</p>
                </div>
                <div className="run-summary">
                  <span
                    className={`run-status run-status--${activeRun?.status ?? "idle"}`}
                  >
                    {humanize(activeRun?.status ?? "idle")}
                  </span>
                  <small>
                    {activeRun?.current_node
                      ? `At ${humanize(activeRun.current_node)}`
                      : "Workspace ready"}
                  </small>
                </div>
              </header>

              {activeRun && (
                <RunControls
                  error={
                    runControlMutation.error instanceof Error
                      ? runControlMutation.error.message
                      : null
                  }
                  isPending={runControlMutation.isPending}
                  onCommand={(action, targetNode, budget) => {
                    runControlMutation.mutate({
                      action,
                      budget,
                      targetNode,
                    });
                  }}
                  onRetryNodeChange={setRetryNode}
                  retryNode={
                    retryNode.length > 0
                      ? retryNode
                      : (activeRun.retryable_nodes[0] ?? "")
                  }
                  run={activeRun}
                />
              )}

              <section className="conversation-panel">
                <Timeline
                  conversations={workspace.conversations}
                  events={eventsQuery.data?.events ?? []}
                />
              </section>

              {activeRun?.status === "paused" &&
                activeRun.active_interrupt_id && (
                  <DecisionComposer
                    error={
                      decisionMutation.error instanceof Error
                        ? decisionMutation.error.message
                        : null
                    }
                    instruction={instruction}
                    isPending={decisionMutation.isPending}
                    onChange={setInstruction}
                    onDecision={(action) => {
                      decisionMutation.mutate(action);
                    }}
                    onReview={() => {
                      setInspectorOpen(true);
                    }}
                  />
                )}
            </>
          )}
        </main>

        <ArtifactInspector
          artifact={selectedArtifact}
          detail={artifactDetailQuery.data}
          isLoading={artifactDetailQuery.isPending}
          isOpen={isInspectorOpen}
          onClose={() => {
            setInspectorOpen(false);
          }}
          onSelectVersion={setRequestedVersionId}
          selectedVersionId={selectedVersionId}
        />
      </div>

      {(isNavigationOpen || isInspectorOpen) && (
        <button
          className="panel-backdrop"
          type="button"
          aria-label="Close open panel"
          onClick={() => {
            setNavigationOpen(false);
            setInspectorOpen(false);
          }}
        />
      )}
      <ModelSettings
        catalog={modelCatalogQuery.data}
        error={
          profileMutation.error instanceof Error
            ? profileMutation.error.message
            : modelProfilesQuery.error instanceof Error
              ? modelProfilesQuery.error.message
              : modelCatalogQuery.error instanceof Error
                ? modelCatalogQuery.error.message
                : null
        }
        isCatalogLoading={modelCatalogQuery.isPending}
        isOpen={isSettingsOpen}
        isProfilesLoading={modelProfilesQuery.isPending}
        isSaving={profileMutation.isPending}
        onClose={() => {
          setSettingsOpen(false);
        }}
        onSaveAndActivate={(profile, localModel, cloudModel) => {
          profileMutation.mutate({ cloudModel, localModel, profile });
        }}
        profiles={modelProfilesQuery.data?.profiles ?? []}
      />
    </div>
  );
}

function Topbar({
  connectionState,
  onOpenNavigation,
  onOpenSettings,
}: {
  connectionState: "connected" | "connecting" | "unavailable";
  onOpenNavigation?: () => void;
  onOpenSettings?: () => void;
}) {
  return (
    <header className="topbar">
      {onOpenNavigation && (
        <button
          className="icon-button menu-button"
          type="button"
          onClick={onOpenNavigation}
          aria-label="Open story navigation"
        >
          ☰
        </button>
      )}
      <img
        className="brand-logo"
        src="/open_hollywood_logo_no_bg.png"
        alt="Open Hollywood"
      />
      <div className="topbar-meta">
        <span className={`connection connection--${connectionState}`}>
          <i aria-hidden="true" />
          {connectionState === "connected"
            ? "Local service"
            : connectionState === "connecting"
              ? "Connecting"
              : "Offline"}
        </span>
        <span className="version-label">v0.1</span>
        {onOpenSettings && (
          <button
            className="settings-button"
            type="button"
            onClick={onOpenSettings}
          >
            Model setup
          </button>
        )}
      </div>
    </header>
  );
}

function ArtifactButton({
  artifact,
  isActive,
  onClick,
}: {
  artifact: WorkspaceArtifact;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      className={`artifact-button ${isActive ? "artifact-button--active" : ""}`}
      type="button"
      onClick={onClick}
    >
      <span aria-hidden="true">{artifactGlyph(artifact.artifact_type)}</span>
      <span>
        <strong>{artifact.title}</strong>
        <small>
          {artifact.versions.length}{" "}
          {artifact.versions.length === 1 ? "version" : "versions"} ·{" "}
          {humanize(artifact.status)}
        </small>
      </span>
    </button>
  );
}

function RunControls({
  error,
  isPending,
  onCommand,
  onRetryNodeChange,
  retryNode,
  run,
}: {
  error: string | null;
  isPending: boolean;
  onCommand: (
    action: RunControlAction,
    targetNode?: string,
    budget?: RunBudgetPatch,
  ) => void;
  onRetryNodeChange: (node: string) => void;
  retryNode: string;
  run: WorkspaceRun;
}) {
  const callsUsed = numericValue(run.usage, "model_calls");
  const callsLimit = numericValue(run.budget, "max_model_calls");
  const costUsed = numericValue(run.usage, "cost_usd");
  const costLimit = numericValue(run.budget, "max_cost_usd");
  const tokensUsed =
    numericValue(run.usage, "input_tokens") +
    numericValue(run.usage, "output_tokens");
  const tokensLimit =
    numericValue(run.budget, "max_input_tokens") +
    numericValue(run.budget, "max_output_tokens");
  const canPause = run.status === "pending" || run.status === "running";
  const canResume =
    run.status === "paused" && run.pause_reason !== "human_approval";
  const canStop = !["cancelled", "succeeded"].includes(run.status);
  const canRetry =
    run.retryable_nodes.length > 0 &&
    ["paused", "failed", "cancelled", "succeeded"].includes(run.status);

  return (
    <section className="run-controls" aria-label="Workflow run controls">
      <div className="run-budget-summary">
        <span>
          Calls <strong>{callsUsed}</strong> / {callsLimit}
        </span>
        <span>
          Tokens <strong>{tokensUsed.toLocaleString()}</strong> /{" "}
          {tokensLimit.toLocaleString()}
        </span>
        <span>
          Cost <strong>${costUsed.toFixed(2)}</strong> / ${costLimit.toFixed(2)}
        </span>
      </div>
      <div className="run-control-actions">
        {canPause && (
          <button
            className="secondary-action"
            disabled={isPending}
            type="button"
            onClick={() => {
              onCommand("pause");
            }}
          >
            Pause
          </button>
        )}
        {canResume && (
          <button
            className="primary-action"
            disabled={isPending}
            type="button"
            onClick={() => {
              onCommand("resume");
            }}
          >
            Resume
          </button>
        )}
        {run.pause_reason === "budget" && (
          <button
            className="secondary-action"
            disabled={isPending}
            type="button"
            onClick={() => {
              const perCallInput = numericValue(
                run.budget,
                "per_call_input_tokens",
              );
              const perCallOutput = numericValue(
                run.budget,
                "per_call_output_tokens",
              );
              const perCallCost = numericValue(run.budget, "per_call_cost_usd");
              onCommand("update_budget", undefined, {
                max_cost_usd: costLimit + Math.max(1, perCallCost * 4),
                max_input_tokens:
                  numericValue(run.budget, "max_input_tokens") +
                  perCallInput * 4,
                max_model_calls: callsLimit + 4,
                max_output_tokens:
                  numericValue(run.budget, "max_output_tokens") +
                  perCallOutput * 4,
                max_wall_clock_seconds:
                  numericValue(run.budget, "max_wall_clock_seconds") + 1_800,
              });
            }}
          >
            Expand budget
          </button>
        )}
        {canRetry && (
          <label className="retry-control">
            <span>Retry from</span>
            <select
              disabled={isPending}
              value={retryNode}
              onChange={(event) => {
                onRetryNodeChange(event.target.value);
              }}
            >
              {run.retryable_nodes.map((node) => (
                <option key={node} value={node}>
                  {humanize(node)}
                </option>
              ))}
            </select>
            <button
              className="secondary-action"
              disabled={isPending || !retryNode}
              type="button"
              onClick={() => {
                onCommand("retry_from_node", retryNode);
              }}
            >
              Retry
            </button>
          </label>
        )}
        {canStop && (
          <button
            className="danger-action"
            disabled={isPending}
            type="button"
            onClick={() => {
              onCommand("stop");
            }}
          >
            Stop
          </button>
        )}
      </div>
      {run.pause_reason === "budget" && (
        <p className="run-control-note">
          This run paused before the next call could exceed its hard budget.
          Expand the limits, then resume when ready.
        </p>
      )}
      {error && <p className="decision-error">{error}</p>}
    </section>
  );
}

function numericValue(
  values: Record<string, number | string>,
  key: string,
): number {
  return Number(values[key] ?? 0);
}

function DecisionComposer({
  error,
  instruction,
  isPending,
  onChange,
  onDecision,
  onReview,
}: {
  error: string | null;
  instruction: string;
  isPending: boolean;
  onChange: (value: string) => void;
  onDecision: (action: BlueprintDecisionAction) => void;
  onReview: () => void;
}) {
  const hasInstruction = instruction.trim().length > 0;
  return (
    <section className="decision-composer" aria-labelledby="decision-heading">
      <div className="decision-heading">
        <span className="decision-mark" aria-hidden="true">
          ◇
        </span>
        <div>
          <p className="eyebrow">Human checkpoint</p>
          <h2 id="decision-heading">
            The Story Blueprint needs your decision.
          </h2>
        </div>
        <button className="text-button" type="button" onClick={onReview}>
          Review artifact
        </button>
      </div>
      <label>
        <span className="sr-only">Revision instruction</span>
        <textarea
          value={instruction}
          onChange={(event) => {
            onChange(event.target.value);
          }}
          placeholder="Describe a change, a new direction, or why this blueprint should be regenerated…"
          rows={3}
        />
      </label>
      <div className="decision-actions">
        <button
          className="secondary-action"
          type="button"
          disabled={!hasInstruction || isPending}
          onClick={() => {
            onDecision("revise");
          }}
        >
          Revise
        </button>
        <button
          className="secondary-action"
          type="button"
          disabled={!hasInstruction || isPending}
          onClick={() => {
            onDecision("reject");
          }}
        >
          Regenerate
        </button>
        <button
          className="secondary-action"
          type="button"
          disabled={!hasInstruction || isPending}
          onClick={() => {
            onDecision("fork");
          }}
        >
          Fork direction
        </button>
        <button
          className="primary-action"
          type="button"
          disabled={isPending}
          onClick={() => {
            onDecision("approve");
          }}
        >
          {isPending ? "Applying…" : "Approve blueprint"}
        </button>
      </div>
      {error && <p className="decision-error">{error}</p>}
    </section>
  );
}

function WorkspaceLoading({
  connectionState,
}: {
  connectionState: "connected" | "connecting" | "unavailable";
}) {
  return (
    <div className="workspace-app">
      <Topbar connectionState={connectionState} />
      <div className="workspace-loading" aria-label="Loading story library">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}

function StoryLoading() {
  return (
    <div className="story-loading" aria-label="Loading story workspace">
      <span />
      <span />
      <span />
    </div>
  );
}

function WorkspaceUnavailable({
  connectionState,
  onRetry,
}: {
  connectionState: "connected" | "connecting" | "unavailable";
  onRetry: () => void;
}) {
  return (
    <div className="workspace-app">
      <Topbar connectionState={connectionState} />
      <main className="global-state">
        <p className="eyebrow">Local service unavailable</p>
        <h1>Your story library is still safely stored on this device.</h1>
        <p>Start the Open Hollywood API, then reconnect to the workspace.</p>
        <button type="button" onClick={onRetry}>
          Retry connection
        </button>
      </main>
    </div>
  );
}

function EmptyLibrary({
  connectionState,
}: {
  connectionState: "connected" | "connecting" | "unavailable";
}) {
  return (
    <div className="workspace-app">
      <Topbar connectionState={connectionState} />
      <main className="global-state">
        <p className="eyebrow">Local story library</p>
        <h1>Every story starts with a spark.</h1>
        <p>
          Your first project will appear here as soon as a Story Blueprint run
          is created.
        </p>
        <div className="workflow-preview" aria-label="Open Hollywood workflow">
          <span>Premise</span>
          <span aria-hidden="true">→</span>
          <span>Blueprint approval</span>
          <span aria-hidden="true">→</span>
          <span>Autonomous draft</span>
        </div>
      </main>
    </div>
  );
}

function artifactGlyph(artifactType: string) {
  const glyphs: Record<string, string> = {
    character: "◎",
    creative_brief: "✦",
    critique: "△",
    location: "⌂",
    premise: "◌",
    relationship: "∞",
    story_blueprint: "▤",
    world_rule: "◇",
  };
  return glyphs[artifactType] ?? "□";
}

function humanize(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}
