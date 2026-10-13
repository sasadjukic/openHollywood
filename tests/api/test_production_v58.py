"""Single-source repair rendering. Simulated citations do not prove semantic support."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_critic_obligations import OBLIGATION_RULE
from open_hollywood_api.services.production_failure_evidence import capture_review_failure
from open_hollywood_api.services.production_model_executor import (
    _critic_repair_sources,
    _Execution,
    _materialize_output_data,
    _Operation,
    _output_schema,
    _scene_boundary_audit,
    _structured_failure_issues,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_repair_conditions import (
    condition_obligation_rule,
    render_assignment_repairs,
    repair_source_catalog,
)
from open_hollywood_engine.artifacts import Critique
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.api.test_production_v29 import _raw, _refs
from tests.api.test_production_v31 import _review
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v41 import _revision
from tests.api.test_production_v45 import _claim
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _materialize(raw: dict[str, Any], execution: _Execution) -> dict[str, Any]:
    """Exercise actual wire validation, without the historical-fixture adapter."""
    draft = next(a for a in execution.inputs if a["artifact_kind"] == "scene_draft")
    task = SimpleNamespace(
        draft=SimpleNamespace(
            artifact_key=draft["artifact_key"], version_id=UUID(draft["artifact_version_id"])
        )
    )
    result = _materialize_output_data(_Operation.CRITIQUE, task, execution, raw)
    Critique.model_validate(result)
    return result


def _record(execution: _Execution, ref: str, *conditions: str) -> dict[str, Any]:
    source = next(
        s for s in _critic_repair_sources(execution) if s["source_path"] == "/content/outcome"
    )
    return {
        "repair_ref": ref,
        "conditions": [
            {
                "condition": text,
                "source_refs": [
                    {"source_ref": source["source_ref"], "exact_quote": source["text"]}
                ],
                "support_assessment": "Simulated support assessment for routing tests only.",
            }
            for text in conditions
        ],
    }


def _wire(execution: _Execution, *, unmet: bool = True) -> dict[str, Any]:
    raw = _raw(execution)
    raw["assignment_repair_conditions"] = []
    if unmet:
        raw["assignment_checks"]["outcome"]["status"] = "unmet"
        raw["assignment_repair_conditions"] = [
            _record(execution, "assignment:outcome", "Establish her decision to verify.")
        ]
    return raw


@pytest.mark.parametrize("deployment", list(ModelDeployment))
@pytest.mark.parametrize("revision", [0, 1])
def test_wire_schema_and_instructions_keep_met_semantics(
    deployment: ModelDeployment, revision: int
) -> None:
    execution = _fixture()
    execution = replace(
        execution,
        selection=replace(execution.selection, deployment=deployment),
        revision_number=revision,
    )
    schema = _output_schema(
        _Operation.CRITIQUE, continuity_schema_variant=None, critic_execution=execution
    )
    assert "assignment_repair_conditions" in schema["required"]
    for check in schema["properties"]["assignment_checks"]["properties"].values():
        assert all(
            v["properties"]["recommended_resolution"] == {"type": "null"} for v in check["anyOf"]
        )
    props = schema["$defs"]["CritiqueIssue"]["properties"]
    assert props["recommendation"]["anyOf"][0] == {"type": "null"}
    payload = _payload(_Operation.CRITIQUE, execution)
    assert payload["repair_source_catalog"] == _critic_repair_sources(execution)
    # Only the wire-field sentence changes, not the complete fact/evidence definition.
    marker = "In assessment, compare the complete assigned fact"
    assert (
        condition_obligation_rule(OBLIGATION_RULE).split(marker)[1]
        == OBLIGATION_RULE.split(marker)[1]
    )


def test_multiple_conditions_render_losslessly_into_canonical_advice_and_audit() -> None:
    execution = _fixture()
    raw = _wire(execution)
    raw["assignment_repair_conditions"] = [
        _record(
            execution,
            "assignment:outcome",
            "Establish her decision.",
            "Leave the result unverified.",
        )
    ]
    before = deepcopy((raw, execution.inputs))
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise"
    assert (
        result["issues"][0]["recommendation"]
        == "Establish her decision. Leave the result unverified."
    )
    assert result["issues"][0]["severity"] == "blocking"
    assert "assignment_repair_conditions" not in result
    audit = cast(dict[str, Any], _scene_boundary_audit(raw, execution))
    assert audit["schema_version"] == "7"
    assert audit["repair_advice_origin"] == "shared_finding_conditions"
    entry = audit["assignment_repair_conditions"][0]
    assert entry["rendered_recommendation"] == result["issues"][0]["recommendation"]
    assert (
        entry["conditions"][0]["source_refs"][0]["artifact_version_id"]
        == execution.inputs[0]["artifact_version_id"]
    )
    assert (raw, execution.inputs) == before


@pytest.mark.parametrize(
    "bad",
    [
        "omitted_array",
        "missing_record",
        "extra_record",
        "duplicate_record",
        "met_record",
        "nonnull_identical",
        "nonnull_conflicting",
        "missing_null",
        "empty_conditions",
        "too_many",
        "blank_condition",
        "long_condition",
        "long_joined",
        "blank_support",
        "unknown_source",
        "nonexact_quote",
        "blank_quote",
        "missing_quote",
        "duplicate_citation",
        "no_sources",
        "extra_condition_field",
        "extra_record_field",
        "malformed_record",
        "source_object",
    ],
)
def test_bad_condition_contract_never_creates_a_manuscript_finding(bad: str) -> None:
    execution = _fixture()
    raw = _wire(execution)
    records = raw["assignment_repair_conditions"]
    condition = records[0]["conditions"][0]
    citation = condition["source_refs"][0]
    check = raw["assignment_checks"]["outcome"]
    if bad == "omitted_array":
        del raw["assignment_repair_conditions"]
    elif bad == "missing_record":
        records.clear()
    elif bad == "extra_record":
        records.append(_record(execution, "issue:17", "Invented route."))
    elif bad == "duplicate_record":
        records.append(deepcopy(records[0]))
    elif bad == "met_record":
        check["status"] = "met"
    elif bad == "nonnull_identical":
        check["recommended_resolution"] = condition["condition"]
    elif bad == "nonnull_conflicting":
        check["recommended_resolution"] = "Enter immediately because of the touch."
    elif bad == "missing_null":
        del check["recommended_resolution"]
    elif bad == "empty_conditions":
        records[0]["conditions"] = []
    elif bad == "too_many":
        records[0]["conditions"] *= 9
    elif bad == "blank_condition":
        condition["condition"] = " "
    elif bad == "long_condition":
        condition["condition"] = "x" * 601
    elif bad == "long_joined":
        condition["condition"] = "x" * 300
        records[0]["conditions"].append(deepcopy(condition))
    elif bad == "blank_support":
        condition["support_assessment"] = " "
    elif bad == "unknown_source":
        citation["source_ref"] = "repair_source_stale"
    elif bad == "nonexact_quote":
        citation["exact_quote"] += " invented"
    elif bad == "blank_quote":
        citation["exact_quote"] = " "
    elif bad == "missing_quote":
        del citation["exact_quote"]
    elif bad == "duplicate_citation":
        condition["source_refs"] *= 2
    elif bad == "no_sources":
        condition["source_refs"] = []
    elif bad == "extra_condition_field":
        condition["free_advice"] = "Enter now."
    elif bad == "extra_record_field":
        records[0]["recommendation"] = "Enter now."
    elif bad == "malformed_record":
        records[0] = None
    elif bad == "source_object":
        citation["source_ref"] = {"id": "invalid"}
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    assert (
        _structured_failure_issues(failure.value)[0]["type"]
        == "invalid_assignment_repair_conditions"
    )


@pytest.mark.parametrize("severity", ["note", "minor", "major", "blocking"])
def test_consolidated_additions_come_only_from_the_shared_conditions(severity: str) -> None:
    execution = _fixture()
    raw = _wire(execution)
    claim = _claim(execution, repeated=True, severity=severity)
    claim["recommendation"] = None
    raw["issues"] = [claim]
    raw["assignment_repair_conditions"][0]["conditions"].extend(
        _record(execution, "assignment:outcome", "Leave verification inconclusive.")["conditions"]
    )
    result = _materialize(raw, execution)
    assert len(result["issues"]) == 1
    advice = result["issues"][0]["recommendation"]
    for entry in raw["assignment_repair_conditions"]:
        assert entry["conditions"][0]["condition"] in advice
    assert (
        cast(dict[str, Any], _scene_boundary_audit(raw, execution))["assignment_restatements"][0][
            "recommendation"
        ]
        == advice
    )
    raw["issues"][0]["recommendation"] = "Unchecked separate advice."
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_optional_craft_and_met_checks_do_not_acquire_conditions_or_force_revision() -> None:
    execution = _fixture()
    raw = _wire(execution, unmet=False)
    raw["issues"] = _raw(execution, "craft")["issues"]
    result = _materialize(raw, execution)
    assert result["verdict"] == "pass"
    assert result["issues"][0]["recommendation"] == raw["issues"][0]["recommendation"]
    raw["assignment_repair_conditions"] = [_record(execution, "issue:0", "Mandatory polish.")]
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


@pytest.mark.parametrize("route", ["viewpoint", "assignment:scene_id"])
def test_other_native_routes_are_rendered_before_existing_validation(route: str) -> None:
    execution = _fixture()
    raw = _wire(execution, unmet=False)
    if route == "viewpoint":
        raw["point_of_view_check"] = _raw(execution, "pov")["point_of_view_check"]
        raw["point_of_view_check"]["recommended_resolution"] = None
    else:
        raw["assignment_violations"] = [
            {
                "anchor": "scene_id",
                "explanation": "The assigned exit state is absent.",
                "draft_evidence_refs": _refs(execution)[:1],
                "recommended_resolution": None,
            }
        ]
    raw["assignment_repair_conditions"] = [_record(execution, route, "Restore the assigned state.")]
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise"
    assert result["issues"][0]["recommendation"] == "Restore the assigned state."


def test_boundary_policy_is_application_authored_and_reused_by_restatements() -> None:
    execution = _fixture()
    raw = _wire(execution, unmet=False)
    raw["scene_boundary_check"]["status"] = "overrun"
    result = _materialize(raw, execution)
    assert "remove unassigned material advancement" in result["issues"][0]["recommendation"]
    claim = _claim(execution, repeated=True)
    claim.update(assignment_finding_ref="boundary", recommendation=None)
    claim["assignment_comparison"]["finding_refs"] = ["boundary"]
    raw["issues"] = [claim]
    assert (
        _materialize(raw, execution)["issues"][0]["recommendation"]
        == result["issues"][0]["recommendation"]
    )
    raw["assignment_repair_conditions"] = [_record(execution, "issue:0", "Preserve uncertainty.")]
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, execution)


def test_traceable_but_unsupported_condition_is_not_falsely_certified_by_validation() -> None:
    execution = _fixture()
    raw = _wire(execution)
    invented = "Require the letter to cause immediate completed verification."
    raw["assignment_repair_conditions"] = [_record(execution, "assignment:outcome", invented)]
    # Exact current citation is real, but it does not require this cause/completion.
    result = _materialize(raw, execution)
    assert result["issues"][0]["recommendation"] == invented


def test_source_catalog_preserves_original_paths_versions_and_visible_content() -> None:
    original: dict[str, Any] = {
        "artifact_kind": "story_bible",
        "artifact_version_id": "version1",
        "content": {
            "established_facts": [
                {"id": "hidden", "text": "Hidden fact."},
                {"id": "visible", "text": "Visible fact.", "detail/a~b": "Escaped path."},
            ]
        },
    }
    shown = deepcopy(original)
    shown["content"]["established_facts"].pop(0)
    sources = repair_source_catalog([original], [shown])
    assert {s["source_path"] for s in sources} == {
        "/content/established_facts/1/text",
        "/content/established_facts/1/detail~1a~0b",
    }
    assert all(s["artifact_version_id"] == "version1" for s in sources)
    old_ids = {s["source_ref"] for s in sources}
    original["artifact_version_id"] = shown["artifact_version_id"] = "version2"
    assert old_ids.isdisjoint(s["source_ref"] for s in repair_source_catalog([original], [shown]))
    execution = _fixture()
    assert not {"scene_draft", "critique"} & {
        s["artifact_kind"] for s in _critic_repair_sources(execution)
    }


def test_condition_retry_gives_shape_and_current_sources_without_rejected_advice() -> None:
    execution = _fixture()
    raw = _wire(execution)
    raw["assignment_checks"]["outcome"]["recommended_resolution"] = "SENTINEL unchecked advice."
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    retry = replace(
        execution,
        attempt_number=2,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(_structured_failure_issues(failure.value)),
        },
    )
    packet = _payload(_Operation.CRITIQUE, retry)
    serialized = json.dumps(packet)
    assert "SENTINEL" not in serialized
    assert "support_assessment" in serialized and "exact_quote" in serialized
    assert packet["repair_source_catalog"] == _critic_repair_sources(execution)
    raw["assignment_checks"]["outcome"]["recommended_resolution"] = None
    assert _materialize(raw, retry)["verdict"] == "revise"


def test_rendering_does_not_mutate_model_output() -> None:
    execution = _fixture()
    raw = _wire(execution)
    before = deepcopy(raw)
    rendered = render_assignment_repairs(raw, _critic_repair_sources(execution))
    assert raw == before and "assignment_repair_conditions" not in rendered
    assert rendered["assignment_checks"]["outcome"]["recommended_resolution"] is not None


def test_immutable_historical_repairs_are_not_reauthored_by_current_conditions() -> None:
    execution = _revision()
    raw = _review(execution, "unmet")
    raw["assignment_repair_conditions"] = []
    before = deepcopy(execution.inputs)
    result = _materialize(raw, execution)
    assert result["verdict"] == "revise" and result["issues"]
    assert execution.inputs == before


def test_condition_audit_and_failed_capture_redact_and_resolve_sources(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v58-only-test-secret-value"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    execution = _fixture()
    raw = _wire(execution)
    condition = raw["assignment_repair_conditions"][0]["conditions"][0]
    condition.update(condition=secret, support_assessment=secret)
    audit = _scene_boundary_audit(raw, execution)
    assert secret not in json.dumps(audit)
    captured = capture_review_failure(
        operation="critique",
        response_content=json.dumps(raw),
        request_content=json.dumps(_payload(_Operation.CRITIQUE, execution)),
        input_version_ids=tuple(str(v) for v in execution.input_version_ids),
        validation_issues=(),
    )
    assert captured is not None and not captured["manuscript_defect_established"]
    assert secret not in json.dumps(captured)
    assert "assignment_repair_conditions" in captured["attempted_review"]
    assert "/content/outcome" in json.dumps(captured)


class RenderedRepairGateway(V26Gateway):
    critic_calls = 0
    rendered_advice = "Establish the assigned turn. Preserve the fulfilled outcome."

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if (
            assignment.get("operation") != "critique"
            or assignment.get("unit_number") != 1
            or assignment.get("revision_number") != 0
        ):
            return response
        self.critic_calls += 1
        raw = json.loads(response.content)
        check = raw["assignment_checks"]["turning_point"]
        check.update(status="unmet", recommended_resolution=None)
        source = next(
            s
            for s in payload["repair_source_catalog"]
            if s["source_path"] == "/content/turning_point"
        )
        raw["assignment_repair_conditions"] = [
            {
                "repair_ref": "assignment:turning_point",
                "conditions": [
                    {
                        "condition": text,
                        "source_refs": [
                            {"source_ref": source["source_ref"], "exact_quote": source["text"]}
                        ],
                        "support_assessment": "Synthetic routing test only.",
                    }
                    for text in ("Establish the assigned turn.", "Preserve the fulfilled outcome.")
                ],
            }
        ]
        raw["issues"] = [
            {
                "category": category,
                "severity": "major",
                "description": "The assigned turn is missing; simulated restatement.",
                "recommendation": None,
                "draft_evidence_refs": check["draft_evidence_refs"],
                "assignment_finding_ref": "assignment:turning_point",
                "assignment_comparison": {
                    "finding_refs": ["assignment:turning_point"],
                    "assessment": "The same missing turn and repair are repeated here.",
                },
            }
            for category in ("Pacing", "Plot")
        ]
        if self.critic_calls == 1:
            check["recommended_resolution"] = "Separate advice must trigger a critic-only retry."
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
async def test_durable_retry_renders_one_repair_target_then_replays_without_calls(
    migrated_database_path: Path, database_engine: Engine
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = RenderedRepairGateway(prompt.prompt, prompt, mode="rendered-repair")
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3 and gateway.critic_calls == 2
    packets = [json.loads(r.messages[-1].content) for r in gateway.requests]
    writers = [
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "write"
        and p["assignment"]["revision_number"] > 0
    ]
    assert len(writers) == 1
    targets = writers[0]["revision_contract"]["critic_acceptance_tests"]
    assert len(targets) == 1 and targets[0]["requested_change"] == gateway.rendered_advice
    with create_session_factory(database_engine)() as session:
        critics = [
            i
            for i in session.scalars(select(AgentInvocation))
            if i.specialist_role == "scene_critic"
        ]
        failed = [i for i in critics if i.error_code]
        assert len(failed) == 1 and not failed[0].output_versions
        valid = next(
            i
            for i in critics
            if i.request_settings.get("scene_boundary_audit", {}).get(
                "assignment_repair_conditions"
            )
        )
        assert valid.request_settings["scene_boundary_audit"]["schema_version"] == "7"
        assert valid.request_settings["scene_boundary_audit"]["assignment_restatements_total"] == 2
        assert (
            valid.output_versions[0].content["issues"][0]["recommendation"]
            == gateway.rendered_advice
        )
