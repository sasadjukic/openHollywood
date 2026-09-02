# Open Hollywood

Open Hollywood is a local-first agentic story studio that turns a user premise
into an approved story blueprint and then autonomously produces a versioned,
evaluated, properly formatted work through a durable specialist-agent workflow.

## Project status

The legacy scene-execution prototype is preserved on the
`openHollywood-legacy` branch and at the immutable `legacy-v2-final` tag. The
active rewrite now includes a browser-based React client, a local FastAPI
service, a generated TypeScript SDK shared through the contracts package, and a
migration-managed SQLite persistence layer for projects, conversations,
artifacts, workflow runs, model invocations, profiles, and evaluations. Workflow
activity is exposed through a durable append-only event log with paginated
cursor replay and resumable Server-Sent Events. The provider-neutral model
gateway supports dynamically discovered local Ollama models and optional Ollama
Cloud inference with explicit per-model capabilities and budgeted calls. Runtime
secret handles and fail-closed gateway, persistence, fixture, and database-export
guards keep model credentials outside story data and observability records.
The provider-neutral engine now exposes immutable Pydantic schemas for every
v0.1 planning artifact, including an integrated Story Blueprint with validated
character, location, beat, and scene references. A deterministic context-packet
compiler assembles only manifest-declared artifact versions, story-bible
sections, and nearby summaries under explicit input-token budgets. Creative
workflow execution now begins with a fixed, SQLite-checkpointed Story Blueprint
LangGraph. It runs the brief and premise stages, parallel world and character
specialists, integration, and evaluation before pausing at the mandatory
blueprint review boundary. Checkpoints retain only orchestration state and exact
immutable artifact-version references, and failed parallel work resumes without
repeating a successful sibling branch. The review is now a real durable human
interrupt with typed, idempotent approve, revise, reject, and fork commands.
Approval marks the exact blueprint version accepted; revision and rejection
create immutable descendant versions through bounded graph routes; forks create
linked child workflow threads without discarding the source lineage. The
FastAPI command boundary and generated TypeScript SDK expose the same durable
transition contract to the persisted workspace UI. The responsive three-panel
client now reads projects, conversations, workflow activity, run state,
artifact versions, provenance, and evaluations from SQLite-backed API views.
It keeps the Story Blueprint decision beside its source artifact and activity
timeline while preserving the product boundary against a general-purpose
manuscript editor. A new installation opens directly in that workspace shell:
the first-premise composer atomically creates the local project, conversation,
user message, and queued Story Blueprint run, so the empty library is no longer
a separate welcome-screen dead end.

Model configuration is now a first-class persisted workflow surface. The
workspace offers Local, Cloud, and Hybrid presets backed by fixed,
provider-neutral role-routing policies and dynamically discovered Ollama model
catalogs. A preset cannot become active until all of its required exact model
slots are configured. Stored profiles contain model identifiers and inference
placement only; cloud credentials continue to resolve from runtime secret
handles and never enter SQLite or the generated API contract.

The useful legacy character-agent dialogue experiment has also been ported as
an isolated, bounded subgraph rather than restored as an application module.
Two registered character actors speak in sequence under a dialogue director
that briefs once and evaluates after each round. Dialogue bodies and director
assessments use typed immutable artifacts, while checkpoint state retains only
budgets, counters, model-profile IDs, and exact version references. This
subgraph is now an optional specialist pass inside the bounded scene-production
loop; it does not add a second human checkpoint or a standalone scene editor.

After blueprint approval, the provider-neutral production graph processes the
three-to-eight planned prose scenes in stable order. Each scene receives an
initial writer pass, an optional embedded dialogue pass and prose integration,
and an independent critique against the exact draft version. Non-passing scenes
return to the writer only while the configured revision allowance remains.
Every accepted scene records whether it passed the rubric or reached that hard
limit, and later scenes receive only immutable references to earlier accepted
work. Checkpoints contain plans, counters, dispositions, and artifact-version
references—not prose, critiques, prompts, or conversation history. The same
unit contract can support chapters when a later product version adds a
long-form format; v0.1 deliberately produces scenes only.

