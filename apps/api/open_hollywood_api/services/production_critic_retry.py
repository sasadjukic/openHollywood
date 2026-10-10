"""Bounded structural link diagnostics; rejected review prose is never retry input."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

MAX_HINT_CHARS = 500
MAX_DIAGNOSTICS = 12
_SEVERITIES = {"note", "minor", "major", "blocking"}


def critic_link_diagnostics(
    raw: Mapping[str, Any],
    *,
    candidate_version_id: str,
    tests: Sequence[Mapping[str, Any]],
    assignment_routes: Mapping[str, str],
    hard_findings: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Inspect metadata after rejection, without producing a corrected critique."""
    diagnostics: list[dict[str, str]] = []

    def add(location: str, hint: dict[str, Any]) -> None:
        encoded = json.dumps(
            {"candidate": candidate_version_id, **hint}, separators=(",", ":"), sort_keys=True
        )
        if len(encoded) <= MAX_HINT_CHARS and len(diagnostics) < MAX_DIAGNOSTICS:
            diagnostics.append(
                {
                    "location": location,
                    "type": "critic_link_structure_invalid",
                    "repair_hint": encoded,
                }
            )

    findings = {
        ref: finding for finding in hard_findings for ref in finding["_current_finding_refs"]
    }
    reported = [ref for ref in assignment_routes if ref in findings]
    issues = raw.get("issues", [])
    if isinstance(issues, list):
        for index, issue in enumerate(issues[:64]):
            if (
                not isinstance(issue, dict)
                or not isinstance(issue.get("severity"), str)
                or issue["severity"] not in _SEVERITIES
            ):
                continue
            severity = issue["severity"]
            ref = issue.get("assignment_finding_ref")
            allowed = [None, *reported] if severity == "blocking" else [None]
            if "assignment_finding_ref" not in issue or ref not in allowed:
                add(
                    f"issues.{index}.assignment_finding_ref",
                    {"kind": "restatement", "severity": severity, "allowed_refs": allowed},
                )
            # Nonblocking findings cannot be restatements. These facts apply if
            # the reviewer retains them as independent craft with a null ref.
            if (ref is None or severity != "blocking") and isinstance(issue.get("category"), str):
                findings[f"issue:{index}"] = {
                    "category": issue["category"],
                    "severity": severity,
                    "_current_finding_refs": [f"issue:{index}"],
                }

    checks = raw.get("repair_checks")
    if not isinstance(checks, dict):
        return diagnostics
    known_tests = {test["test_id"]: test for test in tests}
    owners: dict[str, list[str]] = {}
    for test_id, check in checks.items():
        if test_id not in known_tests or not isinstance(check, dict):
            continue
        refs = check.get("current_finding_refs")
        if isinstance(refs, list):
            for ref in refs[:16]:
                if isinstance(ref, str) and ref in findings:
                    owners.setdefault(ref, []).append(test_id)
    for test_id, test in known_tests.items():
        check = checks.get(test_id)
        if not isinstance(check, dict) or check.get("status") not in ("met", "unmet"):
            continue
        refs = check.get("current_finding_refs")
        selected = [ref for ref in refs if isinstance(ref, str)] if isinstance(refs, list) else []
        eligible = (
            [
                ref
                for ref, finding in findings.items()
                if (finding["category"], finding["severity"])
                == (test["category"], test["severity"])
            ]
            if check["status"] == "unmet"
            else []
        )
        required = list(
            dict.fromkeys(
                route
                for ref in selected
                if ref in findings
                for route in findings[ref]["_current_finding_refs"]
            )
        )
        missing = [ref for ref in required if ref not in selected]
        competing = list(
            dict.fromkeys(
                owner for ref in required for owner in owners.get(ref, []) if owner != test_id
            )
        )
        if (
            not isinstance(refs, list)
            or len(refs) > 16
            or len(selected) != len(refs)
            or len(set(selected)) != len(selected)
            or any(ref not in eligible for ref in selected)
            or missing
            or competing
        ):
            add(
                f"repair_checks.{test_id}.current_finding_refs",
                {
                    "kind": "repair_links",
                    "status": check["status"],
                    "allowed_refs": eligible[:16],
                    "choices_truncated": len(eligible) > 16,
                    "required_refs": required[:16],
                    "missing_refs": missing[:16],
                    "competing_tests": competing[:2],
                },
            )
    return diagnostics


