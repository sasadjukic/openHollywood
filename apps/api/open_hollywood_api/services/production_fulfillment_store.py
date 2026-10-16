"""Exact SQLite provenance and pinned writer handoff snapshots."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.workflows import SceneProductionError, SceneWritingTask
from sqlalchemy import select
from sqlalchemy.orm import Session

from open_hollywood_api.persistence.models import (
    AgentInvocation,
    ArtifactVersion,
    InvocationStatus,
)
from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services.production_fulfillment import (
    HANDOFF_POLICY_VERSION,
    HANDOFF_PROMPT_VERSION,
    MAX_PACKET_BYTES,
    SUPPORTED_CRITIC_VERSIONS,
    Projection,
    packet_bytes,
)


class FulfillmentIntegrityError(SceneProductionError):
    """A pinned request must never acquire new evidence or another retry identity."""


@dataclass(frozen=True)
class FulfillmentSource:
    inputs: tuple[dict[str, Any], ...]
    audit: object
    response_sha256: str


def _version_state(version: ArtifactVersion) -> dict[str, Any]:
    return {
        "version_id": str(version.id),
        "artifact_key": version.artifact.artifact_key,
        "artifact_kind": version.artifact.artifact_type,
        "project_id": str(version.artifact.project_id),
        "schema_version": version.schema_version,
        "content_sha256": version.content_sha256,
        "actual_content_sha256": canonical_sha256(version.content),
        "creator_invocation_id": (
            str(version.created_by_invocation_id) if version.created_by_invocation_id else None
        ),
    }


def _shared(versions: list[ArtifactVersion], scene_number: int) -> dict[str, list[str]]:
    shared = {
        kind: sorted(str(v.id) for v in versions if v.artifact.artifact_type == kind)
        for kind in ("story_blueprint", "story_bible", "scene_plan")
    }
    shared["accepted_prior_scenes"] = sorted(
        str(v.id)
        for v in versions
        if v.artifact.artifact_type == "scene_draft"
        and isinstance(v.content.get("scene_number"), int)
        and v.content["scene_number"] < scene_number
    )
    return shared


def _source_state(
    session: Session, critique: ArtifactVersion
) -> tuple[AgentInvocation | None, dict[str, Any]]:
    creator = (
        session.get(AgentInvocation, critique.created_by_invocation_id)
        if critique.created_by_invocation_id
        else None
    )
    state: dict[str, Any] = {"source_invocation_id": str(creator.id) if creator else None}
    if creator is not None:
        settings = creator.request_settings
        state.update(
            workflow_run_id=str(creator.workflow_run_id),
            project_id=str(creator.workflow_run.project_id),
            status=creator.status.value,
            schema_validation_succeeded=creator.schema_validation_succeeded,
            specialist_role=creator.specialist_role,
            operation=_bounded_metadata_text(settings.get("operation")),
            prompt_template_version=_bounded_metadata_text(settings.get("prompt_template_version")),
            source_response_sha256=(
                settings.get("provider_response_content_sha256")
                if _is_sha256(settings.get("provider_response_content_sha256"))
                else None
            ),
            source_identity_sha256=canonical_sha256(
                {
                    key: settings.get(key)
                    for key in (
                        "operation",
                        "prompt_template_version",
                        "provider_response_content_sha256",
                    )
                }
            ),
            source_audit_sha256=canonical_sha256(settings.get("scene_boundary_audit")),
            inputs=sorted(
                (_version_state(v) for v in creator.input_versions), key=lambda v: v["version_id"]
            ),
            outputs=sorted(str(v.id) for v in creator.output_versions),
        )
    return creator, state


def _bounded_metadata_text(value: object) -> str | None:
    return value if isinstance(value, str) and len(value) <= 64 else None


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    )


def _eligible_source(
    creator: AgentInvocation | None,
    task: SceneWritingTask,
    versions: list[ArtifactVersion],
    project_id: UUID,
) -> tuple[FulfillmentSource | None, str]:
    if creator is None:
        return None, "missing_creator"
    settings = creator.request_settings
    if (
        creator.workflow_run_id != task.production.workflow_run_id
        or creator.workflow_run.project_id != project_id
        or creator.specialist_role != "scene_critic"
        or settings.get("operation") != "critique"
        or creator.status is not InvocationStatus.SUCCEEDED
        or creator.schema_validation_succeeded is not True
    ):
        return None, "ineligible_creator"
    source_version = settings.get("prompt_template_version")
    if not isinstance(source_version, str) or source_version not in SUPPORTED_CRITIC_VERSIONS:
        return None, "unsupported_critic"
    response_hash = settings.get("provider_response_content_sha256")
    if not isinstance(response_hash, str) or not _is_sha256(response_hash):
        return None, "invalid_response_hash"
    source_versions = creator.input_versions
    if task.previous_draft is None or task.previous_critique is None:
        raise SceneProductionError("fulfillment revision requires exact previous inputs")
    if task.previous_critique.version_id not in {
        v.id for v in creator.output_versions
    } or task.previous_draft.version_id not in {v.id for v in source_versions}:
        return None, "source_lineage_mismatch"
    if any(
        v.artifact.project_id != project_id or canonical_sha256(v.content) != v.content_sha256
        for v in source_versions
    ):
        return None, "source_lineage_mismatch"
    if _shared(source_versions, task.unit.unit_number) != _shared(versions, task.unit.unit_number):
        return None, "shared_authority_mismatch"
    return (
        FulfillmentSource(
            inputs=tuple(
                {
                    "artifact_key": v.artifact.artifact_key,
                    "artifact_kind": v.artifact.artifact_type,
                    "artifact_version_id": str(v.id),
                    "content": dict(v.content),
                }
                for v in source_versions
            ),
            audit=settings.get("scene_boundary_audit"),
            response_sha256=response_hash,
        ),
        "included",
    )


def _writer_versions(
    session: Session, task: SceneWritingTask, version_ids: tuple[UUID, ...], project_id: UUID
) -> list[ArtifactVersion]:
    versions: list[ArtifactVersion] = []
    for version_id in version_ids:
        version = session.get(ArtifactVersion, version_id)
        if (
            version is None
            or version.artifact.project_id != project_id
            or canonical_sha256(version.content) != version.content_sha256
        ):
            raise SceneProductionError("fulfillment writer input lineage or hash is invalid")
        versions.append(version)
    by_id = {v.id: v for v in versions}
    previous = task.previous_draft
    review = task.previous_critique
    if (
        previous is None
        or review is None
        or previous.version_id not in by_id
        or review.version_id not in by_id
    ):
        raise SceneProductionError("fulfillment revision requires exact previous inputs")
    draft, critique = by_id[previous.version_id], by_id[review.version_id]
    reviews = [v for v in versions if v.artifact.artifact_type == "critique"]
    drafts = [
        v
        for v in versions
        if v.artifact.artifact_type == "scene_draft"
        and v.content.get("scene_id") == task.unit.unit_id
        and v.content.get("revision_number") == task.revision_number - 1
    ]
    shared = _shared(versions, task.unit.unit_number)
    if (
        not reviews
        or reviews[-1].id != critique.id
        or [v.id for v in drafts] != [draft.id]
        or draft.artifact.artifact_key != f"scene_draft_{task.unit.unit_id}"
        or critique.artifact.artifact_key != f"critique_{task.unit.unit_id}"
        or critique.content.get("target_artifact_kind") != "scene_draft"
        or critique.content.get("target_artifact_key") != draft.artifact.artifact_key
        or critique.content.get("target_artifact_version_id") != str(draft.id)
        or draft.content.get("scene_number") != task.unit.unit_number
        or shared
        != {
            "story_blueprint": [str(task.production.approved_blueprint.version_id)],
            "story_bible": [str(task.story_bible.version_id)],
            "scene_plan": [str(task.unit.plan.version_id)],
            "accepted_prior_scenes": sorted(str(v.version_id) for v in task.accepted_units),
        }
    ):
        raise SceneProductionError("fulfillment revision task disagrees with its input lineage")
    plan = by_id[task.unit.plan.version_id]
    if (
        plan.content.get("id") != task.unit.unit_id
        or plan.content.get("scene_number") != task.unit.unit_number
    ):
        raise SceneProductionError("fulfillment scene plan identity is invalid")
    return versions


def select_handoff(
    session: Session,
    *,
    task: SceneWritingTask,
    project_id: UUID,
    version_ids: tuple[UUID, ...],
    base_fingerprint: str,
    project: Callable[[FulfillmentSource], Projection],
) -> dict[str, Any]:
    """Find a pinned decision before projecting anything from mutable audit metadata."""
    logical_key = canonical_sha256(
        {
            "base_fingerprint": base_fingerprint,
            "handoff_policy_version": HANDOFF_POLICY_VERSION,
        }
    )
    candidates = []
    for invocation in session.scalars(
        select(AgentInvocation).where(
            AgentInvocation.workflow_run_id == task.production.workflow_run_id,
            AgentInvocation.specialist_role == "scene_writer",
        )
    ):
        settings = invocation.request_settings
        same_inputs = {v.id for v in invocation.input_versions} == set(version_ids)
        if settings.get("writer_logical_task_key") == logical_key or (
            same_inputs
            and settings.get("prompt_template_version") == HANDOFF_PROMPT_VERSION
            and settings.get("operation") == "write"
        ):
            candidates.append(invocation)
    versions = _writer_versions(session, task, version_ids, project_id)
    critique = next(
        v for v in versions if task.previous_critique and v.id == task.previous_critique.version_id
    )
    creator, source_state = _source_state(session, critique)
    dependencies = [_version_state(v) for v in versions]
    provenance = {
        "source_critique_version_id": str(critique.id),
        "reviewed_draft_version_id": str(task.previous_draft.version_id)
        if task.previous_draft
        else None,
        "plan_version_id": str(task.unit.plan.version_id),
        "dependencies": dependencies,
        "source_state": source_state,
    }
    if candidates:
        snapshots = [i.request_settings.get("writer_fulfillment_handoff") for i in candidates]
        first = snapshots[0]
        if not isinstance(first, dict) or any(s != first for s in snapshots):
            raise FulfillmentIntegrityError("conflicting or missing writer fulfillment snapshots")
        validate_snapshot(first, logical_key=logical_key, base_fingerprint=base_fingerprint)
        if first.get("provenance") != provenance:
            raise FulfillmentIntegrityError("writer fulfillment source or dependencies changed")
        if any(
            i.request_settings.get("task_fingerprint") != first["task_fingerprint"]
            for i in candidates
        ):
            raise FulfillmentIntegrityError("writer fulfillment fingerprint changed")
        active_secret_guard().ensure_safe(first, destination="writer fulfillment replay")
        return first
    source, reason = _eligible_source(creator, task, versions, project_id)
    projection = project(source) if source is not None else Projection(None, reason)
    # Credentials are security errors even when the optional packet is too large.
    active_secret_guard().ensure_safe(projection.packet, destination="writer fulfillment packet")
    if projection.packet is not None and len(packet_bytes(projection.packet)) > MAX_PACKET_BYTES:
        projection = Projection(None, "packet_too_large")
    snapshot: dict[str, Any] = {
        "schema_version": "1",
        "policy_version": HANDOFF_POLICY_VERSION,
        "logical_task_key": logical_key,
        "base_fingerprint": base_fingerprint,
        "status": "included" if projection.packet is not None else "omitted",
        "reason": projection.reason,
        "packet": projection.packet,
        "packet_sha256": canonical_sha256(projection.packet),
        "provenance": provenance,
    }
    snapshot["snapshot_sha256"] = canonical_sha256(snapshot)
    snapshot["task_fingerprint"] = canonical_sha256(
        {
            "logical_task_key": logical_key,
            "snapshot_sha256": snapshot["snapshot_sha256"],
        }
    )
    active_secret_guard().ensure_safe(snapshot, destination="writer fulfillment snapshot")
    return snapshot


def validate_snapshot(snapshot: dict[str, Any], *, logical_key: str, base_fingerprint: str) -> None:
    body = {k: v for k, v in snapshot.items() if k not in {"snapshot_sha256", "task_fingerprint"}}
    digest = canonical_sha256(body)
    if (
        snapshot.get("schema_version") != "1"
        or snapshot.get("policy_version") != HANDOFF_POLICY_VERSION
        or snapshot.get("logical_task_key") != logical_key
        or snapshot.get("base_fingerprint") != base_fingerprint
        or snapshot.get("snapshot_sha256") != digest
        or snapshot.get("packet_sha256") != canonical_sha256(snapshot.get("packet"))
        or snapshot.get("task_fingerprint")
        != canonical_sha256(
            {
                "logical_task_key": logical_key,
                "snapshot_sha256": digest,
            }
        )
        or (snapshot.get("packet") is None) != (snapshot.get("status") == "omitted")
    ):
        raise FulfillmentIntegrityError("writer fulfillment snapshot integrity check failed")


def verify_handoff_before_start(
    session: Session, snapshot: dict[str, Any], invocation: AgentInvocation
) -> None:
    """Recheck after the invocation insert takes SQLite's write lock, before commit."""
    validate_snapshot(
        snapshot,
        logical_key=snapshot["logical_task_key"],
        base_fingerprint=snapshot["base_fingerprint"],
    )
    provenance = snapshot["provenance"]
    for dependency in provenance["dependencies"]:
        version = session.get(ArtifactVersion, UUID(dependency["version_id"]))
        if version is None or _version_state(version) != dependency:
            raise FulfillmentIntegrityError(
                "writer fulfillment dependency changed before submission"
            )
    critique = session.get(ArtifactVersion, UUID(provenance["source_critique_version_id"]))
    if critique is None or _source_state(session, critique)[1] != provenance["source_state"]:
        raise FulfillmentIntegrityError("writer fulfillment source changed before submission")
    expected_attempt = 1
    for other in session.scalars(
        select(AgentInvocation).where(
            AgentInvocation.workflow_run_id == invocation.workflow_run_id,
            AgentInvocation.id != invocation.id,
            AgentInvocation.specialist_role == "scene_writer",
        )
    ):
        settings = other.request_settings
        if settings.get("writer_logical_task_key") != snapshot["logical_task_key"]:
            continue
        if settings.get("writer_fulfillment_handoff") != snapshot:
            raise FulfillmentIntegrityError(
                "conflicting writer fulfillment snapshot before submission"
            )
        if other.status in {InvocationStatus.RUNNING, InvocationStatus.SUCCEEDED}:
            raise FulfillmentIntegrityError("writer fulfillment task already running or succeeded")
        if other.status is InvocationStatus.FAILED and other.error_code != "interrupted_execution":
            expected_attempt += 1
    if invocation.request_settings.get("attempt_number") != expected_attempt:
        raise FulfillmentIntegrityError(
            "writer fulfillment retry context changed before submission"
        )
