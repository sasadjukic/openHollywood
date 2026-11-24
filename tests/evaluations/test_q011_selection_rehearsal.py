"""Check the active whole field and its evidence obligation using two sealed v61 reviews."""

from __future__ import annotations

import json
import socket
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, NoReturn

import pytest
from open_hollywood_engine.evaluations.review_evidence import EvidenceError

from scripts.q011_arrival.sources import REPO
from scripts.q011_transfer import scope_audit as audit
from scripts.q011_transfer import selection_rehearsal as rehearsal


@pytest.fixture(scope="module")
def reviews() -> dict[str, rehearsal.Review]:
    if not audit.ROOT.is_dir():
        pytest.skip("requires the private version-bound review archives")
    return rehearsal.load_reviews()


@pytest.fixture(scope="module")
def rows(reviews: dict[str, rehearsal.Review]) -> dict[str, dict[str, Any]]:
    return {u: rehearsal.select(reviews[case], u) for u, (case, _, _) in rehearsal.FIELDS.items()}


def test_offline_replay_reads_only_original_critic_and_sealed_scope(
    rows: dict[str, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    protocol = audit.ROOT / "protocol.json"
    allowed = {audit.ROOT / name for name in ("audit-seal.json", "scope-decisions.json")}
    allowed.add(protocol)
    for case, source in zip(
        ("S01", "S02"), json.loads(protocol.read_bytes())["reviews"][:2], strict=True
    ):
        export = REPO / source["source"]
        allowed.update(
            (audit.ROOT / f"packets/{case}.json", export, export.parents[1] / "http.json")
        )
    initial = {path: path.read_bytes() for path in allowed}
    seen = set()
    read = Path.read_bytes

    def archive_only(path: Path) -> bytes:
        assert path in allowed
        seen.add(path)
        return read(path)

    def offline(*args: object, **kwargs: object) -> NoReturn:
        pytest.fail("the read-only selection rehearsal must remain offline")

    monkeypatch.setattr(Path, "read_bytes", archive_only)
    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    monkeypatch.setattr(socket.socket, "connect_ex", offline)
    replay = rehearsal.rehearse()
    assert replay["live_calls"] == 0 and replay["selections"] == list(rows.values())
    assert seen == allowed
    assert initial == {p: read(p) for p in allowed}


def test_motion_and_standing_remain_distinct(rows: dict[str, dict[str, Any]]) -> None:
    moving, standing = rows["Q010"], rows["Q011"]
    for key in ("versions", "source_sha256", "review_invocation"):
        assert moving[key] == standing[key]
    assert moving["work_sha256"] != standing["work_sha256"]
    assert moving["pointer"].endswith("/achieved_state")
    assert standing["pointer"].endswith("/current_endpoint_comparison")
    assert moving["text"] == (
        "Elias has moved past the circle of shoes and is entering the threshold of the monolith."
    )
    assert standing["text"] == (
        "The achieved state matches the outcome ('drawn to the entrance') and exit state "
        "('stands at the threshold') defined in the scene plan."
    )
    for row, unit, verbatim, expected, other in (
        (moving, "Q010", "is entering the threshold of the monolith", "entering", "standing"),
        (standing, "Q011", "stands at the threshold", "standing", "entering"),
    ):
        assert (row["route"], row["status"], row["active_units"]) == (
            "E",
            "pending_assessment",
            [unit],
        )
        target = row["position_target"]
        assert (
            target["subject"] == "Elias"
            and target["instant"] == "Scene one's final narrated instant."
        )
        assert row["text"][target["start"] : target["end"]] == target["literal"] == verbatim
        obligation = row["brief"]["evidence_obligation"]
        assert f"establishes, rules out, or leaves open Elias {expected}" in obligation
        assert obligation.endswith(target["landmark"] + " at the scene cut.")
        assert other not in json.dumps(row["brief"])
    assert "past the circle of shoes" in moving["components"][0]
    assert "drawn to the entrance" in standing["components"][0]
    assert [e["pointer"] for e in moving["evidence_locations"]] == ["/prose"]
    assert [e["pointer"] for e in standing["evidence_locations"]] == [
        "/prose",
        "/input_artifacts/1/content/outcome",
        "/input_artifacts/1/content/exit_state",
    ]


def test_textual_coverage_uses_default_brief(rows: dict[str, dict[str, Any]]) -> None:
    row = rows["Q012"]
    assert row["source_sha256"] == rows["Q010"]["source_sha256"]
    assert (row["route"], row["status"], row["active_units"]) == (
        "B",
        "pending_assessment",
        ["Q012"],
    )
    assert row["text"] == (
        "The draft stops at the threshold; it does not advance into the building or introduce "
        "the disembodied voice of Julian Vane reserved for scene 2."
    )
    assert "position_target" not in row and "Elias" not in json.dumps(row["brief"])
    assert "Identify the draft observation" not in row["brief"]["evidence_obligation"]
    assert row["observation_basis"] == "absence_in_complete_scope"
    locations = {e["ref"]: e for e in row["evidence_locations"]}
    assert locations["E0883"]["pointer"] == "/prose"
    assert locations["E0883"]["document_version"] == row["versions"]["draft"]
    assert locations["E0865"]["pointer"] == "/scene_boundary/next_scene/turning_point"
    assert "voice reserved for scene two" in row["brief"]["question"]


def test_held_whole_field_and_repeat(
    reviews: dict[str, rehearsal.Review], rows: dict[str, dict[str, Any]]
) -> None:
    held = rows["Q016"]
    assert held["pointer"] == rows["Q011"]["pointer"]
    assert held["review_invocation"] != rows["Q011"]["review_invocation"]
    assert (
        "haunted by the card's existence" in held["text"]
        and "implied by her attempt" in held["text"]
    )
    assert (held["route"], held["status"], held["brief"], held["active_units"]) == (
        "hold",
        "hold",
        None,
        [],
    )
    assert "position_target" not in held and "work_sha256" not in held
    for row in rows.values():
        assert row["assessment_result"] is None and row["completion_receipt"] is None
        assert row["factual_support"] == "unassessed"
        assert row["writer_dispatch_authorized"] is row["model_input"] is False
    assert rehearsal.select(reviews["S01"], "Q010") == rows["Q010"]


def test_rejects_unregistered_or_misbound_field(reviews: dict[str, rehearsal.Review]) -> None:
    elias, elara = reviews["S01"], reviews["S02"]
    with pytest.raises(EvidenceError, match="selection_unregistered"):
        rehearsal.select(elias, "Q999")
    with pytest.raises(EvidenceError, match="selection_versions"):
        rehearsal.select(elara, "Q011")
    wrong_source = replace(elias, source=elara.source)
    with pytest.raises(EvidenceError, match="selection_source_versions"):
        rehearsal.select(wrong_source, "Q010")
    wrong_versions = dict(elias.versions, draft=elara.versions["draft"])
    with pytest.raises(EvidenceError, match="selection_source_versions"):
        rehearsal.select(
            replace(
                elias, versions=wrong_versions, ruling=dict(elias.ruling, versions=wrong_versions)
            ),
            "Q011",
        )
    changed = deepcopy(elias.ruling)
    fields = changed["fields"]
    fields["/native/check/achieved_state"]["text"] = fields[
        "/native/check/current_endpoint_comparison"
    ]["text"]
    with pytest.raises(EvidenceError, match="selection_whole_field"):
        rehearsal.select(replace(elias, ruling=changed), "Q010")


@pytest.mark.parametrize(
    ("unit", "original", "substitute"),
    [
        ("Q010", "is entering the threshold of the monolith", "is standing at the threshold"),
        ("Q011", "stands at the threshold", "is entering the threshold of the monolith"),
    ],
)
def test_substituted_predicate_rejected(
    reviews: dict[str, rehearsal.Review], unit: str, original: str, substitute: str
) -> None:
    context = reviews["S01"].source.inventory_work.context
    field = next(f for f in context.report_fields if f.field_id == unit)
    stmt = next(s for s in context.statements if s.unit_id == unit)
    changed = field.text.replace(original, substitute)
    with pytest.raises(EvidenceError, match="selection_position_predicate"):
        rehearsal.choice_for(field.model_copy(update={"text": changed}), stmt)
