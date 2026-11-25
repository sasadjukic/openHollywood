"""Preserve the six observed B deliveries and replay their two sealed scores offline."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import UUID, uuid5

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import REPO, Cell, digest, schedule
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent
from scripts.q011_arrival.run import evaluate
from scripts.wading_path_observations.plan import selected_work
from scripts.wading_path_observations.regression import inventory
from scripts.wading_path_three_claims import regression as prior
from scripts.wading_path_three_claims.plan import authored_cell
from scripts.wading_path_three_claims.visit_position import GOLD_SHA

from . import plan, scoring

ARCHIVE = plan.ROOT.parent / "wading-path-visit-position-regression-2026-11-25"
RESULTS = plan.ROOT.parent / "wading-path-visit-position-results-2026-11-25"
APPROVAL = "e6274e578c2036d5be76318b0e30cb16d9e61f47791ec20102c72b5d2c1bcbb6"
SEAL = "6339d86c0c033d470161f9b931f3bc09ac6bb3b06d522feb2ddc80e4ce132344"
EVIDENCE_SEAL = "c25863bfb6b4002cb9758d87c42f600abbadfeb9c6442b05edc1e630bde32b23"
HISTORY = {
    "intake.json": "source/intake.json",
    "source-locations.json": "source/previous-locations.json",
    "prior-locations.json": "operator/cited-locations.json",
    "prior-sheet.json": "operator/evidence-sheet.json",
    "prior-scores.json": "operator/scores.json",
}


def verified(archive: Path) -> Path:
    raw = (archive / "capture-manifest.json").read_bytes()
    require(digest(raw) == SEAL, "visit_position_archive_seal")
    capture = archive / "capture"
    require(
        {k: file_hash(p) for k, p in inventory(capture).items()} == json.loads(raw),
        "visit_position_archive_members",
    )
    return capture


def preserve() -> None:
    if ARCHIVE.exists():
        verified(ARCHIVE)
        return
    old = prior.verified(prior.ARCHIVE)
    files = {"run/" + k: p for k, p in inventory(plan.ROOT).items()}
    for name in ("audit", "cited-locations", "evidence-sheet", "scores", "slot-inspection"):
        files[f"operator/{name}.json"] = RESULTS / f"{name}.json"
    files.update({"source/" + k: old / v for k, v in HISTORY.items()})
    files["source/previous-manifest.json"] = prior.ARCHIVE / "capture-manifest.json"
    files["source/rehearsal-gold.json"] = (
        REPO / "tests/fixtures/wading_path_visit_position_gold.json"
    )
    with TemporaryDirectory(dir=ARCHIVE.parent) as tmp:
        staged = Path(tmp) / "archive"
        for name, path in files.items():
            dst = staged / "capture" / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dst)
        hashes = {k: file_hash(p) for k, p in inventory(staged / "capture").items()}
        (staged / "capture-manifest.json").write_bytes(encoded(hashes))
        verified(staged)
        staged.rename(ARCHIVE)


def source_drafts(capture: Path) -> tuple[dict[str, Any], dict[str, str]]:
    sources = capture / "source"
    parent = (sources / "previous-manifest.json").read_bytes()
    members = json.loads(parent)
    require(
        digest(parent) == prior.SEAL
        and all(file_hash(sources / k) == members[v] for k, v in HISTORY.items()),
        "visit_position_history",
    )
    gold = json.loads((sources / "rehearsal-gold.json").read_bytes())
    require(canonical_sha256(gold) == GOLD_SHA, "visit_position_rehearsal_gold")
    locations = json.loads((sources / "source-locations.json").read_bytes())
    drafts = {}
    for ending, old_case in (("stop", "K3"), ("arrival", "K2")):
        loc = locations[old_case]["E1420"]
        entry = gold["endings"][ending]
        prose = loc["quote"]
        require(
            loc["document_version"] == entry["version"]
            and text_hash(prose) == entry["prose_sha256"],
            "visit_position_source_version",
        )
        drafts[ending] = prose
    exclusion = gold["endings"]["exclusion"]
    parent_version = gold["endings"]["stop"]["version"]
    prose = drafts["stop"] + "\n\n" + exclusion["append_paragraph"]
    sha = text_hash(prose)
    require(
        exclusion["parent"] == "stop"
        and exclusion["parent_version"] == parent_version
        and sha == exclusion["prose_sha256"]
        and str(uuid5(UUID(parent_version), sha)) == exclusion["version"],
        "visit_position_exclusion",
    )
    drafts["exclusion"] = prose
    return gold, drafts


def archived_cells(capture: Path) -> list[Cell]:
    frozen = capture / "run"
    source = IntakeSource.model_validate_json((capture / "source/intake.json").read_bytes())
    gold, drafts = source_drafts(capture)
    plan_body = json.loads((frozen / "plan.json").read_bytes())
    versions = tuple(UUID(v) for v in plan_body["historical_source_versions"])
    locations = json.loads((capture / "operator/cited-locations.json").read_bytes())
    cells = []
    for case, (ending, predicate) in plan.CASES.items():
        name = case + "-B"
        version = gold["endings"][ending]["version"]
        work = selected_work(source, "Q008", drafts[ending], version, authored=True)
        cell = authored_cell(work, gold["claims"][predicate], (*versions, UUID(version)))
        refs = {r.ref: r.model_dump(mode="json") for r in _registry(cell.work).entries}
        require(
            all(refs[k] == loc for k, loc in locations[case].items()), "visit_position_citation"
        )
        cells.append(Cell(name, cell.work, cell.wire))
    return cells


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    capture = verified(archive)
    frozen, operator = capture / "run", capture / "operator"
    output = frozen / "output"
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "visit_position_registration",
    )
    manifest = json.loads((frozen / "plan.json").read_bytes())
    previous = (output / "header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["origin"] == "observed_openai_transport" and header["approval"] == APPROVAL,
        "visit_position_origin",
    )
    audit: Audit = dict(
        approval=APPROVAL,
        origin=header["origin"],
        ledger="dispatched",
        closed=True,
        state="bound_unassessed",
        slots=[],
    )
    for i, ((cell, end), slot) in enumerate(
        zip(schedule(archived_cells(capture)), manifest["slots"], strict=True), 1
    ):
        stem = f"{i:02d}-{cell.name}-{end.stage}"
        message = (output / (stem + "-intent.json")).read_bytes()
        require(
            slot["slot"] == i
            and (slot["cell"], slot["stage"]) == (cell.name, end.stage)
            and message == intent(previous, cell, end)
            and slot["work_sha256"] == cell.work.fingerprint
            and slot["native_request_sha256"] == cell.wire.native_request_sha256
            and (frozen / slot["filename"]).read_bytes() == end.body_utf8.encode(),
            "visit_position_request",
        )
        previous = (output / (stem + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous)
        require(terminal.intent_sha256 == digest(message), "visit_position_terminal")
        state, details = evaluate(cell, end, terminal)
        eligible = end.stage == "generation"
        require(
            state == ("bound_unassessed" if eligible else "count_admitted"),
            "visit_position_delivery",
        )
        audit["slots"].append(
            dict(cell=cell.name, stage=end.stage, state=state, eligible=eligible, **details)
        )
    require(
        (output / "close.json").read_bytes() == closure(previous, audit["state"])
        and encoded(audit) == (operator / "audit.json").read_bytes(),
        "visit_position_audit",
    )
    sheet = evidence_sheet(audit)
    form = (frozen / "sealed-evidence-decisions.json").read_bytes()
    scores = scoring.scores(audit, form, (frozen / "gold.json").read_bytes())
    require(
        digest(form) == EVIDENCE_SEAL
        and encoded(dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet))
        == (operator / "evidence-sheet.json").read_bytes()
        and encoded(scores) == (operator / "scores.json").read_bytes(),
        "visit_position_scores",
    )
    return dict(manifest_sha256=SEAL, slots=len(audit["slots"]), live_calls=0, **scores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preserve", action="store_true")
    if parser.parse_args().preserve:
        preserve()
    print(json.dumps(replay(), indent=2))
