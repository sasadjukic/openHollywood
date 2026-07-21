"""Small persistence factories shared across integration tests."""

from open_hollywood_api.persistence.models import Project, RunStatus, WorkflowRun
from sqlalchemy.orm import Session


def persist_workflow_run(session: Session, *, name: str = "story_blueprint") -> WorkflowRun:
    """Create a minimal project and workflow run and commit their IDs."""
    project = Project(name=f"Project for {name}")
    workflow_run = WorkflowRun(
        project=project,
        workflow_name=name,
        graph_version="1",
        status=RunStatus.RUNNING,
    )
    session.add(project)
    session.commit()
    return workflow_run
