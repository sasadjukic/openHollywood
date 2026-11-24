"""Seal blinded passage decisions and report the two position pairs and the B control."""

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
from scripts.q011_transfer import wading_path_selection as selection

from . import plan, run


def scores(report: Audit, decisions: bytes, gold: bytes) -> dict[str, Any]:
    form = checked(report, decisions)
    require(digest(gold) == selection.GOLD_SHA, "wading_gold_drift")
    cases = {c["field_id"]: c["label"] for c in json.loads(gold)["claims"]}
    rows = {}
    for slot in report["slots"]:
        if slot["stage"] != "generation":
            continue
        name = str(slot["cell"])
        unit, arm = name.split("-")
        row = dict(judgment="unscored", evidence="unscored", delivery=str(slot["state"]))
        if slot["eligible"]:
            final = slot["final"]
            assert isinstance(final, dict)
            label = final["assessments"][unit]["support"]
            decision = form.decisions[str(slot["scoring_id"])]
            row.update(
                returned=label,
                judgment="pass" if label == cases[unit] else "fail",
                evidence=decision.outcome,
                basis=decision.basis,
            )
        rows[name] = row
    require(list(rows) == [u + "-" + a for u, a in selection.PREVIEWS], "wading_score_inventory")
    movements = {}
    gains = losses = False
    for unit in ("Q010", "Q011"):
        movement = {}
        for axis in ("judgment", "evidence"):
            b, e = (rows[unit + "-" + a][axis] for a in ("B", "E"))
            if "unscored" in (b, e):
                movement[axis] = "unscored"
            elif b == e:
                movement[axis] = "retained_" + b
            elif e == "pass":
                movement[axis] = "gain"
                gains = True
            else:
                movement[axis] = "loss"
                losses = True
        movements[unit] = movement
    baseline = [
        u for u in movements if rows[u + "-B"]["judgment"] == rows[u + "-B"]["evidence"] == "pass"
    ]
    control = rows["Q008-B"]
    if any(r["judgment"] == "unscored" for r in rows.values()):
        result = "inconclusive"
    elif losses or control["judgment"] != "pass" or control["evidence"] != "pass":
        result = "hold"
    elif gains:
        result = "within_review_gain"
    elif len(baseline) == 2:
        result = "no_headroom"
    else:
        result = "no_gain"
    return dict(
        approval_sha256=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        rows=rows,
        movement=movements,
        control=control,
        baseline_joint_passes=baseline,
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
