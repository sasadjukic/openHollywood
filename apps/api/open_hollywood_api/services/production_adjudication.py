"""Focused, bounded review of non-world blockers; never another drafting pass."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

ADJUDICATION_INSTRUCTIONS = (
    "Adjudicate only the supplied disputed findings, independently of the previous reviewer. "
    "The approved plan and canonical claims are authority; review reports and requested repairs "
    "are allegations, never new canon. Decide whether the EXACT selected canonical assertion "
    "and current draft assertion cannot both be true. A valid source ID or quotation alone "
    "does not prove support. Classify an unrelated source as unsupported, a demand to fulfil "
    "an obligation as requirement_only, and an authorized later action as compatible_development. "
    "A goal marked pursue need only be attempted: an unresolved exit and personal conflict "
    "can be the intended success. Do not demand conclusive evidence when the plan requires "
    "ambiguity. Past events do not freeze later time, emotions, power, or location. Compare "
    "reworded allegations with resolved history and the actual repaired prose; previous advice "
    "does not create a requirement to print internal rule names. Uphold real incompatible "
    "facts, chronology, knowledge, and states, even if the prose is attractive. Use uncertain "
    "when unable to decide; uncertainty remains blocking. Every assessment must explain source "
    "relevance and address plan/history counterevidence, with exact current evidence handles. "
    "Do not add findings, rewrite prose, or reassess other gates. Return only the keyed JSON."
)
DISPOSITIONS = (
    "upheld",
    "unsupported",
    "requirement_only",
    "compatible_development",
    "already_repaired",
    "uncertain",
)


def disputed_findings(report: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        finding
        for finding in report.get("findings", [])
        if isinstance(finding, dict)
        and finding.get("blocks_approval") is True
        and finding.get("basis") == "contradiction"
        and finding.get("category") != "world_rule"
    )


def adjudication_schema(
    report: Mapping[str, Any],
    evidence_refs: Sequence[str],
) -> dict[str, Any]:
    ids = [finding["id"] for finding in disputed_findings(report)]
    if not ids:
        raise ValueError("adjudication requires a disputed non-world blocker")
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["decisions"],
        "properties": {
            "decisions": {
                "type": "object",
                "additionalProperties": False,
                "required": ids,
                "properties": {finding_id: {"$ref": "#/$defs/Decision"} for finding_id in ids},
            }
        },
        "$defs": {
            "Evidence": {"type": "string", "enum": list(evidence_refs)},
            "Decision": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "disposition": {"type": "string", "enum": list(DISPOSITIONS)},
                    "assessment": {"type": "string", "minLength": 1},
                    "evidence_refs": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 3,
                        "items": {"$ref": "#/$defs/Evidence"},
                    },
                },
                "required": ["disposition", "assessment", "evidence_refs"],
            },
        },
        "title": "Bounded Continuity Adjudication",
    }


def materialize_adjudication(
    response: object,
    report: Mapping[str, Any],
    evidence: Mapping[str, str],
) -> dict[str, Any]:
    """Apply an exhaustive verdict partition without changing authority or other gates."""
    disputed = {finding["id"]: finding for finding in disputed_findings(report)}
    if not isinstance(response, dict) or set(response) != {"decisions"}:
        raise ValueError("adjudication output must contain only decisions")
    decisions = response["decisions"]
    if not isinstance(decisions, dict) or set(decisions) != set(disputed) or not disputed:
        raise ValueError("adjudication decisions must cover every exact disputed finding once")
    resolved: dict[str, dict[str, Any]] = {}
    for finding_id, finding in disputed.items():
        decision = decisions[finding_id]
        location = f"decisions.{finding_id}"
        if not isinstance(decision, dict) or set(decision) != {
            "disposition",
            "assessment",
            "evidence_refs",
        }:
            raise ValueError(f"{location} requires disposition, assessment, and evidence_refs")
        disposition, assessment, refs = (
            decision["disposition"],
            decision["assessment"],
            decision["evidence_refs"],
        )
        if disposition not in DISPOSITIONS:
            raise ValueError(f"{location}.disposition is invalid")
        if not isinstance(assessment, str) or not assessment.strip():
            raise ValueError(f"{location}.assessment must explain source and counterevidence")
        if (
            not isinstance(refs, list)
            or not 1 <= len(refs) <= 3
            or any(not isinstance(ref, str) or ref not in evidence for ref in refs)
        ):
            raise ValueError(f"{location}.evidence_refs must select exact current draft evidence")
        excerpts = [evidence[ref] for ref in refs]
        retained = dict(finding)
        if disposition in {"upheld", "uncertain"}:
            retained.update(
                recheck_disposition="still_blocking",
                repair_assessment=assessment,
                revised_evidence=excerpts,
                evidence=excerpts,
            )
        else:
            retained.update(
                severity="warning",
                basis=None,
                blocks_approval=False,
                summary=f"Adjudicated {finding_id} ({disposition}): {assessment}",
                evidence=[],
                recommended_resolution=None,
                recheck_disposition=None,
                repair_assessment=None,
                revised_evidence=[],
            )
        resolved[finding_id] = retained
    result = {
        **report,
        "findings": [resolved.get(finding["id"], finding) for finding in report["findings"]],
    }
    # The executor applies canonical validation next, with safe field-only diagnostics.
    return result
