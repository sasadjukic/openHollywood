"""Offline source authentication, exact publication/reuse and failure preservation."""

from __future__ import annotations

import hashlib
import json
import socket
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_completion as service
from open_hollywood_api.services import assessment_intake as intake_service
from open_hollywood_api.services import probe_review_export as probe_service
from open_hollywood_engine.evaluations.assessment_completion import (
    encoded,
    parse_submission,
    render_completion,
)
from open_hollywood_engine.secrets import SecretLeakError

from scripts import assessment_completion as cli
from tests.assessment_intake_fixtures import choice_for, plan_for
from tests.oct17_probe_fixtures import make_oct17, refresh
from tests.probe_review_fixtures import ProbeFixture, make_probe_fixture


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("No network or SQLite in authored completion publication")

    for owner, name in (
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, deny)


@dataclass
class Prepared:
    fixture: ProbeFixture
    intake: Path
    preparation: Path
    submission: Path
    output: Path


def prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str = "initial") -> Prepared:
    if mode in ("contrast", "craft", "post17"):
        fixture, parent = make_oct17(tmp_path, "post" if mode == "post17" else mode)
        contracts = [refresh(fixture)]
        if parent:
            contracts.append(refresh(parent))
    else:
        fixture = make_probe_fixture(tmp_path, retry=mode == "retry", post=mode == "post")
        contracts = [fixture.seal()]
    # Test-only registry substitution; no public service or CLI trust-pin parameter exists.
    monkeypatch.setattr(probe_service, "REGISTERED", tuple(contracts))
    collection = intake_service.collect_intakes("diagnostic_probe", fixture.live, (fixture.trial,))
    source = collection.entries[0].source
    assert source is not None
    fields = source.inventory_work.context.report_fields
    plan = intake_service.IntakeBatchPlan(
        plans={
            source.review_id: plan_for(
                source,
                choice_for(source, fields[0].field_id),
                choice_for(source, fields[1].field_id, "ambiguous"),
            )
        }
    )
    intake_folder = tmp_path / "intake"
    intake_service.write_intake(intake_folder, collection, plan)
    intake = intake_folder / "review-01.json"
    preparation = tmp_path / "preparation"
    assert service.prepare_inputs(intake, preparation) == "created"
    obj = json.loads((preparation / "submission.template.json").read_text("utf-8"))
    obj["authored_by"] = "Local test author, no semantic gold"
    for i, attempt in enumerate(obj["attempts"], 1):
        request = json.loads((preparation / f"input-{i:02d}.json").read_text("utf-8"))
        attempt["raw_final"] = json.dumps(
            {
                "assessments": {
                    u: {
                        "support": "uncertain",
                        "evidence": [],
                        "reason": "Authored fixture only.",
                    }
                    for u in request["active_unit_ids"]
                }
            }
        )
    submission = tmp_path / "submission.json"
    submission.write_bytes(encoded(obj))
    return Prepared(fixture, intake, preparation, submission, tmp_path / "publication")


