"""Authored scope/citation regressions; no private captures, live transport or database."""

from __future__ import annotations

import json
import socket
import sqlite3
from typing import Any

import httpx
import pytest
from open_hollywood_engine.evaluations import assessment_result as result_module
from open_hollywood_engine.evaluations.assessment_result import (
    AssessmentScope,
    EvidenceLocation,
    EvidenceRegistry,
    assessment_response_schema,
    bind_assessment_result,
    render_assessment_result,
    scope_for_batch,
)
from open_hollywood_engine.evaluations.assessment_work import (
    AssessmentContext,
    AssessmentReceipt,
    AssessmentWork,
    ContextDocument,
    DeclaredLink,
    ReportField,
    SelectedStatement,
    complete_work,
    partition_work,
)
from open_hollywood_engine.evaluations.review_evidence import (
    EvidenceError,
    SavedMessage,
    strict_object,
    text_hash,
)
from pydantic import ValidationError

ERRORS = (EvidenceError, ValidationError, json.JSONDecodeError)


def many_field_work(work: AssessmentWork, *, duplicate_key: bool = False) -> AssessmentWork:
    source = document("many-fields", "source", {"first": "one", "second": "two", "third": "three"})
    if duplicate_key:
        raw = '{"first":"one","first":"one","second":"two","third":"three"}'
        source = source.model_copy(update={"content_json": raw, "content_sha256": text_hash(raw)})
    entries = tuple(
        location(source, f"M{i}", "/" + key, 0, len(value), None)
        for i, (key, value) in enumerate(
            {"first": "one", "second": "two", "third": "three"}.items()
        )
    )
    registry = document(
        "index", "registry", EvidenceRegistry(entries=entries).model_dump(mode="json")
    )
    documents = tuple(d for d in work.context.documents if d.kind != "registry") + (
        source,
        registry,
    )
    return partition_work(work.context.model_copy(update={"documents": documents}), 2)


