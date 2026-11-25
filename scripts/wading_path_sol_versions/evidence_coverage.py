"""Rehearse claim-specific evidence coverage on operator readings of saved explanations."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.ordinary_v61_capture import file_hash
from scripts.wading_path_be.rehearsal import FIXTURES, read
from scripts.wading_path_three_claims.coverage import PASSAGES
from scripts.wading_path_visit_position import regression as endpoint

from . import regression

EXPECTED = FIXTURES / "wading_path_evidence_coverage_expected.json"
EXPECTED_SHA = "315a415cbd71136ba38814b85140959fb495666db0f04ef568d5d0bd69a25d30"
READINGS = FIXTURES / "wading_path_evidence_coverage_readings.json"
READINGS_SHA = "ec50f55494521ff7ffca8169b17fe1ddf35e0336bff254c655255d404f3e27ff"

SCOPE_ASSERTIONS = {
    "narration": {"no_account", "account_of_visit"},
    "event": {"no_visit", "visit_occurred", "open_visit"},
    "endpoint": {"short_at_cut"},
}


def coverage_findings(
    obligations: Mapping[str, set[str]], assertions: set[str], adequate: Mapping[str, bool]
) -> list[str]:
    """Check every asserted proposition and require an answer to each active obligation."""
    require(bool(assertions) and assertions <= adequate.keys(), "unknown_assertion")
    findings = [f"insufficient_evidence_for_{a}" for a in sorted(assertions) if not adequate[a]]
    for scope, allowed in obligations.items():
        if assertions.isdisjoint(allowed):
            findings.append(f"{scope}_scope_unanswered")
    return findings


def coverage(scope: str, assertions: set[str], used: set[str], available: set[str]) -> list[str]:
    """Check the propositions the explanation advances, using only the witnesses it invokes."""
    require(scope in SCOPE_ASSERTIONS and bool(assertions), "unknown_claim_scope_or_empty_reading")
    require(used <= available, "witness_outside_selected_draft")
    adequate = {
        "short_at_cut": "gap" in used,
        "no_visit": "exclusion" in used,
        "visit_occurred": "visit" in used,
        "account_of_visit": "visit" in used,
        "open_visit": "gap" in used and available.isdisjoint({"visit", "exclusion"}),
        "no_account": "account" in used
        and "visit" not in available
        and ("exclusion" in used if "exclusion" in available else {"approach", "gap"} <= used),
    }
    return coverage_findings({scope: SCOPE_ASSERTIONS[scope]}, assertions, adequate)


def source_ranges(
    location: dict[str, Any], version: str, gold: dict[str, Any]
) -> dict[str, tuple[int, int]]:
    """Bind each reviewed proposition to its own version of the complete cited draft."""
    prose: str = location["quote"]
    history = next((h for h in gold["endings"].values() if h["version"] == version), None)
    require(
        history is not None
        and location["document_version"] == version
        and text_hash(prose) == history["prose_sha256"],
        "coverage_source_version",
    )
    gap = gold["fixed_stop"]
    start, end = gap["start"], gap["end"]
    require(prose[start:end] == gap["quote"], "coverage_gap")
    ranges = {
        "account": (0, len(prose)),
        "approach": (PASSAGES["entry"][0], PASSAGES["housing"][1]),
        "gap": (start, end),
    }
    for name in ("exclusion", "visit"):
        entry = gold["endings"][name]
        if version == entry["version"]:
            require(prose[end:] == "\n\n" + entry["append_paragraph"], "coverage_retrospective")
            ranges[name] = (end + 2, len(prose))
    return ranges


def assess(
    scope: str,
    reason: str,
    reading: dict[str, dict[str, str]],
    ranges: Mapping[str, tuple[int, int]],
) -> dict[str, Any]:
    uses, assertions = reading["uses"], reading["asserts"]
    require(
        set(reading) == {"uses", "asserts"}
        and all(
            anchor and anchor in reason for group in (uses, assertions) for anchor in group.values()
        ),
        "coverage_reason_anchor",
    )
    findings = coverage(scope, set(assertions), set(uses), set(ranges))
    return dict(
        scope=scope,
        decision="flag" if findings else "pass",
        findings=findings,
        used_ranges={k: ranges[k] for k in uses},
    )


def rehearse() -> dict[str, Any]:
    require(file_hash(EXPECTED) == EXPECTED_SHA, "coverage_expectations_changed")
    frozen = read(EXPECTED)
    require(
        file_hash(READINGS) == READINGS_SHA
        and all(file_hash(FIXTURES / name) == sha for name, sha in frozen["sources"].items()),
        "coverage_input_changed",
    )
    readings = read(READINGS)
    gold = read(FIXTURES / "wading_path_narration_event_gold.json")
    rows = read(FIXTURES / "wading_path_sol_versions_observed.json")["rows"]
    rows["S2-B"] = read(FIXTURES / "wading_path_measured_stop_observed.json")["rows"]["S2-B"]
    require(
        rows.keys() == frozen["saved"].keys()
        and readings.keys() == rows.keys() | frozen["authored"].keys(),
        "coverage_inventory",
    )

    paired, prior = regression.verified(regression.ARCHIVE), endpoint.verified(endpoint.ARCHIVE)
    locations = read(paired / "operator/cited-locations.json")
    locations["S2"] = read(prior / "operator/cited-locations.json")["S2"]
    endpoint_claim = read(prior / "source/rehearsal-gold.json")["claims"]["at_cut"]
    scopes = {
        gold["claims"]["narrated"]: "narration",
        gold["claims"]["reached"]: "event",
        endpoint_claim: "endpoint",
    }
    sources = {}
    saved, authored = {}, {}
    for name, row in rows.items():
        case = name.split("-")[0]
        capture = prior if name == "S2-B" else paired
        (terminal,) = (capture / "run/output").glob(f"*-{name}-generation-outcome.json")
        body = json.loads(read(terminal)["body"])
        (delivery,) = (
            json.loads(part["text"])["assessments"]["A001"]
            for item in body["output"]
            if item["type"] == "message"
            for part in item["content"]
            if part["type"] == "output_text"
        )
        expected = frozen["saved"][name]
        version = row["draft_version"]
        require(
            expected["terminal_sha256"] == row["generation_terminal_sha256"] == file_hash(terminal)
            and version == expected["draft_version"]
            and delivery["evidence"] == row["citations"] == ["E1420"]
            and delivery["reason"] == row["reason"]
            and delivery["support"] == row["returned"]
            and row["claim"] in scopes,
            "coverage_capture_binding",
        )
        scope = scopes[row["claim"]]
        ranges = source_ranges(locations[case]["E1420"], version, gold)
        sources[name] = scope, ranges
        result = assess(scope, delivery["reason"], readings[name], ranges)
        require(result["decision"] == expected["expected"], "saved_coverage_mismatch")
        saved[name] = dict(
            **result, returned=row["returned"], judgment=row["judgment"], evidence=row["evidence"]
        )
    for name, fixture in frozen["authored"].items():
        scope, ranges = sources[fixture["source"]]
        result = assess(scope, fixture["reason"], readings[name], ranges)
        require(result["decision"] == fixture["expected"], "authored_coverage_mismatch")
        authored[name] = result
    return dict(
        expected_sha256=EXPECTED_SHA,
        readings_sha256=READINGS_SHA,
        live_calls=0,
        paired={k: v for k, v in saved.items() if k != "S2-B"},
        endpoint=saved["S2-B"],
        authored=authored,
    )


if __name__ == "__main__":
    print(json.dumps(rehearse(), indent=2))
