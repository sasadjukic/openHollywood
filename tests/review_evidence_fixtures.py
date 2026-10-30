"""Authored review evidence fixtures through the unchanged production renderer."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, Literal
from uuid import uuid4

from open_hollywood_api.services.production_model_executor import (
    _critic_evidence_catalog,
    _messages,
    _Operation,
    _output_schema,
    _scene_boundary_audit,
)
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import ReviewSnapshot, messages_hash

from tests.api.test_production_v37 import _fixture
from tests.api.test_production_v41 import _revision
from tests.api.test_production_v58 import _wire


def review_snapshot(
    *, revision: bool = False, status: Literal["met", "unmet"] = "met"
) -> ReviewSnapshot:
    execution = (
        _revision()
        if revision
        else _fixture(
            "Elara decides to verify the handwriting. Mira waits. "
            "Elara decides to verify the handwriting."
        )
    )
    for item in execution.inputs:
        if item["artifact_kind"] in ("scene_plan", "scene_draft"):
            item["artifact_key"] = item["artifact_kind"] + "_" + execution.unit_id
        if item["artifact_kind"] == "critique":
            item["content"]["target_artifact_key"] = "scene_draft_" + execution.unit_id
    audit: dict[str, Any] = _scene_boundary_audit(_wire(execution, unmet=False), execution)
    catalog = _critic_evidence_catalog(execution)
    for check in audit["assignment_checks"].values():
        check.update(
            status=status,
            assessment="Authored local judgment; not semantic ground truth.",
            recommended_resolution=None if status == "met" else "Authored repair advice.",
            draft_evidence_refs=[catalog[0]["evidence_ref"]],
        )
    messages = _messages(
        _Operation.CRITIQUE,
        execution,
        _output_schema(_Operation.CRITIQUE, continuity_schema_variant=None),
        continuity_schema_variant=None,
        continuity_model_context=None,
    )
    project = str(execution.project_id)
    # Minimal authored review content; real persisted canonical reviews are covered separately.
    critique = {
        "target_artifact_kind": "scene_draft",
        "target_artifact_key": "scene_draft_" + execution.unit_id,
        "target_artifact_version_id": audit["candidate_version_id"],
        "verdict": "pass",
        "issues": [],
    }
    body: dict[str, Any] = {
        "invocation": {
            "invocation_id": str(uuid4()),
            "workflow_run_id": str(execution.workflow_run_id),
            "project_id": project,
            "attempt": 1,
            "task_fingerprint": "a" * 64,
            "prompt_sha256": "b" * 64,
            "response_sha256": "c" * 64,
        },
        "critique": {
            "version_id": str(uuid4()),
            "project_id": project,
            "artifact_kind": "critique",
            "artifact_key": "critique_" + execution.unit_id,
            "content": critique,
            "content_sha256": canonical_sha256(critique),
        },
        "draft_version_id": audit["candidate_version_id"],
        "plan_version_id": audit["current_plan_version_id"],
        "scene_id": execution.unit_id,
        "sources": [
            {
                "version_id": a["artifact_version_id"],
                "project_id": project,
                "artifact_kind": a["artifact_kind"],
                "artifact_key": a["artifact_key"],
                "content": deepcopy(a["content"]),
                "content_sha256": canonical_sha256(a["content"]),
            }
            for a in execution.inputs
        ],
        "messages": [{"role": m.role.value, "content": m.content} for m in messages],
        "native_audit": audit,
    }
    snapshot = ReviewSnapshot.model_validate_json(json.dumps(body))
    body["invocation"]["prompt_sha256"] = messages_hash(snapshot.messages)
    return ReviewSnapshot.model_validate_json(json.dumps(body))