def test_many_fields_parse_source_once_per_validation_without_cross_call_cache(
    work: AssessmentWork,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    changed = many_field_work(work)
    source = next(d for d in changed.context.documents if d.identity == "many-fields")
    original = strict_object
    parsed: list[str] = []

    def counted(raw: str) -> Any:
        if raw == source.content_json:
            parsed.append(raw)
        return original(raw)

    monkeypatch.setattr(result_module, "strict_object", counted)
    for expected in (1, 2):
        scope_for_batch(changed, changed.batches[0].batch_id, "a" * 64)
        assert len(parsed) == expected


def test_many_field_reuse_does_not_hide_duplicate_keys_or_changed_source(
    work: AssessmentWork,
) -> None:
    with pytest.raises(ERRORS):
        duplicate = many_field_work(work, duplicate_key=True)
        scope_for_batch(duplicate, duplicate.batches[0].batch_id, "a" * 64)
    checked = many_field_work(work)
    scope_for_batch(checked, checked.batches[0].batch_id, "a" * 64)
    source = document(
        "many-fields", "source", {"first": "changed", "second": "two", "third": "three"}
    )
    registry = json.loads(
        next(d.content_json for d in checked.context.documents if d.kind == "registry")
    )
    for entry in registry["entries"]:
        entry["document_sha256"] = source.content_sha256
    new_registry = document("index", "registry", registry)
    documents = tuple(
        d
        for d in checked.context.documents
        if d.kind != "registry" and d.identity != source.identity
    ) + (source, new_registry)
    changed = partition_work(checked.context.model_copy(update={"documents": documents}), 2)
    with pytest.raises(ValueError, match="evidence_field_mismatch"):
        scope_for_batch(changed, changed.batches[0].batch_id, "a" * 64)


@pytest.fixture(autouse=True)
def offline(monkeypatch: pytest.MonkeyPatch) -> None:
    def deny(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("Real transports and database operations forbidden")

    for owner, name in (
        (httpx.Client, "request"),
        (httpx.AsyncClient, "request"),
        (socket.socket, "connect"),
        (socket.socket, "connect_ex"),
        (socket, "create_connection"),
        (socket, "getaddrinfo"),
        (sqlite3, "connect"),
    ):
        monkeypatch.setattr(owner, name, deny)


def document(identity: str, kind: Any, content: dict[str, Any]) -> ContextDocument:
    text = json.dumps(content, ensure_ascii=False)
    return ContextDocument(
        identity=identity,
        version="v1",
        kind=kind,
        content_json=text,
        content_sha256=text_hash(text),
    )


def location(
    source: ContextDocument, ref: str, field: str, start: int, end: int, paragraph: int | None
) -> EvidenceLocation:
    text = json.loads(source.content_json)[field[1:]]
    return EvidenceLocation(
        ref=ref,
        document_id=source.identity,
        document_version=source.version,
        document_sha256=source.content_sha256,
        field_pointer=field,
        field_sha256=text_hash(text),
        start=start,
        end=end,
        quote=text[start:end],
        paragraph=paragraph,
    )


@pytest.fixture
def work() -> AssessmentWork:
    # Repeated text, Unicode code points, CRLF and edge spaces must keep exact locations.
    prose = (
        "Mara reads the date.\r\n\r\n écho 🔑 \r\n\r\n écho 🔑 \r\n\r\n"
        "She compares the handwriting."
    )
    draft = document("current-draft", "source", {"prose": prose})
    plan = document(
        "next-plan", "source", {"outcome": "Mara enters, then tests a private flourish."}
    )
    registry = EvidenceRegistry(
        entries=(
            location(draft, "S1", "/prose", 0, 20, 1),
            location(draft, "S2", "/prose", 24, 32, 2),
            location(draft, "S3", "/prose", 36, 44, 3),
            location(draft, "S4", "/prose", 48, len(prose), 4),
            location(
                plan, "S5", "/outcome", 0, len(json.loads(plan.content_json)["outcome"]), None
            ),
        )
    )
    claims = [
        "Mara notices the date and compares the handwriting.",
        "The handwriting match proves the private flourish was tested.",
        "The next scene starts with Mara already inside.",
        "An echo is repeated.",
        "Entry is planned.",
        "A later test is planned.",
        "The current draft records a date.",
    ]
    report = document("review", "report", {"claims": claims})
    registry_document = document("index", "registry", registry.model_dump(mode="json"))
    documents = (draft, plan, report, registry_document)
    context = AssessmentContext(
        provenance="synthetic_fixture",
        origin_sha256="a" * 64,
        documents=documents,
        report_fields=tuple(
            ReportField(field_id=f"F{i}", pointer=f"/claims/{i}", text=text)
            for i, text in enumerate(claims)
        ),
        statements=tuple(
            SelectedStatement(unit_id=f"U{i}", field_id=f"F{i}", start=0, end=len(t), quote=t)
            for i, t in enumerate(claims)
        ),
        declared_links=(
            DeclaredLink(
                link_id="whole-contrast", unit_ids=("U0", "U1"), origin="authored_diagnostic"
            ),
        ),
        messages=(
            SavedMessage(role="user", content=json.dumps([d.model_dump() for d in documents])),
        ),
    )
    return partition_work(context, 2)


def response(work: AssessmentWork, index: int = 0) -> dict[str, Any]:
    return {
        "assessments": {
            unit: {
                "support": "supported",
                "evidence": ["S1", "S4"],
                "reason": "Authored model-shaped judgment, not application-established truth.",
            }
            for unit in work.batches[index].unit_ids
        }
    }


def attempt(
    work: AssessmentWork, raw: str, index: int = 0
) -> tuple[AssessmentScope, AssessmentReceipt]:
    scope = scope_for_batch(work, work.batches[index].batch_id, str(index + 1) * 64)
    return scope, AssessmentReceipt(
        work_sha256=work.fingerprint,
        batch_id=scope.batch_id,
        request_sha256=scope.request_sha256,
        attempt_id=f"attempt-{index}",
        status="valid",
        result_sha256=text_hash(raw),
        assessed_unit_ids=scope.active_unit_ids,
        active_seconds=1.5,
        input_tokens=100,
        output_tokens=50,
        reasoning_tokens=30,
    )


def replace_registry(work: AssessmentWork, value: dict[str, Any]) -> AssessmentWork:
    documents = tuple(
        document(d.identity, d.kind, value) if d.kind == "registry" else d
        for d in work.context.documents
    )
    return partition_work(work.context.model_copy(update={"documents": documents}), 2)


def test_schema_has_only_required_active_slots_with_no_model_claim_identity(
    work: AssessmentWork,
) -> None:
    scope, _ = attempt(work, json.dumps(response(work)))
    schema = assessment_response_schema(work, scope)
    slots = json.loads(json.dumps(schema))["properties"]["assessments"]
    assert slots["required"] == ["U0", "U1"]
    assert set(slots["properties"]) == {"U0", "U1"} and not slots["additionalProperties"]
    for item in slots["properties"].values():
        assert item["required"] == ["support", "evidence", "reason"]
        assert set(item["properties"]) == set(item["required"])
        assert item["properties"]["evidence"]["items"]["enum"] == [f"S{i}" for i in range(1, 6)]
    assert len(work.context.statements) == 7


def test_successful_binding_flows_into_existing_completion_without_semantic_credit(
    work: AssessmentWork,
) -> None:
    before = work.model_dump_json()
    results = []
    for i in range(len(work.batches)):
        raw = json.dumps(response(work, i), indent=2)
        scope, receipt = attempt(work, raw, i)
        result = bind_assessment_result(work, scope, receipt, raw)
        assert result.receipt.binding == result.binding == "complete"
        assert result.delivery_receipt == receipt
        assert receipt.binding == "unresolved"
        assert result.raw_final == raw
        assert [u.statement for u in result.units] == [
            s for s in work.context.statements if s.unit_id in scope.active_unit_ids
        ]
        assert result.support == result.evidence_adequacy == result.craft == "unassessed"
        assert not result.whole_relation_credit and not result.writer_dispatch_authorized
        results.append(result)
    completion = complete_work(
        work,
        tuple(r.receipt for r in results),
        {r.scope.batch_id: r.scope.request_sha256 for r in results},
    )
    assert completion.complete_delivery and completion.binding == "complete"
    assert completion.delivered_units == 7 and completion.known_output_tokens == 200
    assert completion.support == completion.edit_necessity == "unassessed"
    assert not completion.writer_dispatch_authorized
    assert before == work.model_dump_json()


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "all_context",
        "empty",
        "array",
        "null",
        "bad_label",
        "blank",
        "long",
        "no_evidence",
        "duplicate_ref",
        "unknown_ref",
        "too_many_refs",
        "bad_ref_type",
        "model_quote",
        "model_field",
        "model_offsets",
        "model_unit",
        "authority",
        "extra_root",
    ],
)
def test_reject_wrong_scope_and_malformed_model_output(work: AssessmentWork, mutation: str) -> None:
    value = response(work)
    rows = value["assessments"]
    row = rows["U0"]
    if mutation == "missing":
        rows.pop("U1")
    elif mutation == "all_context":
        for unit in work.context.statements:
            rows[unit.unit_id] = dict(row)
    elif mutation in ("empty", "array", "null"):
        value["assessments"] = {"empty": {}, "array": list(rows.values()), "null": None}[mutation]
    elif mutation == "bad_label":
        row["support"] = "probably"
    elif mutation in ("blank", "long"):
        row["reason"] = " \n " if mutation == "blank" else "x" * 1201
    elif mutation in (
        "no_evidence",
        "duplicate_ref",
        "unknown_ref",
        "too_many_refs",
        "bad_ref_type",
    ):
        row["evidence"] = {
            "no_evidence": [],
            "duplicate_ref": ["S1", "S1"],
            "unknown_ref": ["S999"],
            "too_many_refs": [f"S{i}" for i in range(9)],
            "bad_ref_type": [True],
        }[mutation]
    elif mutation.startswith("model_"):
        row[
            {
                "model_quote": "quote",
                "model_field": "field_id",
                "model_offsets": "start",
                "model_unit": "unit_id",
            }[mutation]
        ] = "invented"
    else:
        value["writer_dispatch_authorized" if mutation == "authority" else "extra"] = True
    raw = json.dumps(value)
    scope, receipt = attempt(work, raw)
    with pytest.raises(ERRORS):
        bind_assessment_result(work, scope, receipt, raw)


