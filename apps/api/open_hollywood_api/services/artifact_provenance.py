"""Compact read-only inspector projection over the qualified local association lookup."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Literal

from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import Digest, Identifier, Record, require
from open_hollywood_engine.secrets import SecretLeakError

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import production_association_lookup as lookup
from open_hollywood_api.services.production_association_records import ArtifactSelection

UnavailableReason = Literal[
    "unregistered_workspace",
    "source_unavailable",
    "source_changed",
    "no_registered_association",
    "selection_mismatch",
    "ambiguous_association",
    "current_source_missing",
    "current_source_mismatch",
]


class ProvenanceRelationship(Record):
    review_artifact_id: Identifier
    review_version_id: Identifier
    review_content_sha256: Digest
    draft_artifact_id: Identifier
    draft_version_id: Identifier
    draft_content_sha256: Digest
    review_invocation_id: Identifier
    workflow_run_id: Identifier
    source_registration: str
    selected_is_latest_at_lookup: bool
    review_is_latest_at_lookup: bool
    draft_is_latest_at_lookup: bool
    assessment_source: Literal["unsupported_contract"] = "unsupported_contract"
    captured_assessment_delivery: Literal["missing"] = "missing"
    semantic_support: Literal["unassessed"] = "unassessed"
    evidence_adequacy: Literal["unassessed"] = "unassessed"
    editorial_effect: Literal["unassessed"] = "unassessed"
    edit_necessity: Literal["unassessed"] = "unassessed"
    craft: Literal["unassessed"] = "unassessed"


class ArtifactProvenance(Record):
    contract: Literal["artifact-provenance-view-1"] = "artifact-provenance-view-1"
    selection: ArtifactSelection
    status: Literal["identity_verified", "unavailable"]
    reason: Literal["exact_registered_identity"] | UnavailableReason
    relationship: ProvenanceRelationship | None = None
    assessment_attachment_eligible: Literal[False] = False
    writer_dispatch_authorized: Literal[False] = False
    live_calls: Literal[0] = 0


def unavailable(selection: ArtifactSelection, reason: UnavailableReason) -> ArtifactProvenance:
    return ArtifactProvenance(selection=selection, status="unavailable", reason=reason)


def _project(result: lookup.LookupResult, selection: ArtifactSelection) -> ArtifactProvenance:
    # Revalidate a typed value too: unchecked model_copy is not a trusted response.
    result = lookup.LookupResult.model_validate_json(result.model_dump_json())
    request = lookup.LookupRequest(workspace=result.workspace, selections=(selection,))
    require(
        result.request_sha256 == canonical_sha256(request.model_dump(mode="json")), "view_request"
    )
    require(len(result.entries) == 1 and result.entries[0].selection == selection, "view_binding")
    entry = result.entries[0]
    if entry.status == "unavailable":
        require(
            entry.identity is None and entry.reason != "exact_registered_identity", "view_state"
        )
        return ArtifactProvenance.model_validate(
            {
                "selection": selection,
                "status": "unavailable",
                "reason": entry.reason,
            }
        )
    identity = entry.identity
    require(identity is not None and entry.reason == "exact_registered_identity", "view_state")
    assert identity is not None
    from open_hollywood_api.services.production_association_records import selection_matches

    require(selection_matches(identity.historical, selection), "view_historical_binding")
    binding = identity.historical.evidence.binding
    return ArtifactProvenance(
        selection=selection,
        status="identity_verified",
        reason="exact_registered_identity",
        relationship=ProvenanceRelationship(
            review_artifact_id=binding.critique_artifact_id,
            review_version_id=binding.critique_version_id,
            review_content_sha256=binding.critique_content_sha256,
            draft_artifact_id=binding.target_artifact_id,
            draft_version_id=binding.target_version_id,
            draft_content_sha256=binding.target_content_sha256,
            review_invocation_id=binding.review_invocation_id,
            workflow_run_id=binding.workflow_run_id,
            source_registration=identity.historical.source.registration,
            selected_is_latest_at_lookup=(
                identity.review_lineage_at_lookup.selected_is_latest
                if selection.role == "original_review"
                else identity.draft_lineage_at_lookup.selected_is_latest
            ),
            review_is_latest_at_lookup=identity.review_lineage_at_lookup.selected_is_latest,
            draft_is_latest_at_lookup=identity.draft_lineage_at_lookup.selected_is_latest,
        ),
    )


class ArtifactProvenanceService:
    """App-owned source path, never a request-controlled database or workspace registry."""

    def __init__(self, database: Path) -> None:
        self._database = database.absolute()

    def view(self, selection: ArtifactSelection) -> ArtifactProvenance:
        selection = ArtifactSelection.model_validate_json(selection.model_dump_json())
        try:
            path = storage._unlinked(self._database)
            candidates = [w for w in lookup.REGISTERED if storage._unlinked(w.path) == path]
            if len(candidates) != 1:
                return unavailable(selection, "unregistered_workspace")
            result = lookup.lookup(
                lookup.LookupRequest(
                    workspace=candidates[0].name,
                    selections=(selection,),
                )
            )
            require(result.workspace == candidates[0].name, "view_workspace")
            return _project(result, selection)
        except SecretLeakError:
            # No raw exception or source body reaches the view or logs.
            return unavailable(selection, "source_unavailable")
        except (OSError, sqlite3.Error):
            return unavailable(selection, "source_unavailable")
        except (ValueError, LookupError, TypeError):
            return unavailable(selection, "source_changed")
