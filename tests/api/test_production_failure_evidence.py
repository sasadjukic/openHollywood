"""Failed reviews remain inspectable without becoming manuscript facts or retry input."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import AgentInvocation, Artifact, ArtifactVersion
from open_hollywood_api.persistence.secret_policy import audit_database_export
from open_hollywood_api.services.production_failure_evidence import (
    MAX_RESPONSE_CHARS,
    capture_review_failure,
)
from open_hollywood_api.services.production_model_executor import _retry_context
from open_hollywood_engine.evaluations import load_benchmark_corpus
from open_hollywood_engine.models import ModelRequest, ModelResponse
from open_hollywood_engine.workflows import SceneProductionError
from sqlalchemy import Engine, select

from tests.api.test_production_v26 import V26Gateway, _run_gateway
from tests.evaluations.test_agentic_blueprint import CORPUS_PATH
from tests.evaluations.test_agentic_production import ProductionFixtureGateway


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _payload(assigned: str | None = None) -> dict[str, Any]:
    return {
        "assignment": {"unit_id": "scene_2", "revision_number": 0},
        "scene_assignment_contract": {
            "scene_id": "scene_2",
            "point_of_view_character_id": assigned,
        },
        "viewpoint_contract": {
            "assignment_origin": "unassigned" if assigned is None else "scene_plan"
        },
        "candidate_draft": {
            "artifact_version_id": "exact-draft-version",
            "content": {
                "evidence_catalog": [
                    {"evidence_ref": "current", "exact_excerpt": "Clara wanted to believe him."},
                ]
            },
        },
        "contradiction_claim_catalog": [
            {"canonical_claim_id": "claim_1", "claim": "The door was open.", "category": "fact"},
        ],
    }


def _capture(
    raw: object, *, payload: dict[str, Any] | None = None, operation: str = "critique"
) -> dict[str, Any]:
    result = capture_review_failure(
        operation=operation,
        response_content=json.dumps(raw),
        request_content=json.dumps(payload or _payload()),
        input_version_ids=("exact-draft-version", "exact-plan-version"),
        validation_issues=({"type": "viewpoint_subject_not_other_character"},),
    )
    assert result is not None
    return result


@pytest.mark.parametrize(
    "assigned,subject,reason",
    [(None, "clara", "no_assigned_viewpoint"), ("elias", "elias", "subject_is_assigned_character")],
)
def test_rejected_pov_retains_finding_and_exact_evidence(
    assigned: str | None,
    subject: str,
    reason: str,
) -> None:
    check = {
        "status": "violation",
        "violation_kind": "unauthorized_private_state",
        "subject_character_id": subject,
        "draft_evidence_refs": ["current", "stale"],
        "assessment": "An alleged private belief.",
        "recommended_resolution": "Use observation.",
    }
    result = _capture({"point_of_view_check": check}, payload=_payload(assigned))
    assert result["viewpoint_failure_reason"] == reason
    assert result["attempted_review"]["point_of_view_check"] == check
    assert result["manuscript_defect_established"] is False
    selected = result["selected_evidence"]
    assert selected[0]["source"]["exact_excerpt"] == "Clara wanted to believe him."
    assert selected[0]["artifact_version_id"] == "exact-draft-version"
    assert len(selected[0]["excerpt_sha256"]) == 64
    assert selected[1]["resolution"] == "unresolved"
    assert "source" not in selected[1]


def test_continuity_and_recheck_fields_survive_materialization_failure() -> None:
    raw = {
        "new_findings": [
            {
                "summary": "Alleged conflict.",
                "draft_evidence_refs": ["current"],
                "basis_details": {
                    "canonical_claim_ids": ["claim_1", "missing"],
                    "conflict_explanation": "They cannot coexist.",
                },
            }
        ],
        "prior_finding_rechecks": {
            "old_finding": {
                "status": "still_blocking",
                "repair_assessment": "Not repaired.",
                "revised_draft_evidence_refs": ["current"],
            }
        },
        "requirement_coverage": {
            "scene_plan_time_context": {
                "status": "partial",
                "assessment": "Time is uncertain.",
                "evidence_refs": ["stale"],
            }
        },
    }
    result = _capture(raw, operation="continuity")
    attempted = result["attempted_review"]
    assert attempted["new_findings"][0]["basis_details"]["canonical_claim_ids"] == [
        "claim_1",
        "missing",
    ]
    assert attempted["prior_finding_rechecks"][0]["entry_id"] == "old_finding"
    assert attempted["prior_finding_rechecks"][0]["finding"]["repair_assessment"] == "Not repaired."
    assert attempted["requirement_coverage"][0]["finding"]["status"] == "partial"
    assert any(
        r.get("source", {}).get("claim") == "The door was open."
        for r in result["selected_evidence"]
    )


@pytest.mark.parametrize("operation", ["critique", "continuity", "continuity_adjudication"])
def test_parse_failures_record_availability_not_raw_prose(operation: str) -> None:
    for body, expected in [
        ('{"assessment": "private prose"', "unparseable_response"),
        ("{} trailing private prose", "unparseable_response"),
        ("[]", "non_object_response"),
        ("x" * (MAX_RESPONSE_CHARS + 1), "response_too_large"),
    ]:
        result = capture_review_failure(
            operation=operation,
            response_content=body,
            request_content=json.dumps(_payload()),
            input_version_ids=("exact-draft-version",),
            validation_issues=(),
        )
        assert result is not None and result["capture_status"] == expected
        assert result["candidate_artifact_version_id"] == "exact-draft-version"
        assert "private prose" not in json.dumps(result)


def test_evidence_is_allowlisted_bounded_and_redacted_before_truncation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-only-failure-evidence-credential"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    record = {
        "assessment": "x" * 990 + secret + "tail",
        "draft_evidence_refs": ["current", secret],
        "api_key": secret,
        "unexpected": "DO_NOT_STORE",
    }
    payload = _payload()
    payload["candidate_draft"]["content"]["evidence_catalog"][0]["exact_excerpt"] = secret
    raw = {
        "point_of_view_check": record,
        "issues": [record] * 100,
        "decisions": {secret: record},
        "prose": "DO_NOT_STORE",
    }
    result = _capture(raw, payload=payload)
    serialized = json.dumps(result)
    assert "test-only-" not in serialized and "DO_NOT_STORE" not in serialized
    assert "api_key" not in serialized
    assert result["truncated"] is True
    assert len(serialized) < 40_000
    assert len(result["attempted_review"]["issues"]) == 8


def test_capture_errors_do_not_replace_original_failure() -> None:
    result = capture_review_failure(
        operation="critique",
        response_content="{}",
        request_content="not json",
        input_version_ids=(),
        validation_issues=(),
    )
    assert result is not None and result["capture_status"] == "capture_unavailable"
    assert (
        capture_review_failure(
            operation="write",
            response_content="{}",
            request_content="{}",
            input_version_ids=(),
            validation_issues=(),
        )
        is None
    )


class FailureEvidenceGateway(V26Gateway):
    def __init__(self, *args: Any, fail_once: bool, operation: str) -> None:
        super().__init__(*args, mode="diagnostics")
        self.fail_once = fail_once
        self.operation = operation
        self.injected = 0

    async def generate(self, request: ModelRequest) -> ModelResponse:
        response = await ProductionFixtureGateway.generate(self, request)
        payload = json.loads(request.messages[-1].content)
        assignment = payload.get("assignment", {})
        if assignment.get("operation") != self.operation or assignment.get("unit_number") != 1:
            return response
        if self.fail_once and self.injected:
            return response
        self.injected += 1
        raw = json.loads(response.content)
        if self.operation == "critique":
            draft = next(
                x for x in payload["input_artifacts"] if x["artifact_kind"] == "scene_draft"
            )
            ref = draft["content"]["evidence_catalog"][0]["evidence_ref"]
            raw["point_of_view_check"] = {
                "status": "violation",
                "violation_kind": "unauthorized_private_state",
                "subject_character_id": (
                    payload["scene_assignment_contract"]["point_of_view_character_id"]
                    or "invented_subject"
                ),
                "draft_evidence_refs": [ref],
                "assessment": (
                    "DIAGNOSTIC_ONLY_ALLEGATION test-only-persisted-failure-evidence-value"
                ),
                "recommended_resolution": "A rejected reviewer proposal.",
            }
        else:
            ref = payload["candidate_draft"]["content"]["evidence_catalog"][0]["evidence_ref"]
            raw["findings"] = [
                {
                    "severity": "blocking",
                    "summary": (
                        "DIAGNOSTIC_ONLY_ALLEGATION test-only-persisted-failure-evidence-value"
                    ),
                    "draft_evidence_refs": [ref],
                    "recommended_resolution": "A rejected proposal.",
                    "basis_details": {
                        "basis": "contradiction",
                        "canonical_claim_ids": [],
                        "conflict_disposition": "directly_incompatible",
                        "repair_action": "replace",
                        "conflict_explanation": "Unsupported.",
                    },
                }
            ]
        return replace(response, content=json.dumps(raw))


@pytest.mark.anyio
@pytest.mark.parametrize("fail_once", [False, True])
@pytest.mark.parametrize("operation", ["critique", "continuity"])
async def test_failure_evidence_survives_sqlite_without_changing_bounded_recovery(
    fail_once: bool,
    operation: str,
    migrated_database_path: Path,
    database_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "test-only-persisted-failure-evidence-value"
    monkeypatch.setenv("OLLAMA_API_KEY", secret)
    prompt = load_benchmark_corpus(CORPUS_PATH).prompts[0]
    gateway = FailureEvidenceGateway(
        prompt.prompt, prompt, fail_once=fail_once, operation=operation
    )
    if fail_once:
        result = await _run_gateway(gateway, migrated_database_path, database_engine)
        assert len(result.result.accepted_units) == 3
    else:
        with pytest.raises(SceneProductionError):
            await _run_gateway(gateway, migrated_database_path, database_engine)
    assert gateway.injected == (1 if fail_once else 2)
    sessions = create_session_factory(database_engine)
    with sessions() as session:
        failed = [i for i in session.scalars(select(AgentInvocation)).all() if i.error_code]
        assert len(failed) == (1 if fail_once else 2)
        for invocation in failed:
            evidence = invocation.request_settings["review_failure_evidence"]
            assert evidence["capture_status"] == "captured"
            assert secret not in json.dumps(evidence)
            assert evidence["status"] == "unvalidated_review_response"
            assert evidence["selected_evidence"][0]["resolution"] == "matched_request_catalog"
            assert (
                evidence["candidate_artifact_version_id"] in evidence["input_artifact_version_ids"]
            )
            assert evidence["manuscript_defect_established"] is False
            if operation == "critique":
                assert evidence["viewpoint_failure_reason"] == (
                    "subject_is_assigned_character"
                    if evidence["scene_assignment"]["point_of_view_character_id"]
                    else "no_assigned_viewpoint"
                )
            settings = invocation.request_settings
            before = _retry_context(
                session,
                workflow_run_id=invocation.workflow_run_id,
                specialist_role=invocation.specialist_role,
                task_fingerprint=settings["task_fingerprint"],
            )
            assert "DIAGNOSTIC_ONLY_ALLEGATION" not in json.dumps(before)
            saved = invocation.request_settings
            invocation.request_settings = {
                k: v for k, v in saved.items() if k != "review_failure_evidence"
            }
            after = _retry_context(
                session,
                workflow_run_id=invocation.workflow_run_id,
                specialist_role=invocation.specialist_role,
                task_fingerprint=settings["task_fingerprint"],
            )
            assert before == after
            invocation.request_settings = saved
        artifacts = session.scalars(select(ArtifactVersion)).all()
        assert all("DIAGNOSTIC_ONLY_ALLEGATION" not in json.dumps(v.content) for v in artifacts)
        if not fail_once and operation == "critique":
            assert not session.scalars(
                select(Artifact).where(
                    Artifact.artifact_type == "critique",
                    Artifact.artifact_key == "critique_scene_1",
                )
            ).all()
    for request in gateway.requests:
        assert "DIAGNOSTIC_ONLY_ALLEGATION" not in str(request.messages)
        assert "review_failure_evidence" not in str(request.messages)
    audit_database_export(database_engine)
