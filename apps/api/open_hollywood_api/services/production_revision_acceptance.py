"""Version-bound repair targets shared by writer and critic, never new story canon."""

from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from typing import Any


def critic_repair_tests(inputs: tuple[dict[str, Any], ...], scene_id: str) -> list[dict[str, Any]]:
    drafts = {
        item["artifact_version_id"]: item["content"]
        for item in inputs
        if item.get("artifact_kind") == "scene_draft"
        and isinstance(item.get("content"), dict)
        and item["content"].get("scene_id") == scene_id
    }
    reviews = [
        item
        for item in inputs
        if item.get("artifact_kind") == "critique"
        and isinstance(item.get("content"), dict)
        and item["content"].get("target_artifact_version_id") in drafts
    ]
    reviews.sort(
        key=lambda item: drafts[item["content"]["target_artifact_version_id"]]["revision_number"]
    )
    tests: list[dict[str, Any]] = []
    prior_claims: set[str] = set()
    for review in reviews:
        content = review["content"]
        current_claims: set[str] = set()
        for index, issue in enumerate(content.get("issues", [])):
            if not isinstance(issue, dict) or (
                issue.get("severity") != "blocking"
                and not (content.get("verdict") == "revise" and issue.get("severity") == "major")
            ):
                continue
            # Only exact repeated claim/repair text is folded across review versions.
            # Preserve separate issues within the original report; never fuzzy-match prose.
            identity = json.dumps(
                [
                    issue.get(key)
                    for key in ("category", "severity", "description", "recommendation")
                ],
                ensure_ascii=False,
            )
            current_claims.add(identity)
            if identity in prior_claims:
                continue
            category = issue["category"]
            if category == "scene_assignment:point_of_view_character_id":
                criterion = (
                    "The cited access is removed, or is authorized, spoken/observable, or "
                    "inference attributable to the assigned viewpoint in context. A qualifier "
                    "alone neither proves nor disproves repair."
                )
            elif category.startswith("scene_assignment:"):
                criterion = (
                    "The scene satisfies the cited approved assignment in context; the alleged "
                    "replacement or omission no longer holds. Extra dramatization is not required."
                )
            else:
                criterion = (
                    "The cited weakness no longer holds in context; achieve the intended effect "
                    "of the requested repair, not necessarily its sample wording."
                )
            tests.append(
                {
                    "test_id": f"repair_{review['artifact_version_id']}_{index}",
                    "source_critique_version_id": review["artifact_version_id"],
                    "source_draft_version_id": content["target_artifact_version_id"],
                    "source_issue_index": index,
                    "category": category,
                    "severity": issue["severity"],
                    "claim": issue["description"],
                    "original_evidence": deepcopy(issue["evidence"]),
                    "requested_change": issue["recommendation"],
                    "accept_when": criterion,
                }
            )
        prior_claims.update(current_claims)
    return tests


