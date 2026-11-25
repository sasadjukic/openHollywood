"""Replay the observed model pairs, test the scope contrast and check prefix applicability."""

from __future__ import annotations

import json
import shutil
import socket
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_sol_versions import omission_audit, regression

FIXTURE = Path(__file__).parents[1] / "fixtures/wading_path_sol_versions_observed.json"


def test_portable_pairs() -> None:
    observed = json.loads(FIXTURE.read_bytes())
    assert file_hash(FIXTURE) == "1e742af64f6b5a38242733540cae4485e571fb7f568058ea05ffbccca828bd22"
    assert observed["approval_sha256"] == regression.APPROVAL
    assert observed["evidence_decisions_sha256"] == regression.EVIDENCE_SEAL
    rows = observed["rows"]
    expected = {
        "SE": ("uncertain", "unsupported", "fail", "fail"),
        "SN": ("unsupported", "unsupported", "pass", "fail"),
        "XE": ("unsupported", "unsupported", "pass", "pass"),
        "XN": ("unsupported", "unsupported", "pass", "pass"),
        "VE": ("supported", "supported", "pass", "pass"),
        "VN": ("supported", "supported", "pass", "pass"),
    }
    assert len(rows) == len({r["generation_terminal_sha256"] for r in rows.values()}) == 12
    for case, grades in expected.items():
        for arm in ("61", "62"):
            row = rows[f"{case}-{arm}"]
            assert tuple(row[k] for k in ("gold", "returned", "judgment", "evidence")) == grades
            assert row["model"] == f"gpt-6.{arm[-1]}-sol"
            assert row["citations"] == ["E1420"] and row["draft_version"] in row["reason"]


@pytest.fixture(scope="module")
def archive() -> Path:
    if not regression.ARCHIVE.is_dir():
        pytest.skip("requires the private paired comparison archive")
    return regression.ARCHIVE


@pytest.fixture(scope="module")
def audit(archive: Path) -> dict[str, Any]:
    observed = json.loads(FIXTURE.read_bytes())
    read = Path.read_bytes

    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("network attempted in historical replay")

    def local(path: Path) -> bytes:
        assert path.is_relative_to(archive)
        return read(path)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(Path, "read_bytes", local)
        patch.setattr(socket, "getaddrinfo", offline)
        patch.setattr(socket.socket, "connect", offline)
        patch.setattr(socket.socket, "connect_ex", offline)
        replay = regression.replay(archive)
        result = omission_audit.audit(archive)
    assert replay["slots"] == 24 and replay["observed_joint_passes"] == {"61": 4, "62": 4}
    assert replay["live_calls"] == result["live_calls"] == 0
    assert result["observations"] == observed
    return result


def test_scope_and_stable_endpoint(archive: Path, audit: dict[str, Any]) -> None:
    rows = audit["request_audit"]
    assert all(
        r["claim_predicates"] == r["evidence_predicates"] == ["observed_event"]
        for r in rows.values()
    )
    assert all(
        r["brief"] == rows["SN-61"]["brief"] and r["unresolved_qualifiers"] == []
        for r in rows.values()
    )
    assert all(
        r["source_scopes"]
        == [{"coverage": "complete_fields", "evidence_refs": ["E1420"], "role": "draft"}]
        for r in rows.values()
    )
    loc = json.loads((archive / "capture/operator/cited-locations.json").read_bytes())
    stop = loc["SE"]["E1420"]["quote"]
    assert (
        stop == loc["SN"]["E1420"]["quote"]
        and len(stop) == 4945
        and stop.endswith("and stayed there.")
    )
    for n, e in (("XN", "XE"), ("VN", "VE")):
        assert loc[n]["E1420"] == loc[e]["E1420"] and loc[e]["E1420"]["quote"].startswith(
            stop + "\n\n"
        )
    assert "neither Elias nor Maya had ever been closer" in loc["XE"]["E1420"]["quote"][4947:]
    assert (
        "had reached the master breaker panel housing together"
        in loc["VE"]["E1420"]["quote"][4947:]
    )


def test_reasoning_and_cache_records(audit: dict[str, Any]) -> None:
    rows = audit["request_audit"]
    assert len(rows) == 12
    assert (
        len({r["system_sha256"] for r in rows.values()})
        == len({r["schema_sha256"] for r in rows.values()})
        == 1
    )
    for r in rows.values():
        assert r["input_roles"] == ["system", "user"] and r["input_item_types"] == [None, None]
        assert (
            r["store"] is False
            and r["reasoning"] == {"effort": "high"}
            and r["truncation"] == "disabled"
        )
        assert set(r["request_fields"]) == {
            "background",
            "input",
            "max_output_tokens",
            "model",
            "reasoning",
            "service_tier",
            "store",
            "stream",
            "text",
            "truncation",
        }
        assert r["input_transformations"] == [] and not r["has_cache_diagnostics"]
        assert r["cached_read_tokens"] == 0 and r["cache_write_tokens"] > 0
    assert sum(r["encrypted_reasoning_items"] for r in rows.values()) == 7
    assert all(
        r["system_chars"] == 2595 and r["shared_user_chars"] == 801
        for r in audit["within_history_prefix"].values()
    )


@pytest.mark.parametrize(
    ("member", "replacement"),
    [
        (
            "run/output/19-SE-62-generation-outcome.json",
            "run/output/20-SE-61-generation-outcome.json",
        ),
        ("run/requests/SN-61-generation.json", "run/requests/SE-61-generation.json"),
        ("run/output/02-SN-62-input_count-outcome.json", None),
        ("operator/cited-locations.json", None),
        ("run/sealed-evidence-decisions.json", None),
        ("source/narration-event-gold.json", None),
    ],
)
def test_damaged_archive(
    archive: Path, tmp_path: Path, member: str, replacement: str | None
) -> None:
    staged = tmp_path / "archive"
    shutil.copytree(archive / "capture", staged / "capture")
    shutil.copyfile(archive / "capture-manifest.json", staged / "capture-manifest.json")
    target = staged / "capture" / member
    if replacement is None:
        target.unlink()
    else:
        shutil.copyfile(staged / "capture" / replacement, target)
    with pytest.raises(EvidenceError, match="sol_versions_archive_members"):
        regression.replay(staged)