@pytest.fixture
def prepared(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Prepared:
    return prepare(tmp_path, monkeypatch)


def snapshot(folder: Path) -> dict[str, tuple[bytes, int]]:
    return {
        str(p.relative_to(folder)): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in folder.rglob("*")
        if p.is_file()
    }


@pytest.mark.parametrize("mode", ["initial", "retry", "post", "contrast", "craft", "post17"])
def test_registered_sources_prepare_publish_and_reuse_without_source_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
) -> None:
    p = prepare(tmp_path, monkeypatch, mode)
    before = snapshot(p.intake.parent), snapshot(p.fixture.live), snapshot(p.preparation)
    with pytest.raises(ValueError):
        parse_submission((p.preparation / "submission.template.json").read_bytes())
    assert service.prepare_inputs(p.intake, p.preparation) == "reused"
    assert service.publish_completion(p.intake, p.submission, p.output) == "created"
    files = snapshot(p.output)
    assert len(files) == 6
    assert service.publish_completion(p.intake, p.submission, p.output) == "reused"
    assert snapshot(p.output) == files
    assert (snapshot(p.intake.parent), snapshot(p.fixture.live), snapshot(p.preparation)) == before
    assert (p.output / "intake.json").read_bytes() == p.intake.read_bytes()
    obj = json.loads((p.output / "envelope.json").read_text("utf-8"))
    assert obj["origin"] == "authored_fixture" and obj["publication_state"] == "bound_unassessed"
    assert obj["completion"]["binding"] == "complete" and not obj["writer_dispatch_authorized"]
    assert obj["intake"]["assessment_result"] is obj["intake"]["completion_receipt"] is None
    assert obj["source_adapter_receipt"]["assessment_delivery_authenticated"] is False
    assert any(f["status"] == "hold" for f in obj["intake"]["findings"])
    manifest = json.loads((p.output / "manifest.json").read_text("utf-8"))
    for name, digest in manifest["files_sha256"].items():
        assert hashlib.sha256((p.output / name).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize("where", ["live", "prepared", "intake", "submission", "ancestor"])
def test_source_and_input_paths_protected(prepared: Prepared, where: str) -> None:
    p = prepared
    destination = {
        "live": p.fixture.live / "output",
        "prepared": p.fixture.root / p.fixture.experiment / "output",
        "intake": p.intake.parent / "output",
        "submission": p.submission,
        "ancestor": p.fixture.root,
    }[where]
    before = snapshot(p.fixture.root)
    with pytest.raises(ValueError):
        service.publish_completion(p.intake, p.submission, destination)
    assert snapshot(p.fixture.root) == before


@pytest.mark.parametrize("kind", ["partial", "changed", "extra"])
def test_conflicting_output_not_repaired(prepared: Prepared, kind: str) -> None:
    p = prepared
    service.publish_completion(p.intake, p.submission, p.output)
    if kind == "partial":
        (p.output / "manifest.json").unlink()
    elif kind == "changed":
        (p.output / "view.md").write_bytes(b"changed")
    else:
        (p.output / "extra.txt").write_bytes(b"extra")
    before = snapshot(p.output)
    with pytest.raises(ValueError):
        service.publish_completion(p.intake, p.submission, p.output)
    assert snapshot(p.output) == before


@pytest.mark.parametrize(
    "mutation",
    [
        "manifest",
        "member",
        "plan",
        "raw_source",
        "unregistered",
        "saved_source",
        "traversal",
        "absolute_member",
        "extra_member",
    ],
)
def test_source_bundle_is_not_a_trust_root(
    prepared: Prepared,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    p = prepared
    path = p.intake.parent / "manifest.json"
    manifest = json.loads(path.read_text("utf-8"))
    if mutation == "manifest":
        manifest["source_sha256"] = "f" * 64
    elif mutation == "member":
        p.intake.write_bytes(p.intake.read_bytes() + b" ")
    elif mutation == "plan":
        plan = p.intake.parent / "plan.json"
        obj = json.loads(plan.read_text("utf-8"))
        next(iter(obj["plans"].values()))["source_sha256"] = "f" * 64
        plan.write_bytes(encoded(obj))
        manifest["files_sha256"]["plan.json"] = hashlib.sha256(plan.read_bytes()).hexdigest()
    elif mutation == "raw_source":
        p.fixture.path("live", "closure.json").write_bytes(b"{}")
    elif mutation == "unregistered":
        monkeypatch.setattr(probe_service, "REGISTERED", ())
    elif mutation == "saved_source":
        manifest["origin"] = "saved_review"
    else:
        name = {
            "traversal": "../escape.json",
            "absolute_member": str(p.submission),
            "extra_member": "extra.json",
        }[mutation]
        manifest["files_sha256"][name] = "0" * 64
    path.write_bytes(encoded(manifest))
    with pytest.raises((ValueError, OSError)):
        service.publish_completion(p.intake, p.submission, p.output)
    assert not p.output.exists()


@pytest.mark.parametrize("phase", ["render", "before_manifest", "submission", "output_write"])
def test_mid_publication_failure_never_commits_a_manifest(
    prepared: Prepared,
    monkeypatch: pytest.MonkeyPatch,
    phase: str,
) -> None:
    p = prepared
    if phase == "render":
        render = render_completion

        def drift(envelope: Any) -> str:
            result = render(envelope)
            p.fixture.path("live", "closure.json").write_bytes(b"{}")
            return result

        monkeypatch.setattr(service, "render_completion", drift)
    else:
        write = service._write_new

        def altered(target: Path, data: bytes) -> None:
            write(target, data)
            if target.name == "view.md":
                if phase == "before_manifest":
                    p.fixture.path("live", "closure.json").write_bytes(b"{}")
                elif phase == "submission":
                    p.submission.write_bytes(p.submission.read_bytes() + b" ")
                else:
                    raise OSError("authored injected disk failure")

        monkeypatch.setattr(service, "_write_new", altered)
    with pytest.raises((ValueError, OSError)):
        service.publish_completion(p.intake, p.submission, p.output)
    assert not (p.output / "manifest.json").exists()
    if phase == "render":
        assert not p.output.exists()
    else:
        assert p.output.exists() and len(list(p.output.iterdir())) == 5


@pytest.mark.parametrize("kind", ["symlink", "junction", "traversal"])
def test_linked_and_traversal_paths_rejected(
    prepared: Prepared, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    p = prepared
    if kind == "traversal":
        output = p.output / ".." / "escape"
    else:
        method = "is_symlink" if kind == "symlink" else "is_junction"
        real = getattr(Path, method)
        monkeypatch.setattr(Path, method, lambda path: path == p.output or real(path))
        output = p.output
    with pytest.raises(ValueError):
        service.publish_completion(p.intake, p.submission, output)
    assert not p.output.exists()


@pytest.mark.parametrize("limit", ["MAX_OUTPUT_BYTES", "MAX_SUBMISSION_BYTES", "MAX_BUNDLE_BYTES"])
def test_limits_fail_before_writes(
    prepared: Prepared, monkeypatch: pytest.MonkeyPatch, limit: str
) -> None:
    monkeypatch.setattr(service, limit, 1)
    with pytest.raises(ValueError):
        service.publish_completion(prepared.intake, prepared.submission, prepared.output)
    assert not prepared.output.exists()


def test_secret_refusal_precedes_any_output(
    prepared: Prepared, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Guard:
        def ensure_safe(self, *_args: Any, **_kwargs: Any) -> None:
            raise SecretLeakError("completion", "$")

    monkeypatch.setattr(service, "active_secret_guard", lambda: Guard())
    with pytest.raises(SecretLeakError):
        service.publish_completion(prepared.intake, prepared.submission, prepared.output)
    assert not prepared.output.exists()


def test_cli_success_and_redacted_error(
    prepared: Prepared, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    p = prepared
    args = [
        "publish",
        "--intake",
        str(p.intake),
        "--submission",
        str(p.submission),
        "--output",
        str(p.output),
    ]
    assert cli.main(args) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "created"

    def fail(*_args: Any, **_kwargs: Any) -> Any:
        raise ValueError("UNPUBLISHED_SOURCE_MUST_NOT_APPEAR")

    monkeypatch.setattr(cli, "publish_completion", fail)
    assert cli.main(args) == 2
    text = capsys.readouterr().out
    assert "UNPUBLISHED" not in text and "invalid" in text


def test_output_secret_guard_runs_after_rendering(
    prepared: Prepared,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sentinel = "authored-sensitive-sentinel"
    rendered = []

    def render(envelope: Any) -> str:
        rendered.append(True)
        return render_completion(envelope) + sentinel

    class Guard:
        def ensure_safe(self, value: Any, **_kwargs: Any) -> None:
            if sentinel in str(value):
                raise SecretLeakError("completion", "$")

    monkeypatch.setattr(service, "render_completion", render)
    monkeypatch.setattr(service, "active_secret_guard", lambda: Guard())
    with pytest.raises(SecretLeakError):
        service.publish_completion(prepared.intake, prepared.submission, prepared.output)
    assert rendered == [True] and not prepared.output.exists()


@pytest.mark.parametrize("conflict", ["directory", "file"])
def test_exclusive_creation_keeps_another_writers_bytes(
    prepared: Prepared,
    monkeypatch: pytest.MonkeyPatch,
    conflict: str,
) -> None:
    p = prepared
    if conflict == "directory":
        mkdir = Path.mkdir

        def occupied(path: Path, *args: Any, **kwargs: Any) -> None:
            if path == p.output:
                mkdir(path)
                (path / "other-owner").write_bytes(b"keep")
            mkdir(path, *args, **kwargs)

        monkeypatch.setattr(Path, "mkdir", occupied)
    else:
        write = service._write_new

        def occupied_file(path: Path, data: bytes) -> None:
            if path.name == "envelope.json":
                path.write_bytes(b"keep")
            write(path, data)

        monkeypatch.setattr(service, "_write_new", occupied_file)
    with pytest.raises(FileExistsError):
        service.publish_completion(p.intake, p.submission, p.output)
    assert not (p.output / "manifest.json").exists()
    assert (
        p.output / ("other-owner" if conflict == "directory" else "envelope.json")
    ).read_bytes() == b"keep"


def test_external_parent_archives_are_protected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from open_hollywood_engine.evaluations.probe_review_evidence import CONTRASTS

    p = prepare(tmp_path, monkeypatch, "post17")
    for name in (CONTRASTS, CONTRASTS + "-live"):
        destination = p.fixture.live.with_name(name) / "output"
        with pytest.raises(ValueError, match="completion_protected_path"):
            service.publish_completion(p.intake, p.submission, destination)
        assert not destination.exists()


def test_no_pending_work_cannot_prepare_an_empty_success(
    prepared: Prepared,
) -> None:
    p = prepared
    collection = intake_service.collect_intakes(
        "diagnostic_probe", p.fixture.live, (p.fixture.trial,)
    )
    empty = p.fixture.root / "empty-intake"
    intake_service.write_intake(empty, collection)
    with pytest.raises(ValueError, match="no_pending_work"):
        service.prepare_inputs(empty / "review-01.json", p.output)
    assert not p.output.exists()
