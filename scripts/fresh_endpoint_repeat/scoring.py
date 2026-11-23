"""Seal masked evidence decisions before joining returned labels for the fresh repeat."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Literal

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import Digest, Record, require, strict_object

from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet

from . import controls, plan, run

DECISIONS = plan.ROOT / "sealed-evidence-decisions.json"


class Judgment(Record):
    case: str
    outcome: Literal["pass", "fail"]
    basis: str


class Decisions(Record):
    approval_sha256: Digest
    sheet_sha256: Digest
    decisions: dict[str, Judgment]


def checked(report: Audit, raw: bytes) -> Decisions:
    require(
        report["closed"] and report["origin"] == "observed_openai_transport", "observed_closure"
    )
    form = Decisions.model_validate(strict_object(raw.decode()))
    sheet = evidence_sheet(report)
    require(
        form.approval_sha256 == report["approval"] and form.sheet_sha256 == digest(encoded(sheet)),
        "wrong_worksheet",
    )
    expected = {str(row["scoring_id"]): row["case"] for row in sheet}
    require(len(expected) == len(sheet) and set(form.decisions) == set(expected), "decision_ids")
    for key, decision in form.decisions.items():
        require(decision.case == expected[key] and bool(decision.basis.strip()), "decision_basis")
    return form


def gate(
    pairs: dict[str, dict[str, tuple[bool, bool]]], states: dict[str, str]
) -> dict[str, object]:
    """A baseline pass retained by C is a tie. Control regressions take priority over ties."""
    complete = len(pairs) == 8 and all(set(pairs.get(k, {})) == {"B", "C"} for k in states)
    recoveries, losses = [], []
    for case, state in states.items():
        arms = pairs.get(case, {})
        if set(arms) != {"B", "C"}:
            continue
        b, c = arms["B"], arms["C"]
        if state == "unresolved" and not all(b) and all(c):
            recoveries.append(case)
        if state != "unresolved":
            for axis, was, now in zip(("claim", "evidence"), b, c, strict=True):
                if was and not now:
                    losses.append({"case": case, "axis": axis})
    if not complete:
        decision = "inconclusive"
    elif losses or any(not all(arms["C"]) for arms in pairs.values()):
        decision = "hold"
    elif not recoveries:
        decision = "no_recovery_headroom"
    else:
        decision = "fresh_transfer_signal"
    return {
        "decision": decision,
        "unresolved_recoveries": recoveries,
        "movement_case_recovered": "R06" in recoveries,
        "control_axis_losses": losses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-plan-sha256", required=True)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("worksheet")
    commands.add_parser("seal-evidence").add_argument("form", type=Path)
    commands.add_parser("score")
    args = parser.parse_args()
    report = run.audit(plan.ROOT, args.approved_plan_sha256)
    require(report["closed"], "journal_open")
    if args.action == "worksheet":
        sheet = evidence_sheet(report)
        print(
            encoded(
                {
                    "approval_sha256": report["approval"],
                    "sheet_sha256": digest(encoded(sheet)),
                    "rows": sheet,
                }
            ).decode()
        )
    elif args.action == "seal-evidence":
        form = checked(report, _read(args.form))
        _durable_write(DECISIONS, encoded(form.model_dump(mode="json")))
    else:
        raw = _read(DECISIONS)
        form = checked(report, raw)
        gold = json.loads(_read(controls.ROOT / "frozen/gold.json"))["cases"]
        states = {r["case_id"]: r["state"] for r in gold}
        labels = {r["case_id"]: r["whole_claim_gold"] for r in gold}
        pairs: dict[str, dict[str, tuple[bool, bool]]] = {}
        rows = []
        for slot in report["slots"]:
            if slot["stage"] != "generation":
                continue
            case, arm = str(slot["cell"]).split("-")
            row = dict(
                cell=slot["cell"], delivery=slot["state"], claim="unscored", evidence="unscored"
            )
            if slot["eligible"]:
                d = form.decisions[str(slot["scoring_id"])]
                final = slot["final"]
                assert isinstance(final, dict)
                (answer,) = final["assessments"].values()
                label_ok = answer["support"] == labels[case]
                pairs.setdefault(case, {})[arm] = (label_ok, d.outcome == "pass")
                row.update(
                    claim="pass" if label_ok else "fail",
                    evidence=d.outcome,
                    expected=labels[case],
                    returned=answer["support"],
                    basis=d.basis,
                    scoring_id=slot["scoring_id"],
                )
            rows.append(row)
        print(
            encoded(
                {
                    "approval": report["approval"],
                    "decisions_sha256": digest(raw),
                    "generations": rows,
                    **gate(pairs, states),
                }
            ).decode()
        )


if __name__ == "__main__":
    main()
