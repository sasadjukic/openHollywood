"""Identity can be verified while assessment remains ineligible; every operation is offline."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import production_association_export as exporter
from open_hollywood_api.services import production_association_records as records
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue

from scripts import production_association as cli
from tests.models.test_assessment_openai import offline as offline
from tests.production_association_fixtures import (
    archive,
    capture,
    expectation,
    payload,
    prompt,
    record,
    reseal,
    uid,
)


def validate(
    value: dict[str, Any], expected: records.ExpectedReview
) -> records.AssociationEvidence:
    return records.validate_snapshot(
        records.AssociationSnapshot.model_validate_json(encoded(value)), expected
    )


@pytest.mark.parametrize("historical", [True, False])
def test_identity_coverage_and_historical_heads_never_grant_eligibility(historical: bool) -> None:
    result = record(capture(historical=historical))
    proof = result.evidence
    assert proof.review_lineage.selected_is_latest_at_capture is not historical
    assert proof.draft_lineage.selected_is_latest_at_capture is not historical
    assert proof.repeated_excerpt_texts == 2
    assert [(r.start, r.end) for r in proof.catalog_occurrences] == [(0, 5), (7, 12)]
    assert (
        proof.catalog_non_whitespace_prose_coverage
        and not proof.visible_target_is_full_canonical_json
    )
    assert proof.eligibility.source_contract == "unsupported_contract"
    assert proof.eligibility.native_assessment_delivery == "missing"
    assert not proof.eligibility.assessment_attachment_eligible
    assert result.whole_review_verdict is None and result.actual_billed_cost is None
    assert result.semantic_support == result.craft == result.edit_necessity == "unassessed"
    assert not result.writer_dispatch_authorized and result.live_calls == 0
    assert not result.source.current_database_revalidated and not result.source.provider_signed
    text = records.render_record(result).decode()
    assert "````json" in text and "[Association record](R01.association.json)" in text
    assert "as of the captured snapshot" in text


@pytest.mark.parametrize(
    "path,replacement",
    [
        (("database_sha256",), "f" * 64),
        (("invocation", "id"), uid(999)),
        (("invocation", "workflow_run_id"), uid(999)),
        (("invocation", "project_id"), uid(999)),
        (("invocation", "status"), "FAILED"),
        (("invocation", "specialist_role"), "scene_writer"),
        (("invocation", "schema_validation_succeeded"), 0),
        (("invocation", "workflow_name"), "other"),
        (("invocation", "request_settings", "operation"), "draft"),
        (("invocation", "request_settings", "prompt_template_version"), "61"),
        (("invocation", "request_settings", "graph_version"), "10"),
        (("invocation", "request_settings", "scene_boundary_audit"), {"schema_version": "7"}),
        (("invocation", "run_prompt_version"), "61"),
        (("invocation", "prompt_sha256"), "f" * 64),
        (("review", "id"), uid(999)),
        (("review", "artifact_id"), uid(999)),
        (("review", "created_by_invocation_id"), uid(999)),
        (("review", "artifact_type"), "scene_draft"),
        (("review", "content", "summary"), "altered"),
        (("review", "content", "target_artifact_version_id"), uid(999)),
        (("review_outputs",), [uid(112), uid(112)]),
        (("input_link_ids",), [uid(110)]),
        (("input_link_ids",), [uid(110), uid(110)]),
        (("inputs", 0, "project_id"), uid(999)),
        (("inputs", 0, "artifact_type"), "scene_plan"),
        (("inputs", 0, "content", "prose"), "Unrelated prose."),
        (("inputs", 0, "content_sha256"), "f" * 64),
        (("inputs", 1, "artifact_type"), "story_bible"),
        (("draft_creator", "id"), uid(999)),
        (("draft_creator", "workflow_run_id"), uid(999)),
        (("draft_creator", "project_id"), uid(999)),
        (("draft_creator", "specialist_role"), "scene_critic"),
        (("draft_creator", "status"), "FAILED"),
        (("review_lineage", 0, "content_sha256"), "f" * 64),
        (("draft_lineage", 0, "parent_version_id"), uid(999)),
        (("draft_lineage", 0, "artifact_id"), uid(999)),
        (("existing_intake_reason",), "eligible"),
    ],
)
def test_snapshot_faults_are_refused(path: tuple[str | int, ...], replacement: Any) -> None:
    value = capture()
    expected = expectation(value)
    cursor: Any = value
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = replacement
    with pytest.raises(ValueError):
        validate(value, expected)


@pytest.mark.parametrize("kind", ["duplicate_input", "duplicate_lineage", "duplicate_number"])
def test_ambiguous_source_rows_are_refused(kind: str) -> None:
    value = capture(historical=True)
    if kind == "duplicate_input":
        value["inputs"].append(value["inputs"][0])
    elif kind == "duplicate_lineage":
        value["draft_lineage"].append(value["draft_lineage"][0])
    else:
        value["draft_lineage"][1]["version_number"] = 1
    with pytest.raises(ValueError):
        validate(value, expectation(value))


@pytest.mark.parametrize(
    "kind", ["scene", "duplicate", "kind", "key", "content", "prose", "gap", "ref", "tail", "blank"]
)
def test_rehashed_wrong_visible_context_and_catalogs_are_refused(kind: str) -> None:
    value = capture()
    expected = expectation(value)
    request = payload(value)
    view = request["input_artifacts"][0]
    entries = view["content"]["evidence_catalog"]
    if kind == "scene":
        request["assignment"]["unit_id"] = uid(999)
    elif kind == "duplicate":
        request["input_artifacts"][1] = view
    elif kind in ("kind", "key"):
        view[f"artifact_{kind}"] = "wrong"
    elif kind == "content":
        view["content"]["scene_id"] = uid(999)
    elif kind == "prose":
        view["content"]["prose"] = "Echo."
    elif kind == "gap":
        entries[0]["exact_excerpt"] = "cho."
    elif kind == "ref":
        entries[1]["evidence_ref"] = entries[0]["evidence_ref"]
    elif kind == "tail":
        entries.pop()
    else:
        entries[0]["exact_excerpt"] = ""
    prompt(value, request)
    # Use the new saved-message hash, so this exercises binding/coverage, not just hashing.
    with pytest.raises(ValueError):
        validate(value, expected)


@pytest.mark.parametrize("role", ["original_review", "reviewed_draft"])
def test_selection_requires_all_four_exact_keys_and_never_follows_latest(role: str) -> None:
    value = capture(historical=True)
    result = record(value)
    item = value["review"] if role == "original_review" else value["inputs"][0]
    selection = records.ArtifactSelection.model_validate_json(
        encoded(
            {
                "role": role,
                "project_id": item["project_id"],
                "artifact_id": item["artifact_id"],
                "version_id": item["id"],
                "content_sha256": item["content_sha256"],
            }
        )
    )
    assert records.selection_matches(result, selection)
    for key in ("project_id", "artifact_id", "version_id", "content_sha256"):
        assert not records.selection_matches(
            result,
            selection.model_copy(update={key: "f" * 64 if key == "content_sha256" else uid(999)}),
        )
    lineage = (
        result.evidence.review_lineage
        if role == "original_review"
        else result.evidence.draft_lineage
    )
    assert not records.selection_matches(
        result, selection.model_copy(update={"version_id": lineage.latest_version_id_at_capture})
    )
    assert not result.evidence.eligibility.assessment_attachment_eligible


def test_unchecked_models_and_duplicate_json_keys_are_rejected() -> None:
    value = capture()
    snapshot = records.AssociationSnapshot.model_validate_json(encoded(value))
    with pytest.raises(ValueError):
        records.validate_snapshot(
            snapshot.model_copy(update={"existing_intake_reason": "eligible"}), expectation(value)
        )
    with pytest.raises(ValueError):
        records.render_record(record(value).model_copy(update={"writer_dispatch_authorized": True}))
    with pytest.raises(ValueError):
        exporter._object(b'{"same":1,"same":2}')


@pytest.fixture
def registered(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> exporter._Registration:
    registration = archive(tmp_path)
    monkeypatch.setattr(exporter, "REGISTERED", (registration,))
    return registration


def pins(root: Path) -> dict[str, tuple[bytes, int]]:
    return {
        p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


def test_complete_publication_exact_reuse_and_no_current_database(
    registered: exporter._Registration,
    tmp_path: Path,
) -> None:
    before = pins(registered.archive)
    output = tmp_path / "output"
    assert not registered.database.exists()
    assert exporter.export_associations(registered.name, output) == "created"
    saved = pins(output)
    assert len(saved) == 23
    for name in [f"{case}.snapshot.json" for case in exporter.CASES]:
        assert saved[name][0] == before[name][0]
    for a, b in [
        ("source-seal.json", "acceptance-seal.json"),
        ("source-selection.json", "selection.json"),
        ("source-database-pins.json", "database-before.json"),
    ]:
        assert saved[a][0] == before[b][0]
    manifest = json.loads(saved["manifest.json"][0])
    assert manifest["files_sha256"] == {
        n: storage._sha(d[0]) for n, d in saved.items() if n != "manifest.json"
    }
    assert manifest["copied_source_members"] == 9
    assert not manifest["eligibility"]["assessment_attachment_eligible"]
    assert not manifest["current_database_revalidated"]
    assert exporter.export_associations(registered.name, output) == "reused"
    assert pins(output) == saved and pins(registered.archive) == before


@pytest.mark.parametrize("kind", ["unknown", "seal", "member", "missing", "extra", "directory"])
def test_changed_archive_is_refused_before_writing(
    registered: exporter._Registration,
    tmp_path: Path,
    kind: str,
) -> None:
    if kind == "seal":
        (registered.archive / "acceptance-seal.json").write_bytes(b"{}")
    elif kind == "member":
        (registered.archive / "R01.snapshot.json").write_bytes(b"{}")
    elif kind == "missing":
        (registered.archive / "R01.snapshot.json").unlink()
    elif kind == "extra":
        (registered.archive / "extra").write_bytes(b"unsealed")
    elif kind == "directory":
        (registered.archive / "extra").mkdir()
    with pytest.raises(ValueError):
        exporter.export_associations(
            "unknown" if kind == "unknown" else registered.name, tmp_path / "output"
        )
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("kind", ["cardinality", "duplicate", "path", "snapshot"])
def test_resealed_test_archives_still_require_valid_complete_content(
    registered: exporter._Registration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    selection = json.loads((registered.archive / "selection.json").read_bytes())
    if kind == "cardinality":
        selection["reviews"].pop()
    elif kind == "duplicate":
        selection["reviews"][1] = selection["reviews"][0]
    elif kind == "snapshot":
        (registered.archive / "R01.snapshot.json").write_bytes(encoded(capture(99)))
    (registered.archive / "selection.json").write_bytes(encoded(selection))
    changed = reseal(registered)
    if kind == "path":
        seal = json.loads((registered.archive / "acceptance-seal.json").read_bytes())
        seal["members_sha256"]["../outside"] = "f" * 64
        raw = encoded(seal)
        (registered.archive / "acceptance-seal.json").write_bytes(raw)
        changed = replace(changed, seal_sha256=storage._sha(raw))
    monkeypatch.setattr(exporter, "REGISTERED", (changed,))
    with pytest.raises(ValueError):
        exporter.export_associations(changed.name, tmp_path / "output")
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("where", ["source", "parent", "child", "db", "wal", "shm"])
def test_destination_protects_archive_and_database_family(
    registered: exporter._Registration,
    tmp_path: Path,
    where: str,
) -> None:
    target = {
        "source": registered.archive,
        "parent": tmp_path,
        "child": registered.archive / "child",
        "db": registered.database,
        "wal": Path(str(registered.database) + "-wal"),
        "shm": Path(str(registered.database) + "-shm"),
    }[where]
    before = pins(registered.archive)
    with pytest.raises(ValueError):
        exporter.export_associations(registered.name, target)
    assert pins(registered.archive) == before


@pytest.mark.parametrize("kind", ["source", "implementation", "partial_write"])
def test_drift_never_receives_a_completion_manifest(
    registered: exporter._Registration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    original_render, original_write = records.render_record, storage._write_new

    def render(value: records.AssociationRecord) -> bytes:
        output = original_render(value)
        if kind == "source":
            (registered.archive / "R01.snapshot.json").write_bytes(b"changed")
        elif kind == "implementation":
            monkeypatch.setattr(exporter, "_implementation", lambda: {"drift": "yes"})
        return output

    def write(path: Path, data: bytes) -> None:
        original_write(path, data)
        if path.name == "R01.md":
            (registered.archive / "R01.snapshot.json").write_bytes(b"changed")

    monkeypatch.setattr(records, "render_record", render)
    if kind == "partial_write":
        monkeypatch.setattr(storage, "_write_new", write)
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        exporter.export_associations(registered.name, output)
    assert not (output / "manifest.json").exists()
    assert output.exists() == (kind == "partial_write")


@pytest.mark.parametrize("kind", ["missing", "changed", "extra"])
def test_partial_or_conflicting_output_is_retained(
    registered: exporter._Registration,
    tmp_path: Path,
    kind: str,
) -> None:
    output = tmp_path / "output"
    exporter.export_associations(registered.name, output)
    if kind == "missing":
        (output / "manifest.json").unlink()
    elif kind == "changed":
        (output / "R01.association.json").write_bytes(b"changed")
    else:
        (output / "extra").write_bytes(b"changed")
    before = pins(output)
    with pytest.raises(ValueError):
        exporter.export_associations(registered.name, output)
    assert pins(output) == before


def test_secret_rejection_is_sanitized(
    registered: exporter._Registration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    guard = SecretLeakGuard((SecretValue("A repeated call."),))
    monkeypatch.setattr(storage, "active_secret_guard", lambda: guard)
    monkeypatch.setattr(cli, "REGISTERED", (registered,))
    assert cli.main(["--source", registered.name, "--output", str(tmp_path / "output")]) == 2
    text = capsys.readouterr().out
    assert "secret_guard_rejected_association_export" in text and "A repeated call." not in text
    assert not (tmp_path / "output").exists()


def test_cli_exposes_no_source_or_trust_override(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--source", "unknown", "--output", "ignored", "--trusted", "true"])
    assert "invalid choice" in capsys.readouterr().err


def test_schema_matches_tracked_contract() -> None:
    schema = records.AssociationRecord.model_json_schema()
    schema["$comment"] = (
        "Historical source identity only. Source authentication and eligibility require "
        "registered application checks; parsing this schema is not authority "
        "or assessment admission."
    )
    assert (
        exporter.ROOT / "docs/contracts/production-review-association-1.schema.json"
    ).read_bytes() == encoded(schema)


def test_cache_is_excluded_and_private_scripts_never_execute(
    registered: exporter._Registration,
    tmp_path: Path,
) -> None:
    cache = registered.archive / "__pycache__"
    cache.mkdir()
    (cache / "unloaded.pyc").write_bytes(b"unsealed cache, never opened or executed")
    assert exporter.export_associations(registered.name, tmp_path / "output") == "created"
    assert not (tmp_path / "output/private-audit.py").exists()
    assert not (tmp_path / "output/__pycache__").exists()