@pytest.mark.parametrize(
    "raw",
    [
        '{"assessments":{},"assessments":{}}',
        '{"assessments":{"U0":{},"U0":{}}}',
        '{"assessments":{"U0":{"reason":"a","reason":"b"}}}',
        '{"assessments":NaN}',
        '{"assessments":Infinity}',
        '{"assessments":-Infinity}',
        "[]",
        "",
        "```json\n{}\n```",
        "{} trailing",
        " " * 64001,
    ],
    ids=[
        "duplicate-root",
        "duplicate-slot",
        "duplicate-field",
        "nan",
        "infinity",
        "negative-infinity",
        "array",
        "empty",
        "fenced",
        "trailing",
        "oversized",
    ],
)
def test_raw_json_rejects_duplicates_nonfinite_and_salvage(work: AssessmentWork, raw: str) -> None:
    scope, receipt = attempt(work, raw)
    with pytest.raises(ERRORS):
        bind_assessment_result(work, scope, receipt, raw)


@pytest.mark.parametrize(
    "mutation", ["work", "scope", "batch", "request", "hash", "units", "duplicate_units"]
)
def test_receipt_and_scope_identity_cannot_drift(work: AssessmentWork, mutation: str) -> None:
    raw = json.dumps(response(work))
    scope, receipt = attempt(work, raw)
    if mutation == "scope":
        scope = scope.model_copy(update={"active_unit_ids": ("U0", "U2")})
    else:
        changes: dict[str, Any] = {
            "work": {"work_sha256": "0" * 64},
            "batch": {"batch_id": "batch-002"},
            "request": {"request_sha256": "0" * 64},
            "hash": {"result_sha256": "0" * 64},
            "units": {"assessed_unit_ids": ("U0",)},
            "duplicate_units": {"assessed_unit_ids": ("U0", "U0")},
        }
        receipt = receipt.model_copy(update=changes[mutation])
    with pytest.raises(ERRORS):
        bind_assessment_result(work, scope, receipt, raw)


