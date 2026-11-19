"""Supported saved-review intake → fixture-authenticated native completion, offline only."""

from __future__ import annotations

import json
import socket
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.persistence.models import AgentInvocation, ArtifactVersion
from open_hollywood_api.services import assessment_completion as publisher
from open_hollywood_api.services import assessment_intake as intake_service
from open_hollywood_engine.evaluations.assessment_completion import encoded, expected_pin
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceRegistry,
    bind_assessment_result,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import strict_object
from sqlalchemy import update

from tests import production_assessment_fixtures as fixture_bridge
from tests.api.test_assessment_intake import offline as offline
from tests.api.test_production_fulfillment import Prepared
from tests.api.test_production_fulfillment import prepared as prepared
from tests.production_assessment_fixtures import (
    FixtureRegistration,
    audit,
    capture,
    files,
    register,
    response_for,
    sha,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def source(
    prepared: Prepared,
    migrated_database_path: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> FixtureRegistration:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("No socket connections in production-source qualification")

    # The Windows event loop has already created its own local socket pair.
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)
    monkeypatch.setattr(socket, "create_connection", deny)
    with prepared.sessions() as session:
        review_id = str(prepared.source(session).id)
    return register(migrated_database_path, review_id, tmp_path / "source-fixture")


def database_bytes(path: Path) -> dict[str, str]:
    return {str(p): sha(p.read_bytes()) for p in (path, Path(str(path) + "-wal")) if p.exists()}


async def test_supported_intake_and_fixture_bound_completion_remain_separate_from_authority(
    source: FixtureRegistration,
    tmp_path: Path,
) -> None:
    before_db = database_bytes(source.database)
    before_intake = files(source.intake_folder)
    result = source.intake
    work = result.pending_work
    assert work is not None and len(work.batches) == 1 and len(work.context.statements) == 1
    assert result.source.origin == "saved_review"
    assert result.source.report_origin == "saved_normalized_and_audit"
    assert work.context.canonical_review_id is None
    assert work.context.documents == result.source.inventory_work.context.documents
    assert work.context.messages == result.source.inventory_work.context.messages
    assert work.context.report_fields == result.source.inventory_work.context.report_fields
    assert sum(f.status == "not_selected" for f in result.findings) > 0
    assert result.assessment_result is result.completion_receipt is None
    registry = EvidenceRegistry.model_validate_json(
        next(d.content_json for d in work.context.documents if d.kind == "registry")
    )
    assert all(
        e.document_id != "operator-provenance-not-visible-authority" for e in registry.entries
    )
    draft = next(
        d for d in work.context.documents if d.identity == "catalog-complete-current-draft"
    )
    assert draft.version == source.selections[1].version_id

    absent = audit(source, source.selections[0], None)
    assert absent.state == "missing_delivery" and absent.result is None
    assert not absent.completion.complete_delivery and absent.completion.completed_batches == 0
    interrupted = capture(source, tmp_path / "intent-only", "", terminal=False)
    missing = audit(source, source.selections[0], interrupted)
    assert missing.state == "missing_terminal" and missing.possibly_sent_without_terminal == 1
    assert not missing.completion.complete_delivery and missing.result is None

    delivered = capture(source, tmp_path / "delivery", response_for(source))
    frozen_journal = files(delivered.journal)
    verified = audit(source, source.selections[0], delivered)
    assert verified == audit(source, source.selections[1], delivered)
    assert verified == audit(source, source.selections[0], delivered)
    assert verified.state == "bound_fixture" and verified.completion.binding == "complete"
    assert verified.result is not None
    assert verified.completion.unknown_usage_attempts == 1
    assert not verified.model_evidence and not verified.production_attachment_eligible
    assert not verified.result.writer_dispatch_authorized
    assert verified.result.support == verified.result.evidence_adequacy == "unassessed"
    assert verified.result.edit_necessity == verified.result.craft == "unassessed"
    assert not verified.completion.whole_relation_credit
    assert before_db == database_bytes(source.database)
    assert before_intake == files(source.intake_folder)
    assert frozen_journal == files(delivered.journal)
    (tmp_path / "qualification.json").write_bytes(
        encoded(
            {
                "origin": "authored_source_and_delivery_rehearsal",
                "source_contract": "v61/graph-9/schema-7",
                "exact_selections": [s.model_dump(mode="json") for s in source.selections],
                "complete_intake": result.model_dump(mode="json"),
                "bound_result": verified.result.model_dump(mode="json"),
                "completion": verified.completion.model_dump(mode="json"),
                "missing_delivery": absent.state,
                "intent_only": missing.state,
                "database_bytes_unchanged": True,
                "intake_and_journal_unchanged": True,
                "production_attachment_eligible": False,
                "model_evidence": False,
                "live_calls": 0,
            }
        )
    )


async def test_runtime_source_and_publication_contracts_still_refuse_saved_origin(
    source: FixtureRegistration,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="source_origin_not_qualified"):
        expected_pin(source.intake, source.manifest, encoded(source.intake.model_dump(mode="json")))
    destination = tmp_path / "should-not-publish"
    with pytest.raises(ValueError):
        publisher.prepare_inputs(source.intake_folder / "review-01.json", destination)
    assert not destination.exists()


@pytest.mark.parametrize(
    "field", ["project_id", "artifact_id", "version_id", "content_sha256", "role"]
)
async def test_wrong_selected_identity_never_gets_completion(
    source: FixtureRegistration,
    tmp_path: Path,
    field: str,
) -> None:
    delivered = capture(source, tmp_path / "delivery", response_for(source))
    for selection in source.selections:
        changed = selection.model_copy(
            update={
                field: "f" * 64
                if field == "content_sha256"
                else (
                    "reviewed_draft" if selection.role == "original_review" else "original_review"
                )
                if field == "role"
                else str(uuid4())
            }
        )
        with pytest.raises(ValueError, match="fixture_wrong_selection"):
            audit(source, changed, delivered)


async def test_captured_request_for_a_different_draft_is_refused(
    source: FixtureRegistration,
    tmp_path: Path,
) -> None:
    wrong = source.request.replace(source.selections[1].version_id.encode(), str(uuid4()).encode())
    assert wrong != source.request
    delivered = capture(source, tmp_path / "wrong-version", response_for(source), request=wrong)
    with pytest.raises(ValueError, match="fixture_wrong_request_or_origin"):
        audit(source, source.selections[0], delivered)


@pytest.mark.parametrize(
    "fault",
    [
        "missing_slot",
        "unknown_citation",
        "empty",
        "duplicate",
        "length",
        "refusal",
        "transport_error",
    ],
)
async def test_failed_delivery_does_not_become_a_completed_subset(
    source: FixtureRegistration,
    tmp_path: Path,
    fault: str,
) -> None:
    raw = response_for(source)
    status = "valid"
    if fault == "missing_slot":
        raw = '{"assessments":{}}'
    elif fault == "unknown_citation":
        value = json.loads(raw)
        next(iter(value["assessments"].values()))["evidence"] = ["OTHER-DRAFT:E0001"]
        raw = json.dumps(value)
    elif fault == "empty":
        raw = ""
    elif fault == "duplicate":
        raw = raw[:-1] + ',"assessments":{}}'
    else:
        status = fault
    delivered = capture(source, tmp_path / "failed", raw, status=status)
    result = audit(source, source.selections[0], delivered)
    assert result.state == "failed_delivery" and result.result is None
    assert not result.completion.complete_delivery and result.completion.binding == "unresolved"
    assert result.completion.unknown_usage_attempts == 1
    assert not result.production_attachment_eligible


@pytest.mark.parametrize(
    "member",
    ["request.json", "source-manifest.json", "intake/review-01.json", "terminal.json", "stop.json"],
)
async def test_changed_evidence_is_not_authenticated_by_its_own_claims(
    source: FixtureRegistration,
    tmp_path: Path,
    member: str,
) -> None:
    delivered = capture(source, tmp_path / "delivery", response_for(source))
    parent = (
        delivered.journal
        if member in {"terminal.json", "stop.json"}
        else source.intake_folder.parent
    )
    target = parent / member
    target.write_bytes(target.read_bytes() + b" ")
    with pytest.raises(ValueError, match="fixture_(request|intake|journal)_changed"):
        audit(source, source.selections[0], delivered)


@pytest.mark.parametrize("fault", ["wrong_target", "changed_prompt", "legacy_v33", "missing_audit"])
async def test_incompatible_source_is_not_admitted(
    source: FixtureRegistration,
    prepared: Prepared,
    fault: str,
) -> None:
    with prepared.sessions() as session:
        invocation = session.get(AgentInvocation, UUID(source.review_id))
        assert invocation is not None
        if fault == "changed_prompt":
            assert invocation.prompt_text is not None
            invocation.prompt_text += " changed"
        elif fault == "wrong_target":
            version = session.get(ArtifactVersion, UUID(source.selections[0].version_id))
            assert version is not None
            content = {**version.content, "target_artifact_version_id": str(uuid4())}
            # Deliberately corrupt the disposable fixture below the ORM's immutable-row guard.
            session.execute(
                update(ArtifactVersion)
                .where(ArtifactVersion.id == version.id)
                .values(
                    content=content,
                    content_sha256=canonical_sha256(content),
                )
            )
        else:
            settings = dict(invocation.request_settings)
            if fault == "legacy_v33":
                settings["prompt_template_version"] = "33"
            else:
                settings.pop("scene_boundary_audit")
            invocation.request_settings = settings
        session.commit()
    entry = intake_service.collect_intakes(
        "saved_review", source.database, (source.review_id,)
    ).entries[0]
    assert entry.source is None
    if fault in {"legacy_v33", "missing_audit"}:
        assert entry.reason == "unsupported_contract"
    with pytest.raises(ValueError, match="fixture_source_changed"):
        audit(source, source.selections[0], None)


async def test_copy_of_source_file_does_not_inherit_registration(
    source: FixtureRegistration,
    tmp_path: Path,
) -> None:
    copied = tmp_path / "copied.db"
    copied.write_bytes(source.database.read_bytes())
    with pytest.raises(ValueError, match="fixture_database_replaced"):
        audit(replace(source, database=copied), source.selections[0], None)


async def test_newer_identical_draft_does_not_replace_the_original_review_target(
    source: FixtureRegistration,
    prepared: Prepared,
    tmp_path: Path,
) -> None:
    delivered = capture(source, tmp_path / "delivery", response_for(source))
    old = source.selections[1]
    newer_id = uuid4()
    with prepared.sessions() as session:
        original = session.get(ArtifactVersion, UUID(old.version_id))
        assert original is not None
        session.add(
            ArtifactVersion(
                id=newer_id,
                artifact_id=original.artifact_id,
                parent_version_id=original.id,
                version_number=original.version_number + 1,
                schema_version=original.schema_version,
                content=original.content,
                content_sha256=original.content_sha256,
                change_summary="Authored identical-content newer version; not reviewed",
            )
        )
        session.commit()
    # A valid appended head does not change the selected source closure.
    assert audit(source, old, delivered).state == "bound_fixture"
    assert audit(source, source.selections[0], delivered).state == "bound_fixture"
    with pytest.raises(ValueError, match="fixture_wrong_selection"):
        audit(source, old.model_copy(update={"version_id": str(newer_id)}), delivered)


async def test_explicit_authored_origin_cannot_be_relabelled_as_observed(
    source: FixtureRegistration,
    tmp_path: Path,
) -> None:
    delivered = capture(source, tmp_path / "delivery", response_for(source))
    intent = delivered.journal / "intent.json"
    data = strict_object(intent.read_text("utf-8"))
    data["origin"] = "observed_model_delivery"
    intent.write_bytes(encoded(data))
    with pytest.raises(ValueError, match="fixture_journal_changed"):
        audit(source, source.selections[0], delivered)


async def test_drift_during_binding_cannot_return_a_verified_completion(
    source: FixtureRegistration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    delivered = capture(source, tmp_path / "delivery", response_for(source))
    original = bind_assessment_result

    def changing(*args: Any, **kwargs: Any) -> Any:
        result = original(*args, **kwargs)
        (source.intake_folder.parent / "request.json").write_bytes(source.request + b" ")
        return result

    monkeypatch.setattr(fixture_bridge, "bind_assessment_result", changing)
    with pytest.raises(ValueError, match="fixture_request_changed"):
        audit(source, source.selections[0], delivered)
