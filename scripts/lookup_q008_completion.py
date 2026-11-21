"""Look up Q008 by exact artifact selection in the registered read-only publication."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services.assessment_consumer_projection import Usage
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    ModelAssessment,
)
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    EvidenceError,
    JsonObject,
    Record,
    require,
    strict_object,
    string_value,
)
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import NonNegativeInt

from scripts import publish_q008_completion as publisher

PUBLICATION = (
    Path(__file__).resolve().parents[1]
    / "data/diagnostics/q008-publication-2026-11-21/critique-first"
)
MANIFEST_SHA = "efef8fc3348b3a5cfc3c9529e6e645d390685e5030c01d56b257eaa27631619d"


class Available(Record):
    selection: ArtifactSelection
    status: Literal["available"] = "available"
    reason: None = None
    delivery_id: str
    claim_id: str


class Unavailable(Record):
    selection: ArtifactSelection
    status: Literal["unavailable"] = "unavailable"
    reason: str
    delivery_id: None = None
    claim_id: None = None


class Assessment(Record):
    delivery_id: str
    claim_id: str
    claim: str
    model: str
    model_assessment: ModelAssessment
    operator_score: JsonObject
    application_status: JsonObject


class Accounting(Record):
    delivery_id: str
    request_selection: ArtifactSelection
    request_manifest_sha256: Digest
    preflight_input_count: NonNegativeInt
    generation_usage: Usage
    actual_billed_cost: None


class Inventory(Record):
    contract: Literal["q008-consumer-lookup-1"] = "q008-consumer-lookup-1"
    lookups: tuple[Available | Unavailable, ...]
    assessments: tuple[Assessment, ...] = ()
    accounting_records: tuple[Accounting, ...] = ()
    generation_totals: Usage | None = None


def _read_publication() -> tuple[
    tuple[ArtifactSelection, ...], dict[str, bytes], BoundAssessmentResult
]:
    directory = storage._unlinked(PUBLICATION)
    require(directory.is_dir(), "publication_missing")
    require((directory / "manifest.json").is_file(), "publication_incomplete")
    raw = storage._read(directory / "manifest.json")
    require(storage._sha(raw) == MANIFEST_SHA, "publication_manifest_changed")
    manifest = strict_object(raw.decode())
    selectors = manifest["lookup_selections"]
    assert isinstance(selectors, list)
    allowed = tuple(ArtifactSelection.model_validate_json(encoded(s)) for s in selectors)

    # The registered manifest puts the observed critique first, even for draft-only lookups.
    files, bound = publisher.collect_observed(allowed[0])
    require(files["manifest.json"] == raw, "q008_canonical_manifest_changed")
    names = {path.name for path in directory.iterdir()}
    require(files.keys() <= names, "publication_incomplete")
    require(files.keys() == names, "publication_unexpected_member")
    storage._verify_output(directory, files, manifest=True)
    return allowed, files, bound


def _project(
    files: dict[str, bytes], bound: BoundAssessmentResult
) -> tuple[Assessment, Accounting]:
    delivery = strict_object(files["delivery.json"].decode())
    score = strict_object(files["operator-score.json"].decode())
    (unit,) = bound.units
    assessment = Assessment(
        delivery_id=bound.receipt.attempt_id,
        claim_id=unit.statement.unit_id,
        claim=unit.statement.quote,
        model=string_value(delivery["generation_model"]),
        model_assessment=unit.model_assessment,
        operator_score={
            k: score[k]
            for k in (
                "scoring_origin",
                "passed_judgments",
                "possible_judgments",
                "whole_claim_label",
                "plan_evidence",
                "draft_ending_evidence",
            )
        },
        application_status={
            k: delivery[k]
            for k in (
                "semantic_support",
                "evidence_adequacy",
                "edit_necessity",
                "craft",
                "production_attachment_eligible",
                "writer_dispatch_authorized",
            )
        },
    )
    accounting = Accounting.model_validate_json(
        encoded(
            {
                "delivery_id": bound.receipt.attempt_id,
                "request_selection": delivery["observed_request_selection"],
                "request_manifest_sha256": bound.scope.request_sha256,
                "preflight_input_count": delivery["counted_input_tokens"],
                "generation_usage": delivery["usage"],
                "actual_billed_cost": delivery["actual_billed_cost"],
            }
        )
    )
    return assessment, accounting


def lookup(selections: Sequence[ArtifactSelection]) -> Inventory:
    """Resolve selections in order and count the registered delivery once."""
    selected = tuple(ArtifactSelection.model_validate_json(s.model_dump_json()) for s in selections)
    require(bool(selected), "q008_selection_required")
    try:
        allowed, files, bound = _read_publication()
        assessment, account = _project(files, bound)
    except (OSError, sqlite3.Error, ValueError, KeyError, SecretLeakError) as exc:
        # Exceptions may include private paths or source text. Expose only fixed lookup reasons.
        reason = "publication_unavailable"
        if isinstance(exc, EvidenceError):
            if str(exc) in {
                "publication_missing",
                "publication_incomplete",
                "publication_manifest_changed",
                "publication_unexpected_member",
            }:
                reason = str(exc)
            elif str(exc) == "completion_output_conflict":
                reason = "publication_member_changed"
        return Inventory(lookups=tuple(Unavailable(selection=s, reason=reason) for s in selected))

    rows = tuple(
        Available(selection=s, delivery_id=assessment.delivery_id, claim_id=assessment.claim_id)
        if s in allowed
        else Unavailable(selection=s, reason="exact_selection_unavailable")
        for s in selected
    )
    if not any(isinstance(row, Available) for row in rows):
        return Inventory(lookups=rows)
    # This registration has exactly one delivered claim. A lookup row contributes no tokens.
    return Inventory(
        lookups=rows,
        assessments=(assessment,),
        accounting_records=(account,),
        generation_totals=account.generation_usage,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--selection",
        type=Path,
        action="append",
        required=True,
        help="Exact selection JSON. Repeat to look up multiple versions together.",
    )
    args = parser.parse_args(argv)
    try:
        selected = [
            ArtifactSelection.model_validate_json(
                encoded(strict_object(storage._read(path, 8192).decode()))
            )
            for path in args.selection
        ]
    except (ValueError, OSError, SecretLeakError):
        print(json.dumps({"error": "invalid_artifact_selection"}))
        return 2
    print(json.dumps(lookup(selected).model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