@pytest.mark.parametrize("status", ["invalid", "length", "refusal", "transport_error", "cancelled"])
def test_valid_looking_failed_final_is_not_salvaged(work: AssessmentWork, status: str) -> None:
    raw = json.dumps(response(work))
    scope, receipt = attempt(work, raw)
    failed = receipt.model_copy(
        update={
            "status": status,
            "result_sha256": None,
            "assessed_unit_ids": (),
            "binding": "unresolved",
        }
    )
    with pytest.raises(ERRORS, match="unsuccessful"):
        bind_assessment_result(work, scope, failed, raw)


@pytest.mark.parametrize(
    "mutation",
    [
        "version",
        "document_digest",
        "field_digest",
        "quote",
        "offset",
        "paragraph",
        "out_of_bounds",
        "field_as_paragraph",
        "paragraph_as_field",
        "wrong_document",
        "report_as_source",
        "unknown_pointer",
        "malformed_pointer",
        "duplicate_ref",
        "registry_contract",
        "registry_extra",
        "unicode_normalization",
    ],
)
def test_registry_binding_rejects_wrong_version_section_and_text(
    work: AssessmentWork, mutation: str
) -> None:
    value = json.loads(next(d.content_json for d in work.context.documents if d.kind == "registry"))
    row = value["entries"][1]
    if mutation == "version":
        row["document_version"] = "v2"
    elif mutation in ("document_digest", "field_digest"):
        row["document_sha256" if mutation == "document_digest" else "field_sha256"] = "0" * 64
    elif mutation == "quote":
        row["quote"] = "changed"
    elif mutation == "offset":
        row["start"] += 1
    elif mutation == "paragraph":
        row["paragraph"] = 3  # Identical text, different occurrence; still reject.
    elif mutation == "out_of_bounds":
        row["paragraph"] = 999
    elif mutation == "field_as_paragraph":
        value["entries"][4]["paragraph"] = 2
    elif mutation == "paragraph_as_field":
        row["paragraph"] = None
    elif mutation in ("wrong_document", "report_as_source"):
        row["document_id"] = "missing" if mutation == "wrong_document" else "review"
    elif mutation in ("unknown_pointer", "malformed_pointer"):
        row["field_pointer"] = "/missing" if mutation == "unknown_pointer" else "/bad~2pointer"
    elif mutation == "duplicate_ref":
        row["ref"] = "S1"
    elif mutation == "registry_contract":
        value["contract"] = "legacy-unknown"
    elif mutation == "registry_extra":
        value["authority"] = True
    else:
        row["quote"] = row["quote"].replace("é", "e\u0301")
    changed = replace_registry(work, value)
    with pytest.raises(ERRORS):
        scope_for_batch(changed, "batch-001", "1" * 64)


