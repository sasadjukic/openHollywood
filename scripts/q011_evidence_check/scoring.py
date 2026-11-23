"""Review cited observations before joining the ten returned position judgments to gold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Literal

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import Digest, Record, require, strict_object
from pydantic import Field

from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_arrival.scope_rehearsal import UNIT
from scripts.q011_scope.position_rehearsal import GOLD

from . import plan, run


class Passage(Record):
    ref: Literal["E0883", "D01"]
    draft_version: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    quote: str = Field(min_length=1)


class EvidenceDecision(Record):
    case: str
    outcome: Literal["pass", "fail"]
    basis: str = Field(min_length=1)
    passage: Passage | None
    instant: Literal["at_cut", "before_cut", "earlier_through_cut", "unspecified"]
    relation: Literal["establishes", "excludes", "leaves_open", "unspecified"]


class Decisions(Record):
    approval_sha256: Digest
    sheet_sha256: Digest
    decisions: dict[str, EvidenceDecision]


def checked(report: Audit, raw: bytes, witnesses: dict[str, Any]) -> Decisions:
    require(
        report["closed"] and report["origin"] == "observed_openai_transport", "observed_closure"
    )
    sheet = evidence_sheet(report)
    form = Decisions.model_validate(strict_object(raw.decode()))
    require(
        form.approval_sha256 == report["approval"] and form.sheet_sha256 == digest(encoded(sheet)),
        "wrong_worksheet",
    )
    keys = {str(row["scoring_id"]) for row in sheet}
    require(len(keys) == len(sheet) and keys == set(form.decisions), "decision_ids")
    for row in sheet:
        d = form.decisions[str(row["scoring_id"])]
        require(d.case == row["case"] and bool(d.basis.strip()), "decision_basis")
        p = d.passage
        if d.outcome == "pass":
            require(
                p is not None and d.instant != "unspecified" and d.relation != "unspecified",
                "unlocated_evidence_pass",
            )
        if p is not None:
            w = witnesses[d.case]
            prose = w["fields"]["E0883"]
            field = w["fields"][p.ref]
            citations = row["citations"]
            require(isinstance(citations, list) and p.ref in citations, "uncited_field")
            require(
                p.draft_version == w["draft_version"]
                and len(prose) - len(field) <= p.start < p.end <= len(prose)
                and prose[p.start : p.end] == p.quote,
                "wrong_position_span",
            )
    return form


def scores(
    report: Audit, decisions: bytes, witnesses: dict[str, Any], gold: bytes
) -> dict[str, Any]:
    form = checked(report, decisions, witnesses)
    require(digest(gold) == GOLD, "position_gold_drift")
    cases = json.loads(gold)["cases"]
    deliveries = {s["cell"]: s for s in report["slots"] if s["stage"] == "generation"}
    pairs: dict[str, dict[str, Any]] = {}
    for key, name in plan.CASES.items():
        arms = {}
        for arm in ("B", "E"):
            slot = deliveries[key + "-" + arm]
            row = dict(delivery=str(slot["state"]), judgment="unscored", evidence="unscored")
            if slot["eligible"]:
                final = slot["final"]
                assert isinstance(final, dict)
                label = final["assessments"][UNIT]["support"]
                evidence = form.decisions[str(slot["scoring_id"])]
                row.update(
                    returned=label,
                    judgment="pass" if label == cases[name]["label"] else "fail",
                    evidence=evidence.outcome,
                    basis=evidence.basis,
                    scoring_id=str(slot["scoring_id"]),
                )
            arms[arm] = row
        moves = {}
        for axis in ("judgment", "evidence"):
            before, after = arms["B"][axis], arms["E"][axis]
            if "unscored" in (before, after):
                moves[axis] = "unscored"
            elif before == after:
                moves[axis] = "retained_" + after
            else:
                moves[axis] = "gain" if after == "pass" else "loss"
        pairs[name] = dict(gold=cases[name]["label"], arms=arms, movement=moves)
    original = pairs["approach"]["arms"]["B"]
    baseline_recovery = (
        None
        if original["judgment"] == "unscored"
        else (original["judgment"] == original["evidence"] == "pass")
    )
    if any("unscored" in p["movement"].values() for p in pairs.values()):
        decision = "inconclusive"
    elif any(
        p["arms"]["E"][axis] != "pass" for p in pairs.values() for axis in ("judgment", "evidence")
    ):
        decision = "hold"
    elif baseline_recovery:
        decision = "genuine_baseline_recovery"
    else:
        decision = "genuine_paired_recovery"
    return dict(
        approval_sha256=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        decision=decision,
        genuine_baseline_recovery=baseline_recovery,
        pairs=pairs,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-plan-sha256", required=True)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("worksheet")
    actions.add_parser("seal-evidence").add_argument("form", type=Path)
    actions.add_parser("score")
    args = parser.parse_args()
    report = run.audit(plan.ROOT, args.approved_plan_sha256)
    require(
        report["closed"] and report["origin"] == "observed_openai_transport", "observed_closure"
    )
    witnesses = json.loads(_read(plan.ROOT / "witnesses.json"))
    destination = plan.ROOT / "sealed-evidence-decisions.json"
    if args.action == "worksheet":
        sheet = evidence_sheet(report)
        print(
            encoded(
                dict(
                    approval_sha256=report["approval"],
                    sheet_sha256=digest(encoded(sheet)),
                    rows=sheet,
                    sources=witnesses,
                )
            ).decode()
        )
    elif args.action == "seal-evidence":
        form = checked(report, _read(args.form), witnesses)
        _durable_write(destination, encoded(form.model_dump(mode="json")))
    else:
        print(
            encoded(
                scores(report, _read(destination), witnesses, _read(plan.ROOT / "gold.json"))
            ).decode()
        )


if __name__ == "__main__":
    main()
