# Workflows

The first durable workflow is the versioned `story_blueprint` graph:

```text
START -> intake -> brief -> premise -+-> world_specialist -----+
                                      +-> character_specialist -+-> integration
                                                                  -> evaluation
                                                                  -> approval -> END
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

The approval node currently leaves the run in `PAUSED` with
`awaiting_approval=True`. Approve, revise, reject, and fork commands are the
human-interrupt work reserved for Step 11.
