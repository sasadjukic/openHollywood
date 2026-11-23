"""Verify the local source admission for transfer beyond the Q011 scene family."""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from contextlib import closing
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash
from scripts.q011_arrival.scope_rehearsal import pinned
from scripts.q011_arrival.sources import DATA, REPO

ROOT = DATA / "q011-transfer-admission-2026-11-23"
SEAL = "a8183e25993df790fa96453cd927e39146d7a2affb71147bdb8f401d3e66ba43"


def version(row: sqlite3.Row) -> dict[str, Any]:
    content = json.loads(row["content"])
    require(canonical_sha256(content) == row["content_sha256"], "transfer_saved_content")
    return dict(version=str(UUID(row["id"])), content_sha256=row["content_sha256"], content=content)


def saved_sources(protocol: dict[str, Any]) -> dict[str, Any]:
    source = REPO / protocol["db"]
    wal = Path(str(source) + "-wal")
    require(
        file_hash(source) == protocol["db_sha256"]
        and (not wal.exists() or wal.stat().st_size == 0),
        "transfer_snapshot_drift",
    )
    rows = {}
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro&immutable=1", uri=True)) as db:
        db.row_factory = sqlite3.Row
        for number in range(3, 9):
            family = f"OH-V01-{number:03}"
            drafts = db.execute(
                "SELECT p.id AS project, v.* FROM projects p JOIN artifacts a ON a.project_id=p.id "
                "JOIN artifact_versions v ON v.artifact_id=a.id WHERE p.name LIKE ? "
                "AND a.artifact_type='scene_draft' AND v.version_number=1 "
                "ORDER BY v.created_at,v.id",
                (f"Benchmark {family} %cloud",),
            )
            draft = next(r for r in drafts if json.loads(r["content"]).get("is_complete") is True)
            (plan,) = db.execute(
                "SELECT v.* FROM agent_invocation_inputs i JOIN artifact_versions v "
                "ON v.id=i.artifact_version_id JOIN artifacts a ON a.id=v.artifact_id "
                "WHERE i.agent_invocation_id=? AND a.artifact_type='scene_plan' AND a.project_id=?",
                (draft["created_by_invocation_id"], draft["project"]),
            )
            d, p = version(draft), version(plan)
            require(
                d["content"]["scene_id"] == p["content"]["id"]
                and p["content"]["scene_number"] == 1,
                "transfer_saved_plan",
            )
            rows[family] = dict(
                project=str(UUID(draft["project"])),
                creating_invocation=str(UUID(draft["created_by_invocation_id"])),
                draft=d,
                plan=p,
            )
    return rows


def check_family(rows: dict[str, tuple[dict[str, Any], dict[str, Any]]]) -> None:
    labels = dict(
        approach="uncertain",
        arrival="supported",
        terminal_gap="unsupported",
        earlier_gap="uncertain",
    )
    require(set(rows) == set(labels), "transfer_family_coverage")
    base = rows["approach"][0]
    prose = base["draft"]["content"]["prose"]
    gap = rows["terminal_gap"][1]["witnesses"]["gap"]["quote"]
    renewed = rows["earlier_gap"][1]["witnesses"]["renewed_motion"]["quote"]
    arrival = rows["arrival"][1]["witnesses"]["arrival"]["quote"]
    endings = dict(
        approach=prose,
        arrival=prose + " " + arrival,
        terminal_gap=" ".join((prose, renewed, gap)),
        earlier_gap=" ".join((prose, gap, renewed)),
    )
    for state, (packet, decision) in rows.items():
        d = packet["draft"]
        text = d["content"]["prose"]
        require(
            packet == base | {"draft": d}
            and d["content"]["is_complete"] is True
            and decision["label"] == labels[state]
            and text == endings[state],
            "transfer_timing_or_source",
        )
        for witness in decision["witnesses"].values():
            start, end = witness["start"], witness["end"]
            require(
                witness["draft_version"] == d["version"]
                and 0 <= start < end <= len(text)
                and text[start:end] == witness["quote"],
                "transfer_witness",
            )


def verify(root: Path = ROOT) -> dict[str, Any]:
    members = pinned(root / "admission-seal.json", SEAL)
    assets = {name: pinned(root / name, sha) for name, sha in members.items()}
    protocol = assets["protocol.json"]
    saved = saved_sources(protocol)
    screened = assets["saved-source-screen.json"]
    require(set(saved) == set(screened), "transfer_saved_inventory")
    for family, source in saved.items():
        item = screened[family]
        require(
            item == source | {"disposition": "hold", "reason": item["reason"]} and item["reason"],
            "transfer_saved_screen",
        )
    groups: dict[str, dict[str, tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(dict)
    versions = set()
    cases = assets["gold.json"]["cases"]
    require(
        {p.name for p in (root / "packets").iterdir()} == {key + ".json" for key in cases},
        "transfer_packet_inventory",
    )
    for key, decision in cases.items():
        filename = f"packets/{key}.json"
        packet = assets[filename]
        require(
            set(packet) == {"family", "origin", "draft", "plan", "context", "claim"}
            and packet["origin"] == "authored_diagnostic"
            and members[filename] == decision["packet_sha256"]
            and packet["claim"] == decision["claim"]
            and packet["plan"]["version"] == decision["plan_version"]
            and packet["family"] == decision["family"],
            "transfer_packet_binding",
        )
        for role in ("context", "plan", "draft"):
            require(
                canonical_sha256(packet[role]["content"]) == packet[role]["content_sha256"],
                "transfer_authored_content",
            )
        versions.add(packet["draft"]["version"])
        groups[packet["family"]][decision["state"]] = packet, decision
    require(len(groups) == 2 and len(cases) == len(versions) == 8, "transfer_authored_inventory")
    for rows in groups.values():
        check_family(rows)

    prior = assets["prior-input-screen.json"]
    phrases = [
        phrase.casefold()
        for name, rows in groups.items()
        for phrase in (
            name,
            rows["approach"][1]["witnesses"]["first_fact"]["quote"],
            rows["terminal_gap"][1]["witnesses"]["gap"]["quote"],
        )
    ]
    inputs = prior["checked_generation_bodies"]
    for name, sha in inputs.items():
        messages = pinned(DATA / name, sha)["input"]
        text = "\n".join(m["content"] for m in messages).casefold()
        require(not any(phrase in text for phrase in phrases), "transfer_prior_input_match")
    return dict(
        admission_sha256=SEAL,
        saved_screened=len(saved),
        saved_admitted=0,
        authored_families=list(groups),
        admitted_cases=len(cases),
        prior_generation_bodies=len(inputs),
        live_calls=0,
    )


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
