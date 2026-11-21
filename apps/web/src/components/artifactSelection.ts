import type {
  ArtifactSelection,
  ArtifactVersionDetail,
} from "@open-hollywood/contracts";

export interface ReviewPanelProps {
  projectId: string;
  detail: ArtifactVersionDetail;
}

export function selectionForReview({
  projectId,
  detail,
}: ReviewPanelProps): ArtifactSelection {
  return {
    project_id: projectId,
    artifact_id: detail.artifact.id,
    version_id: detail.selected_version.id,
    content_sha256: detail.content_sha256,
    role:
      detail.artifact.artifact_type === "critique"
        ? "original_review"
        : "reviewed_draft",
  };
}

export function sameSelection(
  left: ArtifactSelection,
  right: ArtifactSelection,
): boolean {
  return (
    left.project_id === right.project_id &&
    left.artifact_id === right.artifact_id &&
    left.version_id === right.version_id &&
    left.content_sha256 === right.content_sha256 &&
    left.role === right.role
  );
}
