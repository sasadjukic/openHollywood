"""Preserve the twelve paired Sol deliveries and replay their two sealed scores offline."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import REPO, Cell, digest, schedule
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent
from scripts.wading_path_observations.plan import selected_work
from scripts.wading_path_observations.regression import inventory
from scripts.wading_path_three_claims.plan import authored_cell
from scripts.wading_path_visit_position import narration_event as rehearsal
from scripts.wading_path_visit_position import regression as prior

from . import plan, scoring
from .run import evaluate

ARCHIVE = plan.ROOT.parent / "wading-path-sol-versions-regression-2026-11-25"
RESULTS = plan.ROOT.parent / "wading-path-sol-versions-results-2026-11-25"
APPROVAL = "6eaadeb7d5290667d3e63a47eb9974a0d1d9f89ba9f5bda2f5a5d45934a40a93"
SEAL = "85488b224f425cde697760ec722e62d21f77aec50aa52ea8366f5b2b7cf7d71b"
EVIDENCE_SEAL = "9197f99a29dc576d63a6b7bbe5cc8fe0ffbf0d41e1d1061cb59bda18c1d70ea0"


def verified(archive: Path) -> Path:
    raw = (archive / "capture-manifest.json").read_bytes()
    require(digest(raw) == SEAL, "sol_versions_archive_seal")
    capture = archive / "capture"
    require(
        {k: file_hash(p) for k, p in inventory(capture).items()} == json.loads(raw),
        "sol_versions_archive_members",
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
    files["source/intake.json"] = old / "source/intake.json"
    files["source/narration-event-gold.json"] = (
        REPO / "tests/fixtures/wading_path_narration_event_gold.json"
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


def archived_cells(capture: Path) -> list[Cell]:
    gold = json.loads((capture / "source/narration-event-gold.json").read_bytes())
    require(canonical_sha256(gold) == rehearsal.GOLD_SHA, "sol_versions_rehearsal")
    source = IntakeSource.model_validate_json((capture / "source/intake.json").read_bytes())
    manifest = json.loads((capture / "run/plan.json").read_bytes())
    versions = tuple(UUID(v) for v in manifest["historical_source_versions"])
    locations = json.loads((capture / "operator/cited-locations.json").read_bytes())
    pairs = {}
    for case, (ending, predicate) in plan.CASES.items():
        loc = locations[case]["E1420"]
        version = gold["endings"][ending]["version"]
        require(
            loc["document_version"] == version
            and text_hash(loc["quote"]) == gold["endings"][ending]["prose_sha256"],
            "sol_versions_source",
        )
        draft = selected_work(source, "Q008", loc["quote"], version, authored=True)
        invoked = (*versions, UUID(version))
        first = authored_cell(draft, gold["claims"][predicate], invoked)
        ref = next(r for r in _registry(first.work).entries if r.ref == "E1420")
        require(ref.model_dump(mode="json") == loc, "sol_versions_citation")
        pairs[case + "-61"] = Cell(case + "-61", first.work, first.wire)
        pairs[case + "-62"] = plan.paired_cell(
            first, case + "-62", plan.specifications()["62"], invoked
        )
    return [pairs[k] for k in plan.ORDER]


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    capture = verified(archive)
    frozen, operator = capture / "run", capture / "operator"
    output = frozen / "output"
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "sol_versions_registration",
    )
    manifest = json.loads((frozen / "plan.json").read_bytes())
    previous = (output / "header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["origin"] == "observed_openai_transport" and header["approval"] == APPROVAL,
        "sol_versions_origin",
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
            and slot["expected_model"] == cell.wire.model_spec.model_identifier
            and (slot["cell"], slot["stage"]) == (cell.name, end.stage)
            and message == intent(previous, cell, end)
            and slot["work_sha256"] == cell.work.fingerprint
            and slot["native_request_sha256"] == cell.wire.native_request_sha256
            and (frozen / slot["filename"]).read_bytes() == end.body_utf8.encode(),
            "sol_versions_request",
        )
        previous = (output / (stem + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous)
        require(terminal.intent_sha256 == digest(message), "sol_versions_terminal")
        state, details = evaluate(cell, end, terminal)
        eligible = end.stage == "generation"
        require(
            state == ("bound_unassessed" if eligible else "count_admitted"),
            "sol_versions_delivery",
        )
        audit["slots"].append(
            dict(cell=cell.name, stage=end.stage, state=state, eligible=eligible, **details)
        )
    require(
        (output / "close.json").read_bytes() == closure(previous, audit["state"])
        and encoded(audit) == (operator / "audit.json").read_bytes(),
        "sol_versions_audit",
    )
    sheet = evidence_sheet(audit)
    form = (frozen / "sealed-evidence-decisions.json").read_bytes()
    scores = scoring.scores(audit, form, (frozen / "gold.json").read_bytes())
    require(
        digest(form) == EVIDENCE_SEAL
        and encoded(dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet))
        == (operator / "evidence-sheet.json").read_bytes()
        and encoded(scores) == (operator / "scores.json").read_bytes(),
        "sol_versions_scores",
    )
    return dict(manifest_sha256=SEAL, slots=len(audit["slots"]), live_calls=0, **scores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preserve", action="store_true")
    if parser.parse_args().preserve:
        preserve()
    print(json.dumps(replay(), indent=2))
