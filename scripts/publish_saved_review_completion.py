"""Publish one registered observed saved-review assessment for either exact selection, offline."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services import saved_review_openai_fixture as wire
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    render_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.review_evidence import (
    EvidenceError,
    JsonObject,
    require,
    strict_object,
)
from open_hollywood_engine.models.assessment_openai import MappedResponse
from open_hollywood_engine.secrets import SecretLeakError

from scripts import q008_sol_smoke as q008
from scripts import q013_assessment, q013_sol_smoke
from scripts import verify_q008_observed_completion as observed_q008
from scripts import verify_q013_observed_completion as observed_q013


@dataclass(frozen=True)
class Registration:
    source: Callable[[], wire._Plan]
    audit: Callable[[Path, str], JsonObject]
    smoke_root: Path
    source_root: Path
    regression_root: Path
    gold: Path
    gold_sha256: str
    approval: str
    score: Path
    score_sha256: str
    audit_sha256: str
    journal_sha256: str

    @property
    def protected(self) -> tuple[Path, ...]:
        return (
            self.source_root,
            self.smoke_root,
            self.regression_root,
            self.gold.parent,
            self.score.parent,
        )


REGISTRATIONS = {
    "q008": Registration(
        source=q008.source,
        audit=q008.audit,
        smoke_root=q008.ROOT,
        source_root=saved.CAPTURED_Q008.archive.parent,
        regression_root=observed_q008.ARCHIVE,
        gold=q008.GOLD,
        gold_sha256=q008.GOLD_SHA,
        approval=observed_q008.APPROVAL,
        score=q008.ROOT.parent / "q008-sol-high-smoke-results-2026-11-20/score.json",
        score_sha256="002ed7f911f46e29db5171543b7e29bc7a4f79cd4a1ba7449aa4d2d2c8586d2c",
        audit_sha256="48efc5b0b38b1e6a25ca729e924df0df2d13878ffd561700d54a1e2e2728623d",
        journal_sha256="3296473ea28363ae080e756f5a8a4b2d8c24c11aa61d3f7fdfd4f8c80cc7363e",
    ),
    "q013": Registration(
        source=q013_sol_smoke.source,
        audit=q013_sol_smoke.audit,
        smoke_root=q013_sol_smoke.ROOT,
        source_root=q013_assessment.REGISTRATION.archive.parent,
        regression_root=observed_q013.ARCHIVE,
        gold=q013_sol_smoke.GOLD,
        gold_sha256=q013_sol_smoke.GOLD_SHA,
        approval=observed_q013.APPROVAL,
        score=q013_sol_smoke.ROOT.parent / "q013-sol-high-smoke-results-2026-11-21/score.json",
        score_sha256="d5e58e34ae7c7bcfc028cf57d730405950bc2df3f7f737834243d289a0683b8e",
        audit_sha256="f0226b6ce1f67be2c037893aac6a4721f4856a019a04a0efcefb0a0791d6c49f",
        journal_sha256="b7a99ff24e0f927b3d9fe215facca923756ef99678dc54379abb873b8e6304cd",
    ),
}


def collect_observed(
    case: str,
    selection: ArtifactSelection,
) -> tuple[dict[str, bytes], BoundAssessmentResult]:
    """Rebuild the registered publication and its bound result without writing a bundle."""
    require(case in REGISTRATIONS, "unregistered_publication")
    reg = REGISTRATIONS[case]
    plan = reg.source()
    pin = plan.source.pin
    require(selection in (pin.review, pin.draft), f"{case}_wrong_selection")
    journal = reg.smoke_root / "output"
    require(not (journal / "journal.json").exists(), f"{case}_unsupported_journal")
    header = strict_object(storage._read(journal / "header.json").decode())
    require(
        header.get("contract") == f"{case}-smoke-journal-1"
        and header.get("origin") == "observed_openai_transport",
        f"{case}_unsupported_journal",
    )
    audit = reg.audit(reg.smoke_root, reg.approval)
    require(
        audit["eligible_for_scoring"] is True
        and audit["ledger"] == "dispatched"
        and audit["closed"] is True
        and audit["delivery_origin"] == "observed_openai_transport"
        and audit["state"] == "bound_unassessed",
        f"{case}_delivery_incomplete",
    )
    score_bytes = storage._read(reg.score)
    require(storage._sha(score_bytes) == reg.score_sha256, f"{case}_operator_score_changed")
    score = strict_object(score_bytes.decode())
    audit_sha = storage._sha(encoded(audit))
    require(
        score["audit_sha256"] == audit_sha == reg.audit_sha256
        and score["approval_sha256"] == reg.approval
        and score["gold_sha256"] == reg.gold_sha256,
        f"{case}_observation_changed",
    )
    bound = BoundAssessmentResult.model_validate_json(encoded(audit["bound_result"]))
    receipt = bound.receipt
    scope = scope_for_batch(plan.work, plan.wire.batch_id, plan.digest)
    require(
        scope == bound.scope
        and receipt.result_sha256 == score["result_final_sha256"]
        and plan.source.selected == pin.review,
        f"{case}_observation_binding",
    )
    completion = complete_work(plan.work, (receipt,), {scope.batch_id: plan.digest})
    require(
        completion.complete_delivery
        and completion.binding == "complete"
        and completion.delivered_units == completion.expected_units == 1
        and completion.unknown_usage_attempts == 0,
        f"{case}_incomplete_work",
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
        f"{case}_usage_incomplete",
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
    require(
        storage._sha(encoded(journal_hashes)) == reg.journal_sha256,
        f"{case}_registered_journal_changed",
    )
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
                "contract": f"{case}-observed-delivery-1",
                "delivery_id": delivery_id,
                "origin": audit["delivery_origin"],
                "state": audit["state"],
                "approval_sha256": reg.approval,
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
            "contract": f"{case}-observed-saved-review-publication-1",
            "source_registration": pin.registration,
            "delivery_id": delivery_id,
            "lookup_selections": [s.model_dump(mode="json") for s in (pin.review, pin.draft)],
            "files_sha256": {k: storage._sha(v) for k, v in files.items()},
            "live_calls": 0,
            "writer_dispatch_authorized": False,
        }
    )
    return files, bound


def publish(
    case: str, selection: ArtifactSelection, destination: Path, *, journal: Path | None = None
) -> Literal["created", "reused"]:
    """Create or reuse one immutable bundle from the named, fixed observation."""
    require(case in REGISTRATIONS, "unregistered_publication")
    if journal is not None:
        require(
            storage._unlinked(journal) == REGISTRATIONS[case].smoke_root / "output",
            f"{case}_unsupported_journal",
        )
    selected = ArtifactSelection.model_validate_json(selection.model_dump_json())
    protected = tuple(path for reg in REGISTRATIONS.values() for path in reg.protected)
    storage._destination(destination, protected)
    files, _ = collect_observed(case, selected)

    def recheck() -> None:
        require(collect_observed(case, selected)[0] == files, f"{case}_publication_source_drift")

    return storage._publish(destination, files, protected, recheck)


def _main(argv: list[str] | None, *, q008_only: bool) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    if not q008_only:
        parser.add_argument("--registration", choices=tuple(REGISTRATIONS), required=True)
    parser.add_argument(
        "--selection", type=Path, required=True, help="Exact artifact selection JSON"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--journal", type=Path, help="Only the registered observed journal is supported"
    )
    args = parser.parse_args(argv)
    case = "q008" if q008_only else args.registration
    try:
        data = strict_object(storage._read(args.selection, 8192).decode())
        selected = ArtifactSelection.model_validate_json(encoded(data))
        status = publish(case, selected, args.output, journal=args.journal)
    except EvidenceError as exc:
        # Only expose fixed operator-facing reasons. Other validators can include source text.
        code = str(exc)
        if code not in {
            f"{case}_unsupported_journal",
            f"{case}_wrong_selection",
            f"{case}_delivery_incomplete",
            "completion_output_conflict",
            "completion_protected_path",
        }:
            code = f"{case}_publication_refused"
        print(json.dumps({"error": code}))
        return 2
    except (ValueError, OSError, sqlite3.Error, KeyError, SecretLeakError):
        print(json.dumps({"error": f"{case}_publication_refused"}))
        return 2
    print(json.dumps({"status": status, "live_calls": 0, "writer_dispatch_authorized": False}))
    return 0


def main(argv: list[str] | None = None) -> int:
    return _main(argv, q008_only=False)


if __name__ == "__main__":
    raise SystemExit(main())
