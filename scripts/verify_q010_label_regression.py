"""Replay the sealed Q010 label/evidence disagreement locally. No transport or credentials."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from open_hollywood_engine.evaluations.assessment_delivery import Stage
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import map_response
from open_hollywood_engine.models.openai_catalog import OpenAIModelSpec

from scripts.ordinary_v61_capture import file_hash, ledger_state

ROOT = Path(__file__).resolve().parents[1] / "data/diagnostics/q010-label-audit-2026-11-22"
MANIFEST = "a99ba2894468426e5261721b3ef813601e3502a0a9ad11e87b08f1a3b319a19b"
FINAL = "567e36524c111534f4fd791d7761fe973e621eacd4ebbb852cf9d65decdecd8f"


def verified_capture(root: Path) -> Path:
    manifest = root / "capture-manifest.json"
    require(file_hash(manifest) == MANIFEST, "q010_regression_manifest")
    members = json.loads(manifest.read_bytes())
    capture = root / "capture"
    require(
        {p.relative_to(capture).as_posix() for p in capture.rglob("*") if p.is_file()}
        == set(members),
        "q010_regression_inventory",
    )
    for name, expected in members.items():
        require(file_hash(capture / name) == expected, "q010_regression_member")
    return capture


def replay() -> dict[str, object]:
    capture = verified_capture(ROOT)
    smoke = capture / "smoke"
    audit = json.loads((capture / "operator/audit.json").read_bytes())
    score = json.loads((capture / "operator/score.json").read_bytes())
    (gold,) = (
        r
        for r in json.loads((capture / "operator/gold.json").read_bytes())["records"]
        if r["whole_field"]["field_id"] == "Q010"
    )
    require(
        ledger_state(smoke, file_hash(smoke / "plan.json")) == "dispatched"
        and audit["closed"]
        and audit["eligible_for_scoring"]
        and audit["delivery_origin"] == "observed_openai_transport",
        "q010_observed_delivery",
    )
    manifest = smoke / "request-manifest.json"
    request_manifest = json.loads(manifest.read_bytes())
    source = json.loads((smoke / "source-receipt.json").read_bytes())
    require(
        request_manifest["selected"] == score["selected"] == source["review"]
        and source["review"]["version_id"] == gold["artifacts"]["critique"]["version"]
        and source["draft"] == score["reviewed_draft"]
        and request_manifest["input_artifact_version_ids"]
        == [source["review"]["version_id"], source["draft"]["version_id"]]
        and source["capture_seal_sha256"] == file_hash(capture / "source/critic-seal.json")
        and source["intake_sha256"] == file_hash(capture / "source/intake.json")
        and source["native_request_sha256"] == file_hash(capture / "source/native-input.json"),
        "q010_regression_versions",
    )
    spec = OpenAIModelSpec.model_validate(request_manifest["wire"]["model_spec"])
    bound = BoundAssessmentResult.model_validate_json(json.dumps(audit["bound_result"]))
    stages: tuple[Stage, Stage] = ("input_count", "generation")
    for stage, slot in zip(stages, audit["slots"], strict=True):
        terminal = json.loads((smoke / "output" / (stage + "-outcome.json")).read_bytes())
        raw = terminal["body"].encode()
        mapped = map_response(stage, terminal["http_status"], raw, spec)
        require(
            slot["stage"] == stage
            and slot["http_status"] == 200
            and slot["raw_sha256"] == hashlib.sha256(raw).hexdigest()
            and mapped.model_dump(mode="json") == slot["mapped"],
            "q010_endpoint_replay",
        )
        if stage == "generation":
            require(
                mapped.raw_final == bound.raw_final and mapped.raw_final_utf8_sha256 == FINAL,
                "q010_provider_final",
            )

    intake = IntakeResult.model_validate_json((capture / "source/intake.json").read_bytes())
    work = intake.pending_work
    if work is None:
        raise ValueError("q010_missing_work")
    (batch,) = work.batches
    scope = scope_for_batch(work, batch.batch_id, file_hash(manifest))
    rebuilt = bind_assessment_result(work, scope, bound.delivery_receipt, bound.raw_final)
    require(rebuilt == bound and scope.active_unit_ids == ("Q010",), "q010_binding_replay")
    (unit,) = rebuilt.units
    (location,) = unit.evidence_locations
    (ending,) = (w for w in gold["draft_witnesses"] if w["ref"] == "E0321")
    start, end = ending["prose_span"]
    require(
        unit.statement.quote == gold["whole_field"]["text"]
        and unit.model_assessment.evidence == (location.ref,) == ("E0883",)
        and location.document_version == gold["artifacts"]["scene_draft"]["version"]
        and location.field_pointer == "/prose"
        and location.quote[start:end] == ending["quote"]
        and end == len(location.quote)
        and score["evidence_coverage"]["model_assessment"]
        == unit.model_assessment.model_dump(mode="json"),
        "q010_passage_binding",
    )
    require(
        unit.model_assessment.support == score["claim_correctness"]["returned"] == "unsupported"
        and gold["judgment"]["whole_claim_gold"]
        == score["claim_correctness"]["expected"]
        == "uncertain"
        and score["claim_correctness"]["score"] == "fail"
        and score["evidence_coverage"]["score"] == "pass"
        and rebuilt.support == rebuilt.evidence_adequacy == "unassessed"
        and not rebuilt.writer_dispatch_authorized,
        "q010_label_or_score",
    )
    return {
        "observed_final_sha256": FINAL,
        "archive_manifest_sha256": MANIFEST,
        "returned": unit.model_assessment.support,
        "gold": gold["judgment"]["whole_claim_gold"],
        "claim_score": score["claim_correctness"]["score"],
        "evidence_score": score["evidence_coverage"]["score"],
        "live_calls_this_replay": 0,
    }


if __name__ == "__main__":
    print(json.dumps(replay()))
