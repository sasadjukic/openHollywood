"""Explicit current-scene obligations; semantic judgments remain with the critic."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

MANDATORY_ANCHORS = ("turning_point", "outcome")
COMPLIANCE_CRAFT_RULE = (
    "Apply assignment compliance in both directions: when the complete assigned facts and "
    "all supported applicable conditions hold, select met with recommended_resolution=null. "
    "A preferred dramatic purpose, catalyst, stronger connection or staging cannot make a "
    "fulfilled obligation unmet. Missing facts or violated explicit/canonical relationships "
    "still require unmet; actions and indirect narration remain valid fulfillment evidence. "
    "Evaluate genuine craft defects separately against the rubric, with current evidence "
    "and the required assignment comparison. Do not invent a finding reference for a met "
    "check. An optional alternative mechanism is a preference, not proof of a craft defect. "
    "If retained in issues, label its recommendation Optional and use note/minor severity; "
    "never fold it into mandatory native or restatement repairs. Keep that optional scope "
    "during structural retries. Before choosing the final verdict, check which actual "
    "unresolved defect warrants revision. Use pass when only optional preferences remain; "
    "neither those preferences nor their effect on craft scores alone justify revise/reject. "
    "Genuine independent craft defects may still warrant revise/reject even with met "
    "assignment checks; do not automatically waive minor issues or demote real defects. "
    "Keep the summary, comparisons, recommendations and verdict consistent with this "
    "distinction. Do not add output fields."
)
REQUIREMENT_BASIS_RULE = (
    "In each assignment assessment/comparison, assess required facts, temporal order/immediacy "
    "and causation separately. Name the assignment field or applicable canonical version/field "
    "and quote the words requiring each relation; compare it with draft evidence. Scope "
    "permissions to the named relation: optional causation leaves required order intact; "
    "required order does not require causation. If no source requires a relation, say so; its "
    "absence is not a missing fact. 'And', mention order, genre or preferred dramatic purpose "
    "cannot add one. Check every remaining requirement before met; an exemption cannot satisfy "
    "another obligation. Applicable canon still binds. Actions and indirect narration are "
    "valid evidence; literal plan wording is unnecessary. Do not add output fields."
)
MINIMUM_REPAIR_RULE = (
    "Carry those same distinctions into every recommended_resolution and restatement "
    "recommendation. Repair only the missing fact or violated required relation, preserving "
    "fulfilled facts and the scene endpoint. Do not add a trigger to an order-only repair, or "
    "replace required immediate onset with later onset. Require completed action only when "
    "assigned or required by applicable canon; a decision or attempt does not require "
    "completion. Unassigned staging, motivation and craft preferences stay explicitly optional, "
    "outside mandatory repairs and acceptance conditions."
)
OBLIGATION_RULE = (
    "Complete assignment_checks independently for every supplied turning_point and outcome. "
    "Each check requires status (met/unmet), assessment (1-600 nonblank characters comparing "
    "that exact obligation with the whole current draft), 1-3 distinct current "
    "draft_evidence_refs, and recommended_resolution (null when met; a targeted 1-600 "
    "character repair when unmet). In assessment, compare the complete assigned fact or "
    "state, including every explicit condition, with what the cited draft establishes. "
    "Select met only when that whole obligation holds. Performing the named action, "
    "noticing the relevant object or serving a similar dramatic purpose cannot substitute "
    "for different or missing required content. Use broader context to interpret the draft, "
    "never to replace an absent or contradictory required fact. Select unmet if any "
    "required condition is absent or contradicted, even when the scene achieves the intended "
    "dramatic effect. For absence, cite the closest relevant passage and explain what is "
    "missing. Actions, embodied reactions and indirect narration are valid evidence when "
    "they establish the complete assigned fact; literal plan wording is not required. "
    "An intentional attempt can establish a decision without an explicit decision sentence "
    "or promise to continue afterward. Judge only what this assignment requires; do not add "
    "conditions or demand more explicit prose. A failed "
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
