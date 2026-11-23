"""Replay eight observed transfer pairs from the sealed private archive."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import digest, schedule
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent
from scripts.q011_arrival.run import evaluate

from . import plan, scoring

ARCHIVE = plan.ROOT.parent / "q011-transfer-regression-2026-11-23"
SEAL = "083759ebba66d0b3dba4b6957b30575fb6012eb04a980ccaaca51608ea07d3a8"
APPROVAL = "6ef2effd0f6d9cbfbc54962b0b984b0fcd49039af7a457db0f56341d46166588"


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    raw = (archive / "capture-manifest.json").read_bytes()
    require(digest(raw) == SEAL, "transfer_regression_seal")
    members = json.loads(raw)
    capture = archive / "capture"
    inventory = {p.relative_to(capture).as_posix() for p in capture.rglob("*") if p.is_file()}
    require(inventory == set(members), "transfer_regression_inventory")
    require(
        all(file_hash(capture / p) == h for p, h in members.items()),
        "transfer_regression_member",
    )

    frozen = capture / "run"
    operator = capture / "operator"
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "transfer_regression_approval",
    )
    issued = json.loads((frozen / "plan.json").read_bytes())
    packets = {
        name: json.loads((frozen / f"packets/{name}.json").read_bytes()) for name in plan.FIRST_ARM
    }
    cells = plan.render(packets)
    gold = (frozen / "gold.json").read_bytes()
    require(digest(gold) == plan.GOLD == issued["gold_sha256"], "transfer_regression_gold")
    require(
        all(file_hash(frozen / name) == sha for name, sha in issued["members"].items()),
        "transfer_regression_frozen_member",
    )
    output = frozen / "output"
    previous = (output / "header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["origin"] == "observed_openai_transport" and header["approval"] == APPROVAL,
        "transfer_regression_origin",
    )
    observed: Audit = dict(
        approval=APPROVAL,
        origin=header["origin"],
        closed=True,
        ledger="dispatched",
        state="bound_unassessed",
        slots=[],
    )
    readback = json.loads((operator / "delivery-readback.json").read_bytes())
    for i, ((cell, end), slot, record) in enumerate(
        zip(schedule(cells), issued["slots"], readback["slots"], strict=True), 1
    ):
        stem = f"{i:02d}-{cell.name}-{end.stage}"
        message = (output / (stem + "-intent.json")).read_bytes()
        require(
            message == intent(previous, cell, end)
            and slot["work_sha256"] == record["work_sha256"] == cell.work.fingerprint
            and slot["case"] == cell.name.split("-")[0]
            and slot["stage"] == record["stage"] == end.stage
            and slot["native_request_sha256"]
            == record["native_request_sha256"]
            == cell.wire.native_request_sha256
            and slot["slot"] == record["slot"] == i
            and slot["cell"] == record["cell"] == cell.name
            and (frozen / slot["filename"]).read_bytes() == end.body_utf8.encode()
            and slot["body_bytes_sha256"] == record["request_body_sha256"] == end.body_bytes_sha256,
            "transfer_regression_request",
        )
        previous = (output / (stem + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous)
        require(
            terminal.intent_sha256 == digest(message)
            and digest(message) == record["intent_sha256"]
            and digest(previous) == record["outcome_sha256"]
            and terminal.http_status == 200
            and terminal.request_id == record["request_id"]
            and terminal.body is not None
            and terminal.raw_sha256 == digest(terminal.body.encode()),
            "transfer_regression_terminal",
        )
        state, details = evaluate(cell, end, terminal)
        generation = end.stage == "generation"
        require(
            state == ("bound_unassessed" if generation else "count_admitted"),
            "transfer_regression_delivery",
        )
        require(
            record["eligible"] == generation
            and record["state"] == state
            and all(
                encoded(record[k]) == encoded(v)
                for k, v in details.items()
                if k not in ("final", "scoring_id")
            ),
            "transfer_regression_slot",
        )
        observed["slots"].append(
            dict(cell=cell.name, stage=end.stage, state=state, eligible=generation, **details)
        )
    require(
        (output / "close.json").read_bytes() == closure(previous, observed["state"])
        and encoded(observed) == (operator / "audit.json").read_bytes(),
        "transfer_regression_closure",
    )
    witnesses = json.loads((frozen / "witnesses.json").read_bytes())
    sheet = evidence_sheet(observed)
    require(
        encoded(
            dict(
                approval_sha256=APPROVAL,
                sheet_sha256=digest(encoded(sheet)),
                rows=sheet,
                sources=witnesses,
            )
        )
        == (operator / "worksheet.json").read_bytes(),
        "transfer_regression_worksheet",
    )
    decisions = (frozen / "sealed-evidence-decisions.json").read_bytes()
    result = scoring.scores(observed, decisions, witnesses, gold)
    require(
        decisions == (operator / "evidence-form.json").read_bytes()
        and encoded(result) == (operator / "scores.json").read_bytes()
        and result["decision"] == "cross_family_recovery"
        and result["baseline_joint_passes"] == ["T03", "T04", "T05", "T06", "T08"],
        "transfer_regression_scores",
    )
    require(
        len(observed["slots"]) == 32 and len({s["request_id"] for s in observed["slots"]}) == 32,
        "transfer_regression_attempts",
    )
    for case, pair in result["pairs"].items():
        expected = "gain" if case in ("T01", "T02", "T07") else "retained_pass"
        require(
            pair["movement"] == dict(judgment=expected, evidence=expected)
            and pair["arms"]["E"]["returned"] == pair["gold"]
            and pair["arms"]["B"]["returned"]
            == ("unsupported" if expected == "gain" else pair["gold"]),
            "transfer_regression_pair",
        )
    return dict(
        manifest_sha256=SEAL,
        members=len(members),
        slots=len(observed["slots"]),
        live_calls=0,
        **result,
    )


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
