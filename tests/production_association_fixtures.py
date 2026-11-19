"""Authored v33 identity snapshots, unrelated to private production data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from open_hollywood_api.services import assessment_completion as storage
from open_hollywood_api.services import production_association_export as exporter
from open_hollywood_api.services import production_association_records as records
from open_hollywood_engine.evaluations.assessment_completion import encoded
from open_hollywood_engine.evaluations.contracts import canonical_sha256
from open_hollywood_engine.evaluations.review_evidence import SavedMessage, messages_hash


def uid(number: int) -> str:
    return str(UUID(int=number))


def prompt(snapshot: dict[str, Any], payload: dict[str, Any]) -> None:
    messages = (
        SavedMessage(role="system", content="Authored fixture only.\n\nNo model call."),
        SavedMessage(role="user", content=json.dumps(payload)),
    )
    snapshot["invocation"]["prompt_text"] = "\n\n".join(m.content for m in messages)
    snapshot["invocation"]["prompt_sha256"] = messages_hash(messages)


def payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    text = snapshot["invocation"]["prompt_text"]
    return json.loads(text[text.index('{"assignment"') :])  # type: ignore[no-any-return]


def capture(number: int = 1, *, historical: bool = False) -> dict[str, Any]:
    base = 100 * number
    project, run, critic, writer, scene = (uid(base + n) for n in range(1, 6))

    def artifact(offset: int, kind: str, content: dict[str, Any], creator: str) -> dict[str, Any]:
        return {
            "id": uid(base + offset),
            "artifact_id": uid(base + offset + 20),
            "parent_version_id": None,
            "created_by_invocation_id": creator,
            "version_number": 1,
            "schema_version": "1",
            "project_id": project,
            "artifact_type": kind,
            "artifact_key": f"{kind}:{scene}",
            "content": content,
            "content_sha256": canonical_sha256(content),
            "stored_content_bytes_sha256": "a" * 64,
        }

    draft = artifact(10, "scene_draft", {"scene_id": scene, "prose": "Echo.\n\nEcho."}, writer)
    plan = artifact(11, "scene_plan", {"id": scene, "summary": "A repeated call."}, writer)
    review = artifact(
        12, "critique", {"target_artifact_version_id": draft["id"], "summary": "Fixture"}, critic
    )

    def lineage(item: dict[str, Any]) -> list[dict[str, Any]]:
        row = {
            k: item[k]
            for k in (
                "id",
                "artifact_id",
                "parent_version_id",
                "created_by_invocation_id",
                "version_number",
                "content_sha256",
            )
        }
        result = [row]
        if historical:
            result.append(
                {
                    **row,
                    "id": uid(int(UUID(item["id"])) + 40),
                    "parent_version_id": row["id"],
                    "version_number": 2,
                }
            )
        return result

    result = {
        "contract": "private-production-association-snapshot-1",
        "origin": "saved_production_review_identity_audit_not_assessment_delivery",
        "database_sha256": "b" * 64,
        "invocation": {
            "id": critic,
            "workflow_run_id": run,
            "project_id": project,
            "specialist_role": "scene_critic",
            "provider": "fixture",
            "model_identifier": "fixture",
            "status": "SUCCEEDED",
            "schema_validation_succeeded": 1,
            "request_settings": {
                "operation": "critique",
                "prompt_template_version": "33",
                "graph_version": "9",
            },
            "prompt_sha256": "c" * 64,
            "prompt_text": "replaced below",
            "workflow_name": "scene_production",
            "graph_version": "9",
            "execution_kind": "production",
            "run_prompt_version": None,
        },
        "review_outputs": [review["id"]],
        "review": review,
        "input_link_ids": [draft["id"], plan["id"]],
        "inputs": [draft, plan],
        "draft_creator": {
            "id": writer,
            "workflow_run_id": run,
            "project_id": project,
            "specialist_role": "scene_writer",
            "status": "SUCCEEDED",
        },
        "review_lineage": lineage(review),
        "draft_lineage": lineage(draft),
        "existing_intake_reason": "unsupported_contract",
    }
    prompt(
        result,
        {
            "assignment": {"unit_id": scene},
            "input_artifacts": [
                {
                    "artifact_version_id": item["id"],
                    "artifact_kind": item["artifact_type"],
                    "artifact_key": item["artifact_key"],
                    "content": item["content"],
                }
                if item is plan
                else {
                    "artifact_version_id": draft["id"],
                    "artifact_kind": "scene_draft",
                    "artifact_key": draft["artifact_key"],
                    "content": {
                        "scene_id": scene,
                        "evidence_catalog": [
                            {"evidence_ref": "P1", "exact_excerpt": "Echo."},
                            {"evidence_ref": "P2", "exact_excerpt": "Echo."},
                        ],
                    },
                }
                for item in (draft, plan)
            ],
        },
    )
    return result


def expectation(value: dict[str, Any]) -> records.ExpectedReview:
    return records.ExpectedReview(
        database_snapshot_sha256=value["database_sha256"],
        invocation_id=value["invocation"]["id"],
        workflow_run_id=value["invocation"]["workflow_run_id"],
        project_id=value["invocation"]["project_id"],
        critique_artifact_id=value["review"]["artifact_id"],
        critique_version_id=value["review"]["id"],
        draft_version_id=value["inputs"][0]["id"],
    )


def record(value: dict[str, Any]) -> records.AssociationRecord:
    return records.AssociationRecord(
        source=records.SourceAuthentication(
            registration="test-only ``` [link](https://invalid.example)",
            archive_seal_bytes_sha256="d" * 64,
            snapshot_member="R01.snapshot.json",
            snapshot_bytes_sha256=storage._sha(encoded(value)),
        ),
        evidence=records.validate_snapshot(
            records.AssociationSnapshot.model_validate_json(encoded(value)), expectation(value)
        ),
    )


def archive(root: Path) -> exporter._Registration:
    directory = root / "source"
    directory.mkdir()
    database = root / "private.db"
    # Deliberately absent: the exporter must not need or open a current database.
    rows = []
    for index, case in enumerate(exporter.CASES, start=1):
        value = capture(index, historical=index in (3, 5))
        (directory / f"{case}.snapshot.json").write_bytes(encoded(value))
        selected = expectation(value).model_dump(mode="json")
        del selected["database_snapshot_sha256"]
        rows.append(selected)
    (directory / "selection.json").write_bytes(encoded({"maximum_reviews": 6, "reviews": rows}))
    (directory / "database-before.json").write_bytes(encoded({str(database): {"sha256": "b" * 64}}))
    (directory / "private-audit.py").write_bytes(b"raise RuntimeError('must never execute')")
    (directory / "source-snapshot").mkdir()
    (directory / "source-snapshot/readme.md").write_bytes(b"source context, not exported")
    return reseal(exporter._Registration("test-only", directory, "", database))


def reseal(registration: exporter._Registration) -> exporter._Registration:
    from dataclasses import replace

    files = {
        p.relative_to(registration.archive).as_posix(): storage._sha(p.read_bytes())
        for p in registration.archive.rglob("*")
        if p.is_file() and p.name != "acceptance-seal.json"
    }
    seal = encoded(
        {"contract": "production-association-acceptance-seal-1", "members_sha256": files}
    )
    (registration.archive / "acceptance-seal.json").write_bytes(seal)
    return replace(registration, seal_sha256=storage._sha(seal))
