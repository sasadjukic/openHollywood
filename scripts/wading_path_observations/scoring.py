"""Join independent frozen judgments and sealed evidence decisions for seven fixed slots."""

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

GOLD_SHA = "e0c9ba29062f618298efa8dd99c7673cd79e8d6af96aa85f51215a460a4ceb9e"


def scores(report: Audit, decisions: bytes, gold: bytes) -> dict[str, Any]:
    form = checked(report, decisions)
    require(digest(gold) == GOLD_SHA, "observation_gold_drift")
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
    require(tuple(rows) == plan.ORDER, "observation_score_inventory")
    movement = {}
    for case in ("K1", "K2", "K3"):
        axes = {}
        for axis in ("judgment", "evidence"):
            b, o = (rows[case + "-" + a][axis] for a in ("B", "O"))
            if "unscored" in (b, o):
                axes[axis] = "unscored"
            elif b == o:
                axes[axis] = "retained_" + b
            else:
                axes[axis] = "gain" if o == "pass" else "loss"
        movement[case] = axes
    joint = {k: r["judgment"] == r["evidence"] == "pass" for k, r in rows.items()}
    if any(r["judgment"] == "unscored" for r in rows.values()):
        result = "inconclusive"
    elif not all(joint[k] for k in ("K2-B", "K2-O", "K3-B", "K3-O", "Q008-B")):
        result = "hold_controls"
    elif not joint["K1-O"]:
        result = "hold_original"
    elif joint["K1-B"]:
        result = "no_original_headroom"
    else:
        result = "within_scene_recovery"
    return dict(
        approval_sha256=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        rows=rows,
        movement=movement,
        original_baseline_recovery=(
            joint["K1-B"] if rows["K1-B"]["judgment"] != "unscored" else None
        ),
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
