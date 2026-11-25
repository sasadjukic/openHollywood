"""Seal evidence judgments blind to model and presentation, then join the two scores."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, TypedDict

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.fresh_endpoint_repeat.scoring import checked
from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.wading_path_sol_astra.scoring import CONTRASTS, change

from . import plan, run


class ArmSummary(TypedDict):
    joint_passes: int
    target_joint: dict[str, bool]
    control_joint: dict[str, bool]
    qualifies: bool | None


def scores(report: Audit, decisions: bytes, gold: bytes) -> dict[str, Any]:
    form = checked(report, decisions)
    require(digest(gold) == plan.GOLD_SHA, "planetarium_gold_changed")
    key, rows = json.loads(gold), {}
    for slot in report["slots"]:
        if slot["stage"] != "generation":
            continue
        name = str(slot["cell"])
        case = name.split("-")[0]
        row = dict(judgment="unscored", evidence="unscored", delivery=str(slot["state"]))
        if slot["eligible"]:
            final = slot["final"]
            assert isinstance(final, dict)
            label = final["assessments"][key[case]["unit"]]["support"]
            grade = form.decisions[str(slot["scoring_id"])]
            row.update(
                returned=label,
                judgment="pass" if label == key[case]["gold"] else "fail",
                evidence=grade.outcome,
                basis=grade.basis,
            )
        rows[name] = row
    require(tuple(rows) == plan.ORDER, "score_inventory")
    complete = all(r["judgment"] != "unscored" for r in rows.values())
    arms: dict[str, ArmSummary] = {}
    for arm in plan.ARMS:
        joint = {
            case: rows[f"{case}-{arm}"]["judgment"] == rows[f"{case}-{arm}"]["evidence"] == "pass"
            for case in plan.CASES
        }
        arms[arm] = dict(
            joint_passes=sum(joint.values()),
            target_joint={
                c: joint[c] for c in plan.TARGETS if rows[f"{c}-{arm}"]["judgment"] != "unscored"
            },
            control_joint={
                c: joint[c] for c in plan.CONTROLS if rows[f"{c}-{arm}"]["judgment"] != "unscored"
            },
            qualifies=all(joint.values()) if complete else None,
        )
    contrasts = {
        name: {
            case: {
                axis: change(rows[f"{case}-{left}"][axis], rows[f"{case}-{right}"][axis])
                for axis in ("judgment", "evidence")
            }
            for case in plan.CASES
        }
        for name, (left, right) in CONTRASTS.items()
    }
    qualified = [arm for arm in plan.ARMS if arms[arm]["qualifies"]]
    open_passes = [arm for arm in plan.ARMS if arms[arm]["target_joint"].get("OE")]
    if not complete:
        decision = "inconclusive"
    elif "AX" not in qualified:
        decision = "hold_astra_scope"
    elif open_passes == ["AX"]:
        decision = "astra_explicit_only_transfer"
    else:
        decision = "shared_open_event_recovery"
    return dict(
        approval_sha256=report["approval"],
        evidence_sha256=digest(decisions),
        rows=rows,
        arms=arms,
        paired_axes=contrasts,
        open_event_joint_passes=open_passes,
        sol_B_open_recovery=arms["SB"]["target_joint"].get("OE"),
        qualified_arms=qualified,
        decision=decision,
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
    path = plan.ROOT / "sealed-evidence-decisions.json"
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
        _durable_write(path, encoded(form.model_dump(mode="json")))
    else:
        print(encoded(scores(report, _read(path), _read(plan.ROOT / "gold.json"))).decode())


if __name__ == "__main__":
    main()
