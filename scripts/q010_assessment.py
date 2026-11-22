"""Bind Q010's rehearsed endpoint bytes to the authenticated ordinary critique and fresh work."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services import saved_review_openai_fixture as renderer
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.assessment_result import scope_for_batch
from open_hollywood_engine.evaluations.assessment_work import AssessmentWork
from open_hollywood_engine.evaluations.review_evidence import object_value, require, strict_object
from open_hollywood_engine.models.assessment_openai import WireMapping, check_outgoing

REHEARSAL = (
    Path(__file__).resolve().parents[1] / "data/diagnostics/q010-intake-rehearsal-2026-11-22"
)
INTAKE_SHA = "fed24c56430685a65ab7cfb693f9e4703ad7848c694a0c78cd4e68e316a54722"
WIRE_SHA = "f31e223b79e2de14b52225cc49e8003408605a08f371ee72a87de74754448f10"
BODY_HASHES = (
    "2ee4c9e4617f6b8c7cc203af1d4491c9ec85c916ea3b9c68c2fa3971f16dcb46",
    "b30c0697f7aca46f7ae7075ad17a2c15cfc13c4a6c0fd8458d7425a743a35bb5",
)


@dataclass(frozen=True)
class Plan:
    work: AssessmentWork
    selected: ArtifactSelection
    reviewed_draft: ArtifactSelection
    wire: WireMapping
    files: dict[str, bytes]

    @property
    def digest(self) -> str:
        return storage._sha(self.files["request-manifest.json"])


def source() -> Plan:
    capture = saved.CAPTURED_Q008
    original = saved._prepare(saved._open(capture.name, allow_capture=True), None)
    review, draft = original.pin.review, original.pin.draft
    require(
        original.selected == review
        and review.version_id == "2268e6e8-b82b-4cca-932f-55cc418a58b5"
        and draft.version_id == "b74efc96-dbe6-4147-8dd3-a1c24f295321",
        "q010_version_pair",
    )
    rendered = REHEARSAL / "rendered"
    intake_bytes = storage._read(rendered / "Q010-intake.json")
    require(storage._sha(intake_bytes) == INTAKE_SHA, "q010_intake_drift")
    recorded = IntakeResult.model_validate_json(intake_bytes)
    intake = compile_intake(original.intake.source, recorded.plan)
    require(intake == recorded, "q010_source_intake_replay")
    work, declarations, briefs = intake.pending_work, intake.declarations, intake.briefs
    if work is None or declarations is None or briefs is None:
        raise ValueError("q010_missing_work")
    (batch,) = work.batches
    native = encoded(
        {
            "work_sha256": work.fingerprint,
            "batch_id": batch.batch_id,
            "declarations": declarations.model_dump(mode="json"),
            "briefs": briefs.model_dump(mode="json"),
            "selected": review.model_dump(mode="json"),
        }
    )
    require(native == storage._read(rendered / "Q010-rehearsal-input.json"), "q010_native_drift")
    scope = scope_for_batch(work, batch.batch_id, storage._sha(native))
    metadata = storage._read(rendered / "Q010-wire.json")
    require(storage._sha(metadata) == WIRE_SHA, "q010_mapping_drift")
    mapping = strict_object(metadata.decode())
    endpoints = mapping["endpoints"]
    assert isinstance(endpoints, list)
    files = {}
    for stage, item, digest in zip(
        ("input_count", "generation"), endpoints, BODY_HASHES, strict=True
    ):
        endpoint = object_value(item)
        name = stage + "-request.json"
        body = storage._read(rendered / name)
        require(endpoint["stage"] == stage and storage._sha(body) == digest, "q010_body_drift")
        endpoint["body_utf8"] = body.decode()
        files[name] = body
    wire = WireMapping.model_validate_json(encoded(mapping))
    require(
        scope.active_unit_ids == wire.active_unit_ids == ("Q010",)
        and wire.native_request_sha256 == scope.request_sha256
        and wire.batch_id == scope.batch_id
        and wire.work_sha256 == work.fingerprint,
        "q010_assessment_binding",
    )
    for end in wire.endpoints:
        check_outgoing(end, renderer._request(end))
    # The archive supplies the critic and immutable versions. The Q010 intake supplies
    # the assessment identity. No earlier assessment receipt participates in this chain.
    critic = strict_object(original.files["source-receipt.json"].decode())
    files["source-receipt.json"] = encoded(
        {
            "contract": "q010-critique-source-1",
            "capture_registration": capture.name,
            "capture_seal_sha256": capture.seal_sha256,
            "critic_invocation": original.pin.invocation_id,
            "critic_terminal_sha256": critic["critic_terminal_sha256"],
            "critic_http_receipt_sha256": critic["critic_http_receipt_sha256"],
            "database_sha256": original.pin.database_capture_sha256,
            "review": review.model_dump(mode="json"),
            "draft": draft.model_dump(mode="json"),
            "intake_sha256": INTAKE_SHA,
            "work_sha256": work.fingerprint,
            "native_request_sha256": scope.request_sha256,
        }
    )
    files["request-manifest.json"] = encoded(
        {
            "contract": "q010-sol-high-request-1",
            "wire": strict_object(metadata.decode()),
            "source_receipt_sha256": storage._sha(files["source-receipt.json"]),
            "selected": review.model_dump(mode="json"),
            "input_artifact_version_ids": [review.version_id, draft.version_id],
            "count_limit": 1,
            "generation_limit": 1,
            "retry_limit": 0,
        }
    )
    return Plan(work, review, draft, wire, files)
