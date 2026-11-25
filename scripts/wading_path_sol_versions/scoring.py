"""Join frozen judgments and masked evidence grades across paired Sol versions."""

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

GOLD_SHA = "6ad2f72dcf8ad8fade23140be0bad24e50f0d87a424f08604d74864cd551d7dd"


def scores(report: Audit, decisions: bytes, gold: bytes) -> dict[str, Any]:
    form = checked(report, decisions)
    require(digest(gold) == GOLD_SHA, "sol_versions_gold_drift")
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
    require(tuple(rows) == plan.ORDER, "sol_versions_score_inventory")
    pairs = {}
    for case in plan.CASES:
        a, b = (rows[f"{case}-{arm}"] for arm in ("61", "62"))
        paired = {}
        for axis in ("judgment", "evidence"):
            left, right = a[axis], b[axis]
            if "unscored" in (left, right):
                paired[axis] = "unscored"
            elif left == right:
                paired[axis] = "both_" + left
            else:
                paired[axis] = "gain_62" if right == "pass" else "loss_62"
        pairs[case] = paired
    complete = all("unscored" not in pair.values() for pair in pairs.values())
    joint = {
        arm: sum(
            rows[f"{case}-{arm}"]["judgment"] == rows[f"{case}-{arm}"]["evidence"] == "pass"
            for case in plan.CASES
        )
        for arm in plan.MODELS
    }
    a, b = (rows["SE-" + arm] for arm in plan.MODELS)
    recovery = (
        None
        if "unscored" in pairs["SE"].values()
        else (
            (a["judgment"], a["evidence"]) != ("pass", "pass")
            and (b["judgment"], b["evidence"]) == ("pass", "pass")
        )
    )
    return dict(
        approval_sha256=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        rows=rows,
        paired_axes=pairs,
        observed_joint_passes=joint,
        open_event_recovery_62=recovery,
        decision="complete_within_scene" if complete else "inconclusive",
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
