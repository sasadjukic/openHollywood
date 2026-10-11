"""Explicit current-scene obligations; semantic judgments remain with the critic."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

MANDATORY_ANCHORS = ("turning_point", "outcome")
OBLIGATION_RULE = (
    "Complete assignment_checks independently for every supplied turning_point and outcome. "
    "Each check requires status (met/unmet), assessment (1-600 nonblank characters comparing "
    "that exact obligation with the whole current draft), 1-3 distinct current "
    "draft_evidence_refs, and recommended_resolution (null when met; a targeted 1-600 "
    "character repair when unmet). For absence, cite the closest relevant passage and "
    "explain what is missing. Actions, embodied reactions and indirect realization count; "
    "an intentional attempt can establish a decision without an explicit decision sentence "
    "or promise to continue afterward. Judge only what this assignment requires. A failed "
    "turn does not prove a failed outcome: each unmet judgment needs its own comparison. "
    "A met outcome, no_overrun, high score or satisfied historical repair cannot substitute "
    "for a met turning point. Report these two obligations only in assignment_checks, not "
    "assignment_violations; every unmet check becomes a blocker. Other assignment anchors "
    "retain their existing routes. Missing or malformed checks are review errors, never "
    "evidence of a manuscript defect."
)


class AssignmentCheckError(ValueError):
    """A malformed review is not a missing story obligation."""

    def __init__(self, location: str, message: str) -> None:
        super().__init__(message)
        self.location = location


def assignment_checks_schema(assignment: Mapping[str, Any]) -> dict[str, Any]:
    """Require exactly the populated obligations from the immutable current plan."""
    properties: dict[str, Any] = {}
    for anchor in MANDATORY_ANCHORS:
        if not assignment.get(anchor):
            continue
        variants = []
        for status in ("met", "unmet"):
            fields = {
                "status": {"type": "string", "const": status},
                "assessment": {"type": "string", "minLength": 1, "maxLength": 600},
                "draft_evidence_refs": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 3,
                    "uniqueItems": True,
                    "items": {"$ref": "#/$defs/CriticDraftEvidenceReference"},
                },
                "recommended_resolution": (
                    {"type": "null"}
                    if status == "met"
                    else {"type": "string", "minLength": 1, "maxLength": 600}
                ),
            }
            variants.append(
                {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": fields,
                    "required": list(fields),
                }
            )
        properties[anchor] = {"anyOf": variants}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties),
    }


def validated_assignment_checks(
    value: object, assignment: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    """Validate coverage and shape only; the executor resolves exact evidence identity."""
    expected = {anchor for anchor in MANDATORY_ANCHORS if assignment.get(anchor)}
    if not isinstance(value, dict) or set(value) != expected:
        raise AssignmentCheckError(
            "assignment_checks",
            f"provide exactly the applicable mandatory checks: {sorted(expected)}",
        )
    fields = {"status", "assessment", "draft_evidence_refs", "recommended_resolution"}
    for anchor, check in value.items():
        location = f"assignment_checks.{anchor}"
        if not isinstance(check, dict) or set(check) != fields:
            raise AssignmentCheckError(location, "provide status, assessment, evidence and repair")
        if check["status"] not in ("met", "unmet"):
            raise AssignmentCheckError(f"{location}.status", "select met or unmet")
        assessment = check["assessment"]
        if not isinstance(assessment, str) or not assessment.strip() or len(assessment) > 600:
            raise AssignmentCheckError(f"{location}.assessment", "use 1-600 nonblank characters")
        repair = check["recommended_resolution"]
        if (check["status"] == "met" and repair is not None) or (
            check["status"] == "unmet"
            and (not isinstance(repair, str) or not repair.strip() or len(repair) > 600)
        ):
            raise AssignmentCheckError(
                f"{location}.recommended_resolution",
                "use null when met or a targeted 1-600 character repair when unmet",
            )
    return value
