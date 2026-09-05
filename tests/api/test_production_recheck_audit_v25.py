"""Recheck releases remain auditable without storing model assessment prose."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    InvocationStatus,
    Project,
    RunStatus,
    WorkflowRun,
)
from open_hollywood_api.services.production_model_executor import (
    BenchmarkProductionExecutor,
    _continuity_recheck_decision_audit,
    _ContinuityModelContext,
    _Operation,
    _StructuredOutputContractError,
)
from open_hollywood_engine.artifacts import ArtifactKind, ContinuityCategory, ContinuityReport
from open_hollywood_engine.models import ModelGateway, ModelResponse, ModelTiming, ModelUsage
from sqlalchemy import Engine

from tests.evaluations.test_agentic_production import (
    _schema_test_continuity_context,
    _v17_catalog_test_execution,
)


def _context() -> _ContinuityModelContext:
    context = _schema_test_continuity_context(recheck=True)
    previous = deepcopy(context.previous_continuity_report)
    assert previous is not None
    previous["content"]["findings"] = [
        {"id": "issue_1", "severity": "error", "basis": "contradiction"}
    ]
    return replace(context, previous_continuity_report=previous)


def _decision(
    status: str, assessment: str = "The current evidence supports this decision."
) -> dict[str, Any]:
    field = "repair_assessment" if status == "still_blocking" else "resolution_assessment"
    return {
        "prior_finding_rechecks": {
            "issue_1": {
                "status": status,
                field: assessment,
                "revised_draft_evidence_refs": ["draft_evidence_1", "Mara pockets the brass key."],
            }
        }
    }


@pytest.mark.parametrize("status", ["resolved", "invalidated", "advisory", "still_blocking"])
def test_every_validated_recheck_outcome_keeps_original_id_and_normalized_evidence(
    status: str,
) -> None:
    audit = _continuity_recheck_decision_audit(
        _decision(status), _context(), materialized_blocking_finding_ids=frozenset()
    )

    assert len(audit) == 1
    assert audit[0]["finding_id"] == "issue_1"
    assert audit[0]["status"] == status
    assert audit[0]["revised_draft_evidence_refs"] == ["draft_evidence_0001"]
    assert audit[0]["materialized_blocks_approval"] is False
    assert len(str(audit[0]["assessment_sha256"])) == 64
    assert "The current evidence" not in json.dumps(audit)


def test_materialized_blocking_flag_distinguishes_application_routing_from_model_decision() -> None:
    audit = _continuity_recheck_decision_audit(
        _decision("still_blocking"),
        _context(),
        materialized_blocking_finding_ids=frozenset({"issue_1"}),
    )
    assert audit[0]["materialized_blocks_approval"] is True


def test_assessment_hash_redacts_runtime_secret_and_normalizes_whitespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "v25-audit-unit-test-runtime-credential"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    audit = _continuity_recheck_decision_audit(
        _decision("invalidated", f"  Unsupported  {secret}\nclaim.  "),
        _context(),
        materialized_blocking_finding_ids=frozenset(),
    )
    assert (
        audit[0]["assessment_sha256"]
        == hashlib.sha256(b"Unsupported [REDACTED] claim.").hexdigest()
    )
    assert secret not in json.dumps(audit)


@pytest.mark.parametrize(
    "invalid", ["unknown_finding", "bad_evidence", "empty_evidence", "missing_reason"]
)
def test_audit_cannot_turn_unvalidated_releases_into_valid_records(invalid: str) -> None:
    data = _decision("resolved")
    entry = data["prior_finding_rechecks"]["issue_1"]
    if invalid == "unknown_finding":
        data["prior_finding_rechecks"]["invented"] = data["prior_finding_rechecks"].pop("issue_1")
    elif invalid == "bad_evidence":
        entry["revised_draft_evidence_refs"] = ["draft_evidence_9999"]
    elif invalid == "empty_evidence":
        entry["revised_draft_evidence_refs"] = []
    else:
        entry["resolution_assessment"] = " "
    with pytest.raises(_StructuredOutputContractError):
        _continuity_recheck_decision_audit(
            data, _context(), materialized_blocking_finding_ids=frozenset()
        )


def test_initial_continuity_call_has_no_prior_decision_audit() -> None:
    assert (
        _continuity_recheck_decision_audit(
            {}, _schema_test_continuity_context(), materialized_blocking_finding_ids=frozenset()
        )
        == ()
    )


def test_successful_invocation_persists_released_decision_even_without_blocking_artifact(
    database_engine: Engine,
) -> None:
    session_factory = create_session_factory(database_engine)
    original = _v17_catalog_test_execution()
    inputs = list(deepcopy(original.inputs))
    for item in inputs:
        if item["artifact_kind"] == ArtifactKind.SCENE_DRAFT.value:
            item["content"]["revision_number"] = 1
    prior = _context().previous_continuity_report
    assert prior is not None
    inputs.append(prior)
    execution = replace(original, revision_number=1, inputs=tuple(inputs))
    invocation_id = uuid4()
    with session_factory.begin() as session:
        project = Project(id=execution.project_id, name="Recheck audit")
        run = WorkflowRun(
            id=execution.workflow_run_id,
            project=project,
            workflow_name="scene_production",
            graph_version="4",
            status=RunStatus.RUNNING,
        )
        session.add_all(
            (
                project,
                run,
                AgentInvocation(
                    id=invocation_id,
                    workflow_run=run,
                    specialist_role="continuity_supervisor",
                    provider="ollama",
                    model_identifier="local-fixture",
                    status=InvocationStatus.RUNNING,
                    request_settings={"operation": "continuity"},
                    prompt_sha256="0" * 64,
                ),
            )
        )
    report = ContinuityReport(
        story_bible_version_id=uuid4(),
        scene_version_id=uuid4(),
        scene_plan_version_id=uuid4(),
        scene_id="scene_1",
        scene_number=1,
        checked_categories=tuple(ContinuityCategory),
    )
    response = ModelResponse(
        provider=execution.selection.provider,
        model_identifier=execution.selection.model_identifier,
        deployment=execution.selection.deployment,
        content=json.dumps(_decision("invalidated")),
        thinking=None,
        finish_reason="stop",
        created_at=datetime.now(UTC),
        usage=ModelUsage(input_tokens=1, output_tokens=1),
        timing=ModelTiming(total_ms=1),
        estimated_cost_usd=Decimal("0"),
    )
    executor = BenchmarkProductionExecutor(
        session_factory=session_factory, gateway=cast(ModelGateway, object())
    )

    references = executor._complete_invocation(
        invocation_id, _Operation.CONTINUITY, object(), execution, report, response
    )

    assert len(references) == 1
    with session_factory() as session:
        invocation = session.get(AgentInvocation, invocation_id)
        assert invocation is not None
        assert invocation.status is InvocationStatus.SUCCEEDED
        assert invocation.schema_validation_succeeded is True
        assert invocation.request_settings["operation"] == "continuity"
        audit = invocation.request_settings["continuity_recheck_decisions"]
    assert audit["schema_version"] == "1"
    assert audit["decisions"][0]["status"] == "invalidated"
    assert audit["decisions"][0]["finding_id"] == "issue_1"
    assert audit["decisions"][0]["revised_draft_evidence_refs"] == ["draft_evidence_0001"]
    assert audit["decisions"][0]["materialized_blocks_approval"] is False
