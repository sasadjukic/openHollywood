"""Rebuild a read-only Sol-high assessment request for either registered Q013 selection."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services import saved_review_openai_fixture as wire
from open_hollywood_api.services.assessment_intake import IntakeBatchPlan, collect_intakes
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.review_evidence_export import readonly_connection
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.review_evidence import object_value, require, strict_object
from open_hollywood_engine.models.assessment_openai import _prepare_wire
from open_hollywood_engine.models.contracts import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)
from open_hollywood_engine.models.openai_catalog import builtin_model_specs

REGISTRATION = saved._Registration(
    "saved-v61-q013-2026-11-21",
    Path(__file__).resolve().parents[1]
    / "data/diagnostics/q013-downstream-2026-11-21/registration",
    "source",
    "ee479205f2bddddd57b66e69bdeae0b444bdf7ae29cc443616f864d7c32b9636",
    database_limit=24_580_096,
)


def _open() -> saved._Archive:
    raw = storage._read(REGISTRATION.archive / "acceptance-seal.json")
    require(storage._sha(raw) == REGISTRATION.seal_sha256, "q013_seal_changed")
    seal = strict_object(raw.decode())
    require(seal["registration"] == REGISTRATION.name, "q013_registration")
    members = object_value(seal["members_sha256"])
    return saved._Archive(REGISTRATION, {k: v for k, v in members.items() if isinstance(v, str)})


def _source(archive: saved._Archive, selection: ArtifactSelection) -> saved._Prepared:
    archive.inventory("source-fixture", {"intake", "request.json", "source-manifest.json"})
    manifest_raw = archive.read("source-fixture/source-manifest.json")
    manifest = saved._CaptureManifest.model_validate_json(manifest_raw)
    selected = ArtifactSelection.model_validate_json(selection.model_dump_json())
    review, draft = manifest.selection
    require(selected in (review, draft), "saved_review_wrong_selection")
    members = saved._intake_members(archive, manifest)
    index = strict_object(members["manifest.json"].decode())
    archive.inventory("database", {"open_hollywood.db"})
    image = archive.read("database/open_hollywood.db", database=True)
    with TemporaryDirectory() as tmp:
        database = Path(tmp) / "review.db"
        database.write_bytes(image)
        with readonly_connection(database) as conn:
            saved._verify_selection(conn, review)
            saved._verify_selection(conn, draft)
        collection = collect_intakes("saved_review", database, (manifest.review_invocation_id,))
    source = collection.entries[0].source
    require(source is not None, "q013_incompatible_source")
    assert source is not None
    collection_data = collection.model_dump(mode="json")
    collection_data["source_path"] = index["source_path"]
    require(
        canonical_sha256(collection_data) == manifest.collection_sha256 == index["source_sha256"],
        "q013_collection",
    )
    plans = IntakeBatchPlan.model_validate_json(members["plan.json"])
    require(
        set(plans.plans) == {source.review_id}
        and canonical_sha256(plans.model_dump(mode="json")) == index["plan_sha256"],
        "q013_plan_binding",
    )
    intake = compile_intake(source, plans.plans[source.review_id])
    require(intake == IntakeResult.model_validate_json(members["review-01.json"]), "q013_intake")
    work, decl, briefs = intake.pending_work, intake.declarations, intake.briefs
    assert work is not None and decl is not None and briefs is not None
    (batch,) = work.batches
    require(
        batch.unit_ids == ("Q013",)
        and batch.batch_id == manifest.batch_id
        and work.fingerprint == manifest.work_sha256,
        "q013_work_scope",
    )
    snapshot_doc = next(d for d in work.context.documents if d.kind == "scope")
    snapshot = object_value(strict_object(snapshot_doc.content_json)["snapshot"])
    require(
        review.role == "original_review"
        and draft.role == "reviewed_draft"
        and object_value(snapshot["critique"])["version_id"] == review.version_id
        and snapshot["draft_version_id"] == draft.version_id,
        "q013_review_draft_pair",
    )
    local_request = archive.read("source-fixture/request.json")
    require(storage._sha(local_request) == manifest.request_sha256, "q013_local_request")
    require(
        local_request
        == encoded(
            {
                "contract": "captured-local-assessment-input-1",
                "notice": manifest.notice,
                "provider_request": False,
                "model_input": False,
                "live_calls": 0,
                "work": work.model_dump(mode="json"),
                "declarations": decl.model_dump(mode="json"),
                "briefs": briefs.model_dump(mode="json"),
                "batch": batch.model_dump(mode="json"),
                "response_schema": assessment_response_schema(
                    work, scope_for_batch(work, batch.batch_id, manifest.request_sha256)
                ),
            }
        ),
        "q013_source_request_replay",
    )
    pin = saved.SavedReviewPin(
        registration=REGISTRATION.name,
        archive_seal_sha256=REGISTRATION.seal_sha256,
        database_capture_sha256=storage._sha(image),
        invocation_id=source.review_id,
        review=review,
        draft=draft,
        intake_sha256=storage._sha(members["review-01.json"]),
        intake_manifest_sha256=storage._sha(members["manifest.json"]),
        collection_sha256=manifest.collection_sha256,
        work_sha256=work.fingerprint,
        declarations_sha256=canonical_sha256(decl.model_dump(mode="json")),
        briefs_sha256=canonical_sha256(briefs.model_dump(mode="json")),
        request_sha256=manifest.request_sha256,
        fixture_manifest_sha256=storage._sha(manifest_raw),
    )
    receipt = {
        "contract": "saved-review-source-receipt-1",
        "source": pin.model_dump(mode="json"),
        "selected": selected.model_dump(mode="json"),
        "source_data_origin": manifest.origin,
        "raw_critic_response_available": True,
        "request_kind": "offline_fixture",
        "model_evidence": False,
        "production_attachment_eligible": False,
        "writer_dispatch_authorized": False,
        "live_calls": 0,
        **saved._capture_receipt(archive, snapshot, pin),
    }
    return saved._Prepared(
        intake,
        manifest,
        pin,
        selected,
        {
            "source-receipt.json": encoded(receipt),
            "request.json": local_request,
            "intake.json": members["review-01.json"],
            "fixture-manifest.json": manifest_raw,
        },
    )


def prepare(selection: ArtifactSelection) -> wire._Plan:
    """Resolve the selected version and prepare the two exact endpoint bodies offline."""
    archive = _open()
    source = _source(archive, selection)
    work = source.intake.pending_work
    assert work is not None
    scope = scope_for_batch(work, source.manifest.batch_id, source.pin.request_sha256)
    spec = builtin_model_specs()["gpt-6.1-sol"]
    versions = (UUID(source.pin.review.version_id), UUID(source.pin.draft.version_id))
    request = ModelRequest(
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        model_identifier=spec.model_identifier,
        invocation=InvocationContext(
            "read_only_saved_review_assessment", "saved-review-openai-packet-1", versions
        ),
        messages=(
            ModelMessage(MessageRole.SYSTEM, SYSTEM),
            ModelMessage(MessageRole.USER, compact(wire._packet(source, work, scope))),
        ),
        settings=ModelSettings(thinking="high"),
        budget=ModelCallBudget(96_000, 32_000, Decimal("0.60")),
        response_schema=assessment_response_schema(work, scope),
    )
    mapping = _prepare_wire(work, scope, request, spec, guard=active_secret_guard())
    receipt = source.files["source-receipt.json"]
    files = {"source-receipt.json": receipt}
    for end in mapping.endpoints:
        files[end.stage + "-request.json"] = end.body_utf8.encode()
    files["request-manifest.json"] = encoded(
        {
            "contract": "saved-review-openai-request-1",
            "wire": mapping.model_dump(
                mode="json", exclude={"endpoints": {"__all__": {"body_utf8"}}}
            ),
            "input_artifact_version_ids": [str(v) for v in versions],
            "source_receipt_bytes_sha256": storage._sha(receipt),
            "selected": source.selected.model_dump(mode="json"),
            "count_limit": 1,
            "generation_limit": 1,
            "retry_limit": 0,
            "live_calls": 0,
        }
    )
    return wire._Plan(work, mapping, files, archive, source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", type=Path, required=True)
    args = parser.parse_args()
    plan = prepare(ArtifactSelection.model_validate_json(storage._read(args.selection, 8192)))
    print(json.dumps({"request_manifest_sha256": plan.digest, "live_calls": 0}))
