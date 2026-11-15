"""Offline authored-source qualification; source provenance cannot grant delivery authority."""

from __future__ import annotations

import json
import socket
import sqlite3
from pathlib import Path
from typing import Any

import httpx
import pytest
from open_hollywood_api.services import assessment_authored_source as service
from open_hollywood_api.services import assessment_completion as publication
from open_hollywood_engine.evaluations.assessment_authored_source import (
    AuthoredSource,
    AuthoredSourceSubmission,
    complete_fixture,
    render_presentation,
    validate_source,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_presentation import SYSTEM
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import EvidenceError
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import ValidationError

from scripts import assessment_authored_source as cli
from tests.authored_source_fixtures import make_archive, reseal, submission


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Authored-source integration forbids network and database I/O")

    for owner, name in (
        (httpx.Client, "send"),
        (httpx.AsyncClient, "send"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "getaddrinfo"),
        (socket, "create_connection"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, deny)


@pytest.fixture
def archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "archive"
    monkeypatch.setattr(service, "REGISTERED", (make_archive(root),))
    return root


def snapshot(path: Path) -> dict[str, tuple[bytes, int]]:
    return {
        p.relative_to(path).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
        for p in path.rglob("*")
        if p.is_file()
    }


@pytest.mark.parametrize("family", ["F01", "F02", "F03"])
def test_source_preparation_and_fixture_completion(
    archive: Path, tmp_path: Path, family: str
) -> None:
    before = snapshot(archive)
    source = service.collect(service.SOURCE_ID, family).source
    presentation = render_presentation(source)
    assert presentation.messages[0].content == SYSTEM
    assert presentation.active_unit_ids == ("Q001", "Q002", "Q003")
    visible = json.loads(presentation.messages[1].content)
    assert visible["full_original_work"] == source.work.model_dump(mode="json")
    assert visible["whole_field_dispositions"][-1]["disposition"] == "unselected_context"
    assert "OPERATOR_ONLY_GOLD_SENTINEL" not in presentation.model_dump_json()
    prep, output = tmp_path / "prepare", tmp_path / "complete"
    assert service.prepare(service.SOURCE_ID, family, prep) == "created"
    prepared = snapshot(prep)
    assert service.prepare(service.SOURCE_ID, family, prep) == "reused"
    assert snapshot(prep) == prepared
    with pytest.raises(ValidationError):
        AuthoredSourceSubmission.model_validate_json(
            (prep / "submission.template.json").read_bytes()
        )
    path = tmp_path / "submission.json"
    path.write_bytes(encoded(submission(source)))
    assert service.publish_fixture(service.SOURCE_ID, family, path, output) == "created"
    published = snapshot(output)
    assert service.publish_fixture(service.SOURCE_ID, family, path, output) == "reused"
    assert snapshot(output) == published and snapshot(archive) == before
    envelope = json.loads((output / "envelope.json").read_bytes())
    assert envelope["source_origin"] == "authored_diagnostic"
    assert envelope["delivery_origin"] == "authored_fixture"
    assert envelope["source"]["result"] is None and envelope["source"]["receipt"] is None
    assert (
        envelope["completion"]["complete_delivery"]
        and envelope["completion"]["binding"] == "complete"
    )
    assert envelope["completion"]["support"] == "unassessed"
    assert envelope["bound_result"]["evidence_adequacy"] == "unassessed"
    assert not envelope["model_evidence"] and not envelope["writer_dispatch_authorized"]
    assert envelope["usage"]["cached_input_tokens"] is None
    assert envelope["usage"]["provenance"] == "not_applicable_no_inference"
    assert envelope["fixture_input_identity_sha256"] != source.original_scope.request_sha256
    assert (
        envelope["derived_fixture_authority"]["request_sha256"]
        == envelope["fixture_input_identity_sha256"]
    )
    assert envelope["source"]["authority"] == source.authority.model_dump(mode="json")
    for name in service.SAFE_MEMBERS:
        assert (output / name).read_bytes() == (archive / "admitted" / family / name).read_bytes()
    for name, digest in json.loads((output / "manifest.json").read_bytes())["files_sha256"].items():
        assert publication._sha((output / name).read_bytes()) == digest


@pytest.mark.parametrize(
    "member",
    ["manifest.json", "F01/work.json", "F02/admission.json", "F03/view.md", "cases-and-gold.md"],
)
def test_archive_drift_rejected(archive: Path, tmp_path: Path, member: str) -> None:
    path = archive / "admitted" / member
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError):
        service.prepare(service.SOURCE_ID, "F01", tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    "part",
    [
        "root_extra",
        "family_extra",
        "missing",
        "helper",
        "manifest_duplicate",
        "unknown_source",
        "unknown_family",
    ],
)
def test_source_failures(archive: Path, tmp_path: Path, part: str) -> None:
    source_id, family = service.SOURCE_ID, "F01"
    if part == "root_extra":
        (archive / "admitted" / "extra").mkdir()
    elif part == "family_extra":
        (archive / "admitted/F01/extra.json").write_text("{}")
    elif part == "missing":
        (archive / "admitted/F01/work.json").unlink()
    elif part == "helper":
        (archive / "admit.py").write_text("changed")
    elif part == "manifest_duplicate":
        path = archive / "admitted/manifest.json"
        path.write_bytes(path.read_bytes().replace(b"{", b'{"live_calls":0,', 1))
    elif part == "unknown_source":
        source_id = "unregistered"
    else:
        family = "F04"
    with pytest.raises(ValueError):
        service.prepare(source_id, family, tmp_path / "out")


@pytest.mark.parametrize(
    "change",
    ["origin", "scope", "authority", "messages", "document", "partial_field", "brief", "pin"],
)
def test_domain_rechecks_bindings(archive: Path, change: str) -> None:
    source = service.collect(service.SOURCE_ID, "F01").source
    data = source.model_dump(mode="json")
    if change == "origin":
        data["source"]["source_origin"] = "diagnostic_probe"
    elif change == "scope":
        data["original_scope"]["request_sha256"] = "0" * 64
    elif change == "authority":
        data["authority"]["request_sha256"] = "0" * 64
    elif change == "messages":
        data["work"]["context"]["messages"][0]["content"] = "omitted context"
    elif change == "document":
        data["source_packet"]["sources"].pop()
    elif change == "partial_field":
        data["work"]["context"]["statements"][0]["end"] -= 1
    elif change == "brief":
        data["briefs"]["briefs"][0]["question"] = "Changed question"
    else:
        data["source"]["input_members_sha256"]["work.json"] = "0" * 64
    with pytest.raises(ValueError):
        validate_source(AuthoredSource.model_validate_json(encoded(data)))


@pytest.mark.parametrize(
    "change",
    [
        "origin",
        "receipt",
        "usage",
        "approval",
        "family",
        "presentation",
        "missing_unit",
        "extra_unit",
        "bad_ref",
        "duplicate_id",
        "duplicate_key",
        "truncated",
        "unsupported_field",
        "blank_author",
    ],
)
def test_submission_rejects_untrusted_or_malformed(
    archive: Path, tmp_path: Path, change: str
) -> None:
    source = service.collect(service.SOURCE_ID, "F01").source
    data = submission(source)
    final = json.loads(data["raw_final"])
    if change == "origin":
        data["delivery_origin"] = "observed_openai_transport"
    elif change == "receipt":
        data["receipt"] = {}
    elif change == "usage":
        data["usage"] = {"input_tokens": 12}
    elif change == "approval":
        data["writer_dispatch_authorized"] = True
    elif change == "family":
        data["source"]["family"] = "F02"
    elif change == "presentation":
        data["presentation_canonical_sha256"] = "0" * 64
    elif change == "blank_author":
        data["authored_by"] = "   "
    else:
        if change == "missing_unit":
            final["assessments"].pop("Q001")
        elif change == "extra_unit":
            final["assessments"]["Q004"] = final["assessments"]["Q001"]
        elif change == "bad_ref":
            final["assessments"]["Q001"]["evidence"] = ["S404"]
        elif change == "unsupported_field":
            final["assessments"]["Q001"]["effect_note"] = "extra"
        data["raw_final"] = encoded(final).decode()
        if change == "duplicate_id":
            data["raw_final"] = data["raw_final"].replace('"Q001":', '"Q002":')
        elif change == "truncated":
            data["raw_final"] = data["raw_final"][:-4]
    raw = encoded(data)
    if change == "duplicate_key":
        raw = raw.replace(b"{", b'{"delivery_origin":"authored_fixture",', 1)
    path = tmp_path / "submission.json"
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        service.publish_fixture(service.SOURCE_ID, "F01", path, tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_binding_does_not_verify_semantics(archive: Path) -> None:
    source = service.collect(service.SOURCE_ID, "F01").source
    data = submission(source)
    final = json.loads(data["raw_final"])
    final["assessments"]["Q001"]["reason"] = "Unsupported invented semantic interpretation."
    data["raw_final"] = encoded(final).decode()
    envelope, _ = complete_fixture(
        source, AuthoredSourceSubmission.model_validate_json(encoded(data))
    )
    assert envelope["publication_state"] == "bound_unassessed"
    bound = envelope["bound_result"]
    assert isinstance(bound, dict) and bound["evidence_adequacy"] == "unassessed"


def test_gold_not_parsed_or_presented(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    before = render_presentation(service.collect(service.SOURCE_ID, "F01").source)
    (archive / "admitted/F01/admission.json").write_text("NEW_NON_JSON_GOLD_SENTINEL")
    monkeypatch.setattr(service, "REGISTERED", (reseal(archive),))
    after = render_presentation(service.collect(service.SOURCE_ID, "F01").source)
    old_packet, new_packet = (json.loads(p.messages[1].content) for p in (before, after))
    old_packet.pop("source")
    new_packet.pop("source")
    assert old_packet == new_packet and before.response_schema == after.response_schema
    assert "GOLD_SENTINEL" not in after.model_dump_json()
    assert before.source.manifest_bytes_sha256 != after.source.manifest_bytes_sha256


@pytest.mark.parametrize("target", ["source_child", "ancestor", "submission", "traversal"])
def test_protected_paths(archive: Path, tmp_path: Path, target: str) -> None:
    source = service.collect(service.SOURCE_ID, "F01").source
    path = tmp_path / "submission.json"
    path.write_bytes(encoded(submission(source)))
    output = {
        "source_child": archive / "new",
        "ancestor": tmp_path,
        "submission": path,
        "traversal": tmp_path / "child/../out",
    }[target]
    with pytest.raises(ValueError):
        service.publish_fixture(service.SOURCE_ID, "F01", path, output)


def test_partial_publication_is_not_repaired(
    archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = publication._write_new
    output = tmp_path / "out"

    def interrupt(path: Path, raw: bytes) -> None:
        if path.name == "manifest.json":
            raise OSError("injected disk failure")
        original(path, raw)

    monkeypatch.setattr(publication, "_write_new", interrupt)
    with pytest.raises(OSError):
        service.prepare(service.SOURCE_ID, "F01", output)
    assert output.is_dir() and not (output / "manifest.json").exists()
    before = snapshot(output)
    monkeypatch.setattr(publication, "_write_new", original)
    with pytest.raises(ValueError):
        service.prepare(service.SOURCE_ID, "F01", output)
    assert snapshot(output) == before


def test_source_drift_before_manifest(
    archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = publication._write_new

    def mutate(path: Path, raw: bytes) -> None:
        original(path, raw)
        (archive / "admitted/F03/view.md").write_text("drift")

    monkeypatch.setattr(publication, "_write_new", mutate)
    with pytest.raises(ValueError):
        service.prepare(service.SOURCE_ID, "F01", tmp_path / "out")
    assert not (tmp_path / "out/manifest.json").exists()


def test_cli_errors_redacted(
    archive: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail(*args: Any, **kwargs: Any) -> Any:
        raise SecretLeakError("PRIVATE_SENTINEL", "fixture")

    monkeypatch.setattr(cli, "prepare", fail)
    assert (
        cli.main(
            [
                "prepare",
                "--source",
                service.SOURCE_ID,
                "--family",
                "F01",
                "--output",
                str(tmp_path / "out"),
            ]
        )
        == 2
    )
    assert "PRIVATE_SENTINEL" not in capsys.readouterr().out


def test_presentation_hash_exact(archive: Path) -> None:
    presentation = render_presentation(service.collect(service.SOURCE_ID, "F01").source)
    assert presentation.messages_canonical_sha256 == canonical_sha256(
        [m.model_dump(mode="json") for m in presentation.messages]
    )
    assert presentation.schema_canonical_sha256 == canonical_sha256(presentation.response_schema)
    with pytest.raises(EvidenceError):
        service.collect("not-registered", "F01")


def test_self_signed_manifest_is_not_registration(archive: Path, tmp_path: Path) -> None:
    (archive / "admitted/F01/admission.json").write_text("self signed replacement")
    reseal(archive)
    with pytest.raises(ValueError, match="authored_registration_changed"):
        service.prepare(service.SOURCE_ID, "F01", tmp_path / "out")


def test_submission_drift_prevents_manifest(
    archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "submission.json"
    path.write_bytes(encoded(submission(service.collect(service.SOURCE_ID, "F01").source)))
    original = publication._write_new

    def mutate(target: Path, raw: bytes) -> None:
        original(target, raw)
        path.write_bytes(path.read_bytes() + b" ")

    monkeypatch.setattr(publication, "_write_new", mutate)
    with pytest.raises(ValueError, match="authored_submission_drift"):
        service.publish_fixture(service.SOURCE_ID, "F01", path, tmp_path / "out")
    assert not (tmp_path / "out/manifest.json").exists()


def test_changed_output_not_repaired(archive: Path, tmp_path: Path) -> None:
    output = tmp_path / "out"
    service.prepare(service.SOURCE_ID, "F01", output)
    (output / "presentation.json").write_text("altered")
    before = snapshot(output)
    with pytest.raises(ValueError, match="completion_output_conflict"):
        service.prepare(service.SOURCE_ID, "F01", output)
    assert snapshot(output) == before


def test_file_bounds(archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(publication, "MAX_FILE_BYTES", 8)
    with pytest.raises(ValueError, match="completion_input_too_large"):
        service.prepare(service.SOURCE_ID, "F01", tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_secret_guard_prevents_publication(
    archive: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Guard:
        def ensure_safe(self, value: Any, **kwargs: Any) -> None:
            if kwargs.get("destination") == "authored completion publication":
                raise SecretLeakError("fixture", "projection")

    monkeypatch.setattr(publication, "active_secret_guard", lambda: Guard())
    with pytest.raises(SecretLeakError):
        service.prepare(service.SOURCE_ID, "F01", tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_linked_source_refused(archive: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = Path.is_junction

    def linked(path: Path) -> bool:
        return path.name == "F02" or original(path)

    monkeypatch.setattr(Path, "is_junction", linked)
    with pytest.raises(ValueError, match="completion_linked_path"):
        service.collect(service.SOURCE_ID, "F01")


def test_cli_has_no_live_or_origin_override(archive: Path, tmp_path: Path) -> None:
    for extra in (
        ("--origin", "observed_openai_transport"),
        ("--run",),
        ("--manifest-sha256", "0" * 64),
    ):
        with pytest.raises(SystemExit) as raised:
            cli.main(
                [
                    "prepare",
                    "--source",
                    service.SOURCE_ID,
                    "--family",
                    "F01",
                    "--output",
                    str(tmp_path / "out"),
                    *extra,
                ]
            )
        assert raised.value.code == 2
    assert not (tmp_path / "out").exists()
