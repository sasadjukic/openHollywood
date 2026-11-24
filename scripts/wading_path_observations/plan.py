"""Freeze seven full-context Sol-high requests and the independent operator materials."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_intake import IntakeSource, build_intake_source
from open_hollywood_engine.evaluations.assessment_result import _paragraphs, _registry
from open_hollywood_engine.evaluations.assessment_work import AssessmentWork, partition_work
from open_hollywood_engine.evaluations.review_evidence import require, strict_object, text_hash
from open_hollywood_engine.models.openai import _cost

from scripts import ordinary_v61_capture as ledger
from scripts.fresh_endpoint_repeat.scoring import Decisions
from scripts.q010_uncertainty_plan import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    MODEL,
    REPO,
    Cell,
    digest,
    filename,
    schedule,
)
from scripts.wading_path_be import plan as base
from scripts.wading_path_be import regression, rehearsal

ROOT = base.ROOT.parent / "wading-path-sol-high-observations-2026-11-24"
CASES = {"K1": "original", "K2": "arrival", "K3": "stop_short", "Q008": "original"}
ORDER = ("K1-B", "K2-O", "K3-B", "Q008-B", "K1-O", "K2-B", "K3-O")
WALL_SECONDS = len(ORDER) * (COUNT_SECONDS + GENERATION_SECONDS)
FILES = (
    *base.FILES,
    "scripts/wading_path_be/regression.py",
    "scripts/wading_path_be/rehearsal.py",
    "scripts/wading_path_observations/plan.py",
    "scripts/wading_path_observations/run.py",
    "scripts/wading_path_observations/scoring.py",
)
STOPS = (
    base.STOPS[0],
    "All seven serial input counts must return HTTP 200 and a positive in-budget count before "
    "any generation. No retries, replacements, redirects, polling or fallback.",
    *base.STOPS[2:],
)
SCORING = {
    "eligibility": base.SCORING["eligibility"],
    "judgment": base.SCORING["judgment"],
    "evidence": "Mask arm, returned label and order. Resolve citations against the selected "
    "version and both required plan fields for Q011, or the outcome for Q008. Judge the reason "
    "against the case requirements in gold.json. Record version, passage, instant and basis. "
    "Equivalent precise locators earn credit. An observation copied at the wrong instant, a "
    "bare citation, stale draft, unsupported stop, or claim of never arriving from a final gap "
    "fails evidence. Seal every eligible evidence decision before joining labels.",
    "decision": "Any missing eligible arm is inconclusive. A miss on either axis in any "
    "determinate arm or Q008 holds advancement. For the original, report both axes, their "
    "movement and any baseline joint recovery. A joint O pass after a B miss is a within-scene "
    "recovery. Two joint passes leave no original headroom. Otherwise hold.",
}


def selected_work(
    source: IntakeSource, unit: str, prose: str, version: str, authored: bool
) -> AssessmentWork:
    ctx = source.inventory_work.context
    if authored:
        docs = {d.kind: d for d in ctx.documents}
        provenance = strict_object(docs["scope"].content_json)
        provenance["diagnostic_assessed_draft"] = version
        synthetic = build_intake_source(
            origin=source.origin,
            review_id=source.review_id,
            report_origin=source.report_origin,
            messages=ctx.messages,
            current_prose=prose,
            current_version=version,
            report=strict_object(docs["report"].content_json),
            operator_provenance=provenance,
        )
        ctx = synthetic.inventory_work.context.model_copy(
            update={"provenance": "synthetic_fixture"}
        )
    (stmt,) = (s for s in ctx.statements if s.unit_id == unit)
    return partition_work(ctx.model_copy(update={"statements": (stmt,)}), 1)


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    capture, _ = regression.verified_capture(regression.ARCHIVE)
    key, endings = rehearsal.materials(capture)
    source = IntakeSource.model_validate_json(_read(capture / "source/intake.json"))
    previous = json.loads(_read(capture / "run/plan.json"))
    versions = tuple(UUID(v) for v in previous["source_version_ids"])
    previews = json.loads(_read(capture / "run/selections.json"))
    baseline = {r["unit"]: r for r in previews if r["arm"] == "B"}
    prior_gold = json.loads(_read(capture / "run/gold.json"))
    original = json.loads(_read(capture / "operator/cited-locations.json"))["E1420"]["quote"]
    rows = {}
    rendered = {}
    observations = {}
    for case, ending in CASES.items():
        unit = "Q008" if case == "Q008" else "Q011"
        authored = ending != "original"
        selected = endings[ending]
        version = selected["draft_version"]
        prose = original + ("\n\n" + key["cases"][ending]["append_paragraph"] if authored else "")
        work = selected_work(source, unit, prose, version, authored)
        registry = {e.ref: e for e in _registry(work).entries}
        draft = registry["E1420"]
        require(
            draft.quote == prose
            and draft.document_version == version
            and draft.field_sha256 == selected["prose_sha256"] == text_hash(prose),
            "selected_draft_binding",
        )
        # Copy the same three complete closing paragraphs in every case, plus any new last one.
        spans = [(a, b) for a, b in _paragraphs(prose) if a >= 3995]
        require(spans[0][0] == 3995 and spans[-1][1] == len(prose), "observation_range")
        quotations = [
            dict(ref=draft.ref, draft_version=version, start=a, end=b, quote=prose[a:b])
            for a, b in spans
        ]
        info = next(c for c in prior_gold["claims"] if c["field_id"] == unit)
        require(info["text"] == work.context.statements[0].quote, "selected_claim")
        rows[case] = dict(
            unit=unit,
            claim=info["text"],
            ending=ending,
            draft_version=version,
            prose_sha256=draft.field_sha256,
            plan_refs=info["plan_refs"],
            plan_version=key["plan_version"],
            gold=key["cases"][ending]["gold"] if unit == "Q011" else info["label"],
            evidence_requirements=(
                [key["evidence_rule"], key["cases"][ending]["observation"]]
                if unit == "Q011"
                else info["evidence_pass_requires"]
            ),
        )
        invoked = (*versions, UUID(version)) if authored else versions
        if unit == "Q011":
            observations[case] = quotations
        for arm in ("B", "O") if unit == "Q011" else ("B",):
            brief = dict(baseline[unit]["brief"])
            if authored:
                brief["source_authority"] += (
                    f" Assess draft {version} in E1420. The review and its original candidate "
                    "describe the historical review."
                )
            if arm == "O":
                brief["exact_observations"] = quotations
            row = {**baseline[unit], "arm": arm, "brief": brief, "work_sha256": work.fingerprint}
            cell = base.render(work, row, invoked)
            if not authored and arm == "B":
                for end in cell.wire.endpoints:
                    require(
                        end.body_utf8.encode()
                        == _read(capture / "run/requests" / filename(cell, end)),
                        "historical_baseline_drift",
                    )
            name = case + "-" + arm
            rendered[name] = Cell(name, work, cell.wire)
    cells = [rendered[name] for name in ORDER]
    assets = {
        "gold.json": encoded(rows),
        "observations.json": encoded(observations),
        "scoring.json": encoded(SCORING),
        "evidence-form-schema.json": encoded(Decisions.model_json_schema()),
    }
    slots = []
    for i, (cell, end) in enumerate(schedule(cells), 1):
        path = "requests/" + filename(cell, end)
        assets[path] = end.body_utf8.encode()
        slots.append(
            dict(
                slot=i,
                cell=cell.name,
                filename=path,
                http_body_bytes=len(assets[path]),
                native_request_sha256=cell.wire.native_request_sha256,
                work_sha256=cell.work.fingerprint,
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    spec = cells[0].wire.model_spec
    cost = _cost(spec, base.INPUT, base.OUTPUT)
    return (
        cells,
        assets,
        encoded(
            dict(
                contract="wading-path-q011-exact-observations-1",
                live_directory=ROOT.relative_to(REPO).as_posix(),
                model=MODEL,
                reasoning="high",
                model_spec=spec.model_dump(mode="json"),
                historical_source_versions=previous["source_version_ids"],
                historical_source_binding=prior_gold["binding"],
                assessment_draft_versions={k: r["draft_version"] for k, r in rows.items()},
                archive_sha256=regression.SEAL,
                rehearsal_gold_sha256=rehearsal.GOLD_SHA,
                gold_sha256=digest(assets["gold.json"]),
                ordered_cells=ORDER,
                slots=slots,
                stops=STOPS,
                budget=dict(
                    input_counts=7,
                    max_generations=7,
                    retries=0,
                    input_per_generation=base.INPUT,
                    output_per_generation=base.OUTPUT,
                    aggregate_generation_input=7 * base.INPUT,
                    aggregate_generation_output=7 * base.OUTPUT,
                    max_usd_per_generation=str(cost),
                    aggregate_generation_usd=str(7 * cost),
                    count_seconds=COUNT_SECONDS,
                    generation_seconds=GENERATION_SECONDS,
                    wall_seconds=WALL_SECONDS,
                ),
                implementation={p: ledger.file_hash(REPO / p) for p in FILES},
                members={k: digest(v) for k, v in assets.items()},
            )
        ),
    )


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
