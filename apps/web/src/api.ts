import {
  activateModelProfile,
  configureModelProfile,
  controlWorkflowRun,
  createStoryProject,
  deleteStoryProject,
  getArtifactVersion,
  getHealth,
  getProjectWorkspace,
  listModelCatalog,
  listModelProfiles,
  listProjectExports,
  listProjects,
  listWorkflowRunEvents,
  submitBlueprintDecision,
  type ArtifactVersionDetail,
  type BlueprintDecisionAction,
  type BlueprintDecisionResponse,
  type ConfigureModelProfileRequest,
  type CreateStoryProjectResponse,
  type ModelCatalog,
  type ModelProfileList,
  type ModelProfileSummary,
  type ProjectList,
  type ProjectExportFormat,
  type ProjectExportManifest,
  type ProjectWorkspace,
  type RunBudgetPatch,
  type RunControlAction,
  type RunControlResponse,
  type ServiceStatus,
  type WorkflowEventPage,
} from "@open-hollywood/contracts";
import { client } from "@open-hollywood/contracts/client";

const apiBaseUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

client.setConfig({ baseUrl: apiBaseUrl });

export async function fetchServiceStatus(): Promise<ServiceStatus> {
  const result = await getHealth();
  return requireData(
    result,
    "The local Open Hollywood API returned no service status.",
  );
}

export async function fetchProjects(): Promise<ProjectList> {
  const result = await listProjects();
  return requireData(result, "The project library could not be loaded.");
}

export async function startStoryProject(input: {
  premise: string;
  requestId: string;
  title?: string;
}): Promise<CreateStoryProjectResponse> {
  const result = await createStoryProject({
    body: {
      premise: input.premise,
      request_id: input.requestId,
      title: input.title,
    },
  });
  return requireData(result, "The new story could not be created.");
}

export async function removeStoryProject(projectId: string): Promise<void> {
  const result = await deleteStoryProject({
    path: { project_id: projectId },
  });
  if (result.error) {
    throw new Error(
      "This story could not be deleted. Stop its workflow first, then try again.",
    );
  }
}

export async function fetchProjectWorkspace(
  projectId: string,
): Promise<ProjectWorkspace> {
  const result = await getProjectWorkspace({
    path: { project_id: projectId },
  });
  return requireData(result, "This story workspace could not be loaded.");
}

export async function fetchProjectExports(
  projectId: string,
): Promise<ProjectExportManifest> {
  const result = await listProjectExports({
    path: { project_id: projectId },
  });
  return requireData(result, "Export availability could not be loaded.");
}

export function projectExportUrl(
  projectId: string,
  format: ProjectExportFormat,
): string {
  const base = client.getConfig().baseUrl?.replace(/\/$/, "") ?? apiBaseUrl;
  return `${base}/api/v1/projects/${encodeURIComponent(projectId)}/exports/${format}`;
}

export async function fetchArtifactVersion(
  versionId: string,
): Promise<ArtifactVersionDetail> {
  const result = await getArtifactVersion({
    path: { artifact_version_id: versionId },
  });
  return requireData(result, "This artifact version could not be loaded.");
}

export async function fetchWorkflowEvents(
  workflowRunId: string,
): Promise<WorkflowEventPage> {
  const result = await listWorkflowRunEvents({
    path: { workflow_run_id: workflowRunId },
    query: { after: 0, limit: 500 },
  });
  return requireData(result, "The workflow timeline could not be loaded.");
}

export async function fetchModelProfiles(): Promise<ModelProfileList> {
  const result = await listModelProfiles();
  return requireData(result, "The model presets could not be loaded.");
}

export async function fetchModelCatalog(): Promise<ModelCatalog> {
  const result = await listModelCatalog();
  return requireData(result, "The Ollama model catalog could not be loaded.");
}

export async function saveModelProfile(
  profileId: string,
  configuration: ConfigureModelProfileRequest,
): Promise<ModelProfileSummary> {
  const result = await configureModelProfile({
    body: configuration,
    path: { profile_id: profileId },
  });
  return requireData(result, "The model preset could not be saved.");
}

export async function selectModelProfile(
  profileId: string,
): Promise<ModelProfileSummary> {
  const result = await activateModelProfile({
    path: { profile_id: profileId },
  });
  return requireData(result, "The model preset could not be activated.");
}

export interface SubmitDecisionInput {
  action: BlueprintDecisionAction;
  decisionId: string;
  instruction?: string;
  interruptId: string;
  workflowRunId: string;
}

export async function submitDecision(
  input: SubmitDecisionInput,
): Promise<BlueprintDecisionResponse> {
  const result = await submitBlueprintDecision({
    body: {
      action: input.action,
      decision_id: input.decisionId,
      instruction: input.instruction,
      interrupt_id: input.interruptId,
    },
    path: { workflow_run_id: input.workflowRunId },
  });
  return requireData(result, "The workflow did not accept this decision.");
}

export interface ControlRunInput {
  action: RunControlAction;
  budget?: RunBudgetPatch;
  commandId: string;
  targetNode?: string;
  workflowRunId: string;
}

export async function controlRun(
  input: ControlRunInput,
): Promise<RunControlResponse> {
  const result = await controlWorkflowRun({
    body: {
      action: input.action,
      budget: input.budget,
      command_id: input.commandId,
      target_node: input.targetNode,
    },
    path: { workflow_run_id: input.workflowRunId },
  });
  return requireData(result, "The workflow did not accept this run command.");
}

function requireData<T>(
  result: { data?: T; error?: unknown },
  fallbackMessage: string,
): T {
  if (result.error || !result.data) {
    throw new Error(apiErrorMessage(result.error, fallbackMessage));
  }
  return result.data;
}

function apiErrorMessage(error: unknown, fallbackMessage: string): string {
  if (typeof error === "string" && error.trim()) {
    return error;
  }
  if (error && typeof error === "object" && "detail" in error) {
    const detail = error.detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
  }
  return fallbackMessage;
}
