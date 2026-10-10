"""Retain bounded, structurally valid classification choices during review repair.

Metadata signatures identify retained slots, not semantic equivalence. No rejected
claim prose is replayed, and preserving a choice does not certify its truth.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from open_hollywood_engine.artifacts import CritiqueIssue
from pydantic import ValidationError

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.production_critic_retry import MAX_DIAGNOSTICS, MAX_HINT_CHARS

_FIELDS = {"category", "severity", "description", "recommendation"}
_WIRE_FIELDS = {
    "draft_evidence_refs",
    "assignment_finding_ref",
    "assignment_comparison",
    "repair_test_id",
}
_SEVERITIES = {"note", "minor", "major", "blocking"}
PRESERVATION_RULE = (
    "These are structurally valid choices from your rejected review, not established story "
    "defects. Preserve each listed category, severity, evidence set and classification count "
    "while repairing the response. Issue and evidence ordering may change. Repair malformed "
    "assignment_comparison fields using the retained choice: for a repetition include its "
    "selected target; for independent craft compare every reported assignment finding. "
    "Do not silently reclassify, drop, duplicate, rename or change evidence to evade retention. "
    "Do not rewrite the underlying allegation or invent a finding to satisfy this metadata. "
    "All current findings and links must still pass normal validation. Retention applies only "
    "to this structural retry of these exact inputs, never to a new draft or a fresh review."
)


def _signature(issue: Mapping[str, Any]) -> tuple[str, str, tuple[str, ...]] | None:
    category, severity, evidence = (
        issue.get(k) for k in ("category", "severity", "draft_evidence_refs")
    )
    if (
        not isinstance(category, str)
        or not category.strip()
        or len(category) > 80
        or active_secret_guard().redact_text(category) != category
        or not isinstance(severity, str)
        or severity not in _SEVERITIES
        or not isinstance(evidence, list)
        or not 1 <= len(evidence) <= 3
        or any(not isinstance(ref, str) for ref in evidence)
        or len(set(evidence)) != len(evidence)
    ):
        return None
    return category, severity, tuple(sorted(evidence))


def classification_diagnostics(
    raw: Mapping[str, Any],
    *,
    candidate: str,
    context: str,
    evidence_catalog: Mapping[str, str],
    reported_refs: Sequence[str],
) -> list[dict[str, str]]:
    issues = raw.get("issues")
    if not isinstance(issues, list) or len(issues) > 64:
        return []
    groups: dict[tuple[str, str, tuple[str, ...]], list[tuple[int, Mapping[str, Any]]]] = {}
    for index, issue in enumerate(issues):
        if isinstance(issue, dict) and (signature := _signature(issue)) is not None:
            groups.setdefault(signature, []).append((index, issue))
    diagnostics = []
    for (category, severity, evidence), group in groups.items():
        choices = []
        for _, issue in group:
            ref = issue.get("assignment_finding_ref")
            if (
                set(issue) - (_FIELDS | _WIRE_FIELDS)
                or "assignment_finding_ref" not in issue
                or (ref is not None and (not isinstance(ref, str) or ref not in reported_refs))
                or any(e not in evidence_catalog for e in evidence)
            ):
                break
            try:
                CritiqueIssue.model_validate(
                    {
                        **{k: issue.get(k) for k in _FIELDS},
                        "evidence": [evidence_catalog[e] for e in evidence],
                    }
                )
            except ValidationError:
                break
            choices.append(ref)
        if len(choices) != len(group):
            continue  # Never retain only part of a metadata-identical group.
        hint = json.dumps(
            {
                "kind": "classification",
                "candidate": candidate,
                "context": context,
                "category": category,
                "severity": severity,
                "evidence": list(evidence),
                "choices": choices,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        if len(hint) <= MAX_HINT_CHARS:
            diagnostics.append(
                {
                    "location": f"issues.{group[0][0]}.assignment_finding_ref",
                    "type": "critic_classification_preserved",
                    "repair_hint": hint,
                }
            )
    return diagnostics[:MAX_DIAGNOSTICS]


def retained_classifications(
    failure: Mapping[str, object] | None,
    *,
    candidate: str,
    context: str,
    evidence_refs: Sequence[str],
    assignment_routes: Mapping[str, str],
) -> list[dict[str, Any]]:
    if failure is None or failure.get("error_code") != "schema_validation_failed":
        return []
    records = failure.get("validation_issues")
    if not isinstance(records, list):
        return []
    retained: list[dict[str, Any]] = []
    seen = set()
    for record in records[:MAX_DIAGNOSTICS]:
        if not isinstance(record, dict) or record.get("type") != "critic_classification_preserved":
            continue
        encoded = record.get("repair_hint")
        if not isinstance(encoded, str) or len(encoded) > MAX_HINT_CHARS:
            continue
        try:
            hint = json.loads(encoded)
        except ValueError:
            continue
        if (
            not isinstance(hint, dict)
            or set(hint)
            != {"kind", "candidate", "context", "category", "severity", "evidence", "choices"}
            or hint["kind"] != "classification"
            or hint["candidate"] != candidate
            or hint["context"] != context
        ):
            continue
        signature = _signature({**hint, "draft_evidence_refs": hint["evidence"]})
        choices = hint["choices"]
        if (
            signature is None
            or signature in seen
            or any(ref not in evidence_refs for ref in signature[2])
            or not isinstance(choices, list)
            or not 1 <= len(choices) <= 64
            or any(
                ref is not None and (not isinstance(ref, str) or ref not in assignment_routes)
                for ref in choices
            )
        ):
            continue
        seen.add(signature)
        retained.append(
            {
                "category": signature[0],
                "severity": signature[1],
                "draft_evidence_refs": list(signature[2]),
                "assignment_finding_refs": choices,
            }
        )
    return retained


def classification_drift(raw: Mapping[str, Any], retained: Sequence[Mapping[str, Any]]) -> bool:
    """Compare metadata multisets, without guessing which prose claims are equivalent."""
    issues = raw.get("issues")
    if not isinstance(issues, list):
        return bool(retained)
    for entry in retained:
        signature = _signature(entry)
        matches = [i for i in issues if isinstance(i, dict) and _signature(i) == signature]
        if any(
            "assignment_finding_ref" not in i
            or not isinstance(i["assignment_finding_ref"], (str, type(None)))
            for i in matches
        ):
            return True
        if Counter(i["assignment_finding_ref"] for i in matches) != Counter(
            entry["assignment_finding_refs"]
        ):
            return True
    return False