Before any scene becomes canonical, a continuity supervisor checks its exact
draft and plan versions against the exact current Story Bible. Severe findings
enter the shared bounded revision loop and fail closed at the hard limit.
Continuity-cleared scenes produce typed deltas that a deterministic reducer
applies to immutable full-snapshot Story Bible versions. Accepted-scene and
timeline history only append, established identifiers cannot be reused,
resolved mysteries and setup/payoff promises cannot reopen, and the next scene
receives the exact resulting canonical version.

Workflow runs now expose durable, idempotent pause, resume, stop,
retry-from-node, and budget-update commands. Active pause requests take effect
at the next safe node boundary; stop cancels the run and any open invocation;
resume continues from the SQLite checkpoint without repeating completed work.
Retry-from-node creates a linked child run from compatible immutable artifact
versions instead of rewriting source history. Aggregate model-call, token,
cost, and wall-clock usage is visible in the workspace and checked before each
model-backed node so an unaffordable next call pauses with partial artifacts
preserved. Human approval remains a distinct pause reason and still requires
the Story Blueprint decision flow.

The browser runtime is composed through the local workflow worker. It claims
ordinary queued Story Blueprint runs sequentially, freezes the active complete
model profile before the first call, resumes durable checkpoints after restart,
and starts scene production after Blueprint approval. Benchmark runs remain
isolated under the operator harness and are never claimed by the interactive
worker.

Completed short-prose projects now have a deterministic publication boundary.
The provider-neutral engine assembles only complete, latest approved Scene
Draft versions in contiguous story order, renders canonical Markdown, and
exports searchable PDF and editable DOCX files with stable metadata and bytes.
A separate typed Fountain renderer supports future screenplay-family formats
without guessing screenplay structure from prose. The API exposes export
readiness, exact source-version lineage, content hashes, and downloads; the
workspace shows Markdown, PDF, and DOCX controls only when the manuscript
invariants pass.

