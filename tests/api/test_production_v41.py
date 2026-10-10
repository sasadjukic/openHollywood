"""Explicit repair links preserve original targets without hiding independent findings."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_failure_evidence import capture_review_failure
from open_hollywood_api.services.production_model_executor import (
    _Execution,
    _Operation,
    _output_schema,
    _revision_acceptance_audit,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import critic_repair_tests
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _materialize, _raw, _refs
from tests.api.test_production_v31 import _review
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v40 import _duplicate
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _revision(route: str = "assignment", *, two_originals: bool = False) -> _Execution:
    old = _fixture("She matched the writing. The date was wrong. She still trusted it.")
    draft = next(a for a in old.inputs if a["artifact_kind"] == "scene_draft")
    content = _materialize(_raw(old, route), old)
    if two_originals:
        content["issues"].append(
            {**content["issues"][0], "description": "A separate original defect."}
        )
    review = {
        "artifact_kind": "critique",
        "artifact_key": "critique_scene_1",
        "artifact_version_id": str(uuid4()),
        "content": content,
    }
    new = deepcopy(draft)
    new["artifact_version_id"] = str(uuid4())
    new["content"].update(
        revision_number=1,
        prose="The letters still matched. The date was today. She still trusted it.",
    )
    inputs = tuple(new if a is draft else a for a in old.inputs) + (review, draft)
    return replace(
        old,
        inputs=inputs,
        revision_number=1,
        input_version_ids=tuple(UUID(a["artifact_version_id"]) for a in inputs),
    )


def _linked(execution: _Execution) -> dict[str, Any]:
    raw = _duplicate(execution)
    raw["repair_checks"] = _review(execution, "unmet")["repair_checks"]
    for check in raw["repair_checks"].values():
        check.update(
            current_finding_refs=["boundary", "assignment:outcome"],
            draft_evidence_refs=[_refs(execution)[-1]],
            assessment="The linked current reports repeat this original outcome breach.",
        )
    return raw


def test_linked_different_evidence_keeps_one_original_target_through_next_revision() -> None:
    execution = _revision()
    raw = _linked(execution)
    before = deepcopy((raw, execution.inputs))
    tests = critic_repair_tests(execution.inputs, execution.unit_id)
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and len(result["issues"]) == 1
    issue = result["issues"][0]
    assert issue["description"] == tests[0]["claim"]
    assert issue["recommendation"] == tests[0]["requested_change"]
    assert issue["severity"] == "blocking" and len(issue["evidence"]) == 3
    repeated = {
        "artifact_kind": "critique",
        "artifact_key": "critique_scene_1",
        "artifact_version_id": str(uuid4()),
        "content": result,
    }
    assert critic_repair_tests((*execution.inputs, repeated), execution.unit_id) == tests
    audit = _revision_acceptance_audit(raw, execution)
    assert audit["schema_version"] == "2" and audit["tests"] == tests
    assert audit["candidate_version_id"] != tests[0]["source_draft_version_id"]
    assert audit["linked_current_findings"][0]["finding_refs"] == ["boundary", "assignment:outcome"]
    assert (
        raw["assignment_violations"][0]["explanation"]
        in audit["linked_current_findings"][0]["description"]
    )
    assert "_current_finding_refs" not in json.dumps(result)
    assert (raw, execution.inputs) == before


def test_unlinked_same_category_and_new_blocker_survive_even_with_met_original() -> None:
    execution = _revision()
    raw = _linked(execution)
    check = next(iter(raw["repair_checks"].values()))
    check["current_finding_refs"] = []
    assert len(_materialize(raw, execution)["issues"]) == 2
    check["status"] = "met"
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and len(result["issues"]) == 1


def test_linking_one_finding_does_not_hide_different_evidence_for_same_anchor() -> None:
    execution = _revision()
    raw = _linked(execution)
    raw["assignment_violations"][0]["draft_evidence_refs"] = [_refs(execution)[-1]]
    next(iter(raw["repair_checks"].values()))["current_finding_refs"] = ["assignment:outcome"]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 2
    assert "Current endpoint:" in result["issues"][0]["description"]
    assert (
        result["issues"][1]["description"]
        == critic_repair_tests(execution.inputs, execution.unit_id)[0]["claim"]
    )


@pytest.mark.parametrize("route,ref", [("blocking_craft", "issue:0"), ("pov", "viewpoint")])
def test_explicit_links_cover_craft_and_viewpoint_without_new_canonical_fields(
    route: str, ref: str
) -> None:
    execution = _revision(route)
    raw = _raw(execution, route)
    raw["repair_checks"] = _review(execution, "unmet")["repair_checks"]
    if route == "blocking_craft":
        raw["issues"][0]["repair_test_id"] = next(iter(raw["repair_checks"]))
    else:
        next(iter(raw["repair_checks"].values()))["current_finding_refs"] = [ref]
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 1 and result["verdict"] == "revise"
    assert _revision_acceptance_audit(raw, execution)["linked_current_findings"][0][
        "finding_refs"
    ] == [ref]


@pytest.mark.parametrize(
    "bad", ["category", "severity", "description", "recommendation", "blank", "extra"]
)
def test_linked_craft_finding_is_validated_before_it_can_be_consolidated(bad: str) -> None:
    execution = _revision("blocking_craft")
    raw = _raw(execution, "blocking_craft")
    raw["repair_checks"] = _review(execution, "unmet")["repair_checks"]
    raw["issues"][0]["repair_test_id"] = next(iter(raw["repair_checks"]))
    if bad == "blank":
        raw["issues"][0]["description"] = " "
    elif bad == "extra":
        raw["issues"][0]["unrecognized"] = "must not disappear through linking"
    else:
        raw["issues"][0].pop(bad)
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


@pytest.mark.parametrize(
    "bad",
    [
        "missing",
        "met",
        "unknown",
        "duplicate",
        "partial",
        "category",
        "severity",
        "owner",
        "inactive",
        "bad_evidence",
        "malformed_route",
    ],
)
def test_invalid_links_cannot_remove_or_create_findings(bad: str) -> None:
    execution = _revision(two_originals=bad == "owner")
    raw = _linked(execution)
    check = next(iter(raw["repair_checks"].values()))
    if bad == "missing":
        check.pop("current_finding_refs")
    elif bad == "met":
        check["status"] = "met"
    elif bad == "unknown":
        check["current_finding_refs"] = ["issue:99"]
    elif bad == "duplicate":
        check["current_finding_refs"] = ["boundary", "boundary"]
    elif bad == "partial":
        check["current_finding_refs"] = ["boundary"]
    elif bad in {"category", "severity"}:
        raw["issues"] = _raw(execution, "blocking_craft")["issues"]
        check["current_finding_refs"] = ["issue:0"]
        if bad == "severity":
            review = next(a for a in execution.inputs if a["artifact_kind"] == "critique")
            review["content"]["issues"][0]["category"] = "pacing"
            review["content"]["issues"][0]["severity"] = "major"
    elif bad == "inactive":
        raw["scene_boundary_check"]["status"] = "no_overrun"
    elif bad == "bad_evidence":
        raw["assignment_violations"][0]["draft_evidence_refs"] = ["stale"]
    elif bad == "malformed_route":
        raw["assignment_violations"][0]["explanation"] = " "
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_separate_original_tests_remain_separate_even_with_identical_claims() -> None:
    execution = _revision(two_originals=True)
    review = next(a for a in execution.inputs if a["artifact_kind"] == "critique")
    review["content"]["issues"][1] = deepcopy(review["content"]["issues"][0])
    raw = _review(execution, "unmet")
    assert len(raw["repair_checks"]) == 2
    assert len(_materialize(raw, execution)["issues"]) == 2


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
def test_link_field_is_only_in_repair_schema_and_does_not_expand_initial_reviews(
    deployment: ModelDeployment,
) -> None:
    execution = _revision()
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    schema = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )
    check = schema["$defs"]["RepairAcceptanceCheck"]["anyOf"][1]
    assert "current_finding_refs" in check["required"]
    assert check["properties"]["current_finding_refs"]["maxItems"] == 16
    initial = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=_fixture()
    )
    assert "repair_checks" not in initial["properties"]


def test_audit_redacts_current_feedback_and_failure_capture_retains_links(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v41-only-test-secret-value"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    execution = _revision()
    raw = _linked(execution)
    raw["assignment_violations"][0]["explanation"] = f"Duplicate finding {secret}"
    audit = _revision_acceptance_audit(raw, execution)
    assert secret not in json.dumps(audit)
    assert "[REDACTED" in json.dumps(audit)
    check = next(iter(raw["repair_checks"].values()))
    check["current_finding_refs"] = ["unknown"]
    capture = capture_review_failure(
        operation="critique",
        response_content=json.dumps(raw),
        request_content=json.dumps(_payload(_Operation.CRITIQUE, execution)),
        input_version_ids=tuple(str(v) for v in execution.input_version_ids),
        validation_issues=({"type": "repair_test_links_invalid", "loc": "repair_checks"},),
    )
    assert capture and capture["manuscript_defect_established"] is False
    assert "current_finding_refs" in json.dumps(capture) and secret not in json.dumps(capture)


class LinkedRepairGateway(V26Gateway):
    def __init__(self, *args: Any, invalid_once: bool) -> None:
        super().__init__(*args, mode="linked-repair")
        self.invalid_once = invalid_once
        self.revision_one_reviews = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "critique" or assignment["unit_number"] != 1:
            return response
        raw = json.loads(response.content)
        if assignment["revision_number"] < 2:
            raw["assignment_violations"] = [
                {
                    "anchor": "outcome",
                    "draft_evidence_refs": raw["scene_boundary_check"]["draft_evidence_refs"],
                    "explanation": (
                        f"Simulated outcome breach at revision {assignment['revision_number']}."
                    ),
                    "recommended_resolution": "Restore the original outcome.",
                }
            ]
        if assignment["revision_number"] == 1:
            self.revision_one_reviews += 1
            raw["scene_boundary_check"]["status"] = "overrun"
            for check in raw["repair_checks"].values():
                check.update(
                    status="unmet",
                    current_finding_refs=["boundary", "assignment:outcome"],
                    assessment="The current outcome finding repeats the original repair target.",
                )
                if self.invalid_once and self.revision_one_reviews == 1:
                    check["current_finding_refs"] = ["boundary"]
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("invalid_once", [False, True])
async def test_persisted_links_keep_original_test_across_two_revisions_and_replay(
    invalid_once: bool, migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = LinkedRepairGateway(prompt.prompt, prompt, invalid_once=invalid_once)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3
    payloads = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writers = [p for p in payloads if p.get("assignment", {}).get("operation") == "write"]
    assert len(writers) == 5
    revisions = [p for p in writers if p["assignment"]["revision_number"] > 0]
    first = revisions[0]["revision_contract"]["critic_acceptance_tests"]
    assert len(first) == 1
    assert revisions[1]["revision_contract"]["critic_acceptance_tests"] == first
    assert gateway.revision_one_reviews == (2 if invalid_once else 1)
    with create_session_factory(database_engine)() as session:
        invocations = session.scalars(select(AgentInvocation)).all()
        audited = [i for i in invocations if "revision_acceptance_audit" in i.request_settings]
        assert len(audited) == 2
        assert all(
            i.request_settings["revision_acceptance_audit"]["tests"] == first for i in audited
        )
        carried = next(
            i
            for i in audited
            if i.request_settings["revision_acceptance_audit"]["linked_current_findings"]
        )
        assert len(carried.output_versions[0].content["issues"]) == 1
        assert "current_finding_refs" not in json.dumps(carried.output_versions[0].content)
        failed = [i for i in invocations if i.error_code]
        assert len(failed) == int(invalid_once)
        assert all(not i.output_versions for i in failed)
