"""Bounded current-row reads for historical association lookup; no connections or writes."""

from __future__ import annotations

import sqlite3
from typing import Any
from uuid import UUID

from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import strict_object, text_hash

from open_hollywood_api.persistence.secret_policy import active_secret_guard
from open_hollywood_api.services import production_association_records as records


class Unavailable(LookupError):
    """A selected association has absent or conflicting current source rows."""


def _require(condition: bool) -> None:
    if not condition:
        raise Unavailable("current_source_mismatch")


def _rows(
    connection: sqlite3.Connection, sql: str, identifier: str, limit: int
) -> list[dict[str, Any]]:
    result = connection.execute(sql, (UUID(identifier).hex,)).fetchmany(limit + 1)
    _require(len(result) <= limit)
    return [dict(row) for row in result]


def _one(connection: sqlite3.Connection, sql: str, identifier: str) -> dict[str, Any]:
    rows = _rows(connection, sql, identifier, 1)
    if not rows:
        raise Unavailable("current_source_missing")
    return rows[0]


def _uuids(value: dict[str, Any], *names: str) -> dict[str, Any]:
    for key in names:
        value[key] = str(UUID(value[key])) if value[key] is not None else None
    return value


def artifact(connection: sqlite3.Connection, version: str) -> records.ArtifactRow:
    row = _one(
        connection,
        "SELECT v.id,v.artifact_id,v.parent_version_id,v.created_by_invocation_id,"
        "v.version_number,v.schema_version,v.content,v.content_sha256,a.project_id,"
        "a.artifact_type,a.artifact_key FROM artifact_versions v "
        "JOIN artifacts a ON a.id=v.artifact_id WHERE v.id=?",
        version,
    )
    _uuids(row, "id", "artifact_id", "parent_version_id", "created_by_invocation_id", "project_id")
    raw = row["content"]
    active_secret_guard().ensure_safe(raw, destination="association current source")
    row["content"] = strict_object(raw)
    row["stored_content_bytes_sha256"] = text_hash(raw)
    _require(canonical_sha256(row["content"]) == row["content_sha256"])
    return records.ArtifactRow.model_validate(row)


def lineage(connection: sqlite3.Connection, logical: str) -> tuple[records.LineageRow, ...]:
    rows = _rows(
        connection,
        "SELECT id,artifact_id,parent_version_id,created_by_invocation_id,version_number,"
        "content_sha256 FROM artifact_versions WHERE artifact_id=? ORDER BY version_number",
        logical,
        64,
    )
    return tuple(
        records.LineageRow.model_validate(
            _uuids(row, "id", "artifact_id", "parent_version_id", "created_by_invocation_id")
        )
        for row in rows
    )


def revalidate(
    connection: sqlite3.Connection, original: records.AssociationSnapshot
) -> tuple[records.LineageFacts, records.LineageFacts, str]:
    """Revalidate the full registered dependency closure, not just a selected UUID/hash."""
    invocation = _one(
        connection,
        "SELECT i.id,i.workflow_run_id,i.specialist_role,i.provider,i.model_identifier,"
        "i.status,i.schema_validation_succeeded,i.request_settings,i.prompt_sha256,i.prompt_text,"
        "r.project_id,r.workflow_name,r.graph_version,"
        "json_extract(r.input_state,'$.execution_kind') AS execution_kind,"
        "json_extract(r.input_state,'$.production_prompt_template_version') AS run_prompt_version "
        "FROM agent_invocations i JOIN workflow_runs r ON r.id=i.workflow_run_id WHERE i.id=?",
        original.invocation.id,
    )
    _uuids(invocation, "id", "workflow_run_id", "project_id")
    active_secret_guard().ensure_safe(invocation, destination="association current invocation")
    invocation["request_settings"] = strict_object(invocation["request_settings"])
    _require(records.InvocationRow.model_validate(invocation) == original.invocation)
    outputs = _rows(
        connection,
        "SELECT v.id FROM artifact_versions v JOIN artifacts a ON a.id=v.artifact_id "
        "WHERE v.created_by_invocation_id=? AND a.artifact_type='critique' ORDER BY v.id",
        original.invocation.id,
        64,
    )
    _require([str(UUID(row["id"])) for row in outputs] == list(original.review_outputs))
    links = _rows(
        connection,
        "SELECT artifact_version_id FROM agent_invocation_inputs "
        "WHERE agent_invocation_id=? ORDER BY artifact_version_id",
        original.invocation.id,
        128,
    )
    _require(
        sorted(str(UUID(row["artifact_version_id"])) for row in links)
        == sorted(original.input_link_ids)
    )
    current = [artifact(connection, row.id) for row in (original.review, *original.inputs)]
    for row, old in zip(current, (original.review, *original.inputs), strict=True):
        # SQL JSON serialization is not semantic identity; canonical content is rehashed.
        _require(
            row.model_dump(exclude={"stored_content_bytes_sha256"})
            == old.model_dump(exclude={"stored_content_bytes_sha256"})
        )
    creator = _one(
        connection,
        "SELECT i.id,i.workflow_run_id,i.specialist_role,i.status,r.project_id "
        "FROM agent_invocations i JOIN workflow_runs r ON r.id=i.workflow_run_id WHERE i.id=?",
        original.draft_creator.id,
    )
    _require(
        records.CreatorRow.model_validate(_uuids(creator, "id", "workflow_run_id", "project_id"))
        == original.draft_creator
    )
    draft = next(
        row for row in current if row.id == original.review.content["target_artifact_version_id"]
    )
    review_history = lineage(connection, original.review.artifact_id)
    draft_history = lineage(connection, draft.artifact_id)
    for history, old_history in (
        (review_history, original.review_lineage),
        (draft_history, original.draft_lineage),
    ):
        _require(all(row in history for row in old_history))
    facts = (
        records._lineage(review_history, current[0]),
        records._lineage(draft_history, draft),
    )
    digest = canonical_sha256(
        {
            "invocation": invocation,
            "review_outputs": outputs,
            "input_links": links,
            "artifacts": [r.model_dump(mode="json") for r in current],
            "draft_creator": creator,
            "review_lineage": [r.model_dump(mode="json") for r in review_history],
            "draft_lineage": [r.model_dump(mode="json") for r in draft_history],
        }
    )
    return (*facts, digest)
