# ADR 0002: Explicit durable workflow graph

- Status: Accepted
- Date: 2026-07-13

## Context

The application needs specialist agents, sparse human approval, recovery after
restart, bounded revision, and protection against recursive delegation and
runaway cost.

## Decision

Use an explicit LangGraph state graph composed of registered workflow nodes and
specialist subgraphs. The orchestrator may choose among registered capabilities
but may not recursively invent or spawn arbitrary agents.

Every node has typed input/output, a completion condition, retry policy, model
profile, and budget. Human approval uses durable interrupts.

Domain models remain independent from LangGraph classes so the workflow runtime
can be replaced if necessary.

## Consequences

- Runs are inspectable, resumable, testable, and bounded.
- Adding a new specialist requires registration and a defined contract.
- Some apparent agent freedom is intentionally traded for reliability.
