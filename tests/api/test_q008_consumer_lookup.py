"""Exercise fresh Q008 lookups against a closed portable publication."""

from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services import saved_review_openai_fixture as wire
from open_hollywood_engine.evaluations.assessment_completion import encoded

from scripts import lookup_q008_completion as consumer
from scripts import publish_q008_completion as publisher
from tests.api.test_q008_publisher import anyio_backend as anyio_backend
from tests.api.test_q008_publisher import archive as archive
from tests.api.test_q008_publisher import prepared as prepared
from tests.api.test_q008_publisher import registered as registered
from tests.api.test_q008_publisher import snapshot
from tests.api.test_q008_publisher import source as source

pytestmark = pytest.mark.usefixtures("anyio_backend")


@pytest.fixture
def published(registered: wire._Plan, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    score = json.loads(publisher.SCORE.read_bytes())
    score.update(
        passed_judgments=3,
        possible_judgments=3,
        whole_claim_label={"score": "pass"},
        plan_evidence={"score": "pass"},
        draft_ending_evidence={"score": "pass"},
    )
    publisher.SCORE.write_bytes(encoded(score))
    monkeypatch.setattr(publisher, "SCORE_SHA", storage._sha(publisher.SCORE.read_bytes()))
    directory = tmp_path / "publication"
    assert publisher.publish(registered.source.pin.review, directory) == "created"
    monkeypatch.setattr(consumer, "PUBLICATION", directory)
    monkeypatch.setattr(
        consumer, "MANIFEST_SHA", storage._sha((directory / "manifest.json").read_bytes())
    )
    return directory


def assert_unavailable(result: consumer.Inventory, reason: str) -> None:
    assert result.lookups
    assert all(
        row.status == "unavailable"
        and row.reason == reason
        and row.claim_id is None
        and row.delivery_id is None
        for row in result.lookups
    )
    assert not result.assessments and not result.accounting_records
    assert result.generation_totals is None


def test_exact_orders_and_repeated_opens_share_usage(
    registered: wire._Plan, published: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    review, draft = registered.source.pin.review, registered.source.pin.draft
    before = snapshot(published)
    selector_files = []
    for sel in (draft, review, draft):
        path = tmp_path / f"{sel.role}.json"
        path.write_bytes(encoded(sel.model_dump(mode="json")))
        selector_files.extend(["--selection", str(path)])
    assert consumer.main(selector_files) == 0
    combined = consumer.Inventory.model_validate_json(capsys.readouterr().out)
    (assessment,), (account,) = combined.assessments, combined.accounting_records
    assert [r.selection for r in combined.lookups] == [draft, review, draft]
    for seq in ((review,), (draft,), (review, draft), (draft, review)):
        result = consumer.lookup(seq)
        assert tuple(row.selection for row in result.lookups) == seq
        assert result.assessments == (assessment,) and result.accounting_records == (account,)
        assert result.generation_totals == combined.generation_totals == account.generation_usage
        assert all(
            r.status == "available"
            and (r.delivery_id, r.claim_id) == (assessment.delivery_id, assessment.claim_id)
            for r in (*result.lookups, *combined.lookups)
        )
    assert (account.delivery_id, account.request_selection) == (assessment.delivery_id, review)
    assert account.generation_usage.model_dump() == dict(
        input_tokens=100, output_tokens=20, cached_input_tokens=0, reasoning_tokens=5
    )
    assert account.preflight_input_count == 100 and account.actual_billed_cost is None
    assert account.request_manifest_sha256 == registered.digest
    assert assessment.claim_id == registered.wire.active_unit_ids[0]
    assert assessment.operator_score["scoring_origin"] == "test operator"
    assert assessment.application_status["semantic_support"] == "unassessed"
    assert assessment.application_status["production_attachment_eligible"] is False
    assert snapshot(published) == before


def test_same_text_successor_does_not_inherit_claim_or_usage(
    registered: wire._Plan, published: Path, archive: Path, tmp_path: Path
) -> None:
    review, draft = registered.source.pin.review, registered.source.pin.draft
    scratch = tmp_path / "lineage.db"
    shutil.copyfile(archive / "work/database/open_hollywood.db", scratch)
    child_id = uuid4()
    parent_id = UUID(draft.version_id).hex
    child = draft.model_copy(update={"version_id": str(child_id)})
    with closing(sqlite3.connect(scratch)) as db, db:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute(
            "INSERT INTO artifact_versions (id, artifact_id, parent_version_id, version_number, "
            "schema_version, content, content_sha256, change_summary, created_at) SELECT ?, "
            "artifact_id, id, version_number+1, schema_version, content, content_sha256, "
            "'same-text successor', created_at FROM artifact_versions WHERE id=?",
            (child_id.hex, parent_id),
        )
        saved._verify_selection(db, child)
    exact = consumer.lookup((review, draft))
    isolated = consumer.lookup((child,))
    assert_unavailable(isolated, "exact_selection_unavailable")
    for seq in ((child, review, draft), (draft, review, child)):
        result = consumer.lookup(seq)
        assert [r.selection for r in result.lookups] == list(seq)
        assert [r for r in result.lookups if r.status == "unavailable"] == list(isolated.lookups)
        assert result.assessments == exact.assessments and len(result.assessments) == 1
        assert (
            result.accounting_records == exact.accounting_records
            and len(result.accounting_records) == 1
        )
        assert result.generation_totals == exact.generation_totals


def test_known_version_with_mismatched_identity_is_unavailable(
    registered: wire._Plan, published: Path
) -> None:
    review, draft = registered.source.pin.review, registered.source.pin.draft
    selections = tuple(
        exact.model_copy(update={field: value})
        for exact, other in ((review, draft), (draft, review))
        for field, value in (
            ("project_id", str(uuid4())),
            ("artifact_id", other.artifact_id),
            ("role", other.role),
            ("content_sha256", other.content_sha256),
        )
    )
    result = consumer.lookup(selections)
    assert tuple(row.selection for row in result.lookups) == selections
    assert_unavailable(result, "exact_selection_unavailable")


@pytest.mark.parametrize(
    "fault,reason",
    [
        ("usage", "publication_member_changed"),
        ("resealed_usage", "publication_manifest_changed"),
        ("missing_closure", "publication_incomplete"),
        ("extra_member", "publication_unexpected_member"),
        ("missing_manifest", "publication_incomplete"),
        ("removed_directory", "publication_missing"),
        ("source_score", "publication_unavailable"),
    ],
)
def test_unavailable_after_successful_read(
    registered: wire._Plan, published: Path, fault: str, reason: str
) -> None:
    seq = (registered.source.pin.draft, registered.source.pin.review)
    healthy = consumer.lookup(seq)
    assert all(r.status == "available" for r in healthy.lookups)
    assert len(healthy.assessments) == len(healthy.accounting_records) == 1
    if fault in ("usage", "resealed_usage"):
        member = published / "delivery.json"
        delivery = json.loads(member.read_bytes())
        delivery["usage"]["input_tokens"] += 1
        member.write_bytes(encoded(delivery))
        if fault == "resealed_usage":
            manifest = published / "manifest.json"
            data = json.loads(manifest.read_bytes())
            data["files_sha256"][member.name] = storage._sha(member.read_bytes())
            manifest.write_bytes(encoded(data))
    elif fault in ("missing_closure", "missing_manifest"):
        (published / ("stop.json" if fault == "missing_closure" else "manifest.json")).unlink()
    elif fault == "removed_directory":
        published.rename(published.with_name("withdrawn"))
    elif fault == "extra_member":
        (published / "extra.json").write_bytes(b"{}")
    else:
        publisher.SCORE.write_bytes(b"{}")
    before = snapshot(published) if published.exists() else None
    invalid = consumer.lookup(seq)
    assert_unavailable(invalid, reason)
    assert tuple(row.selection for row in invalid.lookups) == seq
    after = snapshot(published) if published.exists() else None
    assert before == after


def test_invalid_selector_is_sanitized(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"private": "unpublished prose"}', encoding="utf-8")
    assert consumer.main(["--selection", str(invalid)]) == 2
    assert json.loads(capsys.readouterr().out) == {"error": "invalid_artifact_selection"}
