"""Preserve and replay the seven observed Wading Path answers without provider access."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource
from open_hollywood_engine.evaluations.assessment_result import _registry
from open_hollywood_engine.evaluations.review_evidence import require, text_hash

from scripts.ordinary_v61_capture import file_hash, ledger_state
from scripts.q008_sol_smoke import Terminal
from scripts.q010_uncertainty_plan import Cell, digest, schedule
from scripts.q010_uncertainty_run import Audit, closure, evidence_sheet, intent
from scripts.q011_arrival.run import evaluate
from scripts.wading_path_be import plan as base
from scripts.wading_path_be import regression as prior

from . import plan, scoring

ARCHIVE = plan.ROOT.parent / "wading-path-observations-regression-2026-11-24"
RESULTS = plan.ROOT.parent / "wading-path-observations-results-2026-11-24"
APPROVAL = "8ba8473e3496a68ccb250c05b31b3aae217bda7a84aec19051913e619fe3ae82"
SEAL = "f053b71703ef5d1df3a0aa76cbce3d18c99ebdbac7485504096757111b7ca980"


def inventory(root: Path) -> dict[str, Path]:
    return {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}


def verified(archive: Path) -> Path:
    raw = (archive / "capture-manifest.json").read_bytes()
    require(digest(raw) == SEAL, "observation_archive_seal")
    capture = archive / "capture"
    require(
        {name: file_hash(p) for name, p in inventory(capture).items()} == json.loads(raw),
        "observation_archive_members",
    )
    return capture


def preserve() -> None:
    if ARCHIVE.exists():
        verified(ARCHIVE)
        return
    old, _ = prior.verified_capture(prior.ARCHIVE)
    files = {
        f"{group}/{name}": p
        for group, root in (("run", plan.ROOT), ("operator", RESULTS))
        for name, p in inventory(root).items()
    }
    files.update(
        {
            "source/intake.json": old / "source/intake.json",
            "source/previous-plan.json": old / "run/plan.json",
            "source/previous-scores.json": old / "operator/scores.json",
            "source/previous-manifest.json": prior.ARCHIVE / "capture-manifest.json",
        }
    )
    with TemporaryDirectory(dir=ARCHIVE.parent) as temp:
        staged = Path(temp) / "archive"
        for name, p in files.items():
            dest = staged / "capture" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p, dest)
        manifest = encoded({k: file_hash(p) for k, p in inventory(staged / "capture").items()})
        (staged / "capture-manifest.json").write_bytes(manifest)
        verified(staged)
        staged.rename(ARCHIVE)


def replay(archive: Path = ARCHIVE) -> dict[str, Any]:
    capture = verified(archive)
    frozen, operator, sources = (capture / name for name in ("run", "operator", "source"))
    manifest = json.loads((frozen / "plan.json").read_bytes())
    require(
        file_hash(frozen / "plan.json") == APPROVAL
        and ledger_state(frozen, APPROVAL) == "dispatched",
        "observation_archive_approval",
    )
    # Carry the historical B comparison and exact native intake inside this archive.
    previous = json.loads((sources / "previous-manifest.json").read_bytes())
    require(
        file_hash(sources / "previous-manifest.json") == prior.SEAL == manifest["archive_sha256"]
        and file_hash(sources / "intake.json") == previous["source/intake.json"]
        and file_hash(sources / "previous-plan.json") == previous["run/plan.json"]
        and file_hash(sources / "previous-scores.json") == previous["operator/scores.json"],
        "observation_archive_history",
    )
    source = IntakeSource.model_validate_json((sources / "intake.json").read_bytes())
    gold = (frozen / "gold.json").read_bytes()
    cases = json.loads(gold)
    locations = json.loads((operator / "cited-locations.json").read_bytes())
    observations = json.loads((frozen / "observations.json").read_bytes())
    versions = tuple(UUID(v) for v in manifest["historical_source_versions"])
    cells = []
    for name in plan.ORDER:
        case, arm = name.split("-")
        key = cases[case]
        draft = locations[case]["E1420"]
        prose, version = draft["quote"], draft["document_version"]
        require(
            version == key["draft_version"] and text_hash(prose) == key["prose_sha256"],
            "observation_archive_draft",
        )
        authored = case in ("K2", "K3")
        unit = key["unit"]
        work = plan.selected_work(source, unit, prose, version, authored)
        registry = {r.ref: r for r in _registry(work).entries}
        for ref, record in locations[case].items():
            r = registry[ref]
            require(all(record[k] == v for k, v in r.model_dump(mode="json").items()), "citation")
            if ref in key["plan_refs"]:
                doc = next(d for d in work.context.documents if d.identity == r.document_id)
                _, artifacts, index, _, _ = r.field_pointer.split("/")
                art = json.loads(doc.content_json)[artifacts][int(index)]
                require(
                    art["artifact_version_id"]
                    == record["source_artifact_version"]
                    == key["plan_version"],
                    "plan_version",
                )
        body = json.loads((frozen / "requests" / f"{name}-generation.json").read_bytes())
        packet = json.loads(body["input"][1]["content"])
        brief = packet["work_brief"]
        if arm == "O":
            require(brief["exact_observations"] == observations[case], "observation_archive_quotes")
            for q in observations[case]:
                require(
                    q["ref"] == "E1420"
                    and q["draft_version"] == version
                    and q["quote"] == prose[q["start"] : q["end"]],
                    "observation_archive_span",
                )
        else:
            require("exact_observations" not in brief, "observation_archive_baseline")
        row = dict(
            unit=unit,
            arm=arm,
            work_sha256=work.fingerprint,
            declaration=packet["claim_scope"],
            brief=brief,
        )
        mapped = base.render(work, row, (*versions, UUID(version)) if authored else versions)
        cells.append(Cell(name, work, mapped.wire))

    output = frozen / "output"
    previous_raw = (output / "header.json").read_bytes()
    header = json.loads(previous_raw)
    require(
        header["origin"] == "observed_openai_transport" and header["approval"] == APPROVAL, "origin"
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
        stem = f"{i:02d}-{cell.name}-{end.stage}"
        message = (output / (stem + "-intent.json")).read_bytes()
        require(
            message == intent(previous_raw, cell, end)
            and slot["slot"] == i
            and (slot["cell"], slot["stage"]) == (cell.name, end.stage)
            and slot["work_sha256"] == cell.work.fingerprint
            and slot["native_request_sha256"] == cell.wire.native_request_sha256
            and (frozen / slot["filename"]).read_bytes() == end.body_utf8.encode(),
            "observation_archive_request",
        )
        previous_raw = (output / (stem + "-outcome.json")).read_bytes()
        terminal = Terminal.model_validate_json(previous_raw)
        require(terminal.intent_sha256 == digest(message), "observation_archive_terminal")
        state, details = evaluate(cell, end, terminal)
        eligible = end.stage == "generation"
        require(
            state == ("bound_unassessed" if eligible else "count_admitted"),
            "observation_archive_delivery",
        )
        audit["slots"].append(
            dict(cell=cell.name, stage=end.stage, state=state, eligible=eligible, **details)
        )
    require(
        (output / "close.json").read_bytes() == closure(previous_raw, audit["state"])
        and encoded(audit) == (operator / "audit.json").read_bytes(),
        "observation_archive_audit",
    )
    sheet = evidence_sheet(audit)
    form = (frozen / "sealed-evidence-decisions.json").read_bytes()
    scores = scoring.scores(audit, form, gold)
    require(
        encoded(dict(approval_sha256=APPROVAL, sheet_sha256=digest(encoded(sheet)), rows=sheet))
        == (operator / "evidence-worksheet.json").read_bytes()
        and form == (operator / "evidence-form.json").read_bytes()
        and encoded(scores) == (operator / "scores.json").read_bytes(),
        "observation_archive_scoring",
    )
    return dict(manifest_sha256=SEAL, slots=len(audit["slots"]), live_calls=0, **scores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preserve", action="store_true", help="Copy the sealed local run if absent."
    )
    if parser.parse_args().preserve:
        preserve()
    print(json.dumps(replay(), ensure_ascii=True, indent=2))
