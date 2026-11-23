"""Seal source-specific evidence decisions before comparing labels with the six-case gold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.fresh_endpoint_repeat.scoring import checked
from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_arrival import scope_rehearsal as rehearsal

from . import plan, run


def scores(report: Audit, decisions: bytes, gold: bytes) -> dict[str, object]:
    form = checked(report, decisions)
    require(digest(gold) == rehearsal.GOLD, "q011_scope_wrong_gold")
    cases = json.loads(gold)["cases"]
    deliveries = [s for s in report["slots"] if s["stage"] == "generation"]
    rows = []
    for (key, case), slot in zip(plan.CASES.items(), deliveries, strict=True):
        require(slot["cell"] == key + "-B", "q011_scope_wrong_slot")
        row: dict[str, object] = dict(
            case=case,
            cell=slot["cell"],
            delivery=slot["state"],
            judgment="unscored",
            evidence="unscored",
        )
        if slot["eligible"]:
            final = slot["final"]
            assert isinstance(final, dict)
            label = final["assessments"][rehearsal.UNIT]["support"]
            expected = cases[case]["gold"]
            decision = form.decisions[str(slot["scoring_id"])]
            row.update(
                expected=expected,
                returned=label,
                judgment="pass" if label == expected else "fail",
                evidence=decision.outcome,
                basis=decision.basis,
                scoring_id=slot["scoring_id"],
            )
        rows.append(row)

    def outcome(group: list[dict[str, object]]) -> str:
        if any(r["judgment"] == "unscored" for r in group):
            return "inconclusive"
        return "pass" if all(r["judgment"] == r["evidence"] == "pass" for r in group) else "hold"

    overall = outcome(rows)
    return dict(
        approval=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        original_pair=dict(outcome=outcome(rows[:2]), cases=rows[:2]),
        clear_controls=dict(outcome=outcome(rows[2:]), cases=rows[2:]),
        decision="grounded_scope_split" if overall == "pass" else overall,
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
    destination = plan.ROOT / "sealed-evidence-decisions.json"
    if args.action == "worksheet":
        sheet = evidence_sheet(report)
        print(
            encoded(
                dict(
                    approval_sha256=report["approval"],
                    sheet_sha256=digest(encoded(sheet)),
                    rows=sheet,
                )
            ).decode()
        )
    elif args.action == "seal-evidence":
        form = checked(report, _read(args.form))
        _durable_write(destination, encoded(form.model_dump(mode="json")))
    else:
        print(encoded(scores(report, _read(destination), _read(plan.ROOT / "gold.json"))).decode())


if __name__ == "__main__":
    main()