def critic_link_directive(
    issue: Mapping[str, Any],
    *,
    candidate_version_id: str,
    tests: Sequence[Mapping[str, Any]],
    assignment_routes: Mapping[str, str],
) -> dict[str, Any] | None:
    """Decode only known structural fields, bound again to the exact retry inputs."""
    encoded = issue.get("repair_hint")
    if not isinstance(encoded, str) or len(encoded) > MAX_HINT_CHARS:
        return None
    try:
        hint = json.loads(encoded)
    except ValueError:
        return None
    if not isinstance(hint, dict) or hint.get("candidate") != candidate_version_id:
        return None
    location = issue.get("location")
    if not isinstance(location, str):
        return None

    def refs(key: str, *, nullable: bool = False, craft: bool = False) -> bool:
        values = hint.get(key)
        return (
            isinstance(values, list)
            and len(values) <= 16
            and all(
                (nullable and value is None)
                or (
                    isinstance(value, str)
                    and (
                        value in assignment_routes
                        or (craft and re.fullmatch(r"issue:(0|[1-9][0-9]{0,3})", value) is not None)
                    )
                )
                for value in values
            )
        )

    if hint.get("kind") == "restatement":
        if (
            re.fullmatch(r"issues\.(0|[1-9][0-9]{0,3})\.assignment_finding_ref", location) is None
            or not isinstance(hint.get("severity"), str)
            or hint["severity"] not in _SEVERITIES
            or not refs("allowed_refs", nullable=True)
            or (hint["severity"] != "blocking" and hint["allowed_refs"] != [None])
        ):
            return None
        return {
            "location": location,
            "action": "Nonblocking issues require null. For a blocking issue use null for "
            "independent craft, or an exact reported assignment ref only for the same defect. "
            "Do not escalate severity to make a link legal.",
            "reported_severity": hint["severity"],
            "allowed_assignment_finding_refs": hint["allowed_refs"],
        }
    test = next(
        (t for t in tests if location == f"repair_checks.{t['test_id']}.current_finding_refs"), None
    )
    if (
        hint.get("kind") != "repair_links"
        or test is None
        or hint.get("status") not in ("met", "unmet")
        or any(
            not refs(key, craft=True) for key in ("allowed_refs", "required_refs", "missing_refs")
        )
        or not isinstance(hint.get("choices_truncated"), bool)
        or not isinstance(hint.get("competing_tests"), list)
        or len(hint["competing_tests"]) > 2
        or any(
            not isinstance(key, str) or key not in {t["test_id"] for t in tests}
            for key in hint["competing_tests"]
        )
        or not set(hint["missing_refs"]).issubset(hint["required_refs"])
        or (hint["status"] == "met" and hint["allowed_refs"])
    ):
        return None
    return {
        "location": location,
        "action": "Met checks require []. For an unmet check, link only the same original "
        "claim with its exact category and severity; otherwise leave that finding independent. "
        "An unmet check may use []. A retained link must cover every consolidated route with "
        "one owner. Do not rename or escalate a different defect merely to match this repair.",
        "expected_category": test["category"],
        "expected_severity": test["severity"],
        "reported_status": hint["status"],
        "eligible_refs_if_independent_craft_is_retained": hint["allowed_refs"],
        "eligible_refs_truncated": hint["choices_truncated"],
        "all_routes_for_selected_findings": hint["required_refs"],
        "missing_routes": hint["missing_refs"],
        "competing_original_test_ids": hint["competing_tests"],
    }
