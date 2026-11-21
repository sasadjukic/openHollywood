"""Replay the original Q013 delivery and both exact selection paths without dispatching."""

from __future__ import annotations

import json

from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    bind_assessment_result,
    render_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import complete_work
from open_hollywood_engine.evaluations.review_evidence import (
    object_value,
    require,
    strict_object,
    text_hash,
)
from open_hollywood_engine.models.assessment_openai import MappedResponse

from scripts import q013_assessment as case
from scripts import q013_sol_smoke as smoke
from scripts.ordinary_v61_capture import file_hash

ARCHIVE = smoke.ROOT.parent / "q013-observed-completion-audit-2026-11-21"
APPROVAL = "ca0314f557dc4a8b4e23085cc974dfd4d7c51abbc30c510d6f1e6f9149342ee3"
CAPTURE = "20a66691b10bd8462b8cd611782ef5cabe265a8ee079be2c782ffa88ee9d6ff3"
DRAFT_MANIFEST = "47f1bc0e1778e7663c2a6cfcde86e69bc36b28109373a171747ec63067054169"
NATIVE_RENDER = "177fc22bb38ca93665e53d9fd375f2b3a7f22f8d981c43dc26b0a401dc46d5ad"


def replay() -> dict[str, object]:
    capture = ARCHIVE / "capture"
    manifest = ARCHIVE / "capture-manifest.json"
    require(file_hash(manifest) == CAPTURE, "q013_regression_manifest")
    members = {
        p.relative_to(capture).as_posix(): file_hash(p) for p in capture.rglob("*") if p.is_file()
    }
    require(members == strict_object(manifest.read_text("utf-8")), "q013_regression_members")
    results = smoke.ROOT.parent / "q013-sol-high-smoke-results-2026-11-21"
    originals = {
        "smoke": smoke.ROOT,
        "registration": case.REGISTRATION.archive,
        "selections": case.REGISTRATION.archive.parent,
        "operator": results,
    }
    for name, digest in members.items():
        group, relative = name.split("/", 1)
        original_file = smoke.GOLD if name == "operator/gold.json" else originals[group] / relative
        require(file_hash(original_file) == digest, "q013_regression_source_changed")

    # Only the registered original journal supplies observed transport authority.
    audit = smoke.audit(smoke.ROOT, APPROVAL)
    require(
        audit["eligible_for_scoring"] is True
        and audit["delivery_origin"] == "observed_openai_transport"
        and audit["closed"] is True
        and audit["ledger"] == "dispatched"
        and encoded(audit) == (capture / "operator/audit.json").read_bytes(),
        "q013_observed_delivery",
    )
    original = smoke.source()
    bound = BoundAssessmentResult.model_validate_json(encoded(audit["bound_result"]))
    receipt = bound.receipt
    expected = {receipt.batch_id: original.digest}
    completion = complete_work(original.work, (receipt,), expected)
    require(
        receipt.assessed_unit_ids == ("Q013",)
        and receipt.request_sha256 == smoke.MANIFEST
        and receipt.result_sha256 == text_hash(bound.raw_final)
        and completion.complete_delivery
        and completion.binding == "complete"
        and completion.completed_batches == completion.expected_batches == 1
        and completion.delivered_units == completion.expected_units == 1
        and completion.unknown_usage_attempts == 0
        and not completion.writer_dispatch_authorized
        and bound.support
        == bound.evidence_adequacy
        == bound.edit_necessity
        == bound.craft
        == "unassessed",
        "q013_native_completion",
    )
    slots = audit["slots"]
    assert isinstance(slots, list)
    count_slot, generation_slot = map(object_value, slots)
    counted = MappedResponse.model_validate_json(encoded(count_slot["mapped"]))
    generation = MappedResponse.model_validate_json(encoded(generation_slot["mapped"]))
    usage = generation.usage
    require(
        count_slot["state"] == "count_admitted"
        and generation_slot["state"] == "bound_unassessed"
        and counted.counted_input_tokens
        == usage.input_tokens
        == completion.known_input_tokens
        == 62_835
        and usage.output_tokens == completion.known_output_tokens == 427
        and usage.reasoning_tokens == receipt.reasoning_tokens == 255
        and usage.cached_input_tokens == 0
        and generation.raw_final == bound.raw_final,
        "q013_observed_accounting",
    )
    score = strict_object((capture / "operator/score.json").read_text("utf-8"))
    (unit,) = bound.units
    (location,) = unit.evidence_locations
    require(
        score["audit_sha256"] == members["operator/audit.json"]
        and score["gold_sha256"] == members["operator/gold.json"] == smoke.GOLD_SHA
        and score["approval_sha256"] == APPROVAL
        and score["request_manifest_sha256"] == receipt.request_sha256
        and score["result_final_sha256"] == receipt.result_sha256
        and score["review_version"] == original.source.pin.review.version_id
        and score["draft_version"]
        == location.document_version
        == original.source.pin.draft.version_id
        and object_value(score["claim_correctness"])["score"] == "pass"
        and object_value(score["evidence_coverage"])["score"] == "pass"
        and unit.model_assessment.support == "supported"
        and unit.model_assessment.evidence == ("E0920",),
        "q013_separate_score",
    )

    lookups = []
    for selected, digest in (
        (original.source.pin.review, smoke.MANIFEST),
        (original.source.pin.draft, DRAFT_MANIFEST),
    ):
        saved = capture / "selections" / (selected.role + ".json")
        require(
            ArtifactSelection.model_validate_json(saved.read_bytes()) == selected, "q013_selector"
        )
        plan = case.prepare(selected)
        require(
            plan.source.selected == selected
            and plan.source.pin == original.source.pin
            and plan.work == original.work
            and plan.digest == digest,
            "q013_selection_association",
        )
        # Reopening through the draft retains the critique-selected wire identity.
        scope = scope_for_batch(plan.work, receipt.batch_id, original.digest)
        rebuilt = bind_assessment_result(plan.work, scope, bound.delivery_receipt, bound.raw_final)
        require(
            rebuilt == bound
            and complete_work(plan.work, (rebuilt.receipt,), expected) == completion,
            "q013_selection_completion",
        )
        rendered = render_assessment_result(
            plan.work, scope, bound.delivery_receipt, bound.raw_final
        )
        require(text_hash(rendered) == NATIVE_RENDER, "q013_evidence_render")
        lookups.append(
            {
                "selection": selected.model_dump(mode="json"),
                "selection_manifest_sha256": plan.digest,
                "selected_for_request": selected == original.source.selected,
                "delivery_id": rebuilt.receipt.attempt_id,
            }
        )
    return {
        "capture_manifest_sha256": CAPTURE,
        "observed_request_selection": original.source.selected.model_dump(mode="json"),
        "observed_request_manifest_sha256": original.digest,
        "delivery_id": receipt.attempt_id,
        "preflight_input_count": counted.counted_input_tokens,
        "generation_usage": usage.model_dump(mode="json"),
        "completion": completion.model_dump(mode="json"),
        "lookups": lookups,
        "native_render_sha256": NATIVE_RENDER,
        "operator_score_sha256": members["operator/score.json"],
        "live_calls": 0,
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
