"""Local OpenAI wire and fixture journals for fixed saved-review registrations."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

import httpx
from open_hollywood_engine.evaluations.assessment_compact_presentation import (
    NOTICE,
    PROVENANCE_ID,
    SYSTEM,
    compact,
)
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    EvidenceRegistry,
    assessment_response_schema,
    bind_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentReceipt,
    AssessmentWork,
    complete_work,
)
from open_hollywood_engine.evaluations.assessment_work_brief import preview_work_briefs
from open_hollywood_engine.evaluations.review_evidence import (
    JsonObject,
    require,
    strict_object,
    string_value,
)
from open_hollywood_engine.models.assessment_openai import (
    MappedResponse,
    WireEndpoint,
    WireMapping,
    _prepare_wire,
    check_outgoing,
    count_admitted,
    map_response,
)
from open_hollywood_engine.models.contracts import (
    InvocationContext,
    MessageRole,
    ModelCallBudget,
    ModelDeployment,
    ModelMessage,
    ModelRequest,
    ModelSettings,
)
from open_hollywood_engine.models.openai_catalog import builtin_model_specs

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import assessment_delivery as io
from open_hollywood_api.services import saved_review_completion as saved
from open_hollywood_api.services.production_association_records import ArtifactSelection

Scenario = Literal["complete", "missing-terminal", "count-rejected"]


def _packet(source: saved._Prepared, work: AssessmentWork, scope: AssessmentScope) -> JsonObject:
    intake = source.intake
    assert intake.briefs is not None and intake.declarations is not None
    preview = preview_work_briefs(work, scope, intake.declarations, intake.briefs)
    require(all(u.status == "declared_consistent" for u in preview.units), "saved_wire_claim_scope")
    documents = []
    for doc in work.context.documents:
        view = doc.model_dump(mode="json", exclude={"content_json"})
        if doc.kind == "scope":
            require(doc.identity == PROVENANCE_ID, "saved_wire_unknown_local_document")
            view["local_only"] = True
        elif doc.kind == "registry":
            # scope_for_batch already verifies every version, pointer, quote, hash and offset.
            registry = EvidenceRegistry.model_validate_json(doc.content_json)
            require(all(e.paragraph is None for e in registry.entries), "saved_wire_partial_field")
            view["columns"] = ["ref", "document_id", "field_pointer"]
            view["whole_field_locations"] = [
                [e.ref, e.document_id, e.field_pointer] for e in registry.entries
            ]
        else:
            view["structured_content"] = strict_object(doc.content_json)
        documents.append(view)
    native = work.model_dump(mode="json")
    native["context"]["documents"] = documents
    return {
        "contract": "saved-review-openai-packet-1",
        "selected_artifact": source.selected.model_dump(mode="json"),
        "original_review": source.pin.review.model_dump(mode="json"),
        "reviewed_draft": source.pin.draft.model_dump(mode="json"),
        "batch_id": scope.batch_id,
        "active_unit_ids": list(scope.active_unit_ids),
        "native_work_view": native,
        "original_scope_declarations": intake.declarations.model_dump(mode="json"),
        "original_work_briefs": intake.briefs.model_dump(mode="json"),
        "whole_intake_dispositions": [f.model_dump(mode="json") for f in intake.findings],
        "availability_notice": NOTICE,
    }


@dataclass(frozen=True)
class _Plan:
    work: AssessmentWork
    wire: WireMapping
    files: dict[str, bytes]
    archive: saved._Archive
    source: saved._Prepared

    @property
    def digest(self) -> str:
        return storage._sha(self.files["request-manifest.json"])


def _prepare(registration: str, selection: ArtifactSelection | None) -> _Plan:
    archive = saved._open(registration, allow_capture=True)
    source = saved._prepare(archive, selection)
    work = source.intake.pending_work
    assert work is not None
    spec = builtin_model_specs()["gpt-6.1-sol"]
    scope = scope_for_batch(work, source.manifest.batch_id, source.pin.request_sha256)
    packet = _packet(source, work, scope)
    versions = (UUID(source.pin.review.version_id), UUID(source.pin.draft.version_id))
    input_limit = 96_000 if isinstance(source.manifest, saved._CaptureManifest) else 24_000
    request = ModelRequest(
        provider="openai",
        deployment=ModelDeployment.CLOUD,
        model_identifier=spec.model_identifier,
        invocation=InvocationContext(
            "read_only_saved_review_assessment", "saved-review-openai-packet-1", versions
        ),
        messages=(
            ModelMessage(MessageRole.SYSTEM, SYSTEM),
            ModelMessage(MessageRole.USER, compact(packet)),
        ),
        settings=ModelSettings(thinking="high"),
        budget=ModelCallBudget(input_limit, 32_000, Decimal("0.60")),
        response_schema=assessment_response_schema(work, scope),
    )
    wire = _prepare_wire(work, scope, request, spec, guard=active_secret_guard())
    files = {"source-receipt.json": source.files["source-receipt.json"]}
    for end in wire.endpoints:
        files[end.stage + "-request.json"] = end.body_utf8.encode()
    manifest = wire.model_dump(mode="json", exclude={"endpoints"})
    manifest["endpoints"] = [
        e.model_dump(mode="json", exclude={"body_utf8"}) for e in wire.endpoints
    ]
    files["request-manifest.json"] = encoded(
        {
            "contract": "saved-review-openai-request-1",
            "wire": manifest,
            "input_artifact_version_ids": [str(v) for v in versions],
            "source_receipt_bytes_sha256": storage._sha(files["source-receipt.json"]),
            "selected": source.selected.model_dump(mode="json"),
            "count_limit": 1,
            "generation_limit": 1,
            "retry_limit": 0,
            "live_calls": 0,
        }
    )
    return _Plan(work, wire, files, archive, source)


def _reply(plan: _Plan, endpoint: WireEndpoint, scenario: Scenario) -> bytes:
    captured = isinstance(plan.source.manifest, saved._CaptureManifest)
    fixture_input_tokens = 60_000 if captured else 100
    if endpoint.stage == "input_count":
        return encoded(
            {
                "object": "response.input_tokens",
                "input_tokens": plan.wire.max_input_tokens + 1
                if scenario == "count-rejected"
                else fixture_input_tokens,
            }
        )
    if captured:
        # This fixture exercises binding only. It is independent of operator gold.
        declarations = plan.source.intake.declarations
        assert declarations is not None
        (claim,) = declarations.declarations
        final = compact(
            {
                "assessments": {
                    "Q008": {
                        "support": "uncertain",
                        "evidence": [
                            ref for scope in claim.source_scopes for ref in scope.evidence_refs
                        ],
                        "reason": "Injected Q008 transport fixture; no assessor judgment.",
                    }
                }
            }
        )
    else:
        evidence, eligible = saved._audit(plan.archive, plan.source, "complete")
        require(eligible, "saved_wire_response_fixture")
        final = string_value(strict_object(evidence["terminal.json"].decode())["raw_final"])
    return encoded(
        {
            "id": "resp_saved_review_fixture",
            "model": plan.wire.model_spec.model_identifier,
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": final}],
                }
            ],
            "usage": {
                "input_tokens": fixture_input_tokens,
                "output_tokens": 20,
                "total_tokens": fixture_input_tokens + 20,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 5},
            },
        }
    )


def _header(plan: _Plan, scenario: Scenario, journal_id: str) -> dict[str, bytes]:
    require(scenario in ("complete", "missing-terminal", "count-rejected"), "saved_wire_scenario")
    identity = UUID(journal_id)
    require(identity.version == 4 and str(identity) == journal_id, "saved_wire_journal_id")
    return plan.files | {
        "journal.json": encoded(
            {
                "contract": "saved-review-openai-fixture-journal-1",
                "origin": "injected_fixture",
                "journal_id": journal_id,
                "scenario": scenario,
                "request_manifest_sha256": plan.digest,
                "live_calls": 0,
            }
        )
    }


def _intent(plan: _Plan, end: WireEndpoint, previous: bytes) -> bytes:
    return encoded(
        {
            "kind": "intent",
            "request_manifest_sha256": plan.digest,
            "previous_sha256": storage._sha(previous),
            "endpoint": end.model_dump(mode="json", exclude={"body_utf8"}),
        }
    )


def _outcome(intent: bytes, status: int, body: bytes) -> bytes:
    # All admitted bodies are independently pinned authored fixture bytes.
    return encoded(
        {
            "kind": "outcome",
            "intent_sha256": storage._sha(intent),
            "http_status": status,
            "response_utf8": body.decode(),
            "response_bytes_sha256": storage._sha(body),
        }
    )


def _close(previous: bytes) -> bytes:
    return encoded({"kind": "stop", "previous_sha256": storage._sha(previous)})


def _request(end: WireEndpoint) -> httpx.Request:
    return httpx.Request(
        end.method,
        end.destination + end.path,
        content=end.body_utf8.encode(),
        headers={"Content-Type": "application/json"},
    )


def _mock_transport(end: WireEndpoint, reply: bytes, scenario: Scenario) -> httpx.MockTransport:
    def injected(actual: httpx.Request) -> httpx.Response:
        check_outgoing(end, actual)
        if end.stage == "generation" and scenario == "missing-terminal":
            raise io.FixtureInterrupted()
        return httpx.Response(200, content=reply)

    return httpx.MockTransport(injected)


def capture(
    registration: str, selection: ArtifactSelection | None, journal: Path, scenario: Scenario
) -> None:
    """Write intent before touching the mock. An open intent consumes its one fixture slot."""
    plan = _prepare(registration, selection)
    files = _header(plan, scenario, str(uuid4()))
    journal = storage._destination(journal, (saved.REGISTERED.archive, saved.CAPTURED_Q008.archive))
    journal.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        io._durable_write(journal / name, data)

    def append(name: str, data: bytes) -> None:
        require(io._read_journal(journal) == files, "saved_wire_journal_changed")
        io._durable_write(journal / name, data)
        files[name] = data

    previous = files["journal.json"]
    for end in plan.wire.endpoints:
        current = _prepare(registration, selection)
        require(current.files == plan.files, "saved_wire_source_changed")
        req = _request(end)
        check_outgoing(end, req)
        reply = (
            b""
            if end.stage == "generation" and scenario == "missing-terminal"
            else _reply(current, end, scenario)
        )
        previous = _intent(plan, end, previous)
        append(end.stage + "-intent.json", previous)
        with _mock_transport(end, reply, scenario) as mock:
            try:
                response = mock.handle_request(req)
            except io.FixtureInterrupted:
                return
            try:
                require(
                    response.status_code == 200 and response.content == reply,
                    "saved_wire_fixture_response",
                )
                previous = _outcome(previous, response.status_code, response.content)
            finally:
                response.close()
        append(end.stage + "-outcome.json", previous)
        if end.stage == "input_count" and not count_admitted(
            plan.wire, map_response(end.stage, 200, reply, plan.wire.model_spec)
        ):
            break
    append("stop.json", _close(previous))


def _audit(plan: _Plan, scenario: Scenario, journal: Path) -> tuple[JsonObject, dict[str, bytes]]:
    files = io._read_journal(journal)
    header = strict_object(files["journal.json"].decode())
    expected = _header(plan, scenario, string_value(header["journal_id"]))
    require(all(files.get(k) == v for k, v in expected.items()), "saved_wire_manifest_or_version")
    previous = expected["journal.json"]
    count = generation = pending = 0
    counted_tokens = None
    mapped: MappedResponse | None = None
    state = "missing_count_intent"
    can_close = False
    for end in plan.wire.endpoints:
        key = end.stage + "-intent.json"
        if key not in files:
            break
        previous = _intent(plan, end, previous)
        expected[key] = previous
        require(files[key] == previous, "saved_wire_intent_binding")
        count += int(end.stage == "input_count")
        generation += int(end.stage == "generation")
        key = end.stage + "-outcome.json"
        if key not in files:
            state, pending = "missing_" + end.stage + "_terminal", 1
            break
        require(
            end.stage != "generation" or scenario != "missing-terminal",
            "saved_wire_unobserved_response",
        )
        reply = _reply(plan, end, scenario)
        previous = _outcome(previous, 200, reply)
        expected[key] = previous
        require(files[key] == previous, "saved_wire_outcome_binding")
        observed = strict_object(files[key].decode())
        mapped = map_response(
            end.stage,
            200,
            string_value(observed["response_utf8"]).encode(),
            plan.wire.model_spec,
            guard=active_secret_guard(),
        )
        if end.stage == "input_count":
            counted_tokens = mapped.counted_input_tokens
            if not count_admitted(plan.wire, mapped):
                state, can_close = "count_rejected", True
                break
            state = "missing_generation_intent"
        else:
            state, can_close = "generation_observed", True
    closed = "stop.json" in files
    if closed:
        require(can_close, "saved_wire_premature_stop")
        expected["stop.json"] = _close(previous)
    elif can_close:
        state = "missing_stop"
    require(files == expected, "saved_wire_journal_coverage")
    scope = scope_for_batch(plan.work, plan.wire.batch_id, plan.digest)
    bound = None
    if closed and state == "generation_observed":
        require(mapped is not None and mapped.state == "complete", "saved_wire_incomplete_response")
        assert mapped is not None and mapped.raw_final is not None
        receipt = AssessmentReceipt(
            work_sha256=scope.work_sha256,
            batch_id=scope.batch_id,
            request_sha256=scope.request_sha256,
            attempt_id="fixture-" + storage._sha(expected["journal.json"]),
            status="valid",
            result_sha256=mapped.raw_final_utf8_sha256,
            assessed_unit_ids=scope.active_unit_ids,
            input_tokens=mapped.usage.input_tokens,
            output_tokens=mapped.usage.output_tokens,
            reasoning_tokens=mapped.usage.reasoning_tokens,
            active_seconds=0,
        )
        bound = bind_assessment_result(plan.work, scope, receipt, mapped.raw_final)
        state = "bound_unassessed"
    completion = complete_work(
        plan.work, (bound.receipt,) if bound else (), {scope.batch_id: plan.digest}
    )
    return {
        "contract": "saved-review-openai-fixture-audit-1",
        "origin": "injected_fixture",
        "state": state,
        "request_manifest_sha256": plan.digest,
        "closed": closed,
        "fixture_count_attempts": count,
        "fixture_generation_attempts": generation,
        "counted_input_tokens": counted_tokens,
        "generation_usage": mapped.usage.model_dump(mode="json")
        if mapped and mapped.stage == "generation"
        else None,
        "possibly_sent_without_terminal": pending,
        "result": bound.model_dump(mode="json") if bound else None,
        "last_observed_response": mapped.model_dump(mode="json") if mapped else None,
        "completion": completion.model_dump(mode="json"),
        "fixture_publication_eligible": bool(closed and completion.complete_delivery and bound),
        "usage_origin": "injected_fixture",
        "actual_billed_cost": None,
        "model_evidence": False,
        "production_attachment_eligible": False,
        "writer_dispatch_authorized": False,
        "live_calls": 0,
    }, files


def export(
    registration: str,
    selection: ArtifactSelection | None,
    journal: Path,
    scenario: Scenario,
    destination: Path,
    *,
    publish: bool = False,
) -> str:
    """Recollect source and verify the full journal before publishing or reusing a bundle."""

    def collect() -> dict[str, bytes]:
        plan = _prepare(registration, selection)
        report, files = _audit(plan, scenario, journal)
        if publish:
            require(
                report["fixture_publication_eligible"] is True, "saved_wire_publication_incomplete"
            )
            files["completion.json"] = encoded(
                {
                    "contract": "saved-review-openai-fixture-completion-1",
                    "source_receipt": strict_object(files["source-receipt.json"].decode()),
                    "audit": report,
                }
            )
        files["audit.json"] = encoded(report)
        files["manifest.json"] = encoded(
            {
                "contract": "saved-review-openai-fixture-export-1",
                "mode": "publish" if publish else "audit",
                "files_sha256": {k: storage._sha(v) for k, v in files.items()},
            }
        )
        return files

    files = collect()

    def recheck() -> None:
        require(collect() == files, "saved_wire_export_drift")

    return storage._publish(
        destination,
        files,
        (saved.REGISTERED.archive, saved.CAPTURED_Q008.archive, journal),
        recheck,
    )
