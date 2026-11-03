"""Authored fixtures for exact selection, full context and non-semantic completion."""

import json
from typing import Any

import pytest
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
    render_work,
)
from open_hollywood_engine.evaluations.review_evidence import (
    EvidenceError,
    SavedMessage,
    text_hash,
)
from pydantic import ValidationError


def document(identity: str, kind: Any, value: dict[str, Any]) -> ContextDocument:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return ContextDocument(
        identity=identity,
        version="version-1",
        kind=kind,
        content_json=content,
        content_sha256=text_hash(content),
    )


@pytest.fixture
def context() -> AssessmentContext:
    report = {
        "claims": [
            "The plan requires Nia to remain outside.",
            "Nia enters, violating that boundary.",
            "The handwriting match proves the private flourish was tested.",
            "The next scene starts inside.",
            "A date is noticed ten years ahead.",
        ]
    }
    source = {
        "prose": "Nia matches the general handwriting, notices the future date, then enters.",
        "next_plan": (
            "Nia crosses the threshold during the next scene and later tests a private flourish."
        ),
        "source_scope": "A plan is available; a future draft is not.",
    }
    fields = tuple(
        ReportField(field_id=f"F{i}", pointer=f"/claims/{i}", text=v)
        for i, v in enumerate(report["claims"])
    )
    return AssessmentContext(
        provenance="synthetic_fixture",
        origin_sha256="1" * 64,
        documents=(
            document("draft", "source", source),
            document("review", "report", report),
            document("scope", "scope", {"availability": "complete supplied documents"}),
        ),
        report_fields=fields,
        statements=tuple(
            SelectedStatement(
                unit_id=f"U{i}", field_id=f.field_id, start=0, end=len(f.text), quote=f.text
            )
            for i, f in enumerate(fields)
        ),
        declared_links=(
            DeclaredLink(link_id="boundary", unit_ids=("U0", "U1"), origin="authored_diagnostic"),
        ),
        messages=(
            SavedMessage(
                role="user", content=json.dumps({"full_sources": source, "full_report": report})
            ),
        ),
    )


def receipt(work: AssessmentWork, index: int = 0, **changes: Any) -> AssessmentReceipt:
    batch = work.batches[index]
    return AssessmentReceipt(
        **{
            "work_sha256": work.fingerprint,
            "batch_id": batch.batch_id,
            "attempt_id": f"attempt-{index}",
            "request_sha256": "2" * 64,
            "status": "valid",
            "result_sha256": "3" * 64,
            "assessed_unit_ids": batch.unit_ids,
            "binding": "complete",
            "input_tokens": 100,
            "output_tokens": 50,
            "reasoning_tokens": 30,
            "active_seconds": 1.5,
            **changes,
        }
    )


def manifest(work: AssessmentWork) -> dict[str, str]:
    return {b.batch_id: "2" * 64 for b in work.batches}


@pytest.mark.parametrize(
    "maximum,expected",
    [
        (2, (("U0", "U1"), ("U2", "U3"), ("U4",))),
        (3, (("U0", "U1", "U2"), ("U3", "U4"))),
        (5, (("U0", "U1", "U2", "U3", "U4"),)),
    ],
)
def test_full_context_and_whole_claims_retained(
    context: AssessmentContext, maximum: int, expected: tuple[tuple[str, ...], ...]
) -> None:
    work = partition_work(context, maximum)
    assert tuple(b.unit_ids for b in work.batches) == expected
    assert work.context == context
    assert AssessmentWork.model_validate_json(work.model_dump_json()) == work
    assert work.support == work.edit_necessity == work.craft == "unassessed"
    assert not work.writer_dispatch_authorized


def test_transitive_links_cannot_be_cut(context: AssessmentContext) -> None:
    extended = context.model_copy(
        update={
            "declared_links": context.declared_links
            + (
                DeclaredLink(
                    link_id="another", unit_ids=("U1", "U2"), origin="authored_diagnostic"
                ),
            )
        }
    )
    with pytest.raises(EvidenceError, match="linked_group"):
        partition_work(extended, 2)
    assert partition_work(extended, 3).batches[0].unit_ids == ("U0", "U1", "U2")


@pytest.mark.parametrize("limit", [0, -1, True, 1])
def test_invalid_or_relation_severing_limit(context: AssessmentContext, limit: int) -> None:
    with pytest.raises(EvidenceError):
        partition_work(context, limit)


@pytest.mark.parametrize(
    "mutation",
    [
        "source",
        "message",
        "quote",
        "pointer",
        "missing",
        "duplicate",
        "split",
        "authority",
        "provenance",
    ],
)
def test_reject_context_and_work_mutations(context: AssessmentContext, mutation: str) -> None:
    value = partition_work(context, 3).model_dump(mode="json")
    c = value["context"]
    if mutation == "source":
        c["documents"][0]["content_json"] = "{}"
    elif mutation == "message":
        c["messages"][0]["content"] = "trimmed"
    elif mutation == "quote":
        c["statements"][0]["quote"] = "changed"
    elif mutation == "pointer":
        c["report_fields"][0]["pointer"] = "/claims/1"
    elif mutation == "missing":
        value["batches"][0]["unit_ids"].pop()
    elif mutation == "duplicate":
        value["batches"].append(value["batches"][0])
    elif mutation == "split":
        value["batches"][0]["unit_ids"], value["batches"][1]["unit_ids"] = (
            ["U0", "U2"],
            ["U1", "U3", "U4"],
        )
    elif mutation == "authority":
        value["writer_dispatch_authorized"] = True
    else:
        c["provenance"] = "ordinary_production"
    with pytest.raises((EvidenceError, ValidationError)):
        AssessmentWork.model_validate_json(json.dumps(value))