The Step 19 evaluation harness is now in progress. Its provider-neutral core
loads the frozen 12-prompt v0.1 corpus, pins exact graph, prompt-contract, and
model-profile snapshots into 48-case campaign plans, resumes failure-isolated case execution,
builds provenance-free blind A/B review packets with separate answer keys, and
aggregates the accepted rubric, hard gates, preference rate, completion rate,
and cost criteria. The direct baseline now runs through a bounded
provider-neutral call with idempotent SQLite prompt, invocation, workflow, and
story lineage; long campaigns atomically checkpoint after every case. Formal
operators can extend the Ollama transport timeout for long-form inference;
timeout failures are distinct from provider outages, and a retry reconciles
invocations left running by an interrupted process without mutating their
immutable input artifacts. Ollama Cloud response aliases are normalized only
when they resolve to the requested frozen model, while both requested and
provider-reported identifiers remain persisted for audit. Failed structured
calls retain provider usage, finish reason, response hash, and response length;
a lone JSON Markdown fence is normalized without accepting mixed commentary.
The agentic path now runs profile-routed, schema-validated specialists through
the real durable Story Blueprint graph and stops at its mandatory human approval
interrupt without duplicate calls on replay. Prompted non-schema invariants keep
benchmark constraints exact, parallel World output cannot invent unresolved
character IDs, and integration generates only new beats and scene plans while
the application assembles authoritative specialist artifacts deterministically.
Creative Brief prompt contract v6 likewise asks the model only for creative
choices; the application attaches the exact frozen premise, format, genres,
maturity, required elements, and forbidden elements so optional model fields
cannot silently weaken benchmark intent.
Prompt contract v9 also bounds Blueprint integration to a compact world summary,
the Creative Brief's exact scene count, and at most two beats per scene. When
prompt-only cloud structured output fails, the persisted retry count and safe
validation locations feed the one allowed retry without retaining or echoing the
failed story response. Word bounds remain application-validated instead of
emitting grammar keywords unsupported by local Ollama structured output.
Model-executing operator commands reject campaign plans whose baseline,
Blueprint, production prompt, or graph versions differ from the running build,
so diagnostic staging cannot silently become formal benchmark evidence.
The frozen runtime snapshot includes the direct-story graph and nested dialogue
subgraph as well. Blueprint graph v4, scene-production graph v2, and dialogue
subgraph v2 allow model-backed nodes up to 900 seconds for formal long-form
inference; ordinary provider timeouts can remain shorter. Cancelling or timing
out a model task now closes its persisted invocation instead of leaving it
indefinitely running.
Operators can prepare selected cases independently. Batch preparation isolates
terminal Blueprint failures and continues with sibling cases; production reports
carry those failures forward while still requiring explicit approval for every
surviving Blueprint. Once approved, the
benchmark materializes immutable Scene Plans and an initial Story Bible, executes
the checkpointed
writer/critic/continuity/bible-maintainer loop, and deterministically assembles
accepted scene versions into a complete benchmark story with exact usage and
lineage. The formal
operator flow can stage all three profiles, preserve the mandatory Blueprint
approval through an offline, digest-bound human review packet and completed
reviewer form, route frozen local/cloud deployments
through signed-in local Ollama or direct Ollama Cloud, and resume production
into the same atomically checkpointed report. `run-agentic --case-id` is
repeatable, allowing deterministic operator-sized batches without creating a
new campaign; separate processes merge their case results under an interprocess
checkpoint lock instead of overwriting one another. `--batch-size` plus
one-based `--batch-number` also partitions the selected target in frozen plan
order (for example, Cloud batches 1-3 at size 4). Production wall-clock budgets
count persisted active node intervals rather than paused downtime, and
an interrupted open interval is discarded when the durable graph is recovered.
Cloud and Hybrid stories default to a configurable `$5.00` aggregate ceiling
(`--cost-ceiling-usd`) while recorded provider cost remains the actual billed or
reported amount; Local production retains its derived no-cloud ceiling. The
bounded second production attempt now receives safe structural validation
diagnostics and records its retry ordinal without application-authored semantic
repairs. Scene-production prompt contract v8 scopes benchmark requirements
deterministically for continuity: non-final scenes receive only opaque IDs for
story-wide requirements deferred until the ending, while the final scene
receives their exact frozen text as due-now gates. Scene Plan requirements
remain current-scene obligations except when a non-final plan repeats an exact
story-wide benchmark requirement that is still deferred. Continuity re-checks express an
unresolved or newly exposed blocker through typed disposition, repair-assessment,
and revised-evidence fields instead of being judged by textual difference alone;
the Local profile remains fail-closed and the existing audited Hybrid-only
stagnation escalation remains bounded. The harness also creates reviewer-specific
CSV forms and provenance-free rubric guides, imports complete human scores, and
cryptographically binds review evidence to the exact public blind packet and
private answer key. Complete campaigns can be sealed into deterministic,
tamper-evident archives whose manifest, member hashes, review coverage, summary,
and cross-document lineage are independently reverified. The formal
Local/Cloud/Hybrid campaign and actual blind human reviews remain pending, so
Step 19 is not yet marked complete.

The first Local v8 canary batch completed two of five production-runnable cases.
Its failed invocations exposed that ordinary application validation messages
were being reduced to `$:ValueError`, leaving the bounded Local retry without
actionable field guidance. Scene-production prompt contract v9 now persists a
redacted, bounded diagnostic envelope with field location, validation type, and
message while retaining only the failed provider response's hash, length, finish
reason, and usage metadata. Local structured-output retries receive a concise
operation-specific repair packet focused on those locations, including paired
continuity re-check fields and canonical Story Bible IDs. Cloud retries do not
receive Local guidance, and the existing Hybrid-only continuity-stagnation
escalation remains unchanged and drops the Local packet when routed to Cloud.

