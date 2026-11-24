"""Preserve the seven observed B deliveries and replay their two sealed scores offline."""

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
from scripts.wading_path_be import plan as baseline
from scripts.wading_path_observations import regression as prior
from scripts.wading_path_observations.plan import selected_work
from scripts.wading_path_observations.three_claims import GOLD_SHA

from . import plan, scoring

ARCHIVE = plan.ROOT.parent / "wading-path-three-claims-regression-2026-11-24"
RESULTS = plan.ROOT.parent / "wading-path-three-claims-results-2026-11-24"
APPROVAL = "91285c0d71c0e48e92ba22abf6d83e93b97b2bfc21be015e64cb7b739c45c137"
SEAL = "344884c7adbb929cd2c57ecb16e9c6d319393730d374504180aa91b535e825ee"
EVIDENCE_SEAL = "ccbf9d191fa697ef5ff9eadd48d05cb921237e6dbb0ae588f1a98c68f1f020f4"
HISTORY = {
    "intake.json": "source/intake.json",
    "previous-plan.json": "run/plan.json",
    "previous-locations.json": "operator/cited-locations.json",
}


def verified(archive: Path) -> Path:
    raw = (archive / "capture-manifest.json").read_bytes()
    require(digest(raw) == SEAL, "three_claims_archive_seal")
    capture = archive / "capture"
    require(
        {k: file_hash(p) for k, p in prior.inventory(capture).items()} == json.loads(raw),
        "three_claims_archive_members",
    )
    return capture


def preserve() -> None:
    if ARCHIVE.exists():
        verified(ARCHIVE)
        return
    old = prior.verified(prior.ARCHIVE)
    files = {"run/" + k: p for k, p in prior.inventory(plan.ROOT).items()}
    for name in ("audit", "cited-locations", "evidence-sheet", "scores", "slot-inspection"):
        files[f"operator/{name}.json"] = RESULTS / f"{name}.json"
    files.update({"source/" + k: old / v for k, v in HISTORY.items()})
    files["source/previous-manifest.json"] = prior.ARCHIVE / "capture-manifest.json"
    files["source/rehearsal-gold.json"] = REPO / "tests/fixtures/wading_path_three_claims_gold.json"
    with TemporaryDirectory(dir=ARCHIVE.parent) as tmp:
        staged = Path(tmp) / "archive"
        for name, path in files.items():
            dst = staged / "capture" / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dst)
        hashes = {k: file_hash(p) for k, p in prior.inventory(staged / "capture").items()}
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
        "three_claims_history",
    )
    gold = json.loads((sources / "rehearsal-gold.json").read_bytes())
    require(canonical_sha256(gold) == GOLD_SHA, "three_claims_rehearsal_gold")
    locations = json.loads((sources / "previous-locations.json").read_bytes())
    drafts = {}
    for name, entry in gold["endings"].items():
        archived = locations[entry["source_case"]]["E1420"]
        prose = archived["quote"]
        if "append_paragraph" in entry:
            prose += "\n\n" + entry["append_paragraph"]
            version = uuid5(UUID(locations["K1"]["E1420"]["document_version"]), text_hash(prose))
            require(str(version) == entry["version"], "three_claims_authored_version")
        else:
            require(archived["document_version"] == entry["version"], "three_claims_version")
        require(text_hash(prose) == entry["prose_sha256"], "three_claims_prose")
        drafts[name] = prose
    return gold, drafts


def archived_cells(capture: Path) -> list[Cell]:
    frozen = capture / "run"
    source = IntakeSource.model_validate_json((capture / "source/intake.json").read_bytes())
    gold, drafts = source_drafts(capture)
    plan_body = json.loads((frozen / "plan.json").read_bytes())
    versions = tuple(UUID(v) for v in plan_body["historical_source_versions"])
    locations = json.loads((capture / "operator/cited-locations.json").read_bytes())
    previous = json.loads((capture / "source/previous-plan.json").read_bytes())
    q008_hashes = {
        s["stage"]: s["body_bytes_sha256"] for s in previous["slots"] if s["cell"] == "Q008-B"
    }
    cells = []
    for name in plan.ORDER:
        case = name.split("-")[0]
        ending, predicate = plan.CASES.get(case, ("original", "control"))
        version = gold["endings"][ending]["version"]
        work = selected_work(source, "Q008", drafts[ending], version, ending == "retreat")
        if case == "Q008":
            raw = (frozen / "requests/Q008-B-generation.json").read_bytes()
            packet = json.loads(json.loads(raw)["input"][1]["content"])
            row = dict(
                unit=case,
                arm="B",
                work_sha256=work.fingerprint,
                declaration=packet["claim_scope"],
                brief=packet["work_brief"],
            )
            cell = baseline.render(work, row, versions)
            require(
                all(e.body_bytes_sha256 == q008_hashes[e.stage] for e in cell.wire.endpoints),
                "three_claims_control_drift",
            )
        else:
            invoked = (*versions, UUID(version)) if ending == "retreat" else versions
            cell = plan.authored_cell(work, gold["claims"][predicate], invoked)
        refs = {r.ref: r.model_dump(mode="json") for r in _registry(cell.work).entries}
        require(all(refs[k] == loc for k, loc in locations[case].items()), "three_claims_citation")
        cells.append(Cell(name, cell.work, cell.wire))
    return cells


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    capture = verified(archive)
    frozen, operator = capture / "run", capture / "operator"
    output = frozen / "output"
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "three_claims_registration",
    )
    manifest = json.loads((frozen / "plan.json").read_bytes())
    previous = (output / "header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["origin"] == "observed_openai_transport" and header["approval"] == APPROVAL,
        "three_claims_origin",
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
            "three_claims_request",
        )
        previous = (output / (stem + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous)
        require(terminal.intent_sha256 == digest(message), "three_claims_terminal")
        state, details = evaluate(cell, end, terminal)
        eligible = end.stage == "generation"
        require(
            state == ("bound_unassessed" if eligible else "count_admitted"), "three_claims_delivery"
        )
        audit["slots"].append(
            dict(cell=cell.name, stage=end.stage, state=state, eligible=eligible, **details)
        )
    require(
        (output / "close.json").read_bytes() == closure(previous, audit["state"])
        and encoded(audit) == (operator / "audit.json").read_bytes(),
        "three_claims_audit",
    )
    sheet = evidence_sheet(audit)
    form = (frozen / "sealed-evidence-decisions.json").read_bytes()
    scores = scoring.scores(audit, form, (frozen / "gold.json").read_bytes())
    require(
        digest(form) == EVIDENCE_SEAL
        and encoded(dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet))
        == (operator / "evidence-sheet.json").read_bytes()
        and encoded(scores) == (operator / "scores.json").read_bytes(),
        "three_claims_scores",
    )
    return dict(manifest_sha256=SEAL, slots=len(audit["slots"]), live_calls=0, **scores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preserve", action="store_true")
    if parser.parse_args().preserve:
        preserve()
    print(json.dumps(replay(), indent=2))