def test_complete_delivery_and_binding_never_grant_semantic_truth(
    context: AssessmentContext,
) -> None:
    work = partition_work(context, 3)
    result = complete_work(work, tuple(receipt(work, i) for i in range(2)), manifest(work))
    assert result.complete_delivery and result.binding == "complete"
    assert result.delivered_units == 5
    assert result.known_input_tokens == 200 and result.known_output_tokens == 100
    assert result.support == result.craft == result.edit_necessity == "unassessed"
    assert not result.writer_dispatch_authorized and not result.whole_relation_credit
    # The fixture includes false flourish/timing claims; completion cannot judge them.
    assert len(work.context.statements) == 5


@pytest.mark.parametrize("status", ["invalid", "length", "refusal", "transport_error", "cancelled"])
def test_failure_keeps_usage_and_prevents_case_completion(
    context: AssessmentContext, status: str
) -> None:
    work = partition_work(context, 3)
    failed = receipt(
        work,
        1,
        status=status,
        result_sha256=None,
        assessed_unit_ids=(),
        binding="unresolved",
        input_tokens=None,
        output_tokens=None,
        reasoning_tokens=None,
    )
    result = complete_work(work, (receipt(work), failed), manifest(work))
    assert not result.complete_delivery and result.binding == "unresolved"
    assert result.delivered_units == 3 and result.unknown_usage_attempts == 1
    assert result.known_output_tokens == 50 and result.total_active_seconds == 3


@pytest.mark.parametrize(
    "bad", ["duplicate", "attempt", "scope", "request", "unknown", "unit", "manifest"]
)
def test_completion_rejects_bad_receipts(context: AssessmentContext, bad: str) -> None:
    work = partition_work(context, 3)
    a, b = receipt(work), receipt(work, 1)
    expected = manifest(work)
    if bad == "duplicate":
        b = a
    elif bad == "attempt":
        b = b.model_copy(update={"attempt_id": a.attempt_id})
    elif bad == "scope":
        b = b.model_copy(update={"work_sha256": "4" * 64})
    elif bad == "request":
        b = b.model_copy(update={"request_sha256": "4" * 64})
    elif bad == "unknown":
        b = b.model_copy(update={"batch_id": "unknown"})
    elif bad == "unit":
        b = b.model_copy(update={"assessed_unit_ids": ("U3",)})
    else:
        expected.pop(b.batch_id)
    with pytest.raises(EvidenceError):
        complete_work(work, (a, b), expected)


def test_absence_and_unresolved_binding_are_explicit(context: AssessmentContext) -> None:
    work = partition_work(context, 3)
    assert not complete_work(work, (), manifest(work)).complete_delivery
    assert not complete_work(work, (receipt(work),), manifest(work)).complete_delivery
    result = complete_work(
        work, (receipt(work), receipt(work, 1, binding="unresolved")), manifest(work)
    )
    assert result.complete_delivery and result.binding == "unresolved"


@pytest.mark.parametrize("mutation", ["credit", "reasoning", "bool_usage", "negative_time", "nan"])
def test_invalid_terminal_records(context: AssessmentContext, mutation: str) -> None:
    changes: dict[str, Any] = {
        "credit": {"status": "length"},
        "reasoning": {"reasoning_tokens": 51},
        "bool_usage": {"input_tokens": True},
        "negative_time": {"active_seconds": -1.0},
        "nan": {"active_seconds": float("nan")},
    }
    with pytest.raises((EvidenceError, ValidationError)):
        receipt(partition_work(context, 3), **changes[mutation])


def test_repeated_text_uses_explicit_offsets_without_normalization() -> None:
    source = document("review", "report", {"text": "é x é"})
    c = AssessmentContext(
        provenance="synthetic_fixture",
        origin_sha256="1" * 64,
        documents=(
            source,
            document("draft", "source", {"text": "complete"}),
            document("scope", "scope", {}),
        ),
        report_fields=(ReportField(field_id="F", pointer="/text", text="é x é"),),
        statements=(SelectedStatement(unit_id="U", field_id="F", start=4, end=5, quote="é"),),
        messages=(SavedMessage(role="user", content="full context"),),
    )
    assert partition_work(c, 1).context.statements[0].start == 4
    with pytest.raises((EvidenceError, ValidationError)):
        partition_work(
            c.model_copy(
                update={"statements": (c.statements[0].model_copy(update={"quote": "e\u0301"}),)}
            ),
            1,
        )


def test_renderer_is_literal_and_revalidates(context: AssessmentContext) -> None:
    c = context.model_copy(
        update={"messages": (SavedMessage(role="user", content="```\n<script>do()</script>\n```"),)}
    )
    work = partition_work(c, 3)
    rendered = render_work(work)
    assert "\n````json\n" in rendered and "<script>" in rendered
    assert (
        "unassessed" in rendered
        and c.messages[0].content
        in json.loads(rendered.split("````json\n")[1].split("\n````")[0])["context"]["messages"][0][
            "content"
        ]
    )
    with pytest.raises((EvidenceError, ValidationError)):
        render_work(work.model_copy(update={"context_sha256": "0" * 64}))