The first Local v9 canary batch completed one of five production-runnable cases;
the success produced 3,365 words within target and passed every automated hard
gate. The four terminal failures shared one exact cause: initial continuity
calls populated fields intended only for continuity re-checks. Prompt contract
v10 now selects an explicit `initial_check` or `recheck` output schema from
immutable input lineage. The initial schema omits the re-check disposition,
repair-assessment, and revised-evidence fields entirely and receives no re-check
instructions; the re-check schema exposes them with the existing verification
contract. The selected variant is identical in the prompt and Local provider
grammar and is persisted for replay diagnostics. Canonical artifact validation,
Cloud behavior, bounded repair, and Hybrid-only escalation remain unchanged.

The first Local v10 canary batch again completed one of five
production-runnable cases; its success produced 3,455 words within target and
passed every automated hard gate. Two failures omitted
`recommended_resolution` from blocking findings after repair, while two reached
the revision limit after continuity re-checks cited non-exact evidence or copied
stale assessments despite changed drafts. Prompt contract v11 now gives initial
and re-check continuity findings severity-discriminated schemas: error/blocking
branches require a concrete resolution, advisory branches do not, and the
application-owned `blocks_approval` field is unavailable to the model. Re-check
blocking branches also require their three audit fields together. Application
validation binds every revised-evidence excerpt to the exact current draft,
rejects copied assessments when evidence changes, and requires an explicit
explanation when evidence is unchanged. Exact story-wide benchmark requirements
copied into non-final Scene Plans are deferred and redacted from the continuity
prompt view. Canonical artifacts, retry limits, Cloud behavior, and Hybrid-only
escalation remain unchanged.

The first Local v11 canary batch completed two of five production-runnable
cases; both successes passed all automated hard gates. Its failures showed that
one finding shape still allowed missing requirements and absent forbidden
shortcuts to masquerade as contradictions, that world-rule checks could ignore
explicit companion-rule authorization, and that critic-only revisions could
consume the revision allowance before continuity ran. Prompt contract v12 now
uses separate contradiction, missing-requirement, and forbidden-shortcut
branches with basis-specific source and evidence fields. Exact draft evidence
is validated during initial checks and re-checks. World-rule blockers must cite
canonical rule IDs, assess companion rules and exceptions, and cannot block a
condition declared explicitly authorized. Production graph v3 evaluates critic
and continuity for every candidate, consolidates their feedback, and increments
the revision counter once. Benchmark failures now retain the redacted persisted
Production node and cause instead of a generic wrapper.

The first Local v12 canary batch completed none of its five
production-runnable cases. Prompt contract v13 keeps production graph v3 and
turns exact continuity evidence and canonical provenance into model-selected,
enum-constrained references. The prompt identifies one candidate draft as the
only valid evidence source, labels earlier accepted drafts as context only, and
exposes its prose as deterministic exact-excerpt handles. A bounded canonical
claim catalog carries the supporting statement plus immutable artifact and path
provenance; the application resolves selected evidence handles into the
canonical persisted `evidence` fields. Due requirement IDs and canonical World
Rule IDs are also constrained by the call-specific schema, advisory findings
cannot emit evidence, impossible requirement branches are omitted, and
application-owned report lineage is no longer generated by the model.

The first Local v13 canary batch completed none of its five
production-runnable cases, but it eliminated the v12 exact-evidence,
canonical-reference, requirement-ID, and truncated-JSON failure classes. The
remaining continuity failures were concentrated in world-rule analysis fields:
missing companion-rule assessments, absent or invalid rule IDs, incorrect
authorization state, and world-only fields attached to a non-world finding.
Prompt contract v14 retains production graph v3 and gives every blocking basis
an explicit world-rule branch and an explicit non-world branch. World branches
structurally require call-valid rule IDs, a companion-rule assessment, and
`condition_explicitly_authorized=false`; non-world branches cannot emit any of
those fields. Benchmark `report.json` failures now prefer the terminal failed
invocation's exact redacted field-level diagnostic, falling back to the durable
workflow cause only when no model invocation caused the failure.

