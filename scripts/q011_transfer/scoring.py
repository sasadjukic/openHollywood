"""Review cited observations before joining the sixteen transfer judgments to gold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.q011_arrival.scope_rehearsal import UNIT

from . import plan, run
from .evidence import checked


def scores(
    report: Audit, decisions: bytes, witnesses: dict[str, Any], gold: bytes
) -> dict[str, Any]:
    form = checked(report, decisions, witnesses)
    require(digest(gold) == plan.GOLD, "transfer_gold_drift")
    cases = json.loads(gold)["cases"]
    deliveries = {s["cell"]: s for s in report["slots"] if s["stage"] == "generation"}
    pairs: dict[str, dict[str, Any]] = {}
    for key in plan.FIRST_ARM:
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
                    judgment="pass" if label == cases[key]["label"] else "fail",
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
        pairs[key] = dict(
            family=cases[key]["family"],
            state=cases[key]["state"],
            gold=cases[key]["label"],
            arms=arms,
            movement=moves,
        )
    baseline_passes = []
    unresolved = {}
    control_movement = {}
    recovered_families = set()
    for key, pair in pairs.items():
        arms = pair["arms"]
        baseline = (arms["B"]["judgment"], arms["B"]["evidence"])
        candidate = (arms["E"]["judgment"], arms["E"]["evidence"])
        if baseline == ("pass", "pass"):
            baseline_passes.append(key)
        if pair["state"] in ("approach", "earlier_gap"):
            recovery = (
                None
                if "unscored" in (*baseline, *candidate)
                else ("fail" in baseline and candidate == ("pass", "pass"))
            )
            unresolved[key] = dict(family=pair["family"], state=pair["state"], recovered=recovery)
            if recovery:
                recovered_families.add(pair["family"])
        else:
            control_movement[key] = pair["movement"]
    if any("unscored" in p["movement"].values() for p in pairs.values()):
        decision = "inconclusive"
    elif any(
        p["arms"]["E"][axis] != "pass" for p in pairs.values() for axis in ("judgment", "evidence")
    ):
        decision = "hold"
    elif len(recovered_families) == 2:
        decision = "cross_family_recovery"
    elif recovered_families:
        decision = "family_specific_recovery"
    elif len(baseline_passes) == len(pairs):
        decision = "no_recovery_opportunity"
    else:
        decision = "control_only_gains"
    return dict(
        approval_sha256=report["approval"],
        evidence_decisions_sha256=digest(decisions),
        decision=decision,
        baseline_joint_passes=baseline_passes,
        unresolved=unresolved,
        determinate_movement=control_movement,
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
