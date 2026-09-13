"""Version-bound repair targets shared by writer and critic, never new story canon."""

from __future__ import annotations

import json
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


def repair_checks_schema(tests: list[dict[str, Any]]) -> dict[str, Any]:
    decision = {
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
        },
        "required": ["status", "assessment", "draft_evidence_refs"],
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "$defs": {"RepairAcceptanceCheck": decision},
        "properties": {
            test["test_id"]: {"$ref": "#/$defs/RepairAcceptanceCheck"} for test in tests
        },
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
