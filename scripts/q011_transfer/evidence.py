"""Blind operator form for locating both material clauses in the cited draft."""

from __future__ import annotations

from typing import Any

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import Digest, Record, require, strict_object

from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_evidence_check.scoring import EvidenceDecision, Passage
from scripts.q011_evidence_check.scoring import checked as check_passages


class TransferEvidence(EvidenceDecision):
    first_action: Passage | None


class Decisions(Record):
    approval_sha256: Digest
    sheet_sha256: Digest
    decisions: dict[str, TransferEvidence]


def checked(report: Audit, raw: bytes, witnesses: dict[str, Any]) -> Decisions:
    form = Decisions.model_validate(strict_object(raw.decode()))
    # Reuse the sealed position instrument for IDs, worksheet binding and position spans.
    position_form = form.model_dump(
        mode="json", exclude={"decisions": {"__all__": {"first_action"}}}
    )
    check_passages(report, encoded(position_form), witnesses)
    for row in evidence_sheet(report):
        d = form.decisions[str(row["scoring_id"])]
        p = d.first_action
        citations = row["citations"]
        assert isinstance(citations, list)
        if d.outcome == "pass":
            require(
                {"E0233", "E0229"}.issubset(citations) and p is not None, "missing_clause_coverage"
            )
        if p is not None:
            w = witnesses[d.case]
            prose = w["fields"]["E0883"]
            field = w["fields"][p.ref]
            require(
                p.ref in citations
                and p.draft_version == w["draft_version"]
                and len(prose) - len(field) <= p.start < p.end <= len(prose)
                and prose[p.start : p.end] == p.quote,
                "wrong_first_action_span",
            )
    return form
