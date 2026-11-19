"""Consumer boundaries with authored fixtures and no model/database/network operations."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_consumer as service
from open_hollywood_api.services import assessment_consumer_projection as projection
from open_hollywood_api.services import assessment_observed_completion as probe
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.secrets import SecretLeakGuard, SecretValue

from scripts import assessment_consumer as cli
from tests.assessment_consumer_fixtures import envelope, publication
from tests.models.test_assessment_openai import offline as offline


def project(value: dict[str, Any]) -> projection.ConsumerProjection:
    return projection._project(
        value,
        registration="test-only",
        publication_sha256="b" * 64,
        work_name="N06",
        source_origin="registered_diagnostic_probe",
        observation_binding={"fixture_only": True},
    )


def test_full_inventory_holds_attributed_uncertainty_and_literal_renderer() -> None:
    value = envelope()
    view = project(value)
    assert len(view.fields) == 6
    assert [r.display_status for r in view.fields] == [
        "model_judgment_available",
        "model_judgment_available",
        "hold",
        "hold",
        "not_selected",
        "not_selected",
    ]
    assert view.production_binding.canonical_review_id is None
    assert view.production_binding.artifact_version_id is None
    assert view.authority_record is None and view.whole_review_verdict is None
    assert view.usage.cached_input_tokens == 10
    for row in view.fields:
        assert all(row.model_dump()[key] == "unassessed" for key in projection.HOLDS)
        assert not row.writer_dispatch_authorized
    assert all(r.model_judgment is None for r in view.fields[2:])
    assert all(
        r.model_judgment and r.model_judgment.support == "uncertain" and not r.citations
        for r in view.fields[:2]
    )
    text = projection._render(view).decode()
    assert "````json" in text and "[Consumer record](consumer.N06.json)" in text
    assert "not a whole-review verdict" in text and "material sufficiency" in text
    assert len({r.identity_sha256 for r in view.fields}) == 6
    assert project(value).model_dump() == view.model_dump()


@pytest.mark.parametrize("label", ["supported", "unsupported", "uncertain"])
def test_definite_labels_and_complete_spans_never_establish_semantic_credit(label: str) -> None:
    view = project(envelope(support=label, cite=True))
    for row in view.fields[:2]:
        assert row.model_judgment is not None and row.model_judgment.support == label
        assert row.citations[0].field_extent == "complete_field"
        assert row.citations[0].material_coverage == row.semantic_support == "unassessed"
        assert row.edit_necessity == row.craft == "unassessed"
        assert not row.writer_dispatch_authorized


@pytest.mark.parametrize("label", ["supported", "unsupported"])
def test_definite_judgment_without_evidence_is_refused(label: str) -> None:
    with pytest.raises(ValueError, match="definite_without_evidence"):
        project(envelope(support=label))


def test_identity_namespaces_repeat_field_ids() -> None:
    value = envelope()
    first = project(value)
    second = projection._project(
        value,
        registration="different-registration",
        publication_sha256="c" * 64,
        work_name="N06",
        source_origin="registered_diagnostic_probe",
        observation_binding={"fixture_only": True},
    )
    assert {r.identity_sha256 for r in first.fields}.isdisjoint(
        r.identity_sha256 for r in second.fields
    )


@pytest.mark.parametrize(
    "path,replacement",
    [
        (("origin",), "authored_fixture"),
        (("source_origin",), "saved_review"),
        (("work",), "N07"),
        (("observation_binding",), {}),
        (("state",), "failed"),
        (("journal_closed",), False),
        (("stop_reason",), "length"),
        (("accounting_clear",), False),
        (("actual_billed_cost",), 1.0),
        (("writer_dispatch_authorized",), True),
        (("semantic_support",), "supported"),
        (("endpoint_slots",), []),
        (("terminal", "accounting_hold"), True),
        (("terminal", "unknown_elapsed_endpoints"), 1),
        (("terminal", "budget_violations"), ["overrun"]),
        (("terminal", "usage", "cached_input_tokens"), None),
        (("terminal", "usage", "input_tokens"), True),
        (("terminal", "usage", "output_tokens"), -1),
        (("terminal", "state"), "length"),
        (("terminal", "bound_result"), None),
        (("terminal", "native_receipt", "request_sha256"), "e" * 64),
        (("terminal", "bound_result", "raw_final"), "{}"),
        (("completion", "delivered_units"), 1),
        (("intake", "findings"), []),
        (("intake", "declarations", "declarations"), []),
        (("intake", "briefs", "briefs"), []),
    ],
)
def test_failed_or_incomplete_input_never_becomes_available(
    path: tuple[str, ...],
    replacement: Any,
) -> None:
    value = envelope()
    cursor = value
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = replacement
    with pytest.raises((ValueError, TypeError, KeyError)):
        project(value)


@pytest.fixture
def registered(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> service._Registration:
    registration = publication(tmp_path)
    monkeypatch.setattr(service, "REGISTERED", (registration,))
    monkeypatch.setattr(probe, "publish_observed", lambda name, path: "reused")
    return registration


def pins(path: Path) -> dict[str, tuple[bytes, int]]:
    return {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in path.iterdir()}


def test_all_members_byte_exact_manifest_last_and_idempotent(
    registered: service._Registration,
    tmp_path: Path,
) -> None:
    before = pins(registered.publication)
    output = tmp_path / "output"
    assert service.export_consumer(registered.name, output) == "created"
    saved = pins(output)
    assert len(saved) == 7
    for name, (data, _) in before.items():
        assert saved["source-manifest.json" if name == "manifest.json" else name][0] == data
    manifest = json.loads(saved["manifest.json"][0])
    assert manifest["files_sha256"] == {
        n: storage._sha(d[0]) for n, d in saved.items() if n != "manifest.json"
    }
    assert service.export_consumer(registered.name, output) == "reused"
    assert pins(output) == saved and pins(registered.publication) == before


@pytest.mark.parametrize("kind", ["unknown", "manifest", "member", "missing", "extra", "upstream"])
def test_changed_sources_refused_before_writing(
    registered: service._Registration,
    tmp_path: Path,
    kind: str,
) -> None:
    if kind == "manifest":
        (registered.publication / "manifest.json").write_bytes(b"{}")
    elif kind == "member":
        (registered.publication / "N06.view.md").write_bytes(b"changed")
    elif kind == "missing":
        (registered.publication / "N06.view.md").unlink()
    elif kind == "extra":
        (registered.publication / "extra").write_bytes(b"extra")
    elif kind == "upstream":
        (tmp_path / "upstream.json").write_bytes(b"changed")
    with pytest.raises(ValueError):
        service.export_consumer(
            "unknown" if kind == "unknown" else registered.name, tmp_path / "output"
        )
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize("where", ["source", "parent", "child", "upstream"])
def test_bidirectional_destination_protection(
    registered: service._Registration,
    tmp_path: Path,
    where: str,
) -> None:
    target = {
        "source": registered.publication,
        "parent": tmp_path,
        "child": registered.publication / "child",
        "upstream": tmp_path / "upstream.json",
    }[where]
    before = pins(registered.publication)
    with pytest.raises(ValueError):
        service.export_consumer(registered.name, target)
    assert pins(registered.publication) == before


@pytest.mark.parametrize("kind", ["source", "implementation", "partial_write"])
def test_changes_during_render_or_write_never_receive_manifest(
    registered: service._Registration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    kind: str,
) -> None:
    old_render = projection._render
    old_implementation = service._implementation
    old_write = storage._write_new

    def render(view: projection.ConsumerProjection) -> bytes:
        result = old_render(view)
        if kind == "source":
            (tmp_path / "upstream.json").write_bytes(b"drift")
        elif kind == "implementation":
            monkeypatch.setattr(
                service, "_implementation", lambda: {**old_implementation(), "changed": True}
            )
        return result

    def write(path: Path, data: bytes) -> None:
        old_write(path, data)
        if path.name == "N06.view.md":
            (tmp_path / "upstream.json").write_bytes(b"drift")

    monkeypatch.setattr(projection, "_render", render)
    if kind == "partial_write":
        monkeypatch.setattr(storage, "_write_new", write)
    output = tmp_path / "output"
    with pytest.raises(ValueError):
        service.export_consumer(registered.name, output)
    assert not (output / "manifest.json").exists()
    assert output.exists() == (kind == "partial_write")


@pytest.mark.parametrize("kind", ["missing", "changed", "extra"])
def test_conflicting_output_is_retained_and_never_repaired(
    registered: service._Registration,
    tmp_path: Path,
    kind: str,
) -> None:
    output = tmp_path / "output"
    service.export_consumer(registered.name, output)
    if kind == "missing":
        (output / "manifest.json").unlink()
    elif kind == "changed":
        (output / "consumer.N06.json").write_bytes(b"changed")
    else:
        (output / "extra").write_bytes(b"extra")
    before = pins(output)
    with pytest.raises(ValueError):
        service.export_consumer(registered.name, output)
    assert pins(output) == before


def test_untrusted_filename_and_secret_refusals(
    registered: service._Registration,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = registered.publication / "manifest.json"
    manifest = json.loads(path.read_bytes())
    manifest["files_sha256"]["../outside"] = "f" * 64
    path.write_bytes(encoded(manifest))
    changed = replace(registered, manifest_sha256=storage._sha(path.read_bytes()), member_count=4)
    monkeypatch.setattr(service, "REGISTERED", (changed,))
    with pytest.raises(ValueError, match="filename"):
        service.export_consumer(changed.name, tmp_path / "output")
    guard = SecretLeakGuard((SecretValue("fixture_only"),))
    monkeypatch.setattr(storage, "active_secret_guard", lambda: guard)
    monkeypatch.setattr(cli, "REGISTERED", (changed,))
    assert cli.main(["--source", changed.name, "--output", str(tmp_path / "output")]) == 2
    assert not (tmp_path / "output").exists()


def test_cli_has_no_trust_or_receipt_override(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--source", "unknown", "--output", "ignored", "--trusted", "true"])
    assert "invalid choice" in capsys.readouterr().err