The first Local v14 canary batch again completed none of its five
production-runnable cases, while OH-V01-006 retained its terminal Blueprint
failure. The explicit world-rule/non-world branches eliminated every v13
world-field shape failure. Two stories instead stopped on continuity re-check
stagnation, and three advanced far enough to exceed the unchanged 20,000-token
continuity input ceiling after accepting four scenes between them. A
representative all-bases v14 continuity schema is about 70% larger than v13,
making schema compaction the first follow-up before changing the production
budget. The run also exposed one reporting-precedence edge case: a recovered
failed invocation can mask a later, specific workflow-level terminal cause in
`report.json`.

Prompt contract v15 retains production graph v3 while removing the v14 schema
cross-product. Blocking findings now carry one shared object plus independent
`basis_details` and `category_details` unions; this preserves all six semantic
combinations while reducing representative initial and re-check schemas by
59.4% and 58.4%, respectively. Local calls receive that schema only through
Ollama's enforced `format` channel instead of duplicating it in the user
message. Every invocation records content-free byte, hash, and diagnostic token
estimates for system, artifact, control, retry/repair, inline-schema, and
gateway-schema contributions, while provider-reported usage is retained even
when it exceeds budget. Re-check contradiction and forbidden-shortcut details
must declare whether exact evidence is `changed`, `unchanged`, or
`newly_exposed`; the application verifies the declaration against the prior
report. Benchmark failure reporting now prefers a specific terminal workflow
cause over any earlier failed invocation that a retry subsequently recovered.

The first Local v15 canary still completed no cases, but it narrowed the failure
surface: the v14 world-branch shape failures did not recur, 45 of 58 production
invocations succeeded, and four scenes were accepted before terminal continuity
failures. Prompt contract v16 retains production graph v3 and separates an
exhaustive Scene Plan requirement audit from affirmative contradictions. Every
due obligation has a stable ID and must be classified exactly once as covered or
missing; the application derives canonical missing-finding identity, category,
lineage, and routing state. Re-check evidence change is now application-owned,
so an unchanged exact blocker follows the existing revision path while a copied
assessment is rejected only after evidence actually changes. Canonical claims
are grouped, only the immediately prior accepted scene ending is supplied, and
the critic's overall score is the deterministic mean of bounded rubric scores.

The first Local v16 canary also completed no cases, but every production-runnable
story reached its final scene and accepted 18 scenes, up from four under v15.
Successful production calls rose to 91 of 103, continuity calls to 21 of 33,
critic failures fell to zero, and the largest continuity input remained below
the unchanged 20,000-token ceiling. Terminal failures were isolated to omitted
IDs in parallel coverage arrays, model-authored re-check disposition, one
application validator that rejected a valid Scene Plan scalar requirement, and
one copied-assessment heuristic. Prompt contract v17 retains production graph v3
and replaces those boundaries with one application-deduplicated due requirement
catalog and a schema-required `requirement_coverage` object keyed by exact IDs.
The application now owns missing-finding identity and category for every due ID,
as well as blocker identity and re-check disposition. Contradictions cannot use
the `constraint` category, forbidden shortcuts remain a separate catalog, and a
copied assessment after changed exact evidence is persisted as advisory telemetry
instead of invalidating the output.
Safe persisted diagnostics retain focused reason codes for invalid evidence,
requirement-basis misuse, copied changed-evidence assessments, and invalid
re-check disposition.

