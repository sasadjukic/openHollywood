"""Replay the private Q008 capture through both exact source selections, offline."""

from __future__ import annotations

import json

from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services import saved_review_openai_fixture as wire
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
    EvidenceError,
    require,
    strict_object,
    text_hash,
)

from scripts import q008_sol_smoke as smoke
from scripts.ordinary_v61_capture import file_hash

ARCHIVE = smoke.ROOT.parent / "q008-observed-completion-audit-2026-11-20"
APPROVAL = "f447f66fa27d9731244304fbebd1a99426e7ed4b8794c0aaa23a3ed6f227e58a"
CAPTURE = "d8b133364673b9f455463ebc4636be1313d8638b60663cca838d11dd9a58fe48"
DRAFT_MANIFEST = "ab5816798cbe453ca1a4c4508e8950d6a9d159bfe61e4039495cc979961cf564"
NATIVE_RENDER = "512879e518d405e71a28b854c159ea89c3b26f157cc07262f637299855b51a7b"


def replay() -> dict[str, object]:
    directory = ARCHIVE / "capture"
    manifest = ARCHIVE / "capture-manifest.json"
    require(file_hash(manifest) == CAPTURE, "q008_regression_manifest")
    members = {
        p.relative_to(directory).as_posix(): file_hash(p)
        for p in directory.rglob("*")
        if p.is_file()
    }
    require(members == strict_object(manifest.read_text("utf-8")), "q008_regression_inventory")

    # Only the original registered location authenticates this as an observed delivery.
    audit = smoke.audit(smoke.ROOT, APPROVAL)
    require(
        audit["eligible_for_scoring"] is True
        and audit["ledger"] == "dispatched"
        and encoded(audit) == (directory / "operator/audit.json").read_bytes(),
        "q008_observed_audit",
    )
    bound = BoundAssessmentResult.model_validate_json(encoded(audit["bound_result"]))
    receipt = bound.receipt
    expected = {receipt.batch_id: smoke.MANIFEST}
    score = strict_object((directory / "operator/score.json").read_text("utf-8"))
    require(
        score["audit_sha256"] == members["operator/audit.json"]
        and score["gold_sha256"] == smoke.GOLD_SHA == members["operator/gold.json"]
        and score["result_final_sha256"] == receipt.result_sha256 == text_hash(bound.raw_final)
        and score["passed_judgments"] == score["possible_judgments"] == 3,
        "q008_operator_score",
    )

    observed = smoke.source()
    completion = complete_work(observed.work, (receipt,), expected)
    require(
        completion.complete_delivery
        and completion.binding == "complete"
        and completion.delivered_units == completion.expected_units == 1
        and (completion.known_input_tokens, completion.known_output_tokens) == (58894, 345)
        and completion.unknown_usage_attempts == 0
        and completion.support == completion.edit_necessity == completion.craft == "unassessed"
        and not completion.whole_relation_credit
        and not completion.writer_dispatch_authorized,
        "q008_incomplete_observed_work",
    )
    views = []
    for selection, digest in (
        (observed.source.pin.review, smoke.MANIFEST),
        (observed.source.pin.draft, DRAFT_MANIFEST),
    ):
        frozen = directory / "selections" / (selection.role + ".json")
        require(
            selection == ArtifactSelection.model_validate_json(frozen.read_bytes()),
            "q008_exact_selection",
        )
        plan = wire._prepare(saved.CAPTURED_Q008.name, selection)
        require(
            plan.source.selected == selection
            and plan.source.pin == observed.source.pin
            and plan.work == observed.work
            and plan.digest == digest,
            "q008_selection_association",
        )
        scope = scope_for_batch(plan.work, receipt.batch_id, smoke.MANIFEST)
        rebuilt = bind_assessment_result(plan.work, scope, bound.delivery_receipt, bound.raw_final)
        require(rebuilt == bound, "q008_observed_result_changed")
        if selection.role == "reviewed_draft":
            draft_scope = scope_for_batch(plan.work, receipt.batch_id, plan.digest)
            try:
                bind_assessment_result(
                    plan.work, draft_scope, bound.delivery_receipt, bound.raw_final
                )
            except EvidenceError as exc:
                require(str(exc) == "wrong_request_receipt", "q008_wrong_rejection")
            else:
                raise EvidenceError("q008_reassigned_observed_receipt")
        require(
            complete_work(plan.work, (rebuilt.receipt,), expected) == completion,
            "q008_selection_completion_changed",
        )
        rendered = render_assessment_result(
            plan.work, scope, bound.delivery_receipt, bound.raw_final
        )
        lines = rendered.splitlines()
        fence = lines[-1]
        rendered_data = strict_object("\n".join(lines[lines.index(fence + "json") + 1 : -1]))
        require(
            rendered_data
            == {
                "full_work": plan.work.model_dump(mode="json"),
                "result": bound.model_dump(mode="json"),
            },
            "q008_render_changed",
        )
        require(text_hash(rendered) == NATIVE_RENDER, "q008_selection_render_changed")
        views.append(
            {
                "selection": selection.model_dump(mode="json"),
                "selection_manifest_sha256": plan.digest,
                "selected_for_observed_request": selection == observed.source.selected,
            }
        )
    return {
        "capture_manifest_sha256": CAPTURE,
        "attempt_id": receipt.attempt_id,
        "observed_request_selection": observed.source.selected.model_dump(mode="json"),
        "observed_request_manifest_sha256": receipt.request_sha256,
        "completion": completion.model_dump(mode="json"),
        "native_render_sha256": NATIVE_RENDER,
        "views": views,
        "operator_score_sha256": members["operator/score.json"],
    }


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
