"""Offline registered-source export, immutable reuse and protected boundaries."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from open_hollywood_api.services import assessment_compact_presentation as service
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_engine.secrets import SecretLeakError

from scripts import assessment_compact_presentation as cli
from tests.api.test_assessment_completion import offline, prepare, snapshot  # noqa: F401


@pytest.mark.parametrize("mode", ["initial", "post", "contrast", "post17"])
def test_authenticated_export_reuse_and_verify(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    fixture = prepare(tmp_path, monkeypatch, mode)
    dest = tmp_path / "compact"
    before = snapshot(fixture.intake.parent)
    assert service.prepare(fixture.intake, dest) == "created"
    exported = snapshot(dest)
    assert service.prepare(fixture.intake, dest) == "reused"
    assert service.verify(fixture.intake, dest) == "verified_zero_calls"
    assert before == snapshot(fixture.intake.parent) and exported == snapshot(dest)
    presentation = json.loads((dest / "presentation-01.json").read_bytes())
    assert presentation["contract"] == "assessment-intake-presentation-2"
    assert not presentation["live_authorized"]
    assert json.loads((dest / "manifest.json").read_bytes())["state"] == "diagnostic_inputs_only"


@pytest.mark.parametrize("failure", ["extra", "missing", "changed", "local", "linked", "protected"])
def test_conflicting_or_unsafe_outputs_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    fixture = prepare(tmp_path, monkeypatch)
    dest = tmp_path / "compact"
    if failure == "protected":
        with pytest.raises(ValueError):
            service.prepare(fixture.intake, fixture.intake.parent)
        return
    service.prepare(fixture.intake, dest)
    if failure == "extra":
        (dest / "extra").write_text("x")
    elif failure == "missing":
        (dest / "manifest.json").unlink()
    elif failure == "changed":
        (dest / "presentation-01.json").write_text("{}")
    elif failure == "local":
        (dest / "local-provenance.json").write_text("{}")
    else:
        # Avoid OS-specific symlink privileges; exercise the same linked-path refusal branch.
        unlinked = storage._unlinked

        def reject(path: Path) -> Path:
            if path.name == "presentation-01.json":
                raise ValueError("linked")
            return unlinked(path)

        monkeypatch.setattr(storage, "_unlinked", reject)
    before = snapshot(dest)
    with pytest.raises(ValueError):
        service.prepare(fixture.intake, dest)
    with pytest.raises(ValueError):
        service.verify(fixture.intake, dest)
    assert snapshot(dest) == before


def test_drift_during_final_recheck_leaves_no_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = prepare(tmp_path, monkeypatch)
    dest = tmp_path / "compact"
    collect = storage._collect
    calls = 0

    def drift(path: Path) -> storage._Collected:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise ValueError("source drift")
        return collect(path)

    monkeypatch.setattr(storage, "_collect", drift)
    with pytest.raises(ValueError):
        service.prepare(fixture.intake, dest)
    assert dest.is_dir() and not (dest / "manifest.json").exists()


def test_cli_has_no_live_option_and_redacts_bad_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        cli.main(["run"])
    capsys.readouterr()
    assert (
        cli.main(
            [
                "verify",
                "--intake",
                str(tmp_path / "private-title"),
                "--output",
                str(tmp_path / "out"),
            ]
        )
        == 2
    )
    assert "private-title" not in capsys.readouterr().out


def test_secret_guard_checks_rendered_output_before_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = prepare(tmp_path, monkeypatch)

    class Guard:
        def ensure_safe(self, text: str, *, destination: str) -> None:
            if "diagnostic presentation version 2" in text:
                raise SecretLeakError("authored test marker", "$")

    monkeypatch.setattr(storage, "active_secret_guard", lambda: Guard())
    dest = tmp_path / "compact"
    with pytest.raises(SecretLeakError):
        service.prepare(fixture.intake, dest)
    assert not dest.exists()