The first Local v17 canary completed two of five production-runnable cases,
with 81 of 87 production invocations and 22 of 26 continuity calls succeeding.
The v16 coverage-partition failures disappeared. One remaining structured
failure came from application-generated positional finding IDs colliding across
consecutive re-checks; two stories reached the revision limit after continuity
misread a pursued Scene Plan goal as a required outcome or promoted intentional
dramatic/pacing choices to World Rule blockers. Prompt contract v18 retains
production graph v3 and replaces re-check finding references with an exhaustive
keyed prior audit plus separate new findings and revision-scoped IDs. Requirement
catalog policy v2 declares fulfillment semantics and companion requirements,
including goal-as-pursuit. World Rule blockers require exact rule-source
provenance, an explicit violation kind, and a direct conflict assessment, while
duplicate missing-requirement contradictions are rejected.

The first Local v18 canary completed three of five production-runnable cases,
accepted 18 scenes, and produced no revision-limit failure. OH-V01-003 moved
from a false World Rule revision-limit failure under v17 to a complete story,
while OH-V01-002 and OH-V01-004 remained successful. Continuity structured-
output reliability nevertheless fell to 18 of 25 calls: one World Rule ID/source
copy mismatch occurred, and a missing/contradiction text-overlap validator fired
six times across four runnable cases. Prompt contract v19 retains production
graph v3, derives World Rule canonical provenance from enum-constrained rule IDs,
and deterministically consolidates an exact repeated missing summary-and-repair
pair while allowing independently evidenced contradictions that merely share
general wording. Local repair packets now carry issue-specific structural
directives and exact key sets without retaining failed story responses.
Benchmark failures also preserve an ordered, redacted `failure_history` for
every failed production invocation so an earlier attempt cannot disappear behind
the terminal message.

The first Local v19 canary completed two of five production-runnable cases and
accepted 15 scenes, below v18's three completions and 18 scenes. Call reliability
improved to 95 of 98 production calls and 26 of 29 continuity calls, and the new
ordered failure history worked, but false semantic blockers remained. Explicit
early-afternoon/long-shadow and dusk-light evidence still reached the revision
limit, non-world contradictions could select unrelated canonical handles such
as Scene Plan titles, and a `pursue` goal was evaluated as though achievement
were required. Prompt contract v20 retains production graph v3 and replaces
untyped non-world source selection with typed canonical claims carrying category,
entity/scene, and requirement lineage. Requirement coverage now uses
satisfaction-mode-specific status pairs and exact positive evidence, while
entry-state and time-context omissions are advisory. Rechecks return compact
decisions and current evidence; the application rehydrates the persisted finding.
Local repair policy v3 exposes exact claim types and lineage without retaining
failed response content.

The first Local v20 canary completed none of the five production-runnable cases
and accepted only two scenes. Its typed continuity schema roughly doubled the
v19 initial-check and recheck grammar sizes, while duplicate Scene Plan claim
and coverage representations allowed requirements to be recast as unrelated
contradictions. Prompt contract v21 retains production graph v3 but makes keyed
coverage the exclusive Scene Plan path, uses a shared `met`/`partial`/`absent`
contract with exact evidence or an explicit negative search result, and keeps
partial or qualitative coverage advisory. The application now owns continuity
metadata and stable semantic identity; compact contradiction and World Rule
catalogs plus focused Local repair policy v4 remove repeated grammar. Evidence:
`docs/benchmark_reports/step-19-local-v20-canary-2026-09-02.md`.

Benchmark word-count ranges are advisory creative targets. New outputs persist a
non-gating adherence measurement with the target, actual count, status, and word
deviation. Automatic completion reflects a finished, non-truncated document,
while requested short-prose format remains a human hard-gate judgment; merely
falling outside the preferred range cannot fail either gate.

The v0.1 target is deliberately narrow: short prose fiction, local-first
storage, optional local/cloud/hybrid inference, and one mandatory story
blueprint approval before autonomous drafting.

## Source of truth

- [`open_hollywood_future.md`](open_hollywood_future.md) describes the product
  vision and the distinction between Open Hollywood and SammyAI.
- [`open_hollywood_bible/`](open_hollywood_bible/) contains the accepted product,
  architecture, workflow, evaluation, and UI guidance.
