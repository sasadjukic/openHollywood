"""Join independent frozen judgments and sealed evidence decisions for six fixed slots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.fresh_endpoint_repeat.scoring import checked
from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet

from . import plan, run

GOLD_SHA = "d184229b5b0ded97dc4ec2ab0405204c9414ac109e0cf76673743136b9168502"


def scores(report: Audit, decisions: bytes, gold: bytes) -> dict[str, Any]:
    form = checked(report, decisions)
    require(digest(gold) == GOLD_SHA, "visit_position_gold_drift")
    key = json.loads(gold)
    rows = {}
    for slot in report["slots"]:
        if slot["stage"] != "generation":
            continue
        name = str(slot["cell"])
        case, _ = name.split("-")
        row = dict(judgment="unscored", evidence="unscored", delivery=str(slot["state"]))
        if slot["eligible"]:
            final = slot["final"]
            assert isinstance(final, dict)
            label = final["assessments"][key[case]["unit"]]["support"]
            decision = form.decisions[str(slot["scoring_id"])]
            row.update(
                returned=label,
                judgment="pass" if label == key[case]["gold"] else "fail",
                evidence=decision.outcome,
                basis=decision.basis,
            )
        rows[name] = row
    require(tuple(rows) == plan.ORDER, "visit_position_score_inventory")
    by_ending = {
        ending: {
            scope: rows[case + "-B"]
            for case, (draft, scope) in plan.CASES.items()
            if draft == ending
        }
        for ending in ("stop", "exclusion", "arrival")
    }
    joint = {k: r["judgment"] == r["evidence"] == "pass" for k, r in rows.items()}
    if any(r["judgment"] == "unscored" for r in rows.values()):
        result = "inconclusive"
    elif not (joint["A1-B"] and joint["A2-B"]):
        result = "hold_arrival_control"
    elif not all(joint.values()):
        result = "hold_claim_scope"
    else:
        result = "within_scene_scope_discrimination"
    return dict(
        approval_sha256=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        rows=rows,
        by_ending=by_ending,
        decision=result,
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
