"""Bounded, unvalidated review evidence for diagnostics only; never prompt or story input."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.structured_output import normalize_json_document

MAX_RESPONSE_CHARS = 262_144
MAX_TEXT_CHARS = 1_000
MAX_TOTAL_TEXT_CHARS = 16_000
MAX_ITEMS = 8
MAX_SELECTED_REFERENCES = 24

_TEXT_FIELDS = frozenset(
    {
        "status",
        "verdict",
        "violation_kind",
        "subject_character_id",
        "assessment",
        "recommended_resolution",
        "recommendation",
        "anchor",
        "explanation",
        "category",
        "severity",
        "description",
        "summary",
        "basis",
        "conflict_disposition",
        "repair_action",
        "conflict_explanation",
        "rule_conflict_assessment",
        "companion_rule_assessment",
        "coverage_status",
        "coverage_assessment",
        "repair_assessment",
        "resolution_assessment",
        "disposition",
        "condition_explicitly_authorized",
        "resolution_basis",
    }
)
_REFERENCE_FIELDS = frozenset(
    {
        "draft_evidence_refs",
        "evidence_refs",
        "canonical_claim_ids",
        "canonical_source_refs",
        "world_rule_ids",
        "revised_evidence_refs",
        "revised_draft_evidence_refs",
    }
)
_OBJECT_FIELDS = frozenset({"basis_details"})
_LIST_SECTIONS = ("assignment_violations", "issues", "findings", "new_findings")
_MAP_SECTIONS = ("requirement_coverage", "prior_finding_rechecks", "decisions")


@dataclass
class _Capture:
    remaining: int = MAX_TOTAL_TEXT_CHARS
    truncated: bool = False

    def text(self, value: str) -> str:
        # Redact the complete value before truncation can split a credential.
        safe = active_secret_guard().redact_text(value)
        limit = min(MAX_TEXT_CHARS, self.remaining)
        if len(safe) > limit:
            self.truncated = True
        result = safe[:limit]
        self.remaining -= len(result)
        return result

    def scalar(self, value: object) -> object:
        if isinstance(value, str):
            return self.text(value)
        if value is None or isinstance(value, bool):
            return value
        # Do not persist arbitrary nested objects or enormous numeric literals.
        return {"unretained_type": type(value).__name__}

    def finding(self, value: object) -> object:
        if not isinstance(value, dict):
            return self.scalar(value)
        result: dict[str, object] = {}
        for key in sorted(_TEXT_FIELDS):
            if key in value:
                result[key] = self.scalar(value[key])
        for key in sorted(_REFERENCE_FIELDS):
            if key in value:
                refs = value[key]
                if isinstance(refs, list):
                    self.truncated |= len(refs) > MAX_ITEMS
                    result[key] = [self.scalar(ref) for ref in refs[:MAX_ITEMS]]
                else:
                    result[key] = self.scalar(refs)
        # Only this one known nesting level is retained.
        for key in sorted(_OBJECT_FIELDS):
            if key in value:
                child = value[key]
                if isinstance(child, dict):
                    result[key] = self.finding(
                        {k: v for k, v in child.items() if k not in _OBJECT_FIELDS}
                    )
                else:
                    result[key] = self.scalar(child)
        return result


def _object(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _candidate(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("candidate_draft"), dict):
        return _object(payload["candidate_draft"])
    assignment = _object(payload.get("assignment"))
    items = payload.get("input_artifacts", [])
    for item in items if isinstance(items, list) else []:
        record = _object(item)
        content = _object(record.get("content"))
        if (
            record.get("artifact_kind") == "scene_draft"
            and content.get("scene_id") == assignment.get("unit_id")
            and content.get("revision_number") == assignment.get("revision_number")
        ):
            return record
    return {}


def _references(value: object) -> list[tuple[str, object]]:
    """Walk only already bounded/allowlisted evidence, not arbitrary response objects."""
    refs: list[tuple[str, object]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in _REFERENCE_FIELDS:
                for ref in child if isinstance(child, list) else [child]:
                    refs.append((key, ref))
            else:
                refs.extend(_references(child))
    elif isinstance(value, list):
        for child in value:
            refs.extend(_references(child))
    return refs


def _catalog(payload: dict[str, Any], name: str, key: str) -> dict[str, dict[str, Any]]:
    values = payload.get(name, [])
    if not isinstance(values, list):
        return {}
    return {
        item[key]: item
        for item in values
        if isinstance(item, dict) and isinstance(item.get(key), str)
    }


def capture_review_failure(
    *,
    operation: str,
    response_content: str,
    request_content: str,
    input_version_ids: tuple[str, ...],
    validation_issues: tuple[dict[str, str], ...],
) -> dict[str, Any] | None:
    """Observe rejected reviews without changing validation, recovery or manuscript state."""
    if operation not in {"critique", "continuity", "continuity_adjudication"}:
        return None
    capture = _Capture()
    evidence: dict[str, Any] = {
        "schema_version": "1",
        "status": "unvalidated_review_response",
        "manuscript_defect_established": False,
        "operation": operation,
        "field_policy": "allowlisted_review_findings",
        "input_artifact_version_ids": list(input_version_ids),
    }
    try:
        payload = _object(json.loads(request_content))
        assignment = _object(payload.get("scene_assignment_contract"))
        evidence["scene_assignment"] = {
            key: capture.scalar(assignment.get(key))
            for key in ("scene_id", "point_of_view_character_id")
        }
        evidence["assignment_origin"] = capture.scalar(
            _object(payload.get("viewpoint_contract")).get("assignment_origin")
        )
        run_assignment = _object(payload.get("assignment"))
        evidence["revision_number"] = run_assignment.get("revision_number")
        candidate = _candidate(payload)
        evidence["candidate_artifact_version_id"] = capture.scalar(
            candidate.get("artifact_version_id")
        )
        if len(response_content) > MAX_RESPONSE_CHARS:
            evidence["capture_status"] = "response_too_large"
            return evidence
        try:
            raw = json.loads(normalize_json_document(response_content))
        except (ValueError, RecursionError):
            evidence["capture_status"] = "unparseable_response"
            return evidence
        if not isinstance(raw, dict):
            evidence["capture_status"] = "non_object_response"
            return evidence

        attempted: dict[str, object] = {}
        for key in ("verdict", "point_of_view_check"):
            if key in raw:
                attempted[key] = (
                    capture.finding(raw[key])
                    if key == "point_of_view_check"
                    else capture.scalar(raw[key])
                )
        for key in _LIST_SECTIONS:
            if key not in raw:
                continue
            section = raw[key]
            if isinstance(section, list):
                capture.truncated |= len(section) > MAX_ITEMS
                attempted[key] = [capture.finding(item) for item in section[:MAX_ITEMS]]
            else:
                attempted[key] = capture.scalar(section)
        for key in _MAP_SECTIONS:
            if key not in raw:
                continue
            section = raw[key]
            if isinstance(section, dict):
                capture.truncated |= len(section) > MAX_ITEMS
                attempted[key] = [
                    {"entry_id": capture.text(str(entry)), "finding": capture.finding(value)}
                    for entry, value in list(section.items())[:MAX_ITEMS]
                ]
            else:
                attempted[key] = capture.scalar(section)
        evidence["attempted_review"] = attempted

        if any(i.get("type") == "viewpoint_subject_not_other_character" for i in validation_issues):
            assigned = assignment.get("point_of_view_character_id")
            check = _object(raw.get("point_of_view_check"))
            if not assigned:
                evidence["viewpoint_failure_reason"] = "no_assigned_viewpoint"
            elif check.get("subject_character_id") == assigned:
                evidence["viewpoint_failure_reason"] = "subject_is_assigned_character"

        draft_catalog = _catalog(
            _object(candidate.get("content")), "evidence_catalog", "evidence_ref"
        )
        catalogs = {
            "canonical_claim_ids": _catalog(
                payload, "contradiction_claim_catalog", "canonical_claim_id"
            ),
            "canonical_source_refs": _catalog(payload, "canonical_source_catalog", "reference_id"),
            "world_rule_ids": _catalog(payload, "world_rule_catalog", "world_rule_id"),
        }
        refs = _references(attempted)
        capture.truncated |= len(refs) > MAX_SELECTED_REFERENCES
        resolved: list[dict[str, object]] = []
        for kind, ref in refs[:MAX_SELECTED_REFERENCES]:
            catalog = catalogs.get(kind, draft_catalog)
            match = catalog.get(ref) if isinstance(ref, str) else None
            row: dict[str, object] = {
                "field": kind,
                "reference": ref,
                "resolution": "matched_request_catalog" if match else "unresolved",
            }
            if match:
                row["source"] = {
                    key: capture.scalar(match[key])
                    for key in ("exact_excerpt", "claim", "statement", "category", "canonical_id")
                    if key in match
                }
                excerpt = match.get("exact_excerpt")
                if isinstance(excerpt, str):
                    safe_excerpt = active_secret_guard().redact_text(excerpt)
                    row["excerpt_sha256"] = hashlib.sha256(safe_excerpt.encode("utf-8")).hexdigest()
                    row["excerpt_characters"] = len(safe_excerpt)
                    row["excerpt_truncated"] = len(
                        str(_object(row["source"]).get("exact_excerpt", ""))
                    ) < len(safe_excerpt)
                    row["artifact_version_id"] = evidence["candidate_artifact_version_id"]
            resolved.append(row)
        evidence["selected_evidence"] = resolved
        evidence["capture_status"] = "captured"
        evidence["truncated"] = capture.truncated
        active_secret_guard().ensure_safe(evidence, destination="failed review diagnostics")
        return evidence
    except Exception:
        # Diagnostics are best effort. Never replace the original production failure.
        return {
            "schema_version": "1",
            "status": "unvalidated_review_response",
            "manuscript_defect_established": False,
            "operation": operation,
            "capture_status": "capture_unavailable",
        }