@pytest.mark.parametrize("refs", [["S1"], ["S2"], ["S3"], ["S5"], ["S4", "S1"]])
def test_valid_but_wrong_or_incomplete_evidence_never_gains_support(
    work: AssessmentWork, refs: list[str]
) -> None:
    # Date-only omits the comparison; a future plan is not current-event proof.
    # The generic handwriting match cannot prove a private-flourish test.
    value = response(work)
    value["assessments"]["U0"]["evidence"] = refs
    raw = json.dumps(value)
    scope, receipt = attempt(work, raw)
    result = bind_assessment_result(work, scope, receipt, raw)
    assert [e.ref for e in result.units[0].evidence_locations] == refs
    assert result.units[0].model_assessment.support == "supported"
    assert result.support == result.evidence_adequacy == "unassessed"
    assert result.units[1].statement.quote.endswith("private flourish was tested.")
    assert not result.writer_dispatch_authorized


def test_uncertain_without_evidence_and_unknown_usage_remain_explicit(work: AssessmentWork) -> None:
    value = response(work)
    value["assessments"]["U0"].update(support="uncertain", evidence=[])
    raw = json.dumps(value)
    scope, receipt = attempt(work, raw)
    receipt = receipt.model_copy(
        update={"input_tokens": None, "output_tokens": None, "reasoning_tokens": None}
    )
    result = bind_assessment_result(work, scope, receipt, raw)
    assert result.units[0].evidence_locations == ()
    completion = complete_work(
        work, (result.receipt,), {b.batch_id: str(i + 1) * 64 for i, b in enumerate(work.batches)}
    )
    assert not completion.complete_delivery and completion.unknown_usage_attempts == 1
    assert completion.known_output_tokens == 0


def test_renderer_retains_full_context_and_literal_raw_output(work: AssessmentWork) -> None:
    value = response(work)
    value["assessments"]["U0"]["reason"] = (
        '````\n<script>alert("x")</script>\n[link](https://invalid.test)'
    )
    raw = json.dumps(value, ensure_ascii=False, indent=2)
    scope, receipt = attempt(work, raw)
    rendered = render_assessment_result(work, scope, receipt, raw)
    assert "\n`````json\n" in rendered
    payload = json.loads(rendered.split("`````json\n")[1].split("\n`````\n")[0])
    assert payload["full_work"] == work.model_dump(mode="json")
    assert payload["result"]["raw_final"] == raw
    assert payload["result"]["units"][0]["statement"] == work.context.statements[0].model_dump()
    assert payload["result"]["units"][0]["evidence_locations"][0]["quote"] == "Mara reads the date."
    with pytest.raises(ERRORS):
        render_assessment_result(work, scope, receipt, raw + " ")
    with pytest.raises(ERRORS):
        render_assessment_result(
            work.model_copy(update={"context_sha256": "0" * 64}), scope, receipt, raw
        )


def test_reason_total_and_active_slot_limits_are_local_bounds(work: AssessmentWork) -> None:
    full = partition_work(work.context, 7)
    value = response(full)
    for row in value["assessments"].values():
        row["reason"] = "x" * 1200
    raw = json.dumps(value)
    scope, receipt = attempt(full, raw)
    with pytest.raises(ERRORS, match="reason_total"):
        bind_assessment_result(full, scope, receipt, raw)
    with pytest.raises(ValidationError):
        AssessmentScope(
            work_sha256=work.fingerprint,
            batch_id="batch",
            request_sha256="1" * 64,
            active_unit_ids=tuple(f"U{i}" for i in range(13)),
        )


