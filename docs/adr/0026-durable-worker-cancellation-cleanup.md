# ADR 0026: Join specialist cleanup before closing a workflow

- Status: Accepted
- Date: 2026-10-09
- Refines: ADR 0002's workflow lifecycle and ADR 0003's SQLite concurrency.

## Context

The final v41 Python suite repeatedly found an invocation still marked RUNNING
after worker shutdown. Delaying the cancellation database write locally exposed
the ordering: the graph wrapper returned cancellation, worker stop returned, and
the specialist's persistence task was still running. Further cancellation could
interrupt its caller while the database thread continued. Awaiting the graph
wrapper alone did not join the actual specialist task.

A later full run exposed a distinct `database is locked` failure while recording
an operator stop. The synchronous control write could block the event loop while
waiting for a checkpoint transaction whose commit needed that same loop. A
controlled real SQLite transaction reproduces the stop-command failure.

## Decision

Track the application-owned specialist tasks in a context-local scope for each
Blueprint or production graph invocation. Both profile-routed executors register
their actual task for the duration of an invocation. On graph failure or
cancellation, cancel any remaining uncancelled specialist tasks and join their
completion before propagating the failure or closing the workflow service.
Concurrent graph calls have separate scopes.

Protect each executor's cancellation-persistence operation with a strongly held,
shielded task and continue awaiting it across repeated cancellation. Propagate
the original cancellation after persistence finishes. Persistence failures remain
visible; worker shutdown reports non-cancellation execution failures instead of
discarding them. Do not add production sleeps, inspect all event-loop tasks, or
depend on LangGraph's private cancellation representation.

Move the queued command service's pause, stop, budget-update and resume store
transactions to `asyncio.to_thread`. The store owns its session within that
thread. Keep cancel/wake callbacks on the event loop, after the transaction
commits. Do not lengthen SQLite timeouts or add lock retries to hide the stall.
This is limited to those generic command mutations; it is not a complete audit
of every synchronous database access in asynchronous services.

This is application lifecycle ownership, not a new engine protocol. Model
requests, provider types, canonical artifacts, database schema, retry budgets,
and the mandatory Blueprint checkpoint are unchanged.

## Verification and limits

Tests hold the database cleanup behind an explicit gate, inject cancellation
again, and require stop to remain pending until the gate is released. Existing
operator-stop, invocation state, no-output, restart and unfinished-work checks
remain. Additional cases cover production-service cleanup, graph wrappers that
do or do not cancel their leaf, cleanup failure propagation and concurrent-scope
isolation.

Four command regressions hold a real asynchronous SQLite write transaction,
release it only once the competing control insert begins, and verify that the
command completes, the worker is notified after commit on the event loop, and
repeating the command is idempotent. The unfixed stop case fails at the same
control insertion as the full-suite failure.

All 758 Python tests, Ruff, strict mypy, frontend checks and the production build
pass after both corrections. Historical v41 failures remain recorded as observed.

This addresses orderly cancellation while the process is alive. Abrupt process
loss still uses durable recovery. It does not establish protection for every
persistence boundary, provider behavior, or possible SQLite failure.

See the [implementation report](../benchmark_reports/worker-cleanup-critic-v42-2026-10-09.md).
