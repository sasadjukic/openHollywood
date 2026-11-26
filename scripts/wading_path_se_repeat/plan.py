"""Freeze repeats from the sealed November 25 wires. Repetition exists only in the journal."""

from __future__ import annotations

import json
from pathlib import Path

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.review_evidence import require

from scripts import ordinary_v61_capture as ledger
from scripts.q010_uncertainty_plan import REPO, Cell, digest, filename, schedule
from scripts.wading_path_sol_astra import plan as prior
from scripts.wading_path_sol_astra import regression

from .rubric import CRITERIA, RULES, Decisions

ROOT = prior.ROOT.parent / "wading-path-se-repeat-2026-11-26"
ARMS, WALL_SECONDS = prior.ARMS, prior.WALL_SECONDS
BLOCKS = (
    ("SE", 1, "SB SX AX AB"),
    ("VE", 1, "AX AB SX SB"),
    ("SE", 2, "SX AB SB AX"),
    ("SE", 3, "AB AX SX SB"),
    ("XE", 1, "SB SX AB AX"),
    ("SE", 4, "AX SB AB SX"),
)
ORDER = tuple(f"{case}-{arm}-{rep}" for case, rep, group in BLOCKS for arm in group.split())
FILES = (
    *prior.FILES,
    "scripts/wading_path_sol_astra/regression.py",
    "scripts/wading_path_se_repeat/plan.py",
    "scripts/wading_path_se_repeat/run.py",
    "scripts/wading_path_se_repeat/rubric.py",
    "scripts/wading_path_se_repeat/scoring.py",
    "tests/fixtures/scope_boundary_rehearsal_expected.json",
    "tests/fixtures/scope_boundary_rehearsal_pairs.json",
)


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    capture = regression.verified(regression.ARCHIVE)
    source = capture / "run"
    raw = _read(source / "plan.json")
    require(digest(raw) == regression.APPROVAL, "historical_plan_drift")
    history = json.loads(raw)
    previous = {c.name: c for c in regression.archived_cells(capture, history)}
    cells = []
    for name in ORDER:
        old = previous[name.rsplit("-", 1)[0]]
        cells.append(Cell(name, old.work, old.wire))
    references = json.loads(_read(capture / "operator/cited-locations.json"))
    gold = json.loads(_read(source / "gold.json"))
    cases = tuple(CRITERIA)
    assets = {
        "gold.json": encoded({k: gold[k] for k in cases}),
        "drafts.json": encoded({k: references[k]["E1420"] for k in cases}),
        "scoring.json": encoded(dict(rules=RULES, cases=CRITERIA)),
        "evidence-form-schema.json": encoded(Decisions.model_json_schema()),
    }
    slots = []
    for i, (cell, end) in enumerate(schedule(cells), 1):
        base_name = cell.name.rsplit("-", 1)[0]
        archived = "requests/" + filename(previous[base_name], end)
        path = "requests/" + filename(cell, end)
        body = _read(source / archived)
        require(body == end.body_utf8.encode(), "historical_wire_drift")
        assets[path] = body
        slots.append(
            dict(
                slot=i,
                cell=cell.name,
                filename=path,
                archived_filename=archived,
                expected_model=cell.wire.model_spec.model_identifier,
                http_body_bytes=len(body),
                work_sha256=cell.work.fingerprint,
                native_request_sha256=cell.wire.native_request_sha256,
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    manifest = dict(
        contract="wading-path-se-repeat-1",
        live_directory=ROOT.relative_to(REPO).as_posix(),
        archive_sha256=regression.SEAL,
        historical_approval_sha256=regression.APPROVAL,
        ordered_cells=ORDER,
        blocks=BLOCKS,
        slots=slots,
        models=history["models"],
        model_specs=history["model_specs"],
        reasoning=history["reasoning"],
        explicit_event_scope=prior.TARGET["reached"],
        historical_source_versions=history["historical_source_versions"],
        historical_source_binding=history["historical_source_binding"],
        assessment_draft_versions={k: history["assessment_draft_versions"][k] for k in cases},
        fixed_stop=history["fixed_stop"],
        gold_sha256=digest(assets["gold.json"]),
        budget=history["budget"],
        stops=prior.STOPS,
        implementation={p: ledger.file_hash(REPO / p) for p in FILES},
        members={k: digest(v) for k, v in assets.items()},
    )
    return cells, assets, encoded(manifest)


def issue(root: Path) -> str:
    _, assets, manifest = materials()
    _unlinked(root).mkdir(exist_ok=False)
    (root / "requests").mkdir()
    for name, raw in assets.items():
        _durable_write(root / name, raw)
    _durable_write(root / "plan.json", manifest)
    approval = digest(manifest)
    ledger.initialize_ledger(root, approval)
    return approval


def verify(root: Path, approval: str) -> list[Cell]:
    cells, assets, manifest = materials()
    require(
        digest(manifest) == approval and _read(root / "plan.json") == manifest,
        "approval_or_source_drift",
    )
    require(all(_read(root / k) == v for k, v in assets.items()), "frozen_member_drift")
    require(
        {p.name for p in (root / "requests").iterdir()}
        == {filename(c, e) for c, e in schedule(cells)},
        "request_inventory",
    )
    ledger.ledger_state(root, approval)
    return cells
