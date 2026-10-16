"""Bounded native-fulfillment projection; no database or provider dependencies."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

HANDOFF_POLICY_VERSION = "1"
HANDOFF_PROMPT_VERSION = "61"
SUPPORTED_CRITIC_VERSIONS = frozenset({"59", "61"})
MAX_PACKET_BYTES = 16_384
FULFILLMENT_POLICY = (
    "These are the latest critic's findings about this exact draft, not new canon. "
    "Preserve the existing expression in the cited passages when repairing unrelated "
    "defects; do not add explicit restatement just to emphasize fulfillment. If a "
    "cited passage itself needs change to repair another supplied defect, make that "
    "necessary repair. Requirements absent here are not certified met: satisfy all "
    "acceptance tests, including any genuinely unmet requirement."
)


class NativeCheck(BaseModel):
    """The saved, rendered schema-7 native check, including unmet coverage."""

    model_config = ConfigDict(extra="forbid", strict=True)
    status: Literal["met", "unmet"]
    assessment: str = Field(min_length=1, max_length=600)
    draft_evidence_refs: list[str] = Field(min_length=1, max_length=3)
    recommended_resolution: str | None = Field(max_length=600)

    @model_validator(mode="after")
    def complete_check(self) -> NativeCheck:
        if not self.assessment.strip():
            raise ValueError("blank native assessment")
        if len(set(self.draft_evidence_refs)) != len(self.draft_evidence_refs):
            raise ValueError("duplicate native evidence")
        if self.status == "met" and self.recommended_resolution is not None:
            raise ValueError("met native check has repair advice")
        if self.status == "unmet" and (
            self.recommended_resolution is None or not self.recommended_resolution.strip()
        ):
            raise ValueError("unmet native check lacks rendered repair advice")
        return self


@dataclass(frozen=True)
class Projection:
    """Omissions are explicit and never salvage part of a malformed audit."""

    packet: dict[str, Any] | None
    reason: str


def packet_bytes(packet: Mapping[str, object]) -> bytes:
    """Use the writer's actual compact UTF-8 JSON representation for the cap."""
    return json.dumps(packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def project_fulfillment(
    *,
    audit: object,
    assignment: Mapping[str, object],
    catalog: tuple[dict[str, str], ...],
    critique_version_id: str,
    draft_version_id: str,
    plan_version_id: str,
    response_sha256: str,
) -> Projection:
    """Project validated whole met checks without interpreting their literary truth."""
    if not isinstance(audit, dict):
        return Projection(None, "missing_audit")
    if audit.get("schema_version") != "7":
        return Projection(None, "unsupported_audit")
    if (
        audit.get("candidate_version_id") != draft_version_id
        or audit.get("current_plan_version_id") != plan_version_id
    ):
        return Projection(None, "stale_audit")
    if audit.get("repair_advice_origin") != "shared_finding_conditions" or not isinstance(
        audit.get("assignment_repair_conditions"), list
    ):
        return Projection(None, "malformed_audit")
    anchors = [a for a in ("turning_point", "outcome") if assignment.get(a)]
    checks = audit.get("assignment_checks")
    if not isinstance(checks, dict) or set(checks) != set(anchors):
        return Projection(None, "malformed_coverage")
    excerpts = {row["evidence_ref"]: row["exact_excerpt"] for row in catalog}
    requirements: list[dict[str, Any]] = []
    for anchor in anchors:
        try:
            check = NativeCheck.model_validate(checks[anchor])
        except ValidationError:
            return Projection(None, "malformed_check")
        if any(ref not in excerpts for ref in check.draft_evidence_refs):
            return Projection(None, "invalid_evidence")
        if check.status == "met":
            requirements.append(
                {
                    "requirement": anchor,
                    "assigned_requirement": assignment[anchor],
                    "assignment_source_version_id": plan_version_id,
                    "status": "met",
                    "assessment": check.assessment,
                    "evidence": [
                        {"evidence_ref": ref, "exact_excerpt": excerpts[ref]}
                        for ref in check.draft_evidence_refs
                    ],
                }
            )
    if not requirements:
        return Projection(None, "no_met_requirements")
    packet = {
        "source_critique_version_id": critique_version_id,
        "reviewed_draft_version_id": draft_version_id,
        "source_response_sha256": response_sha256,
        "scene_id": assignment["scene_id"],
        "policy": FULFILLMENT_POLICY,
        "requirements": requirements,
    }
    return Projection(packet, "included")
