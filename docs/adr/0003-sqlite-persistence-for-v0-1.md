# ADR 0003: SQLite persistence for v0.1

- Status: Accepted
- Date: 2026-07-13

## Context

The prototype lost state on restart. The rewrite needs durable projects,
workflow checkpoints, messages, artifacts, invocations, budgets, and evaluation
results without requiring a database server on a user's PC.

## Decision

Use SQLite as the v0.1 source of truth, accessed through SQLAlchemy and migrated
with Alembic. Use the durable SQLite LangGraph checkpointer for workflow state.

Keep persistence interfaces and SQL usage compatible with a later PostgreSQL
deployment, but do not implement PostgreSQL or dual-database support in v0.1.

## Consequences

- Local setup remains zero-configuration.
- One worker owns write-heavy workflow execution to avoid unnecessary SQLite
  contention.
- Migrations are required for every persisted schema change.
- Hosted concurrency is deferred until the product warrants it.
