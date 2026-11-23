"""Replay both observed Q011 deliveries and their sealed scores from a private offline copy."""

from __future__ import annotations

import json
from pathlib import Path

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import map_response

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import Cell, digest, schedule
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent

from . import plan, run, scoring, sources

ARCHIVE = sources.DATA / "q011-arrival-regression-2026-11-23"
SEAL = "6fd99ab0749bdc1c47f2c9e9270b96cf7200ab34ceb7f0c7a004aeb42813c4b2"
APPROVAL = "91a2d35d1519f0f42b72b7f6197c86cd60fb6c9e1f8fd2db6967e3941d5dde2c"
FINALS = {
    "A-B": "de9c0b3b8ffffc4a3c324a3b77c502d8dad10e4a915fafdfb4e14083e77450d4",
    "B-B": "84fd04d58346924a163b5894b71544140f46235af6f42d7f56f451c668834ef7",
}


def archived_cell(capture: Path, case: str) -> Cell:
    packet = json.loads((capture / f"source/{case}.json").read_bytes())
    request = json.loads((capture / f"run/requests/{case}-B-generation.json").read_bytes())
    docs = json.loads(request["input"][1]["content"])["native_work_view"]["context"]["documents"]
    # The packet JSON sorts object keys. The wire's ordered document array preserves
    # the original presentation order, which also participates in the work fingerprint.
    context = packet["context"]
    packet["context"] = {
        d["identity"]: context[d["identity"]] for d in docs if d["identity"] in context
    }
    require(packet["context"].keys() == context.keys(), "q011_regression_source_documents")
    return plan.render(case, packet)


def replay(archive: Path = ARCHIVE) -> dict[str, object]:
    manifest = (archive / "capture-manifest.json").read_bytes()
    require(digest(manifest) == SEAL, "q011_regression_seal")
    members = json.loads(manifest)
    capture = archive / "capture"
    inventory = {p.relative_to(capture).as_posix() for p in capture.rglob("*") if p.is_file()}
    require(inventory == set(members), "q011_regression_inventory")
    for name, expected in members.items():
        require(file_hash(capture / name) == expected, "q011_regression_member")

    frozen = capture / "run"
    operator = capture / "operator"
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "q011_regression_approval",
    )
    cells = [archived_cell(capture, k) for k in sources.CASES]
    issued = json.loads((frozen / "plan.json").read_bytes())
    audit: Audit = json.loads((operator / "audit.json").read_bytes())
    output = frozen / "output"
    previous = (output / "header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["origin"] == audit["origin"] == "observed_openai_transport"
        and header["approval"] == audit["approval"] == APPROVAL
        and audit["closed"]
        and audit["ledger"] == "dispatched",
        "q011_regression_origin",
    )
    for index, ((cell, end), slot, row) in enumerate(
        zip(schedule(cells), issued["slots"], audit["slots"], strict=True), 1
    ):
        prefix = f"{index:02d}-{cell.name}-{end.stage}"
        message = (output / (prefix + "-intent.json")).read_bytes()
        require(
            message == intent(previous, cell, end)
            and cell.work.fingerprint == slot["work_sha256"]
            and (frozen / slot["filename"]).read_bytes() == end.body_utf8.encode()
            and end.body_bytes_sha256 == slot["body_bytes_sha256"],
            "q011_regression_request",
        )
        previous = (output / (prefix + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous)
        require(
            terminal.intent_sha256 == digest(message) and terminal.http_status == 200,
            "q011_regression_terminal",
        )
        state, observed = run.evaluate(cell, end, terminal)
        eligible = end.stage == "generation"
        rebuilt = dict(cell=cell.name, stage=end.stage, eligible=eligible, state=state, **observed)
        require(
            state == ("bound_unassessed" if eligible else "count_admitted")
            and encoded(row) == encoded(rebuilt),
            "q011_regression_mapping_or_binding",
        )
        if eligible:
            assert terminal.body is not None
            mapped = map_response(end.stage, 200, terminal.body.encode(), cell.wire.model_spec)
            require(mapped.raw_final_utf8_sha256 == FINALS[cell.name], "q011_regression_final")
    require(
        (output / "close.json").read_bytes() == closure(previous, audit["state"]),
        "q011_regression_closure",
    )

    sheet = evidence_sheet(audit)
    require(
        json.loads((operator / "worksheet.json").read_bytes())
        == dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet),
        "q011_regression_worksheet",
    )
    gold = (frozen / "gold.json").read_bytes()
    decisions = (frozen / "sealed-evidence-decisions.json").read_bytes()
    result = scoring.scores(audit, decisions, gold)
    require(
        encoded(result) == (operator / "scores.json").read_bytes() and result["decision"] == "hold",
        "q011_regression_scores",
    )
    rows = result["cases"]
    assert isinstance(rows, list)
    outcomes = [
        (r["case"], r["returned"], r["expected"], r["judgment"], r["evidence"]) for r in rows
    ]
    require(
        outcomes
        == [
            ("A", "unsupported", "uncertain", "fail", "fail"),
            ("B", "supported", "supported", "pass", "pass"),
        ],
        "q011_regression_pair",
    )
    return dict(
        manifest_sha256=SEAL,
        members=len(members),
        raw_final_sha256=FINALS,
        cases=outcomes,
        decision=result["decision"],
        live_calls=0,
    )


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
