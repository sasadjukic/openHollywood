"""Durable workflow event store integration tests."""

from uuid import uuid4

import pytest
from open_hollywood_api.persistence.database import create_session_factory
from open_hollywood_api.persistence.models import WorkflowEvent
from open_hollywood_api.services.workflow_events import (
    WorkflowEventStore,
    WorkflowRunNotFoundError,
)
from sqlalchemy import Engine, delete, select, update
from sqlalchemy.exc import IntegrityError

from tests.factories import persist_workflow_run


def test_events_have_global_ids_and_replay_excludes_the_cursor(database_engine: Engine) -> None:
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        first_run = persist_workflow_run(session, name="first")
        second_run = persist_workflow_run(session, name="second")
        first_run_id = first_run.id
        second_run_id = second_run.id

    store = WorkflowEventStore(session_factory)
    first = store.append(first_run_id, "run.started", {"node": "intake"}, source="worker")
    other_run = store.append(second_run_id, "run.started", {}, source="worker")
    third = store.append(
        first_run_id,
        "node.completed",
        {"node": "intake"},
        source="intake",
    )

    assert first.id < other_run.id < third.id
    assert first.occurred_at.tzinfo is not None
    assert store.list_after(first_run_id, first.id, limit=10) == [third]
    assert store.list_after(first_run_id, third.id, limit=10) == []


def test_replay_pages_report_the_next_exclusive_cursor(database_engine: Engine) -> None:
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        workflow_run_id = persist_workflow_run(session).id

    store = WorkflowEventStore(session_factory)
    first = store.append(workflow_run_id, "run.started", {})
    second = store.append(workflow_run_id, "node.started", {"node": "brief"})
    third = store.append(workflow_run_id, "node.completed", {"node": "brief"})

    first_page = store.page_after(workflow_run_id, first.id, limit=1)
    second_page = store.page_after(workflow_run_id, first_page.next_after, limit=1)

    assert first_page.events == [second]
    assert first_page.next_after == second.id
    assert first_page.has_more is True
    assert second_page.events == [third]
    assert second_page.next_after == third.id
    assert second_page.has_more is False


def test_append_validates_run_and_event_type(database_engine: Engine) -> None:
    store = WorkflowEventStore(create_session_factory(database_engine))

    with pytest.raises(WorkflowRunNotFoundError):
        store.append(uuid4(), "run.started", {})

    with pytest.raises(ValueError, match="event_type"):
        store.append(uuid4(), "Run Started\nmalicious", {})


def test_database_triggers_reject_event_updates_and_deletes(database_engine: Engine) -> None:
    session_factory = create_session_factory(database_engine)
    with session_factory() as session:
        workflow_run_id = persist_workflow_run(session).id
    event = WorkflowEventStore(session_factory).append(workflow_run_id, "run.started", {})

    with pytest.raises(IntegrityError, match="append-only"), database_engine.begin() as connection:
        connection.execute(
            update(WorkflowEvent)
            .where(WorkflowEvent.id == event.id)
            .values(payload={"overwritten": True})
        )

    with pytest.raises(IntegrityError, match="append-only"), database_engine.begin() as connection:
        connection.execute(delete(WorkflowEvent).where(WorkflowEvent.id == event.id))

    with database_engine.connect() as connection:
        stored = connection.execute(
            select(WorkflowEvent.payload).where(WorkflowEvent.id == event.id)
        ).scalar_one()
    assert stored == {}
