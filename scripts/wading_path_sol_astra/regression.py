"""Preserve the closed Sol/Astra comparison and replay its signed-off evidence offline."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import Cell, digest, schedule
from scripts.q010_uncertainty_run import closure, evidence_sheet, intent
from scripts.wading_path_observations.regression import inventory
from scripts.wading_path_sol_versions import evidence_coverage as coverage
from scripts.wading_path_sol_versions import regression as prior
from scripts.wading_path_sol_versions.plan import paired_cell
from scripts.wading_path_sol_versions.run import evaluate

from . import plan, scoring

ARCHIVE = plan.ROOT.parent / "wading-path-sol-astra-scope-regression-2026-11-25"
RESULTS = plan.ROOT.parent / "wading-path-sol-astra-scope-results-2026-11-25"
APPROVAL = "01513dd73de11e779413b554a9bb04703e8706d2c6ca4620e254cbb84890c7dd"
SEAL = "f9c97479ca0db118a9f02712a496eb9691da560bf0f37843ce9441bb7c7bfeb9"
EVIDENCE_SEAL = "0c79fb8baf8b96195ec2a5cf11b0d7ca5e5c4be5c06b3e6a3cf6e3b77b93522d"

# Manual readings of the four saved reasons. The inherited rule checks their source coverage.
OPEN_EVENT_READINGS = {
    "SB": {
        "uses": {"approach": "enter the service plenum", "gap": "three full strides short"},
        "asserts": {"short_at_cut": "stay there through the end of the scene"},
    },
    "SX": {
        "uses": {
            "approach": "the preceding sequence shows their approach",
            "gap": "three full strides short",
        },
        "asserts": {
            "short_at_cut": "That final observation covers only the closing interval",
            "no_visit": "They never reach the housing during the scene.",
        },
    },
    "AB": {
        "uses": {
            "approach": "see the housing at the end of the passage",
            "gap": "three full strides short",
        },
        "asserts": {"no_visit": "Neither reaches the housing at any point in the scene."},
    },
    "AX": {
        "uses": {
            "approach": "entering the plenum and seeing the housing",
            "gap": "stop three full strides short of the housing when the light steadies",
        },
        "asserts": {
            "short_at_cut": "That rules out arrival from the stop onward.",
            "open_visit": "does not establish an earlier arrival, "
            "and the closing observation does not rule one out",
        },
    },
}


def verified(archive: Path) -> Path:
    manifest = (archive / "capture-manifest.json").read_bytes()
    require(digest(manifest) == SEAL, "scope_archive_seal")
    capture = archive / "capture"
    require(
        {k: file_hash(p) for k, p in inventory(capture).items()} == json.loads(manifest),
        "scope_archive_members",
    )
    return capture


def preserve() -> None:
    if ARCHIVE.exists():
        verified(ARCHIVE)
        return
    old = prior.verified(prior.ARCHIVE)
    files = {"run/" + k: p for k, p in inventory(plan.ROOT).items()}
    for name in ("audit", "scores", "evidence-sheet", "slot-inspection", "cited-locations"):
        files[f"operator/{name}.json"] = RESULTS / f"{name}.json"
    for name in ("intake", "narration-event-gold"):
        files[f"source/{name}.json"] = old / f"source/{name}.json"
    files["source/previous-manifest.json"] = prior.ARCHIVE / "capture-manifest.json"
    files["source/previous-scores.json"] = old / "operator/scores.json"
    with TemporaryDirectory(dir=ARCHIVE.parent) as tmp:
        staged = Path(tmp) / "archive"
        for name, path in files.items():
            dst = staged / "capture" / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dst)
        manifest = encoded({k: file_hash(p) for k, p in inventory(staged / "capture").items()})
        (staged / "capture-manifest.json").write_bytes(manifest)
        verified(staged)
        staged.rename(ARCHIVE)


def archived_cells(capture: Path, manifest: dict[str, Any]) -> list[Cell]:
    historical = tuple(UUID(v) for v in manifest["historical_source_versions"])
    previous_members = json.loads((capture / "source/previous-manifest.json").read_bytes())
    specs = plan.specifications()
    cells = {}
    for base in prior.archived_cells(capture):
        case, old_model = base.name.split("-")
        if old_model != "62":
            continue
        versions = (*historical, UUID(manifest["assessment_draft_versions"][case]))
        explicit = plan.explicit_cell(base, plan.CASES[case][1], versions)
        for end in base.wire.endpoints:
            require(
                digest(end.body_utf8.encode())
                == previous_members[f"run/requests/{case}-62-{end.stage}.json"],
                "scope_archived_sol_baseline",
            )
        for arm in plan.ARMS:
            name = f"{case}-{arm}"
            source = base if arm[1] == "B" else explicit
            cells[name] = (
                Cell(name, base.work, base.wire)
                if arm == "SB"
                else paired_cell(source, name, specs[arm[0]], versions)
            )
    return [cells[name] for name in plan.ORDER]


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    capture = verified(archive)
    root, operator = capture / "run", capture / "operator"
    manifest = json.loads((root / "plan.json").read_bytes())
    require(
        file_hash(root / "plan.json") == APPROVAL
        and ledger_state(root, APPROVAL) == "dispatched"
        and file_hash(capture / "source/previous-manifest.json")
        == manifest["archive_sha256"]
        == prior.SEAL,
        "scope_registration",
    )
    audit = json.loads((operator / "audit.json").read_bytes())
    scores_file = operator / "scores.json"
    form = (root / "sealed-evidence-decisions.json").read_bytes()
    gold = (root / "gold.json").read_bytes()
    key = json.loads(gold)
    previous = (root / "output/header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["origin"] == audit["origin"] == "observed_openai_transport"
        and header["approval"] == audit["approval"] == APPROVAL
        and audit["closed"]
        and audit["ledger"] == "dispatched"
        and audit["state"] == "bound_unassessed",
        "scope_archive_origin",
    )
    inspection = json.loads((operator / "slot-inspection.json").read_bytes())["slots"]
    rows, counts = {}, {}
    cells = archived_cells(capture, manifest)
    for (cell, end), slot, observed, inspected in zip(
        schedule(cells), manifest["slots"], audit["slots"], inspection, strict=True
    ):
        i = slot["slot"]
        case, arm = cell.name.split("-")
        stem = root / "output" / f"{i:02d}-{cell.name}-{end.stage}"
        message = stem.with_name(stem.name + "-intent.json").read_bytes()
        require(
            (slot["cell"], slot["stage"]) == (cell.name, end.stage)
            and (root / slot["filename"]).read_bytes() == end.body_utf8.encode()
            and message == intent(previous, cell, end),
            "scope_request_chain",
        )
        previous = stem.with_name(stem.name + "-outcome.json").read_bytes()
        terminal = Terminal.model_validate_json(previous)
        state, details = evaluate(cell, end, terminal)
        eligible = end.stage == "generation"
        require(
            terminal.intent_sha256 == digest(message)
            and digest(previous) == inspected["terminal_sha256"]
            and state == ("bound_unassessed" if eligible else "count_admitted")
            and encoded(observed)
            == encoded(
                dict(cell=cell.name, stage=end.stage, state=state, eligible=eligible, **details)
            ),
            "scope_delivery",
        )
        if not eligible:
            counts[cell.name] = dict(slot=i, terminal_sha256=digest(previous))
            continue
        answer = observed["final"]["assessments"]["A001"]
        require(
            answer["evidence"] == ["E1420"] and observed["returned_model"] == plan.MODELS[arm[0]],
            "scope_returned_binding",
        )
        rows[cell.name] = dict(
            model=observed["returned_model"],
            claim=key[case]["claim"],
            draft_version=key[case]["draft_version"],
            prose_sha256=key[case]["prose_sha256"],
            gold=key[case]["gold"],
            returned=answer["support"],
            reason=answer["reason"],
            citations=answer["evidence"],
            count_slot=counts[cell.name]["slot"],
            generation_slot=i,
            count_terminal_sha256=counts[cell.name]["terminal_sha256"],
            generation_terminal_sha256=digest(previous),
            native_request_sha256=cell.wire.native_request_sha256,
            usage=observed["usage"],
            elapsed_seconds=observed["elapsed_seconds"],
        )
    require(
        (root / "output/close.json").read_bytes() == closure(previous, audit["state"]),
        "scope_closure",
    )
    sheet = evidence_sheet(audit)
    require(
        encoded(dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet))
        == (operator / "evidence-sheet.json").read_bytes()
        and digest(form) == EVIDENCE_SEAL,
        "scope_evidence_seal",
    )
    scored = scoring.scores(audit, form, gold)
    require(encoded(scored) == scores_file.read_bytes(), "scope_score_replay")
    for name, row in scored["rows"].items():
        rows[name].update(
            judgment=row["judgment"], evidence=row["evidence"], evidence_basis=row["basis"]
        )
    return dict(
        archive_sha256=SEAL,
        approval_sha256=APPROVAL,
        evidence_decisions_sha256=EVIDENCE_SEAL,
        rows=rows,
    )


def open_event_audit(capture: Path, rows: dict[str, Any]) -> dict[str, Any]:
    gold = json.loads((capture / "source/narration-event-gold.json").read_bytes())
    locations = json.loads((capture / "operator/cited-locations.json").read_bytes())
    result = {}
    for arm, reading in OPEN_EVENT_READINGS.items():
        row = rows["SE-" + arm]
        require(
            row["claim"] == gold["claims"]["reached"] and row["citations"] == ["E1420"],
            "open_event_claim",
        )
        ranges = coverage.source_ranges(locations["SE"]["E1420"], row["draft_version"], gold)
        result[arm] = coverage.assess("event", row["reason"], reading, ranges)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preserve", action="store_true")
    if parser.parse_args().preserve:
        preserve()
    observations = replay()
    print(json.dumps(open_event_audit(verified(ARCHIVE), observations["rows"]), indent=2))