- [`open_hollywood_bible/step_by_step_implementation.md`](open_hollywood_bible/step_by_step_implementation.md)
  is the authoritative implementation progress tracker.
- [`docs/adr/`](docs/adr/) records accepted architecture decisions.

## Toolchain

- Python 3.13
- uv 0.11.28+
- Node.js 24 LTS
- pnpm 11.12.0+

Versions are pinned in `.python-version`, `.node-version`, `pyproject.toml`,
and `package.json` where appropriate.

## Repository layout

```text
apps/          Deployable API, worker, web, and desktop applications
engine/        Provider-neutral creative workflow and domain engine
packages/      Shared TypeScript contracts and UI components
migrations/    Database migrations
tests/         Cross-package, integration, evaluation, and legacy fixtures
docs/          Architecture decisions and technical documentation
images/        Open Hollywood brand assets
```

## Development

Run every command in this section from the repository root. Install the pinned
Python and JavaScript dependencies:

```powershell
uv sync --extra api
pnpm install
```

The uv workspace installs `open_hollywood_engine`, `open_hollywood_api`, and
`open_hollywood_worker` as editable local packages. No `PYTHONPATH`
configuration or Uvicorn `--app-dir` option is required.

Create or upgrade the local SQLite database before starting the API. The
default database is `./data/open_hollywood.db`:

```powershell
uv run alembic upgrade head
```

Then start the worker-composed API and web client in separate terminals.

Terminal 1 — API + workflow worker:

```powershell
uv run --extra api uvicorn open_hollywood_worker.app:app --reload
```

Terminal 2 — web client:

```powershell
pnpm --filter @open-hollywood/web dev
```

Open `http://127.0.0.1:5173`. The API health endpoint is
`http://127.0.0.1:8000/api/v1/health`, and its interactive documentation is at
`http://127.0.0.1:8000/docs`.

`open_hollywood_api.app:app` remains available for API-only contract and storage
development, but it intentionally has no workflow executor. Use the
worker-composed command above for browser story execution and run controls.

The defaults require no environment variables. To use another database, set
its path in the API terminal before running Alembic and Uvicorn:

```powershell
$env:OPEN_HOLLYWOOD_DB_PATH = "C:\path\to\open_hollywood.db"
uv run alembic upgrade head
uv run --extra api uvicorn open_hollywood_worker.app:app --reload
```

To use an API origin other than `http://127.0.0.1:8000`, set the client
variable before starting Vite:

```powershell
$env:VITE_API_URL = "http://127.0.0.1:8000"
pnpm --filter @open-hollywood/web dev
```

Local Ollama must be running only when using local models. Direct Ollama Cloud
catalog discovery additionally reads `OLLAMA_API_KEY` from the API process
environment; credentials must never be written to project files.

When a project has three to eight complete, approved Scene Draft artifacts, its
workspace header enables Markdown, PDF, and DOCX downloads. The same downloads
are available from:

```text
GET /api/v1/projects/{project_id}/exports
GET /api/v1/projects/{project_id}/exports/{markdown|pdf|docx}
```

The manifest reports the exact immutable scene-version IDs used. A project
that does not yet form a complete, contiguous manuscript reports no available
formats, and a direct download attempt returns `409 Conflict`.

When a FastAPI route or response model changes, regenerate the shared SDK:

```powershell
pnpm contracts:generate
```

Inspect the active revision or roll back one migration during development:

```powershell
uv run alembic current
uv run alembic downgrade -1
```

Run the applicable quality checks before handing off a change:

```powershell
uv run --extra api ruff check apps/api apps/worker engine scripts tests migrations
uv run --extra api ruff format --check apps/api apps/worker engine scripts tests migrations
uv run --extra api mypy apps/api apps/worker engine scripts tests migrations
uv run --extra api pytest
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## License

Open Hollywood is available under the [MIT License](LICENSE). Contributions,
forks, experimentation, and derivative projects are welcome under its terms.
