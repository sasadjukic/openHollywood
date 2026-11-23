"""Freeze the admitted transfer packets, paired Sol-high requests and operator scoring rules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_authored_source import _document
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    EvidenceLocation,
    EvidenceRegistry,
    _paragraphs,
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentWork,
    ReportField,
    SelectedStatement,
    partition_work,
)
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
from scripts.q011_evidence_check import plan as previous
from scripts.q011_evidence_check import regression, transfer_audit

from .evidence import Decisions

ROOT = sources.DATA / "q011-transfer-comparison-2026-11-23"
FIRST_ARM = dict(T01="B", T02="E", T03="E", T04="B", T05="B", T06="E", T07="E", T08="B")
GOLD = "cd97a37cfa7aac55ebb91cb684206bb17c929caea84164cc57467a81750c6069"
PROPOSITIONS = {
    "The Understudy's Hem": "Iven standing on the blue star",
    "The Mended Burgee": "the skiff's bow being level with the white post",
}
WALL_SECONDS = 2 * len(FIRST_ARM) * (COUNT_SECONDS + GENERATION_SECONDS)
STOPS = (
    previous.STOPS[0],
    "All sixteen serial counts must return HTTP 200 and a positive "
    "in-budget input count before any generation.",
    *previous.STOPS[2:],
)
IMPLEMENTATION = (
    *previous.IMPLEMENTATION,
    "scripts/q011_evidence_check/transfer_audit.py",
    "scripts/q011_evidence_check/regression.py",
    "scripts/q011_transfer/evidence.py",
    "scripts/q011_transfer/plan.py",
    "scripts/q011_transfer/run.py",
    "scripts/q011_transfer/scoring.py",
)
RULES = {
    "eligibility": previous.RULES["eligibility"],
    "judgment": "Pass only for an exact match to the sealed whole-claim label.",
    "evidence": "Withhold arm, returned label and dispatch order. Inspect citations and reason. "
    "Locate both plan assignments, credit the depicted first action in a cited draft passage, "
    "and locate the draft observation bearing on physical position at the cut. Record its "
    "exact span, version, instant and bearing, and a cited span for the first action. "
    "Accept equivalent precise locators and reasoning. "
    "The brief and plan are not evidence that the assigned action occurred.",
    "endings": "For approach, distinguish direction from final position. For arrival, locate "
    "affirmative placement. For a terminal gap, locate incompatible separation at the cut. "
    "For an earlier gap, locate it and the subsequent unmeasured motion and explain why "
    "the earlier distance does not settle final position. Alignment does not require stopping. "
    "An unlocated full draft, wrong instant or material overread fails evidence.",
    "seal": "Seal every eligible evidence decision before joining the model labels to gold.",
    "comparison": "Report both independent scores and axis movement per pair, baseline joint "
    "passes, and unresolved recoveries by family and timing state. A joint miss means at least "
    "one axis failed. Report any control gains or losses separately.",
    "decision": "Missing eligible arms make transfer inconclusive. Any E miss holds advancement. "
    "Otherwise require a B joint miss becoming an E joint pass on an unresolved case in each "
    "family for cross-family recovery. One family is family-specific. If no unresolved B miss, "
    "distinguish a perfect baseline from control-only gains.",
}


def addition(family: str) -> str:
    return previous.ADDITION.replace("Elias standing at the threshold", PROPOSITIONS[family])


def base_work(packet: dict[str, Any]) -> AssessmentWork:
    docs = []
    refs = []
    for role, pointers in (
        ("context", ()),
        ("plan", (("E0233", "outcome"), ("E0229", "exit_state"))),
        ("draft", (("E0883", "prose"), ("D01", "prose"))),
    ):
        src = packet[role]
        doc = _document(role, "source", src["content"]).model_copy(
            update={"version": src["version"]}
        )
        docs.append(doc)
        for ref, field_name in pointers:
            value = src["content"][field_name]
            paragraph = None
            start, end = 0, len(value)
            if ref == "D01":
                spans = _paragraphs(value)
                paragraph, (start, end) = len(spans), spans[-1]
            refs.append(
                EvidenceLocation(
                    ref=ref,
                    document_id=role,
                    document_version=doc.version,
                    document_sha256=doc.content_sha256,
                    field_pointer="/" + field_name,
                    field_sha256=text_hash(value),
                    start=start,
                    end=end,
                    quote=value[start:end],
                    paragraph=paragraph,
                )
            )
    claim = packet["claim"]
    report = _document("authored-claim", "report", {"claim": claim})
    docs.append(report.model_copy(update={"version": report.content_sha256}))
    registry = EvidenceRegistry(entries=tuple(refs))
    docs.append(_document("registry", "registry", registry.model_dump(mode="json")))
    visible = []
    for doc in docs:
        entry = doc.model_dump(mode="json", exclude={"content_json"})
        if doc.kind == "registry":
            entry.update(
                columns=["ref", "document_id", "field_pointer"],
                whole_field_locations=[
                    [r.ref, r.document_id, r.field_pointer] for r in refs if r.paragraph is None
                ],
                paragraph_locations=[
                    dict(
                        ref=r.ref,
                        document_id=r.document_id,
                        field_pointer=r.field_pointer,
                        paragraph_one_based=r.paragraph,
                        start=r.start,
                        end=r.end,
                        quote=r.quote,
                    )
                    for r in refs
                    if r.paragraph is not None
                ],
            )
        else:
            entry["structured_content"] = json.loads(doc.content_json)
        visible.append(entry)
    unit = rehearsal.UNIT
    field = ReportField(field_id=unit, pointer="/claim", text=claim)
    brief = dict(
        unit_id=unit,
        question="Assess the whole active claim according to its stated subject.",
        temporal_scope="Scene one through its final narrated instant.",
        source_authority="Use the plan for the assignment and the assessed draft for the story "
        "and its closing paragraph. The authored claim identifies the statement to assess.",
        evidence_obligation="Locate both plan fields and the relevant passage. Explain what "
        "each material part of the claim requires and what the cited source establishes.",
    )
    user = compact(
        dict(
            active_unit_ids=[unit],
            claim=field.model_dump(mode="json"),
            work_brief=brief,
            documents=visible,
        )
    )
    return partition_work(
        AssessmentContext(
            provenance="synthetic_fixture",
            origin_sha256=text_hash(user),
            documents=tuple(docs),
            report_fields=(field,),
            statements=(
                SelectedStatement(
                    unit_id=unit, field_id=unit, start=0, end=len(claim), quote=claim
                ),
            ),
            messages=(
                SavedMessage(role="system", content=SYSTEM),
                SavedMessage(role="user", content=user),
            ),
        ),
        1,
    )


def paired_works(packets: dict[str, dict[str, Any]]) -> list[tuple[str, AssessmentWork]]:
    require(set(packets) == set(FIRST_ARM), "transfer_case_inventory")
    works = []
    for key in FIRST_ARM:
        base = base_work(packets[key])
        system, original_user = base.context.messages
        payload = json.loads(original_user.content)
        payload["work_brief"]["evidence_obligation"] += " " + addition(packets[key]["family"])
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
            "transfer_wire_scope",
        )
        versions = tuple(UUID(d.version) for d in work.context.documents if d.kind == "source")
        request_id = digest(encoded([work.fingerprint, MODEL, "high", parent.INPUT, parent.OUTPUT]))
        scope = scope_for_batch(work, batch.batch_id, request_id)
        request = ModelRequest(
            provider="openai",
            deployment=ModelDeployment.CLOUD,
            model_identifier=MODEL,
            invocation=InvocationContext(
                "endpoint_fact_assessment", "q011-transfer-pair-1", versions
            ),
            messages=messages,
            settings=ModelSettings(thinking="high"),
            budget=budget,
            response_schema=assessment_response_schema(work, scope),
        )
        result.append(Cell(cell_name, work, _prepare_wire(work, scope, request, spec, guard=None)))
    return result


def materials() -> tuple[list[Cell], dict[str, bytes], bytes]:
    sealed = rehearsal.pinned(transfer_audit.ROOT / "admission-seal.json", transfer_audit.SEAL)
    gold = _read(transfer_audit.ROOT / "gold.json")
    require(digest(gold) == GOLD == sealed["gold.json"], "transfer_gold_drift")
    decisions = json.loads(gold)["cases"]
    require(set(decisions) == set(FIRST_ARM), "transfer_gold_inventory")
    assets = {
        "gold.json": gold,
        "scoring.json": encoded(RULES),
        "evidence-form-schema.json": encoded(Decisions.model_json_schema()),
    }
    witnesses = {}
    packets = {}
    for key in FIRST_ARM:
        name = f"packets/{key}.json"
        raw = _read(transfer_audit.ROOT / name)
        require(
            digest(raw) == sealed[name] == decisions[key]["packet_sha256"], "transfer_packet_drift"
        )
        packet = json.loads(raw)
        packets[key] = packet
        assets[name] = raw
        prose = packet["draft"]["content"]["prose"]
        scene_plan = packet["plan"]
        witnesses[key] = dict(
            claim=packet["claim"],
            plan_version=scene_plan["version"],
            draft_version=packet["draft"]["version"],
            fields={
                "E0233": scene_plan["content"]["outcome"],
                "E0229": scene_plan["content"]["exit_state"],
                "E0883": prose,
                "D01": prose.rsplit("\n\n", 1)[-1],
            },
        )
    assets["witnesses.json"] = encoded(witnesses)
    cells = render(packets)
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
                case=key,
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
            contract="q011-sol-high-transfer-evidence-check-1",
            evidence_check_addition={f: addition(f) for f in PROPOSITIONS},
            first_arm=FIRST_ARM,
            offline_q011_pairs=["AP", "RP", "SP", "GC", "GM"],
            admission_sha256=transfer_audit.SEAL,
            source_archive_sha256=regression.SEAL,
            live_directory=ROOT.relative_to(sources.REPO).as_posix(),
            cases={
                key: {k: d[k] for k in ("family", "state", "label", "packet_sha256")}
                for key, d in decisions.items()
            },
            slots=slots,
            gold_sha256=GOLD,
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
    (root / "packets").mkdir()
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
    require(
        {p.name for p in (root / "packets").iterdir()} == {k + ".json" for k in FIRST_ARM},
        "packet_inventory",
    )
    ledger.ledger_state(root, approval)
    return cells
