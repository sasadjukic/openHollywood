"""Freeze the source-only B/C endpoint controls and their operator-only scoring contract."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from open_hollywood_api.services.assessment_completion import _read, _unlinked
from open_hollywood_api.services.assessment_delivery import _durable_write
from open_hollywood_engine.evaluations.assessment_compact_presentation import SYSTEM, compact
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    assessment_response_schema,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import AssessmentWork
from open_hollywood_engine.evaluations.review_evidence import require
from open_hollywood_engine.models.assessment_openai import _prepare_wire
from open_hollywood_engine.models.contracts import (
    InvocationContext,
    MessageRole,
    ModelDeployment,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)
from open_hollywood_engine.models.openai import _cost
from open_hollywood_engine.models.openai_catalog import builtin_model_specs

from scripts import ordinary_v61_capture as ledger
from scripts.q010_uncertainty_plan import (
    ADDITION,
    BASE,
    BUDGET,
    COUNT_SECONDS,
    GENERATION_SECONDS,
    INPUT,
    MODEL,
    OUTPUT,
    STOPS,
    WALL_SECONDS,
    Cell,
    digest,
    filename,
    schedule,
)
from scripts.q010_uncertainty_plan import IMPLEMENTATION as BASE_IMPLEMENTATION

from . import controls

REPO = Path(__file__).resolve().parents[2]
ROOT = controls.ROOT.parent / "q010-fresh-repeat-2026-11-23"
FIRST_B = {"R01", "R02", "R05", "R08"}
PREDECESSOR = "3600fc37fcd142cd1fe733895f19c77a1ca4a1aa0595d18c4481524840869729"
IMPLEMENTATION = (
    *BASE_IMPLEMENTATION,
    "scripts/fresh_endpoint_repeat/__init__.py",
    "scripts/fresh_endpoint_repeat/controls.py",
    "scripts/fresh_endpoint_repeat/plan.py",
    "scripts/fresh_endpoint_repeat/run.py",
    "scripts/fresh_endpoint_repeat/scoring.py",
)


def render() -> list[Cell]:
    """Only the seal, qualified neutral previews and packet bodies are readable inputs."""
    frozen = controls.ROOT / "frozen"
    seal = _read(frozen / "seal.json")
    require(digest(seal) == controls.SEAL and SYSTEM.count(BASE) == 1, "control_contract_drift")
    require(
        digest(SYSTEM.encode())
        == "9b95b4fda41557bcc730fa821b7ba96cda2ab711cebd79d011730cd35686549b",
        "baseline_drift",
    )
    spec = builtin_model_specs()[MODEL]
    require(_cost(spec, INPUT, OUTPUT) == BUDGET.max_cost_usd, "cost_basis_changed")
    cells = []
    for key, pin in sorted(json.loads(seal)["packets_sha256"].items()):
        raw = _read(frozen / "packets" / (key + ".json"))
        require(digest(raw) == pin, "packet_drift")
        packet = controls.Packet.model_validate_json(raw)
        work = controls.native_work(packet, pin)
        require(
            AssessmentWork.model_validate_json(_read(controls.ROOT / "previews" / (key + ".json")))
            == work,
            "preview_drift",
        )
        msg = json.loads(work.context.messages[0].content)
        docs = []
        for doc in work.context.documents:
            view = doc.model_dump(mode="json", exclude={"content_json"})
            content = json.loads(doc.content_json)
            if doc.kind == "registry":
                view["columns"] = ["ref", "document_id", "field_pointer"]
                view["whole_field_locations"] = [
                    [e["ref"], e["document_id"], e["field_pointer"]] for e in content["entries"]
                ]
            else:
                view["structured_content"] = content
            docs.append(view)
        msg.update(
            active_unit_ids=[packet.claim_id], native_work_view={"context": {"documents": docs}}
        )
        user = compact(msg)
        (batch,) = work.batches
        pair = {}
        for arm in "BC" if key in FIRST_B else "CB":
            system = SYSTEM if arm == "B" else SYSTEM.replace(BASE, BASE + " " + ADDITION)
            request_id = digest(encoded([work.fingerprint, MODEL, "high", system, user]))
            scope = scope_for_batch(work, batch.batch_id, request_id)
            request = ModelRequest(
                model_identifier=MODEL,
                provider="openai",
                deployment=ModelDeployment.CLOUD,
                messages=(
                    ModelMessage(MessageRole.SYSTEM, system),
                    ModelMessage(MessageRole.USER, user),
                ),
                invocation=InvocationContext(
                    "endpoint_fact_assessment",
                    "paired-uncertainty-1",
                    tuple(UUID(s.version) for s in packet.sources),
                ),
                response_schema=assessment_response_schema(work, scope),
                settings=ModelSettings(thinking="high"),
                budget=BUDGET,
            )
            wire = _prepare_wire(work, scope, request, spec, guard=None)
            cells.append(Cell(key + "-" + arm, work, wire))
            pair[arm] = wire
        for b, c in zip(pair["B"].endpoints, pair["C"].endpoints, strict=True):
            require(
                b.body_utf8.count(BASE) == 1
                and ADDITION not in b.body_utf8
                and b.body_utf8.replace(BASE, BASE + " " + ADDITION) == c.body_utf8,
                "pair_not_isolated",
            )
    require(len(cells) == 16, "wrong_cell_count")
    return cells


def materials() -> tuple[list[Cell], bytes]:
    cells = render()
    admitted = controls.verify()
    scoring = _read(controls.ROOT / "frozen/scoring.json")
    require(digest(scoring) == admitted["scoring_sha256"], "scoring_drift")
    manifest = encoded(
        {
            "contract": "q010-fresh-paired-uncertainty-1",
            "predecessor_approval_sha256": PREDECESSOR,
            "model": MODEL,
            "reasoning": "high",
            "live_directory": ROOT.relative_to(REPO).as_posix(),
            "source_verification": admitted,
            "clarification": ADDITION,
            "budget": {
                "input_counts": 16,
                "generations": 16,
                "retries": 0,
                "input_per_generation": INPUT,
                "output_per_generation": OUTPUT,
                "aggregate_generation_input": 16 * INPUT,
                "aggregate_generation_output": 16 * OUTPUT,
                "max_generation_usd": str(BUDGET.max_cost_usd),
                "aggregate_generation_usd": str(16 * BUDGET.max_cost_usd),
                "count_seconds": COUNT_SECONDS,
                "generation_seconds": GENERATION_SECONDS,
                "wall_seconds": WALL_SECONDS,
            },
            "slots": [
                {
                    "cell": c.name,
                    "filename": filename(c, e),
                    "work_sha256": c.work.fingerprint,
                    "request_sha256": c.wire.native_request_sha256,
                    "http_body_bytes": len(e.body_utf8.encode()),
                    **e.model_dump(mode="json", exclude={"body_utf8"}),
                }
                for c, e in schedule(cells)
            ],
            "scoring": json.loads(scoring),
            "stops": STOPS,
            "model_spec": cells[0].wire.model_spec.model_dump(mode="json"),
            "implementation": {p: ledger.file_hash(REPO / p) for p in IMPLEMENTATION},
        }
    )
    return cells, manifest


def issue(root: Path) -> str:
    cells, plan = materials()
    _unlinked(root).mkdir(exist_ok=False)
    (root / "requests").mkdir()
    for cell, end in schedule(cells):
        _durable_write(root / "requests" / filename(cell, end), end.body_utf8.encode())
    _durable_write(root / "plan.json", plan)
    approval = digest(plan)
    ledger.initialize_ledger(root, approval)
    return approval


def verify(root: Path, approval: str) -> list[Cell]:
    cells, plan = materials()
    require(
        digest(plan) == approval and _read(root / "plan.json") == plan, "approval_or_source_drift"
    )
    files = {filename(c, e): e.body_utf8.encode() for c, e in schedule(cells)}
    folder = root / "requests"
    require(
        set(files) == {p.name for p in folder.iterdir()}
        and all(_read(folder / k) == v for k, v in files.items()),
        "frozen_request_drift",
    )
    ledger.ledger_state(root, approval)
    return cells
