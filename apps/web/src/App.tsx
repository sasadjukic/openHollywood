import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  BlueprintDecisionAction,
  ModelProfileSummary,
  ModelSelectionInput,
  ProjectExportFormat,
  ProjectList,
  ProjectSummary,
  RunBudgetPatch,
  RunControlAction,
  WorkspaceArtifact,
  WorkspaceRun,
  WorkflowEventEnvelope,
} from "@open-hollywood/contracts";
import { useEffect, useLayoutEffect, useRef, useState } from "react";

import {
  controlRun,
  fetchArtifactVersion,
  fetchModelCatalog,
  fetchModelProfiles,
  fetchProjects,
  fetchProjectExports,
  fetchProjectWorkspace,
  fetchServiceStatus,
  fetchWorkflowEvents,
  projectExportUrl,
  removeStoryProject,
  saveModelProfile,
  selectModelProfile,
  startStoryProject,
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
  const [requestedRunId, setRequestedRunId] = useState<string | null>(null);
  const [requestedArtifactId, setRequestedArtifactId] = useState<string | null>(
    null,
  );
  const [requestedVersionId, setRequestedVersionId] = useState<string | null>(
    null,
  );
  const [instruction, setInstruction] = useState("");
  const [premise, setPremise] = useState("");
  const [storyTitle, setStoryTitle] = useState("");
  const [retryNode, setRetryNode] = useState("");
  const [isCreatingStory, setCreatingStory] = useState(false);
  const [isNavigationOpen, setNavigationOpen] = useState(false);
  const [isInspectorOpen, setInspectorOpen] = useState(false);
  const [isSettingsOpen, setSettingsOpen] = useState(false);
  const intakeRequestId = useRef<string | null>(null);

  const serviceStatus = useQuery({
    queryFn: fetchServiceStatus,
    queryKey: serviceQueryKey,
    retry: 1,
  });
  const projectsQuery = useQuery({
    queryFn: fetchProjects,
    queryKey: projectsQueryKey,
    refetchInterval: (query) =>
      query.state.data?.projects.some((project) =>
        ["pending", "running"].includes(project.latest_workflow_status ?? ""),
      )
        ? 1_000
        : false,
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

  const projectList = projectsQuery.data?.projects ?? [];
  const selectedProjectId = isCreatingStory
    ? null
    : (projectList.find((project) => project.id === requestedProjectId)?.id ??
      projectList[0]?.id ??
      null);

  const workspaceQuery = useQuery({
    enabled: selectedProjectId !== null,
    queryFn: () => {
      if (!selectedProjectId) {
        throw new Error("Select a project before loading its workspace.");
      }
      return fetchProjectWorkspace(selectedProjectId);
    },
    queryKey: ["workspace", selectedProjectId],
    refetchInterval: (query) => {
      const latestRun = query.state.data?.workflow_runs[0];
      if (!latestRun) {
        return false;
      }
      if (latestRun.status === "pending" || latestRun.status === "running") {
        return 1_000;
      }
      return latestRun.workflow_name === "story_blueprint" &&
        latestRun.status === "succeeded"
        ? 1_000
        : false;
    },
  });
  const workspace = workspaceQuery.data;
  const workspaceLatestRun = workspace?.workflow_runs[0];
  const projects = projectList.map((project) =>
    workspace && workspaceLatestRun && project.id === workspace.project.id
      ? {
          ...project,
          artifact_count: workspace.project.artifact_count,
          latest_workflow_name: workspaceLatestRun.workflow_name,
          latest_workflow_node: workspaceLatestRun.current_node,
          latest_workflow_run_id: workspaceLatestRun.id,
          latest_workflow_status: workspaceLatestRun.status,
        }
      : project,
  );
  useEffect(() => {
    if (!workspace || !workspaceLatestRun) {
      return;
    }
    queryClient.setQueryData<ProjectList>(projectsQueryKey, (current) =>
      current
        ? {
            ...current,
            projects: current.projects.map((project) =>
              project.id === workspace.project.id
                ? {
                    ...project,
                    artifact_count: workspace.project.artifact_count,
                    latest_workflow_name: workspaceLatestRun.workflow_name,
                    latest_workflow_node: workspaceLatestRun.current_node,
                    latest_workflow_run_id: workspaceLatestRun.id,
                    latest_workflow_status: workspaceLatestRun.status,
                  }
                : project,
            ),
          }
        : current,
    );
  }, [queryClient, workspace, workspaceLatestRun]);
  const activeRun =
    workspace?.workflow_runs.find((run) => run.id === requestedRunId) ??
    workspace?.workflow_runs[0];
  const activeRunId = activeRun?.id ?? null;
  const exportsQuery = useQuery({
    enabled: selectedProjectId !== null && workspace !== undefined,
    queryFn: () => {
      if (!selectedProjectId) {
        throw new Error("Select a project before loading its exports.");
      }
      return fetchProjectExports(selectedProjectId);
    },
    queryKey: ["project-exports", selectedProjectId],
    refetchInterval: (query) => {
      if (
        !query.state.data ||
        query.state.data.available_formats.length > 0 ||
        !activeRun
      ) {
        return false;
      }
      return activeRun.status === "pending" || activeRun.status === "running"
        ? 3_000
        : false;
    },
  });

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
      activeRun?.status === "pending" ||
      activeRun?.status === "running" ||
      activeRun?.status === "paused"
        ? 3_000
        : false,
  });

  const activeArtifactVersionIds =
    activeRun?.workflow_name === "story_blueprint" && eventsQuery.data
      ? artifactVersionIdsFromEvents(eventsQuery.data.events)
      : new Set<string>();
  const artifacts =
    workspace && activeArtifactVersionIds.size > 0
      ? workspace.artifacts.filter((artifact) =>
          artifact.versions.some((version) =>
            activeArtifactVersionIds.has(version.id),
          ),
        )
      : (workspace?.artifacts ?? []);

  const selectedArtifact =
    artifacts.find((artifact) => artifact.id === requestedArtifactId) ??
    artifacts[0] ??
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
    onSuccess: async (_result, action) => {
      if (action === "approve") {
        setRequestedRunId(null);
        setRequestedArtifactId(null);
        setRequestedVersionId(null);
      }
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
      workflowRunId,
    }: {
      action: RunControlAction;
      budget?: RunBudgetPatch;
      projectId: string;
      targetNode?: string;
      workflowRunId: string;
    }) => {
      return controlRun({
        action,
        budget,
        commandId: crypto.randomUUID(),
        targetNode,
        workflowRunId,
      });
    },
    onSuccess: async (result, variables) => {
      if (result.resulting_workflow_run_id) {
        setRequestedRunId(result.resulting_workflow_run_id);
      }
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: projectsQueryKey }),
        queryClient.invalidateQueries({
          queryKey: ["workspace", variables.projectId],
        }),
        queryClient.invalidateQueries({
          queryKey: ["workflow-events", variables.workflowRunId],
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
  const createProjectMutation = useMutation({
    mutationFn: () => {
      intakeRequestId.current ??= crypto.randomUUID();
      return startStoryProject({
        premise: premise.trim(),
        requestId: intakeRequestId.current,
        title: storyTitle.trim() || undefined,
      });
    },
    onSuccess: async (created) => {
      setRequestedProjectId(created.project_id);
      setRequestedRunId(created.workflow_run_id);
      await queryClient.invalidateQueries({ queryKey: projectsQueryKey });
      setPremise("");
      setStoryTitle("");
      intakeRequestId.current = null;
      setCreatingStory(false);
    },
  });
  const deleteProjectMutation = useMutation({
    mutationFn: removeStoryProject,
    onSuccess: async (_result, deletedProjectId) => {
      queryClient.setQueryData<ProjectList>(projectsQueryKey, (current) =>
        current
          ? {
              ...current,
              projects: current.projects.filter(
                (project) => project.id !== deletedProjectId,
              ),
            }
          : current,
      );
      queryClient.removeQueries({
        queryKey: ["workspace", deletedProjectId],
      });
      queryClient.removeQueries({
        queryKey: ["project-exports", deletedProjectId],
      });
      if (selectedProjectId === deletedProjectId) {
        setRequestedProjectId(null);
        setRequestedRunId(null);
        setRequestedArtifactId(null);
        setRequestedVersionId(null);
        setInspectorOpen(false);
      }
      await queryClient.invalidateQueries({ queryKey: projectsQueryKey });
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
              <span>{projects.length}</span>
            </div>
            <button
              className={`new-story-button ${
                selectedProjectId === null ? "new-story-button--active" : ""
              }`}
              type="button"
              onClick={() => {
                intakeRequestId.current = null;
                setCreatingStory(true);
                setRequestedRunId(null);
                setRequestedArtifactId(null);
                setRequestedVersionId(null);
                setNavigationOpen(false);
              }}
            >
              <span aria-hidden="true">+</span>
              New story
            </button>
            <div className="project-list">
              {projects.map((project) => {
                const mustStopBeforeDelete = ["pending", "running"].includes(
                  project.latest_workflow_status ?? "",
                );
                return (
                  <div
                    className={`project-row ${
                      project.id === selectedProjectId
                        ? "project-row--active"
                        : ""
                    }`}
                    key={project.id}
                  >
                    <button
                      className="project-button"
                      type="button"
                      onClick={() => {
                        setCreatingStory(false);
                        setRequestedProjectId(project.id);
                        setRequestedRunId(null);
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
                          {projectWorkflowLabel(project)}
                        </small>
                      </span>
                    </button>
                    <button
                      aria-label={`Delete story ${project.name}`}
                      className="project-delete"
                      disabled={
                        mustStopBeforeDelete || deleteProjectMutation.isPending
                      }
                      title={
                        mustStopBeforeDelete
                          ? "Stop this story's workflow before deleting it"
                          : `Delete ${project.name}`
                      }
                      type="button"
                      onClick={() => {
                        const confirmed = window.confirm(
                          `Delete “${project.name}”? This permanently removes its messages, workflow history, and artifacts from this device.`,
                        );
                        if (confirmed) {
                          deleteProjectMutation.mutate(project.id);
                        }
                      }}
                    >
                      <span aria-hidden="true">×</span>
                    </button>
                  </div>
                );
              })}
              {projects.length === 0 && (
                <p className="nav-empty">
                  Your local story library is ready for its first premise.
                </p>
              )}
            </div>
            {deleteProjectMutation.error instanceof Error && (
              <p className="nav-error">{deleteProjectMutation.error.message}</p>
            )}
          </section>

          <section className="nav-section nav-section--artifacts">
            <div className="nav-heading">
              <span>
                {activeArtifactVersionIds.size > 0
                  ? "Artifacts in attempt"
                  : "Artifacts across attempts"}
              </span>
              <span>{artifacts.length}</span>
            </div>
            <div className="artifact-list">
              {artifacts.map((artifact) => (
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
              {!workspace && (
                <p className="nav-empty">
                  Blueprint artifacts will appear here as specialists complete
                  their work.
                </p>
              )}
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
          {selectedProjectId === null && (
            <StoryIntake
              error={
                createProjectMutation.error instanceof Error
                  ? createProjectMutation.error.message
                  : null
              }
              isPending={createProjectMutation.isPending}
              onPremiseChange={(value) => {
                intakeRequestId.current = null;
                setPremise(value);
              }}
              onSubmit={() => {
                createProjectMutation.mutate();
              }}
              onTitleChange={(value) => {
                intakeRequestId.current = null;
                setStoryTitle(value);
              }}
              premise={premise}
              title={storyTitle}
            />
          )}
          {selectedProjectId !== null && workspaceQuery.isPending && (
            <StoryLoading />
          )}
          {selectedProjectId !== null && workspaceQuery.isError && (
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
                <div className="story-actions">
                  <ExportControls
                    availableFormats={
                      exportsQuery.data?.available_formats ?? []
                    }
                    isLoading={exportsQuery.isPending}
                    projectId={workspace.project.id}
                    unavailableReason={
                      exportsQuery.data?.unavailable_reason ?? null
                    }
                  />
                  <div className="run-summary">
                    {workspace.workflow_runs.length > 1 && activeRun && (
                      <RunAttemptSelector
                        activeRunId={activeRun.id}
                        onChange={setRequestedRunId}
                        runs={workspace.workflow_runs}
                      />
                    )}
                    <span
                      className={`run-status run-status--${activeRun?.status ?? "idle"}`}
                    >
                      {humanize(activeRun?.status ?? "idle")}
                    </span>
                    <small>
                      {activeRun
                        ? activeRun.current_node
                          ? `${workflowPhase(activeRun)} at ${humanize(activeRun.current_node)}`
                          : workflowPhase(activeRun)
                        : "Workspace ready"}
                    </small>
                  </div>
                </div>
              </header>

              {activeRun && (
                <RunControls
                  error={
                    runControlMutation.variables?.workflowRunId ===
                      activeRun.id && runControlMutation.error instanceof Error
                      ? runControlMutation.error.message
                      : activeRun.status === "failed"
                        ? (activeRun.failure_detail ?? activeRun.error_message)
                        : null
                  }
                  isPending={
                    runControlMutation.isPending &&
                    runControlMutation.variables.workflowRunId === activeRun.id
                  }
                  onCommand={(action, targetNode, budget) => {
                    if (!selectedProjectId) {
                      return;
                    }
                    runControlMutation.mutate({
                      action,
                      budget,
                      projectId: selectedProjectId,
                      targetNode,
                      workflowRunId: activeRun.id,
                    });
                  }}
                  onRetryNodeChange={setRetryNode}
                  retryNode={
                    activeRun.retryable_nodes.includes(retryNode)
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

function ExportControls({
  availableFormats,
  isLoading,
  projectId,
  unavailableReason,
}: {
  availableFormats: ProjectExportFormat[];
  isLoading: boolean;
  projectId: string;
  unavailableReason: string | null;
}) {
  const labels: Record<ProjectExportFormat, string> = {
    markdown: "Markdown",
    pdf: "PDF",
    docx: "DOCX",
  };
  return (
    <section className="export-controls" aria-label="Story exports">
      <span className="export-label">Export</span>
      <div>
        {(["markdown", "pdf", "docx"] as const).map((format) =>
          availableFormats.includes(format) ? (
            <a
              className="export-link"
              download
              href={projectExportUrl(projectId, format)}
              key={format}
            >
              {labels[format]}
            </a>
          ) : (
            <span
              aria-disabled="true"
              className="export-link export-link--disabled"
              key={format}
              title={
                isLoading
                  ? "Checking export readiness"
                  : (unavailableReason ?? "This format is unavailable")
              }
            >
              {labels[format]}
            </span>
          ),
        )}
      </div>
    </section>
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

function RunAttemptSelector({
  activeRunId,
  onChange,
  runs,
}: {
  activeRunId: string;
  onChange: (runId: string) => void;
  runs: WorkspaceRun[];
}) {
  return (
    <label className="run-attempt-selector">
      <span>Attempt</span>
      <select
        aria-label="Workflow attempt"
        value={activeRunId}
        onChange={(event) => {
          onChange(event.target.value);
        }}
      >
        {runs.map((run, index) => (
          <option key={run.id} value={run.id}>
            {runs.length - index} · {workflowPhase(run)} ·{" "}
            {humanize(run.status)}
            {run.current_node ? ` at ${humanize(run.current_node)}` : ""}
          </option>
        ))}
      </select>
    </label>
  );
}

function artifactVersionIdsFromEvents(
  events: WorkflowEventEnvelope[],
): Set<string> {
  const versionIds = new Set<string>();
  for (const event of events) {
    for (const key of ["output_artifacts", "seed_artifacts"]) {
      const references = event.payload[key];
      if (!Array.isArray(references)) {
        continue;
      }
      for (const reference of references) {
        if (!reference || typeof reference !== "object") {
          continue;
        }
        const record = reference as Record<string, unknown>;
        const versionId = record.artifact_version_id ?? record.version_id;
        if (typeof versionId === "string") {
          versionIds.add(versionId);
        }
      }
    }
  }
  return versionIds;
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
  const canStop = ["pending", "running", "paused"].includes(run.status);
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

function workflowPhase(run: WorkspaceRun): string {
  return run.workflow_name === "scene_production"
    ? "Production"
    : run.workflow_name === "story_blueprint"
      ? "Story Blueprint"
      : humanize(run.workflow_name);
}

function projectWorkflowLabel(project: ProjectSummary): string {
  if (!project.latest_workflow_status) {
    return "Not Started";
  }
  const status = humanize(project.latest_workflow_status);
  const phase =
    project.latest_workflow_name === "scene_production"
      ? "Production"
      : project.latest_workflow_name === "story_blueprint"
        ? "Story Blueprint"
        : project.latest_workflow_name
          ? humanize(project.latest_workflow_name)
          : null;
  const node = project.latest_workflow_node
    ? ` at ${humanize(project.latest_workflow_node)}`
    : "";
  return phase ? `${phase} · ${status}${node}` : `${status}${node}`;
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

function StoryIntake({
  error,
  isPending,
  onPremiseChange,
  onSubmit,
  onTitleChange,
  premise,
  title,
}: {
  error: string | null;
  isPending: boolean;
  onPremiseChange: (value: string) => void;
  onSubmit: () => void;
  onTitleChange: (value: string) => void;
  premise: string;
  title: string;
}) {
  const canSubmit = premise.trim().length > 0 && !isPending;
  const premiseInput = useRef<HTMLTextAreaElement>(null);

  useLayoutEffect(() => {
    const textarea = premiseInput.current;
    if (!textarea) {
      return;
    }
    textarea.style.height = "auto";
    textarea.style.height = `${String(textarea.scrollHeight)}px`;
    const maxHeight = Number.parseFloat(getComputedStyle(textarea).maxHeight);
    textarea.style.overflowY =
      textarea.scrollHeight > maxHeight ? "auto" : "hidden";
  }, [premise]);

  return (
    <section className="story-intake" aria-labelledby="story-intake-heading">
      <div className="story-intake-copy">
        <p className="eyebrow">New short story</p>
        <h1 id="story-intake-heading">What should the studio create?</h1>
        <p>
          Give the specialists a premise, image, character, question, or rough
          idea. They will develop the Story Blueprint and return here for your
          approval before drafting.
        </p>
        <div className="workflow-preview" aria-label="Open Hollywood workflow">
          <span>Premise</span>
          <span aria-hidden="true">→</span>
          <span>Blueprint approval</span>
          <span aria-hidden="true">→</span>
          <span>Autonomous draft</span>
        </div>
      </div>
      <form
        className="premise-composer"
        onSubmit={(event) => {
          event.preventDefault();
          if (canSubmit) {
            onSubmit();
          }
        }}
      >
        <label className="story-title-field">
          <span>Working title</span>
          <input
            maxLength={200}
            onChange={(event) => {
              onTitleChange(event.target.value);
            }}
            placeholder="Optional — we can derive one from your premise"
            type="text"
            value={title}
          />
        </label>
        <label className="premise-field">
          <span>Story premise</span>
          <textarea
            autoFocus
            maxLength={10_000}
            onChange={(event) => {
              onPremiseChange(event.target.value);
            }}
            placeholder="A brand-new stroller waits outside an abandoned, windowless building..."
            ref={premiseInput}
            rows={1}
            value={premise}
          />
        </label>
        <div className="premise-composer-footer">
          <span>{premise.length.toLocaleString()} / 10,000</span>
          <button
            className="primary-action"
            disabled={!canSubmit}
            type="submit"
          >
            {isPending ? "Creating story…" : "Create Story Blueprint"}
          </button>
        </div>
        {error && <p className="decision-error">{error}</p>}
      </form>
    </section>
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
