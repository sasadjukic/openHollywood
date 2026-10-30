"""Offline read-only SQLite adapter and immutable operator export; no gateway imports."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Literal, cast
from uuid import UUID

from open_hollywood_engine.evaluations import review_evidence as domain
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import (
    ArtifactSource,
    EvidenceError,
    Identifier,
    InvocationIdentity,
    JsonObject,
    Reason,
    Record,
    ReviewEvidenceExport,
    ReviewExportEntry,
    ReviewSnapshot,
    object_value,
    project_review,
    recover_messages,
    require,
    strict_object,
    string_value,
)
from open_hollywood_engine.secrets import SecretLeakError
from pydantic import JsonValue, ValidationError

from open_hollywood_api.persistence.secret_policy import active_secret_guard


@contextmanager
def readonly_connection(database: Path) -> Iterator[sqlite3.Connection]:
    """Never use the normal engine: it creates paths and configures journal mode."""
    path = database.resolve(strict=True)
    require(path.is_file(), "database_unavailable")
    connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, isolation_level=None)
    try:
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        yield connection
    finally:
        connection.close()  # Ends the read transaction, including exceptional exits.


class ReviewInventoryRow(Record):
    invocation_id: Identifier
    workflow_run_id: Identifier
    status: str
    prompt_version: str | None
    graph_version: str | None
    audit_schema: str | None
    candidate: bool


class ReviewInventory(Record):
    schema_version: Literal["1"] = "1"
    database_path: str
    rows: tuple[ReviewInventoryRow, ...]
    candidates_are_metadata_only: Literal[True] = True
    live_calls: Literal[0] = 0


def inventory(database: Path) -> ReviewInventory:
    """Read metadata only. Candidate is not yet a successful source validation."""
    with readonly_connection(database) as connection:
        rows = connection.execute(
            "SELECT i.id, i.workflow_run_id, i.status, i.schema_validation_succeeded, "
            "json_extract(i.request_settings, '$.operation') AS operation, "
            "json_extract(i.request_settings, '$.prompt_template_version') AS prompt_version, "
            "json_extract(i.request_settings, '$.graph_version') AS graph_version, "
            "r.graph_version AS run_graph_version, "
            "json_extract(r.input_state, '$.production_prompt_template_version') "
            "AS run_prompt_version, "
            "json_extract(i.request_settings, '$.scene_boundary_audit.schema_version') "
            "AS audit_schema "
            "FROM agent_invocations i JOIN workflow_runs r ON r.id=i.workflow_run_id "
            "WHERE i.specialist_role='scene_critic' AND r.workflow_name='scene_production' "
            "ORDER BY i.id"
        ).fetchall()
    result = ReviewInventory(
        database_path=str(database.resolve()),
        rows=tuple(
            ReviewInventoryRow(
                invocation_id=str(UUID(row["id"])),
                workflow_run_id=str(UUID(row["workflow_run_id"])),
                status=row["status"],
                prompt_version=row["prompt_version"]
                if isinstance(row["prompt_version"], str)
                else None,
                graph_version=row["graph_version"]
                if isinstance(row["graph_version"], str)
                else None,
                audit_schema=row["audit_schema"] if isinstance(row["audit_schema"], str) else None,
                candidate=(
                    row["status"] == "SUCCEEDED"
                    and row["schema_validation_succeeded"] == 1
                    and row["operation"] == "critique"
                    and row["prompt_version"] == "61"
                    and row["graph_version"] == "9"
                    and row["run_graph_version"] == "9"
                    and row["run_prompt_version"] == "61"
                    and row["audit_schema"] == "7"
                ),
            )
            for row in rows
        ),
    )
    active_secret_guard().ensure_safe(
        result.model_dump(mode="json"), destination="review inventory"
    )
    return result


def _source(row: sqlite3.Row) -> ArtifactSource:
    content = strict_object(row["content"])
    active_secret_guard().ensure_safe(content, destination="review export source")
    return ArtifactSource(
        version_id=str(UUID(row["id"])),
        project_id=str(UUID(row["project_id"])),
        artifact_kind=row["artifact_type"],
        artifact_key=row["artifact_key"],
        content_sha256=row["content_sha256"],
        content=content,
    )


def _snapshot(
    connection: sqlite3.Connection, row: sqlite3.Row, settings: JsonObject, critique: ArtifactSource
) -> ReviewSnapshot:
    rows = connection.execute(
        "SELECT v.id, a.project_id, a.artifact_type, a.artifact_key, v.content, v.content_sha256 "
        "FROM agent_invocation_inputs x "
        "LEFT JOIN artifact_versions v ON v.id=x.artifact_version_id "
        "LEFT JOIN artifacts a ON a.id=v.artifact_id "
        "WHERE x.agent_invocation_id=? ORDER BY x.artifact_version_id",
        (row["id"],),
    ).fetchall()
    require(
        all(r["id"] is not None and r["project_id"] is not None for r in rows), "missing_source"
    )
    sources = tuple(_source(r) for r in rows)
    assert critique.content is not None
    draft_id = string_value(critique.content.get("target_artifact_version_id"))
    drafts = [s for s in sources if s.version_id == draft_id]
    require(len(drafts) == 1 and drafts[0].content is not None, "missing_source")
    content = drafts[0].content
    assert content is not None
    scene = string_value(content.get("scene_id"))
    plans = [
        s
        for s in sources
        if s.artifact_kind == "scene_plan"
        and s.content is not None
        and s.content.get("id") == scene
    ]
    require(len(plans) == 1, "missing_source")
    attempt = settings.get("attempt_number")
    require(type(attempt) is int, "malformed_source")
    assert isinstance(attempt, int)
    return ReviewSnapshot(
        invocation=InvocationIdentity(
            invocation_id=str(UUID(row["id"])),
            workflow_run_id=str(UUID(row["workflow_run_id"])),
            project_id=str(UUID(row["project_id"])),
            attempt=attempt,
            task_fingerprint=string_value(settings.get("task_fingerprint")),
            prompt_sha256=row["prompt_sha256"],
            response_sha256=string_value(settings.get("provider_response_content_sha256")),
        ),
        critique=critique,
        draft_version_id=draft_id,
        plan_version_id=plans[0].version_id,
        scene_id=scene,
        sources=sources,
        messages=recover_messages(row["prompt_text"], row["prompt_sha256"]),
        native_audit=object_value(settings.get("scene_boundary_audit")),
    )


def load_entry(connection: sqlite3.Connection, invocation_id: UUID) -> ReviewExportEntry:
    """Preserve a safe original review even when comparison eligibility fails."""
    identity = str(invocation_id)
    original: ArtifactSource | None = None
    audit: JsonValue = None
    try:
        row = connection.execute(
            "SELECT i.*, r.project_id, r.workflow_name, r.graph_version AS run_graph_version, "
            "r.input_state AS run_input_state FROM agent_invocations i "
            "LEFT JOIN workflow_runs r ON r.id=i.workflow_run_id WHERE i.id=?",
            (invocation_id.hex,),
        ).fetchone()
        require(row is not None, "not_found")
        assert row is not None
        settings = strict_object(row["request_settings"])
        active_secret_guard().ensure_safe(settings, destination="saved review settings")
        active_secret_guard().ensure_safe(row["prompt_text"], destination="saved review prompt")
        outputs = connection.execute(
            "SELECT v.id, a.project_id, a.artifact_type, a.artifact_key, "
            "v.content, v.content_sha256 "
            "FROM artifact_versions v JOIN artifacts a ON a.id=v.artifact_id "
            "WHERE v.created_by_invocation_id=? AND a.artifact_type='critique' ORDER BY v.id",
            (invocation_id.hex,),
        ).fetchall()
        if len(outputs) == 1:
            candidate = _source(outputs[0])
            require(candidate.project_id == str(UUID(row["project_id"])))
            original = candidate
        audit = settings.get("scene_boundary_audit")
        require(
            row["status"] == "SUCCEEDED"
            and row["schema_validation_succeeded"] == 1
            and row["specialist_role"] == "scene_critic"
            and row["workflow_name"] == "scene_production"
            and settings.get("operation") == "critique",
            "not_successful_ordinary_critic",
        )
        require(
            settings.get("prompt_template_version") == "61"
            and settings.get("graph_version") == "9"
            and isinstance(audit, dict)
            and audit.get("schema_version") == "7",
            "unsupported_contract",
        )
        run_state = strict_object(row["run_input_state"])
        require(
            row["run_graph_version"] == "9"
            and run_state.get("production_prompt_template_version") == "61",
            "unsupported_contract",
        )
        require(len(outputs) == 1 and original is not None, "missing_source")
        assert original is not None
        snapshot = _snapshot(connection, row, settings, original)
        evidence = project_review(snapshot)
        return ReviewExportEntry(
            invocation_id=identity,
            reason="compatible",
            original_critique=original,
            original_native_audit=audit,
            snapshot=snapshot,
            snapshot_sha256=canonical_sha256(snapshot.model_dump(mode="json")),
            evidence=evidence,
        )
    except SecretLeakError:
        raise
    except EvidenceError as exc:
        reason = cast(Reason, str(exc))
    except (ValidationError, ValueError, TypeError, KeyError):
        reason = "malformed_source"
    return ReviewExportEntry(
        invocation_id=identity,
        reason=reason,
        original_critique=original,
        original_native_audit=audit,
    )


def collect_export(database: Path, invocation_ids: tuple[UUID, ...]) -> ReviewEvidenceExport:
    require(
        1 <= len(invocation_ids) <= 12 and len(set(invocation_ids)) == len(invocation_ids),
        "invalid_selection",
    )
    with readonly_connection(database) as connection:
        entries = tuple(load_entry(connection, value) for value in invocation_ids)
        require(connection.total_changes == 0)
    result = ReviewEvidenceExport(
        database_path=str(database.resolve()),
        invocation_ids=tuple(str(i) for i in invocation_ids),
        entries=entries,
        replayer_sha256=hashlib.sha256(Path(domain.__file__).read_bytes()).hexdigest(),
    )
    active_secret_guard().ensure_safe(
        result.model_dump(mode="json"), destination="review evidence export"
    )
    return result


def _quoted(text: str) -> str:
    # Literal source data: embedded Markdown, HTML and fences must not become active markup.
    import re

    fence = "`" * max(3, 1 + max((len(m.group(0)) for m in re.finditer(r"`+", text)), default=0))
    return fence + "\n" + text + "\n" + fence


def render_export(export: ReviewEvidenceExport) -> str:
    lines = [
        "# Saved review evidence",
        "",
        "Application-computed text comparisons. "
        "Selected spans only; semantic judgments are unchanged. No writer action is authorized.",
        "",
    ]
    for entry in export.entries:
        lines += [
            "## Invocation " + entry.invocation_id,
            "",
            "Export result: **" + entry.reason + "**.",
            "",
        ]
        if entry.original_critique is not None:
            lines += [
                "### Original saved critique",
                "",
                "Version: `" + entry.original_critique.version_id + "`.",
                "",
                _quoted(json.dumps(entry.original_critique.content, ensure_ascii=False, indent=2)),
                "",
            ]
        if entry.original_native_audit is not None:
            lines += [
                "### Original saved native audit",
                "",
                _quoted(json.dumps(entry.original_native_audit, ensure_ascii=False, indent=2)),
                "",
            ]
        for requirement in entry.evidence:
            lines += [
                "### Application text comparison: " + requirement.anchor,
                "",
                "Saved critic status: **" + requirement.original_check.status + "**.",
                "",
                _quoted(requirement.original_check.assessment),
                "",
            ]
            for comparison in requirement.comparisons:
                lines += [comparison.statement, ""]
                for label, span in (
                    ("Assigned requirement", comparison.left),
                    ("Selected draft excerpt", comparison.right),
                ):
                    lines += [
                        label
                        + ": `"
                        + span.version_id
                        + "` "
                        + span.field_pointer
                        + f" `[{span.start},{span.end})` — {span.visibility}.",
                        "",
                        "Handle: `" + (span.evidence_ref or "none") + "`.",
                        "",
                        _quoted(span.quote) if span.quote is not None else "Source unavailable.",
                        "",
                    ]
        lines += ["Original/revision correspondence: unresolved; no pairing was selected.", ""]
    return "\n".join(lines)


def write_export(destination: Path, export: ReviewEvidenceExport) -> Literal["created", "reused"]:
    """Publish complete bytes once; an identical repeat verifies without any write."""
    body = export.model_dump(mode="json")
    guard = active_secret_guard()
    guard.ensure_safe(body, destination="review export")
    for entry in export.entries:
        if entry.reason == "compatible":
            require(entry.snapshot is not None)
            assert entry.snapshot is not None
            require(
                entry.original_critique == entry.snapshot.critique
                and entry.original_native_audit == entry.snapshot.native_audit
                and entry.snapshot_sha256
                == canonical_sha256(entry.snapshot.model_dump(mode="json"))
                and entry.evidence == project_review(entry.snapshot)
            )
        else:
            require(entry.snapshot is None and entry.snapshot_sha256 is None and not entry.evidence)
    encoded = (json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    markdown = render_export(export).encode("utf-8")
    guard.ensure_safe(markdown.decode("utf-8"), destination="review export Markdown")
    require(len(encoded) + len(markdown) <= 32 * 1024 * 1024, "export_too_large")
    files = {"review-evidence.json": encoded, "review-evidence.md": markdown}
    manifest = {
        "schema_version": "1",
        "invocation_ids": body["invocation_ids"],
        "files_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
        "export_sha256": canonical_sha256(body),
        "live_calls": 0,
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if destination.exists():
        require(destination.is_dir() and not destination.is_symlink(), "export_conflict")
        require({p.name for p in destination.iterdir()} == set(files), "export_conflict")
        require(
            all(
                not (destination / n).is_symlink()
                and (destination / n).is_file()
                and (destination / n).read_bytes() == data
                for n, data in files.items()
            ),
            "export_conflict",
        )
        return "reused"
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():  # Manifest last: partial directories never count as complete.
        with (destination / name).open("xb") as stream:
            stream.write(data)
    return "created"
