"""Read-only adapter for a registered saved v61 review and its authored assessment journal."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
from uuid import UUID

from open_hollywood_engine.evaluations.assessment_completion import encoded, render_completion
from open_hollywood_engine.evaluations.assessment_intake import IntakeResult, compile_intake
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentReceipt, complete_work
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    Digest,
    Identifier,
    JsonObject,
    Record,
    object_value,
    require,
    strict_object,
    string_value,
    text_hash,
)
from pydantic import Field

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services.assessment_intake import IntakeBatchPlan, collect_intakes
from open_hollywood_api.services.production_association_records import ArtifactSelection
from open_hollywood_api.services.review_evidence_export import readonly_connection

Mode = Literal["prepare", "audit", "publish"]
Journal = Literal["complete", "intent-only", "absent"]
Origin = Literal["authored_terminal_fixture"]


@dataclass(frozen=True)
class _Registration:
    name: str
    archive: Path
    member_root: str
    seal_sha256: str
    database_limit: int = storage.MAX_FILE_BYTES


REGISTERED = _Registration(
    "saved-v61-authored-2026-11-19",
    Path(__file__).resolve().parents[4]
    / "data/diagnostics/assessment-production-intake-qualification-2026-11-19",
    "pytest-verified/test_supported_intake_and_fixt0",
    "8ea766f1bccb5b02d5c794ba68d4a3c693dcc0302bb8f4d7c715a12a357fc7a8",
)
CAPTURED_Q008 = _Registration(
    "saved-v61-q008-2026-11-20",
    Path(__file__).resolve().parents[4]
    / "data/diagnostics/q008-downstream-2026-11-20/registration",
    "source",
    "ea59f333b71458477f3a6bf5e33a1f2906595caa721835ed4e59872cc683ae6d",
    database_limit=24_571_904,
)


class SavedReviewPin(Record):
    contract: Literal["saved-review-completion-source-1"] = "saved-review-completion-source-1"
    registration: str
    archive_seal_sha256: Digest
    database_capture_sha256: Digest
    source_origin: Literal["saved_review"] = "saved_review"
    report_origin: Literal["saved_normalized_and_audit"] = "saved_normalized_and_audit"
    invocation_id: Identifier
    review: ArtifactSelection
    draft: ArtifactSelection
    intake_sha256: Digest
    intake_manifest_sha256: Digest
    collection_sha256: Digest
    work_sha256: Digest
    declarations_sha256: Digest
    briefs_sha256: Digest
    request_sha256: Digest
    fixture_manifest_sha256: Digest


class _SourceManifest(Record):
    attempt_id: str = Field(min_length=1, max_length=200)
    batch_id: str
    collection_sha256: Digest
    intake_files: dict[str, Digest]
    notice: str
    source_origin: Literal["saved_review"]
    report_origin: Literal["saved_normalized_and_audit"]
    review_invocation_id: Identifier
    selection: tuple[ArtifactSelection, ArtifactSelection]
    work_sha256: Digest
    request_sha256: Digest
    live_calls: Literal[0]
    model_evidence: Literal[False]
    provider_request: Literal[False]


class _FixtureManifest(_SourceManifest):
    contract: Literal["production-assessment-source-fixture-1"]
    origin: Literal["authored_source_and_delivery_rehearsal"]


class _CaptureManifest(_SourceManifest):
    contract: Literal["captured-ordinary-assessment-source-1"]
    origin: Literal["isolated_provider_capture"]


class _Terminal(Record):
    origin: Origin
    intent_sha256: Digest
    status: Literal["valid", "length", "refusal", "transport_error", "invalid", "cancelled"]
    raw_final: str = Field(max_length=64_000)
    raw_sha256: Digest
    usage: dict[str, None]
    elapsed_seconds: None


@dataclass(frozen=True)
class _Archive:
    registration: _Registration
    hashes: dict[str, str]

    @property
    def root(self) -> Path:
        return self.registration.archive / self.registration.member_root

    def read(self, name: str, *, database: bool = False) -> bytes:
        path = storage._unlinked(self.root / name)
        digest = self.hashes.get(self.registration.member_root + "/" + name)
        require(digest is not None, "saved_review_unregistered_member")
        if database:
            with path.open("rb") as stream:
                data = stream.read(self.registration.database_limit + 1)
            require(len(data) <= self.registration.database_limit, "saved_review_database_bound")
        else:
            data = storage._read(path)
        require(storage._sha(data) == digest, "saved_review_changed_member")
        return data

    def inventory(self, folder: str, names: set[str]) -> None:
        path = storage._unlinked(self.root / folder)
        require({p.name for p in path.iterdir()} == names, "saved_review_member_inventory")


def _open(name: str, *, allow_capture: bool = False) -> _Archive:
    reg = CAPTURED_Q008 if allow_capture and name == CAPTURED_Q008.name else REGISTERED
    require(name == reg.name, "unknown_saved_review_registration")
    seal = storage._read(reg.archive / "acceptance-seal.json")
    require(storage._sha(seal) == reg.seal_sha256, "saved_review_seal_changed")
    members = strict_object(seal.decode())["members_sha256"]
    require(isinstance(members, dict), "saved_review_seal_members")
    assert isinstance(members, dict)
    return _Archive(reg, {k: v for k, v in members.items() if isinstance(v, str)})


@dataclass(frozen=True)
class _Prepared:
    intake: IntakeResult
    manifest: _FixtureManifest | _CaptureManifest
    pin: SavedReviewPin
    selected: ArtifactSelection
    files: dict[str, bytes]


def _verify_selection(connection: sqlite3.Connection, selected: ArtifactSelection) -> None:
    row = connection.execute(
        "SELECT a.project_id, a.id, v.content_sha256, a.artifact_type FROM artifact_versions v "
        "JOIN artifacts a ON a.id=v.artifact_id WHERE v.id=?",
        (UUID(selected.version_id).hex,),
    ).fetchone()
    kind = "critique" if selected.role == "original_review" else "scene_draft"
    require(
        row is not None
        and tuple(row)
        == (
            UUID(selected.project_id).hex,
            UUID(selected.artifact_id).hex,
            selected.content_sha256,
            kind,
        ),
        "saved_review_selection_rows",
    )


def _intake_members(archive: _Archive, manifest: _SourceManifest) -> dict[str, bytes]:
    folder = "source-fixture/intake"
    names = {
        "index.json",
        "index.md",
        "review-01.json",
        "review-01.md",
        "plan.json",
        "manifest.json",
    }
    archive.inventory(folder, names)
    members = {n: archive.read(f"{folder}/{n}") for n in names}
    require(
        {n: storage._sha(b) for n, b in members.items()} == manifest.intake_files,
        "saved_review_intake_files",
    )
    intake_manifest = strict_object(members["manifest.json"].decode())
    require(
        intake_manifest.get("contract") == "ordinary-review-intake-manifest-1"
        and intake_manifest.get("origin") == manifest.source_origin
        and intake_manifest.get("review_ids") == [manifest.review_invocation_id]
        and intake_manifest.get("files_sha256")
        == {name: manifest.intake_files[name] for name in names - {"manifest.json"}},
        "saved_review_intake_manifest",
    )
    return members


def _capture_receipt(archive: _Archive, snapshot: JsonObject, pin: SavedReviewPin) -> JsonObject:
    archive.inventory("capture", {"http.json", "terminal.json"})
    raw_terminal = archive.read("capture/terminal.json")
    terminal = strict_object(raw_terminal.decode())
    http = archive.read("capture/http.json")
    receipt = strict_object(http.decode())
    reply = object_value(receipt["response"])
    message = object_value(reply["message"])
    creator = object_value(snapshot["invocation"])
    require(
        terminal.get("origin") == "isolated_provider_capture"
        and terminal.get("status") == "captured"
        and terminal.get("dispatch_state") == "dispatched"
        and terminal.get("database_sha256") == pin.database_capture_sha256
        and terminal.get("critique_version") == pin.review.version_id
        and terminal.get("invocation_id") == creator["invocation_id"] == pin.invocation_id
        and terminal.get("run_id") == creator["workflow_run_id"]
        and terminal.get("http_sha256") == storage._sha(http)
        and terminal.get("http_status") == receipt.get("http_status") == 200
        and reply.get("done") is True
        and reply.get("done_reason") == "stop"
        and text_hash(string_value(message["content"])) == creator["response_sha256"],
        "saved_review_capture_receipt_binding",
    )
    return {
        "critic_terminal_sha256": storage._sha(raw_terminal),
        "critic_http_receipt_sha256": storage._sha(http),
    }


def _prepare(archive: _Archive, selection: ArtifactSelection | None) -> _Prepared:
    archive.inventory("source-fixture", {"intake", "request.json", "source-manifest.json"})
    original_manifest = archive.read("source-fixture/source-manifest.json")
    captured = archive.registration == CAPTURED_Q008
    manifest_type = _CaptureManifest if captured else _FixtureManifest
    manifest = manifest_type.model_validate_json(encoded(strict_object(original_manifest.decode())))
    review, draft = manifest.selection
    selected = (
        review
        if selection is None
        else ArtifactSelection.model_validate_json(selection.model_dump_json())
    )
    require(selected in manifest.selection, "saved_review_wrong_selection")
    members = _intake_members(archive, manifest)
    intake_manifest = strict_object(members["manifest.json"].decode())
    archive.inventory("database", {"open_hollywood.db"})
    database_bytes = archive.read("database/open_hollywood.db", database=True)
    # Replay the sealed, closed image in isolation. SQLite may create coordination
    # sidecars beside the copy. No SQLite connection touches the registered source.
    with TemporaryDirectory() as tmp:
        database = Path(tmp) / "open_hollywood.db"
        database.write_bytes(database_bytes)
        collection = collect_intakes("saved_review", database, (manifest.review_invocation_id,))
        with readonly_connection(database) as connection:
            _verify_selection(connection, review)
            _verify_selection(connection, draft)
    source = collection.entries[0].source
    require(source is not None, "saved_review_incompatible")
    assert source is not None
    provenance = strict_object(
        next(d.content_json for d in source.inventory_work.context.documents if d.kind == "scope")
    )
    snapshot = provenance["snapshot"]
    require(isinstance(snapshot, dict), "saved_review_snapshot")
    assert isinstance(snapshot, dict)
    critique = snapshot["critique"]
    require(
        isinstance(critique, dict)
        and critique.get("version_id") == review.version_id
        and snapshot["draft_version_id"] == draft.version_id
        and review.role == "original_review"
        and draft.role == "reviewed_draft",
        "saved_review_pair",
    )
    # The historical locator is part of the collection digest, never an input path.
    canonical_collection = collection.model_dump(mode="json")
    canonical_collection["source_path"] = intake_manifest["source_path"]
    require(
        canonical_sha256(canonical_collection)
        == manifest.collection_sha256
        == intake_manifest["source_sha256"],
        "saved_review_collection_binding",
    )
    plans = IntakeBatchPlan.model_validate_json(members["plan.json"])
    require(
        set(plans.plans) == {source.review_id}
        and canonical_sha256(plans.model_dump(mode="json")) == intake_manifest["plan_sha256"],
        "saved_review_plan_binding",
    )
    intake = compile_intake(source, plans.plans[source.review_id])
    require(
        intake == IntakeResult.model_validate_json(members["review-01.json"]),
        "saved_review_intake_changed",
    )
    work, declarations, briefs = intake.pending_work, intake.declarations, intake.briefs
    require(
        work is not None and declarations is not None and briefs is not None,
        "saved_review_pending_work",
    )
    assert work is not None and declarations is not None and briefs is not None
    require(
        len(work.batches) == 1
        and work.batches[0].batch_id == manifest.batch_id
        and work.fingerprint == manifest.work_sha256,
        "saved_review_whole_work",
    )
    request = archive.read("source-fixture/request.json")
    schema = assessment_response_schema(work, scope_for_batch(work, manifest.batch_id, "0" * 64))
    require(
        storage._sha(request) == manifest.request_sha256
        and request
        == encoded(
            {
                "contract": "captured-local-assessment-input-1"
                if captured
                else "authored-local-assessment-input-1",
                "notice": manifest.notice,
                "provider_request": False,
                "model_input": False,
                "live_calls": 0,
                "work": work.model_dump(mode="json"),
                "declarations": declarations.model_dump(mode="json"),
                "briefs": briefs.model_dump(mode="json"),
                "batch": work.batches[0].model_dump(mode="json"),
                "response_schema": schema,
            }
        ),
        "saved_review_request_binding",
    )
    pin = SavedReviewPin(
        registration=archive.registration.name,
        archive_seal_sha256=archive.registration.seal_sha256,
        database_capture_sha256=storage._sha(database_bytes),
        invocation_id=source.review_id,
        review=review,
        draft=draft,
        intake_sha256=storage._sha(members["review-01.json"]),
        intake_manifest_sha256=storage._sha(members["manifest.json"]),
        collection_sha256=manifest.collection_sha256,
        work_sha256=work.fingerprint,
        declarations_sha256=canonical_sha256(declarations.model_dump(mode="json")),
        briefs_sha256=canonical_sha256(briefs.model_dump(mode="json")),
        request_sha256=manifest.request_sha256,
        fixture_manifest_sha256=storage._sha(original_manifest),
    )
    receipt = {
        "contract": "saved-review-source-receipt-1",
        "source": pin.model_dump(mode="json"),
        "selected": selected.model_dump(mode="json"),
        "source_data_origin": manifest.origin if captured else "authored_workspace_fixture",
        "raw_critic_response_available": captured,
        "request_kind": "offline_fixture",
        "model_evidence": False,
        "production_attachment_eligible": False,
        "writer_dispatch_authorized": False,
        "live_calls": 0,
    }
    if captured:
        require(work.batches[0].unit_ids == ("Q008",), "saved_review_capture_scope")
        receipt.update(_capture_receipt(archive, snapshot, pin))
    return _Prepared(
        intake,
        manifest,
        pin,
        selected,
        {
            "source-receipt.json": encoded(receipt),
            "intake.json": members["review-01.json"],
            "request.json": request,
            "fixture-manifest.json": original_manifest,
        },
    )


def _audit(
    archive: _Archive, prepared: _Prepared, journal: Journal
) -> tuple[dict[str, bytes], bool]:
    require(journal in ("absent", "intent-only", "complete"), "saved_review_unknown_journal")
    work = prepared.intake.pending_work
    assert work is not None
    manifest = prepared.manifest
    scope = scope_for_batch(work, manifest.batch_id, prepared.pin.request_sha256)
    evidence: dict[str, bytes] = {}
    receipt = None
    bound = None
    state = "missing_delivery"
    if journal != "absent":
        folder = "delivery" if journal == "complete" else "intent-only"
        names = (
            {"intent.json", "terminal.json", "stop.json"}
            if journal == "complete"
            else {"intent.json"}
        )
        archive.inventory(folder, names)
        evidence = {n: archive.read(f"{folder}/{n}") for n in sorted(names)}
        require(
            strict_object(evidence["intent.json"].decode())
            == {
                "origin": "authored_terminal_fixture",
                "attempt_id": manifest.attempt_id,
                "manifest_sha256": prepared.pin.fixture_manifest_sha256,
                "request_sha256": scope.request_sha256,
            },
            "saved_review_wrong_intent",
        )
        state = "missing_terminal"
    if journal == "complete":
        data = evidence["terminal.json"]
        terminal = _Terminal.model_validate_json(encoded(strict_object(data.decode())))
        require(
            terminal.intent_sha256 == storage._sha(evidence["intent.json"])
            and terminal.raw_sha256 == text_hash(terminal.raw_final)
            and set(terminal.usage) == {"input_tokens", "output_tokens", "reasoning_tokens"}
            and strict_object(evidence["stop.json"].decode())
            == {"terminal_sha256": storage._sha(data)},
            "saved_review_terminal_binding",
        )
        valid = terminal.status == "valid"
        receipt = AssessmentReceipt(
            work_sha256=work.fingerprint,
            batch_id=scope.batch_id,
            request_sha256=scope.request_sha256,
            attempt_id=manifest.attempt_id,
            status=terminal.status,
            result_sha256=terminal.raw_sha256 if valid else None,
            assessed_unit_ids=scope.active_unit_ids if valid else (),
            active_seconds=0,
        )
        state = terminal.status
        if valid:
            try:
                bound = bind_assessment_result(work, scope, receipt, terminal.raw_final)
            except ValueError:
                receipt = receipt.model_copy(
                    update={"status": "invalid", "assessed_unit_ids": (), "result_sha256": None}
                )
                state = "invalid"
            else:
                receipt = bound.receipt
                state = "bound_unassessed"
    completion = complete_work(
        work, (receipt,) if receipt else (), {scope.batch_id: scope.request_sha256}
    )
    eligible = (
        completion.complete_delivery and completion.binding == "complete" and bound is not None
    )
    evidence["audit.json"] = encoded(
        {
            "contract": "saved-review-terminal-audit-1",
            "source": prepared.pin.model_dump(mode="json"),
            "selection": prepared.selected.model_dump(mode="json"),
            "journal": journal,
            "state": state,
            "delivery_origin": "authored_terminal_fixture" if journal == "complete" else None,
            "usage_applicability": "not_applicable_no_inference",
            "possibly_sent_without_terminal": int(state == "missing_terminal"),
            "native_receipt": receipt.model_dump(mode="json") if receipt else None,
            "result": bound.model_dump(mode="json") if bound else None,
            "completion": completion.model_dump(mode="json"),
            "fixture_publication_eligible": eligible,
            "production_attachment_eligible": False,
            "model_evidence": False,
            "editorial_effect": "unassessed",
            "writer_dispatch_authorized": False,
            "live_calls": 0,
        }
    )
    return evidence, eligible


def export_saved_review(
    mode: Mode,
    registration: str,
    destination: Path,
    *,
    selection: ArtifactSelection | None = None,
    journal: Journal | None = None,
) -> Literal["created", "reused"]:
    """Prepare exact input, audit a registered fixture journal, or publish a bound completion."""
    require(
        mode in ("prepare", "audit", "publish") and (mode == "prepare") == (journal is None),
        "saved_review_export_mode",
    )

    def collect() -> dict[str, bytes]:
        archive = _open(registration)
        prepared = _prepare(archive, selection)
        files = prepared.files.copy()
        if journal is not None:
            evidence, eligible = _audit(archive, prepared, journal)
            files.update(evidence)
            if mode == "publish":
                require(eligible, "saved_review_incomplete_publication")
                envelope: JsonObject = {
                    "contract": "saved-review-completion-1",
                    "source_receipt": strict_object(files["source-receipt.json"].decode()),
                    "intake": prepared.intake.model_dump(mode="json"),
                    "audit": strict_object(files["audit.json"].decode()),
                    "origin": "authored_fixture",
                    "publication_state": "bound_unassessed",
                }
                files["envelope.json"] = encoded(envelope)
                files["view.md"] = render_completion(envelope).encode("utf-8")
        files["manifest.json"] = encoded(
            {
                "contract": "saved-review-export-1",
                "mode": mode,
                "origin": "authored_fixture",
                "files_sha256": {name: storage._sha(data) for name, data in files.items()},
                "adapter_sha256": storage._sha(Path(__file__).read_bytes()),
                "live_calls": 0,
                "writer_dispatch_authorized": False,
                "model_evidence": False,
                "production_attachment_eligible": False,
            }
        )
        return files

    files = collect()

    def recheck() -> None:
        require(collect() == files, "saved_review_export_drift")

    return storage._publish(destination, files, (REGISTERED.archive,), recheck)
