"""Offline evidence-coverage transfer to six saved explanations from The Pristine Lure."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_be.rehearsal import FIXTURES, read
from scripts.wading_path_sol_versions.evidence_coverage import coverage_findings

from . import regression

FREEZE = FIXTURES / "pristine_lure_coverage_freeze.json"
FREEZE_SHA = "1ed474f1baa3759f7d5b7f94154c799d044f99d7b6610c9fb675f921b1e16773"
PACKET = FIXTURES / "pristine_lure_coverage_masked.json"
READINGS = FIXTURES / "pristine_lure_coverage_readings.json"
PACKET_SHA = "e476d12b3fdf770f5717b2121ae0fa36a2ef30f53066e63835562088ca763932"
READINGS_SHA = "3019ad9a72411b2f8cca4fe6acaa3850840f4af7ab07341a75a2ecdb48eb5b53"
DECISIONS_SHA = "edb0c5963de2af7b1b840cbdb0ddb8b5e171ee28695f0187f34b6a3589cdbd64"


def frozen() -> dict[str, Any]:
    require(file_hash(FREEZE) == FREEZE_SHA, "coverage_transfer_freeze")
    data: dict[str, Any] = read(FREEZE)
    return data


def member_index(archive: Path) -> dict[str, str]:
    manifest = archive / "capture-manifest.json"
    require(file_hash(manifest) == regression.SEAL, "coverage_transfer_archive")
    members: dict[str, str] = read(manifest)
    return members


def masked_packet(archive: Path = regression.ARCHIVE) -> tuple[dict[str, Any], dict[str, str]]:
    """Allowlist the request and generation receipt. Prior scores and gold stay unopened."""
    freeze = frozen()
    members = member_index(archive)
    require(freeze["archive_sha256"] == regression.SEAL, "coverage_transfer_archive")

    def sealed(name: str) -> Any:
        path = archive / "capture" / name
        require(file_hash(path) == members[name], "coverage_transfer_member")
        return read(path)

    packet, index = {}, {}
    for case, cell in freeze["cases"].items():
        request = sealed(f"run/requests/{case}-B-generation.json")
        user = json.loads(request["input"][1]["content"])
        docs = {d["identity"]: d for d in user["documents"]}
        plan, draft = docs["scene_plan"], docs["assessment_draft"]
        history = freeze["drafts"][cell["history"]]
        claim = freeze["claim_scopes"][cell["scope"]]
        prose = draft["structured_content"]["prose"]
        spans = history["spans"]
        require(
            user["claim"]["text"] == claim
            and draft["version"] == history["version"]
            and plan["version"] == freeze["plan"]["version"]
            and draft["structured_content"]["is_complete"] is True
            and text_hash(prose) == history["prose_sha256"]
            and prose.rsplit("\n\n", 1)[-1]
            == draft["structured_content"]["ending_excerpt"]
            == spans["closing"]["quote"],
            "coverage_transfer_request",
        )
        for s in spans.values():
            require(prose[s["start"] : s["end"]] == s["quote"], "coverage_transfer_span")
        for s in freeze["plan"]["spans"].values():
            field = plan["structured_content"][s["field"].removeprefix("/")]
            require(field[s["start"] : s["end"]] == s["quote"] == field, "coverage_transfer_plan")
        refs = {r: (doc, ptr) for r, doc, ptr in docs["registry"]["whole_field_locations"]}
        require(
            refs
            == {
                "E0233": ("scene_plan", "/outcome"),
                "E0229": ("scene_plan", "/exit_state"),
                "E0883": ("assessment_draft", "/prose"),
                "D01": ("assessment_draft", "/ending_excerpt"),
            },
            "coverage_transfer_registry",
        )
        path = cell["terminal_path"]
        require(members[path] == cell["terminal_sha256"], "coverage_transfer_terminal")
        terminal = sealed(path)
        body = json.loads(terminal["body"])
        require(terminal["http_status"] == 200 and body["status"] == "completed", "ineligible")
        (answer,) = (
            json.loads(part["text"])["assessments"]["Q011-scope"]
            for item in body["output"]
            if item["type"] == "message"
            for part in item["content"]
            if part["type"] == "output_text"
        )
        require(set(answer["evidence"]) <= refs.keys(), "coverage_transfer_ref")
        row = dict(
            claim=claim,
            draft_version=history["version"],
            citations=answer["evidence"],
            reason=answer["reason"],
        )
        key = canonical_sha256(row)[:16]
        require(key not in packet, "duplicate_masked_row")
        packet[key], index[key] = row, case
    return dict(sorted(packet.items())), index


def assess(
    row: dict[str, Any], uses: dict[str, str], assertions: dict[str, str], freeze: dict[str, Any]
) -> dict[str, Any]:
    """Evaluate the anchored reading against source spans and the compound claim."""
    (history,) = (d for d in freeze["drafts"].values() if d["version"] == row["draft_version"])
    (scope,) = (s for s, claim in freeze["claim_scopes"].items() if claim == row["claim"])
    spans = freeze["plan"]["spans"] | history["spans"]
    require(uses.keys() <= spans.keys(), "coverage_transfer_wrong_witness")
    require(
        all(q and q in row["reason"] for group in (uses, assertions) for q in group.values()),
        "coverage_transfer_reason_anchor",
    )
    used = {k for k in uses if set(freeze["source_uses"][k]).intersection(row["citations"])}
    grounded_gap = "gap" in used
    placement = "placement" in used
    open_ending = {"gap", "placement"}.isdisjoint(spans)
    adequate = {
        "drawn": {"draw", "approach"} <= used,
        "at_cut": placement,
        "away_at_cut": grounded_gap,
        "open_at_cut": {"closing", "approach"} <= used and open_ending,
        "depicts_placement": placement and "closing" in used,
        "no_depiction": "closing" in used
        and (grounded_gap or (open_ending and "approach" in used)),
    }
    answers = {
        "position": {"at_cut", "away_at_cut", "open_at_cut"},
        "depiction": {"depicts_placement", "no_depiction"},
    }
    findings = coverage_findings(
        {"attraction": {"drawn"}, scope: answers[scope]}, set(assertions), adequate
    )
    findings.extend("uncited_" + k for k in sorted(uses.keys() - used))
    findings.extend("missing_" + k for k in sorted({"plan_outcome", "plan_exit"} - used))
    return dict(decision="flag" if findings else "pass", findings=findings)


def masked_decisions() -> dict[str, Any]:
    require(
        file_hash(PACKET) == PACKET_SHA and file_hash(READINGS) == READINGS_SHA,
        "coverage_transfer_annotation_seal",
    )
    packet, readings, freeze = read(PACKET), read(READINGS), frozen()
    require(
        packet.keys() == readings.keys() and len(packet) == len(freeze["cases"]),
        "coverage_transfer_annotation_inventory",
    )
    results = {}
    for key, row in packet.items():
        require(
            key == canonical_sha256(row)[:16]
            and set(row) == {"reason", "claim", "draft_version", "citations"},
            "coverage_transfer_mask",
        )
        r = readings[key]
        primary = assess(row, r["uses"], r["asserts"], freeze)
        alternatives = [assess(row, r["uses"], a["asserts"], freeze) for a in r["alternatives"]]
        results[key] = dict(
            primary=primary,
            alternatives=alternatives,
            sensitive=any(a["decision"] != primary["decision"] for a in alternatives),
        )
    return results


def rehearse(archive: Path = regression.ARCHIVE) -> dict[str, Any]:
    decisions = masked_decisions()
    require(canonical_sha256(decisions) == DECISIONS_SHA, "coverage_transfer_prejoin_decisions")
    packet, index = masked_packet(archive)
    require(packet == read(PACKET), "coverage_transfer_packet_binding")
    historical = regression.replay(archive)
    cases = {
        r["cell"]: r
        for group in ("original_pair", "clear_controls")
        for r in historical[group]["cases"]
    }
    require({case + "-B" for case in index.values()} == cases.keys(), "coverage_transfer_case_join")
    rows = {}
    for key, case in index.items():
        old = cases[case + "-B"]
        rows[case] = dict(
            masked_id=key,
            **decisions[key],
            historical={k: old[k] for k in ("returned", "judgment", "evidence")},
        )
    return dict(
        live_calls=0,
        source_scope_sha256=FREEZE_SHA,
        masked_decisions_sha256=DECISIONS_SHA,
        rows=rows,
    )


if __name__ == "__main__":
    print(json.dumps(rehearse(), indent=2))
