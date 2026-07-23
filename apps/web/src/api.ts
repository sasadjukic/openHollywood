import {
  activateModelProfile,
  configureModelProfile,
  getArtifactVersion,
  getHealth,
  getProjectWorkspace,
  listModelCatalog,
  listModelProfiles,
  listProjects,
  listWorkflowRunEvents,
  submitBlueprintDecision,
  type ArtifactVersionDetail,
  type BlueprintDecisionAction,
  type BlueprintDecisionResponse,
  type ConfigureModelProfileRequest,
  type ModelCatalog,
  type ModelProfileList,
  type ModelProfileSummary,
  type ProjectList,
  type ProjectWorkspace,
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

export async function fetchProjectWorkspace(
  projectId: string,
): Promise<ProjectWorkspace> {
  const result = await getProjectWorkspace({
    path: { project_id: projectId },
  });
  return requireData(result, "This story workspace could not be loaded.");
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

function requireData<T>(
  result: { data?: T; error?: unknown },
  fallbackMessage: string,
): T {
  if (result.error || !result.data) {
    throw new Error(fallbackMessage);
  }
  return result.data;
}
