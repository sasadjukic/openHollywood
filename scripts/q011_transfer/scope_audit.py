"""Verify six saved critic sources and their local claim-scope decisions, without inference."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash
from scripts.q010_uncertainty_plan import digest
from scripts.q011_arrival.scope_rehearsal import pinned
from scripts.q011_arrival.sources import DATA, REPO

ROOT = DATA / "q011-position-scope-audit-2026-11-23"
PROTOCOL = "d825452f9e473d0cf62015d403d6e74748c4955d84f402c02023af6385504fbd"
SEAL = "436a8571a3e1b661f460d584df365b7a202e8b7561eaf807f1c53a1b25d3d36f"


def artifact(version: str, content: dict[str, Any], sha: str) -> dict[str, Any]:
    require(canonical_sha256(content) == sha, "scope_artifact_hash")
    return dict(version=str(UUID(version)), content=content, content_sha256=sha)


def registered(row: dict[str, Any]) -> dict[str, Any]:
    (entry,) = pinned(REPO / row["source"], row["source_sha256"])["entries"]
    s = entry["snapshot"]
    native = s["native_audit"]
    require(
        canonical_sha256(s) == entry["snapshot_sha256"]
        and s["critique"] == entry["original_critique"]
        and native == entry["original_native_audit"]
        and s["invocation"]["prompt_version"] == "61"
        and entry["invocation_id"] == s["invocation"]["invocation_id"] == row["invocation"]
        and native["candidate_version_id"] == s["draft_version_id"] == row["draft"]
        and native["current_plan_version_id"] == s["plan_version_id"] == row["plan"],
        "scope_native_binding",
    )
    sources = {a["artifact_kind"]: a for a in s["sources"]}
    docs = {}
    for role, a in (
        ("review", s["critique"]),
        ("draft", sources["scene_draft"]),
        ("plan", sources["scene_plan"]),
    ):
        docs[role] = artifact(a["version_id"], a["content"], a["content_sha256"])
    packet = dict(
        origin="isolated_ordinary_v61",
        prompt_version="61",
        invocation=row["invocation"],
        native=native,
        **docs,
    )
    http = json.loads(((REPO / row["source"]).parents[1] / "http.json").read_bytes())
    final = http["response"]["message"]["content"]
    require(digest(final.encode()) == s["invocation"]["response_sha256"], "scope_critic_final")
    lines = final.strip().splitlines()
    require(lines[0] == "```json" and lines[-1] == "```", "scope_response_fence")
    raw = json.loads("\n".join(lines[1:-1]))
    by_dimension = {score["dimension"]: score for score in raw["scores"]}
    for path, text in explanations(packet).items():
        if path.startswith("/critique/scores/"):
            dim = docs["review"]["content"]["scores"][int(path.split("/")[3])]["dimension"]
            original = by_dimension[dim]["rationale"]
        elif path.startswith("/native/assignment_comparisons/"):
            i = int(path.split("/")[3])
            original = raw["issues"][native["assignment_comparisons"][i]["raw_issue_index"]][
                "assignment_comparison"
            ]["assessment"]
        else:
            keys = path.split("/")[2:]
            if keys[0] == "check":
                keys[0] = "scene_boundary_check"
            original = raw
            for key in keys:
                original = original[int(key)] if isinstance(original, list) else original[key]
        require(text == original, "scope_authorship")
    return packet


def campaign(db: sqlite3.Connection, query: str, row: dict[str, Any]) -> dict[str, Any]:
    chosen = db.execute(query, (f"Benchmark {row['family']} %cloud",)).fetchone()
    require(chosen == (row["review"], row["invocation"], row["project"]), "scope_selection")
    linked = db.execute(
        "SELECT a.artifact_type,v.id FROM agent_invocation_inputs i JOIN artifact_versions v "
        "ON v.id=i.artifact_version_id JOIN artifacts a ON a.id=v.artifact_id "
        "WHERE i.agent_invocation_id=? AND a.project_id=? "
        "AND a.artifact_type IN ('scene_plan','scene_draft')",
        (row["invocation"], row["project"]),
    ).fetchall()
    require(
        len(linked) == 2
        and dict(linked) == {"scene_plan": row["plan"], "scene_draft": row["draft"]},
        "scope_input_versions",
    )
    docs = {}
    for role in ("review", "draft", "plan"):
        raw, sha = db.execute(
            "SELECT content,content_sha256 FROM artifact_versions WHERE id=?", (row[role],)
        ).fetchone()
        docs[role] = artifact(row[role], json.loads(raw), sha)
    (raw_settings,) = db.execute(
        "SELECT request_settings FROM agent_invocations WHERE id=?", (row["invocation"],)
    ).fetchone()
    settings = json.loads(raw_settings)
    require(str(settings["prompt_template_version"]) == "33", "scope_campaign_version")
    return dict(
        origin="benchmark_scene_production",
        prompt_version="33",
        invocation=row["invocation"],
        native={"viewpoint_audit": settings["viewpoint_audit"]},
        **docs,
    )


def packets(protocol: dict[str, Any]) -> dict[str, dict[str, Any]]:
    path = REPO / protocol["db"]
    wal = Path(str(path) + "-wal")
    require(
        file_hash(path) == protocol["db_sha256"] and (not wal.exists() or wal.stat().st_size == 0),
        "scope_snapshot",
    )
    rows = protocol["reviews"]
    require(len(rows) == len({r["review"] for r in rows}) == 6, "scope_limit")
    result = {}
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True)) as db:
        for i, row in enumerate(rows, 1):
            p = registered(row) if "source" in row else campaign(db, protocol["selector"], row)
            require(
                all(p[k]["version"] == str(UUID(row[k])) for k in ("review", "draft", "plan"))
                and p["review"]["content"]["target_artifact_version_id"] == p["draft"]["version"]
                and p["draft"]["content"]["is_complete"] is True
                and p["plan"]["content"]["id"] == p["draft"]["content"]["scene_id"],
                "scope_target",
            )
            result[f"S{i:02}"] = p
    return result


def explanations(p: dict[str, Any]) -> dict[str, str]:
    """Whole critic prose, excluding numeric scores, identifiers and copied draft excerpts."""
    c = p["review"]["content"]
    fields = {"/critique/summary": c["summary"]}
    for k, items in (
        ("strengths", c["strengths"]),
        ("scores", c["scores"]),
        ("issues", c["issues"]),
    ):
        for i, item in enumerate(items):
            path = f"/critique/{k}/{i}"
            if k == "strengths":
                fields[path] = item
            else:
                for field in ("rationale",) if k == "scores" else ("description", "recommendation"):
                    if item.get(field):
                        fields[path + "/" + field] = item[field]
    n = p["native"]
    if "check" in n:
        for k in ("achieved_state", "current_endpoint_comparison", "next_scene_comparison"):
            fields["/native/check/" + k] = n["check"][k]
        for k, check in n["assignment_checks"].items():
            fields[f"/native/assignment_checks/{k}/assessment"] = check["assessment"]
            if check.get("recommended_resolution"):
                fields[f"/native/assignment_checks/{k}/recommended_resolution"] = check[
                    "recommended_resolution"
                ]
        for i, comparison in enumerate(n.get("assignment_comparisons", [])):
            fields[f"/native/assignment_comparisons/{i}/assessment"] = comparison["assessment"]
        require(not n["assignment_repair_conditions"], "uninspected_repair_condition")
    elif n["viewpoint_audit"]["assessment"]:
        fields["/native/viewpoint_audit/assessment"] = n["viewpoint_audit"]["assessment"]
    return fields


def check_decisions(p: dict[str, Any], row: dict[str, Any]) -> None:
    fields = explanations(p)
    require(
        row["versions"] == {k: p[k]["version"] for k in ("review", "draft", "plan")}
        and set(fields) == set(row["fields"])
        and row["focus"] in fields,
        "scope_field_inventory",
    )
    for path, field in row["fields"].items():
        require(
            field["text"] == fields[path] and field["route"] in {"E", "B", "hold"},
            "scope_whole_field",
        )
    for span in row["witnesses"]:
        doc = p[span["role"]]
        text = doc["content"][span["field"]]
        require(
            span["version"] == doc["version"]
            and 0 <= span["start"] < span["end"] <= len(text)
            and text[span["start"] : span["end"]] == span["quote"],
            "scope_witness",
        )
    require({s["role"] for s in row["witnesses"]} == {"draft", "plan"}, "scope_missing_source")


def verify(root: Path = ROOT) -> dict[str, Any]:
    members = pinned(root / "audit-seal.json", SEAL)
    require(
        {p.relative_to(root / "packets").as_posix() for p in (root / "packets").iterdir()}
        == {f"S{i:02}.json" for i in range(1, 7)},
        "scope_packet_inventory",
    )
    require(all(file_hash(root / name) == sha for name, sha in members.items()), "scope_member")
    protocol = pinned(root / "protocol.json", PROTOCOL)
    cases = packets(protocol)
    decisions = json.loads((root / "scope-decisions.json").read_bytes())
    require(set(cases) == set(decisions), "scope_case_inventory")
    counts: Counter[str] = Counter()
    eligible = []
    for key, p in cases.items():
        require(encoded(p) == (root / f"packets/{key}.json").read_bytes(), "scope_packet")
        check_decisions(p, decisions[key])
        routes = [f["route"] for f in decisions[key]["fields"].values()]
        counts.update(routes)
        if "E" in routes:
            eligible.append(key)
    return dict(
        reviews=len(cases),
        fields=counts.total(),
        field_routes=dict(counts),
        reviews_with_E=eligible,
        live_calls=0,
        audit_sha256=SEAL,
    )


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))
