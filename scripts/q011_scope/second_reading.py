"""Replay a second, score-masked coverage reading of the six Q011 explanations."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_be.rehearsal import FIXTURES, read

from . import coverage_transfer as first

READINGS = FIXTURES / "pristine_lure_second_readings.json"
SEALED = FIXTURES / "pristine_lure_second_decisions.json"
PACKET_SHA = "f0dfc5cf21b5556c87f991585336e9b311c042efc09fe91561b5802d533a9732"
SEAL_SHA = "73c20eb3b343f881c8af92960f04f30d6d7254157f7dba352dbfec8a11ee5de2"


def packet() -> tuple[dict[str, Any], dict[str, str]]:
    """Build the reader's view using only the source freeze and the masked explanations."""
    freeze = first.frozen()
    require(file_hash(first.PACKET) == first.PACKET_SHA, "second_reader_packet_source")
    original = read(first.PACKET)
    drafts = {d["version"]: d["spans"] for d in freeze["drafts"].values()}
    order = sorted(original, key=lambda k: canonical_sha256(["pristine-lure-reader-two", k]))
    index = {f"R{i:02}": key for i, key in enumerate(order, 1)}
    rows = {}
    for alias, key in index.items():
        row = original[key]
        require(
            set(row) == {"claim", "draft_version", "citations", "reason"}
            and key == canonical_sha256(row)[:16],
            "second_reader_fields",
        )
        rows[alias] = dict(**row, draft_spans=drafts[row["draft_version"]])
    return dict(
        rubric=freeze["rubric"], plan=freeze["plan"], source_uses=freeze["source_uses"], rows=rows
    ), index


def prejoin() -> dict[str, Any]:
    """Score the independent annotations before opening any other reader's annotations."""
    view, _ = packet()
    require(canonical_sha256(view) == PACKET_SHA, "second_reader_packet_identity")
    raw = READINGS.read_bytes()
    freeze, annotations = first.frozen(), json.loads(raw)
    require(annotations.keys() == view["rows"].keys(), "second_reader_inventory")
    rows = {}
    for alias, explanation in view["rows"].items():
        primary = annotations[alias]
        fields = {"uses", "asserts", "basis", "decision"}
        require(
            set(primary) == fields | {"alternatives"}
            and all(set(a) == fields for a in primary["alternatives"]),
            "second_reader_interpretation_fields",
        )
        scored = []
        for reading in [primary, *primary["alternatives"]]:
            require(
                bool(reading["basis"].strip()) and reading["decision"] in ("pass", "flag"),
                "second_reader_interpretation",
            )
            result = first.assess(explanation, reading["uses"], reading["asserts"], freeze)
            scored.append(dict(declared=reading["decision"], **result))
        rows[alias] = dict(primary=scored[0], alternatives=scored[1:])
    return dict(
        packet_sha256=PACKET_SHA,
        source_freeze_sha256=first.FREEZE_SHA,
        annotations_sha256=sha256(raw).hexdigest(),
        rows=rows,
    )


def interpretations(note: dict[str, Any], scores: dict[str, Any]) -> list[dict[str, Any]]:
    """Keep extra assertions and alternate readings visible alongside their decisions."""
    return [
        dict(assertions=sorted(n["asserts"]), witnesses=sorted(n.get("uses", note["uses"])), **s)
        for n, s in zip(
            [note, *note["alternatives"]], [scores["primary"], *scores["alternatives"]], strict=True
        )
    ]


def sealed_json(path: Path, digest: str) -> dict[str, Any]:
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, "reader_comparison_seal")
    rows: dict[str, Any] = json.loads(raw)
    return rows


def compare() -> dict[str, Any]:
    receipt = prejoin()
    require(sealed_json(SEALED, SEAL_SHA) == receipt, "second_reader_seal")
    earlier = first.masked_decisions()
    require(canonical_sha256(earlier) == first.DECISIONS_SHA, "first_reader_seal")
    first_notes = sealed_json(first.READINGS, first.READINGS_SHA)
    second_notes = sealed_json(READINGS, receipt["annotations_sha256"])
    view, index = packet()
    freeze = first.frozen()
    cases = {
        (freeze["claim_scopes"][c["scope"]], freeze["drafts"][c["history"]]["version"]): k
        for k, c in freeze["cases"].items()
    }
    rows = {}
    for alias, key in index.items():
        left = interpretations(first_notes[key], earlier[key])
        right = interpretations(second_notes[alias], receipt["rows"][alias])
        row = view["rows"][alias]
        case = cases[(row["claim"], row["draft_version"])]
        rows[case] = dict(
            masked_alias=alias,
            first=left,
            second=right,
            primary_reader_agreement=left[0]["decision"] == right[0]["declared"],
            alternate_changes_first=any(s["decision"] != left[0]["decision"] for s in left[1:]),
            alternate_changes_second=any(s["declared"] != right[0]["declared"] for s in right[1:]),
        )
    require(rows.keys() == freeze["cases"].keys(), "second_reader_case_join")
    return dict(live_calls=0, reader_two_seal=SEAL_SHA, rows=rows)


if __name__ == "__main__":
    print(json.dumps(compare(), indent=2))
