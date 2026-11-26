"""Seal the masked readings before joining the returned labels to the frozen case gold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from open_hollywood_api.services.assessment_completion import _read
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require, strict_object

from scripts.q010_uncertainty_plan import digest
from scripts.q010_uncertainty_run import Audit, evidence_sheet
from scripts.wading_path_sol_astra.scoring import CONTRASTS, change

from . import plan, run
from .rubric import Decisions

AXES = ("judgment", "factual_sufficiency", "diagnostic_completeness")


def checked(report: Audit, raw: bytes, drafts: bytes) -> Decisions:
    require(
        report["closed"] and report["origin"] == "observed_openai_transport", "observed_closure"
    )
    form = Decisions.model_validate(strict_object(raw.decode()))
    sheet = evidence_sheet(report)
    require(
        form.approval_sha256 == report["approval"] and form.sheet_sha256 == digest(encoded(sheet)),
        "wrong_worksheet",
    )
    require(
        len(sheet) == len(form.decisions)
        and set(form.decisions) == {r["scoring_id"] for r in sheet},
        "decision_ids",
    )
    sources = json.loads(drafts)
    for row in sheet:
        d = form.decisions[str(row["scoring_id"])]
        why = row["reason"]
        assert isinstance(why, str)
        require(
            d.case == row["case"]
            and all(
                x.strip()
                for x in (d.reason_excerpt, d.draft_excerpt, d.factual_basis, d.diagnostic_basis)
            )
            and d.reason_excerpt in why
            and d.draft_excerpt in sources[d.case]["quote"],
            "reading_binding",
        )
        require(
            d.factual_sufficiency == "pass" or d.diagnostic_completeness == "fail",
            "completeness_requires_sufficiency",
        )
        citations = row["citations"]
        require(
            d.factual_sufficiency == "fail" or isinstance(citations, list) and "E1420" in citations,
            "selected_draft_citation",
        )
        if d.false_denial_excerpt is not None:
            require(
                d.case in ("SE", "VE")
                and d.factual_sufficiency == "fail"
                and bool(d.false_denial_excerpt.strip())
                and d.false_denial_excerpt in why,
                "denial_annotation",
            )
    return form


def scores(report: Audit, decisions: bytes, drafts: bytes, gold: bytes) -> dict[str, Any]:
    form = checked(report, decisions, drafts)
    key = json.loads(gold)
    rows: dict[str, dict[str, Any]] = {}
    for slot in report["slots"]:
        if slot["stage"] != "generation":
            continue
        name = str(slot["cell"])
        case = name.split("-")[0]
        row: dict[str, Any] = dict.fromkeys(AXES, "unscored")
        row.update(delivery=slot["state"], false_scene_wide_denial=None)
        if slot["eligible"]:
            final = slot["final"]
            assert isinstance(final, dict)
            label = final["assessments"][key[case]["unit"]]["support"]
            reading = form.decisions[str(slot["scoring_id"])]
            row.update(
                **reading.model_dump(),
                scoring_id=slot["scoring_id"],
                returned=label,
                judgment="pass" if label == key[case]["gold"] else "fail",
                false_scene_wide_denial=reading.false_denial_excerpt is not None,
            )
        rows[name] = row
    require(tuple(rows) == plan.ORDER, "score_inventory")
    arms = {}
    for arm in plan.ARMS:
        target = [rows[f"SE-{arm}-{i}"] for i in range(1, 5)]
        controls = {case: rows[f"{case}-{arm}-1"] for case in ("XE", "VE")}
        arms[arm] = dict(
            hard_scored=sum(r["judgment"] != "unscored" for r in target),
            hard_axis_passes={a: sum(r[a] == "pass" for r in target) for a in AXES},
            hard_grounded=sum(r["judgment"] == r["factual_sufficiency"] == "pass" for r in target),
            hard_false_denials=sum(r["false_scene_wide_denial"] is True for r in target),
            controls={k: {a: r[a] for a in AXES} for k, r in controls.items()},
        )
    candidate = arms["AX"]
    complete = all(r["judgment"] != "unscored" for r in rows.values())
    lead = candidate["hard_grounded"] - max(arms[a]["hard_grounded"] for a in ("AB", "SB", "SX"))
    control_pass = all(v == "pass" for r in candidate["controls"].values() for v in r.values())
    decision = "hold"
    if not complete:
        decision = "inconclusive"
    elif candidate["hard_grounded"] >= 3 and lead >= 2 and control_pass:
        decision = "consider_held_out_family"
    paired = {
        contrast: {
            f"{case}-{rep}": {
                a: change(rows[f"{case}-{left}-{rep}"][a], rows[f"{case}-{right}-{rep}"][a])
                for a in AXES
            }
            for case, rep, _ in plan.BLOCKS
        }
        for contrast, (left, right) in CONTRASTS.items()
    }
    return dict(
        approval_sha256=report["approval"],
        decisions_sha256=digest(decisions),
        rows=rows,
        arms=arms,
        paired_axes=paired,
        decision=decision,
        hard_lead_over_best_other=lead if complete else None,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--approved-plan-sha256", required=True)
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("worksheet")
    actions.add_parser("seal-evidence").add_argument("form", type=Path)
    actions.add_parser("score")
    args = parser.parse_args()
    root = plan.ROOT
    report = run.audit(root, args.approved_plan_sha256)
    require(
        report["closed"] and report["origin"] == "observed_openai_transport", "observed_closure"
    )
    path = root / "sealed-evidence-decisions.json"
    drafts = _read(root / "drafts.json")
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
        form = checked(report, _read(args.form), drafts)
        _durable_write(path, encoded(form.model_dump(mode="json")))
    else:
        print(encoded(scores(report, _read(path), drafts, _read(root / "gold.json"))).decode())


if __name__ == "__main__":
    main()
