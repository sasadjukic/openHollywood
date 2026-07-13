# ADR 0005: Versioned artifacts and bounded context

- Status: Accepted
- Date: 2026-07-13

## Context

Long creative workflows cannot safely treat the complete conversation as model
memory. Agents need relevant facts, reproducible inputs, revision history, and a
canonical story state that survives summarization.

## Decision

Persist story outputs as immutable artifact versions with lineage. Maintain a
structured canonical story bible for accepted facts. Build a bounded context
packet for each task from user intent, required story-bible sections, direct
dependencies, nearby summaries, output schema, and evaluation rubric.

Vector retrieval is optional support for later long-form work; it does not
replace deterministic dependency selection in v0.1.

## Consequences

- Revisions create new versions rather than overwriting accepted work.
- Model calls can be replayed and audited against exact inputs.
- Changing an approved artifact can mark dependent artifacts stale.
- Context assembly becomes a first-class, tested subsystem.
