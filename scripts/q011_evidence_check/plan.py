"""Freeze ten Q011 position assessments with a single diagnostic brief intervention."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_compact_presentation import compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentWork, partition_work
from open_hollywood_engine.evaluations.review_evidence import SavedMessage, require, text_hash
from open_hollywood_engine.models.assessment_openai import _prepare_wire
from open_hollywood_engine.models.contracts import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)
from open_hollywood_engine.models.openai import _cost
from open_hollywood_engine.models.openai_catalog import builtin_model_specs

from scripts import ordinary_v61_capture as ledger
from scripts.q010_uncertainty_plan import (
    COUNT_SECONDS,
    GENERATION_SECONDS,
    MODEL,
    Cell,
    digest,
    filename,
    schedule,
)
from scripts.q011_arrival import plan as parent
from scripts.q011_arrival import scope_rehearsal as rehearsal
from scripts.q011_arrival import sources
from scripts.q011_scope import plan as scope_plan
from scripts.q011_scope import position_rehearsal as position
from scripts.q011_scope import regression

ROOT = sources.DATA / "q011-evidence-check-comparison-2026-11-23"
CASES = {
    "AP": "approach",
    "RP": "arrival",
    "SP": "stop",
    "GC": "gap-at-cut",
    "GM": "gap-before-motion",
}
FIRST_ARM = {"AP": "B", "RP": "E", "SP": "B", "GC": "E", "GM": "B"}
ADDITION = (
    "Identify the draft observation your conclusion relies on, say when it applies, and "
    "explain whether it establishes, rules out, or leaves open Elias standing at the "
    "threshold at the scene cut."
)
WALL_SECONDS = 2 * len(CASES) * (COUNT_SECONDS + GENERATION_SECONDS)
STOPS = (
    scope_plan.STOPS[0],
    "All ten serial counts must return HTTP 200 and a positive in-budget input count "
    "before any generation.",
    *scope_plan.STOPS[2:],
)
IMPLEMENTATION = (
    *scope_plan.IMPLEMENTATION,
    "scripts/q011_scope/position_rehearsal.py",
    "scripts/q011_scope/regression.py",
    "scripts/q011_evidence_check/plan.py",
    "scripts/q011_evidence_check/run.py",
    "scripts/q011_evidence_check/scoring.py",
)
RULES = {
    "eligibility": "Score each complete in-budget bound generation in a closed observed journal. "
    "Report unattempted and ineligible slots as unscored on both axes.",
    "evidence_review": "With arm and support label masked, inspect cited source fields and the "
    "reason. Locate both plan assignments, credit depicted attraction and evaluate the cited "
    "observation, its instant and its bearing on physical standing at the sill. Accept a located "
    "full draft or closing paragraph and equivalent reasoning. Seal the passage and basis for "
    "each decision before joining labels. An accurate quote used at the wrong instant fails.",
    "pair": "Compare judgment and evidence separately. A gain on an axis requires B fail and "
    "E pass in the same case. Report the genuine case and each timing case individually. "
    "Record a genuine B joint pass as a baseline recovery regardless of E.",
    "decision": "Missing eligible arms make the comparison inconclusive. If E misses any axis "
    "on any of the five cases, hold. Otherwise distinguish genuine within-pair recovery "
    "from a joint B/E pass on the genuine case. Report timing/control gains or losses separately. "
    "One observation per arm in one family is diagnostic only.",
}


def paired_works(packets: dict[str, dict[str, Any]]) -> list[tuple[str, AssessmentWork]]:
    require(set(packets) == set(CASES.values()), "position_case_inventory")
    works = []
    for key, case in CASES.items():
        base = rehearsal.work_pair(case, packets[case])[case + "-position"]
        system, original_user = base.context.messages
        payload = json.loads(original_user.content)
        payload["work_brief"]["evidence_obligation"] += " " + ADDITION
        content = compact(payload)
        context = base.context.model_copy(
            update={
                "messages": (system, SavedMessage(role="user", content=content)),
                "origin_sha256": text_hash(content),
            }
        )
        checked_work = partition_work(context, base.maximum_units)
        arms = {"B": base, "E": checked_work}
        for arm in "BE" if FIRST_ARM[key] == "B" else "EB":
            works.append((key + "-" + arm, arms[arm]))
    return works


def render(packets: dict[str, dict[str, Any]]) -> list[Cell]:
    spec = builtin_model_specs()[MODEL]
    budget = ModelCallBudget(parent.INPUT, parent.OUTPUT, _cost(spec, parent.INPUT, parent.OUTPUT))
    result = []
    for cell_name, work in paired_works(packets):
        (batch,) = work.batches
        messages = tuple(
            ModelMessage(MessageRole(m.role), m.content) for m in work.context.messages
        )
        require(
            batch.unit_ids == (rehearsal.UNIT,)
            and [m.role for m in messages] == [MessageRole.SYSTEM, MessageRole.USER],
            "q011_scope_wire_scope",
        )
        versions = tuple(UUID(d.version) for d in work.context.documents if d.kind == "source")
        request_id = digest(encoded([work.fingerprint, MODEL, "high", parent.INPUT, parent.OUTPUT]))
        scope = scope_for_batch(work, batch.batch_id, request_id)
        request = ModelRequest(
            provider="openai",
            deployment=ModelDeployment.CLOUD,
            model_identifier=MODEL,
            invocation=InvocationContext(
                "endpoint_fact_assessment", "q011-position-pair-1", versions
            ),
            messages=messages,
            settings=ModelSettings(thinking="high"),
            budget=budget,
            response_schema=assessment_response_schema(work, scope),
        )
        result.append(Cell(cell_name, work, _prepare_wire(work, scope, request, spec, guard=None)))
    return result


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    packets = position.packets()
    cells = render(packets)
    gold = _read(position.ROOT / "gold.json")
    require(
        digest(gold) == position.GOLD and gold == encoded(position.gold(packets)),
        "position_gold_drift",
    )
    sealed = json.loads(gold)
    witnesses = {}
    for key, name in CASES.items():
        packet = packets[name]
        draft = packet["assessment_draft"]
        scene_plan = packet["context"]["scene_plan"]
        prose = draft["content"]["prose"]
        witnesses[key] = dict(
            claim=sealed["claim"],
            plan_version=scene_plan["version"],
            draft_version=draft["version"],
            fields={
                "E0233": scene_plan["content"]["outcome"],
                "E0229": scene_plan["content"]["exit_state"],
                "E0883": prose,
                "D01": prose.rsplit("\n\n", 1)[-1],
            },
        )
    assets = {
        "gold.json": gold,
        "scoring.json": encoded(RULES | {k: sealed[k] for k in ("judgment_rule", "evidence_rule")}),
        "witnesses.json": encoded(witnesses),
    }
    slots = []
    for i, (cell, end) in enumerate(schedule(cells), 1):
        key, arm = cell.name.split("-")
        path = "requests/" + filename(cell, end)
        body = end.body_utf8.encode()
        assets[path] = body
        slots.append(
            dict(
                slot=i,
                cell=cell.name,
                case=CASES[key],
                arm=arm,
                filename=path,
                work_sha256=cell.work.fingerprint,
                native_request_sha256=cell.wire.native_request_sha256,
                http_body_bytes=len(body),
                **end.model_dump(mode="json", exclude={"body_utf8"}),
            )
        )
    spec = cells[0].wire.model_spec
    ceiling = _cost(spec, parent.INPUT, parent.OUTPUT)
    manifest = encoded(
        dict(
            contract="q011-sol-high-position-evidence-check-1",
            evidence_check_addition=ADDITION,
            first_arm=FIRST_ARM,
            offline_controls=["AD-B", "RD-B", "SD-B"],
            source_archive_sha256=regression.SEAL,
            live_directory=ROOT.relative_to(sources.REPO).as_posix(),
            cases=CASES,
            slots=slots,
            gold_sha256=position.GOLD,
            model=MODEL,
            reasoning="high",
            baseline_sha256=digest(cells[0].work.context.messages[0].content.encode()),
            model_spec=spec.model_dump(mode="json"),
            stops=STOPS,
            budget=dict(
                input_counts=len(cells),
                max_generations=len(cells),
                retries=0,
                input_per_generation=parent.INPUT,
                output_per_generation=parent.OUTPUT,
                aggregate_generation_input=len(cells) * parent.INPUT,
                aggregate_generation_output=len(cells) * parent.OUTPUT,
                max_usd_per_generation=str(ceiling),
                aggregate_generation_usd=str(len(cells) * ceiling),
                count_seconds=COUNT_SECONDS,
                generation_seconds=GENERATION_SECONDS,
                wall_seconds=WALL_SECONDS,
            ),
            implementation={p: ledger.file_hash(sources.REPO / p) for p in IMPLEMENTATION},
            members={k: digest(v) for k, v in assets.items()},
        )
    )
    return cells, assets, manifest


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
    require(all(_read(root / k) == raw for k, raw in assets.items()), "frozen_member_drift")
    require(
        {p.name for p in (root / "requests").iterdir()}
        == {filename(c, e) for c, e in schedule(cells)},
        "request_inventory",
    )
    ledger.ledger_state(root, approval)
    return cells