@pytest.mark.parametrize(
    "pointer,expected",
    [
        ("/items/0/a~1b~0c", "escaped field"),
        ("/items/1", "second item"),
    ],
)
def test_nested_source_pointers_resolve_without_normalization(
    work: AssessmentWork, pointer: str, expected: str
) -> None:
    source = document("nested", "source", {"items": [{"a/b~c": "escaped field"}, "second item"]})
    entry = EvidenceLocation(
        ref="N1",
        document_id=source.identity,
        document_version=source.version,
        document_sha256=source.content_sha256,
        field_pointer=pointer,
        field_sha256=text_hash(expected),
        start=0,
        end=len(expected),
        quote=expected,
    )
    registry = document(
        "index", "registry", EvidenceRegistry(entries=(entry,)).model_dump(mode="json")
    )
    documents = tuple(d for d in work.context.documents if d.kind != "registry") + (
        source,
        registry,
    )
    changed = partition_work(work.context.model_copy(update={"documents": documents}), 2)
    value = response(changed)
    for row in value["assessments"].values():
        row["evidence"] = ["N1"]
    raw = json.dumps(value)
    scope, receipt = attempt(changed, raw)
    result = bind_assessment_result(changed, scope, receipt, raw)
    assert result.units[0].evidence_locations[0].quote == expected


@pytest.mark.parametrize(
    "pointer", ["/items/01", "/items/-1", "/items/9", "/items/١", "/items/0/text/more", "/items"]
)
def test_invalid_array_or_nontext_pointer_rejected(work: AssessmentWork, pointer: str) -> None:
    source = document("nested", "source", {"items": [{"text": "value"}]})
    entry = EvidenceLocation(
        ref="N1",
        document_id=source.identity,
        document_version=source.version,
        document_sha256=source.content_sha256,
        field_pointer=pointer,
        field_sha256=text_hash("value"),
        start=0,
        end=5,
        quote="value",
    )
    registry = document(
        "index", "registry", EvidenceRegistry(entries=(entry,)).model_dump(mode="json")
    )
    changed = partition_work(
        work.context.model_copy(
            update={"documents": work.context.documents[:-1] + (source, registry)}
        ),
        2,
    )
    with pytest.raises(ERRORS):
        scope_for_batch(changed, "batch-001", "1" * 64)


@pytest.mark.parametrize(
    "mutation",
    ["missing", "multiple", "stale_source", "unknown_batch", "scope_fingerprint", "context_drift"],
)
def test_scope_revalidates_complete_work_at_every_boundary(
    work: AssessmentWork, mutation: str
) -> None:
    raw = json.dumps(response(work))
    scope, receipt = attempt(work, raw)
    documents = work.context.documents
    if mutation == "missing":
        documents = tuple(d for d in documents if d.kind != "registry")
    elif mutation == "multiple":
        documents += (documents[-1].model_copy(update={"identity": "second-index"}),)
    elif mutation == "stale_source":
        documents = (document("current-draft", "source", {"prose": "changed"}), *documents[1:])
    elif mutation == "unknown_batch":
        scope = scope.model_copy(update={"batch_id": "unknown"})
    elif mutation == "scope_fingerprint":
        scope = scope.model_copy(update={"work_sha256": "0" * 64})
    else:
        work = work.model_copy(
            update={
                "context": work.context.model_copy(
                    update={"messages": (SavedMessage(role="user", content="trimmed"),)}
                )
            }
        )
    if mutation in ("missing", "multiple", "stale_source"):
        work = partition_work(work.context.model_copy(update={"documents": documents}), 2)
    for action in (
        lambda: assessment_response_schema(work, scope),
        lambda: bind_assessment_result(work, scope, receipt, raw),
        lambda: render_assessment_result(work, scope, receipt, raw),
    ):
        with pytest.raises(ERRORS):
            action()


def test_reordered_slot_keys_do_not_change_application_identity(work: AssessmentWork) -> None:
    value = response(work)
    value["assessments"] = dict(reversed(list(value["assessments"].items())))
    raw = json.dumps(value)
    scope, receipt = attempt(work, raw)
    result = bind_assessment_result(work, scope, receipt, raw)
    assert [unit.statement.unit_id for unit in result.units] == ["U0", "U1"]
    assert result.raw_final == raw


def test_binding_snapshots_unchecked_scope_without_retaining_mutable_alias(
    work: AssessmentWork,
) -> None:
    raw = json.dumps(response(work))
    scope, receipt = attempt(work, raw)
    payload = scope.model_dump(mode="json")
    unchecked = AssessmentScope.model_construct(**payload)
    with pytest.warns(UserWarning, match="Pydantic serializer warnings"):
        result = bind_assessment_result(work, unchecked, receipt, raw)
    payload["active_unit_ids"].append("U6")
    assert result.scope == scope
    assert result.scope.active_unit_ids == ("U0", "U1")
