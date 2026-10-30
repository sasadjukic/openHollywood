"""Exactness and provenance do not establish assignment fulfillment or story quality."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Literal
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.services.production_model_executor import _draft_evidence_catalog
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    ArtifactSource,
    ArtifactView,
    EvidenceError,
    NativeAssignmentCheck,
    ReviewSnapshot,
    SavedMessage,
    catalog_v61,
    compare_spans,
    messages_hash,
    project_review,
    recover_messages,
    resolve_span,
    strict_object,
)
from pydantic import ValidationError

from tests.review_evidence_fixtures import review_snapshot


def updated(body: dict[str, Any]) -> ReviewSnapshot:
    messages = tuple(SavedMessage.model_validate(m) for m in body["messages"])
    body["invocation"]["prompt_sha256"] = messages_hash(messages)
    return ReviewSnapshot.model_validate_json(json.dumps(body))


@pytest.mark.parametrize(
    "condition", ["unique", "duplicate", "multiple", "recovered", "unavailable", "conflict"]
)
@pytest.mark.parametrize("status", ["met", "unmet"])
def test_twelve_source_conditions(condition: str, status: Literal["met", "unmet"]) -> None:
    snapshot = review_snapshot(revision=condition in ("recovered", "unavailable"), status=status)
    body = snapshot.model_dump(mode="json")
    payload = json.loads(body["messages"][1]["content"])
    draft_view = next(
        v
        for v in payload["input_artifacts"]
        if v["artifact_version_id"] == snapshot.draft_version_id
    )
    refs = [v["evidence_ref"] for v in draft_view["content"]["evidence_catalog"]]
    check = body["native_audit"]["assignment_checks"]["outcome"]
    if condition == "duplicate":
        check["draft_evidence_refs"] = [refs[-1]]
    elif condition == "multiple":
        check["draft_evidence_refs"] = refs[:2]
    elif condition == "conflict":
        payload["scene_assignment_contract"]["outcome"] = payload["scene_assignment_contract"][
            "turning_point"
        ]
        body["messages"][1]["content"] = json.dumps(payload)
    snapshot = updated(body)
    if condition == "conflict":
        with pytest.raises(EvidenceError):
            project_review(snapshot)
        return
    before = snapshot.model_dump_json()
    evidence = next(e for e in project_review(snapshot) if e.anchor == "outcome")
    assert evidence.original_check.status == status
    assert evidence.aggregate_equality is None
    assert snapshot.model_dump_json() == before
    if condition in ("unique", "duplicate", "multiple"):
        assert [c.status for c in evidence.comparisons] == (
            ["exact", "different"] if condition == "multiple" else ["exact"]
        )
        if condition == "duplicate":
            assert evidence.comparisons[0].right.start == 53
        return
    old = next(
        s
        for s in snapshot.sources
        if s.artifact_kind == "scene_draft" and s.version_id != snapshot.draft_version_id
    )
    assert old.content is not None
    handle = catalog_v61(str(old.content["prose"]), old.version_id)[0].evidence_ref
    view = ArtifactView.model_validate_json(
        json.dumps(
            next(
                v for v in payload["input_artifacts"] if v["artifact_version_id"] == old.version_id
            )
        )
    )
    if condition == "unavailable":
        old = old.model_copy(update={"content": None})
    left = resolve_span(
        old,
        view,
        scene_id=snapshot.scene_id,
        current_revision=1,
        field="/prose",
        evidence_ref=handle,
        current=False,
    )
    comparison = compare_spans(left, evidence.comparisons[0].right)
    assert comparison.status == ("unavailable" if condition == "unavailable" else "different")
    assert left.visibility == (
        "unavailable" if condition == "unavailable" else "recovered_after_review"
    )


def test_judgment_is_independent_and_json_replay_is_exact() -> None:
    snapshot = review_snapshot()
    before = project_review(snapshot)
    body = snapshot.model_dump(mode="json")
    for check in body["native_audit"]["assignment_checks"].values():
        check.update(status="unmet", recommended_resolution="Authored advice.")
    after = project_review(updated(body))
    assert [e.comparisons for e in before] == [e.comparisons for e in after]
    assert before[0].original_check != after[0].original_check
    roundtrip = ReviewSnapshot.model_validate_json(
        json.dumps(snapshot.model_dump(mode="json"), sort_keys=True)
    )
    assert project_review(roundtrip) == before


@pytest.mark.parametrize(
    "prose",
    [
        "One. Two! Three?",
        "Same. Same.",
        "  Café.\n\n Cafe\u0301.  ",
        'She said, "Wait."\n\nThen… silence.',
        "Unpunctuated text\nwith a line break",
    ],
)
def test_pinned_catalog_matches_unchanged_production(prose: str) -> None:
    version = str(uuid4())
    expected = [
        {**r, "evidence_ref": r["evidence_ref"] + "_" + UUID(version).hex}
        for r in _draft_evidence_catalog(prose)
    ]
    assert [r.model_dump(mode="json") for r in catalog_v61(prose, version)] == expected


@pytest.mark.parametrize(
    "bad",
    [
        "project",
        "scene",
        "draft",
        "plan",
        "hash",
        "catalog",
        "coverage",
        "handle",
        "duplicate_handle",
        "quote_only",
        "view_id",
        "missing_source",
        "critique_target",
        "input_key",
        "catalog_order",
    ],
)
def test_conflicting_bindings_do_not_produce_partial_evidence(bad: str) -> None:
    body = review_snapshot().model_dump(mode="json")
    audit = body["native_audit"]
    if bad == "project":
        body["invocation"]["project_id"] = str(uuid4())
    elif bad == "scene":
        body["scene_id"] = "scene_2"
    elif bad in ("draft", "plan"):
        audit["candidate_version_id" if bad == "draft" else "current_plan_version_id"] = str(
            uuid4()
        )
    elif bad == "hash":
        body["sources"][0]["content_sha256"] = "0" * 64
    elif bad == "coverage":
        del audit["assignment_checks"]["outcome"]
    elif bad in ("handle", "duplicate_handle", "quote_only"):
        refs = audit["assignment_checks"]["outcome"]["draft_evidence_refs"]
        audit["assignment_checks"]["outcome"]["draft_evidence_refs"] = (
            refs * 2
            if bad == "duplicate_handle"
            else ["Mira waits." if bad == "quote_only" else "stale"]
        )
    elif bad == "missing_source":
        body["sources"].pop()
    elif bad == "critique_target":
        body["critique"]["content"]["target_artifact_version_id"] = str(uuid4())
        body["critique"]["content_sha256"] = canonical_sha256(body["critique"]["content"])
    elif bad == "input_key":
        body["sources"][0]["artifact_key"] = "scene_plan_scene_2"
    else:
        payload = json.loads(body["messages"][1]["content"])
        draft = next(
            v
            for v in payload["input_artifacts"]
            if v["artifact_version_id"] == body["draft_version_id"]
        )
        if bad == "view_id":
            draft["artifact_version_id"] = str(uuid4())
        elif bad == "catalog_order":
            draft["content"]["evidence_catalog"].reverse()
        else:
            draft["content"]["evidence_catalog"].pop()
        body["messages"][1]["content"] = json.dumps(payload)
    with pytest.raises((EvidenceError, ValidationError)):
        project_review(updated(body))


@pytest.mark.parametrize("bad", ["missing", "hash", "truncated", "roles"])
def test_message_recovery_rejects_unsupported_or_changed_bytes(bad: str) -> None:
    messages = (
        SavedMessage(role="system", content="Rules\n\nMore rules"),
        SavedMessage(role="user", content='{"prose":"A\\n\\nB"}'),
    )
    text = "\n\n".join(m.content for m in messages)
    assert recover_messages(text, messages_hash(messages)) == messages
    digest = (
        "0" * 64 if bad == "hash" else messages_hash(messages[::-1] if bad == "roles" else messages)
    )
    with pytest.raises(EvidenceError, match="unavailable_view"):
        recover_messages(
            None if bad == "missing" else text[:-1] if bad == "truncated" else text, digest
        )


@pytest.mark.parametrize("text", ['{"x":1,"x":2}', '{"x":NaN}', "[1,2]"])
def test_duplicate_keys_and_non_objects_are_rejected(text: str) -> None:
    with pytest.raises(EvidenceError):
        strict_object(text)


@pytest.mark.parametrize("bad", ["scene", "revision", "key"])
def test_unavailable_historical_body_still_needs_surviving_lineage(bad: str) -> None:
    snapshot = review_snapshot(revision=True)
    old = next(
        s
        for s in snapshot.sources
        if s.artifact_kind == "scene_draft" and s.version_id != snapshot.draft_version_id
    )
    assert old.content is not None
    ref = catalog_v61(str(old.content["prose"]), old.version_id)[0].evidence_ref
    payload = json.loads(snapshot.messages[1].content)
    view = next(v for v in payload["input_artifacts"] if v["artifact_version_id"] == old.version_id)
    source = old.model_dump(mode="json")
    source["content"] = None
    if bad == "scene":
        view["content"]["scene_id"] = "scene_2"
    elif bad == "revision":
        view["content"]["revision_number"] = 99
    else:
        source["artifact_key"] = view["artifact_key"] = "scene_draft_scene_2"
    with pytest.raises(EvidenceError):
        resolve_span(
            ArtifactSource.model_validate_json(json.dumps(source)),
            ArtifactView.model_validate_json(json.dumps(view)),
            scene_id=snapshot.scene_id,
            current_revision=1,
            field="/prose",
            evidence_ref=ref,
            current=False,
        )


def test_exact_rule_does_not_normalize_unicode_or_whitespace() -> None:
    base = project_review(review_snapshot())[1].comparisons[0].right
    for a, b in (("Café", "Cafe\u0301"), ("Wait.", "Wait. "), ("Yes", "yes")):
        left = base.model_copy(update={"quote": a, "start": 0, "end": len(a)})
        right = base.model_copy(update={"quote": b, "start": 0, "end": len(b)})
        assert compare_spans(left, right).status == "different"


def test_native_contract_keeps_one_to_three_distinct_handles() -> None:
    body = deepcopy(project_review(review_snapshot())[0].original_check.model_dump(mode="json"))
    body["draft_evidence_refs"] *= 4
    with pytest.raises(ValidationError):
        NativeAssignmentCheck.model_validate_json(json.dumps(body))


def test_view_hash_preserves_absent_fields_and_assignment_surface() -> None:
    snapshot = review_snapshot()
    payload = json.loads(snapshot.messages[1].content)
    views = {v["artifact_version_id"]: v for v in payload["input_artifacts"]}
    for requirement in project_review(snapshot):
        assert requirement.assignment_contract_sha256 == canonical_sha256(
            payload["scene_assignment_contract"]
        )
        for comparison in requirement.comparisons:
            for span in (comparison.left, comparison.right):
                assert span.rendered_view_sha256 == canonical_sha256(views[span.version_id])
