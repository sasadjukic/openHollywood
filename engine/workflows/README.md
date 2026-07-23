# Workflows

The first durable workflow is the versioned `story_blueprint` graph:

```text
START -> intake -> brief -> premise -+-> world_specialist -----+
                                      +-> character_specialist -+-> integration
                                                                  -> evaluation
                                                                  -> approval interrupt
```

The topology is fixed in code. Each registered node declares its specialist
role, accepted artifact kinds, output cardinalities, timeout, and bounded retry
policy. Only `RetryableSpecialistError` receives an automatic retry; invalid
state and deterministic specialist failures fail the run immediately.

## Durable state

LangGraph checkpoints every super-step into the application's SQLite database.
Alembic migration `0003` owns the checkpointer table schema, while the saver's
startup setup remains safe and idempotent. The workflow-run UUID is the
LangGraph `thread_id`, and the latest checkpoint ID is mirrored onto
`workflow_runs`. Starting the service again with a failed run resumes that
thread from its newest checkpoint. Successful work from one branch of the
parallel specialist super-step is reused if its sibling failed.

Checkpoint values deliberately contain only JSON-safe coordination state:

- the workflow-run ID;
- completed registered node names;
- immutable artifact kind, key, version ID, and schema-version references; and
- whether the graph reached blueprint review.

Creative content stays in immutable `artifact_versions`. Prompts, provider
objects, credentials, private reasoning, and unbounded conversation history do
not enter checkpoint state. The checkpointer uses a strict serializer with no
additional MessagePack module allowlist.

## Execution boundary

`BlueprintNodeExecutor` is the provider-neutral boundary that specialist
implementations use to perform their budgeted model calls and persist validated
artifact versions. The graph refuses undeclared, duplicate, or incorrectly
cardinalized output references before advancing. `BlueprintWorkflowObserver`
mirrors node lifecycle, safe artifact references, failures, and the review
checkpoint into the existing workflow run and append-only event stream.

## Human interrupt

The approval node uses LangGraph's durable `interrupt()` primitive. The
checkpoint exposes only the allowed actions and exact Story Blueprint and
Critique version references. A human command is persisted once in
`human_decisions`; the graph receives only its decision ID and action.
Instructions remain in application persistence and are loaded by the node
executor through that ID, so free-form story feedback is not copied into every
checkpoint or event.

Commands resume the fixed graph as follows:

- `approve` ends the graph, marks the exact active Story Blueprint version
  approved, and succeeds the run;
- `revise` reruns integration and evaluation against the reviewed versions;
- `reject` regenerates from premise through the parallel specialists,
  integration, and evaluation; and
- `fork` freezes the source run and starts a child checkpoint thread from the
  exact active artifact versions before regenerating a new direction.

Every path returns to a new approval interrupt except `approve`. Artifact
reducers replace active references by logical artifact key while immutable
older versions and their parent lineage remain in SQLite. Decision UUIDs are
idempotency keys, and each interrupt accepts at most one decision.
