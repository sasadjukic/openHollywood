"""Look up Q008 and Q013 by exact artifact selection in their registered publications."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass
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

from scripts import publish_saved_review_completion as publisher


@dataclass(frozen=True)
class _Publication:
    case: str
    directory: Path
    manifest_sha256: str
    selector_sha256: tuple[str, str]
    score_fields: tuple[str, ...]


_ARCHIVES = Path(__file__).resolve().parents[1] / "data/diagnostics"
Q008 = _Publication(
    "q008",
    _ARCHIVES / "q008-publication-2026-11-21/critique-first",
    "efef8fc3348b3a5cfc3c9529e6e645d390685e5030c01d56b257eaa27631619d",
    (
        "84c166f4a011fefa6f676ce61bd9ef0247313de7452ab98d76d62b44fd58a843",
        "4c959fe2913da5a9ccedf8e98ddf6ab0d11016b0d53fb9c82c411a4bffb76baa",
    ),
    ("whole_claim_label", "plan_evidence", "draft_ending_evidence"),
)
Q013 = _Publication(
    "q013",
    _ARCHIVES / "q013-publication-2026-11-22/critique-first",
    "aa4d3d4563c03592748eae990449888697681b4611715cc70e0bcde589df24fc",
    (
        "26aa92d3fcfb9acce1345491f9779a0de5499647fbdde15922f9721557a62c34",
        "257913bb812a2732e1c2b83bc648e4047c153a8249f14a3d95af107aec36c01f",
    ),
    ("claim_correctness", "evidence_coverage"),
)


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
    contract: Literal["saved-review-consumer-lookup-1"] = "saved-review-consumer-lookup-1"
    lookups: tuple[Available | Unavailable, ...]
    assessments: tuple[Assessment, ...] = ()
    accounting_records: tuple[Accounting, ...] = ()
    generation_totals: Usage | None = None


def _read_publication(
    registration: _Publication,
) -> tuple[tuple[ArtifactSelection, ...], dict[str, bytes], BoundAssessmentResult]:
    directory = storage._unlinked(registration.directory)
    require(directory.is_dir(), "publication_missing")
    require((directory / "manifest.json").is_file(), "publication_incomplete")
    raw = storage._read(directory / "manifest.json")
    require(storage._sha(raw) == registration.manifest_sha256, "publication_manifest_changed")
    manifest = strict_object(raw.decode())
    selectors = manifest["lookup_selections"]
    require(isinstance(selectors, list) and len(selectors) == 2, "invalid_publication_selectors")
    assert isinstance(selectors, list)
    allowed = tuple(ArtifactSelection.model_validate_json(encoded(s)) for s in selectors)

    # The registered manifest puts the observed critique first, even for draft-only lookups.
    files, bound = publisher.collect_observed(registration.case, allowed[0])
    require(files["manifest.json"] == raw, "publication_binding")
    names = {path.name for path in directory.iterdir()}
    require(files.keys() <= names, "publication_incomplete")
    require(files.keys() == names, "publication_unexpected_member")
    storage._verify_output(directory, files, manifest=True)
    return allowed, files, bound


def _project(
    registration: _Publication, files: dict[str, bytes], bound: BoundAssessmentResult
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
                *registration.score_fields,
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


def _lookup_publication(
    registration: _Publication, selected: Sequence[ArtifactSelection]
) -> Inventory:
    try:
        allowed, files, bound = _read_publication(registration)
        assessment, account = _project(registration, files, bound)
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


def lookup(selections: Sequence[ArtifactSelection]) -> Inventory:
    """Return ordered lookup rows and account once per authenticated delivery."""
    selected = tuple(ArtifactSelection.model_validate_json(s.model_dump_json()) for s in selections)
    require(bool(selected), "selection_required")
    # Routing pins survive a missing publication. The authenticated manifest still
    # has to match the entire selection before the consumer can return a result.
    digests = {s: storage._sha(encoded(s.model_dump(mode="json"))) for s in dict.fromkeys(selected)}
    by_selection: dict[ArtifactSelection, Available | Unavailable] = {}
    assessments: dict[tuple[str, str], Assessment] = {}
    accounts: dict[str, Accounting] = {}
    for registration in (Q008, Q013):
        matching = [s for s, digest in digests.items() if digest in registration.selector_sha256]
        if not matching:
            continue
        view = _lookup_publication(registration, matching)
        by_selection.update((row.selection, row) for row in view.lookups)
        assessments.update(((a.delivery_id, a.claim_id), a) for a in view.assessments)
        accounts.update((a.delivery_id, a) for a in view.accounting_records)

    rows = tuple(
        by_selection[s]
        if s in by_selection
        else Unavailable(selection=s, reason="exact_selection_unavailable")
        for s in selected
    )
    usage = [a.generation_usage for a in accounts.values()]
    return Inventory(
        lookups=rows,
        assessments=tuple(assessments.values()),
        accounting_records=tuple(accounts.values()),
        generation_totals=Usage(
            input_tokens=sum(u.input_tokens for u in usage),
            output_tokens=sum(u.output_tokens for u in usage),
            reasoning_tokens=sum(u.reasoning_tokens for u in usage),
            cached_input_tokens=sum(u.cached_input_tokens for u in usage),
        )
        if usage
        else None,
    )


def _run_cli(
    argv: list[str] | None,
    description: str | None,
    resolve: Callable[[Sequence[ArtifactSelection]], Record],
) -> int:
    parser = argparse.ArgumentParser(description=description)
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
    print(json.dumps(resolve(selected).model_dump(mode="json"), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    return _run_cli(argv, __doc__, lookup)


if __name__ == "__main__":
    raise SystemExit(main())
