"""Offline intake over existing authenticated review exporters; no model dispatch."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal
from uuid import UUID

from open_hollywood_engine.evaluations import assessment_intake as domain
from open_hollywood_engine.evaluations.assessment_intake import (
    IntakePlan,
    IntakeResult,
    IntakeSource,
    build_intake_source,
    compile_intake,
    empty_intake_plan,
    render_intake,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.probe_review_evidence import (
    ProbeArchiveContract,
    ProbeRequest,
    parse_model_json,
)
from open_hollywood_engine.evaluations.review_evidence import (
    JsonObject,
    Record,
    require,
    strict_object,
    string_value,
)
from pydantic import Field, JsonValue

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.probe_review_export import (
    archive_contract,
    collect_probe_export,
    protected_archives,
)
from open_hollywood_api.services.review_evidence_export import collect_export

MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_OUTPUT_BYTES = 64 * 1024 * 1024


class IntakeEntry(Record):
    review_id: str
    reason: str
    source: IntakeSource | None
    # Original incompatible exports also remain inspectable, without promoting them.
    incompatible_export: JsonObject | None = None


class IntakeCollection(Record):
    origin: Literal["saved_review", "diagnostic_probe"]
    source_path: str
    review_ids: tuple[str, ...] = Field(min_length=1, max_length=12)
    entries: tuple[IntakeEntry, ...]
    live_calls: Literal[0] = 0


class IntakeBatchPlan(Record):
    contract: Literal["ordinary-review-intake-batch-plan-1"] = "ordinary-review-intake-batch-plan-1"
    plans: dict[str, IntakePlan]


def _unlinked(path: Path) -> Path:
    path = path.absolute()
    for part in (path, *path.parents):
        require(not part.is_symlink() and not part.is_junction(), "intake_linked_path")
    return path.resolve()


def collect_intakes(
    origin: Literal["saved_review", "diagnostic_probe"],
    source_path: Path,
    review_ids: tuple[str, ...],
    *,
    _contract: ProbeArchiveContract | None = None,
) -> IntakeCollection:
    """Reuse the existing supported source contracts, including their refusal behavior."""
    require(
        1 <= len(review_ids) <= 12 and len(set(review_ids)) == len(review_ids), "intake_selection"
    )
    source_path = _unlinked(source_path)
    entries: list[IntakeEntry] = []
    if origin == "diagnostic_probe":
        exported = collect_probe_export(source_path, review_ids, _contract=_contract)
        for probe in exported.entries:
            projection = probe.projection
            attempt = next(
                a for a in probe.snapshot.attempts if a.number == projection.successful_attempt
            )
            request = ProbeRequest.model_validate_json(attempt.files["request"].text)
            version = projection.manifest.candidate_version_id
            draft = next(a for a in request.inputs if a.artifact_version_id == version)
            source = build_intake_source(
                origin=origin,
                review_id=projection.manifest.trial,
                report_origin="raw_model",
                messages=request.messages,
                current_version=version,
                current_prose=string_value(draft.content.get("prose")),
                report=parse_model_json(projection.raw_model_content),
                operator_provenance=probe.model_dump(mode="json"),
            )
            entries.append(
                IntakeEntry(review_id=source.review_id, reason="compatible", source=source)
            )
    else:
        require(origin == "saved_review", "intake_origin")
        ids = tuple(UUID(i) for i in review_ids)
        require(tuple(str(i) for i in ids) == review_ids, "intake_noncanonical_id")
        saved = collect_export(source_path, ids)
        for entry in saved.entries:
            if entry.reason != "compatible":
                entries.append(
                    IntakeEntry(
                        review_id=entry.invocation_id,
                        reason=entry.reason,
                        source=None,
                        incompatible_export=entry.model_dump(mode="json"),
                    )
                )
                continue
            snapshot = entry.snapshot
            assert snapshot is not None and snapshot.critique.content is not None
            draft_source = next(
                s for s in snapshot.sources if s.version_id == snapshot.draft_version_id
            )
            assert draft_source.content is not None
            source = build_intake_source(
                origin=origin,
                review_id=entry.invocation_id,
                report_origin="saved_normalized_and_audit",
                messages=snapshot.messages,
                current_version=snapshot.draft_version_id,
                current_prose=string_value(draft_source.content.get("prose")),
                report={
                    "saved_critique": snapshot.critique.content,
                    "saved_native_audit": snapshot.native_audit,
                },
                operator_provenance=entry.model_dump(mode="json"),
            )
            entries.append(
                IntakeEntry(review_id=source.review_id, reason="compatible", source=source)
            )
    result = IntakeCollection(
        origin=origin, source_path=str(source_path), review_ids=review_ids, entries=tuple(entries)
    )
    active_secret_guard().ensure_safe(result.model_dump(mode="json"), destination="review intake")
    return result


def template(collection: IntakeCollection) -> IntakeBatchPlan:
    return IntakeBatchPlan(
        plans={
            e.review_id: empty_intake_plan(e.source)
            for e in collection.entries
            if e.source is not None
        }
    )


def read_plan(path: Path) -> IntakeBatchPlan:
    path = _unlinked(path)
    with path.open("rb") as stream:
        data = stream.read(MAX_INPUT_BYTES + 1)
    require(len(data) <= MAX_INPUT_BYTES, "intake_plan_too_large")
    value = strict_object(data.decode("utf-8"))
    active_secret_guard().ensure_safe(value, destination="intake plan")
    return IntakeBatchPlan.model_validate_json(json.dumps(value))


def _encoded(value: JsonObject) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_intake(
    destination: Path,
    collection: IntakeCollection,
    plan: IntakeBatchPlan | None = None,
    *,
    _contract: ProbeArchiveContract | None = None,
) -> Literal["created", "reused"]:
    """Recompute and re-read before publication; publish only new or byte-identical output."""
    collection = IntakeCollection.model_validate_json(collection.model_dump_json())
    require(
        collection.review_ids == tuple(e.review_id for e in collection.entries), "intake_selection"
    )
    path = Path(collection.source_path)
    destination = _unlinked(destination)
    if collection.origin == "diagnostic_probe":
        # Sibling prepared archive is part of the existing registered contract.
        _contract = _contract or archive_contract(path)
        for protected in protected_archives(path, _contract):
            require(not destination.is_relative_to(protected), "intake_protected_source")
    else:
        require(destination != path.resolve(), "intake_protected_source")
    require(
        collection
        == collect_intakes(collection.origin, path, collection.review_ids, _contract=_contract),
        "intake_source_changed",
    )
    supplied = plan is not None
    plan = (
        template(collection)
        if plan is None
        else IntakeBatchPlan.model_validate_json(plan.model_dump_json())
    )
    require(
        set(plan.plans) == {e.review_id for e in collection.entries if e.source is not None},
        "intake_plan_coverage",
    )
    files: dict[str, bytes] = {}
    index_rows: list[JsonValue] = []
    guard = active_secret_guard()
    for number, entry in enumerate(collection.entries, 1):
        stem = f"review-{number:02d}"
        if entry.source is None:
            files[stem + ".json"] = _encoded(entry.model_dump(mode="json"))
            index_rows.append(
                {
                    "review_id": entry.review_id,
                    "file": stem + ".json",
                    "reason": entry.reason,
                    "pending": 0,
                    "holds": 0,
                }
            )
            continue
        result: IntakeResult = compile_intake(entry.source, plan.plans[entry.review_id])
        files[stem + ".json"] = _encoded(result.model_dump(mode="json"))
        files[stem + ".md"] = render_intake(result).encode("utf-8")
        index_rows.append(
            {
                "review_id": entry.review_id,
                "file": stem + ".json",
                "view": stem + ".md",
                "reason": "compatible",
                "pending": sum(f.status == "pending_assessment" for f in result.findings),
                "holds": sum(f.status == "hold" for f in result.findings),
            }
        )
    files["plan.json"] = _encoded(plan.model_dump(mode="json"))
    index: JsonObject = {
        "contract": "ordinary-review-intake-index-1",
        "mode": "declared_intake" if supplied else "inventory",
        "origin": collection.origin,
        "reviews": index_rows,
        "live_calls": 0,
        "model_input": False,
        "writer_dispatch_authorized": False,
    }
    files["index.json"] = _encoded(index)
    index_text = files["index.json"].decode("utf-8")
    fence = "`" * (3 + index_text.count("`"))
    files["index.md"] = (
        "# Read-only review intake\n\nSee each adjacent literal review view and plan.\n"
        "Copy plan.json outside this immutable bundle before authoring declarations.\n"
        "Inventory is not admission. Pending work is not inference or a completed assessment.\n\n"
        + fence
        + "json\n"
        + index_text
        + fence
        + "\n"
    ).encode("utf-8")
    require(sum(map(len, files.values())) <= MAX_OUTPUT_BYTES, "intake_export_too_large")
    for data in files.values():
        guard.ensure_safe(data.decode("utf-8"), destination="review intake publication")
    require(
        collection
        == collect_intakes(collection.origin, path, collection.review_ids, _contract=_contract),
        "intake_source_changed",
    )
    manifest: JsonObject = {
        "contract": "ordinary-review-intake-manifest-1",
        "origin": collection.origin,
        "source_path": collection.source_path,
        "review_ids": list(collection.review_ids),
        "source_sha256": canonical_sha256(collection.model_dump(mode="json")),
        "plan_sha256": canonical_sha256(plan.model_dump(mode="json")),
        "implementation_sha256": {
            "domain": hashlib.sha256(Path(domain.__file__).read_bytes()).hexdigest(),
            "adapter": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
        "files_sha256": {n: hashlib.sha256(d).hexdigest() for n, d in files.items()},
        "live_calls": 0,
    }
    files["manifest.json"] = _encoded(manifest)
    guard.ensure_safe(manifest, destination="review intake manifest")
    _unlinked(destination)
    if destination.exists():
        require(
            destination.is_dir() and {f.name for f in destination.iterdir()} == set(files),
            "intake_export_conflict",
        )
        for name, data in files.items():
            target = _unlinked(destination / name)
            require(
                target.is_file() and target.stat().st_size == len(data), "intake_export_conflict"
            )
            require(target.read_bytes() == data, "intake_export_conflict")
        return "reused"
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        with (destination / name).open("xb") as stream:
            stream.write(data)
    return "created"
