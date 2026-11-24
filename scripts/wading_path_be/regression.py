"""Read-only replay of the two observed Wading Path pairs and their narrated-arrival control."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.assessment_work import partition_work
from open_hollywood_engine.evaluations.review_evidence import require

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import Cell, digest, schedule
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent
from scripts.q011_arrival.run import evaluate
from scripts.q011_transfer import wading_path_selection as selection

from . import plan, scoring

ARCHIVE = plan.ROOT.parent / "wading-path-be-regression-2026-11-24"
SEAL = "3f4295306f6b366b19a292e0147d4fbb4992ce82fd3353581571a10ef2e2c303"
APPROVAL = "81c56dda84c79e97de246c7afeb8a525531e4bd0244fa9ed104e09deba3f8e05"


def verified_capture(archive: Path) -> tuple[Path, int]:
    raw = (archive / "capture-manifest.json").read_bytes()
    require(digest(raw) == SEAL, "wading_regression_seal")
    members = json.loads(raw)
    capture = archive / "capture"
    paths = {p.relative_to(capture).as_posix() for p in capture.rglob("*") if p.is_file()}
    require(paths == set(members), "wading_regression_inventory")
    require(
        all(file_hash(capture / p) == h for p, h in members.items()), "wading_regression_member"
    )
    return capture, len(members)


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    capture, member_count = verified_capture(archive)
    frozen, operator = capture / "run", capture / "operator"
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "wading_regression_approval",
    )
    manifest = json.loads((frozen / "plan.json").read_bytes())
    gold = (frozen / "gold.json").read_bytes()
    key = json.loads(gold)
    require(digest(gold) == manifest["gold_sha256"] == selection.GOLD_SHA, "wading_regression_gold")
    source = IntakeSource.model_validate_json((capture / "source/intake.json").read_bytes())
    require(
        source.source_sha256 == manifest["intake_sha256"] == selection.SOURCE_SHA
        and source.review_id == key["binding"]["invocation"],
        "wading_regression_source",
    )
    ctx = source.inventory_work.context
    versions = tuple(UUID(v) for v in manifest["source_version_ids"])
    selections = json.loads((frozen / "selections.json").read_bytes())
    cells: list[Cell] = []
    for row in selections:
        stmt = next(s for s in ctx.statements if s.unit_id == row["unit"])
        work = partition_work(ctx.model_copy(update={"statements": (stmt,)}), 1)
        cells.append(plan.render(work, row, versions))
    require([c.name for c in cells] == manifest["ordered_cells"], "wading_regression_order")

    output = frozen / "output"
    previous = (output / "header.json").read_bytes()
    header = json.loads(previous)
    require(
        header["approval"] == APPROVAL and header["origin"] == "observed_openai_transport",
        "wading_regression_origin",
    )
    audit: Audit = dict(
        approval=APPROVAL,
        ledger="dispatched",
        origin=header["origin"],
        closed=True,
        state="bound_unassessed",
        slots=[],
    )
    for i, ((cell, end), slot) in enumerate(
        zip(schedule(cells), manifest["slots"], strict=True), 1
    ):
        prefix = f"{i:02d}-{cell.name}-{end.stage}"
        message = (output / (prefix + "-intent.json")).read_bytes()
        require(
            slot["slot"] == i
            and slot["cell"] == cell.name
            and slot["stage"] == end.stage
            and slot["native_request_sha256"] == cell.wire.native_request_sha256
            and slot["work_sha256"] == cell.work.fingerprint
            and (frozen / slot["filename"]).read_bytes() == end.body_utf8.encode()
            and message == intent(previous, cell, end),
            "wading_regression_request",
        )
        previous = (output / (prefix + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous)
        require(terminal.intent_sha256 == digest(message), "wading_regression_receipt")
        state, details = evaluate(cell, end, terminal)
        eligible = end.stage == "generation"
        require(
            state == ("bound_unassessed" if eligible else "count_admitted"),
            "wading_regression_delivery",
        )
        audit["slots"].append(
            dict(cell=cell.name, stage=end.stage, state=state, eligible=eligible, **details)
        )
    require(
        (output / "close.json").read_bytes() == closure(previous, audit["state"])
        and encoded(audit) == (operator / "audit.json").read_bytes(),
        "wading_regression_audit",
    )
    sheet = evidence_sheet(audit)
    require(
        encoded(dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet))
        == (operator / "evidence-worksheet.json").read_bytes(),
        "wading_regression_worksheet",
    )
    form = (frozen / "sealed-evidence-decisions.json").read_bytes()
    result = scoring.scores(audit, form, gold)
    require(
        form == (operator / "evidence-form.json").read_bytes()
        and encoded(result) == (operator / "scores.json").read_bytes(),
        "wading_regression_scores",
    )

    registry = {e.ref: e for e in _registry(source.inventory_work).entries}
    draft = registry[key["draft_complete_ref"]]
    seen = json.loads((operator / "cited-locations.json").read_bytes())
    cited = set()
    for decision in sheet:
        refs = decision["citations"]
        assert isinstance(refs, list)
        cited.update(refs)
    require(
        set(seen) == cited and draft.document_version == key["binding"]["draft"],
        "wading_regression_citations",
    )
    for ref, record in seen.items():
        original = registry[ref].model_dump(mode="json")
        require(all(record[k] == v for k, v in original.items()), "wading_regression_location")
    for w in key["draft_witnesses"].values():
        require(
            w["draft_version"] == draft.document_version
            and draft.quote[w["start"] : w["end"]]
            == registry[w["registered_ref"]].quote
            == w["quote"],
            "wading_regression_draft_witness",
        )
    visible = json.loads(
        next(d.content_json for d in ctx.documents if d.identity == "visible-request")
    )
    for w in key["plan_witnesses"].values():
        ref = w["registered_ref"]
        _, artifacts, index, content, field = registry[ref].field_pointer.split("/")
        artifact = visible[artifacts][int(index)]
        require(
            artifact["artifact_version_id"]
            == seen[ref]["source_artifact_version"]
            == key["binding"]["plan"]
            == w["version"]
            and field == w["field"]
            and artifact[content][field] == registry[ref].quote == w["text"],
            "wading_regression_plan_witness",
        )
    return dict(
        manifest_sha256=SEAL,
        members=member_count,
        slots=len(audit["slots"]),
        live_calls=0,
        **result,
    )


if __name__ == "__main__":
    print(json.dumps(replay(), ensure_ascii=True, indent=2))
