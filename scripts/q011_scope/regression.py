"""Replay the six observed Q011 scope deliveries from the sealed private archive."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import map_response

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import digest, schedule
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent
from scripts.q011_arrival import scope_rehearsal as rehearsal
from scripts.q011_arrival.run import evaluate

from . import plan, scoring

ARCHIVE = plan.ROOT.parent / "q011-scope-regression-2026-11-23"
SEAL = "46bbeba44b2bf6fea881d5ad3014a8b680cd39ecd3e85a522f1508402ea411c0"
APPROVAL = "cae13f5bb291064892d46bfd850e2ce7e77d7014af6ec58c6d412b4c70d48dd2"


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    raw = (archive / "capture-manifest.json").read_bytes()
    require(digest(raw) == SEAL, "q011_scope_regression_seal")
    members = json.loads(raw)
    capture = archive / "capture"
    inventory = {p.relative_to(capture).as_posix() for p in capture.rglob("*") if p.is_file()}
    require(inventory == set(members), "q011_scope_regression_inventory")
    require(
        all(file_hash(capture / p) == h for p, h in members.items()), "q011_scope_regression_member"
    )

    frozen = capture / "run"
    operator = capture / "operator"
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "q011_scope_regression_approval",
    )
    issued = json.loads((frozen / "plan.json").read_bytes())
    packets = {
        name: json.loads((capture / f"source/{name}.json").read_bytes())
        for name in ("approach", "arrival", "stop")
    }
    works = {
        key: work
        for name, packet in packets.items()
        for key, work in rehearsal.work_pair(name, packet).items()
    }
    cells = plan.render(works)
    gold = (frozen / "gold.json").read_bytes()
    require(gold == encoded(rehearsal.gold(packets)), "q011_scope_regression_gold")
    output = frozen / "output"
    previous = (output / "header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["origin"] == "observed_openai_transport" and header["approval"] == APPROVAL,
        "q011_scope_regression_origin",
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
            and slot["work_sha256"] == cell.work.fingerprint
            and slot["slot"] == record["slot"] == i
            and slot["cell"] == record["cell"] == cell.name
            and (frozen / slot["filename"]).read_bytes() == end.body_utf8.encode()
            and slot["body_bytes_sha256"] == record["request_body_sha256"] == end.body_bytes_sha256,
            "q011_scope_regression_request",
        )
        previous = (output / (stem + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous)
        require(
            terminal.intent_sha256 == digest(message)
            and terminal.http_status == 200
            and terminal.request_id == record["request_id"]
            and terminal.raw_sha256 == record["terminal_body_sha256"],
            "q011_scope_regression_terminal",
        )
        state, details = evaluate(cell, end, terminal)
        generation = end.stage == "generation"
        require(
            state == ("bound_unassessed" if generation else "count_admitted"),
            "q011_scope_regression_delivery",
        )
        if generation:
            assert terminal.body is not None
            mapped = map_response(end.stage, 200, terminal.body.encode(), cell.wire.model_spec)
            require(
                mapped.raw_final_utf8_sha256 == record["raw_final_sha256"],
                "q011_scope_regression_final",
            )
        observed["slots"].append(
            dict(cell=cell.name, stage=end.stage, state=state, eligible=generation, **details)
        )
    require(
        (output / "close.json").read_bytes() == closure(previous, observed["state"])
        and encoded(observed) == (operator / "audit.json").read_bytes(),
        "q011_scope_regression_closure",
    )
    sheet = evidence_sheet(observed)
    require(
        encoded(dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet))
        == (operator / "worksheet.json").read_bytes(),
        "q011_scope_regression_worksheet",
    )
    decisions = (frozen / "sealed-evidence-decisions.json").read_bytes()
    result = scoring.scores(observed, decisions, gold)
    require(
        decisions == (operator / "evidence-form.json").read_bytes()
        and encoded(result) == (operator / "scores.json").read_bytes()
        and result["decision"] == "hold",
        "q011_scope_regression_scores",
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
