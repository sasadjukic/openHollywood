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

## Character-dialogue subgraph

The legacy dialogue experiment is preserved as the isolated versioned
`character_dialogue` subgraph:

```text
START -> director_briefing -> character_one -> character_two
                                      ^              |
                                      +-- director_evaluation
                                             |
                                       complete -> END
```

It deliberately supports exactly two character actors. Actor identity and
scene context arrive through exact Character, Scene Plan, and optional context
artifact-version references. The application executor loads those immutable
inputs, performs a budgeted call associated with the selected model profile,
validates a `DialogueBriefing`, `DialogueTurn`, or `DialogueEvaluation`, and
persists the output before returning its reference to the graph.

Each round always calls both actors in stable order and evaluates once
afterward. The director may end only after the configured minimum round, with
closure detected at climax or resolution and a declared ending. Otherwise the
graph continues until its hard maximum. Only explicitly retryable dialogue
failures receive the registered bounded retry; malformed state, mismatched
turns, duplicate input/output versions, undeclared endings, and incorrect
artifact kinds fail immediately.

Checkpoint state contains no dialogue, pacing notes, prompts, credentials, or
provider objects. It stores the per-call budget and prompt-template version,
workflow/model-profile identifiers, counters, completion reason, and immutable
artifact references. The subgraph inherits the parent checkpointer when the
scene-production loop embeds it.

## Scene-production graph

After Story Blueprint approval, v0.1 uses the versioned `scene_production`
graph:

```text
START -> writer -----------------------------> critic
            |                                    |
            +-> character_dialogue -> integrate-+
                                                 |
                        attempts remain <--- revise?
                                                 |
                                           continuity
                                                 |
                        attempts remain <--- blocked?
                                                 |
                                      story-bible update
                                                 |
                                              accept
                                                 |
                                      next scene or END
```

The input contains the exact approved Story Blueprint, three-to-eight ordered
Scene Plan versions, participating Character versions, bounded context
references, one model profile, per-call budget, and a hard revision limit. The
graph cannot invent units or reorder them. `scene_writer` produces the initial
and revised prose artifacts, while the independent `scene_critic` evaluates an
exact `SceneDraft` version. Hybrid profiles route high-impact writing to cloud
and routine critique locally.

An optional two-character pass is declared per scene. On every writing attempt,
the Step 14 subgraph runs under the production graph's checkpoint namespace;
the writer then persists a new prose version integrating its briefing, turns,
and evaluation. Scenes without that declaration go directly to critique.

A passing critique advances the current immutable draft to the continuity
gate. A non-passing critique returns to the writer only while revision attempts
remain. At the hard limit, the best available complete draft may advance with
`revision_limit_reached`, but it still cannot bypass continuity. Error or
blocking findings consume the same bounded revision allowance and fail closed
if they survive its hard limit.

A continuity-cleared scene produces a typed delta against the exact current
Story Bible. A pure reducer creates the only valid successor snapshot,
monotonically appending accepted scenes, timeline events, and established
facts; applying stable entity-state updates; and preventing resolved threads
from reopening. The graph compares the persisted successor with that exact
deterministic result before canonical acceptance. Each accepted scene records
its critique, final continuity report, delta, and resulting Story Bible version.

Parent checkpoints retain only budgets, graph configuration, counters,
deterministic dispositions, and artifact references. Scene prose, critique
bodies, dialogue, prompts, credentials, and provider objects remain in their
own application-owned records. Accepted scenes and the latest canonical Story
Bible are supplied to later specialists by exact version reference.
