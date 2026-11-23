"""Record source-based evidence decisions before comparing labels with the Q011 gold."""

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

from . import plan, run


def scores(report: Audit, decisions: bytes, gold: bytes) -> dict[str, object]:
    form = checked(report, decisions)
    cases = json.loads(gold)["cases"]
    rows = []
    for slot in report["slots"]:
        if slot["stage"] != "generation":
            continue
        case = str(slot["cell"]).split("-")[0]
        row: dict[str, object] = dict(
            case=case, delivery=slot["state"], judgment="unscored", evidence="unscored"
        )
        if slot["eligible"]:
            final = slot["final"]
            assert isinstance(final, dict)
            label = final["assessments"]["Q011"]["support"]
            expected = cases[case]["whole_claim_gold"]
            evidence = form.decisions[str(slot["scoring_id"])]
            row.update(
                returned=label,
                expected=expected,
                judgment="pass" if label == expected else "fail",
                evidence=evidence.outcome,
                evidence_basis=evidence.basis,
            )
        rows.append(row)
    require([r["case"] for r in rows] == ["A", "B"], "q011_scoring_slots")
    decision = "inconclusive"
    if all(r["judgment"] != "unscored" for r in rows):
        decision = (
            "grounded_pair"
            if all(r["judgment"] == r["evidence"] == "pass" for r in rows)
            else "hold"
        )
    return dict(
        approval=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        cases=rows,
        decision=decision,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-plan-sha256", required=True)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("worksheet")
    commands.add_parser("seal-evidence").add_argument("form", type=Path)
    commands.add_parser("score")
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
