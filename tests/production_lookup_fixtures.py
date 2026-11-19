"""Disposable SQLite workspaces from authored association snapshots; no production data."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from open_hollywood_api.persistence.database import sqlite_url
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactVersion,
    Base,
    InvocationStatus,
    Project,
    WorkflowRun,
    agent_invocation_inputs,
)
from open_hollywood_api.services import production_association_export as archive
from open_hollywood_api.services import production_association_lookup as lookup
from open_hollywood_api.services import production_association_records as records
from open_hollywood_engine.evaluations.assessment_completion import encoded
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session

from tests.production_association_fixtures import archive as fixture_archive
from tests.production_association_fixtures import reseal


def workspace(root: Path) -> tuple[archive._Registration, lookup._Workspace]:
    registration = fixture_archive(root)
    engine = create_engine(sqlite_url(registration.database))
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        for case in archive.CASES:
            value = json.loads((registration.archive / f"{case}.snapshot.json").read_bytes())
            for history in (value["review_lineage"], value["draft_lineage"]):
                for head in history[1:]:
                    head["created_by_invocation_id"] = None
            (registration.archive / f"{case}.snapshot.json").write_bytes(encoded(value))
            invocation = value["invocation"]
            project = Project(id=UUID(invocation["project_id"]), name="Fixture")
            run = WorkflowRun(
                id=UUID(invocation["workflow_run_id"]),
                project=project,
                workflow_name="scene_production",
                graph_version="9",
                input_state={"execution_kind": invocation["execution_kind"]},
            )
            critic = AgentInvocation(
                id=UUID(invocation["id"]),
                workflow_run=run,
                specialist_role="scene_critic",
                provider=invocation["provider"],
                model_identifier=invocation["model_identifier"],
                status=InvocationStatus.SUCCEEDED,
                request_settings=invocation["request_settings"],
                prompt_sha256=invocation["prompt_sha256"],
                prompt_text=invocation["prompt_text"],
                schema_validation_succeeded=True,
            )
            writer = AgentInvocation(
                id=UUID(value["draft_creator"]["id"]),
                workflow_run=run,
                specialist_role="scene_writer",
                provider="fixture",
                model_identifier="fixture",
                status=InvocationStatus.SUCCEEDED,
                prompt_sha256="0" * 64,
            )
            session.add_all((project, run, critic, writer))
            session.flush()
            for item in (value["review"], *value["inputs"]):
                logical = Artifact(
                    id=UUID(item["artifact_id"]),
                    project=project,
                    artifact_type=item["artifact_type"],
                    artifact_key=item["artifact_key"],
                    title="Fixture",
                )
                version = ArtifactVersion(
                    id=UUID(item["id"]),
                    artifact=logical,
                    version_number=1,
                    schema_version="1",
                    content=item["content"],
                    content_sha256=item["content_sha256"],
                    created_by_invocation_id=UUID(item["created_by_invocation_id"]),
                )
                session.add_all((logical, version))
                session.flush()
                history = (
                    value["review_lineage"]
                    if item is value["review"]
                    else (value["draft_lineage"] if item["artifact_type"] == "scene_draft" else [])
                )
                for head in history[1:]:
                    session.add(
                        ArtifactVersion(
                            id=UUID(head["id"]),
                            artifact=logical,
                            version_number=head["version_number"],
                            schema_version="1",
                            content=item["content"],
                            content_sha256=head["content_sha256"],
                            parent_version_id=UUID(head["parent_version_id"]),
                            created_by_invocation_id=None,
                        )
                    )
            session.flush()
            session.execute(
                insert(agent_invocation_inputs),
                [
                    {"agent_invocation_id": critic.id, "artifact_version_id": UUID(v)}
                    for v in value["input_link_ids"]
                ],
            )
        session.commit()
    engine.dispose()
    stat = registration.database.stat()
    return reseal(registration), lookup._Workspace(
        "test-workspace",
        registration.database,
        stat.st_dev,
        stat.st_ino,
        registration.name,
    )


def selections(registration: archive._Registration) -> tuple[records.ArtifactSelection, ...]:
    result = []
    for case in archive.CASES:
        value = json.loads((registration.archive / f"{case}.snapshot.json").read_bytes())
        for role, item in (
            ("original_review", value["review"]),
            ("reviewed_draft", value["inputs"][0]),
        ):
            result.append(
                records.ArtifactSelection.model_validate(
                    {
                        "role": role,
                        "project_id": item["project_id"],
                        "artifact_id": item["artifact_id"],
                        "version_id": item["id"],
                        "content_sha256": item["content_sha256"],
                    }
                )
            )
    return tuple(result)
