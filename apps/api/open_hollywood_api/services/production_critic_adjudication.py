"""Terminal adjudication of typed critic allegations; no rewriting or rescoring."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from open_hollywood_engine.workflows.production_contracts import ADJUDICABLE_CRITIC_CATEGORIES

from open_hollywood_api.persistence.secret_policy import active_secret_guard

CRITIC_ADJUDICATION_INSTRUCTIONS = (
    "Independently adjudicate only the supplied critic allegations against the approved "
    "assignment and complete current scene. Previous reviews and repair advice are allegations, "
    "not canon or votes. For each exact issue, return upheld, unsupported, already_repaired, "
    "or uncertain, an assessment, and 1-3 distinct current evidence handles. Explain the "
    "approved permission/obligation, contextual evidence and counterevidence, and original "
    "repair condition. Uphold actual wrong viewpoint or unauthorized private access; "
    "the focal character's interpretations, observable behavior and spoken disclosures are "
    "allowed. A qualifier alone neither proves nor repairs a violation: inspect who can know "
    "the assertion in context and any specifically authorized perspective shift. Generic "
    "literary style does not authorize another character's private thoughts. For assignment "
    "claims, distinguish a missing/incompatible planned turn from one realized indirectly; "
    "do not demand extra explicitness or perform later scenes early. Use already_repaired "
    "only when history and current evidence establish repair, unsupported when the allegation "
    "was unfounded, and uncertain when evidence cannot settle it. Upheld and uncertain block. "
    "Do not add findings, alter scores, rewrite prose, or reassess continuity. Return keyed JSON."
)
CRITIC_DISPOSITIONS = ("upheld", "unsupported", "already_repaired", "uncertain")


def disputed_critic_issues(report: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        f"issue_{index}": issue
        for index, issue in enumerate(report["issues"])
        if issue["severity"] == "blocking" and issue["category"] in ADJUDICABLE_CRITIC_CATEGORIES
    }


def critic_adjudication_schema(
    report: Mapping[str, Any], evidence_refs: Sequence[str]
) -> dict[str, Any]:
    ids = list(disputed_critic_issues(report))
    if not ids:
        raise ValueError("critic adjudication requires eligible blocking issues")
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["decisions"],
        "properties": {
            "decisions": {
                "type": "object",
                "additionalProperties": False,
                "required": ids,
                "properties": {key: {"$ref": "#/$defs/Decision"} for key in ids},
            }
        },
        "$defs": {
            "Decision": {
                "type": "object",
                "additionalProperties": False,
                "required": ["disposition", "assessment", "evidence_refs"],
                "properties": {
                    "disposition": {"type": "string", "enum": list(CRITIC_DISPOSITIONS)},
                    "assessment": {"type": "string", "minLength": 1},
                    "evidence_refs": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 3,
                        "uniqueItems": True,
                        "items": {"type": "string", "enum": list(evidence_refs)},
                    },
                },
            }
        },
        "title": "Bounded Critic Adjudication",
    }


def materialize_critic_adjudication(
    response: object,
    report: Mapping[str, Any],
    evidence: Mapping[str, str],
) -> dict[str, Any]:
    disputed = disputed_critic_issues(report)
    if not isinstance(response, dict) or set(response) != {"decisions"}:
        raise ValueError("critic adjudication must contain only decisions")
    decisions = response["decisions"]
    if not disputed or not isinstance(decisions, dict) or set(decisions) != set(disputed):
        raise ValueError("decisions must cover every exact disputed issue once")
    replacements: dict[str, dict[str, Any]] = {}
    for key, issue in disputed.items():
        decision = decisions[key]
        if not isinstance(decision, dict) or set(decision) != {
            "disposition",
            "assessment",
            "evidence_refs",
        }:
            raise ValueError("decision requires disposition, assessment, and evidence_refs")
        disposition, assessment, refs = (
            decision["disposition"],
            decision["assessment"],
            decision["evidence_refs"],
        )
        if (
            disposition not in CRITIC_DISPOSITIONS
            or not isinstance(assessment, str)
            or not assessment.strip()
        ):
            raise ValueError("decision requires a valid disposition and a nonempty assessment")
        if (
            not isinstance(refs, list)
            or not 1 <= len(refs) <= 3
            or any(not isinstance(ref, str) or ref not in evidence for ref in refs)
            or len(set(refs)) != len(refs)
        ):
            raise ValueError("decision evidence must select distinct exact current draft handles")
        if disposition in {"unsupported", "already_repaired"}:
            replacements[key] = {
                **issue,
                "severity": "note",
                "description": (
                    f"Adjudicated {key} ({disposition}): "
                    + active_secret_guard().redact_text(assessment)
                ),
                "evidence": [evidence[ref] for ref in refs],
                "recommendation": "No revision required for this adjudicated allegation.",
            }
    # Keep upheld/uncertain allegations, independent issues, scores and the rubric verdict intact.
    # At the cap the existing graph permits a non-blocking revise/reject recommendation.
    return {
        **report,
        "summary": (
            f"Terminal critic adjudication: {len(replacements)} supplied findings released; "
            f"{len(disputed) - len(replacements)} retained. Prior review: {report['summary']}"
        ),
        "issues": [
            replacements.get(f"issue_{i}", issue) for i, issue in enumerate(report["issues"])
        ],
    }