def repair_checks_schema(
    tests: list[dict[str, Any]], *, assignment_routes: Mapping[str, str]
) -> dict[str, Any]:
    decision: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "status": {"type": "string", "enum": ["met", "unmet"]},
            "assessment": {"type": "string", "minLength": 1},
            "draft_evidence_refs": {
                "type": "array",
                "minItems": 1,
                "maxItems": 3,
                "items": {"$ref": "#/$defs/CriticDraftEvidenceReference"},
            },
            "current_finding_refs": {
                "type": "array",
                "maxItems": 16,
                "uniqueItems": True,
                "items": {
                    "type": "string",
                    "pattern": r"^(boundary|viewpoint|assignment:[a-z_]+|issue:(0|[1-9][0-9]*))$",
                },
                "description": (
                    "Current findings in THIS response repeating this exact original obligation: "
                    "boundary (overrun), viewpoint (violation), assignment:<anchor>, "
                    "or issue:<zero-based "
                    "issues index>. Use [] when met or none repeat it. Link only the same claim, "
                    "category and severity; different current evidence is allowed. Same category "
                    "alone is insufficient. New defects or changed severity remain independent. "
                    "Explain the equivalence in assessment. Include all linked reporting routes, "
                    "including both boundary and assignment when they repeat it. A finding may "
                    "belong to only one repair test."
                ),
            },
        },
        "required": ["status", "assessment", "draft_evidence_refs", "current_finding_refs"],
    }
    decision["properties"]["assessment"]["description"] = (
        "Assess only this original claim against the current draft. A different current "
        "defect cannot make this repair unmet. Report each independent defect through its "
        "own current finding, with its own evidence and repair; mentioning it here is not "
        "an actionable finding."
    )
    met = deepcopy(decision)
    met["properties"]["status"] = {"type": "string", "const": "met"}
    met["properties"]["current_finding_refs"] = {
        "type": "array",
        "maxItems": 0,
        "description": "A satisfied original repair has no repeated current findings: always [].",
    }
    decision["properties"]["status"] = {"type": "string", "const": "unmet"}
    definitions: dict[str, Any] = {}
    properties: dict[str, Any] = {}
    groups: dict[tuple[str, str], str] = {}
    for test in tests:
        category, severity = test["category"], test["severity"]
        group = (category, severity)
        if group not in groups:
            name = "RepairAcceptanceCheck" + (str(len(groups) + 1) if groups else "")
            groups[group] = name
            unmet = deepcopy(decision)
            links = unmet["properties"]["current_finding_refs"]
            links["description"] = (
                f"Only current {category}/{severity} findings repeating this original claim. "
                "Use [] if none repeat it; an unmet repair remains actionable without links. "
                "Same category alone is insufficient. Explain equivalence in assessment. "
                "Include every consolidated reporting route; each finding has one owner. "
                "A generic issue marked as an assignment restatement is not a separate finding."
            )
            if category.startswith("scene_assignment:"):
                eligible = [
                    ref
                    for ref, target in assignment_routes.items()
                    if target == category and severity == "blocking"
                ]
                if eligible:
                    links["items"] = {"type": "string", "enum": eligible}
                else:
                    links = {"type": "array", "maxItems": 0, "description": links["description"]}
            else:
                links["items"] = {"type": "string", "pattern": r"^issue:(0|[1-9][0-9]*)$"}
            unmet["properties"]["current_finding_refs"] = links
            definitions[name] = {"anyOf": [deepcopy(met), unmet]}
        properties[test["test_id"]] = {"$ref": f"#/$defs/{groups[group]}"}
    return {
        "type": "object",
        "additionalProperties": False,
        "$defs": definitions,
        "properties": properties,
        "required": [test["test_id"] for test in tests],
    }


def compact_repair_inputs(
    inputs: tuple[dict[str, Any], ...], *, scene_id: str, revision: int, critic: bool
) -> tuple[dict[str, Any], ...]:
    """Keep exact lineage, projecting review prose once into the shared repair packet."""
    if revision <= 0:
        return inputs
    projected = deepcopy(inputs)
    plan = next(
        (item["content"] for item in inputs if item.get("artifact_kind") == "scene_plan"),
        None,
    )
    for item in projected:
        content = item.get("content")
        if not isinstance(content, dict):
            continue
        if item.get("artifact_kind") == "story_blueprint" and plan is not None:
            plans = content.get("scene_plans")
            if (
                isinstance(plans, list)
                and len(plans) == 1
                and isinstance(plans[0], dict)
                and all(plan.get(key) == value for key, value in plans[0].items())
            ):
                content.pop("scene_plans")
        if item.get("artifact_kind") == "critique":
            item["content"] = {
                key: content[key]
                for key in ("target_artifact_version_id", "verdict")
                if key in content
            }
            if not critic:
                advice = [
                    issue
                    for issue in content.get("issues", [])
                    if isinstance(issue, dict)
                    and issue.get("severity") != "blocking"
                    and not (
                        content.get("verdict") == "revise" and issue.get("severity") == "major"
                    )
                ]
                if advice:
                    item["content"]["issues"] = deepcopy(advice)
        elif item.get("artifact_kind") == "scene_draft":
            if critic and content.get("scene_id") != scene_id:
                content.pop("prose", None)
                item["context_scope"] = "identity_only_canon_in_story_bible"
            draft_revision = content.get("revision_number")
            old_candidate = (
                content.get("scene_id") == scene_id
                and isinstance(draft_revision, int)
                and draft_revision < revision
            )
            if (
                old_candidate
                and isinstance(draft_revision, int)
                and (critic or draft_revision < revision - 1)
            ):
                # Exact old passages are in original_evidence; the current draft stays complete.
                content.pop("prose", None)
                item["context_scope"] = "repair_source_identity"
    return projected
