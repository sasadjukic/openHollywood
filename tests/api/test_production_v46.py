"""Structural retention is not semantic approval of a critic's classification."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation
from open_hollywood_api.services.production_model_executor import (
    _critic_retained_classifications,
    _Execution,
    _Operation,
    _structured_failure_issues,
    _StructuredOutputContractError,
)
from open_hollywood_api.services.production_revision_acceptance import critic_repair_tests
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelDeployment, ModelRequest, ModelResponse
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import _run_gateway
from tests.api.test_production_v29 import _materialize, _raw
from tests.api.test_production_v37 import _fixture, _payload
from tests.api.test_production_v41 import LinkedRepairGateway, _linked, _revision
from tests.api.test_production_v45 import _claim
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _retry_execution(execution: _Execution, raw: dict[str, Any]) -> _Execution:
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, execution)
    return replace(
        execution,
        attempt_number=2,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(_structured_failure_issues(failure.value)),
        },
    )


def _broken(*, repeated: bool = True) -> tuple[_Execution, dict[str, Any]]:
    execution = _fixture()
    raw = _raw(execution, "assignment")
    raw["issues"] = [_claim(execution, repeated=repeated)]
    raw["issues"][0]["assignment_comparison"] = "Malformed comparison; not retry prose."
    return execution, raw


@pytest.mark.parametrize("deployment", [ModelDeployment.LOCAL, ModelDeployment.CLOUD])
@pytest.mark.parametrize("repeated", [False, True])
def test_retry_preserves_both_choices_without_replaying_rejected_claims(
    deployment: ModelDeployment,
    repeated: bool,
) -> None:
    execution, raw = _broken(repeated=repeated)
    execution = replace(execution, selection=replace(execution.selection, deployment=deployment))
    retry = _retry_execution(execution, raw)
    packet = _payload(_Operation.CRITIQUE, retry)
    retained = packet["schema_repair"]["preserved_classifications"]
    assert len(retained) == 1
    assert retained[0]["assignment_finding_refs"] == ["assignment:outcome" if repeated else None]
    assert retained[0]["category"] == raw["issues"][0]["category"]
    assert "Malformed comparison" not in json.dumps(packet)
    assert raw["issues"][0]["description"] not in json.dumps(packet)
    assert raw["issues"][0]["recommendation"] not in json.dumps(packet)
    assert len(packet["schema_repair"]["focus_locations"]) == 1
    repaired = deepcopy(raw)
    repaired["issues"][0]["assignment_comparison"] = _claim(execution, repeated=repeated)[
        "assignment_comparison"
    ]
    before = deepcopy(repaired)
    assert _materialize(repaired, retry) == _materialize(repaired, execution)
    assert repaired == before


@pytest.mark.parametrize(
    "change",
    ["null", "other_alias", "drop", "duplicate", "category", "severity", "evidence", "missing"],
)
def test_valid_comparison_cannot_hide_reclassification_or_changed_retained_metadata(
    change: str,
) -> None:
    execution, raw = _broken()
    retry = _retry_execution(execution, raw)
    raw["issues"][0]["assignment_comparison"] = _claim(execution, repeated=True)[
        "assignment_comparison"
    ]
    issue = raw["issues"][0]
    if change == "null":
        issue["assignment_finding_ref"] = None
    elif change == "other_alias":
        issue["assignment_finding_ref"] = "boundary"
    elif change == "drop":
        raw["issues"] = []
    elif change == "duplicate":
        raw["issues"].append(deepcopy(issue))
    elif change == "missing":
        issue.pop("assignment_finding_ref")
    elif change == "evidence":
        issue["draft_evidence_refs"] = ["invented"]
    else:
        issue[change] = "prose" if change == "category" else "blocking"
    before = deepcopy(raw)
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, retry)
    assert _structured_failure_issues(failure.value)[0]["type"] == "critic_classification_drift"
    assert raw == before
    later = replace(
        retry,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(_structured_failure_issues(failure.value)),
        },
    )
    assert _critic_retained_classifications(later) == _critic_retained_classifications(retry)


def test_independence_cannot_silently_become_repetition() -> None:
    execution, raw = _broken(repeated=False)
    retry = _retry_execution(execution, raw)
    raw["issues"][0] = _claim(execution, repeated=True)
    with pytest.raises(_StructuredOutputContractError, match="preserve retained"):
        _materialize(raw, retry)


def test_disappearing_target_stays_invalid_and_a_later_retry_keeps_original_choices() -> None:
    execution, raw = _broken()
    retry = _retry_execution(execution, raw)
    raw["issues"][0]["assignment_comparison"] = _claim(execution, repeated=True)[
        "assignment_comparison"
    ]
    raw["assignment_violations"] = []
    with pytest.raises(_StructuredOutputContractError):
        _materialize(raw, retry)
    raw["scene_boundary_check"] = "invalid hard metadata"
    with pytest.raises(_StructuredOutputContractError) as failure:
        _materialize(raw, retry)
    again = replace(
        retry,
        previous_failure={
            "error_code": "schema_validation_failed",
            "validation_issues": list(_structured_failure_issues(failure.value)),
        },
    )
    assert _critic_retained_classifications(again) == _critic_retained_classifications(retry)


def test_capture_bounds_never_partially_preserve_an_oversized_group() -> None:
    execution, raw = _broken()
    raw["issues"] *= 64
    retry = _retry_execution(execution, raw)
    assert not _critic_retained_classifications(retry)
    assert retry.previous_failure is not None
    records: Any = retry.previous_failure["validation_issues"]
    assert len(records) <= 12 and all(
        len(value) <= 500 for item in records for value in item.values()
    )


def test_order_and_shared_metadata_are_not_claim_identity() -> None:
    execution, raw = _broken()
    independent = _claim(execution)
    # Same category, severity and evidence; do not collapse distinct complaints.
    raw["issues"].extend([independent, deepcopy(independent)])
    retry = _retry_execution(execution, raw)
    retained = _critic_retained_classifications(retry)
    assert len(retained) == 1 and retained[0]["assignment_finding_refs"].count(None) == 2
    raw["issues"][0]["assignment_comparison"] = _claim(execution, repeated=True)[
        "assignment_comparison"
    ]
    raw["issues"].reverse()
    for issue in raw["issues"]:
        issue["draft_evidence_refs"].reverse()
    assert len(_materialize(raw, retry)["issues"]) == 3
    raw["issues"].pop(0)
    with pytest.raises(_StructuredOutputContractError, match="preserve retained"):
        _materialize(raw, retry)


@pytest.mark.parametrize(
    "bad",
    [
        "missing_ref",
        "unreported",
        "malformed_ref",
        "stale_evidence",
        "blank_description",
        "extra",
        "secret",
        "oversized",
        "mixed_group",
    ],
)
def test_invalid_or_unbounded_claim_metadata_is_not_frozen(
    bad: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    execution, raw = _broken()
    issue = raw["issues"][0]
    if bad == "missing_ref":
        issue.pop("assignment_finding_ref")
    elif bad == "unreported":
        issue["assignment_finding_ref"] = "assignment:turning_point"
    elif bad == "malformed_ref":
        issue["assignment_finding_ref"] = []
    elif bad == "stale_evidence":
        issue["draft_evidence_refs"] = ["old"]
    elif bad == "blank_description":
        issue["description"] = ""
    elif bad == "extra":
        issue["injected"] = "value"
    elif bad == "secret":
        monkeypatch.setenv("OLLAMA_API_KEY", "private-category")
        issue["category"] = "private-category"
    elif bad == "oversized":
        issue["category"] = "x" * 81
    else:
        broken = deepcopy(issue)
        broken.pop("assignment_finding_ref")
        raw["issues"].append(broken)
    retry = _retry_execution(execution, raw)
    assert _critic_retained_classifications(retry) == []
    assert "private-category" not in json.dumps(_payload(_Operation.CRITIQUE, retry))


@pytest.mark.parametrize(
    "bad", ["candidate", "context", "evidence", "choices", "extra", "truncated"]
)
def test_stale_or_malformed_retention_hints_never_constrain_a_review(bad: str) -> None:
    execution, raw = _broken()
    retry = _retry_execution(execution, raw)
    assert retry.previous_failure is not None
    records: Any = retry.previous_failure["validation_issues"]
    record = next(r for r in records if r["type"] == "critic_classification_preserved")
    hint = json.loads(record["repair_hint"])
    if bad in ("candidate", "context"):
        hint[bad] = "other-inputs"
    elif bad == "evidence":
        hint[bad] = ["old"]
    elif bad == "choices":
        hint[bad] = [{}]
    elif bad == "extra":
        hint["allegation"] = "Invent a defect"
    record["repair_hint"] = "x" * 501 if bad == "truncated" else json.dumps(hint)
    assert _critic_retained_classifications(retry) == []
    assert "Invent a defect" not in json.dumps(_payload(_Operation.CRITIQUE, retry))


def test_other_structural_errors_retain_valid_comparisons_and_original_repair_ids() -> None:
    execution = _revision()
    raw = _linked(execution)
    raw["issues"] = [_claim(execution, repeated=True)]
    raw["issues"][0]["draft_evidence_refs"] = raw["scene_boundary_check"]["draft_evidence_refs"]
    raw["scores"] = []
    retry = _retry_execution(execution, raw)
    assert _critic_retained_classifications(retry)
    raw["scores"] = _linked(execution)["scores"]
    result = _materialize(raw, retry)
    old_tests = critic_repair_tests(execution.inputs, execution.unit_id)
    review = {
        "artifact_kind": "critique",
        "artifact_key": "next",
        "artifact_version_id": "11111111-1111-4111-8111-111111111111",
        "content": result,
    }
    assert critic_repair_tests((*execution.inputs, review), execution.unit_id) == old_tests
    # Retention is attempt-scoped; a fresh assessment can make a different choice.
    raw["issues"][0]["assignment_finding_ref"] = None
    assert _materialize(raw, execution)


class ClassificationRetryGateway(LinkedRepairGateway):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args, invalid_once=False)
        self.revision_calls = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await super().generate(request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != "critique" or assignment["revision_number"] != 1:
            return response
        self.revision_calls += 1
        raw = json.loads(response.content)
        raw["issues"] = [
            {
                "category": "tension",
                "severity": "major",
                "description": "Synthetic repeated outcome complaint.",
                "recommendation": "Restore outcome.",
                "draft_evidence_refs": raw["scene_boundary_check"]["draft_evidence_refs"],
                "assignment_finding_ref": "assignment:outcome",
                "assignment_comparison": {
                    "finding_refs": ["assignment:outcome"],
                    "assessment": "Same state and remedy.",
                },
            }
        ]
        if self.revision_calls == 1:
            # Domain validation fails after materialization, exercising outer capture.
            raw["summary"] = ""
        else:
            assert payload["schema_repair"]["preserved_classifications"][0][
                "assignment_finding_refs"
            ] == ["assignment:outcome"]
            assert "Synthetic repeated outcome complaint" not in json.dumps(payload)
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
async def test_persisted_domain_failure_retries_same_draft_without_extra_writer_or_repair(
    migrated_database_path: Path,
    database_engine: Engine,
) -> None:
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = ClassificationRetryGateway(prompt.prompt, prompt)
    result = await _run_gateway(gateway, migrated_database_path, database_engine)
    assert len(result.result.accepted_units) == 3 and gateway.revision_calls == 2
    packets = [json.loads(r.messages[-1].content) for r in gateway.requests]
    assert sum(p.get("assignment", {}).get("operation") == "write" for p in packets) == 5
    revisions = [
        p
        for p in packets
        if p.get("assignment", {}).get("operation") == "critique"
        and p["assignment"]["revision_number"] == 1
    ]
    assert revisions[0]["input_artifacts"] == revisions[1]["input_artifacts"]
    assert revisions[0]["repair_acceptance_tests"] == revisions[1]["repair_acceptance_tests"]
    with create_session_factory(database_engine)() as session:
        failed = [i for i in session.scalars(select(AgentInvocation)) if i.error_code]
        assert len(failed) == 1 and not failed[0].output_versions
        assert any(
            i["type"] == "critic_classification_preserved"
            for i in failed[0].request_settings["structured_failure"]["issues"]
        )
