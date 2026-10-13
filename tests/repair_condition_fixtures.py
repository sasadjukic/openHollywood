"""Explicitly port historical simulated reviews; these citations are not model evidence."""

from __future__ import annotations

import json
from collections.abc import Sequence
from copy import deepcopy
from typing import Any

from open_hollywood_api.services.production_model_executor import (
    _critic_repair_sources,
    _Execution,
    _revision_acceptance_audit,
    _scene_boundary_audit,
)
from open_hollywood_engine.models import ModelRequest


def condition_fixture(raw: dict[str, Any], sources: Sequence[dict[str, str]]) -> dict[str, Any]:
    result = deepcopy(raw)
    prior = {entry["repair_ref"]: entry for entry in result.get("assignment_repair_conditions", [])}
    records = []

    def record(ref: str, slot: dict[str, Any], field: str) -> None:
        if slot.get(field) is None and ref in prior:
            records.append(prior[ref])
            return
        source = next(
            (
                s
                for s in sources
                if s["source_path"] == f"/content/{ref.removeprefix('assignment:')}"
            ),
            sources[0] if sources else None,
        )
        if source is None:
            return  # Preserve malformed fixtures, rather than invent an artifact.
        records.append(
            {
                "repair_ref": ref,
                "conditions": [
                    {
                        "condition": slot.get(field),
                        "source_refs": [
                            {
                                "source_ref": source["source_ref"],
                                "exact_quote": source["text"][:600],
                            }
                        ],
                        "support_assessment": (
                            "Simulated fixture annotation; not evidence of semantic support."
                        ),
                    }
                ],
            }
        )
        if field in slot:
            slot[field] = None

    checks = result.get("assignment_checks")
    if isinstance(checks, dict):
        for anchor, check in checks.items():
            if isinstance(check, dict) and check.get("status") == "unmet":
                record(f"assignment:{anchor}", check, "recommended_resolution")
    violations = result.get("assignment_violations")
    if isinstance(violations, list):
        for item in violations:
            if isinstance(item, dict):
                record(f"assignment:{item.get('anchor')}", item, "recommended_resolution")
    pov = result.get("point_of_view_check")
    if isinstance(pov, dict) and pov.get("status") == "violation":
        record("viewpoint", pov, "recommended_resolution")
    issues = result.get("issues")
    if isinstance(issues, list):
        for issue in issues:
            if isinstance(issue, dict) and issue.get("assignment_finding_ref") is not None:
                ref = issue["assignment_finding_ref"]
                owner = next((r for r in records if r["repair_ref"] == ref), None)
                # Explicitly move historical simulated additions into their native set.
                # Boundary-only restatements now reuse the application policy.
                advice = issue.get("recommendation")
                if (
                    owner is not None
                    and advice is not None
                    and advice not in [c["condition"] for c in owner["conditions"]]
                ):
                    condition = deepcopy(owner["conditions"][0])
                    condition["condition"] = advice
                    owner["conditions"].append(condition)
                issue["recommendation"] = None
    result["assignment_repair_conditions"] = records
    return result


def condition_fixture_for_request(raw: dict[str, Any], request: ModelRequest) -> dict[str, Any]:
    payload = json.loads(request.messages[-1].content)
    if payload.get("assignment", {}).get("operation") != "critique":
        return raw
    return condition_fixture(raw, payload["repair_source_catalog"])


def fixture_boundary_audit(raw: dict[str, Any], execution: _Execution) -> dict[str, object]:
    return _scene_boundary_audit(
        condition_fixture(raw, _critic_repair_sources(execution)), execution
    )


def fixture_revision_audit(raw: dict[str, Any], execution: _Execution) -> dict[str, Any]:
    return _revision_acceptance_audit(
        condition_fixture(raw, _critic_repair_sources(execution)), execution
    )
