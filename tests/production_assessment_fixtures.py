"""Test-only saved-review bridge. Authored source/delivery, never provider authentication.

The runtime completion SourcePin intentionally rejects saved_review. This rehearsal
keeps that restriction intact and exercises the reusable native binding below it.
Trust pins are owned by fixture setup, not read from a submitted success label.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import open_hollywood_api.services.assessment_completion as storage
from open_hollywood_api.services import assessment_intake as intake_service
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.review_evidence_export import readonly_connection
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    BoundAssessmentResult,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    Completion,
    complete_work,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    object_value,
    require,
    strict_object,
    string_value,
    text_hash,
)

from tests.assessment_completion_fixtures import AUTHORED_NOTICE, local_input
from tests.assessment_intake_fixtures import choice_for, plan_for


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def files(folder: Path) -> dict[str, str]:
    return {p.name: sha(storage._read(p)) for p in folder.iterdir()}


def selection_for(database: Path, version: str, role: str) -> ArtifactSelection:
    with readonly_connection(database) as connection:
        row = connection.execute(
            "SELECT v.artifact_id, a.project_id, v.content_sha256 FROM artifact_versions v "
            "JOIN artifacts a ON a.id=v.artifact_id WHERE v.id=?",
            (UUID(version).hex,),
        ).fetchone()
        require(row is not None, "fixture_selected_version_missing")
        assert row is not None
        return ArtifactSelection.model_validate(
            {
                "role": role,
                "project_id": str(UUID(row["project_id"])),
                "artifact_id": str(UUID(row["artifact_id"])),
                "version_id": version,
                "content_sha256": row["content_sha256"],
            }
        )


@dataclass(frozen=True)
class FixtureRegistration:
    database: Path
    database_file_identity: tuple[int, int]
    review_id: str
    collection_sha256: str
    intake: IntakeResult
    intake_folder: Path
    intake_files: dict[str, str]
    selections: tuple[ArtifactSelection, ArtifactSelection]
    request: bytes
    manifest: bytes


def register(database: Path, review_id: str, destination: Path) -> FixtureRegistration:
    database = storage._unlinked(database)
    collection = intake_service.collect_intakes("saved_review", database, (review_id,))
    source = collection.entries[0].source
    require(source is not None, "fixture_requires_supported_saved_review")
    assert source is not None
    fields = source.inventory_work.context.report_fields
    field = next(
        f for f in fields if f.pointer.endswith("/assignment_checks/turning_point/assessment")
    )
    plan = plan_for(source, choice_for(source, field.field_id))
    result = compile_intake(source, plan)
    intake_folder = destination / "intake"
    intake_service.write_intake(
        intake_folder, collection, intake_service.IntakeBatchPlan(plans={review_id: plan})
    )
    provenance = strict_object(
        next(d.content_json for d in source.inventory_work.context.documents if d.kind == "scope")
    )
    snapshot = object_value(provenance["snapshot"])
    review = selection_for(
        database, string_value(object_value(snapshot["critique"])["version_id"]), "original_review"
    )
    draft = selection_for(database, string_value(snapshot["draft_version_id"]), "reviewed_draft")
    body, scope = local_input(result)
    request = body.encode("utf-8")
    collection_hash = canonical_sha256(collection.model_dump(mode="json"))
    manifest = encoded(
        {
            "contract": "production-assessment-source-fixture-1",
            "origin": "authored_source_and_delivery_rehearsal",
            "notice": AUTHORED_NOTICE,
            "source_origin": source.origin,
            "report_origin": source.report_origin,
            "review_invocation_id": review_id,
            "selection": [review.model_dump(mode="json"), draft.model_dump(mode="json")],
            "collection_sha256": collection_hash,
            "intake_files": files(intake_folder),
            "request_sha256": scope.request_sha256,
            "work_sha256": scope.work_sha256,
            "batch_id": scope.batch_id,
            "attempt_id": "authored-saved-review-assessment-1",
            "provider_request": False,
            "model_evidence": False,
            "live_calls": 0,
        }
    )
    destination.mkdir(exist_ok=True)
    (destination / "request.json").write_bytes(request)
    (destination / "source-manifest.json").write_bytes(manifest)
    stat = database.stat()
    return FixtureRegistration(
        database,
        (stat.st_dev, stat.st_ino),
        review_id,
        collection_hash,
        result,
        intake_folder,
        files(intake_folder),
        (review, draft),
        request,
        manifest,
    )


def revalidate(source: FixtureRegistration, selection: ArtifactSelection) -> None:
    selection = ArtifactSelection.model_validate_json(selection.model_dump_json())
    require(selection in source.selections, "fixture_wrong_selection")
    database = storage._unlinked(source.database)
    stat = database.stat()
    require(
        (stat.st_dev, stat.st_ino) == source.database_file_identity, "fixture_database_replaced"
    )
    collection = intake_service.collect_intakes("saved_review", database, (source.review_id,))
    require(
        canonical_sha256(collection.model_dump(mode="json")) == source.collection_sha256,
        "fixture_source_changed",
    )
    require(files(source.intake_folder) == source.intake_files, "fixture_intake_changed")
    for expected in source.selections:
        require(
            selection_for(database, expected.version_id, expected.role) == expected,
            "fixture_source_selection_changed",
        )
    require(
        storage._read(source.intake_folder.parent / "request.json") == source.request
        and storage._read(source.intake_folder.parent / "source-manifest.json") == source.manifest,
        "fixture_request_changed",
    )
    require(
        source.intake == compile_intake(source.intake.source, source.intake.plan),
        "fixture_intake_mismatch",
    )


def response_for(source: FixtureRegistration) -> str:
    declarations = source.intake.declarations
    assert declarations is not None
    return json.dumps(
        {
            "assessments": {
                d.statement.unit_id: {
                    "support": "supported",
                    "evidence": list(
                        dict.fromkeys(r for s in d.source_scopes for r in s.evidence_refs)
                    ),
                    "reason": AUTHORED_NOTICE,
                }
                for d in declarations.declarations
            }
        }
    )


@dataclass(frozen=True)
class CapturedFixture:
    journal: Path
    member_hashes: dict[str, str]


def capture(
    source: FixtureRegistration,
    destination: Path,
    raw: str,
    *,
    status: str = "valid",
    terminal: bool = True,
    request: bytes | None = None,
) -> CapturedFixture:
    """Own the local fixture records. No network or caller-authored native receipt."""
    revalidate(source, source.selections[0])
    destination.mkdir(exist_ok=False)
    manifest = strict_object(source.manifest.decode())
    intent = encoded(
        {
            "origin": "authored_terminal_fixture",
            "manifest_sha256": sha(source.manifest),
            "request_sha256": sha(source.request if request is None else request),
            "attempt_id": manifest["attempt_id"],
        }
    )
    storage._write_new(destination / "intent.json", intent)
    if terminal:
        outcome = encoded(
            {
                "origin": "authored_terminal_fixture",
                "intent_sha256": sha(intent),
                "status": status,
                "raw_final": raw,
                "raw_sha256": text_hash(raw),
                "usage": {"input_tokens": None, "output_tokens": None, "reasoning_tokens": None},
                "elapsed_seconds": None,
            }
        )
        storage._write_new(destination / "terminal.json", outcome)
        storage._write_new(destination / "stop.json", encoded({"terminal_sha256": sha(outcome)}))
    return CapturedFixture(destination, files(destination))


@dataclass(frozen=True)
class FixtureAudit:
    state: str
    completion: Completion
    result: BoundAssessmentResult | None
    possibly_sent_without_terminal: int = 0
    model_evidence: bool = False
    production_attachment_eligible: bool = False
    live_calls: int = 0


def audit(
    source: FixtureRegistration,
    selection: ArtifactSelection,
    delivery: CapturedFixture | None,
) -> FixtureAudit:
    revalidate(source, selection)
    work = source.intake.pending_work
    assert work is not None
    scope = scope_for_batch(work, work.batches[0].batch_id, sha(source.request))
    expected = {scope.batch_id: scope.request_sha256}
    if delivery is None:
        return FixtureAudit("missing_delivery", complete_work(work, (), expected), None)
    require(files(delivery.journal) == delivery.member_hashes, "fixture_journal_changed")
    intent_bytes = storage._read(delivery.journal / "intent.json")
    intent = strict_object(intent_bytes.decode())
    require(
        intent
        == {
            "origin": "authored_terminal_fixture",
            "manifest_sha256": sha(source.manifest),
            "request_sha256": scope.request_sha256,
            "attempt_id": "authored-saved-review-assessment-1",
        },
        "fixture_wrong_request_or_origin",
    )
    if "terminal.json" not in delivery.member_hashes:
        return FixtureAudit("missing_terminal", complete_work(work, (), expected), None, 1)
    raw_terminal = storage._read(delivery.journal / "terminal.json")
    terminal = strict_object(raw_terminal.decode())
    require(terminal["origin"] == "authored_terminal_fixture", "fixture_wrong_origin")
    require(terminal["intent_sha256"] == sha(intent_bytes), "fixture_terminal_intent")
    require(
        strict_object(storage._read(delivery.journal / "stop.json").decode())
        == {"terminal_sha256": sha(raw_terminal)},
        "fixture_terminal_stop",
    )
    raw = string_value(terminal["raw_final"])
    require(terminal["raw_sha256"] == text_hash(raw), "fixture_terminal_bytes")
    require(
        terminal["status"] in ("valid", "length", "refusal", "transport_error"), "fixture_status"
    )
    status = terminal["status"]
    receipt = AssessmentReceipt.model_validate(
        {
            "work_sha256": work.fingerprint,
            "batch_id": scope.batch_id,
            "request_sha256": scope.request_sha256,
            "attempt_id": string_value(intent["attempt_id"]),
            "status": status,
            "result_sha256": text_hash(raw) if status == "valid" else None,
            "assessed_unit_ids": scope.active_unit_ids if status == "valid" else (),
            "input_tokens": None,
            "output_tokens": None,
            "reasoning_tokens": None,
            # Native schema needs a number; this is synthetic, not measured latency.
            "active_seconds": 0,
        }
    )
    result = None
    if status == "valid":
        try:
            result = bind_assessment_result(work, scope, receipt, raw)
            receipt = result.receipt
        except ValueError:
            receipt = receipt.model_copy(
                update={
                    "status": "invalid",
                    "result_sha256": None,
                    "assessed_unit_ids": (),
                }
            )
    completion = complete_work(work, (receipt,), expected)
    revalidate(source, selection)
    require(files(delivery.journal) == delivery.member_hashes, "fixture_journal_changed")
    return FixtureAudit("bound_fixture" if result else "failed_delivery", completion, result)
