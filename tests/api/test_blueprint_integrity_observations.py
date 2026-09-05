"""Production records uncertain Blueprint names once without changing approval."""

from pathlib import Path
from typing import cast
from uuid import uuid4

from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import (
    AgentInvocation,
    Artifact,
    ArtifactStatus,
    ArtifactVersion,
    InvocationStatus,
    Project,
    RunStatus,
    WorkflowEvent,
    WorkflowRun,
)
from open_hollywood_api.services.production_workflow import SceneProductionService
from open_hollywood_engine.artifacts import ArtifactKind
from open_hollywood_engine.evaluations import canonical_sha256
from open_hollywood_engine.models import (
    MODEL_PRESETS,
    ModelDeployment,
    ModelProfileMode,
    ModelSelection,
)
from open_hollywood_engine.workflows import ArtifactReference, SceneProductionExecutor
from sqlalchemy import Engine, select

from tests.artifacts.test_blueprint_integrity import _with_place_description


def test_handoff_records_advisory_name_observation_once_with_exact_lineage(
    database_engine: Engine, migrated_database_path: Path
) -> None:
    session_factory = create_session_factory(database_engine)
    blueprint = _with_place_description(
        "She moved into the Hawthorne building.", "The Hallways of Blackwood Tower"
    )
    frozen_content = blueprint.model_dump(mode="json")
    configuration = (
        MODEL_PRESETS[ModelProfileMode.LOCAL]
        .configuration(
            local_model=ModelSelection(
                provider="ollama",
                model_identifier="offline-fixture",
                deployment=ModelDeployment.LOCAL,
            )
        )
        .to_data()
    )
    project_id, run_id, version_id = uuid4(), uuid4(), uuid4()
    with session_factory.begin() as session:
        project = Project(id=project_id, name="Building name observation")
        run = WorkflowRun(
            id=run_id,
            project=project,
            workflow_name="story_blueprint",
            graph_version="3",
            status=RunStatus.SUCCEEDED,
            input_state={
                "model_profile_id": str(uuid4()),
                "model_profile_configuration": configuration,
                "model_profile_configuration_sha256": canonical_sha256(configuration),
                "run_seed": 1,
                "benchmark_constraints": {},
            },
        )
        invocation = AgentInvocation(
            workflow_run=run,
            specialist_role="blueprint_integrator",
            provider="fixture",
            model_identifier="offline-fixture",
            status=InvocationStatus.SUCCEEDED,
            request_settings={},
            prompt_sha256="0" * 64,
        )
        artifact = Artifact(
            project=project,
            artifact_key="story_blueprint",
            artifact_type="story_blueprint",
            title="Approved Blueprint",
            status=ArtifactStatus.APPROVED,
        )
        version = ArtifactVersion(
            id=version_id,
            artifact=artifact,
            created_by_invocation=invocation,
            version_number=1,
            schema_version="1",
            content=frozen_content,
            content_sha256=canonical_sha256(frozen_content),
        )
        session.add_all((project, run, invocation, artifact, version))
        for character in blueprint.characters:
            character_content = character.model_dump(mode="json")
            session.add(
                ArtifactVersion(
                    artifact=Artifact(
                        project=project,
                        artifact_key=f"character_{character.id}",
                        artifact_type="character",
                        title=character.name,
                        status=ArtifactStatus.APPROVED,
                    ),
                    version_number=1,
                    schema_version="1",
                    content=character_content,
                    content_sha256=canonical_sha256(character_content),
                )
            )
    reference = ArtifactReference(
        kind=ArtifactKind.STORY_BLUEPRINT,
        artifact_key="story_blueprint",
        version_id=version_id,
        schema_version="1",
    )
    service = SceneProductionService(
        database_path=migrated_database_path,
        session_factory=session_factory,
        executor=cast(SceneProductionExecutor, object()),
    )

    production = service._materialize_handoff(run_id, reference)
    replay = service._materialize_handoff(run_id, reference)

    assert production == replay
    with session_factory() as session:
        events = session.scalars(
            select(WorkflowEvent).where(
                WorkflowEvent.workflow_run_id == production.workflow_run_id,
                WorkflowEvent.event_type == "workflow.blueprint.integrity_observed",
            )
        ).all()
        approved_version = session.get(ArtifactVersion, version_id)
        production_run = session.get(WorkflowRun, production.workflow_run_id)
        assert approved_version is not None
        assert production_run is not None
        assert approved_version.content == frozen_content
        assert approved_version.artifact.status is ArtifactStatus.APPROVED
        assert production_run.status is RunStatus.PENDING
    assert len(events) == 1
    assert events[0].payload["approved_blueprint_version_id"] == str(version_id)
    assert events[0].payload["observations"][0]["blocks_production"] is False
    assert events[0].payload["observations"][0]["observed_name"] == "Hawthorne building"
