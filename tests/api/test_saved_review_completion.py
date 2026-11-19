"""Exercise the operator entry point over portable, disposable saved-review capture fixtures."""

from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import saved_review_completion as adapter
from open_hollywood_api.services.review_evidence_export import readonly_connection
from open_hollywood_engine.evaluations.assessment_completion import encoded

from scripts.saved_review_completion import main
from tests.api.test_production_assessment_qualification import anyio_backend as anyio_backend
from tests.api.test_production_assessment_qualification import offline as offline
from tests.api.test_production_assessment_qualification import prepared as prepared
from tests.api.test_production_assessment_qualification import source as source
from tests.production_assessment_fixtures import FixtureRegistration, capture, response_for, sha

pytestmark = pytest.mark.anyio


def pin_files(folder: Path) -> dict[str, str]:
    return {
        p.relative_to(folder).as_posix(): sha(p.read_bytes())
        for p in folder.rglob("*")
        if p.is_file()
    }


def register(root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    members = {"work/" + k: v for k, v in pin_files(root / "work").items()}
    seal = encoded({"members_sha256": members})
    (root / "acceptance-seal.json").write_bytes(seal)
    monkeypatch.setattr(
        adapter, "REGISTERED", adapter._Registration("unit", root, "work", sha(seal))
    )


@pytest.fixture
def archive(source: FixtureRegistration, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "archive"
    work = root / "work"
    dbdir = work / "database"
    dbdir.mkdir(parents=True)
    with (
        readonly_connection(source.database) as original,
        closing(sqlite3.connect(dbdir / "open_hollywood.db")) as copied,
    ):
        original.backup(copied)
    shutil.copytree(source.intake_folder.parent, work / "source-fixture")
    capture(source, work / "delivery", response_for(source))
    capture(source, work / "intent-only", "", terminal=False)
    register(root, monkeypatch)
    return root


def read(path: Path) -> Any:
    return json.loads(path.read_bytes())


async def test_cli_replays_exact_source_and_publishes_immutable_result(
    archive: Path, source: FixtureRegistration, tmp_path: Path
) -> None:
    before = pin_files(archive)
    base = ["--source", "unit"]
    request_dir = tmp_path / "inputs"
    assert main(["prepare", *base, "--output", str(request_dir)]) == 0
    assert (request_dir / "request.json").read_bytes() == source.request
    assert (request_dir / "intake.json").read_bytes() == (
        source.intake_folder / "review-01.json"
    ).read_bytes()
    pin = adapter.SavedReviewPin.model_validate(read(request_dir / "source-receipt.json")["source"])
    assert (pin.review, pin.draft) == source.selections
    # Changing only the version retains the content digest, as in a same-text revision.
    for exact in (pin.review, pin.draft):
        replacements = {
            "version_id": str(uuid4()),
            "project_id": str(uuid4()),
            "artifact_id": str(uuid4()),
            "content_sha256": "0" * 64,
            "role": "original_review" if exact.role == "reviewed_draft" else "reviewed_draft",
        }
        for field, other in replacements.items():
            with pytest.raises(ValueError, match="saved_review_wrong_selection"):
                adapter.export_saved_review(
                    "publish",
                    "unit",
                    tmp_path / "wrong-selection",
                    selection=exact.model_copy(update={field: other}),
                    journal="complete",
                )
    assert not (tmp_path / "wrong-selection").exists()
    selected = tmp_path / "draft.json"
    selected.write_bytes(encoded(pin.draft.model_dump(mode="json")))
    full_args = [*base, "--journal", "complete", "--selection", str(selected)]
    report = tmp_path / "audit"
    assert main(["audit", *full_args, "--output", str(report)]) == 0
    audit = read(report / "audit.json")
    assert audit["state"] == "bound_unassessed" and audit["fixture_publication_eligible"]
    assert audit["delivery_origin"] == "authored_terminal_fixture"
    assert audit["selection"] == read(selected)
    assert audit["result"]["raw_final"] == response_for(source)
    assert audit["completion"]["complete_delivery"] and audit["completion"]["binding"] == "complete"
    assert audit["completion"]["unknown_usage_attempts"] == 1
    assert not audit["model_evidence"] and not audit["production_attachment_eligible"]
    assert audit["result"]["evidence_adequacy"] == audit["result"]["craft"] == "unassessed"
    dest = tmp_path / "published"
    args = ["publish", *full_args, "--output", str(dest)]
    assert main(args) == 0
    assert read(dest / "envelope.json")["audit"] == audit
    assert read(dest / "envelope.json")["intake"] == source.intake.model_dump(mode="json")
    assert "AUTHORED FIXTURE" in (dest / "view.md").read_text(encoding="utf-8")
    assert not read(dest / "source-receipt.json")["raw_critic_response_available"]
    snapshot = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in dest.iterdir()}
    assert main(args) == 0
    assert all((p.read_bytes(), p.stat().st_mtime_ns) == value for p, value in snapshot.items())
    (dest / "extra.txt").write_text("conflict")
    assert main(args) == 2
    assert pin_files(archive) == before


@pytest.mark.parametrize(
    "journal,state,possible",
    [("absent", "missing_delivery", 0), ("intent-only", "missing_terminal", 1)],
)
async def test_negative_journals_are_auditable_but_unpublishable(
    archive: Path,
    tmp_path: Path,
    journal: adapter.Journal,
    state: str,
    possible: int,
) -> None:
    dest = tmp_path / "audit"
    adapter.export_saved_review("audit", "unit", dest, journal=journal)
    value = read(dest / "audit.json")
    assert value["state"] == state and value["possibly_sent_without_terminal"] == possible
    assert value["native_receipt"] is None and not value["fixture_publication_eligible"]
    assert value["delivery_origin"] is None
    assert value["result"] is None and value["completion"]["binding"] == "unresolved"
    with pytest.raises(ValueError, match="incomplete_publication"):
        adapter.export_saved_review("publish", "unit", tmp_path / "out", journal=journal)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    "fault",
    [
        "wrong_version",
        "wrong_intent",
        "source_drift",
        "unregistered",
        "unexpected_wal",
        "bad_stop",
        "origin",
        "incomplete_result",
        "truncated",
    ],
)
async def test_refusal_before_publishing(
    archive: Path,
    source: FixtureRegistration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fault: str,
) -> None:
    target = archive / "work/delivery"
    selected = source.selections[0]
    name = "unit"
    if fault == "wrong_version":
        selected = selected.model_copy(update={"version_id": source.selections[1].version_id})
    elif fault == "unregistered":
        name = "unknown"
    elif fault == "unexpected_wal":
        (archive / "work/database/open_hollywood.db-wal").write_bytes(b"fixture")
    elif fault == "source_drift":
        (archive / "work/source-fixture/request.json").write_bytes(b"{}")
    else:
        if fault == "wrong_intent":
            path = target / "intent.json"
            value = read(path)
            value["request_sha256"] = "0" * 64
        elif fault == "bad_stop":
            path = target / "stop.json"
            value = {"terminal_sha256": "f" * 64}
        else:
            path = target / "terminal.json"
            value = read(path)
            if fault == "origin":
                value["origin"] = "observed_model_delivery"
            elif fault == "incomplete_result":
                value["raw_final"] = '{"assessments":{}}'
                value["raw_sha256"] = sha(value["raw_final"].encode())
            else:
                value["status"] = "length"
        path.write_bytes(encoded(value))
        if path.name == "terminal.json":
            (target / "stop.json").write_bytes(encoded({"terminal_sha256": sha(path.read_bytes())}))
        # Independently registered bad fixtures exercise semantic checks after byte integrity.
        register(archive, monkeypatch)
    dest = tmp_path / "publish"
    with pytest.raises(ValueError):
        adapter.export_saved_review("publish", name, dest, journal="complete", selection=selected)
    assert not dest.exists()
    if fault in ("truncated", "incomplete_result"):
        adapter.export_saved_review("audit", name, tmp_path / "audit", journal="complete")
        audit = read(tmp_path / "audit/audit.json")
        assert audit["state"] == ("length" if fault == "truncated" else "invalid")
        assert audit["result"] is None and not audit["fixture_publication_eligible"]


async def test_protected_destination_and_drift_during_publication(
    archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(ValueError, match="protected_path"):
        adapter.export_saved_review("prepare", "unit", archive / "output")
    original = storage._write_new

    def drift(path: Path, data: bytes) -> None:
        original(path, data)
        if path.name == "envelope.json":
            (archive / "work/delivery/terminal.json").write_bytes(b"{}")

    monkeypatch.setattr(storage, "_write_new", drift)
    with pytest.raises(ValueError, match="changed_member"):
        adapter.export_saved_review("publish", "unit", tmp_path / "partial", journal="complete")
    assert not (tmp_path / "partial/manifest.json").exists()
