import type {
  ArtifactProvenance as ProvenanceView,
  ArtifactSelection,
} from "@open-hollywood/contracts";
import { useQuery } from "@tanstack/react-query";

import { fetchArtifactProvenance } from "../api";
import {
  sameSelection,
  selectionForReview,
  type ReviewPanelProps,
} from "./artifactSelection";

const unavailableMessages: Partial<Record<string, string>> = {
  exact_registered_identity: "The relationship could not be verified.",
  unregistered_workspace: "This workspace has no registered provenance source.",
  source_unavailable:
    "The registered source is unavailable. Provenance could not be checked.",
  source_changed: "The registered source could not be revalidated.",
  no_registered_association:
    "No registered review relationship was found for this version.",
  selection_mismatch:
    "This selection does not match the registered relationship.",
  ambiguous_association:
    "More than one review relationship matches. No relationship is shown.",
  current_source_missing:
    "A source record needed to verify this relationship is missing.",
  current_source_mismatch:
    "Current source records do not match the registered relationship.",
} satisfies Record<ProvenanceView["reason"], string>;

function boundRelationship(
  view: ProvenanceView,
  selection: ArtifactSelection,
): boolean {
  const relationship = view.relationship;
  if (
    !relationship ||
    view.contract !== "artifact-provenance-view-1" ||
    view.assessment_attachment_eligible !== false ||
    view.writer_dispatch_authorized !== false ||
    view.live_calls !== 0 ||
    relationship.assessment_source !== "unsupported_contract" ||
    relationship.captured_assessment_delivery !== "missing" ||
    [
      relationship.semantic_support,
      relationship.evidence_adequacy,
      relationship.editorial_effect,
      relationship.edit_necessity,
      relationship.craft,
    ].some((state) => state !== "unassessed")
  )
    return false;
  return selection.role === "original_review"
    ? relationship.review_version_id === selection.version_id &&
        relationship.review_artifact_id === selection.artifact_id &&
        relationship.review_content_sha256 === selection.content_sha256
    : relationship.draft_version_id === selection.version_id &&
        relationship.draft_artifact_id === selection.artifact_id &&
        relationship.draft_content_sha256 === selection.content_sha256;
}

export function ArtifactProvenance({ projectId, detail }: ReviewPanelProps) {
  const selection = selectionForReview({ projectId, detail });
  const query = useQuery({
    queryKey: [
      "artifact-provenance",
      selection.project_id,
      selection.artifact_id,
      selection.version_id,
      selection.content_sha256,
      selection.role,
    ],
    queryFn: ({ signal }) => fetchArtifactProvenance(selection, signal),
    retry: false,
    gcTime: 0,
    staleTime: 0,
    refetchOnMount: "always",
    refetchOnWindowFocus: false,
  });
  const view = query.data;
  const matching = view?.selection && sameSelection(view.selection, selection);
  const verified =
    !query.isError &&
    matching &&
    view.status === "identity_verified" &&
    view.reason === "exact_registered_identity" &&
    boundRelationship(view, selection);
  const relationship = verified ? view.relationship : null;
  const checking = query.isPending || query.isFetching;
  const message = query.isError
    ? "Review provenance could not be checked."
    : !matching
      ? "The provenance response does not match this selection."
      : (unavailableMessages[view.reason] ??
        "Review provenance could not be checked.");

  return (
    <section className="review-provenance" aria-label="Review provenance">
      <div className="section-heading">
        <h3>Review provenance</h3>
        <span>v{detail.selected_version.version_number}</span>
      </div>
      {checking ? (
        <p role="status">Checking this exact version…</p>
      ) : relationship ? (
        <>
          <p className="provenance-status">Version relationship verified</p>
          <p>
            The saved review and reviewed draft match their registered source
            records.
          </p>
          {!relationship.selected_is_latest_at_lookup && (
            <p className="provenance-history">
              You are viewing an older version. Its original review relationship
              is retained.
            </p>
          )}
          <dl className="review-relationship">
            <div>
              <dt>Review version</dt>
              <dd>
                <code>{relationship.review_version_id}</code>
              </dd>
            </div>
            <div>
              <dt>Reviewed draft version</dt>
              <dd>
                <code>{relationship.draft_version_id}</code>
              </dd>
            </div>
          </dl>
          <div className="provenance-assessment">
            <h4>Assessment unavailable</h4>
            <p>
              This historical review uses an unsupported assessment contract. No
              assessment delivery is recorded in its capture.
            </p>
            <p>
              Identity verification does not establish accuracy, edit necessity
              or story quality. No assessment is attached.
            </p>
          </div>
          <details>
            <summary>Source details</summary>
            <dl className="review-relationship">
              <div>
                <dt>Registered source</dt>
                <dd>{relationship.source_registration}</dd>
              </div>
              <div>
                <dt>Review invocation</dt>
                <dd>
                  <code>{relationship.review_invocation_id}</code>
                </dd>
              </div>
              <div>
                <dt>Workflow run</dt>
                <dd>
                  <code>{relationship.workflow_run_id}</code>
                </dd>
              </div>
              <div>
                <dt>Selected content hash</dt>
                <dd>
                  <code>{selection.content_sha256}</code>
                </dd>
              </div>
              <div>
                <dt>Review / draft heads at lookup</dt>
                <dd>
                  {relationship.review_is_latest_at_lookup
                    ? "Latest review"
                    : "Older review"}{" "}
                  ·{" "}
                  {relationship.draft_is_latest_at_lookup
                    ? "Latest draft"
                    : "Older draft"}
                </dd>
              </div>
            </dl>
          </details>
        </>
      ) : (
        <>
          <p className="provenance-status">Provenance unavailable</p>
          <p role="status">{message}</p>
          <p>No assessment is attached. Story quality is unassessed.</p>
          <button
            type="button"
            className="provenance-recheck"
            onClick={() => {
              void query.refetch();
            }}
          >
            Check again
          </button>
        </>
      )}
    </section>
  );
}
