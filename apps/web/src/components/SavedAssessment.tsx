import type {
  ArtifactSelection,
  Q008InspectorView,
  Q013InspectorView,
} from "@open-hollywood/contracts";
import { useQuery } from "@tanstack/react-query";
import { fetchQ013Assessment } from "../api";

import {
  sameSelection,
  selectionForReview,
  type ReviewPanelProps,
} from "./artifactSelection";

type Inventory = Q008InspectorView | Q013InspectorView;
type Lookup<T extends Inventory> = (
  selection: ArtifactSelection,
  signal: AbortSignal,
) => Promise<T>;
export type Q013Lookup = Lookup<Q013InspectorView>;
type PanelProps = ReviewPanelProps &
  (
    | { claimId: "Q008"; lookup: Lookup<Q008InspectorView> }
    | { claimId: "Q013"; lookup: Q013Lookup }
  );

function hasDisplayOnlyStatus(status: Record<string, unknown>) {
  return (
    status.production_attachment_eligible === false &&
    status.writer_dispatch_authorized === false &&
    [
      status.semantic_support,
      status.evidence_adequacy,
      status.edit_necessity,
      status.craft,
    ].every((value) => value === "unassessed")
  );
}

function assessmentFor(
  view: Inventory | undefined,
  claimId: "Q008" | "Q013",
  selection: ArtifactSelection,
) {
  const row = view?.lookups[0];
  const assessment = view?.assessments[0];
  const record = view?.accounting_records[0];
  const totals = view?.generation_totals;
  if (
    view?.contract !==
      (claimId === "Q008"
        ? "q008-inspector-view-1"
        : "q013-inspector-view-1") ||
    view.lookups.length !== 1 ||
    !row ||
    !sameSelection(row.selection, selection) ||
    row.status !== "available" ||
    row.reason !== null ||
    !row.delivery_id ||
    !assessment ||
    !record ||
    view.assessments.length !== 1 ||
    view.accounting_records.length !== 1 ||
    row.claim_id !== claimId ||
    assessment.claim_id !== claimId ||
    !hasDisplayOnlyStatus(assessment.application_status) ||
    assessment.delivery_id !== row.delivery_id ||
    record.delivery_id !== row.delivery_id ||
    record.request_selection.role !== "original_review" ||
    record.request_selection.project_id !== selection.project_id ||
    (selection.role === "original_review" &&
      !sameSelection(record.request_selection, selection)) ||
    totals?.input_tokens !== record.generation_usage.input_tokens ||
    record.generation_usage.output_tokens !== totals.output_tokens ||
    record.generation_usage.reasoning_tokens !== totals.reasoning_tokens ||
    record.generation_usage.cached_input_tokens !== totals.cached_input_tokens
  )
    return null;
  return { assessment, record };
}

const number = new Intl.NumberFormat("en-US");

export function SavedAssessment({
  projectId,
  detail,
  lookup,
  claimId,
}: PanelProps) {
  const selection = selectionForReview({ projectId, detail });
  const query = useQuery<Inventory>({
    queryKey: ["saved-assessment", claimId, selection],
    queryFn: ({ signal }) => lookup(selection, signal),
    retry: false,
    staleTime: 0,
    gcTime: 0,
    refetchOnMount: "always",
    refetchOnWindowFocus: false,
  });
  const checking = query.isPending || query.fetchStatus !== "idle";
  const result =
    query.isSuccess && !checking && !query.isPlaceholderData
      ? assessmentFor(query.data, claimId, selection)
      : null;
  const usage = result?.record.generation_usage;
  const row = query.data?.lookups[0];
  const reason =
    !query.isError &&
    row?.status === "unavailable" &&
    sameSelection(row.selection, selection)
      ? row.reason
      : null;
  return (
    <section className="review-provenance" aria-label={`${claimId} assessment`}>
      <div className="section-heading">
        <h3>{claimId} assessment</h3>
        <span>v{detail.selected_version.version_number}</span>
      </div>
      {checking ? (
        <p role="status">Checking this version’s assessment…</p>
      ) : result && usage ? (
        <>
          <h4>Review claim</h4>
          <p>{result.assessment.claim}</p>
          <h4>Model judgment</h4>
          <p>
            {result.assessment.model} ·{" "}
            {result.assessment.model_assessment.support}
          </p>
          <p>{result.assessment.model_assessment.reason}</p>
          <p>
            Citations · {result.assessment.model_assessment.evidence.join(", ")}
          </p>
          {result.assessment.claim_id === "Q013" ? (
            <>
              <h4>Operator scores</h4>
              <p>
                Claim correctness ·{" "}
                {result.assessment.operator_score.claim_correctness}
              </p>
              <p>
                Evidence coverage ·{" "}
                {result.assessment.operator_score.evidence_coverage}
              </p>
            </>
          ) : (
            <p>
              Operator score ·{" "}
              {result.assessment.operator_score.passed_judgments}/
              {result.assessment.operator_score.possible_judgments} against
              frozen gold
            </p>
          )}
          <p>
            Application status · Semantic support, evidence adequacy, edit
            necessity and craft are unassessed.
          </p>
          <h4>Shared generation usage</h4>
          <p>
            {number.format(usage.input_tokens)} input ·{" "}
            {number.format(usage.output_tokens)} output
          </p>
          <p>
            Reasoning tokens included in output ·{" "}
            {number.format(usage.reasoning_tokens)}. Cached input ·{" "}
            {number.format(usage.cached_input_tokens)}.
          </p>
          <p>
            Preflight input count ·{" "}
            {number.format(result.record.preflight_input_count)}. Billed cost
            unknown.
          </p>
          <details>
            <summary>Delivery and request</summary>
            <dl className="review-relationship">
              <div>
                <dt>Delivery</dt>
                <dd>
                  <code>{result.record.delivery_id}</code>
                </dd>
              </div>
              <div>
                <dt>Original critique version</dt>
                <dd>
                  <code>{result.record.request_selection.version_id}</code>
                </dd>
              </div>
            </dl>
          </details>
        </>
      ) : (
        <p role="status">
          {reason === "unregistered_workspace"
            ? "Assessment unavailable in this workspace."
            : reason === "workspace_unavailable"
              ? "The registered workspace could not be verified."
              : reason === "exact_selection_unavailable"
                ? "Assessment unavailable for this version."
                : "Assessment unavailable. The publication could not be verified."}
        </p>
      )}
      {!checking && (
        <button
          type="button"
          className="provenance-recheck"
          onClick={() => {
            void query.refetch();
          }}
        >
          Refresh assessment
        </button>
      )}
    </section>
  );
}

export function Q013Assessment({
  lookup = fetchQ013Assessment,
  ...props
}: ReviewPanelProps & { lookup?: Q013Lookup }) {
  return <SavedAssessment {...props} claimId="Q013" lookup={lookup} />;
}
