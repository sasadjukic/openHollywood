"""Publish the registered Q008 assessment for either exact artifact selection, offline."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Literal

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    render_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.review_evidence import EvidenceError, require, strict_object
from open_hollywood_engine.models.assessment_openai import MappedResponse
from open_hollywood_engine.secrets import SecretLeakError

from scripts import q008_sol_smoke as smoke
from scripts.verify_q008_observed_completion import APPROVAL, ARCHIVE

SCORE = smoke.ROOT.parent / "q008-sol-high-smoke-results-2026-11-20/score.json"
SCORE_SHA = "002ed7f911f46e29db5171543b7e29bc7a4f79cd4a1ba7449aa4d2d2c8586d2c"
AUDIT_SHA = "48efc5b0b38b1e6a25ca729e924df0df2d13878ffd561700d54a1e2e2728623d"
JOURNAL_SHA = "3296473ea28363ae080e756f5a8a4b2d8c24c11aa61d3f7fdfd4f8c80cc7363e"


def collect_observed(
    selection: ArtifactSelection,
) -> tuple[dict[str, bytes], BoundAssessmentResult]:
    """Rebuild the registered publication and its bound result without writing a bundle."""
    plan = smoke.source()
    pin = plan.source.pin
    require(selection in (pin.review, pin.draft), "q008_wrong_selection")
    journal = smoke.ROOT / "output"
    require(not (journal / "journal.json").exists(), "q008_unsupported_journal")
    header = strict_object(storage._read(journal / "header.json").decode())
    require(
        header.get("contract") == "q008-smoke-journal-1"
        and header.get("origin") == "observed_openai_transport",
        "q008_unsupported_journal",
    )
    audit = smoke.audit(smoke.ROOT, APPROVAL)
    require(
        audit["eligible_for_scoring"] is True
        and audit["ledger"] == "dispatched"
        and audit["closed"] is True
        and audit["delivery_origin"] == "observed_openai_transport"
        and audit["state"] == "bound_unassessed",
        "q008_delivery_incomplete",
    )
    score_bytes = storage._read(SCORE)
    require(storage._sha(score_bytes) == SCORE_SHA, "q008_operator_score_changed")
    score = strict_object(score_bytes.decode())
    audit_sha = storage._sha(encoded(audit))
    require(
        score["audit_sha256"] == audit_sha == AUDIT_SHA
        and score["approval_sha256"] == APPROVAL
        and score["gold_sha256"] == smoke.GOLD_SHA,
        "q008_observation_changed",
    )
    bound = BoundAssessmentResult.model_validate_json(encoded(audit["bound_result"]))
    receipt = bound.receipt
    scope = scope_for_batch(plan.work, plan.wire.batch_id, plan.digest)
    require(
        scope == bound.scope
        and receipt.result_sha256 == score["result_final_sha256"]
        and plan.source.selected == pin.review,
        "q008_observation_binding",
    )
    completion = complete_work(plan.work, (receipt,), {scope.batch_id: plan.digest})
    require(
        completion.complete_delivery
        and completion.binding == "complete"
        and completion.delivered_units == completion.expected_units == 1
        and completion.unknown_usage_attempts == 0,
        "q008_incomplete_work",
    )
    slots = audit["slots"]
    assert isinstance(slots, list)
    count, generation = slots
    assert isinstance(count, dict) and isinstance(generation, dict)
    counted = MappedResponse.model_validate_json(encoded(count["mapped"]))
    assessed = MappedResponse.model_validate_json(encoded(generation["mapped"]))
    usage = assessed.usage
    require(
        counted.state == "counted"
        and assessed.state == "complete"
        and counted.counted_input_tokens == usage.input_tokens == completion.known_input_tokens
        and usage.output_tokens == completion.known_output_tokens
        and usage.reasoning_tokens == receipt.reasoning_tokens
        and usage.reasoning_tokens is not None
        and usage.cached_input_tokens is not None,
        "q008_usage_incomplete",
    )
    # The closure authenticates both observed endpoint chains. Retain the raw members
    # separately from the single normalized accounting record.
    journal_files = {
        name: storage._read(journal / name)
        for name in (
            "header.json",
            "input_count-intent.json",
            "input_count-outcome.json",
            "generation-intent.json",
            "generation-outcome.json",
            "stop.json",
        )
    }
    journal_hashes = {k: storage._sha(v) for k, v in journal_files.items()}
    require(storage._sha(encoded(journal_hashes)) == JOURNAL_SHA, "q008_registered_journal_changed")
    delivery_id = receipt.attempt_id
    files = {
        **plan.files,
        **journal_files,
        "intake.json": plan.source.files["intake.json"],
        "operator-score.json": score_bytes,
        "evidence.md": render_assessment_result(
            plan.work, scope, bound.delivery_receipt, bound.raw_final
        ).encode(),
        "delivery.json": encoded(
            {
                "contract": "q008-observed-delivery-1",
                "delivery_id": delivery_id,
                "origin": audit["delivery_origin"],
                "state": audit["state"],
                "approval_sha256": APPROVAL,
                "audit_sha256": audit_sha,
                "observed_request_selection": pin.review.model_dump(mode="json"),
                "request_manifest_sha256": receipt.request_sha256,
                "work_sha256": receipt.work_sha256,
                "batch_id": receipt.batch_id,
                "assessed_unit_ids": receipt.assessed_unit_ids,
                "raw_final_sha256": receipt.result_sha256,
                "binding": completion.binding,
                "complete_delivery": completion.complete_delivery,
                "counted_input_tokens": counted.counted_input_tokens,
                "generation_response_id": assessed.response_id,
                "generation_model": assessed.returned_model,
                "usage": usage.model_dump(mode="json"),
                "actual_billed_cost": audit["actual_billed_cost"],
                "semantic_support": bound.support,
                "evidence_adequacy": bound.evidence_adequacy,
                "edit_necessity": bound.edit_necessity,
                "craft": bound.craft,
                "production_attachment_eligible": False,
                "writer_dispatch_authorized": False,
            }
        ),
    }
    # Lookup order is canonical and independent of the selection that opened this bundle.
    files["manifest.json"] = encoded(
        {
            "contract": "q008-observed-saved-review-publication-1",
            "source_registration": pin.registration,
            "delivery_id": delivery_id,
            "lookup_selections": [s.model_dump(mode="json") for s in (pin.review, pin.draft)],
            "files_sha256": {k: storage._sha(v) for k, v in files.items()},
            "live_calls": 0,
            "writer_dispatch_authorized": False,
        }
    )
    return files, bound


def _collect(selection: ArtifactSelection) -> dict[str, bytes]:
    files, _ = collect_observed(selection)
    return files


def publish(
    selection: ArtifactSelection, destination: Path, *, journal: Path | None = None
) -> Literal["created", "reused"]:
    """Create or reuse one immutable bundle from the fixed observed journal."""
    if journal is not None:
        require(storage._unlinked(journal) == smoke.ROOT / "output", "q008_unsupported_journal")
    selected = ArtifactSelection.model_validate_json(selection.model_dump_json())
    protected = (
        saved.CAPTURED_Q008.archive.parent,
        smoke.ROOT,
        smoke.GOLD.parent,
        SCORE.parent,
        ARCHIVE,
    )
    storage._destination(destination, protected)
    files = _collect(selected)

    def recheck() -> None:
        require(_collect(selected) == files, "q008_publication_source_drift")

    return storage._publish(destination, files, protected, recheck)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--selection", type=Path, required=True, help="Exact artifact selection JSON"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--journal", type=Path, help="Only the registered observed journal is supported"
    )
    args = parser.parse_args(argv)
    try:
        data = strict_object(storage._read(args.selection, 8192).decode())
        selected = ArtifactSelection.model_validate_json(encoded(data))
        status = publish(selected, args.output, journal=args.journal)
    except EvidenceError as exc:
        # Only expose fixed operator-facing reasons. Other validators can include source text.
        code = str(exc)
        if code not in {
            "q008_unsupported_journal",
            "q008_wrong_selection",
            "q008_delivery_incomplete",
            "completion_output_conflict",
            "completion_protected_path",
        }:
            code = "q008_publication_refused"
        print(json.dumps({"error": code}))
        return 2
    except (ValueError, OSError, sqlite3.Error, KeyError, SecretLeakError):
        print(json.dumps({"error": "q008_publication_refused"}))
        return 2
    print(json.dumps({"status": status, "live_calls": 0, "writer_dispatch_authorized": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
