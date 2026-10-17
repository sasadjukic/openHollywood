# Step-by-step implementation sequence

This file is the authoritative implementation progress tracker. Mark a step
complete only when its deliverables exist and the relevant checks pass. Update the completion date and evidence in the same change.

## Status legend

- `[x]` COMPLETED
- `[~]` IN PROGRESS
- `[ ]` NOT STARTED

## Rewrite foundation — COMPLETED 2026-07-13

- [x] Preserve the legacy implementation on `openHollywood-legacy`.
- [x] Create and publish the immutable `legacy-v2-final` tag.
- [x] Move the Python environment to `.venv` and standardize on Python 3.13.
- [x] Standardize on Node.js 24 LTS, pnpm 11, and uv.
- [x] Track the product vision and project bible.
- [x] Adopt the MIT License for the public project.
- [x] Add toolchain pins, workspace manifests, text-format rules, environment
  template, repository guidance, and module responsibility documents.
- [x] Preserve useful legacy prompts, scene configuration, and director-flow
  behavior as regression fixtures.

## Implementation steps

1. [x] **COMPLETED 2026-07-13 — Write architecture decision records.**
   Accepted ADRs cover local-first deployment, an explicit durable graph,
   SQLite persistence, a provider-neutral model gateway, and versioned
   artifacts with bounded context. Evidence: `docs/adr/0001` through `0005`.

2. [x] **COMPLETED 2026-07-13 — Freeze and capture the legacy prototype.**
   The final implementation is preserved by branch and tag. Useful prompts,
   scene configuration, director state, call order, and termination invariants
   are captured under `tests/fixtures/legacy/`.

3. [x] **COMPLETED 2026-07-21 — Create the React/TypeScript client and FastAPI application with a shared generated OpenAPI client.** The branded React/Vite shell consumes a typed FastAPI health boundary through an exactly pinned Hey API SDK generated from OpenAPI 3.1. Evidence:
`apps/web/`, `apps/api/open_hollywood_api/`, `packages/contracts/`, and
`tests/api/`. Ruff, mypy, pytest, Prettier, ESLint, TypeScript, Vitest, the
production build, and desktop/mobile browser verification pass.

4. [x] **COMPLETED 2026-07-21 — Add SQLite, SQLAlchemy, and Alembic.** The
migration-managed SQLite layer implements `Project`, `Conversation`,`Message`, `Artifact`, immutable `ArtifactVersion` lineage, `WorkflowRun`,
observable `AgentInvocation` records with exact input-version links,
secret-free `ModelProfile` configuration, and `Evaluation`. Evidence:
`apps/api/open_hollywood_api/persistence/`, `alembic.ini`, `migrations/`, and `tests/persistence/`. Migration upgrade/downgrade and metadata parity, Ruff, mypy, pytest, Prettier, ESLint, TypeScript, Vitest, and the production build pass.

5. [x] **COMPLETED 2026-07-21 — Implement an append-only workflow event
stream.** Workflow events use globally ordered durable IDs and SQLite
mutation-rejection triggers. The API exposes typed paginated replay after an
exclusive event cursor plus an SSE feed that replays missed events before
following new rows; reconnects accept both `after` and `Last-Event-ID`.
Evidence: `migrations/versions/0002_append_only_workflow_events.py`, `apps/api/open_hollywood_api/services/workflow_events.py`, `apps/api/open_hollywood_api/routes/workflow_events.py`, generated contracts,
and persistence/API integration tests. Migration upgrade/downgrade and
metadata parity, Ruff, mypy, pytest, Prettier, ESLint, TypeScript, Vitest,
and the production build pass.

6. [x] **COMPLETED 2026-07-22 — Build `ModelGateway` and `ModelCapabilities`.** Provider-neutral, immutable call contracts require
explicit token/cost budgets and reproducibility identifiers. The first
adapter dynamically discovers local Ollama and Ollama Cloud models, inspects
per-model features and context windows, classifies cloud offload correctly,
supports runtime-injected cloud bearer authentication, normalizes usage,
timing, finish state, and retryable errors, and rejects unsupported cloud
structured-output calls before inference. No Google, OpenAI, or LiteLLM
dependency was added because Ollama Local plus Ollama Cloud is sufficient for the initial short-fiction slice. Evidence: `engine/open_hollywood_engine/models/`, `tests/models/`, `engine/models/README.md`, and `open_hollywood_bible/model_configuration.md`. Ruff, mypy, pytest (including 16 model-gateway tests), Prettier, ESLint, TypeScript, Vitest, and the production build pass. Live discovery against the development Ollama server also classified two installed local models and two cloud-offloaded models with their reported context windows.

7. [x] **COMPLETED 2026-07-22 — Add secure secret handling.** Provider-neutral runtime handles and opaque redacting values keep model credentials outside workflow and domain contracts. The current environment-backed store resolves credentials only when constructing the provider transport; fail-closed gateway guards reject credentials in prompts and provider responses, while SQLAlchemy flush guards protect every durable story, profile, event, and invocation record. Database exports receive an independent full-table audit, and committed fixtures are checked against credentials configured in the test process. Evidence:
`engine/open_hollywood_engine/secrets/`, `apps/api/open_hollywood_api/persistence/secret_policy.py`, ADR 0006, and secret-policy integration tests. Ruff, mypy, 51 pytest tests, Prettier, ESLint, TypeScript, Vitest, and the production build pass.

8. [x] **COMPLETED 2026-07-22 — Define Pydantic artifact schemas.** Immutable, extra-field-forbidding contracts cover Creative Brief, Character, Relationship, Location, World Rule, Beat, Scene Plan, Critique, Continuity Finding, and the integrated Story Blueprint. A canonical artifact registry exposes JSON Schema for structured model output, while local and blueprint-level validators enforce v0.1 scope, stable IDs, ordered beats and scenes, reference integrity, critique and continuity routing invariants, and agreement with the Creative Brief. Evidence: `engine/open_hollywood_engine/artifacts/`, `tests/artifacts/`, and
`engine/artifacts/README.md`. Ruff, mypy, 66 pytest tests, Prettier, ESLint,
TypeScript, Vitest, and the production build pass.

9. [x] **COMPLETED 2026-07-22 — Build the context-packet compiler.** Versioned per-specialist manifests declare artifact cardinalities, exact story-bible sections, nearby-summary bounds, and structured output types. The deterministic compiler rejects undeclared or ambiguous versions, renders canonical packets with assignments, constraints, dependencies, output JSON Schema, and rubrics, and carries exact input-version lineage into model invocations. Mandatory context fails closed when it exceeds the reserved input-token envelope; budget-optional context is included in stable priority order or omitted with an observable reason. Token counting is injectable and versioned, with a conservative provider-neutral UTF-8 byte fallback. Evidence: `engine/open_hollywood_engine/context/`, `tests/context/`, and `engine/context/README.md`. Ruff, mypy, 76 pytest tests, Prettier, ESLint, TypeScript, Vitest, and the production build pass.

10. [x] **COMPLETED 2026-07-22 — Create the first persisted LangGraph.** The
fixed, versioned Story Blueprint graph runs `intake → brief → premise → parallel world and character specialists → integration → evaluation → approval` with registered node contracts, bounded timeouts, and retries limited to explicit retryable specialist failures. SQLite checkpoints store only JSON-safe coordination state and exact immutable artifact-version references; the workflow run mirrors its latest checkpoint and lifecycle events. A failed parallel super-step resumes in a fresh service without repeating the successful sibling, and the approval boundary leaves the run paused for Step 11. Evidence: `engine/open_hollywood_engine/workflows/`,
`apps/api/open_hollywood_api/services/blueprint_workflow.py`,
`migrations/versions/0003_langgraph_checkpoints.py`, `tests/workflows/`, and
`engine/workflows/README.md`. Ruff, mypy, 80 pytest tests, Prettier, ESLint,
TypeScript, Vitest, and the production build pass.

11. [x] **COMPLETED 2026-07-23 — Implement human interrupts for approve,
revise, reject, and fork.** The Story Blueprint review is a real
SQLite-checkpointed LangGraph interrupt with typed, idempotent human decisions. Approval succeeds the run and marks the exact active blueprint version approved; revision reruns integration and evaluation; rejection regenerates from premise through the parallel specialists; and fork freezes the source lineage while creating an explicitly linked child checkpoint thread. Free-form instructions live once in secret-guarded application persistence while graph state and events carry only decision and artifact-version references. The FastAPI command endpoint and generated TypeScript SDK expose the same durable contract for Step 12. Evidence:
`engine/open_hollywood_engine/workflows/`,
`apps/api/open_hollywood_api/services/blueprint_workflow.py`,
`apps/api/open_hollywood_api/routes/blueprint_decisions.py`,
`migrations/versions/0004_human_interrupts.py`, generated contracts, and
workflow/API/persistence integration tests. Migration upgrade/downgrade and
metadata parity, Ruff, mypy, 86 pytest tests, Prettier, ESLint, TypeScript,
Vitest, and the production build pass.

12. [x] **COMPLETED 2026-07-23; INTAKE CORRECTED 2026-07-25; UX CORRECTED
2026-08-02; RUNTIME CORRECTED 2026-08-04 — Build the
workspace UI around persisted data.** The responsive three-panel React workspace
now lists durable projects and story artifacts, merges persisted chat with
workflow activity, presents current run and checkpoint status, and renders
immutable artifact bodies, version history, provenance, and evaluations without
introducing a manuscript editor. The empty library opens in the same workspace
shell with an actionable first-premise composer instead of a dead-end welcome
screen; its idempotent API command atomically persists the project, conversation,
user message, queued Story Blueprint run, and safe workflow event. The Story
Blueprint checkpoint supports approve, revise, reject, and fork through the
generated SDK. FastAPI boundaries assemble UI-safe project workspaces and
artifact details directly from SQLite while excluding checkpoints, prompts, and
secrets. Each desktop panel now exposes bounded independent scrolling, the
premise composer grows with its content, and stopped stories can be permanently
removed with their complete local workflow and artifact aggregate. Loading,
empty, disconnected, and mobile panel states are covered.
Evidence:
`apps/api/open_hollywood_api/services/workspace.py`,
`apps/api/open_hollywood_api/routes/workspace.py`, `apps/web/src/`, generated
contracts, and API/React tests. Ruff, mypy, 178 pytest tests, Prettier, ESLint,
TypeScript, 7 Vitest tests, and the production build pass.

The browser-runtime correction now composes FastAPI with one sequential local
workflow worker instead of launching the storage-only API. The worker claims
only ordinary queued stories, freezes the active complete Local, Cloud, or
Hybrid profile before the first invocation, resumes SQLite checkpoints, and
hands an approved Story Blueprint to the durable scene-production graph.
Pause, resume, stop, retry, and budget commands share a worker-owned command
boundary; stopping cancels the active execution task. Frozen benchmark runs are
excluded from interactive claiming and remain operator-owned. The API-only app
continues to fail closed with an actionable `503`. Evidence:
`apps/worker/open_hollywood_worker/`, the reusable profile-routed executors,
`apps/api/open_hollywood_api/services/workflow_commands.py`, runtime/API/React
regression tests, and updated launch documentation. Ruff, formatting, mypy,
181 pytest tests, Prettier, ESLint, TypeScript, 8 Vitest tests, and the
production build pass.

13. [x] **COMPLETED 2026-07-23 — Add Local, Cloud, and Hybrid model
presets.** Provider-neutral, schema-versioned preset contracts now route every registered Story Blueprint specialist to an exact local or cloud model. Local keeps all roles on-device, Cloud assigns all roles to cloud inference, and Hybrid keeps structured preparation and evaluation local while sending high-impact creative reasoning to cloud. The three presets are seeded idempotently into SQLite without guessed model names, cannot activate until every required model slot is configured, and resolve exact role assignments for future invocations. FastAPI exposes durable configuration, atomic activation, and failure-isolated dynamic Ollama catalog discovery; the responsive workspace settings surface uses the generated SDK and persists no credentials. Evidence: `engine/open_hollywood_engine/models/profiles.py`, `apps/api/open_hollywood_api/services/model_profiles.py`, `apps/api/open_hollywood_api/routes/model_profiles.py`, `apps/web/src/components/ModelSettings.tsx`, generated contracts, and engine/API/React tests. Ruff, mypy, 99 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

14. [x] **COMPLETED 2026-07-23 — Port the legacy character-agent dialogue
experiment into an isolated subgraph.** The preserved two-actor/director concept now runs as a fixed LangGraph topology: one director briefing, character one, character two, and one director evaluation per bounded round. Typed scene, actor, briefing, dialogue-turn, evaluation, and completion contracts replace legacy mutable state and provider-specific calls. Checkpoints contain only JSON-safe budgets, counters, profile identifiers, and exact immutable artifact references; model output bodies remain validated artifact versions. Minimum rounds, climax-or-resolution closure, declared endings, maximum rounds, timeouts, and retryable failures are enforced deterministically. Step 13 profiles upgrade in memory from schema v1 and route the registered `character_actor` and `dialogue_director` roles without breaking existing profiles. Regression tests use the preserved `legacy-v2-final` director-flow fixture to retain its one-briefing, two-actors-per-round, one-evaluation, and seven-call/two-round behavior. Evidence: `engine/open_hollywood_engine/workflows/dialogue_contracts.py`, `engine/open_hollywood_engine/workflows/dialogue_graph.py`, typed dialogue artifact schemas, and `tests/workflows/test_dialogue_subgraph.py`. Ruff, mypy, 106 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

15. [x] **COMPLETED 2026-07-23 — Implement the scene/chapter production
loop with bounded critique and revision.** The fixed `scene_production`
LangGraph consumes an approved Story Blueprint plus three-to-eight ordered
Scene Plan assignments, writes immutable prose versions, optionally embeds the Step 14 two-character dialogue subgraph and integrates its outputs, and sends each exact draft version to an independent critic. Non-passing drafts return to the writer only while the configured revision allowance remains; each canonical scene records whether it passed the rubric or reached the hard limit. Incomplete drafts, mismatched critique targets, reused versions, invalid artifact kinds, and malformed state fail closed. Checkpoints retain only budgets, counters, deterministic dispositions, and immutable artifact references—not prose, dialogue, critique bodies, prompts, or provider objects. Model-profile schema v3 adds `scene_writer` and `scene_critic` while upgrading Step 13 and Step 14 profiles in memory. The unit abstraction is ready for a later chapter format, while v0.1 remains intentionally limited to prose scenes. Evidence:
`engine/open_hollywood_engine/workflows/production_contracts.py`,
`engine/open_hollywood_engine/workflows/production_graph.py`, the typed
`SceneDraft` artifact, and `tests/workflows/test_scene_production.py`. Ruff,
mypy, 112 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

16. [x] **COMPLETED 2026-07-24 — Add deterministic story-bible updates and
continuity invariants after every accepted unit.** The fixed production graph now gates every candidate scene against the exact current Story Bible, Scene Plan, and Scene Draft versions before canonical acceptance. Error or blocking findings consume the shared bounded revision allowance and fail closed if they survive its hard limit; rubric-limit acceptance cannot bypass continuity. Each cleared scene produces a typed delta and a full immutable Story Bible successor that must equal the pure deterministic reducer exactly. Accepted-scene and timeline histories append monotonically, fact and event identifiers cannot be reused, entity references remain within the approved blueprint catalog, and resolved mysteries or setup/payoff promises cannot reopen. Later writers, dialogue passes, critics, and continuity checks receive the exact resulting bible version, while checkpoints retain only artifact references and deterministic routing state. Model-profile schema v4 registers local-friendly `continuity_supervisor` and `story_bible_maintainer` roles and upgrades versions 1–3 in memory. Evidence: `engine/open_hollywood_engine/artifacts/story_bible.py`, `engine open_hollywood_engine/workflows/production_graph.py`, `tests/artifacts/test_story_bible.py`, and `tests/workflows/test_scene_production.py`. Ruff, mypy, 120 pytest tests, Prettier, ESLint, TypeScript, 4 Vitest tests, and the production build pass.

17. [x] **COMPLETED 2026-07-24 — Add run controls: stop, pause, resume,
retry-from-node, and budgets.** Provider-neutral contracts define strict
aggregate run budgets and typed idempotent commands. SQLite now persists each command, pause reason, source checkpoint, and resulting run. Pause requests made during execution take effect before the next registered node; stop cancels the run and open invocations; resume continues from the durable checkpoint while keeping the Story Blueprint approval interrupt distinct. Story Blueprint retry-from-node prunes obsolete outputs, preserves compatible exact artifact versions, and creates an immutable linked child lineage. Failed production specialists can retry only their exact current node from the same durable checkpoint, preserving completed-scene artifacts and invocation history. Crash replay reuses the resulting run and checkpoint rather than duplicating completed work. Before every model-backed node, the runtime reserves model-call, input-token, output-token, and cost capacity and checks elapsed wall-clock time; exhaustion pauses with useful usage and limit events while preserving partial artifacts. FastAPI, the generated TypeScript SDK, and the workspace expose the same controls, current limits, and aggregate usage. Evidence:
`engine/open_hollywood_engine/workflows/run_controls.py`, `apps/api/open_hollywood_api/services/run_controls.py`, `apps/api/open_hollywood_api/routes/run_controls.py`, `migrations/versions/0005_workflow_run_controls.py`, generated contracts, workspace UI controls, and workflow/API/migration/React tests. Migration upgrade/downgrade and metadata parity, Ruff, mypy, 129 pytest tests, Prettier, ESLint, TypeScript, 5 Vitest tests, and the production build pass.

18. [x] **COMPLETED 2026-07-24 — Implement Fountain/Markdown renderers and
PDF/DOCX export.** A provider-neutral, invariant-checked manuscript contract
assembles only complete latest versions of approved Scene Draft artifacts in
unique, contiguous three-to-eight-scene order. The canonical Markdown renderer normalizes line endings and escapes structural markup. A separate typed Fountain screenplay contract renders title pages, forced headings and action, dialogue structures, transitions, sections, synopses, centered text, and page breaks without guessing script structure from prose. Searchable US-Letter PDF and editable US-Letter DOCX exporters use fixed metadata and canonicalized containers so identical inputs produce identical bytes. FastAPI exposes an export manifest, exact immutable source-version lineage, SHA-256 ETags, sanitized downloads, and fail-closed `409` behavior; the generated TypeScript SDK and workspace enable Markdown, PDF, and DOCX controls only for exportable projects. Evidence: `engine/open_hollywood_engine/rendering/`, `apps/api/open_hollywood_api/services/exports.py`, `apps/api/open_hollywood_api/routes/exports.py`, generated contracts, workspace export controls, and rendering/API/React tests. All four representative PDF pages and all four representative DOCX pages passed visual inspection. Ruff, mypy, 140 pytest tests, Prettier, ESLint, TypeScript, 5 Vitest tests, and the production build pass.

19. [~] **IN PROGRESS 2026-07-26 — Build the evaluation harness** and execute phased benchmark evaluation (Cloud-first scope adopted 2026-09-11 below; Local/Hybrid qualification deferred). The provider-neutral harness core now strictly validates the frozen 12-prompt v0.1 corpus and pins its canonical digest, exact graph and prompt-contract versions, direct-model baseline, complete secret-free Local/Cloud/Hybrid profile snapshots, and prompt seeds into a deterministic 48-case campaign plan. Sequential case execution is failure-isolated and resumable from terminal results; successful outputs must carry exact workflow-run, model-invocation, and immutable artifact-version lineage. The accepted weighted rubric and hard gates are executable contracts. Deterministic A/B packaging separates provenance-free reviewer documents from the private answer key, and reporting maps blind human preferences back to systems while calculating the accepted completion, continuity, quality, preference, and cost thresholds. The operator command validates corpus integrity and creates plans from fully configured persisted presets. The application layer now executes the direct single-model baseline through a bounded provider-neutral call and persists its frozen prompt, invocation, workflow, and immutable story lineage idempotently. Campaign reports checkpoint atomically after each case, failed cases retry only when explicitly requested, and operator-configurable Ollama timeouts support long-form calls while distinguishing provider timeouts from outages. Retrying after an interrupted process closes stale running baseline attempts and preserves their immutable input lineage. Ollama Cloud response aliases are accepted only when they normalize to the frozen requested model; requested and provider-reported identifiers are both persisted. Operator commands create separated public/private review packets and summaries from schema-validated evidence. Failed structured calls retain provider usage, finish reason, response hash, and length, while a lone JSON fence is normalized without accepting surrounding
commentary. Agentic cases now enter the real durable Story Blueprint graph:
every registered specialist resolves its exact frozen profile selection,
receives deterministic immutable inputs and benchmark constraints, uses schema enforcement when the deployment supports it, records a budgeted invocation plus output lineage, validates cross-artifact invariants, and pauses at the mandatory human approval interrupt. Replaying a paused case performs no duplicate model calls. Creative Brief prompt contract v6 requests only creative choices and the application deterministically attaches the frozen premise, format, genres, maturity, required elements, and forbidden elements; this keeps optional model fields from weakening benchmark intent. Prompted non-schema invariants preserve exact benchmark constraints; parallel World specialists cannot invent unresolved character references; the integrator emits only new beats and scene plans, and the application deterministically assembles immutable specialist artifacts into the Story Blueprint. Prompt contract v9 binds integration to a compact world summary, the Creative Brief's exact scene count, and no more than two beats per scene. Prompt-only cloud structured-output retries
persist their attempt number and receive safe validation locations plus provider finish metadata without storing or echoing the failed story response. Word bounds remain application-validated instead of emitting grammar keywords unsupported by local Ollama structured output. Model-executing operator commands now reject a campaign plan when its baseline, Blueprint, production prompt, or graph versions differ from the running build, including the direct-story graph and nested dialogue subgraph. Blueprint graph v4, scene-production graph v2, and dialogue
subgraph v2 give model-backed nodes a 900-second formal long-form ceiling while retaining bounded execution; cancelled or timed-out calls now close their persisted invocation instead of remaining `RUNNING`. A 12-case Local
qualification reached the mandatory approval interrupt while prompt contracts v6 through v9 were being hardened. A subsequent frozen v9 staging campaign completed all 12 Baselines after one explicit provider-timeout retry, paused all 12 Local Blueprints, and paused 9 Cloud Blueprints before exposing the prior 120-second graph-node ceiling on Cloud OH-010. Both campaigns are diagnostic evidence only and must not be sealed as the final frozen campaign. Operators can prepare selected cases independently. Batch preparation now isolates terminal Blueprint failures and continues with sibling cases; production reporting pre-seeds those failed cases while still requiring explicit approval for every surviving Blueprint. The July 31 replacement campaign completed all 12 Baselines
without retry. After the operator-level failure-isolation repair was merged, Blueprint staging resumed and settled every agentic case with no open workflow or invocation: Local paused 11 of 12 at approval and retained OH-008 as a terminal integration failure after twice emitting the unknown literal location ID `null`; Cloud paused all 12 at approval; Hybrid paused 7 of 12 and retained terminal failures for OH-006, OH-008, and OH-010 at integration, OH-009 at the World specialist, and OH-012 at the Character specialist after bounded structured-output repair. No Blueprint has been approved on the operator's behalf. The current staging yield is therefore 30 of 36 agentic cases (83.3%), which cannot meet the accepted 95% technical-completion threshold unless failed cases are explicitly rerun successfully or superseded by a new frozen campaign.
An August 1 frozen replacement campaign changed only the Hybrid cloud model from Nemotron to `gemma4:31b-cloud` while retaining the same accepted graph and prompt-contract versions. Its Baseline completed 12 of 12 after one explicit retry recovered an OH-009 provider HTTP 500; Local paused 11 of 12 at approval and retained OH-006 as a terminal integration failure after invalid cross-specialist character references and missing scene-plan beats exhausted bounded repair; Cloud paused all 12; and Hybrid paused all 12, with one invalid Cloud integration response recovered by bounded repair. All 35 surviving Blueprints remain at the mandatory approval checkpoint and no campaign workflow or invocation remains active. The 35-of-36 Blueprint staging yield is 97.2%, above the accepted 95% technical-completion threshold; final technical completion remains contingent on approved production finishing those cases.
The approved handoff now materializes exact Scene Plan versions and an initial canonical Story Bible, creates a child production run, and invokes the real SQLite-checkpointed writer, critic, continuity, and bible-maintainer graph. Production nodes reserve durable graph/call/token/cost budgets, profile-routed structured calls persist exact input lineage, accepted scene deltas advance the Story Bible through the deterministic reducer, and successful task fingerprints replay without duplicate calls. A final deterministic assembly persists the complete benchmark story and returns its Blueprint, accepted-scene, final-bible, manuscript, invocation, usage, latency, cost, and hard-gate evidence as `BenchmarkOutput`. The mandatory Blueprint approval remains fail-closed, and production pauses before a call that would exceed its reserved budget. The resumable operator flow now stages all Local, Cloud, and Hybrid Blueprint cases, requires explicit per-case approval, then runs approved production into the same atomically checkpointed report. An offline operator command now packages every surviving paused Blueprint, frozen prompt, and exact automated critique into a deterministic JSON packet plus readable Markdown dossier and reviewer CSV. The completed form must affirm every surviving case and preserve its campaign, plan, packet, workflow, artifact-version, and content-digest fields; approval rejects incomplete or stale review evidence and records the reviewer, packet digest, and exact Blueprint lineage durably before resolving each interrupt without enabling model calls. Frozen Ollama deployment routing supports cloud models through a signed-in local daemon or a runtime-secret-backed direct cloud endpoint, including split local/cloud Hybrid execution. Reviewer-specific CSV forms and provenance-free Markdown guides now carry the canonical rubric, score anchors, and hard gates; strict import merges completed forms while rejecting incomplete, duplicate, foreign-campaign, or unknown-comparison evidence. Review schema v2 binds every submission to the exact public-packet digest, which reporting verifies against the separately stored private answer key. Complete evidence can now be sealed into a deterministic archive only when
every planned case has a terminal result, every blinded comparison has human review coverage, and the corpus, plan, report, packets, reviews, declared budget, and recomputed summary agree. Its manifest records fixed public/private paths, counts, and per-member SHA-256 digests; independent verification reproduces the canonical archive and rejects tampering or partial evidence.

**Current status — 2026-10-04:** the September formal Cloud-versus-baseline campaign has
completed generation and all eleven eligible human comparisons; its reviewed
evidence is sealed and verified. All 22 September manual story reviews are also
complete and stored in the repository. **Item 5 is COMPLETE as a repeatability
assessment and evidence-sealing task.** All three prospective campaigns and all
34 eligible human comparisons are reviewed, sealed and independently verified,
with a consolidated evidence register. Cloud completion was 12/12, 12/12 and
10/12; all 36 baselines completed. Weighted Cloud scores were 4.05, 4.1167 and
4.16, while preference was 54.17%, 37.5% and 45%, below the unchanged 60% threshold
in every repeat. Repeat 3 failed technical acceptance on OH-V01-002 and OH-V01-010.
Its reviewed ten-pair score is 4.16 Cloud versus 4.15 baseline. The October 2
reviewer calibration and authorized Ollama 0.35.1 exception in repeat 3 remain
explicit; the original 0.35.0 freeze and historical seals are preserved.
Step 19 remains **IN PROGRESS** for inconsistent technical acceptance, unmet
preference and unknown monetary cost. Repeated acceptance has not been demonstrated.
The reviewer's character-depth, recurring-prose and group-dynamics concerns are
recorded as qualitative evidence without changing scores, criteria or the endpoint.
Local/Hybrid qualification remains deferred under the adopted Cloud-first scope.
The two Repeat 3 continuity response-contract failures have a v34 implementation
with offline regression evidence and two first-attempt-valid Cloud probes,
documented in the October 4 entry below. Both probes retained a blocker; semantic
judgment and full-story recovery remain unqualified. Sealed v33 results are unchanged.
The dated entries below retain their original checkpoint context; the
[September 30 completion entry](#human-reviews-recorded-and-formal-evidence-sealed--2026-09-30)
supersedes earlier pending-review status for these manual and formal outputs.

Evidence so far:
`benchmarks/v0.1/corpus.json`,
`engine/open_hollywood_engine/evaluations/`,
`engine/open_hollywood_engine/evaluations/evidence.py`,
`engine/open_hollywood_engine/evaluations/reviews.py`,
`apps/api/open_hollywood_api/services/agentic_benchmark.py`,
`apps/api/open_hollywood_api/services/blueprint_model_executor.py`,
`apps/api/open_hollywood_api/services/evaluation_campaign.py`,
`apps/api/open_hollywood_api/services/evaluation_execution.py`,
`apps/api/open_hollywood_api/services/production_model_executor.py`,
`apps/api/open_hollywood_api/services/production_workflow.py`,
`engine/open_hollywood_engine/models/routing.py`,
`scripts/evaluation_harness.py`, and `tests/evaluations/`.

The benchmark now treats its 2,500–5,000-word range as advisory creative
guidance rather than a proxy for completion or short-prose format. Every new
output records a validated non-gating adherence measurement, automatic
completion checks only whether the document is present and ends normally, and
human reviewers decide the short-prose format gate. Older resumable reports and
immutable story artifacts remain readable; advisory deviation alone cannot turn
a technically completed story into a failed case.

An August 19 Local v7 regression diagnostic reused the approved August 1
pre-production lineage and ran the first six-case Local batch. The five
runnable production cases fell from four prior v1 successes to one v7 success;
three regressions began when non-final continuity calls treated story-wide
requirements as current-scene blockers, and their re-checks then failed the
text-signature stagnation guard. The preserved diagnostic is not final
benchmark evidence. Scene-production prompt contract v8 now gives continuity a
deterministic applicability packet: non-final scenes receive opaque IDs but not
the text of requirements deferred until the ending, while the final scene
receives the exact frozen required elements and forbidden shortcuts as due-now
gates. Exact Scene Plan requirements remain immediate. Typed continuity
re-check disposition, repair assessment, and revised-draft evidence replace
lexical-difference inference, while Local remains fail-closed and the persisted
Hybrid-only stagnation escalation remains bounded. Regression coverage asserts
non-final/final constraint visibility, permits the same exact quotation when a
repair assessment says the passage was unchanged, and preserves Local, Cloud,
and Hybrid routing behavior. Evidence:
`docs/benchmark_reports/step-19-local-v7-regression-2026-08-19.md`,
`engine/open_hollywood_engine/artifacts/schemas.py`,
`engine/open_hollywood_engine/workflows/production_contracts.py`,
`apps/api/open_hollywood_api/services/production_model_executor.py`, and
`tests/evaluations/test_agentic_production.py`. The isolated v8 canary database
was copied byte-for-byte from the approved pre-production snapshot, migrated to
schema 0007, and frozen into a 48-case plan with canonical digest
`2e1a76a7fec7cec9b408e08c5e65632d0aabf62f7f93a4c1734734bb5298c788`.
Its first six-case Local batch completed two of five production-runnable cases;
OH-V01-006 retained its terminal Blueprint failure. The two successes passed all
automated hard gates at 3,579 and 3,621 words. Two failures exhausted continuity
structured-output repair after ordinary application diagnostics collapsed to
`$:ValueError`; a third recovered continuity but exhausted Story Bible repair on
unknown canonical fact and location IDs. Prompt contract v9 now persists a
redacted, bounded diagnostic envelope with exact output-field locations,
validation types, and messages without retaining provider response bodies. The
one bounded Local retry receives those focus locations plus operation-specific
continuity and Story Bible schema-repair rules. Cloud retries remain unchanged,
and an audited Hybrid continuity-stagnation retry drops Local guidance when it
escalates to Cloud. The v8 canary remains immutable diagnostic evidence; another
batch requires a new plan pinned to prompt v9. Evidence:
`docs/benchmark_reports/step-19-local-v8-canary-2026-08-20.md`.
The fresh v9 canary plan has canonical digest
`83ffb10a8a1ca02f115ac0e4077e7a514cd8362fed9894790cc353a8293521b1`.
Its first Local batch completed one of five production-runnable cases; OH-V01-004
produced 3,365 words within target and passed every automated hard gate, while
OH-V01-006 retained its terminal Blueprint failure. All four terminal Production
failures were initial continuity calls that populated fields intended only for
re-checks. Prompt contract v10 now derives an explicit `initial_check` or
`recheck` schema from immutable input lineage, removes all three re-check-only
fields and their enum definition from the initial schema, and withholds re-check
instructions until a prior Continuity Report is present. The same selected
schema is used in the prompt and Local provider grammar, and its variant is
persisted for replay diagnostics. Canonical artifacts, bounded repair, Cloud
routing, and Hybrid-only escalation are unchanged. The v9 canary remains
immutable diagnostic evidence; another batch requires a new plan pinned to
prompt v10. Evidence:
`docs/benchmark_reports/step-19-local-v9-canary-2026-08-20.md`.
The fresh v10 canary plan has canonical digest
`f985ae1b5976836952451a3011126c796e6e65773339f3b5b933bbfe5c24ee53`.
Its first Local batch completed one of five production-runnable cases;
OH-V01-004 produced 3,455 words within target and passed every automated hard
gate, while OH-V01-006 retained its terminal Blueprint failure. The v9
initial-check regression did not recur. OH-V01-002 and OH-V01-005 instead
exhausted repair after blocking findings omitted `recommended_resolution`;
OH-V01-001 and OH-V01-003 reached the revision limit after continuity re-checks
used non-exact evidence or copied stale assessments despite materially changed
drafts. Prompt contract v11 now uses severity-discriminated finding branches:
error/blocking branches require a non-empty resolution and the model cannot emit
the application-owned `blocks_approval` field, while advisory branches may omit
the resolution. Re-check blocker branches additionally require disposition,
assessment, and revised evidence together. Boundary validation proves every
revised-evidence item is an exact current-draft excerpt, rejects a copied prior
assessment when evidence changes, and requires an explicit explanation for
unchanged evidence. Exact story-wide benchmark requirements duplicated into a
non-final Scene Plan are deferred and removed from the continuity prompt view;
other Scene Plan requirements remain immediate. Canonical persisted artifacts,
bounded repair, Cloud routing, and Hybrid-only escalation are unchanged. The
v10 canary remains immutable diagnostic evidence; another batch requires a new
plan pinned to prompt v11. Evidence:
`docs/benchmark_reports/step-19-local-v10-canary-2026-08-23.md`.
The fresh v11 canary plan has canonical digest
`a71a83a87092f7d095b96918b5dc8503f90508e45d524c5220ab7ccdc6400489`.
Its first Local batch completed two of five production-runnable cases;
OH-V01-003 produced 4,061 words and OH-V01-004 produced 2,992 words, with both
passing every automated hard gate. OH-V01-006 retained its terminal Blueprint
failure. The v11 schema split and resolution guarantee held, but the remaining
Production failures exposed three contract/routing gaps: missing requirements
and absent forbidden shortcuts could fabricate draft evidence; world-rule
findings could ignore explicit companion-rule authorization; and critic-only
revisions could consume the revision allowance before continuity ran. Prompt
contract v12 separates the three blocking bases, validates exact evidence on
initial calls and re-checks, binds requirement and canonical rule IDs, and
prevents an explicitly authorized world condition from blocking. Production
graph v3 runs critic and continuity on every candidate and schedules at most one
revision after consolidating both results. Benchmark failures now surface the
redacted persisted Production cause. The v11 canary remains immutable evidence;
the next canary requires a new plan pinned to graph v3 and prompt v12. Evidence:
`docs/benchmark_reports/step-19-local-v11-canary-2026-08-24.md`.
The fresh v12 canary plan has canonical digest
`b6e25db3c372676bb2973db6305aa360ddc06ee8c4c95189f273f570842be396`.
Its first Local batch completed none of five production-runnable cases;
OH-V01-006 retained its terminal Blueprint artifact-contract failure. All five
Production failures stopped at continuity. Persisted invocation diagnostics
showed ten exact-evidence failures, three canonical-source-reference failures,
and two length-truncated JSON responses across 24 continuity attempts. Prompt
contract v13 retains production graph v3 while replacing free-form evidence
copying with deterministic candidate-draft evidence handles and replacing broad
raw-ID provenance with bounded canonical claims carrying exact immutable source
paths. The call-specific Local schema constrains evidence, canonical source,
due requirement, and World Rule selections to exact enums; advisory findings
cannot emit evidence, prior accepted drafts are explicitly context-only, and
application-owned report lineage is absent from model output. The application
resolves evidence handles into exact canonical artifact excerpts before existing
artifact and routing validation. The v12 canary remains immutable diagnostic
evidence; another batch requires a new plan pinned to graph v3 and prompt v13.
Evidence: `docs/benchmark_reports/step-19-local-v12-canary-2026-08-25.md`.
The fresh v13 canary plan has canonical digest
`323c3a91850be72a4c09ef6911e39ccb59c0f27abfc3abf1441270a164c01a98`.
Its first Local batch completed none of five production-runnable cases;
OH-V01-006 retained its terminal Blueprint artifact-contract failure. Prompt
v13 eliminated the v12 exact-evidence, canonical-source, requirement-ID, and
truncated-JSON failures. The 13 remaining failed continuity calls instead
exposed overlap in each blocking branch: six omitted a companion-rule
assessment, three omitted or invented World Rule IDs, two misrepresented
explicit authorization, one attached world-only fields to a non-world finding,
and one re-check repeated a stale blocker. Prompt contract v14 retains
production graph v3 and splits contradiction, missing-requirement, and
forbidden-shortcut blockers into explicit world-rule and non-world branches for
both initial checks and re-checks. World branches require enum-constrained rule
IDs, a non-empty companion-rule assessment, and
`condition_explicitly_authorized=false`; non-world branches omit all three
world-analysis fields. Benchmark failure reporting now reads the terminal
failed invocation's exact redacted diagnostic before falling back to the
workflow error, so `report.json` records the actionable field-level cause. The
v13 canary remains immutable diagnostic evidence; another batch requires a new
plan pinned to graph v3 and prompt v14. Evidence:
`docs/benchmark_reports/step-19-local-v13-canary-2026-08-25.md`.
The fresh v14 canary plan has canonical digest
`61a3c33ae850c1bb9b7f030b896d362ceb8d2411770acc3354cde0357461b2ac`.
Its first Local batch completed none of five production-runnable cases, while
OH-V01-006 retained its terminal Blueprint artifact-contract failure. Prompt
v14 eliminated all v13 missing/invalid World Rule ID, missing companion-rule
assessment, invalid authorization-state, and non-world/world-field crossover
failures. OH-V01-001 stopped after repeated continuity re-check stagnation;
OH-V01-002 recovered one such structured failure but ultimately retained a
blocker at the revision limit. OH-V01-003, OH-V01-004, and OH-V01-005 accepted
two, one, and one scenes respectively before later continuity inputs exceeded
the unchanged 20,000-token per-call ceiling. A representative v14 initial
schema is 70.2% larger than v13 and the corresponding re-check schema is 70.6%
larger, so compacting the cross-product contract is the leading response rather
than immediately widening the budget. Exact report diagnostics worked for
terminal failed invocations, but OH-V01-002 exposed a precedence defect: its
recovered failed invocation masked the later specific workflow terminal cause.
The database passed integrity checking and retained no running workflow or
invocation. Evidence:
`docs/benchmark_reports/step-19-local-v14-canary-2026-08-26.md`.
Prompt contract v15 retains graph v3 and implements the v14 evidence response.
It composes one shared blocking-finding object with independent nested
basis/category detail unions instead of six duplicated full objects. The
representative initial schema falls from 14,270 to 5,792 UTF-8 bytes (59.4%)
and the re-check schema from 15,733 to 6,543 bytes (58.4%), with no `allOf`
dependency because the Local model did not reliably enforce that keyword.
Local user messages no longer duplicate the schema already sent through
Ollama's enforced format channel; Cloud and Hybrid cloud calls retain the
inline schema contract. Invocation telemetry now separates content-free size,
digest, and estimated-token contributions for system instructions, artifacts,
control data, retry/repair context, inline schema, and gateway schema, and
persists provider usage on over-budget failures with exact observed-versus-limit
diagnostics. Re-check evidence carries an explicit changed/unchanged/newly
exposed state that is checked against prior exact evidence and stripped before
canonical artifact persistence. Finally, report cause selection gives a
specific terminal workflow error precedence over a recovered failed
invocation, using invocation detail only for absent or generic workflow
wrappers. A new canary must use a fresh plan pinned to graph v3 and prompt v15.
Ruff and formatting pass over 133 files, strict mypy passes over 133 source
files, all 224 pytest tests pass, frontend formatting/lint/type checking pass,
all 10 Vitest tests pass, and the production build succeeds.
The first Local v15 canary then completed no cases: OH-V01-006 retained its
Blueprint failure, while all five production-runnable cases stopped at
continuity after accepting four scenes in total. The compact schema and explicit
world-rule branches held, but eight continuity invocations were rejected by the
model-authored re-check-state contract, OH-V01-002 retained a blocker at the
revision limit, and OH-V01-004 used 20,163 input tokens against the unchanged
20,000-token ceiling. Four invalid model-authored critic overall scores recovered
on retry. Evidence:
`docs/benchmark_reports/step-19-local-v15-canary-2026-08-28.md`.
Prompt contract v16 retains graph v3 and separates all due Scene Plan obligations
into an exhaustive application-validated coverage audit with stable IDs. Missing
requirements no longer share the contradiction union; the application derives
their canonical identity, category, lineage, and routing state, while
contradictions require an affirmative current-draft conflict with bounded canon.
Re-check evidence change is application-owned, unchanged exact blockers remain
valid graph feedback, and changed evidence paired with copied assessment yields
a granular safe reason code. Canonical source claims are grouped, continuity sees
at most the immediately prior accepted scene ending, and critic overall score is
the deterministic arithmetic mean of bounded rubric scores. The per-call input
ceiling remains 20,000 tokens so the next fresh canary isolates these prompt and
context changes.
Ruff and formatting pass over 133 files, strict mypy passes over 133 source
files, all 226 pytest tests pass, frontend formatting/lint/type checking pass,
all 10 Vitest tests pass, and the production build succeeds. No v16 canary was
started as part of this implementation change.
The first Local v16 canary then completed no cases, while OH-V01-006 retained its
Blueprint failure. The five production-runnable cases nevertheless reached
their final scenes and accepted 18 scenes, with 91 of 103 production calls and
21 of 33 continuity calls succeeding. No critic or input-budget failure
occurred, and the largest continuity input was 12,558 tokens. Terminal causes
were limited to incomplete model-authored coverage partitions, invalid
model-authored re-check dispositions, one application validator that rejected a
valid missing Scene Plan scalar obligation, and one changed-evidence assessment
heuristic. Evidence:
`docs/benchmark_reports/step-19-local-v16-canary-2026-08-29.md`.
Prompt contract v17 retains graph v3 and the 20,000-token ceiling. The
application now supplies one deduplicated due requirement catalog plus a
separate forbidden-shortcut catalog. Every due required ID is a schema-required
property of `requirement_coverage`, eliminating structurally valid omissions;
missing entries materialize canonical findings for benchmark and Scene Plan IDs
alike. Contradiction categories are nested in their basis and exclude
`constraint`, while forbidden category is application-owned. Re-check blockers
may reference an exact prior ID, but canonical identity and disposition are
derived by the application. Copied assessment after changed evidence is
non-terminal content-free advisory telemetry while exact draft evidence remains
mandatory. Regression coverage exercises the five v16 terminal patterns. Ruff
and formatting pass over 133 files, strict mypy passes over 133 source files,
all 230 pytest tests pass, frontend formatting/lint/type checking pass, all 10
Vitest tests pass, and the production build succeeds. No v17 canary was started
as part of this implementation change.
The first Local v17 canary subsequently completed OH-V01-002 and OH-V01-004,
the first recent Local production completions. Across the five runnable cases,
81 of 87 production calls and 22 of 26 continuity calls succeeded; every v16
coverage-partition failure disappeared. OH-V01-001 exposed a deterministic
collision between application-generated positional new-finding IDs across
consecutive re-checks. OH-V01-003 and OH-V01-005 reached the revision limit
after critic-passing revisions were blocked by continuity: one promoted pacing
and an intended anomaly to World Rule violations, while the other treated a
character goal as a guaranteed outcome despite an explicitly unresolved Scene
Plan exit state. OH-V01-006 retained its Blueprint failure. Evidence:
`docs/benchmark_reports/step-19-local-v17-canary-2026-08-30.md`.
Prompt contract v18 retains production graph v3 and the bounded revision policy.
Re-check output now contains an exhaustive object keyed by every exact prior
non-requirement blocker plus a separate new-finding array; the application
derives prior disposition and revision-scoped new IDs, eliminating positional
collisions and duplicate prior references. Requirement catalog policy v2 adds
per-entry satisfaction modes and companion IDs, distinguishing meaningful goal
pursuit from outcome achievement. World Rule blockers require exact rule-source
provenance, an explicit prohibition/required-condition violation kind, and a
direct logical-conflict assessment; pacing and dramatic framing are routed away
from continuity. Exact duplicate missing-requirement summaries or repairs cannot
also block as contradictions. Regression coverage reproduces all three v17
production terminal mechanisms. Ruff and formatting pass over 133 files, strict
mypy passes over 133 source files, all 236 pytest tests pass, frontend formatting,
lint, and type checking pass, all 10 Vitest tests pass, and the production build
succeeds. No v18 canary was started as part of this implementation change.
The first Local v18 canary subsequently completed OH-V01-002, OH-V01-003, and
OH-V01-004, raising production-runnable completion from two of five to three of
five and accepted scenes from 13 to 18. It produced no revision-limit failure,
and OH-V01-003 specifically validated the v18 semantic direction by completing
after v17 had promoted intended pacing and World Rule behavior to blockers.
Continuity structured-output success fell from 22 of 26 calls to 18 of 25,
however. A text-overlap exclusivity validator fired six times across four cases;
OH-V01-001 and OH-V01-005 terminated after Local repair, and OH-V01-005 first
reported a separate World Rule ID/source mismatch. Its earlier attempt remained
visible in SQLite but not in the final report. Evidence:
`docs/benchmark_reports/step-19-local-v18-canary-2026-08-31.md`.
Prompt contract v19 retains production graph v3. World Rule source provenance is
now derived deterministically from model-selected canonical rule IDs. Exact
duplicate missing summary-and-repair pairs consolidate into the keyed missing
blocker, while one shared text field alone cannot invalidate an independently
evidenced contradiction. Local repair policy v2 provides issue-specific actions
and exact required key sets without retaining failed response content. Failed
benchmark cases now serialize every safe persisted invocation failure in ordered
`failure_history`, preserving earlier attempts alongside the concise terminal
cause. Regression coverage reproduces the v18 terminal mechanisms and verifies
the derived provenance, deterministic consolidation, compact Local grammar,
focused repair packet, and resumable report serialization. No v19 canary was
started as part of this implementation change. Ruff and formatting pass over
133 files, strict mypy passes over 133 source files, all 238 pytest tests pass,
frontend formatting, lint, and type checking pass, all 10 Vitest tests pass,
and the production build succeeds.
The first Local v19 canary subsequently completed OH-V01-002 and OH-V01-003,
for two of five production-runnable cases and 15 accepted scenes. This was a
completion regression from v18, although production-call reliability improved
to 95 of 98 and continuity-call reliability improved to 26 of 29. OH-V01-001
and OH-V01-004 reached the revision limit despite exact time-of-day evidence;
their contradiction sources could resolve to unrelated timeline or Scene Plan
title material. OH-V01-005 also showed that generic coverage statuses allowed a
`pursue` goal to be evaluated as if achievement were required. The v19 ordered
failure history correctly preserved failed-attempt diagnostics. Evidence:
`docs/benchmark_reports/step-19-local-v19-canary-2026-09-01.md`.
Prompt contract v20 retains production graph v3 and the existing revision
limit. Non-world contradictions now select typed canonical claims whose source,
category, entity/scene lineage, and optional requirement lineage are validated
and materialized by the application; Scene Plan titles are not selectable
claims. Requirement coverage uses satisfaction-mode-specific positive/negative
statuses and exact positive draft evidence, with application-owned severity.
Entry-state and time-context omissions are advisory unless an independent
affirmative contradiction exists. Exact requirement lineage deterministically
consolidates missing/contradiction duplicates regardless of paraphrase. Compact
rechecks carry only resolution state, assessment, and current evidence while
the application rehydrates persisted finding details. Local repair policy v3
provides typed claim/category/lineage guidance. Regressions reproduce the v19
time evidence, pursue semantics, irrelevant-title provenance, and revision
grammar failures. Ruff and formatting pass over 125 files, strict mypy passes
over 125 source files, all 246 pytest tests pass, frontend formatting, lint, and
type checking pass, all 10 Vitest tests pass, and the production build succeeds.
No v20 canary was started as part of this implementation change.
The first Local v20 canary subsequently completed none of the five
production-runnable cases and accepted only two scenes, regressing from v19's
two completions and v18's three. Production-call reliability fell to 48 of 53
and continuity-call reliability to 14 of 19. The v20 initial and recheck schema
sizes roughly doubled relative to v19, Scene Plan requirements could be
represented both as keyed coverage and selectable contradiction claims, and
model-authored deterministic metadata produced category and lineage failures.
Evidence: `docs/benchmark_reports/step-19-local-v20-canary-2026-09-02.md`.
Prompt contract v21 retains production graph v3 and the bounded revision policy.
Scene Plan obligations are now exclusive to an exhaustive keyed
`met`/`partial`/`absent` coverage partition; exact draft evidence supports met
and partial results, while absence records a negative search outcome without a
fabricated excerpt. Partial and qualitative Scene Plan coverage is advisory,
and only absent application-owned hard requirements block. Non-World-Rule
contradictions select one compact semantic claim and World Rule findings use a
separate compact rule catalog. The application derives category, provenance,
lineage, and stable semantic finding IDs, then consolidates semantically
repeated recheck findings regardless of wording. Local repair policy v4 sends
only path-specific allowed keys or enums and a focused action. Regression
coverage exercises exclusive requirement routing, application-owned metadata,
shared coverage statuses, partial evidence, qualitative advisory policy,
semantic duplicate suppression, and compact Local repair. No v21 canary was
started as part of this implementation change. Ruff and formatting pass over
133 files, strict mypy passes over 85 source files, all 252 pytest tests pass,
frontend formatting, lint, and type checking pass, all 10 Vitest tests pass,
and the production build succeeds.
The mixed v21 canary plan, digest
`0a85c406fe24a19683f30b644826b5bfe5df7fd4670ede5d6bd366bc62cfe5e3`,
then completed two of five Local production-runnable cases and one of four
Cloud cases. Local OH-V01-003 reached all 40 reserved calls and paused before
its Story Bible update; Local OH-V01-001 and OH-V01-002 retained different
continuity blockers at the revision limit. Cloud OH-V01-002 and OH-V01-003
failed exact requirement-coverage evidence selection after bounded repair, and
Cloud OH-V01-004 reported 21,161 provider input tokens against the 20,000-token
allowance. The known Local OH-V01-006 Blueprint failure remained outside
production. Manual Cloud runs then exposed two product-runtime defects: a
failed production node had no same-node retry control, and regenerating an
approved Blueprint with stable Scene Plan IDs but changed content collided with
the project-level deterministic version-one handoff artifact. Because the
handoff failed before a child production row existed, the worker repeatedly
selected the same approved Blueprint and starved a later approved story.
Prompt contract v21 and production graph v3 remain pinned while the runtime is
hardened. The aggregate budget now derives ten calls per scene from
`3 * (1 + maximum_revision_cycles) + 1`; Cloud-capable profiles receive a
bounded 24,000-token per-call input allowance. The inline continuity grammar
shares one draft-evidence enum, exact excerpt values normalize only when they
map unambiguously to a catalog handle, and invalid values appear in bounded,
secret-redacted field diagnostics. Deterministic handoff artifacts append
Blueprint-lineage versions, handoff errors persist a failed production child,
and the UI distinguishes Blueprint from Production while allowing failed
production to retry only its exact durable node. Regression coverage exercises
the regenerated-Blueprint collision, idempotent version replay, terminal
handoff state and worker de-duplication, production checkpoint retry, corrected
call budget, compact evidence references, exact-excerpt normalization, bounded
invalid-value diagnostics, and the React retry control. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v21-canary-2026-09-03.md`,
`apps/api/open_hollywood_api/services/production_workflow.py`,
`apps/api/open_hollywood_api/services/production_model_executor.py`,
`apps/worker/open_hollywood_worker/runtime.py`, and
`tests/api/test_production_workflow_hardening.py`. Ruff and Python formatting
pass, strict mypy passes over 134 source files, all 257 pytest tests pass,
frontend formatting, lint, and type checking pass, all 11 Vitest tests pass,
and the production build succeeds.
Five subsequent manual Cloud stories on prompt v21 and production graph v3
confirmed that all terminal failures shared continuity evidence-handle
validation rather than writer or critic failure. The catalog emitted
four-digit handles such as `draft_evidence_0021`, while Gemma repeatedly
shortened them to forms such as `draft_evidence_021`; exact-node retry correctly
resumed the durable checkpoint but repeated the deterministic mismatch. The
runtime now zero-pads one-to-four-digit numeric aliases only when the resulting
canonical handle exists in the current catalog, retaining exact validation for
unknown values. Workspace read models expose the latest safe specialist
diagnostic, and project summaries include workflow phase and node. The React
client derives the selected sidebar entry from its polled workspace, polls
active project summaries, and labels statuses as Blueprint or Production so a
terminal center state cannot remain paired with a stale sidebar state. Prompt
v21 and graph v3 remain pinned. All 262 pytest tests pass, Ruff lint and format
checks pass across 134 files, strict mypy passes across 134 source files, all 11
Vitest tests pass, frontend formatting, lint, and type checking pass, and the
production build succeeds. No canary was started as part of this runtime and UI
hardening change.
Manual exact-node retry then completed all four previously failed Cloud stories,
validating the evidence-handle and durable-retry fixes against those persisted
checkpoints. Two fresh Local stories, `The Chronophage` and `The Unblinking
Bloom`, still reached the revision limit after structurally valid calls because
continuity promoted qualitative causal/dramatization feedback into canonical
contradictions and could treat planned or open-ended Blueprint material as
established canon. Prompt contract v22 retains production graph v3 and the
bounded revision policy while narrowing contradiction authority to stable
canonical claims. New non-world blockers require an exact draft assertion, a
category-specific conflict kind, the conflicting attribute, a direct logical
conflict assessment, and a corrective rather than additive repair action.
Qualitative/additive contradiction attempts are deterministically advisory;
keyed requirement coverage owns duplicate obligation feedback, including
partial coverage; and newly exposed re-check blockers must cite evidence added
or changed by the revision. The exact preceding draft is attached to persisted
invocation lineage for that application-side check without enlarging the model
prompt. Regression coverage reproduces both Local failure shapes and preserves
real direct-conflict blocking. Ruff lint and formatting pass across 134 files,
strict mypy passes across 134 source files, all 268 pytest tests pass, frontend
formatting, lint, and type checking pass, all 11 Vitest tests pass, and the
production build succeeds. No canary was started as part of this prompt-v22
hardening change. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v21-canary-2026-09-03.md` and
`docs/benchmark_reports/manual-v21-story-diagnostics-2026-09-03.md`.

The prompt-v22 canary then completed zero of five production-runnable Local
cases and three of four Cloud cases. All six production-terminal failures were
initial continuity application-validation failures in the redundant non-world
direct-conflict certificate: five `conflict_kind` mismatches, four lexical
`logical_conflict_assessment` failures, and three exact-copy `draft_assertion`
failures across twelve attempts. No retry recovered a case. Compact continuity
inputs and schemas stayed substantially below the corrected Cloud allowance,
and genuine World Rule repairs still converged, so prompt v23 retains graph v3
while removing the failure-prone duplication. The model now selects one typed
canonical claim, exact draft evidence handles, a direct-conflict disposition,
and a corrective action; the application derives category, conflict kind,
provenance, lineage, and exact assertion. Optional explanation text is not
lexically gated. Focused schema repair is provider-neutral and includes safe
expected/received values. Writers and critics receive an application-derived
story-wide advisory length packet, and word-count-only critic findings cannot
become revision gates unless an explicit hard scene constraint exists.
Regression coverage preserves real World Rule and structural-critique
blocking. The prompt-v23 acceptance criteria and subsequent results are
recorded below. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v22-canary-2026-09-04.md`.

The prompt-v23 canary completed six of nine production-runnable cases, versus
three of nine for v22. It removed every v22 redundant-certificate terminal
failure, raised structurally valid continuity attempts to 49/51 (26/26 Local),
and kept all six completed stories within the advisory word range. Local
OH-V01-001 still exhausted revisions through semantic repair ping-pong; Local
OH-V01-003 replaced an accepted scene assignment with future-scene material
after a near-total rewrite while its critic returned PASS. Local OH-V01-002's
pause coincided with Windows correcting a two-hour dual-boot host-clock error
and is recorded as environmental rather than an application defect. Production
graph v4 and prompt v24 now scope Blueprint prompt context to the current scene,
promote explicit viewpoint and scene-assignment drift to blocking critique,
enforce a 0.35 prior-draft similarity floor for continuity-only repair, retain
bounded cumulative per-scene continuity history, preserve stable IDs for
semantic recurrences, narrow Blueprint contradiction claims, and persist
cause-oriented revision-limit diagnostics. Blind human review remains required
for semantic requirements, target format, quality, and preference. Ruff
lint/format and strict mypy pass across 134 Python files, all 276 pytest tests
pass, all 11 frontend tests pass, frontend formatting/lint/type checking pass,
and the production build succeeds. These checks refer to the v24 implementation;
the completed canary is recorded below. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v23-canary-2026-09-04.md`.

The completed v24 canary produced four of nine runnable stories: Cloud remained
four of four, but Local fell from two of five to zero of five. The known Local
OH-V01-006 Blueprint failure stayed outside the production denominator. Scoped
context reduced Cloud production input by 17.7%, all Cloud structured attempts
succeeded, and Local persisted revisions avoided the v24 0.35 similarity floor.
Two benign critic notes were falsely promoted by topic keywords. Local
continuity retained unsupported concerns and changed allegations under stable
IDs, while OH-V01-003 cleared scene checks but failed the resolved-thread Bible
invariant twice. The operator-confirmed v23 dual-boot clock correction remains
environmental and does not require runtime clock changes.

Production graph v5 and prompt v25 now use explicit assignment findings with
exact draft evidence, shared critic/continuity requirement timing, smaller
canonical assertions with scope, and recheck outcomes that can invalidate an
unsupported allegation or retain only advisory feedback. Recurrence identity
includes the original normalized allegation as well as its source; this is
conservative identity matching, not semantic equivalence detection. Resolved
Bible threads require an actual explanation and receive application-owned
resolution-scene lineage with precise bounded retry diagnostics. Advisory
Blueprint name observations preserve immutable approved content, and hard
critic blockers now fail at the revision cap even when continuity clears.
Scoped context, repair ledgers, and bounded revision restraint remain in place.
The checks improve structural and provenance guarantees; model interpretation
still requires canary evidence and blind human evaluation. Combined verification
passes: Ruff lint/format and strict mypy across 141 Python files, all 341 pytest
tests, frontend formatting/lint/type checks, all 11 Vitest tests, and the
production build. These checks refer to the v25 implementation; its completed
canary and the next implementation are recorded below. Step 19 remains
**IN PROGRESS** because the formal campaign and human review are not complete.
Evidence: `docs/benchmark_reports/step-19-local-cloud-v24-canary-2026-09-05.md`.

The completed v25 canary matched v23's six of nine runnable completions and
advanced accepted scenes to 38/44 (v23: 32/44; v24: 24/44). Local OH-V01-001
became a new success, OH-V01-004 recovered, and all four Cloud cases completed.
Local OH-V01-002 and OH-V01-003 reached later scenes but failed historical
resolved-thread delta validation; OH-V01-005 retained an unsupported continuity
blocker. Local OH-V01-006 remains the exact inherited Blueprint failure, not a
production failure. The operator-confirmed host clock issue is environmental.
v23 and v25 are pinned comparison baselines until stronger evidence replaces them.

Production graph v6 / prompt v26 implement the six follow-up changes: immutable
resolved-thread history with no-op delta omission; a registered, budgeted terminal
continuity adjudication node; an evidence/source guard against immediately
reintroducing released findings under new wording; regression and positive-control
tests including a separate hard viewpoint audit; failure-layer and selected-claim
diagnostics; and matched technical comparison / blind human review tooling.
The existing revision cap, World Rule and requirement gates, approval checkpoint,
profile routing, and secret guards remain intact. No v26 canary or human review
has been run. Live semantic performance and repeatability are pending; Step 19
stays **IN PROGRESS**, and Step 20 has not been started. Evidence and verification:
`docs/benchmark_reports/step-19-local-cloud-v25-canary-2026-09-07.md`.

The completed v26 canary reached 3/9 runnable completions, 0/5 Local and 3/4
Cloud, with 16/44 accepted scenes. All five Local initial drafts exactly matched
v25, isolating the main regression to downstream review. Five terminal failures
exhausted the new viewpoint evidence contract; Local 003 also retained an
unsupported continuity allegation and a likely false hard critic blocker.
The adjudication node was never eligible in that case. Local Bible fixes were
not reached, and human quality evidence remains pending.

Selective repairs on the existing v26 development branch use graph v7 / prompt
v27 for new executions. Aligned viewpoint reviews need no quotation; genuine
violations use exact evidence handles and a different character's narrative
breach. Reviewer-format failures no longer enter critic input as manuscript
evidence. Approved-style/focal-character distinctions, first-allegation continuity
ledgers, bounded viewpoint audits, and combined terminal diagnostics are added.
Existing Bible-history protection and bounded adjudication remain intact.
Offline regression and protected saved-input probe tooling are implemented;
verification passes Ruff, strict mypy (149 files), all 396 Python tests, frontend
format/lint/type checks, all 11 frontend tests, and the production build. All
eight planned probe selections compile read-only against their frozen inputs;
live probes, a new full canary, repeatability, and blind review are still pending.
Step 19 remains **IN PROGRESS**; no later phase is started. Evidence:
`docs/benchmark_reports/step-19-local-cloud-v26-canary-2026-09-08.md` and ADR 0008.

The completed v27 isolated suite validated all eight responses in eight calls,
with no response repairs. Local 002/003 recovered the intended allowance for
assigned-character interiority/deductions, and both Bible probes preserved exact
resolved-thread history. Local 005 nevertheless missed its intended positive
control: direct narration of Cora's private feelings with Elara explicitly
assigned and no specific style authorization for that shift. The full canary was
held; response validation was not treated as semantic success.

The targeted follow-up uses prompt v28 with unchanged graph v7 on
`codex/v28-production-contract`. Critic guidance now distinguishes attributable
inference from direct private access, generic internalized style from specific
narrative permission, and short intrusions from whole-scene replacement. It
preserves assigned-character interiority, dialogue, observable behavior, authorized
omniscient/shifting narration, and status-only aligned responses. Non-canonical
contrasting examples and offline regression controls are added without changing
the writer, output schemas, graph, budgets, or Bible reducer. Three exact-input
Local follow-up probes are prepared with explicit semantic expectations, not run.
Verification passes Ruff lint/format, strict mypy across 150 Python files, all
412 Python tests (including 16 new viewpoint controls), frontend format/lint/type
checks, all 11 frontend tests, and the production build. All three follow-up
selections compile read-only with verified input hashes and Local 005's exact
reference evidence. Thirteen protected historical/probe hashes remain unchanged.
No live probes or full canary are launched. Step 19 remains **IN PROGRESS**, with
live semantic verification, repeatability, and blind review pending. Evidence:
`docs/benchmark_reports/step-19-v27-isolated-probes-2026-09-08.md` and ADR 0009.

The subsequent 31b candidate stage made 33 Cloud calls: 24/24 new POV controls
matched provisional assistant labels, while the unchanged full critic made 9/9
correct raw POV decisions but validated only 6/9 complete responses. All three
Local-002 failures confused an evidence ID with a quotation. Local-005's Cora
0044 intrusion was caught in all three samples; two raw pass verdicts were
correctly normalized to revise. Other substantive judgments remain unadjudicated.

Prompt v29 retains graph v7 and implements one version-bound evidence-reference
interface for assignment, POV, and ordinary craft findings, plus application-owned
rubric identity and a fixed three-dimension scene-craft mean separate from hard
gates. Canonical evidence remains exact excerpts and old artifacts stay readable.
Generic guidance distinguishes missing outcomes from optional stronger
dramatization without declaring the disputed scenes right or wrong. No model
routing, writer, budget, retry, continuity, or Bible behavior changes.
Verification passes Ruff lint/format, strict mypy across 151 Python files, all
449 Python tests, frontend format/lint/type checks, all 11 frontend tests, and
the production build. Six read-only request compilations confirm Local/Cloud
schema parity for the three frozen scenes; 425 protected evidence files remain
unchanged. Pending promotion requirements are documented in
`docs/benchmark_reports/step-19-31b-transfer-v29-corrections-2026-09-09.md` and
ADR 0010. No live v29 evaluation or canary is launched. Step 19 remains
**IN PROGRESS**, with human adjudication, expanded live controls, bounded repair
loops, and blind story-quality review still pending.

### Testing direction update — 2026-09-11

The operator designates `gemma4:31b` through Ollama Cloud
(`gemma4:31b-cloud`) as the testing model. E4B-driven tuning and further narrow
proofreading experiments are deferred. Local, Hybrid and Cloud remain product
options; no runtime profile, production prompt v29, graph v7 or safety gate changes
in this documentation update. The next priority is complete Cloud production,
including recovered failures, revision behavior and human story quality.

The evidence register now consolidates 264 Cloud calls in the September 9–11
focused series, plus the earlier single Cloud v27 probe. It records strong POV
and assignment results, 3/3 exact-preservation c05 writer repairs, and the latest
17/21 versus 15/21 minimal word-repair recommendations. The human correction
that c05 requires duplicate removal is retained explicitly; Local-002/003's
disputed broader judgments remain unscored. No v27/v28/v29 full canary has been
completed. Latest full Cloud canary completions remain v25 4/4 and v26 3/4.

Step 19 stays **IN PROGRESS**. Its current phase is explicitly Cloud-first:
complete the intended workflows across the frozen 12-prompt corpus, compare
against the direct-model baseline, inspect clean versus recovered completions,
and collect the required blind human scores, hard-gate decisions, preference and
budget evidence. Establish repeatability before closing this phase. This dated
policy supersedes the earlier all-profile completion prerequisite for the current
phase; Local/Hybrid qualification is deferred, not recorded as passed. Declare a
new scope-bound plan and evidence record rather than marking the unfinished
48-case historical campaign complete or weakening its sealing invariants.
Hybrid evaluation is considered only after Cloud-first completion, with separate
authorization. Step 20 has not started and no new model run is launched here.

References:
[testing decision](../docs/benchmark_reports/model-testing-direction-2026-09-11.md),
[exact evaluation register](../docs/benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md),
[deferred issue draft](../docs/issue_drafts/gemma4-31b-critic-repair-follow-up.md).

### Manual v29 Cloud evidence — 2026-09-12

Ten fresh manual stories completed under production prompt v29 / graph v7 with
the Cloud 31B model, accepting 59/59 planned scenes. A read-only SQLite audit
reconciles 326 calls (61 Blueprint + 265 production), six automatically recovered
failed attempts, eight one-cycle scene revisions, 10 exact Blueprint approvals
and zero run-control records. Notes, screenshots, artifacts, invocation lineage
and accepted manuscripts are preserved under
data/diagnostics/manual-v29-cloud-2026-09-12/. Public results and hashes are in
the [manual evaluation report](../docs/benchmark_reports/manual-v29-cloud-production-2026-09-12.md).

This manual completion sample is separate from the frozen 12-prompt corpus and
had no human literary scores or matched direct-model baseline at this checkpoint.
Step 19 remained **IN PROGRESS**; the canary batches, blind review, budget
assessment and repeatability were outstanding. All ten manual literary reviews
are now complete; see the September 30 entry below. No model call, canary staging,
production-contract change or later phase began while documenting this evidence.

### v29 Cloud canary batch 1 completed — 2026-09-12

Cloud OH-V01-001 through OH-V01-004 completed under prompt v29 / graph v7:
**4/4 stories, 21/21 accepted scenes, 99/99 succeeded production invocations**.
Five continuity-driven prose revisions completed without failed calls or manual
controls. The isolated approved-seed copy, explicit four-case scope, exact prior
approvals, source hashes, logs and completed snapshot are preserved under
data/benchmarks/v0.1/v29-cloud-batch-1-2026-09-12/. The
[batch report](../docs/benchmark_reports/step-19-cloud-v29-batch-1-2026-09-12.md)
records usage, matched historical Cloud comparisons and two semantic questions
requiring human review.

At batch 1 close, Step 19 remained **IN PROGRESS**. Batches 2 and 3 had not started; human quality,
direct-model baseline/preference, budget acceptance and repeatability remain
outstanding. No runtime tuning, later phase or Hybrid execution was introduced.

### v29 Cloud canary batch 2 completed — 2026-09-12

Cloud OH-V01-005 through OH-V01-008 reached terminal outcomes under the same
prompt v29 / graph v7, Cloud model, approved Blueprints, seeds and budgets:
**2/4 stories completed, 16/21 scenes accepted, 88 production calls (84 succeeded,
4 failed), five prose revisions**, in 453.888 seconds. Cases 006 and 008
completed. Case 005 exhausted its continuity structured-repair attempt on scene
2; case 007 reached the hard-critic revision limit on scene 5. The latter's
repeated POV allegation despite inference wording remains a semantic review
question, not a human-adjudicated defect. Case 008 recovered a critic validation
failure automatically.

Local receipts, failure details, exact revision diffs, two completed manuscripts,
failed-case partial drafts and an audited final snapshot are preserved under
data/benchmarks/v0.1/v29-cloud-batch-2-2026-09-12/. The archive's 17 evidence files
and 179 artifact content hashes were validated; original seed, batch 1 evidence
and runtime hashes remain unchanged. No new Blueprint calls, approvals, manual
run controls or production tuning occurred.

At batch 2 close, eight of twelve Cloud cases had been attempted: **6 completed, 2 failed,
37/42 planned scenes accepted** across batches 1 and 2. Batch 3 had not started.
The final consolidated diagnostic document was deferred until all three batches
finished, as requested. Step 19 remains **IN PROGRESS**; human quality, direct-model
preference, budget acceptance and repeatability remain outstanding.

### v29 Cloud canary cycle completed; diagnostics consolidated — 2026-09-12

Batch 3 ran Cloud OH-V01-009–012: **3/4 stories completed, 17/22 accepted
scenes, 81 calls (78 succeeded, 3 failed), three prose revisions**, in 452.385
seconds. Cases 010–012 completed; 009 exhausted the critic's structured repair
on the assigned-character interiority validation rule. Its failure and all
partial artifacts are retained. Case 010 recovered a writer JSON error.

All three batches now cover **12/12 frozen Cloud cases: 9 completed, 3 failed,
54/64 planned scenes accepted, 268 calls (261 succeeded, 7 failed), 13 prose
revisions across 12 scenes**. Recorded usage was 2,767,113 input + 224,110 output
tokens; summed runner time was 1,398.995 seconds. No new Blueprint calls,
approvals, manual run controls or runtime tuning occurred.

The [consolidated diagnostic report](../docs/benchmark_reports/step-19-cloud-v29-consolidated-2026-09-12.md)
records outcomes, exact failure classes, recovery, critic/continuity questions,
revision preservation, usage, matched historical context and source receipts.
Nine completed manuscripts and failed-case drafts are indexed in local
data/diagnostics/v29-cloud-cycle-2026-09-12/. All three archives passed source,
approval and integrity checks (52 archived files, 561 artifact hashes).

The canary execution and requested consolidation are complete. **Step 19
remains IN PROGRESS**: repeated POV boundary failures, case 007's inference
loop and questionable continuity rechecks need adjudication; blind human
quality/preference, real cost acceptance and repeatability remain open.
No later phase or additional model experiment has started.

### Failed-review evidence implemented — 2026-09-12

The first production-improvement step is complete: rejected critic, continuity
and continuity-adjudication responses now retain bounded, redacted, allowlisted
findings on the failed invocation, with exact input/candidate versions, scene/POV
assignment, selected request-catalog evidence and explicit capture availability.
The diagnostic record distinguishes an unassigned viewpoint from an allegation
about the assigned character without changing the existing validator or error.
Rejected findings remain unvalidated allegations, never manuscript facts.

Prompt v29, graph v7, response schemas, provider requests, retries, revision
limits and acceptance behavior are unchanged. Failure evidence is excluded from
retry context and model messages. Historical canary archives remain unchanged;
missing historical response bodies cannot be recovered. No live calls were run.
See [ADR 0011](../docs/adr/0011-bounded-failed-review-evidence.md).

Validation: 461 Python tests passed, including 12 new failure-evidence cases
covering both POV causes, source resolution, malformed output, capture bounds,
redaction, migrated SQLite persistence, recovery/terminal failure at the existing
limit, artifact and prompt isolation, unchanged retry context, export and replay.
Ruff lint/format and strict mypy passed. Frontend formatting, lint, type checking,
all 11 tests and the production build also passed.

**Step 19 remains IN PROGRESS.** Assignment-aware schemas, repair acceptance
criteria, critic adjudication and continuity policy are separate future work.
This completes observability work, not a claim of improved model judgment or
production success rate; no later product phase has started.

### Assignment-bound critic schema completed — 2026-09-13

Production-improvement step 2 is complete under prompt v30 / graph v7.
The application specializes each critic response schema from the exact approved
scene assignment: no assigned POV means only aligned status is available;
assignment findings can select only populated supported anchors. Explicit POV
and the existing single-character fallback retain the current narrative audit.
Same-character and other semantic/structural guards remain unchanged; no closed
character roster or keyword-derived narrative permission was introduced.

Production and isolated-probe requests use the same specialization. Prompt prose,
input artifacts, budgets, retry/revision limits and all manuscript acceptance
rules remain unchanged; schema size is equal or smaller for matched inputs.
See [ADR 0012](../docs/adr/0012-assignment-bound-critic-schema.md).

Validation: 472 Python tests passed (11 new cases), Ruff lint/format and strict
mypy passed, and the production build passed. Offline controls cover Local/Cloud
schema delivery, explicit/unassigned/fallback POV, populated anchors, unchanged
hard gates, source immutability, and SQLite workflow completion/replay.

The authorized focused Cloud probe of OH-V01-009 scene 2 used source invocation
c79d2999-842a-4710-a101-fc57ade60b7e and exact frozen v29 input artifacts,
gemma4:31b-cloud, seed 19209 and unchanged per-call budgets. It returned a valid
pass with no issues on its first call: 13,323 input / 467 output tokens, 1,945 ms
provider latency. Evidence is in data/diagnostics/v30-step2-cloud-009-2026-09-13/.
This is one isolated critic result, not a full-story completion, a new canary
score or repeatability evidence. The original source snapshot hash was verified.

Manual-test policy agreed on 2026-09-13: the user will run one or more stories
after each improvement step and keep a date/story log. Do not create individual
manual-story reports. Preserve normal app diagnostics and, when the user asks
after at least ten manually tested stories, compile an aggregate diagnostic
review that distinguishes the contract/runtime versions tested. Focused
benchmark retests may accompany individual steps.

**Step 19 remains IN PROGRESS.** Repair criteria, critic adjudication and
continuity policy remain subsequent work; no later product phase has started.


### Revision acceptance tests completed — 2026-09-13

Production-improvement step 3 is complete under prompt v31 / graph v8.
Writer and critic now share a bounded, version-bound repair target derived from
the current scene's earlier canonical critiques and exact rejected drafts.
Revision reviews must assess each target as met/unmet with current-draft
evidence. Unmet issues retain their original severity; perfect craft scores
cannot clear an unmet hard repair. Independent new blockers still apply.

The original claim, evidence and acceptance condition stay available across the
existing revision allowance. Exact repeated category/severity/claim/repair text
keeps its first target; no fuzzy semantic matching is introduced. Advisory
feedback remains available to the writer without becoming a hard gate. Actual
word changes neither guarantee nor automatically become necessary for approval.
Continuity rechecks/adjudication and all retry, call and revision limits remain
unchanged. Canonical artifact schemas and SQL storage remain compatible.
See [ADR 0013](../docs/adr/0013-revision-acceptance-tests.md).

Context projections replace duplicated historical review and scene prose while
preserving exact input-version lineage, the full current draft and canonical
Bible. Writer/critic instruction text is shorter than v30. All three matched
probe requests were smaller than their v30 equivalents. Successful repair
assessments and failed review checks are retained in redacted diagnostic records.

Validation: 486 Python tests passed, including 14 step-3 cases; the final focused
repair suite also passed after the severity-preservation check. Ruff lint/format,
strict mypy and the production build passed. Tests cover shared targets, stable
original evidence, current-reference validation, missing/invented checks,
unresolved hard gates, nonblocking advice, severity escalation, exact SQLite
lineage, secret-safe audit/export, bounded recovery and replay.

Four authorized isolated Cloud critic probes covered three frozen v29 scenes:
007 scene 5 revision 1 (twice), 006 scene 5 revision 1 and 009 scene 2. All four
validated on their first attempt and returned pass. Both 007 probes and 009
retained nonblocking notes; 006 had no issues. The repeated 007 probe verified the success-audit export.
Its saved assessment overcredits a qualifier already present in the original, so
the pass does not establish sound critic reasoning. Original snapshots were
hash-verified and remain unchanged. Exact requests, restored review lineage,
results, measured sizes and runtime receipts are under
data/diagnostics/v31-step3-cloud-2026-09-13/.

These were critic probes, not fresh writer runs, complete stories or a new canary
completion score. The aggregate manual-test review remains deferred until the
user requests it after at least ten stories. **Step 19 remains IN PROGRESS**;
critic adjudication and continuity-policy changes are steps 4 and 5 and have
not been implemented. No later product phase has started.


### Bounded critic adjudication — 2026-09-13

Production-improvement step 4 is COMPLETE under prompt v32 / graph v9.
The registered critic_adjudication node reuses the existing
one-visit/two-attempt terminal adjudication allowance. It addresses typed POV and
scene-assignment allegations against the approved plan, complete current scene
and original repair tests. Upheld or uncertain findings remain blocking. Unrelated
critic issues and all continuity blockers prevent this path; competing review
blockers are identified explicitly. Continuity-only adjudication is unchanged.

A new immutable critique preserves original evidence, scores and rubric verdict;
only specifically released allegations become notes. Diagnostics bind exact
source critique/candidate IDs and issue decisions. No ordinary prompt growth,
new prose retries, increased budgets, migrations or new human checkpoints.
See [ADR 0014](../docs/adr/0014-bounded-critic-adjudication.md).

Validation: the full 511-test Python regression suite passed. A final 35-test
focused run passed after adding rejection-text isolation, covering all 26 step-4
cases plus the production graph controls. Ruff lint/format, strict mypy (158 files)
and the production build passed. Ordinary writer/critic instructions remain
586/3,848 characters; the separate adjudication instruction is 1,298 characters.
A matched fixture request is shorter than its full critic counterpart. No live
v32 Cloud probe or canary was run; offline outcomes establish control-flow and
contract behavior, not semantic accuracy or a new completion score.

The three post-step-3 manual stories completed under v31 with 74 production calls
and no failed calls. Keep these separate from v32 validation. No individual manual
report or comparative quality judgment is inferred from the SammyAI premise reuse.
The aggregate manual review remains deferred until the user requests it after at
least ten stories. **Step 19 remains IN PROGRESS** and step 5 remains pending.


### Contradiction versus ordinary development — 2026-09-13

Production-improvement step 5 is COMPLETE under prompt v33 / graph v9.
Continuity claims now bind timeline events to their time and scene, identify
state snapshots by their actual update scene, and distinguish initial knowledge,
scoped facts and open/resolved history. Administrative kind/status labels cannot
supply contradiction evidence. Later change and missing explanatory bridges do
not alone establish incompatibility; real contradictions and explicit constraints
remain blocking. Existing dispositions, revision limits, budgets and adjudication
allowances are unchanged. See [ADR 0015](../docs/adr/0015-scoped-continuity-development.md).

The three latest v32 manual stories completed. The Root Ritual resumed at
19:51:02 local after the reported reboot, using the interrupted scene's exact
input lineage. App records do not establish the OS crash's cause. Future recovery
now closes stranded calls as interrupted_execution with unknown provider outcome,
without treating process loss as a malformed-response retry or removing it from
the aggregate call budget. Original completed-run records remain unchanged.
SQLite integrity and foreign-key checks passed, as did all 146 artifact hashes.
No adjudication was exercised by these three manual runs.

Validation: all 521 Python tests passed, Ruff lint/format and strict mypy (159
files) passed, and the production build passed. Nine new cases cover scoped
claims, retained constraints, real SQLite advisory/hard routing and recovery
bookkeeping. Three reconstructed v32 requests exactly matched their recorded
hashes; each matched v33 request was shorter. Continuity system text decreased
from 7,328 to 7,184 characters. Evidence is retained locally under
data/diagnostics/v33-step5-offline-2026-09-13/.

No live v33 probe or canary was run, and offline outcomes do not establish a
semantic improvement or completion rate. All five production-improvement
implementations are complete. The user's manual-test cadence continues; aggregate
review remains deferred until requested after at least ten stories. **Step 19
remains IN PROGRESS** pending evaluation/human review. No later product phase has
started.


### Aggregate manual v29–v33 evidence — tested 2026-09-13, reviewed 2026-09-14

The requested [twelve-story manual diagnostic review](../docs/benchmark_reports/manual-v29-v33-cloud-production-2026-09-13.md)
is COMPLETE. All 12 workflows completed with 70/70 accepted scenes: one story
under v29, two under v30, and three each under v31, v32 and v33. The sample records
381 calls (308 production / 73 Blueprint), seven recovered failed responses,
one interrupted v32 execution and seven one-cycle prose revisions. The interrupted
call remains a historical RUNNING row; its provider outcome is unknown. One
recovery at 19:51:02 local is supported by matching task/input lineage.

The review preserves 613 verified artifact hashes, 2,322 input links, 12 rendered
manuscripts, exact premises, version/seed identities, review audits and revision
diffs under data/diagnostics/manual-v29-v33-cloud-2026-09-13/. All 12 applied
Blueprint approvals are recorded; no in-app run controls or human quality scores
exist. SQLite integrity, completion-event lineage, bundle hashes and report links
were checked. No model calls, application-code changes or historical-data edits
were made for the review.

The sample includes one v31 critic acceptance test and three failed continuity
response captures, but no live adjudication. v33 completed all three stories while
still needing four structural response repairs and two prose revisions. Repeated
time-coverage evidence failures and questionable semantic allegations remain
visible. Different stories tested each contract, so neither a causal improvement
percentage nor a new combined canary score is inferred. At this checkpoint,
**Step 19 remained IN PROGRESS** pending controlled evaluation and human review.
All twelve manual literary reviews are now complete; see the September 30 entry
below. No later phase started.


### v33 Cloud canary batch 1 completed — 2026-09-14

Cloud OH-V01-001–004 completed under prompt v33 / graph v9: **4/4 stories,
21/21 scenes, 88 production calls (87 succeeded, one recovered response failure)**.
One scene received one prose revision. No new Blueprint calls or human approvals,
manual retries, terminal adjudication or revision-limit exhaustion occurred.
The run lasted 682.266 seconds, including one successful 202.158-second critic
request. The next two batches have not been staged or launched.

The isolated batch used the original human-approved seed, migrated only in its
new directory. Exact Blueprint IDs/hashes, seeds, Cloud profile and limits match
v29 batch 1. Ollama remains 0.34.0 and its model alias digest matches. Source,
runtime and v29 evidence hashes were preserved. All 192 selected-project artifact
hashes, final manuscript references, retry input lineage, database integrity and
secret-export checks passed. The report is schema-valid with exactly four results.

Evidence, completed snapshot and manuscripts are under
`data/benchmarks/v0.1/v33-cloud-batch-1-2026-09-14/`; the
[batch report](../docs/benchmark_reports/step-19-cloud-v33-batch-1-2026-09-14.md)
records the matched comparison. Calls decreased from 99 to 88 and revisions from
five to one, with 13.8% fewer total tokens. Failed calls rose from zero to one,
and elapsed time increased. All 21 initial drafts differ from v29, so this is
not an identical-prose test of reviewer accuracy. The time-coverage evidence
failure persists; the isolation-rule repair and its qualification are retained.

The separate cycle scope preserves the original 48-case plan's approval lineage
while selecting only this Cloud subset. Batch 2 is 005–008 and batch 3 is 009–012;
consolidation awaits both. **Step 19 remains IN PROGRESS**; no human quality scores
or later product phase are claimed.


### v33 Cloud canary batch 2 completed — 2026-09-14

Cloud OH-V01-005–008 completed under the unchanged prompt v33 / graph v9:
**4/4 stories, 21/21 scenes, 99/99 successful production calls**. Five revisions
occurred across four scenes; no failed responses, new human approvals, manual
retries, adjudication or revision-limit exhaustion occurred. Cases 005 and 007,
which failed under v29, now complete. Runtime, seeds, exact approved Blueprints,
Cloud profile and limits match the frozen cycle. Batch 1 evidence is preserved.

The [batch-2 report](../docs/benchmark_reports/step-19-cloud-v33-batch-2-2026-09-14.md)
and local archive `data/benchmarks/v0.1/v33-cloud-batch-2-2026-09-14/` preserve the
final snapshot, manuscripts, review audits, five diffs, comparison hashes and
semantic inspection notes. All 201 selected-project artifact hashes passed;
canonical output lineage, inherited seed counts, database integrity, secret export,
source hashes, bundle receipts and documentation links were checked.

Calls increased from v29's 88 to 99 while accepted scenes rose from 16 to 21.
The batch took 881.186 seconds; completion gains do not establish efficiency or
literary superiority. All 18 comparable initial drafts differ. 005's redundant
identification-evidence recap and 007's grief-inference handling remain review
concerns, despite successful production and explicit repair tests.

The first two batches total 8/8 completed cases, 42/42 scenes, 187 calls (186
succeeded, one recovered failure), and six revisions. Batch 3 (009–012) has not
been staged or launched. Full diagnostic consolidation waits for that batch.
**Step 19 remains IN PROGRESS**; no human quality scores or later phase are claimed.


### v33 Cloud canary cycle completed; diagnostics consolidated — 2026-09-14

The final batch, Cloud OH-V01-009–012, completed **4/4 stories and 22/22 scenes**
in 568.998 seconds: 101 calls (100 succeeded, one recovered continuity validation
failure), with four POV revisions in 011. The user-authorized three-batch cycle
is now complete under unchanged prompt v33 / graph v9, with **12/12 completions,
64/64 scenes, 288 calls (286 succeeded, two recovered failures), and ten prose
revisions across nine scenes**. All three v29 failures now complete; no prior
success regresses in this run. No terminal retry, limit increase or tuning occurred.

The [single consolidated report](../docs/benchmark_reports/step-19-cloud-v33-consolidated-2026-09-14.md)
incorporates all three batches, the matched v29 comparison, review/revision
analysis, timing, usage and twelve manuscript links. Final batch evidence lives
in `data/benchmarks/v0.1/v33-cloud-batch-3-2026-09-14/`; consolidated analysis,
lineage, exact recovery checks and semantic notes are in
`data/diagnostics/v33-cloud-cycle-2026-09-14/`. Checks verified 59 source archive
files, 599 artifact hashes, exact selected outcomes/approved inputs, consistent
snapshots, all manuscript hashes, unchanged source/seed/prior receipts, database
integrity/foreign keys, existing secret-export guards, and documentation links.

Both failed responses lacked current-draft time-coverage evidence. The 012
capture additionally preserves an unsupported closed-versus-unlocked allegation
that disappeared on same-draft structured retry. 005/4 requirement scope, 007/5
and 011/2 POV inference, and assessments crediting retained text remain review
concerns. Nine critic repair assessments record eight met and one unmet result;
no live adjudication occurred. All 57 paired initial drafts differ from v29.

The cycle used 3,171,102 tokens and 2,132.449 seconds of summed runner time while
completing ten more scenes than v29. No equal-work speed/cost or literary-quality
claim is inferred. Application source did not change; validation covered canary
evidence and documentation rather than rerunning the application build/test suite.
**Product Step 19 remains IN PROGRESS** pending semantic review, human quality/
preference, cost acceptance and repeatability; no later product phase is started.

### Cloud-first harness configuration completed - 2026-09-19

Item 1 of the remaining Step 19 engineering work is **COMPLETE**. New campaign
plans explicitly declare `cloud-first` (12 Cloud + 12 direct baseline cases) or
`all-profiles` (the existing 48-case default). Cloud-first planning needs only a
complete Cloud preset and freezes the baseline from its scene-writer selection.
Execution and approval defaults follow the plan; out-of-scope targets fail.

Plan schema 2 binds the complete declared matrix and seeds to the frozen corpus.
Summaries omit excluded profiles while retaining missing/failed planned cases in
the denominator. Sealing requires every terminal result, every eligible successful
comparison, exact output content, human reviews and a matching summary. Legacy
schema-1 hashes, summaries and sealing requirements remain intact; old Cloud
canaries do not become completed formal campaigns. Operator commands and design
are documented in the [benchmark guide](../benchmarks/README.md) and
[ADR 0016](../docs/adr/0016-scoped-benchmark-campaigns.md).

Validation passed: 537 Python tests, Ruff lint/format, strict mypy on 160 files,
frontend format/lint/type checks, 11 Vitest tests and production build. Sixteen new
cases cover scoped execution/evidence and historical compatibility. All six actual
v29/v33 campaign plan hashes and report bindings also passed read-only verification.
Two older operator fixtures now use complete matrices over smaller test corpora.
An existing parallel Blueprint recovery test failed once in the initial full run,
then passed isolated and in the final full run without test or workflow changes;
this intermittent result is retained for item 3, with no asserted root cause.

The user's next-model direction is recorded: after v0.1-alpha, limited evaluation
of additional models, tentatively GPT and Gemini; exact choices remain undecided.
Plans remain provider/model-neutral. The CLI still executes through Ollama
transports; this work adds no native GPT/Gemini adapters or live model runs.
Production prompt v33, graph v9, runtime limits and approval rules are unchanged.

Remaining engineering/evaluation sequence:

- [x] 1. Make Cloud-first evaluation a supported harness configuration.
- [x] 2. Distinguish unknown cost from an actual zero cost (completed 2026-09-19 below).
- [x] 3. Complete remaining failure-path verification (completed 2026-09-19 below).
- [x] 4. Execute full premise-to-story Cloud evaluation against the direct baseline (execution and human review complete 2026-09-30; acceptance shortfalls recorded below).
- [ ] 5. Establish repeatability and seal the formal evidence after human review (September campaign sealed; prospective three-repeat series started 2026-10-02, as recorded below).

**Product Step 19 remains IN PROGRESS.** No later product phase has started.

### Evidence-based cost acceptance completed - 2026-09-19

Item 2 of the remaining Step 19 engineering work is **COMPLETE**. Model responses,
persisted invocations and portable benchmark outputs now distinguish unknown,
provider-reported and local-inference cost evidence. An explicit reported zero is
eligible; Ollama Cloud's numeric placeholder is not. Migration 0008 preserves
historical amounts and assigns unknown provenance without inference or repricing.

Complete story costs require evidence for every invocation, including Blueprint
preparation and recovered production attempts. Baseline reporting now also retains
failed attempts and their known response cost/usage when a later attempt succeeds.
Interrupted calls with unknown outcomes prevent the story total being treated as
known. Exact invocation IDs bind the evidence across completion and replay.

Summary schema 2 reports known/unknown case coverage and leaves cost acceptance
`null` until every planned Cloud/Hybrid case has a complete cost total. With full
coverage, the unchanged median-budget criterion can pass or fail. New seals use
schema 2 and cannot reuse an old numeric-cost pass. Historical schema-1 archives
retain exact verification semantics, explicitly identified by the CLI. Sealing
unknown evidence does not establish cost qualification.

Validation passed: **560 Python tests**, Ruff lint/format, strict mypy on 163
files, frontend format/lint/type checks, **11 Vitest tests** and production build.
Twenty-two new cost tests and one populated migration test cover reported zero,
unknown and over-budget amounts, missing coverage, non-finite values, recovered
attempts, exact cost lineage, deterministic seals and legacy compatibility.
Existing production tests also verify that a missing Blueprint or recovered-call
cost makes the entire story total unknown, without additional model calls.

Read-only reanalysis of all six actual v29/v33 canary reports yields unknown Cloud
cost acceptance and preserves the source bytes and plan hashes. A fixed synthetic
archive generated before this change verifies byte for byte. No historical report
or user database was rewritten or migrated, and no live model call was made.

Before starting the updated application or database-backed harness, apply the
normal Alembic upgrade to the active database. The [operator guide](../benchmarks/README.md#cost-evidence-and-acceptance)
and [ADR 0017](../docs/adr/0017-evidence-based-cost-acceptance.md) explain the new
fields and migration. Prompt v33, graph v9, model routing, retry allowances and
runtime ceilings remain unchanged. Unknown provider charges still cannot prove
an actual billed-spend ceiling; no pricing or subscription allocation is invented.

**Product Step 19 remains IN PROGRESS.** Items 3-5, human review and actual cost
qualification remain outstanding. No later product phase has started.

### Failure-path verification completed - 2026-09-19

Item 3 of the remaining Step 19 engineering work is **COMPLETE** for the
application/harness paths documented in the
[failure-path verification matrix](../docs/verification/step-19-failure-paths-2026-09-19.md).
Twenty-five new parametrized cases exercise Cloud transport faults through
persisted baseline/Blueprint execution, process loss and committed-output recovery,
production timeout exhaustion, active-call shutdown/user stop, and failed report
writes. Existing budget, bounded adjudication and case-isolation tests remain part
of the verification evidence.

The checks reproduced and fixed two defects. Blueprint recovery could complete
while leaving a lost provider invocation RUNNING; it now reconciles orphaned calls
using production's shared recovery routine and preserves unknown outcome/cost.
Process loss remains in budget/cost accounting but supplies no false response-repair
instruction. Worker shutdown could cancel the same execution twice and interrupt
terminal-call cleanup; it now waits for cancellation cleanup before closing the
claimant, and repeated stop commands avoid a second cancellation.

The intermittent parallel Blueprint recovery test now waits for the successful
sibling's durable SQLite pending writes, replacing the previous 10 ms timing
assumption. Its original assertion remains intact. Separate tests verify that
outputs committed before graph completion are reused without another provider
call or artifact version. Accepted scenes and prior artifact hashes survive
production recovery. Failed report writes preserve prior bytes and recover from
persisted output without another model call.

Validation passed: **585 Python tests**, plus **30 affected tests** after the final
repair-context adjustment; Ruff lint/format, strict mypy on **165 files**, frontend
format/lint/type checks, **11 Vitest tests** and production build. No live model
request, user-database write or historical-evidence rewrite was performed. No
migration is required. Prompt v33, graph v9, routing, retry/revision allowances and
budgets remain unchanged.

This is deterministic engineering evidence, not live adjudicator-quality or
physical OS/disk-failure certification. Packaged desktop failure testing remains
Step 21 work. **Product Step 19 remains IN PROGRESS**, with items 4-5, real human
review and actual cost qualification still outstanding. No later product phase
has started.

### Formal Cloud-versus-baseline evaluation staged - 2026-09-29

At setup, item 4 was **IN PROGRESS: prepared, not launched**. A fresh plan-schema-2
`cloud-first` campaign covers all twelve frozen premises with twelve agentic Cloud
cases and twelve direct-model baseline cases. It uses `gemma4:31b-cloud`, prompt
v33 / graph v9, current Blueprint prompt v9 / graph v4, and the merged failure-path
fixes at commit `a60f7037367c16b1cdab0bdc55c360caaa22ecde`.

Campaign `042918c2-8a50-49fd-831b-c1a93553d4f6` is staged in
`data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/`, with an isolated schema-0008
database, frozen inputs, zero-result report, source/environment/budget receipt,
read-only verifier and phased PowerShell runner. There are no inherited approvals,
Blueprints, production outputs or checkpoints. All 123 frozen runtime/configuration
hashes and SQLite integrity/foreign-key checks passed; all story-state counts are
zero at setup. Metadata confirmed Ollama 0.34.4 and the existing Cloud model alias.
No model generation had started at setup, and the source application database
was read-only. Subsequent execution is recorded below.

The [setup report and runbook](../docs/benchmark_reports/step-19-formal-cloud-v33-setup-2026-09-29.md)
define fresh Blueprint preparation, mandatory human approval, direct baselines,
three four-case production batches, blind review and later evidence sealing.
Retry/revision allowances, budgets and prompt content are unchanged. No migration
is required for the user's already-updated application database.

At setup, the user reported completing reviews for all **22 manually tested
stories**; their discussion was deferred as requested. Those reviews remain
separate from the formal comparisons. Formal human scoring and independent
repeatability were still outstanding at that checkpoint. Subsequent human review
and sealing are recorded in the September 30 entry below. Cost acceptance remains
unknown under Ollama Cloud's current cost evidence. **Product Step 19 remains
IN PROGRESS.**

### Formal Cloud Blueprint generation - 2026-09-29

At the preparation checkpoint, item 4 was **IN PROGRESS: 12/12 fresh Blueprints awaiting human approval** in
campaign `042918c2-8a50-49fd-831b-c1a93553d4f6`. Sequential preparation took about
6 minutes 48 seconds, using 74 model calls: 72 succeeded and two integrator
responses failed schema validation, then recovered within the existing retry
allowance. There were no terminal case failures. Token totals, including failed
attempts, are 197,928 input and 77,883 output.

The [Blueprint generation report](../docs/benchmark_reports/step-19-formal-cloud-v33-blueprints-2026-09-29.md)
records exact packet lineage, failed-call details and checks. All 123 frozen
runtime/configuration hashes passed verification; no prompts, limits or
application source changed. All twelve Blueprint/critique pairs were packaged and
matched persisted content hashes. No human decision, production run or direct
baseline run had been recorded at that checkpoint.

The user stated an intention to approve the generated set without editorial review or edits.
A technical approval manifest identifies exact versions without revealing story
content. Approval was still pending at that checkpoint; this choice is not a quality
assessment and does not establish that the user read the Blueprints. The existing
mandatory checkpoint was preserved. **Product Step 19 remained IN PROGRESS**;
production, baselines, formal human reviews, cost qualification and independent
repeatability evidence were outstanding at that checkpoint.

### Formal Cloud approval and execution - 2026-09-29

The user explicitly approved all twelve generated Blueprints without editorial
review or edits. Their exact packet-bound decisions were imported with zero model
calls. The twelve direct-model baselines then completed successfully using twelve
calls. All three production batches have finished under the unchanged v33
configuration: **11/12 Cloud stories completed, 64/65 scenes accepted**. Batch
outcomes were 4/4, 4/4 and 3/4. See the
[execution report](../docs/benchmark_reports/step-19-formal-cloud-v33-execution-2026-09-29.md).

OH-V01-012 failed on the final scene's critic request: the provider reported
27,542 input tokens against the unchanged 24,000-token per-call cap. Five scenes
were accepted, and the sixth draft is preserved as partial evidence. The failed
request's usage is retained. No terminal case was rerun and no limit changed.
Cloud completion is **91.7%, so the formal 95% technical criterion is not met**.

The full campaign used 382 calls, including two recovered Blueprint validation
failures, five recovered production validation failures and one terminal budget
failure. Production used 296 calls and made 11 prose revisions across 10 scenes;
there were no adjudication calls. All 622 artifact-version hashes passed audit,
as did exact approval/manuscript lineage, SQLite integrity/foreign keys, budget
and runtime checks, and the database secret-export audit.

At generation close, eleven eligible randomized A/B pairs and a blank canonical
review form were ready; the answer key, detailed diagnostics and database snapshot
remained private. Formal human review, cost qualification and item 5's independent
repeatability evidence were outstanding. Item 4 and **Product Step 19 remained
IN PROGRESS** at that checkpoint. The request-size failure still needs investigation
with the frozen result preserved. Subsequent review and sealing follow below.

### Human reviews recorded and formal evidence sealed — 2026-09-30

- [x] Record literary reviews for all **22 manual stories**: ten from September 12
  and twelve from September 13.
- [x] Import all **11 eligible formal A/B comparisons** from the user's completed
  review CSV, bound to the canonical public packet.
- [x] Recompute formal acceptance from actual human scores.
- [x] Seal and verify the reviewed formal campaign evidence.

The [manual review collection](../docs/september_2026_manual_test_reviews/)
contains 22 individual reviews, the
[review summary](../docs/september_2026_manual_test_reviews/review-summary.md) and
[AI-pattern observations](../docs/september_2026_manual_test_reviews/AI-patterns.md).
All 24 copied documents match the proofread originals. These qualitative manual
reviews remain separate from formal paired scores.

The [formal execution and review report](../docs/benchmark_reports/step-19-formal-cloud-v33-execution-2026-09-29.md#human-review-completed--2026-09-30)
records all outcomes. Cloud technical completion is **11/12 (91.7%)**; mean
weighted human score is **3.4818**; agentic preference is **4/11 (36.4%)**, with
seven baseline wins and no ties. Those three criteria are **not met**. All reviewed
candidates pass the hard gates, the Cloud severe-continuity-free rate is **11/11**,
and the lowest Cloud dimension mean is **3.0**. Cost acceptance remains **unknown**.
The failed OH-V01-012 stays in the technical denominator. No failed output was
replaced and no acceptance threshold changed.

The canonical import, reviewed summary, evidence seal and independent archive
verification passed offline with **zero model calls**. All 123 frozen runtime
files and database row counts were unchanged. The verified archive is retained
at `data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/private/evidence.zip`.

**Item 4 is complete as an executed and reviewed evaluation.** Item 5 remains
open for independent repeatability, although this campaign's seal is complete.
**Product Step 19 remains IN PROGRESS** for repeatability, cost qualification and
the unmet acceptance criteria. No later product phase has started.

### Formal v33 Cloud repeatability started — 2026-10-02

**Item 5 is IN PROGRESS.** The user authorized the repeatability assessment.
The [prospective protocol and evidence register](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md)
declares three fresh Cloud-first campaigns, each with all twelve frozen premises,
twelve independent direct baselines, new Blueprints and exact-version human
approval before production. The September 29 reviewed campaign is a historical
reference and does not count as one of the three prospective repeats.

All three campaigns have unique identities and case IDs, isolated schema-0008
databases and matching corpus/profile/seed/limit snapshots. Setup verified zero
story-state rows and no inherited approvals or outputs. All **123 runtime files**
match the reference at merged source commit
`acf97b8087370acb713857e568e59a1722039bbc`. Prompt v33 / graph v9 is unchanged.
Ollama is now **0.35.0**, compared with 0.34.4 in the reference; all three new
campaigns use 0.35.0, with the same Cloud model alias digest. Historical comparisons
retain that environment difference. Remote provider weights are not pinned.

The series register and pre-generation protocol snapshot are under
`data/benchmarks/v0.1/v33-cloud-repeatability-2026-10-02/`. Repeat 1's Blueprint
preparation completed: **12/12 awaiting approval, zero terminal failures**,
74 calls (72 successful and two recovered HTTP 502 service errors), 189,277
recorded input tokens and 71,889 recorded output tokens in about 7m 18s. Both
service errors occurred on OH-V01-003 and returned no usage; zero placeholders
do not prove no provider work. The approval packet and database snapshot are
preserved, all 155 artifact hashes passed verification, and the secret-export
audit passed. No approval, baseline or production run has been recorded.

Repeats 2 and 3 remain staged with zero story-state rows and model calls.
New exact-version approvals, production, baseline generation, actual human
reviews and the three new evidence seals remain outstanding. All terminal failures
will be retained. The sequence ends after three campaigns and review, regardless
of whether the acceptance criteria pass; no extra attempt is added to improve a
headline result. Cost qualification remains unknown.

The user subsequently approved all twelve repeat-1 Blueprints as generated.
Verification at 07:05:01 UTC confirmed twelve durable decisions and zero model
calls added by import. The direct baseline phase began at 07:05:08 UTC, followed
by the three declared production batches. The blank approval form and
authorization/import receipts are preserved.

Repeat 1 generation finished at 07:29:01 UTC: **12/12 baselines, 12/12 Cloud
stories and 64/64 scenes completed**. The full campaign used 376 calls, including
two recovered Blueprint HTTP 502 failures and one recovered production continuity
evidence-reference failure. Production used 290 calls, with eleven revisions
across eleven scenes and no adjudication. All 620 artifact hashes and exact
manuscript lineages passed verification; the database secret-export audit passed.
The final OH-V01-012 critic call used 23,515 input tokens, only 485 below the
unchanged 24,000 cap. The earlier terminal error did not recur; request-size
reliability remains a concern.

All twelve randomized A/B pairs and a blank canonical review form are packaged.
The technical criterion passes for this campaign; the five human-quality,
preference and cost criteria remain unresolved. The generation receipt binds
81 evidence files, but a reviewed formal seal awaits actual human scoring.
Reference evidence and all frozen runtime files are unchanged. Repeats 2 and
3 remain unlaunched; one completed generation does not establish repeatability.

**Product Step 19 remains IN PROGRESS.** No writing-tic changes or later product
phase has started.

### Repeat 1 reviewed and sealed — 2026-10-02

- [x] Validate all twelve submitted A/B reviews with the canonical parser;
  preserve every score and preference unchanged.
- [x] Record the reviewer's originality/dialogue calibration as dated metadata,
  without changing the frozen protocol, rubric, weights or thresholds.
- [x] Import reviews, recompute acceptance, seal and independently verify repeat 1.

The [repeatability report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-1-human-review-and-seal--2026-10-02)
records **4.05/5 Cloud versus 4.15/5 baseline**, with **5 Cloud wins, 4 baseline
wins and 3 ties**. Canonical half-credit for ties gives **54.1667% Cloud preference**,
below 60%. Technical completion, severe-continuity-free assessments, weighted
quality and the dimension floor pass; cost acceptance remains unknown. All
24 candidates pass all human hard gates. Character depth and voice/prose remain
the lowest Cloud dimensions at 3.0.

Originality now assesses generated execution given the supplied premise, and
occasional dialogue overlength can qualify as a minor editing issue when the
other canonical qualities meet the score anchor. Carry this interpretation into
repeats 2 and 3. It differs from September's review calibration, so scores from
the two periods must not be pooled as identically calibrated quality evidence
or used to claim an engineering improvement.

The reviewed archive SHA-256 is
`0d5611771cd993023338039ebb76becea719900f5e9519ae89e8fb63d15ed43d`;
its manifest SHA-256 is
`f4391c6ff2778beaa5b5ab53fbe04b07dc4acccf9c9fd2ece2572c6d9ae7abe7`.
Input digests, the original blank CSV, generation summary and snapshot remain
preserved, and the dated calibration addendum is bound to the seal by the external
review-verification receipt. Import and sealing added zero model calls.

Repeat 2 passed empty-database, frozen-input and provider checks, then prepared
**12/12 fresh Blueprints** in about 8m 01s. All twelve await human approval;
zero baseline or production runs have started. Preparation used 73 calls
(72 succeeded, one recovered structured-output failure), 195,649 input tokens
and 75,262 output tokens. OH-V01-012's first Blueprint integration response
omitted five required scene numbers and recovered within the existing allowance.
All 161 artifact hashes, exact packet references, SQLite checks and secret-export
audit passed. The exact packet SHA-256 is
`86888a4837922cd88eac4c537c9f30cd3b784048367f214929940306d6a5be87`.
Its identifier-only approval manifest and source snapshot are preserved. The
September reference and repeat-1 review/seal remain unchanged. The new generated
versions require new human approval before production. Repeat 3 remains staged
with zero model calls.

The user subsequently approved all twelve repeat-2 Blueprints. Verification at
15:17:36 UTC confirmed twelve durable decisions and zero inference calls added
by approval import. Baseline generation began at 15:17:36 UTC, followed by the
three declared sequential production batches. All original forms and approval
receipts are preserved. **Item 5 and Product Step 19 remain IN PROGRESS.**

### Repeat 2 generation complete — 2026-10-02

The [repeatability report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-2-generation-results--2026-10-02)
records **12/12 Cloud stories, 12/12 baselines and 64/64 accepted scenes**.
The campaign used 368 calls, with four failed structured responses recovered on
the same task: one Blueprint integration failure and three production failures
covering critic repair-test coverage, a missing continuity finding summary and
invalid continuity evidence references. No terminal case was rerun or replaced.
Production made eight prose revisions across seven scenes and no adjudication
calls. The whole agentic arm used 356 calls, 3,029,350 input tokens and 309,142
output tokens. Dollar cost remains unknown.

Production finished at 15:43:08 UTC / 17:43:08 Europe/Belgrade after about 22m 46s;
baseline generation took about 2m 38s. OH-V01-012 completed without a production
call failure; its largest input was 20,104 tokens. The largest production input
overall was 21,042 on OH-V01-009, below the unchanged 24,000 cap. This does not
establish that request-size reliability is solved.

Verification checked 617 artifact hashes, exact approved/manuscript lineage,
recorded usage, frozen limits, SQLite integrity/foreign keys and secret-export
safety. Blind-packet reconstruction and canonical blank-form checks passed.
The generation receipt binds 84 evidence files; original reference and repeat-1
review/seal hashes remain unchanged. All completed outputs differ by content hash
from Repeat 1, and Repeat 3 remains empty.

The **twelve eligible blind pairs await actual human review** using the recorded
originality/dialogue calibration. The technical criterion passes; four human
quality/preference criteria and cost remain unresolved. The reviewed summary
and formal seal must wait for those scores. **Item 5 and Product Step 19 remain
IN PROGRESS.**

### Repeat 2 reviewed and sealed; repeat 3 preflight stopped — 2026-10-03

- [x] Validate all twelve repeat-2 human comparisons and preserve the submitted
  CSV unchanged; no corrections were needed.
- [x] Import the canonical review, recompute acceptance, seal and independently
  verify repeat 2's evidence.
- [x] Check repeat 3's frozen inputs, empty database and provider metadata.
- [x] Resolve Ollama version drift before any repeat-3 model call; the user
  subsequently authorized 0.35.1 as documented below.

The [repeatability report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-2-human-review-and-seal--2026-10-03)
records **4.1167/5 Cloud versus 4.1583/5 baseline**, with **1 Cloud win, 4 baseline
wins and 7 ties**. Half-credit for ties gives **37.5% Cloud preference**, below
the unchanged 60% threshold. Technical completion, severe-continuity-free review,
weighted quality and the dimension floor pass. All 24 candidates pass all gates;
character depth and voice/prose remain at 3.0 in both arms. Cost remains unknown.
The October 2 reviewer calibration is retained without a further reported change.

The reviewed archive SHA-256 is
`669eb4271dede30804419db802a58762ae91bd2f92d03b07e65090a85008bad2`;
its manifest SHA-256 is
`4854c81df5265eeac1eb760f8e132eb1ab8a1fb885e27cb22c84ec8e3205bc6c`.
Import and sealing added zero model calls. Original scores, generation evidence,
the September reference and repeat 1's reviewed seal remain preserved.

Repeat 3's provider check found **Ollama 0.35.1**, while the frozen series requires
**0.35.0**. All 123 application runtime hashes, frozen inputs/operator helpers,
model alias, alias digest and remote-model name still match. Its story-state
tables are empty; zero inference calls were made. The local
`preflight-environment-drift-2026-10-03.json` receipt preserves the discrepancy.
The next decision is restoring the declared environment or explicitly authorizing
a documented deviation before generation. No frozen check has been bypassed.

Both completed repeats retain their unmet preference criterion and unknown cost.
The third campaign and consolidated assessment remain outstanding. **Item 5 and
Product Step 19 remain IN PROGRESS.** No later product phase has begun.

### Repeat 3 environment exception authorized — 2026-10-03

The user explicitly authorized proceeding with **Ollama 0.35.1**. The
[dated environment addendum](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-authorized-environment-addendum--2026-10-03)
was recorded at 13:07:38 UTC before any repeat-3 generation. The original 0.35.0
freeze, failed-preflight evidence, all original operators and earlier reviewed
seals remain intact. Only the expected daemon version changes for this repeat;
the model/profile/corpus/runtime/prompts/graphs, budgets, retries, checkpoints,
rubric and fixed three-campaign endpoint are unchanged.

The additional `run-campaign-approved-environment.ps1` and
`verify_approved_environment.py` preserve the original checks and require exactly
0.35.1 plus the unchanged alias digest/remote-model name. Their hashes are bound
by `environment-amendment-2026-10-03.json`, SHA-256
`4bd2e765ee1089e85c1d3c7b8a7022ef03ed8370ef40dbc9658db3ca72ee8eaa`.
The approved-environment empty-state/provider verification passed. Blueprint
preparation has started; exact generated-version approval is still required
before drafting. The daemon difference must remain explicit in the consolidated
analysis. **Item 5 and Product Step 19 remain IN PROGRESS.**

### Repeat 3 Blueprints prepared; human approval pending — 2026-10-03

- [x] Prepare all twelve fresh Blueprints under the authorized Ollama 0.35.1
  environment addendum and unchanged model, runtime, prompts and budgets.
- [x] Package the exact-version approval manifest, preserve the source database
  and verify the checkpoint, artifact hashes and earlier reviewed evidence.
- [x] Obtain human approval for these twelve generated versions; the subsequent
  authorization and import are recorded below.
- [x] Run the direct baselines and three production batches; outcomes are
  recorded in the generation-complete entry below.
- [ ] Collect fresh human A/B reviews, seal repeat 3 and consolidate the fixed
  three-repeat assessment.

The [repeat-3 checkpoint](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-blueprint-checkpoint--2026-10-03)
records **12/12 awaiting approval**, **zero terminal failures**, **73 calls**,
**195,239 input / 75,152 output tokens**, and about **6 minutes 20 seconds**.
OH-V01-012's Blueprint integration omitted five required scene numbers and
recovered within the existing retry allowance; no limit or prompt changed.
All 158 artifact hashes, SQLite integrity/foreign keys, secret-export audit and
the preserved earlier seals passed verification. The approval packet SHA-256 is
`c32e2a59867a536d9c6926f7565f5713b515d1f41c8252eda5fb2cb2b5d86c96`.
Zero human approvals, baseline runs or production runs are recorded for repeat 3.
The environment exception does not authorize the new Blueprints. **Item 5 and
Product Step 19 remain IN PROGRESS.**

### Repeat 3 approved; generation underway — 2026-10-03

The user approved all twelve presented Blueprints without editorial changes.
Canonical import persisted twelve exact-version decisions and completed all
twelve Blueprint workflows with zero additional model calls, verified at
13:18:19 UTC. The original blank form, checkpoint and database snapshot remain
preserved. The [approval record](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-approval-and-generation--2026-10-03)
binds the authorization to the previously presented packet. Baseline generation
has started after another successful approved-environment check; the three
production batches and fresh human review follow. **Item 5 and Product Step 19
remain IN PROGRESS.**

### Repeat 3 generation complete; ten human comparisons pending — 2026-10-03

- [x] Complete all 24 planned attempts: **10/12 Cloud successes**, **12/12 baseline
  successes**, **56/64 accepted scenes**, with both failed cases retained.
- [x] Preserve full diagnostics, verify 585 artifact hashes and the completed
  database snapshot, and retain the original freeze and both prior reviewed seals.
- [x] Package and independently verify ten eligible blind A/B pairs, the blank
  canonical review form and unchanged reviewer calibration.
- [x] Receive and import the ten actual human reviews, seal repeat 3, and finish
  the consolidated assessment at the predeclared three-campaign endpoint, as
  recorded in the October 4 completion entry below.

The [generation report](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#repeat-3-generation-complete-human-review-pending--2026-10-03)
records **352 calls**, **2,879,354 input / 330,292 output tokens**, and about
**18 minutes 37 seconds** for production. Seven calls failed: three recovered
within existing retries, while four attempts account for the two failed stories.
OH-V01-002 reintroduced an older, cleared finding into the current continuity
recheck partition; OH-V01-010 first omitted a finding summary and then supplied
invalid evidence references. All four terminal responses retain untruncated
unvalidated review evidence. No manuscript defect is established by those
invalid responses alone. No retry allowance, prompt or budget changed.

The preserved 82-file generation manifest has SHA-256
`5304f86eae2321c9b74a0751ef5cd034e719beb9b310a11f58f8750c13f18d44`.
The public packet SHA-256 is
`decaaa85f9b65ac389da63697e6b6af74138adae0fb882d2093b9aafa40e6eea`.
Technical completion is **83.33%**, below the unchanged 95% criterion. Human
quality/preference results remain pending; cost remains unknown. The technical
series is **12/12, 12/12, 10/12 Cloud**, with **36/36 baselines**; repeat 3 retains
its authorized Ollama 0.35.1 qualification. Generation completion does not close
the reviewed evidence or the full assessment. **Item 5 and Product Step 19
remain IN PROGRESS.** Step 20 has not started.

### Item 5 complete: reviewed three-repeat assessment sealed — 2026-10-04

- [x] Validate and import Repeat 3's ten comparisons without modifying the CSV:
  160 scores, 140 true hard-gate answers and ten valid preferences.
- [x] Recompute results, seal Repeat 3 and independently verify its archive.
- [x] Reverify all three individual seals, submitted reviews, original generation
  evidence, database counts, runtime hashes and declared addenda.
- [x] Consolidate every prompt's three outcomes, technical diagnostics and human
  results, retaining both failed cases and all cost/environment qualifications.
- [x] Preserve the reviewer's new qualitative observations and the unchanged
  manual-review summary separately from the canonical scores.

The [completed assessment](../docs/benchmark_reports/step-19-v33-cloud-repeatability-2026-10-02.md#consolidated-three-repeat-assessment--2026-10-04)
records **34/36 Cloud completions**, **36/36 baselines**, **184/192 accepted scenes**
and **34 reviewed pairs**. Reviewed means are **4.1059 Cloud / 4.1529 baseline**;
preferences are **7 Cloud wins, 10 baseline wins and 17 ties**, or **45.59% Cloud
preference** with half credit. The report preserves the separate campaign results
and cohort differences; pooled numbers are descriptive, not new pass criteria.

Repeat 3 scored **4.16 Cloud / 4.15 baseline**, with 1 Cloud win, 2 baseline wins
and 7 ties. Its reviewed archive SHA-256 is
`f0f74505f17bd08b0480aa9f675a4a604c0b9f1e27c7208b5ac2e7ff37d907af`;
canonical manifest SHA-256 is
`418b578711afc75268d81e1b4936317765323b4b90cd3ca6c5b8948acd23c5c8`.
The local `consolidated-register-2026-10-04.json` under the series directory binds
the three seals and all case-level evidence, SHA-256
`1a15ce8db3619122776c943778c9b0586899c798f970eb44e7c3952293f1876a`.
Review import and consolidation added **zero model calls**; campaign invocation
counts remain 376, 368 and 352. No production code, prompt, limit or retry changed.

All eligible human review and formal evidence work is complete. **Item 5 is
COMPLETE as an assessment; Product Step 19 remains IN PROGRESS.** Technical
acceptance failed in repeat 3, preference failed in all three repeats, and cost
is still unknown. The qualitative feedback identifies character depth, prose
repetition, limited character variety and group dynamics as corrective priorities.
The proposed work is not implemented, and Step 20 has not started. No fourth
campaign or terminal-case replacement was added.

### Repeat 3 continuity response-contract corrections — 2026-10-04

**v34 / graph v9 implementation and targeted format probes complete; full-story
qualification pending.**
[ADR 0018](../docs/adr/0018-current-continuity-rechecks-and-compact-coverage.md)
records the exact OH-V01-002 and OH-V01-010 failure inputs and the corrections.

- [x] Distinguish the latest report's active finding keys from historical
  recurrence context; omit an empty model-facing recheck partition while still
  rejecting stale keys, malformed values and missing active decisions.
- [x] Derive coverage-gap summaries from the assessment; remove the redundant
  evidence-search selector and preserve mandatory exact evidence lists, targeted
  repair suggestions and the existing advisory/blocking rules.
- [x] Locate coverage text failures at the model's keyed response field and make
  the existing bounded repair explicit about missing versus empty evidence.
- [x] Add regression coverage for persisted history, validation, recovery,
  terminal failure, successful audit and replay without duplicate calls.
- [x] Reconstruct both original requests read-only, match their recorded v33
  hashes and verify shorter v34 messages: 41,436 to 39,997 characters for 002;
  40,738 to 40,495 for 010. System instructions also shrink.
- [x] Run the two isolated Cloud continuity probes after explicit user approval
  to send the frozen inputs. Both validated on their first attempts: exactly two
  calls, 19,665 input tokens and 2,069 output tokens, under unchanged limits.
- [ ] Resolve the remaining judgment/recurrence concerns and qualify production
  completion separately. Each valid review still retained one blocking finding.

Offline replay of 010's captured fields reproduces the old missing-summary error
and validates with v34 while retaining its independent contradiction blocker.
It does not establish the model's semantic correctness. Local reproduction files
are in `data/diagnostics/v34-continuity-validation-2026-10-04/`; the source snapshot
hash is unchanged. Writer/critic instructions, graph, budgets, retries, revision
limits, canonical schemas and the v33 campaign evidence remain unchanged. No
migration is required. The literary-quality work has not started.

Verification: **629 Python tests** pass, including **44 new regression cases**;
Ruff lint/format, strict mypy on 166 files, frontend formatting/lint/type checks,
all 11 frontend tests, production build and `git diff --check` pass.

The live probes ran at 14:09:53–14:10:04 Europe/Belgrade on October 4 using Ollama
0.35.1 and the same `gemma4:31b-cloud` alias digest and seeds as the frozen inputs.
Provider latencies were 4.596 s for 002 and 4.398 s for 010. Monetary cost remains
unknown. The actual request hashes matched the offline v34 packets and the source
snapshot hash remained unchanged. Results are stored in the diagnostic directory's
`live/` subdirectory; no canonical artifacts or campaign results were written.

002's stale-key format error did not recur, but the same handwriting-verification
allegation returned through the new-findings route and inherited its historical
ID and `still_blocking` disposition. This exposes a remaining recurrence concern:
that historical match bypasses the guard restricted to `newly_exposed` findings.
010's absent time cue became advisory as intended; its separate back-door blocker
requested a deletion explanation already present in the following sentence.
These observations warrant semantic and recurrence analysis. Neither scene nor
story was declared recovered, and no extra writer or adjudicator calls were made.

**Product Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.** Item 5 remains
complete as an assessment and sealing task, not as demonstrated repeatability.

### Technical stabilization v35 begun 2026-10-08

**IN PROGRESS — offline checks pass; live probes assessed; semantic recovery unqualified.**
Temporary branch: `codex/continuity-stabilization-v35`. The user authorized the
short technical stabilization before the creative-quality changes.
[ADR 0019](../docs/adr/0019-inactive-continuity-recurrence-and-counterevidence.md)
records the implementation and prepared evaluation.

- [x] Apply the revision evidence guard using the latest report's active finding
  IDs, so historical identity cannot bypass it. Preserve historical IDs, real
  blockers, independent hard gates, and the existing repair/revision limits.
- [x] Replace continuity guidance to consider nearby explanations and the strongest
  counterevidence before blocking or requesting a repair already present.
- [x] Add 14 regression cases, including persisted recovery within two review
  attempts and terminal failure without an extra writer call.
- [x] Pass repository checks: 643 Python tests, 11 frontend tests, Python and
  frontend lint/format/type checks, and the production build.
- [x] Reconstruct the exact v34 inputs read-only and verify shorter v35 requests:
  39,997 to 39,958 characters for 002; 40,495 to 40,479 for 010.
- [x] Run and assess four live probes, including two genuine contradiction
  controls, after explicit cloud-payload approval. All validate in one attempt;
  both controls catch the injected contradiction, but both original cases block.
- [ ] Resolve the remaining continuity judgment concern before expanding tests.
- [ ] Perform a bounded full-story check if probe results support proceeding.

The captured 002 finding cites five rewritten excerpts, so the guard change
alone does not reject it; its semantic judgment still needs evaluation.
The four probes used four of the maximum eight calls: 39,384 input / 4,467 output
tokens, with a published-rate estimate of USD 0.00730056 assuming uncached input
(the allocation estimate was USD 0.05248). Actual charges remain unknown.
Historical costs and formal cost-acceptance rules are unchanged. Automatic
approval review initially rejected the cloud launch; it ran only after the user
explicitly approved these private inputs, controls, and destination. The frozen
database and canonical artifacts are unchanged; no formal campaign rerun occurred.

002 still treats repeated verification as a contradiction despite the current
scene assignment requiring verification. Historical advice to remove it remains
in context and is the next focused investigation target. 010 now raises the
current-system flag rather than demanding the deletion explanation already
present; its timing still needs assessment. The 010 positive control catches the
injected denial but mixes physical and code back-doors in its repair explanation.
These results do not support expansion to a full-story run yet.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Inactive review advice investigation v36 begun 2026-10-08

**IN PROGRESS — implementation verified; live assessment does not establish semantic recovery.**
Temporary branch: `codex/continuity-history-v36`.
[ADR 0020](../docs/adr/0020-inactive-review-advice-projection.md) records the narrow
context change and comparison against v35.

- [x] Trace old repair instructions reaching the current continuity review after
  their finding leaves the active set.
- [x] Omit inactive repair advice and stale dispositions from the supervisor's
  history projection; preserve allegation identity, authority references,
  active repairs, full persisted history and all validation gates.
- [x] Add 11 regression cases, including a complete persisted workflow, and
  reconstruct all four saved v35 requests with exact matching hashes.
- [x] Verify that v36 changes only the contract version and inactive history
  projection: 002 requests shrink by 275 characters; 010 sizes are unchanged.
- [x] Pass repository checks: 654 Python tests, 11 frontend tests, lint,
  formatting, strict type checks, production build and clean whitespace checks.
- [x] Run and assess four explicitly approved live probes, all valid on their
  first attempt. 002 still blocks; both injected contradictions are caught.
- [ ] Establish sufficient semantic evidence before a bounded full-story check.

The automatic approval review rejected the v36 cloud launch as a new private
payload requiring explicit authorization. No call ran in that launch; the user
then explicitly approved the v36 probes. The experiment used four calls,
39,300 input / 3,838 output tokens, estimated at USD 0.00703720 with uncached
input, within the eight-call / USD 0.05248 allocation estimate. Actual charges
remain unknown. Request/response hashes and the unchanged snapshot were checked.

The model still treats repeated verification as incompatible with its earlier
occurrence and generates similar repair advice after the original instruction
is removed. The old allegation summary remains visible; its influence versus
independent model judgment is the next focused question. 010 clears on one call,
but it had no historical context affected by this change, so the result cannot
be credited to the fix. Its contradiction control still uses a confused
physical/code back-door explanation. No full-story run or formal rerun follows
from this limited evidence; semantic recovery and repeatability remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Controlled inactive-summary experiment begun 2026-10-08

**Diagnostic COMPLETE — no semantic improvement from history removal; stabilization IN PROGRESS.**
Production remains v36 / graph v9. The
[experiment record](../docs/benchmark_reports/continuity-summary-experiment-2026-10-08.md)
fixes three conditions: current history, inactive summaries omitted, and inactive
findings omitted entirely from model context. Application validation retains the
complete immutable history in all three.

- [x] Prepare exact matched packets and verify that only the designated history
  fields change; preserve active repairs, canon, scene assignment, schema and
  the version label. Check source immutability and saved v36 request hashes.
- [x] Prespecify three paired original-draft seeds plus one positive control per
  condition: 12 probes, up to 24 calls, no outcome-dependent rerolls.
- [x] Obtain explicit permission for this modified private payload set and run it.
- [x] Assess repeated-verification blockers, other findings and control detection
  by seed before making any further production-context change.

The maximum published-rate allocation estimate is USD 0.15744 assuming uncached
input at the dated October 8 rates. The user explicitly approved the set. All
12 probes validated on their first attempts, using 114,632 input / 12,758 output
tokens, estimated at USD 0.02115168. Actual charges remain unknown. Prepared and
live request hashes, response hashes, plan hash and source immutability were
verified; all projection preflight checks passed. No application code changed.

Each condition reproduced the repetition blocker at all three seeds (3/3 each).
All three positive controls correctly identified the injected denial; no other
findings appeared. Historical allegation text is not necessary for this judgment
in the frozen case. No additional history removal is adopted in production.

Read-only inspection also found that the approved scene 1 ends with a decision
to verify, but its accepted draft already performs the verification assigned to
scene 2. The next draft repeats that sequence and two sentences verbatim. The
next focused target is the acceptance of this premature completion of a later
scene's work, together with distinguishing dramatic repetition from contradictory
facts. This experiment does not qualify full-story recovery or repeatability.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Scene-1 acceptance trace completed 2026-10-08

**Diagnostic COMPLETE — scene-endpoint detection gap identified; stabilization IN PROGRESS.**
The [acceptance trace](../docs/benchmark_reports/scene-one-acceptance-trace-2026-10-08.md)
follows OH-V01-002's original v33 writer, critic, continuity and Bible-update
invocations through the recorded scene-1 accept event.

- [x] Verify exact artifact provenance and the unchanged read-only snapshot.
- [x] Establish normal first-draft acceptance: critic PASS, no issues, three 5/5
  scores; continuity has one informational observation and no blocker.
- [x] Confirm that writer and critic saw the current "decides to verify" outcome,
  while future scene assignments were hidden and the overall story arc's later
  verification action remained visible.
- [x] Locate explicit critic praise for the overrun and the missing dedicated
  endpoint/next-scene-reservation assessment.
- [x] Reconstruct an identical critic message hash under current v36 and verify
  that a synthetic reported outcome violation forces revise despite 5/5 scores.

The Bible update accurately recorded the verification already performed in the
accepted prose. The failure was detection of the scene-boundary overrun before
acceptance, not a reported blocker being discarded, a cost/retry limit, or lost
canonical memory. Contextual influence on the model remains an interpretation;
the records cannot reveal unretained internal reasoning.

The next proposed implementation is a compact, version-bound scene endpoint and
immediately subsequent reserved turn/outcome for the existing writer and critic,
with controls for proper stopping, permitted foreshadowing, the original overrun
and correctly assigned verification. It is not implemented by this investigation.
No model calls, new inference costs, production changes or formal reruns occurred.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Shared scene boundary implemented and probed 2026-10-08

**Implementation COMPLETE — semantic detection unqualified; stabilization IN PROGRESS.**
Prompt v37 / graph v9 adds the same compact current endpoint and immediately next
scene's reserved turn/outcome to the existing writer and critic. The exact
current plan and approved Blueprint versions provide provenance. Their scoped
requests replace global plot prose; all 19 measured historical requests are
shorter. See [ADR 0021](../docs/adr/0021-shared-scene-boundary.md) and the
[implementation/probe report](../docs/benchmark_reports/scene-boundary-v37-2026-10-08.md).

- [x] Preserve approved artifacts, current canon and input lineage while sharing
  the boundary on initial and revision calls, without a new role or model call.
- [x] Distinguish premature completion from permitted setup, foreshadowing,
  incidental follow-through and approved overlap; retain existing hard gates.
- [x] Verify 11 focused offline cases, persisted revision/replay, and final
  Python/frontend checks (665 Python tests, 11 frontend tests, production build).
- [x] Prepare five isolated critic probes, obtain explicit permission, and run
  the frozen original, stopping/foreshadowing controls, assigned scene-2
  verification and a missing-turn control.
- [x] Verify prepared/live hashes, source immutability and usage separately from
  actual billing; retain the unsuccessful overrun result without rerolling.
- [ ] Demonstrate reliable overrun detection and fresh writer behavior.

All five probes validated on their first attempts. Proper stopping,
foreshadowing and correctly assigned verification passed; the missing-turn
control produced a blocking assignment issue. **The original scene-1 overrun
still passed with three 5/5 scores.** The model praised journal comparison while
describing the ending as a decision to verify. The context is now available, but
the requested comparison is not reliably applied.

Usage was 53,809 input / 2,497 output tokens: USD 0.00853206 at dated published
rates, against an approved maximum estimate of USD 0.06560. Actual charges remain
unknown. No new writer generation, canonical change or full-story rerun occurred.
The next proposed target is a small evidence-backed boundary assessment within
the existing critic response; this further change is not implemented.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Required critic boundary comparison implemented and probed 2026-10-08

**Implementation COMPLETE — overrun detection still unqualified; stabilization IN PROGRESS.**
Prompt v38 / graph v9 requires an achieved state, separate current/next comparisons,
current evidence handles and an overrun status inside the existing critic call.
Successful comparisons are retained with exact input lineage; malformed responses
use bounded review repair. A valid reported overrun becomes a blocking assignment
issue regardless of craft scores. See
[ADR 0022](../docs/adr/0022-required-critic-boundary-comparison.md) and the
[implementation/probe report](../docs/benchmark_reports/critic-boundary-v38-2026-10-08.md).

- [x] Require bounded comparisons and exact current evidence in Local/Cloud
  schemas and application validation; specialize away inapplicable overruns.
- [x] Preserve independent hard gates, canonical schemas, writer messages,
  profiles, call/revision budgets and graph routing.
- [x] Export bounded, redacted successful audits and failed-review diagnostics.
- [x] Pass 23 new focused cases and complete checks: 688 Python tests, 11 frontend
  tests, lint/format/type checks and production build.
- [x] Obtain explicit permission and run the same five v37 frozen inputs under
  v38; verify exact request/response/source hashes and retain all results.
- [ ] Demonstrate improved overrun detection and qualify fresh writer behavior.

All five probes validated on their first calls and retained their v37 verdicts.
The original still passes with three 5/5 scores, but its required comparison now
explicitly acknowledges verification beyond the decision to verify. It permits
this as a general match, reserving a particular secret flourish for scene 2.
The stopping, foreshadowing and assigned-verification controls pass. The
missing-turn control correctly blocks on assignment but also emits a questionable
extra plot allegation. The comparison is observable; correctness remains fallible.

Usage was 53,894 input / 3,484 output tokens, estimated at USD 0.00893876 against
the approved maximum estimate of USD 0.06560. Actual charges are unknown. The five
initial requests grow by 134 characters each; sampled revision requests grow by
134–912 characters without increased budgets. No writer call, canonical edit or
formal rerun occurred.

The next policy question is whether retaining a more specific later detail
authorizes material advancement beyond the current endpoint. Further changes
and additional probes are not included in this implementation.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Current scene endpoint made independently binding and probed 2026-10-08

**Implementation COMPLETE — original overrun still missed; stabilization IN PROGRESS.**
Prompt v39 / graph v9 tells writer and critic that retaining a more specific later
detail does not authorize an earlier result beyond the current endpoint.
Inconclusive tests, setup and incidental follow-through remain allowed within
that endpoint; explicit current-plan instructions can authorize overlap. See
[ADR 0023](../docs/adr/0023-binding-current-scene-endpoint.md) and the
[implementation/probe report](../docs/benchmark_reports/binding-endpoint-v39-2026-10-08.md).

- [x] Share the revised policy and request the authorizing current-plan field
  and instruction within the existing five-field critic comparison.
- [x] Permit an overrun with a current outcome/turning-point anchor independently
  of a next reservation, including final scenes; preserve other hard gates.
- [x] Route reported overruns through existing blocking issues and revision,
  with repair guidance that removes the unassigned result rather than one detail.
- [x] Preserve schemas, profiles, budgets, repair guidance v10 and graph routing.
- [x] Pass 11 new cases and full checks: 697 Python tests, 11 frontend tests,
  lint/format/type checks and production build.
- [x] Run seven explicitly approved, hash-frozen Cloud critic probes: the same
  five v38 inputs plus an inconclusive test and synthetic authorized overlap.
- [ ] Demonstrate semantic overrun detection, fresh writer compliance and
  full-story recovery.

All seven probes validated on their first calls and returned `no_overrun`.
The original still passes with perfect scores: the critic acknowledges an
identical handwriting match but labels the comparison preliminary, treats the
current outcome as satisfied and relies on the later stronger revelation.
The five legitimate-progress controls pass without boundary false positives,
but this does not establish discrimination when the positive case is missed.
The missing-turn control correctly blocks on assignment and retains an extra
overbroad plot allegation. No semantic rerolls or writer calls occurred.

Usage was 74,937 input / 4,778 output tokens, estimated at USD 0.01240238 against
the approved maximum estimate of USD 0.09184. Actual charges are unknown. The
seven critic requests grow by 251 characters; corresponding writer requests grow
by 254, with unchanged budgets. Source/request/response hashes verified and
canonical stories, sealed benchmarks and historical results remain unchanged.

The next diagnostic question is whether next-scene context still anchors this
judgment or the current outcome is independently treated as a minimum achievement.
No additional ablation or response-contract change is included here.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Controlled next scene reservation comparison completed 2026-10-09

**Diagnostic comparison COMPLETE — overrun detection unresolved; stabilization IN PROGRESS.**
Production remains prompt v39 / graph v9. Twelve approved isolated probes compare
the same request with its explicit next-scene reservation present or projected
as absent. Three paired seeds test the original OH-V01-002 overrun; one pair each
tests an inconclusive attempt, explicitly authorized verification and a missing
required turn. See the
[comparison report](../docs/benchmark_reports/reservation-context-comparison-2026-10-09.md).

- [x] Freeze exact inputs, unchanged system/schema/settings and a single-field
  projection; balance pair order and predeclare the stopping rule.
- [x] Verify that both conditions retain the overrun route and that request,
  materialized guidance and diagnostic audit use the same projected boundary.
- [x] Run the approved twelve probes, preserving all fourteen calls including
  two bounded structural repairs for invalid evidence-handle ordinals.
- [x] Reconstruct every request, replay validated materialization and verify
  source/request/response hashes; pass 36 focused probe/endpoint tests.
- [ ] Establish correct overrun detection and full-story recovery.

The original passes with `no_overrun` under every tested seed in both conditions.
All three no-reservation reviews explicitly recognize completed verification,
then treat the assigned decision to verify as achieved. Two reservation-present
reviews require structural repairs, so only one original pair consists of two
validated first calls. The rejected responses also propose no-overrun, but are
not counted as accepted critiques. The legitimate controls pass and the missing
turn blocks independently in both conditions.

The explicit reservation is not necessary for this failure. Broader creative-brief,
location and premise guidance still describes verification in both conditions;
its influence versus interpreting the endpoint as a minimum remains unresolved.
The next diagnostic target is this distinction between story-wide goals and
current-scene obligations, before further production changes.

Usage was 146,702 input / 9,643 output tokens, estimated at USD 0.02439548 using
the recorded October 8 rates, within the approved USD 0.15744 allocation estimate.
Actual charges remain unknown. Production source, canonical stories, sealed
benchmarks and historical results are unchanged; no writer or full-story run
occurred. Full application gates were not repeated for this diagnostic/docs change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Broader context and current scene obligation comparison completed 2026-10-09

**Diagnostic comparison COMPLETE — overrun detection unresolved; stabilization IN PROGRESS.**
Production remains prompt v39 / graph v9. Twelve approved isolated probes compare
the full no-reservation request with a projection that retains only the current
plan and style guide in the Blueprint view. The exact draft, current obligations,
identity/viewpoint context, empty initial Bible, review policy and model settings
remain unchanged. See the
[comparison report](../docs/benchmark_reports/broader-context-comparison-2026-10-09.md).

- [x] Freeze three paired seeds for the original overrun and one pair each for
  inconclusive investigation, authorized verification and a missing turn.
- [x] Verify the Blueprint-only reduction, exact source inputs and unchanged
  schema/current obligations/evidence; retain the overrun route in both conditions.
- [x] Run the twelve approved probes once; all validate on their first calls.
- [x] Verify request/response/source hashes and exact materialization replay;
  pass 36 focused probe/endpoint tests.
- [ ] Demonstrate faithful endpoint enforcement and full-story recovery.

The original passes with `no_overrun` for all three seeds in both conditions.
Every reduced-context original review recognizes completed verification; one
restates the assigned decision-to-verify outcome as verification itself. The
inconclusive and authorized controls pass, while the missing turn correctly
blocks independently. All boundary statuses are no-overrun, so the legitimate
controls do not establish discrimination. Broad plot allegations also persist.

The omitted guidance is not necessary for the observed failure under the
no-reservation condition. This does not establish that context never influences
judgment. The next target is explicit terminal-state interpretation: a synthetic
plan control stating that no handwriting match is established by scene end,
compared with the existing wording and authorized verification. That stronger
instruction has not been tested or adopted in production.

Each reduced request removes 7,521 characters and 1,520 reported input tokens.
Total usage was 114,884 input / 8,325 output tokens, estimated at USD 0.01941376
using recorded October 8 rates against the approved USD 0.15744 allocation.
Actual charges remain unknown. Production code, canonical stories, sealed
benchmarks and historical results are unchanged; no writer or full-story calls
occurred. Full application gates were not repeated for this diagnostic/docs change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Explicit unresolved endpoint comparison completed 2026-10-09

**Diagnostic comparison COMPLETE — explicit endpoint detected; stabilization IN PROGRESS.**
Production remains prompt v39 / graph v9. Twelve approved isolated probes retain
standard story context and the later-scene reservation. The same original draft
is reviewed under three outcome wordings at three seeds: original decision,
explicitly unverified at scene end, and authorized verification. Three further
probes cover inconclusive investigation under the first two wordings and a
missing required turn under the explicit endpoint. See the
[comparison report](../docs/benchmark_reports/explicit-endpoint-comparison-2026-10-09.md).

- [x] Freeze the twelve requests and rotated condition order before inference;
  validate synthetic plan/Blueprint/Bible lineage and all outcome copies.
- [x] Verify only outcome wording and associated version references differ;
  preserve exact drafts, evidence, broader context, schema and settings.
- [x] Run all twelve approved probes once; all validate on their first calls.
- [x] Verify request/response/source hashes and exact materialization replay;
  pass 36 focused probe/endpoint tests.
- [ ] Consolidate duplicate overrun findings without losing independent issues.
- [ ] Demonstrate actual writer repair, broader endpoint reliability and
  full-story recovery before technical acceptance.

The explicit no-match endpoint produces REVISE / overrun for all three original
draft seeds, using the same exact conclusive-match evidence. Original decision
wording and explicit permission to verify both produce PASS / no-overrun, 3/3.
Inconclusive investigation passes under both tested wordings; the missing turn
correctly blocks independently. These are normalized critic verdicts, not
executed writer revisions. Enforcement of the original implicit boundary remains
unresolved; the positive result applies to a stronger synthetic instruction.

Each positive response reports the same overrun through both boundary and
assignment routes, producing two blocking outcome issues. This needs a focused
normalization fix before testing the full repair loop. Repair advice about a
suspected forgery also needs scrutiny: uncertainty about authorship does not
erase an already established match. The proposed planning owner is the existing
Blueprint integrator, with coherence checked by the Blueprint critic and exact
approved endpoints shared by writer and critic; that planning change is not
implemented here. Useful story context remains intact.

Usage was 126,270 input / 8,853 output tokens, estimated at USD 0.021219 using
recorded October 8 rates, within the approved USD 0.15744 allocation estimate.
Actual charges remain unknown. Production source, canonical stories, sealed
benchmarks and historical results are unchanged. No writer or full-story calls
occurred; full application gates were not repeated for this diagnostic/docs change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Consolidated overrun reporting and writer repair completed 2026-10-09

**Current-review consolidation and bounded experiment COMPLETE — stabilization IN PROGRESS.**
New executions use production contract v40 / graph v9. Boundary and assignment
reports with the same anchor and exact evidence-handle set become one blocking
issue, preserving both explanations and repairs. Independent anchors/evidence,
craft/POV blockers and malformed-response validation remain intact. No new model
call, instruction, schema, migration or revision allowance is added. See
[ADR 0024](../docs/adr/0024-consolidated-scene-overrun-reporting.md) and the
[implementation/live report](../docs/benchmark_reports/consolidated-overrun-writer-repair-2026-10-09.md).

- [x] Consolidate the observed current boundary/assignment duplicate route without
  losing either assessment or bypassing validation.
- [x] Replay all twelve saved reviews: three duplicate pairs consolidate;
  nine other results remain exactly equal.
- [x] Add 13 regression cases including persisted shared writer/critic repair
  tests and replay; pass full Python/frontend quality gates.
- [x] Run three explicitly approved isolated writer/critic pairs and an
  unchanged-draft control; audit exact requests, responses and artifact lineage.
- [x] Inspect full revised prose and preserve exact diffs, distinguishing model
  verdicts from observed changes.
- [ ] Address overlap between current findings and unmet historical repair tests
  without erasing independent obligations or source-test identity.
- [ ] Establish broader endpoint reliability, full-story recovery, technical
  repeatability, preference and cost acceptance before closing Step 19.

Two revisions clearly leave the match unresolved and pass; the third keeps
apparent identity and forgery doubts entangled and requires revision. The control
correctly rejects unchanged prose. All three writers validate on their first
calls; two critics need one structural retry for mistyped evidence handles.
Seven probes use nine calls. Each writer changes four relevant paragraphs and
preserves nine exactly, including the warning and ten-year-future realization.
No second writer revision, continuity or full-story run occurs. The explicit
endpoint remains a synthetic plan, not an automatic Blueprint-generation change.

The two blocked live reviews confirm current-route consolidation but expose
another duplicate path: an unmet historical repair is appended beside a current
finding, with different evidence sets. This is recorded for follow-up; duplicate
reporting is not claimed solved throughout the revision loop. The remaining
semantic target is a clear distinction between an unestablished handwriting
match and uncertain authorship of a likeness already recognized as matching.

Verification: Ruff, strict mypy (172 files), all 710 Python tests, frontend
format/lint/types, 11 frontend tests and production build. The initial full Python
run had one SQLite-lock worker failure; the five worker tests and a second full
suite passed unchanged. The live estimate is USD 0.01559182 for 85,693 input /
8,987 output tokens, within the approved 14-call / USD 0.09184 allocation.
Actual charges remain unknown. Canonical stories, sealed benchmarks and prior
evidence are unchanged.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Linked historical repair findings evaluated 2026-10-09

**Fixed diagnostic COMPLETE — candidate verification and stabilization IN PROGRESS.**
Production contract v41 / graph v9 adds explicit current-finding links to existing
repair checks. Valid links retain the original claim, repair and test identity
with current evidence. Independent findings and distinct original IDs remain;
invalid or partial links cannot bypass response validation. Current wording is
preserved in the audit. No new role, call, canonical schema or migration is added.
See [ADR 0025](../docs/adr/0025-linked-historical-repair-findings.md) and the
[v41 report](../docs/benchmark_reports/linked-repair-findings-v41-2026-10-09.md).

- [x] Implement explicit provenance links, guarded consolidation and shared audit
  evidence without fuzzy matching or category-only suppression.
- [x] Add and pass 28 regression cases, including two persisted revisions and
  replay; pass lint/types and frontend quality gates.
- [x] Replay four prior responses with explicitly labeled manual link annotations;
  preserve verdicts and original targets. These are offline wiring tests.
- [x] Run the approved five critic probes once; replay every valid/failed response
  and verify frozen requests, evidence and original repair lineage.
- [ ] Resolve invalid links on satisfied repairs, then qualify the revised protocol.
- [ ] Resolve the recurring worker shutdown test failure and pass the full Python
  gate before merging the candidate or running further cloud probes.
- [ ] Establish reliable independent reporting of the missing-turn control and
  resolve unstable match-versus-authorship interpretation.
- [ ] Establish broader technical repeatability, full-story recovery, preference
  and cost acceptance before closing Step 19.

The unchanged draft now reports its two original obligations once each. Four
probes validate on their first calls. Revision 19102 instead fails both attempts
because met checks link nonexistent current findings; its proposed PASS is not
accepted. Revision 19103 passes. The ambiguous 19104 revision changes from v40's
REVISE to PASS without prose changes. The missing-turn control requires revision
but notices the omitted turn only in assessment text, reopens the old outcome
repair and creates no independent turn target. That control fails its intended
expectation; no emitted turn finding was removed by consolidation.

The six calls consume 71,252 input / 6,353 output tokens, estimated at USD
0.01251648 using recorded October 8 rates, within the approved ten-call /
USD 0.06560 allocation. Actual charges remain unknown. No writer, canonical
change or full-story run occurs. The source snapshot and prior evidence retain
their frozen hashes. The initial 732-test suite, Ruff, strict mypy (173 files),
frontend format/lint/types, 11 frontend tests and production build pass. Deterministic
checks do not establish the critic's semantic reliability. Final code review also
adds complete issue-field validation before linked craft findings can be removed;
six new cases reproduce then verify that correction. The tested executor is
archived, the final hash is recorded separately, and all saved responses replay
identically under the correction without additional cloud calls.

Final validation also exposes an intermittent worker shutdown failure, with an
invocation remaining marked running. The worker group reproduces it once, then
passes unchanged; a limited in-memory HEAD-source comparison also passes. Its
cause remains unestablished, and no worker change is included in this slice.
Both final full 738-test runs report 737 passed / 1 failed on that same shutdown
assertion. The full gate remains failed; this candidate is not marked ready to
merge. Worker cleanup is the immediate offline stabilization target.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Worker cleanup and critic v42 implemented 2026-10-09

**Local implementation, verification and fixed diagnostic COMPLETE — reviewer qualification IN PROGRESS.**
Production contract v42 / graph v9 gives satisfied repair checks an empty-link
schema alternative and requires independent assignment defects to be reported
separately. Original repair identity and guarded consolidation remain intact.
The recurring worker failure is reproduced by delaying cancellation persistence:
the graph wrapper previously returned before its specialist's cleanup finished.
Workflow-scoped task tracking and protected persistence now join that work before
closure. See [ADR 0026](../docs/adr/0026-durable-worker-cancellation-cleanup.md),
[ADR 0027](../docs/adr/0027-satisfied-repair-schema-and-independent-findings.md),
and the [v42 report](../docs/benchmark_reports/worker-cleanup-critic-v42-2026-10-09.md).

- [x] Reproduce the cleanup ordering locally and verify that repeated cancellation
  cannot end stop before the gated persistence operation finishes.
- [x] Cover Blueprint worker stop/restart, real production-service cleanup,
  graph/leaf cancellation, failure propagation and concurrent-workflow isolation.
- [x] Reproduce the separate SQLite stop-command lock failure; move generic
  control-store writes off the event loop and test real checkpoint contention,
  post-commit worker notification and idempotency for all four mutations.
- [x] Encode met checks with empty links while retaining invalid-response rejection.
- [x] Verify an independent turn reaches the next writer and critic with its own
  source-bound test, whether the original outcome repair is met or unmet.
- [x] Replay all six saved v41 raw responses unchanged: four identical valid
  critiques and the same two rejected attempts.
- [x] Freeze the same five diagnostic cases with exact source/request/code hashes,
  unchanged inputs/settings and a ten-call / USD 0.06560 maximum rate estimate.
- [x] Pass all 758 Python tests, Ruff lint/format, strict mypy (177 files),
  frontend format/lint/types, 11 frontend tests and production build.
- [x] Run the approved five probes in six calls; reconstruct every request and
  replay every valid/failed response and its audit exactly.
- [x] Observe valid satisfied checks and independent missing-turn reporting on
  their frozen controls, keeping the original outcome repair met.
- [ ] Resolve incompatible links from original repairs and duplicate reporting
  of the new turn as a generic plot blocker; qualify the same controls again.
- [ ] Resolve the ambiguous match-versus-authorship judgment and broader reviewer
  reliability; the unchanged negative control remains a failed review.
- [ ] Establish broader technical repeatability, full-story recovery, preference
  and cost acceptance before closing Step 19.

Four live probes validate on their first calls. The unchanged draft fails both
attempts because its major tension repair links a blocking outcome finding also
claimed by the original outcome repair. The missing-turn control now preserves
the repaired outcome and reports the new turn separately, but adds a second
generic plot blocker for the same defect; offline reconstruction yields two new
repair tests. Saved repair 19102 passes with empty met links, where v41 failed
twice. Repairs 19103 and 19104 also pass; the latter's semantic ambiguity remains.

The six calls use 72,298 input / 6,296 output tokens, estimated at USD 0.01264012
against the approved USD 0.06560 allocation at recorded October 8 rates. Actual
charges remain unknown. No writer call or full-story run occurs. Diagnostics
retain the synthetic explicit endpoint; canonical stories, sealed benchmarks and
prior evidence remain unchanged. No role, inference allowance, canonical field
or migration is added. Worker verification is complete for the tested local
paths; narrative reviewer qualification remains open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Eligible repair links and assignment restatements v43: 2026-10-10

Implementation, local verification and the approved diagnostic are **COMPLETE**;
live reviewer qualification remains **IN PROGRESS**. Production contract v43 / graph v9 constrains
eligible original-repair links before inference and adds an explicit reference
for generic issues that repeat current assignment findings. See
[ADR 0028](../docs/adr/0028-eligible-repair-links-and-assignment-restatements.md) and
the [v43 report](../docs/benchmark_reports/eligible-repair-links-v43-2026-10-10.md).

- [x] Bind eligible links by original category/severity and populated current
  assignment, including boundary fallback and satisfied empty-link checks.
- [x] Keep runtime existence, category/severity, ownership and complete-route
  validation; preserve original repair IDs and independent defects.
- [x] Validate explicit generic assignment repetitions before combining them;
  preserve their descriptions, evidence and advice in one assignment finding.
- [x] Retain bounded, redacted repetition audits and rejection evidence.
- [x] Add 26 local cases, including persisted writer/critic repair propagation.
- [x] Replay all six unmodified v42 responses; label protocol annotations
  separately and verify one new turn target from an explicit restatement.
- [x] Freeze five requests with identical source inputs/settings, unchanged
  system instructions, and a ten-call / USD 0.06560 maximum rate estimate.
- [x] Pass all 784 Python tests, Ruff lint/format, strict mypy (178 files),
  frontend format/lint/types, 11 frontend tests and production build.
- [x] Run the five revised probes with explicit approval; inspect raw responses,
  validation, canonical findings and resulting repair identities.
- [x] Observe one independent turn repair on the missing-turn control, while
  retaining its satisfied original outcome repair and empty links.
- [ ] Resolve invalid restatement metadata, incomplete consolidated-route links
  and exact-category drift on the unchanged control; qualify it again.
- [ ] Resolve remaining semantic ambiguity and establish broader repeatability,
  full-story recovery, preference and cost acceptance.

Six approved calls yield four valid reviews and one failed probe. The missing
turn is now reported only through its dedicated route and creates one new repair
target; this live case avoids duplication rather than exercising non-null
consolidation. Three saved revisions pass with empty met links; the ambiguous
match/authorship interpretation remains unresolved. The unchanged draft fails
both attempts on an invalid generic assignment reference. Manual counterfactuals
also expose a severity mismatch, omitted boundary link and category spelling
drift. These annotations do not convert the live failure into a pass.

Every request, response, validation result and audit reconstructs exactly. The
six calls use 73,892 input / 6,363 output tokens, estimated at USD 0.01289008 within
the approved USD 0.06560 allocation at recorded October 8 rates. Actual charges
remain unknown. There are no writer calls or full-story runs. Source database,
canonical stories and sealed benchmarks are unchanged. No role, inference
allowance, canonical schema field or migration is added.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Severity-bound restatements and precise critic retries v44: 2026-10-10

Implementation, local verification and the approved five-probe campaign are
**COMPLETE**; reviewer qualification remains open. Production contract v44 /
graph v9 adds severity
branches for generic restatement references and precise structural metadata for
the existing critic retry. See
[ADR 0029](../docs/adr/0029-severity-bound-restatements-and-precise-retries.md) and
the [v44 report](../docs/benchmark_reports/restatement-retries-v44-2026-10-10.md).

- [x] Require null restatement references for nonblocking issues in schema and
  materialization; retain explicit valid blocking repetitions.
- [x] Provide candidate-bound allowed references, original category/severity,
  complete/missing routes and competing owners without rejected allegations.
- [x] Collect independent link errors after rejection without repairing or
  accepting the rejected response; keep existing limits and fallback guidance.
- [x] Add 22 regressions, including persisted retry with unchanged candidate,
  input artifacts and writer count.
- [x] Replay six unmodified v43 responses: four identical valid critiques and
  two rejected responses producing precise offline retry packets.
- [x] Freeze five requests with identical inputs/settings and a ten-call /
  USD 0.06560 maximum recorded-rate estimate; initial schema growth is 162 chars.
- [x] Pass all 806 Python tests, Ruff lint/format, strict mypy (180 files),
  frontend format/lint/types, 11 frontend tests and production build. Record the
  initial Vitest worker startup timeout and unchanged isolated passing rerun.
- [x] Run all five explicitly approved probes: eight calls, four valid reviews,
  one failed unchanged control; 100,171 input / 8,463 output tokens,
  USD 0.01740914 at recorded rates; actual charges unknown.
- [x] Reconstruct every request and response, verify original repair lineage and
  unchanged frozen hashes, and retain failures plus labeled offline diagnostics.
- [x] Record that both missing boundary links were corrected, but the unchanged
  retry introduced an invalid reference and the ambiguous revision retained a
  generic pacing duplicate despite structural recovery.
- [ ] Distinguish repeated assignment allegations from independent craft claims
  without treating null or category/severity differences as proof of independence.
- [ ] Establish reviewer reliability, resolve semantic ambiguity and demonstrate
  full-story recovery, preference and cost acceptance before closing Step 19.

No writer call, canonical edit, migration, new specialist or inference allowance
is introduced. Story context and system instructions remain unchanged. Structural
hints are not manuscript evidence and do not establish narrative equivalence.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Explicit assignment versus craft comparison v45: 2026-10-10

Implementation, local verification and the approved diagnostic campaign are
**COMPLETE**; semantic qualification remains outstanding. Production contract v45 / graph v9 requires
an explicit comparison for generic critic issues and permits declared repetitions
at any severity. See [ADR 0030](../docs/adr/0030-explicit-assignment-and-craft-comparison.md)
and the [v45 report](../docs/benchmark_reports/claim-comparison-v45-2026-10-10.md).

- [x] Require current finding references and an explanation of the same defect
  or the distinct craft problem remaining after a minimal assignment correction.
- [x] Validate comparison coverage and preserve original repair identities;
  retain declared repetitions without promoting independent craft severity.
- [x] Persist bounded/redacted comparisons in invocation audits, with precise
  structural retry guidance that excludes rejected review prose.
- [x] Add 23 regressions, including two persisted workflows with one new
  assignment repair and one independent craft repair passed to writer and critic.
- [x] Replay eight saved v44 responses and two labeled offline annotations;
  three valid reviews are unchanged, and the duplicate-bearing response now
  requires the comparison. Edited responses are not live model successes.
- [x] Freeze the same five private requests/settings at ten calls maximum and
  USD 0.06560 recorded-rate estimate; initial schema growth is 1,242 characters.
- [x] Pass all 829 Python tests, Ruff lint/format, strict mypy (182 files), frontend
  formatting/lint/types, 11 frontend tests and production build. The first full
  run's old v40 fixture was corrected to supply required comparison coverage;
  no production validation was weakened.
- [x] Run the five explicitly approved probes: six calls, four valid reviews,
  one failed unchanged control; 75,950 input / 6,581 output tokens and
  USD 0.0132654 recorded-rate estimate; actual charges unknown.
- [x] Reconstruct all requests and responses, verify frozen hashes and original
  repair lineage, and retain the first-response/retry classification change.
- [x] Compare the missing-turn control with accepted repair 19103: identical
  verification text and noncandidate inputs/settings, but an extra outcome
  complaint. Preserve this contextual variation without claiming its cause.
- [ ] Stabilize claim classification through structural repair; no successfully
  validated generic comparison occurred in this campaign.
- [ ] Investigate the additional decision-to-verify complaint separately from
  generic craft deduplication.
- [ ] Qualify model accuracy, broader recovery, human preference and cost
  acceptance before closing Step 19.

No new role, writer change, extra call allowance, canonical field or migration
is introduced. Comparison text is a model judgment, not verified story truth.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Preserve critic classification during structural repair v46: 2026-10-10

Implementation, all local verification and the approved diagnostic campaign are
**COMPLETE**; reviewer qualification remains open. Production contract v46 / graph v9,
critic retry policy 13. See [ADR 0031](../docs/adr/0031-preserve-critic-classification-during-structural-repair.md)
and the [v46 report](../docs/benchmark_reports/retry-classification-v46-2026-10-10.md).

- [x] Retain valid classification choices with candidate/task binding and bounded
  category, severity and exact current evidence metadata; exclude rejected prose.
- [x] Reject changed classifications, missing complaints and duplicate counts
  while allowing reordered issues and evidence. Preserve counts for complaints
  sharing metadata without claiming semantic identity.
- [x] Cover materialization and later domain-validation failures; preserve
  original repair IDs and current-finding validation without an extra model call.
- [x] Add 33 regressions, including a persisted structural retry on the same draft
  with the same original repair tests and writer count.
- [x] Replay six saved v45 outputs: four valid results unchanged, both failures
  retained. Reject the manually coverage-corrected retry's classification drift;
  accept the manually format-corrected first response with no new repair target.
- [x] Verify all five initial messages/settings unchanged and freeze three
  retry-only requests at three calls maximum / USD 0.01968 recorded-rate estimate.
- [x] Pass all 862 Python tests, Ruff lint/format, strict mypy (184 files), frontend
  formatting/lint/types, all 11 frontend tests, production build and diff checks.
- [x] Run the three explicitly approved private retries: 3/3 preserve classification,
  repair comparison structure and complete the boundary/outcome links. All three
  still fail after newly linking the original tension repair to a generic issue
  that has been consolidated. No valid live review is claimed.
- [x] Inspect each raw claim/comparison, verify all frozen hashes and isolate the
  remaining error in three labeled offline copies. Changing only the ineligible
  link to [] preserves both original repair IDs and introduces zero new targets.
- [x] Record three calls, 41,832 input / 4,225 output tokens and USD 0.00754648
  recorded-rate estimate; actual charges remain unknown. No writer or canonical edits.
- [ ] Distinguish retained raw complaints from separately linkable current findings
  before emission; exclude consolidated repetitions from original craft links.
- [ ] Qualify semantic accuracy and investigate the separate decision-to-verify
  complaint before claiming wider critic reliability.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Independent craft owns original repair links v47: 2026-10-10

**IN PROGRESS**: implementation and required local quality checks complete.
All three live retries exclude the invalid link; two fully validate, and one
retains a comparison-format failure. Production contract v47 / graph v9,
critic retry policy 14. See [ADR 0032](../docs/adr/0032-independent-craft-owns-original-repair-links.md)
and the [v47 report](../docs/benchmark_reports/independent-repair-links-v47-2026-10-10.md).

- [x] Permit original craft IDs only on independent issues with exact original
  category/severity; require empty craft-check link arrays and reject legacy indexes.
- [x] Validate explicit ownership and translate it to internal routes without
  merging original IDs, dropping obligations or weakening evidence validation.
- [x] Preserve classification during retries; provide eligible ID hints and
  separate wire/effective links in audits, without replaying rejected prose.
- [x] Add 22 regressions, including durable writer/critic propagation of the same
  two originals with independent craft and a consolidated assignment repetition.
- [x] Replay three v46 failures unchanged and reproduce their three labeled
  one-field counterfactuals without changing canonical outcomes.
- [x] Prepare three matching controlled retries: same saved failure, inputs,
  settings and seeds; maximum three calls / USD 0.01968 recorded-rate estimate.
- [x] Pass required quality gates: 884 Python tests, 11 frontend tests, Ruff,
  strict mypy, frontend formatting/lint/types and production build.
- [x] Obtain explicit approval, run exactly three private retries and inspect
  both structure and claims: classification and link exclusion hold in 3/3;
  2/3 validate with the same two originals and zero new targets. Recorded-rate
  estimate USD 0.00770396; actual charges unknown.
- [x] Isolate the remaining comparison-format failure locally: wrapping only its
  existing comparison text and reference validates with the same original tests.
  The actual response stays failed; no additional model attempt is granted.
- [x] Strengthen exact comparison-object instructions in v48 and qualify the
  remaining failure on the same three controlled retries: all validate without
  relaxing validation or classification (see the v48 record below).
- [ ] Qualify broader reviewer accuracy and investigate the separate
  decision-to-verify complaint before closing Step 19.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Explicit comparison retry shape v48: 2026-10-10

**Focused change COMPLETE**: implementation, required local quality checks and
three approved controlled retries complete. All three validate; broader Step 19
qualification remains IN PROGRESS. Production contract v48 / graph v9, critic
retry policy 15. See the [v48 report](../docs/benchmark_reports/comparison-shape-v48-2026-10-10.md).

- [x] State both required comparison fields, object shape and bounds in the
  targeted retry directive, deriving structure from the existing schema.
- [x] Preserve comparison semantics, classification, original repair links and
  existing call allowances without replaying rejected prose or changing schemas.
- [x] Add eight regressions, including two persisted retries retaining independent
  craft and consolidated assignment complaints without extra writer work.
- [x] Replay all three v47 responses with unchanged outcomes and verify the prior
  labeled offline correction produces the same canonical result.
- [x] Prepare the same three saved-first-failure retries: only comparison guidance
  and policy version change, maximum three calls / USD 0.01968 estimated.
- [x] Pass required quality gates: 892 Python tests, 11 frontend tests, Ruff,
  strict mypy, frontend formatting/lint/types and production build.
- [x] Obtain explicit approval and run exactly three retries: all return valid
  comparison objects, retain classification, exclude invalid craft links and
  preserve exactly two original repairs with no new target. Inspect the claims
  and replay all responses without edits; verify frozen evidence and database.
- [x] Record 43,581 input / 4,244 output tokens, USD 0.00779894 estimated at the
  recorded October 8 rates; actual charges remain unknown.
- [ ] Qualify broader reliability and the separate decision-to-verify complaint
  before closing Step 19.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Decision versus inconclusive attempt investigation: 2026-10-10

**Focused investigation COMPLETE**: historical inspection and twelve approved
probes complete; production follow-up remains. Production v48 / graph v9 unchanged.
See the [investigation report](../docs/benchmark_reports/decision-vs-attempt-v48-2026-10-10.md).

- [x] Verify identical handwriting verification passages and shared noncandidate
  context/settings in the v45 repaired draft and missing-turn control.
- [x] Inspect ten saved v41–v45 responses: the repaired draft passes throughout;
  extra outcome allegations on the control vary and concern different defects.
- [x] Separate the actual outcome requirement from the critic's additional demand
  for a future decision to verify; retain uncertainty about its cause.
- [x] Prepare date-present/absent crossed with implicit, explicit prior decision
  and explicit future decision, at two paired seeds: twelve probes, maximum
  24 calls / USD 0.15744 recorded-rate estimate.
- [x] Verify exact synthetic edits, unchanged verification prose, shared context,
  original repair identity and four unchanged historical response replays.
- [x] Execute the approved fixed comparison: twelve first-call valid responses,
  six correct future-date passes; two unmodified missing-turn revisions (one with
  an extra outcome complaint); four incorrect missing-turn passes after explicit
  decision sentences. Original no-match repair remains met in all cases.
- [x] Inspect claim text and exact source evidence; record partial recurrence of
  the extra-demand pattern with a changed rationale, not a stable future-decision
  requirement. Verify all receipts, canonical replays, audits and frozen inputs.
- [x] Record 148,812 input / 11,062 output tokens, USD 0.02525848 estimated at
  recorded October 8 rates; actual charges unknown, no writer or production changes.
- [x] Select the next focused candidate: separate evidence-backed turning-point
  and outcome checks within the existing critic, with consistent blocker routing.
- [x] Implement that candidate without requiring explicit decision prose; see v49
  below. Live semantic qualification remains open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Independent mandatory scene checks v49: 2026-10-11

**Focused implementation and controlled probes COMPLETE; semantic qualification
remains IN PROGRESS.** Production prompt v49 / graph v9, critic retry policy 16. See
[ADR 0033](../docs/adr/0033-independent-mandatory-scene-checks.md) and the
[v49 report](../docs/benchmark_reports/mandatory-assignment-checks-v49-2026-10-11.md).

- [x] Require independent evidence-backed met/unmet checks for each populated
  current turning point and outcome; preserve action-based evidence of intent.
- [x] Route unmet checks into existing blocking assignment findings regardless
  of other satisfied checks, scores or historical repairs.
- [x] Preserve boundary consolidation, generic craft comparisons and original
  repair identity. Reject duplicate legacy reporting of the two mandatory anchors.
- [x] Reject malformed checks as review errors; retain the existing call limits,
  precise structural retries and bounded/redacted diagnostic evidence.
- [x] Pass 34 new local regressions including durable writer-versus-review retry
  behavior; explicitly port existing synthetic fixtures to the new wire contract.
- [x] Pass all required checks: 926 Python tests, 11 frontend tests, Ruff,
  strict mypy (189 files), frontend formatting/lint/types and production build.
- [x] Prepare the exact twelve v48 date/decision cases with unchanged artifacts,
  context, settings and budgets. Pin all requests, sources and candidate code.
  Twelve saved raw reviews correctly fail the new wire contract; four labeled
  human-authored annotations test deterministic blocker routing only.
- [x] Execute the twelve approved probes in 15 calls: 9/12 first-attempt valid,
  all twelve valid after three bounded structural retries. Verify exact request
  replays, output materialization, audits, original repair lineage and source hashes.
- [x] Record six correct future-date passes, two turn-only control revisions and
  four unchanged false passes now explicitly marking the turn met. The prior extra
  outcome complaint does not recur; all original no-match repairs remain met.
- [x] Record 199,327 input / 19,501 output tokens, USD 0.03570618 estimated at
  recorded October 8 rates, within the USD 0.15744 approval; actual charges unknown.
  No writer calls, full-story runs or canonical changes.
- [x] Implement a stricter full-proposition meaning of met while preserving
  indirect/action-based realization; v50 below completes the controlled test.
- [ ] Qualify independent semantic judgments before making broader reliability
  claims. Full-story repeatability, preference and cost acceptance remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Complete assigned fact means met v50: 2026-10-11

**Focused implementation and frozen comparison COMPLETE; broader qualification
IN PROGRESS.** Production prompt v50 / graph v9, critic retry policy 17. See the
[v50 report](../docs/benchmark_reports/complete-assigned-fact-v50-2026-10-11.md).

- [x] Define met as the complete assigned fact/state, including every explicit
  condition. A similar dramatic function or broad premise cannot replace a
  missing or contradictory required fact.
- [x] Preserve action-based evidence, embodied reactions and indirect narration;
  do not demand literal plan wording, explicit decision sentences or new conditions.
- [x] Deliver the rule through the existing critic assessment and structural
  retry paths. Keep schema, runtime validation, writer instructions and budgets.
- [x] Pass eight focused prompt-delivery/retry regressions; replay all fifteen
  saved v49 responses with twelve identical accepted results and three identical
  rejections. The four semantic false passes remain unchanged in this offline replay.
- [x] Pass all required checks: 934 Python tests, 11 frontend tests, Ruff,
  strict mypy (190 files), frontend formatting/lint/types and production build.
- [x] Prepare twelve matching v49 cases with identical input artifacts, settings,
  budgets and first user messages/output schemas. Pin code, source and request hashes.
- [x] Obtain explicit approval and complete twelve probes in 16 calls; all final
  results valid, eight on the first attempt. Correct all four v49 false passes:
  six missing-date controls each produce one turning-point blocker; six positive
  drafts remain accepted. All twelve outcomes and original no-match repairs stay
  met, including action-based decisions in the four implicit cases.
- [x] Inspect all final evidence and four rejected first responses; replay all
  sixteen responses and verify frozen requests, sources, code and database.
  Two first responses still select met despite acknowledging the wrong fact;
  structural retries recover them. Two other retries repair comparison objects
  while preserving valid classification and consolidating duplicate complaints.
  First-response validity is 8/12 versus v49's 9/12: no structural reliability claim.
- [x] Record 216,532 input / 21,654 output tokens and USD 0.03897608 at recorded
  October 8 rates, below the USD 0.15744 cap. Actual charges remain unknown.
  No writer calls, full-story runs or canonical changes.
- [ ] Qualify transfer to a separate scene with complete indirect/action-based
  fulfillment, a similar dramatic effect with a wrong/missing fact, and a genuinely
  missing decision. The comparison below qualifies these distinctions on one new
  scene with v50 unchanged; broader semantic and Step 19 acceptance remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Assignment transfer with unchanged v50: 2026-10-11

**Bounded comparison COMPLETE; broader qualification IN PROGRESS.** See the
[transfer report](../docs/benchmark_reports/assignment-transfer-v50-2026-10-11.md).

- [x] Select OH-V01-001 scene 1's existing approved touch-plus-psychic-pull turning
  point and decision-to-enter outcome. Preserve all source context and production
  prompt v50 / graph v9 / critic retry policy 17.
- [x] Prepare four diagnostic variants: touch present/absent crossed with an entry
  decision shown through action or an explicitly unresolved choice. Preserve the
  same indirect psychic pull and other prose between paired conditions. Include
  the both-missing case to test independent reporting.
- [x] Freeze twelve requests at three paired seeds with opaque draft identifiers,
  exact source lineage, no condition/expectation labels in model messages and no
  synthetic plan or repair history. Verify reconstruction and hashes locally;
  all eight existing v50 delivery/retry regressions pass.
- [x] Obtain explicit approval and complete twelve probes in 21 calls. All first
  mandatory check pairs match the inspected facts; all twelve final reviews are
  valid and correct on those checks. Six valid indirect turns and six action-based
  decisions are accepted; six missing touches and six missing decisions are found.
  Both-missing cases retain two independent blockers; no extra repair targets.
- [x] Inspect all passages and nine failed first responses. All negative reviews
  repeat a complaint with a comparison string instead of the required object;
  only 3/12 complete first responses validate. All retries preserve the native
  checks and valid classification and consolidate repeated complaints. The first
  schema already supplies the object; this is not missing schema delivery.
- [x] Replay all 21 responses and reconstruct requests; verify exact source/code
  and database hashes. Record 275,139 input / 24,356 output tokens and
  USD 0.04826186 at recorded October 8 rates, below the USD 0.15744 cap. Actual
  charges unknown. No production changes, writer/full-story calls or canonical changes.
- [x] Test a compact first-review comparison-object clarification while retaining
  v50 met semantics and existing schema/consolidation. Implementation and matched
  results follow below: v51 validates all twelve first responses. Separately retain
  the concern about repair advice demanding immediate causality or completed entry
  beyond the literal assigned minimum.
- [ ] Establish broader reliability; this one-scene transfer does not qualify
  other models, writer repairs, full-story repeatability, preference or cost acceptance.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### First-review comparison-object clarification v51: 2026-10-11

**Local implementation and bounded comparison COMPLETE; broader qualification
IN PROGRESS.** See the
[implementation and comparison report](../docs/benchmark_reports/first-review-comparison-v51-2026-10-11.md).

- [x] Add the successful comparison-object shape clarification to normal critic
  instructions for local/cloud original and revision reviews. Share the wording
  with the existing retry directive without changing that directive's output.
  Prompt v51 / graph v9 / critic retry policy 17.
- [x] Preserve the exact v50 obligation module, schemas, validation, classification
  retention, duplicate consolidation, repair links and writer contract.
- [x] Replay all 21 sealed v50 responses: twelve identical canonical results and
  nine identical structural rejections, including matching evidence/classification
  audits and retry packets. Verify all 116 sealed evidence-file hashes.
- [x] Freeze the same twelve transfer cases, source artifact versions, seeds,
  order, settings and budgets. Only the 291-character system clarification differs
  in model-facing requests; all first user messages and schemas remain identical.
- [x] Complete local checks: 937 tests pass in the full Python run and the sole
  obsolete prompt-size guard passes after its explicit allowance update. All 938
  collected tests are covered. The 54 focused regressions, Ruff, strict mypy,
  frontend formatting/lint/type checks, 11 frontend tests and production build pass.
- [x] Obtain explicit approval and complete twelve probes in twelve calls, with
  all first responses valid versus v50's 3/12. All nine generic repetitions now
  contain the correct object immediately; none requires a retry.
- [x] Inspect all checks, evidence, generic comparisons and repairs. Native check
  pairs and repair-target counts remain unchanged in all twelve cases: indirect
  fulfillment remains valid and missing touch/decision facts remain separate
  blockers. No extra craft/boundary finding or repair target. Record changed
  generic labels/links in three both-missing fresh reviews without claiming all
  review text or reasoning is identical.
- [x] Replay every new response and reconstruct its request; verify frozen code,
  source, prior evidence and database hashes. Record 150,528 input / 13,881 output
  tokens and USD 0.02662632 at recorded October 8 rates, below the USD 0.15744 cap.
  Actual charges unknown. No writer/full-story calls or canonical changes.
- [ ] Address stronger-than-assigned repair advice separately: immediate causal
  touch triggers and completed entry are prescribed beyond the explicit minimum.
  The focused v52 comparison follows below; its instruction does not resolve
  the repair-scope defect.
  Broader models, writer repair, full-story, preference and cost acceptance remain open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Minimum assignment repairs v52: 2026-10-11

**Local implementation and bounded comparison COMPLETE; repair-scope remedy
NOT QUALIFIED.** See the
[implementation and diagnostic report](../docs/benchmark_reports/minimum-assignment-repairs-v52-2026-10-11.md).

- [x] Add an instruction constraining current assignment assessments, native repairs
  and repeated generic complaints to the missing assigned fact. Preserve fulfilled
  facts and the current endpoint; do not invent causal order, immediacy or completed action. Retain
  explicit applicable assignment/canonical requirements. Keep optional suggestions
  outside mandatory repair text and acceptance conditions.
- [x] Preserve the v50/v51 definition of met and v51 comparison-object clarification.
  Prompt v52 / graph v9 / critic retry policy 17. No schema, validator, consolidation,
  historical repair-test, writer-contract or call-allowance change.
- [x] Preserve the uncommitted v51 baseline and replay its twelve responses to
  identical canonical results and audits. Verify prior sealed evidence and source
  database hashes; past stronger-than-assigned advice is not rewritten.
- [x] Freeze twelve probes: six cases at two seeds. Match four requests to v51's
  complete/both-missing baselines. Add pull-before-touch and settled-decision-outside
  positives, plus same-draft controls with one explicit causality or completed-entry
  requirement. Keep synthetic plans outside canon and preserve coherent lineage.
- [x] Complete full local checks: 946 Python tests, 29 focused regressions, Ruff,
  strict mypy across 192 files, frontend formatting/lint/type checks, 11 frontend
  tests and production build pass.
- [x] Obtain explicit approval and complete twelve probes in twelve calls, all
  first responses valid, with no retries. All eight generic complaints supply valid
  comparison objects and consolidate; no independent craft or boundary blocker.
- [x] Inspect all checks, cited passages, plans, generic complaints and complete
  repairs. Native check pairs match the inspected assignments in 10/12 reviews;
  both pull-before-touch positives gain unsupported causal blockers. Decision-only
  and explicit completed-entry controls are distinguished correctly at both seeds.
- [x] Record the unresolved primary target: neither matched both-missing review
  keeps complete advice within scope. Both touch repairs still prescribe causality;
  one generic complaint still prescribes crossing the threshold. Native baseline
  pairs remain unchanged from v51. Ten repair targets are reported where eight are
  supported; the two extra targets are native false findings, not duplicates.
- [x] Replay all twelve raw responses and reconstruct requests. Verify and seal
  frozen code, sources, prior evidence and database hashes. Record 153,616 input /
  13,206 output tokens and USD 0.02678864 at recorded October 8 rates, below the
  USD 0.15744 cap. Actual charges unknown. No writer/full-story calls or canonical
  changes. New controls have no historical v51 live arm; their failures do not
  establish a regression caused by v52.
- [ ] Test support in the assignment or applicable canon for claimed temporal,
  causal and completion requirements before treating them as mandatory. Retain
  action/indirect fulfillment. This next focused remedy is not implemented or
  qualified; broader reliability, preference and cost acceptance remain open.
- [x] Record the user's observation that v50/v51 charges appear below estimates as
  qualitative billing evidence awaiting more monitoring. Keep estimates, actual
  charges and broader cost acceptance separate; retain current reference ceilings.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Source-backed assignment requirements v53: 2026-10-11

**Local implementation and bounded comparison COMPLETE; remedy NOT QUALIFIED.**
See the [implementation and diagnostic report](../docs/benchmark_reports/requirement-basis-v53-2026-10-11.md).

- [x] Add a critic instruction requiring the assignment field or canonical artifact
  version/field, exact source words and applicability before treating causal,
  temporal or completion relations as mandatory. Carry only supported requirements
  into judgments and native/repeated repair advice. Retain action and indirect
  narration as valid fulfillment evidence; source quotation is not a prose test.
- [x] Preserve the exact met/minimum-repair rules, comparison-object clarification,
  schemas, validators, consolidation, writer contract and retry policy 17. Prompt
  v53 / graph v9. Support is a model instruction, not a semantic guarantee enforced
  by the application; false or inapplicable quotations still require inspection.
- [x] Pass 42 focused regressions, Ruff formatting/lint and strict mypy across 193
  files. Replay all twelve v52 responses to identical canonical results/audits;
  retain all 97 sealed v52 evidence files, its report and source database hashes.
- [x] Freeze sixteen probes at two seeds: twelve matched v52 requests and four
  new controls isolating explicit noncausal order or a synthetic applicable Bible
  rule. Verify exact paired drafts, single-clause context changes, schemas,
  coherent artifact lineage and canon-rule delivery. No canonical writes.
- [x] Complete the full Python suite: 954 tests pass. Required frontend
  formatting/lint/type checks, 11 frontend tests, production build and
  `git diff --check` also pass.
- [x] Obtain explicit approval and complete sixteen probes in sixteen calls, all
  first responses valid. All thirteen generic comparisons validate and consolidate;
  no independent craft, viewpoint or boundary blocker and no structural retries.
- [x] Inspect all 32 native checks, source claims, draft evidence and complete
  repairs. All twelve matched v52 status pairs are unchanged. Both unsupported
  causal blockers persist despite quoting the correct conjunction; neither
  both-missing repair set stays within the assigned minimum. Native decision
  repairs remain appropriate, and the unconditional completed-entry demand does
  not recur; avoid treating that wording difference as broad qualification.
- [x] Inspect new controls separately: both order-only repairs avoid demanding
  causation. Both canon-control verdicts are correct, but neither quotes/identifies
  the exact supporting Bible version/rule. One mentions its field only in generic
  advice and permits an insufficient intensification alternative in the native
  repair. Correct verdicts do not prove correct grounding or sufficient advice.
- [x] Replay all sixteen responses and reconstruct requests; verify and seal
  frozen code, source database, prior evidence and inputs. Record 206,870 input /
  18,707 output tokens and USD 0.03644460 at recorded October 8 rates, below the
  USD 0.20992 cap. Actual charges unknown. No writer/full-story calls or canonical
  changes. Four new controls have no historical v52 live arm.
- [x] Hold v53 stable and isolate assignment wording: original conjunction versus
  separately expressed facts and explicitly unassigned relationships, retaining
  explicit-relation and indirect-fulfillment controls. The subsequent approved
  diagnostic is completed in the section below. Source quotation alone does not
  prove entailment; broader reliability remains unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Assignment wording comparison under stable v53: 2026-10-11

**Preparation, local verification and bounded comparison COMPLETE; remedy NOT QUALIFIED.**
See the [diagnostic results and frozen design](../docs/benchmark_reports/assignment-wording-v53-2026-10-11.md).

- [x] Keep production prompt v53, graph v9, critic retry policy 17 and all runtime
  code unchanged. Verify the sealed v53 code hashes at current merge `f5a665b`.
- [x] Freeze a three-wording comparison: original conjunction, separate fact
  statements and an explicit clarification that the turning point imposes no
  order/causal relation while applicable canon still binds. Change only the
  synthetic turning-point fields and coherent artifact lineage, outside canon.
- [x] Prepare 24 probes at two paired seeds: three wordings crossed with the
  pull-before-touch, both-missing and valid action-decision drafts (18), plus
  explicit cause, order-only and applicable-canon controls (6). Ten requests match
  prior v53 requests exactly; fourteen are new. Preserve system messages, schemas,
  drafts, settings, budgets and all unrelated model context.
- [x] Replay all sixteen saved v53 responses with identical requests, results and
  audits. Verify all 108 sealed evidence files, prior report and source database.
  Pass 20 relevant offline regressions and `git diff --check`. The prior full v53
  build checks remain recorded evidence; no new full-suite run is claimed.
- [x] Obtain explicit approval bound to the frozen plan and complete 24 probes in
  25 calls, below the 48-call ceiling. Record 324,585 input / 30,306 output tokens
  and USD 0.05756430 at recorded October 8 rates, below the USD 0.31488 cap. Actual
  charges unknown. No writer/full-story calls or canonical changes.
- [x] Inspect all final native checks, generic complaints and complete repairs,
  plus the one rejected first response. All ten historical matched status pairs
  remain unchanged. Original and separate wordings both falsely block the valid
  pull-before-touch draft at both seeds; clarification produces one correct
  assignment judgment out of two. That review still returns revise for a minor
  craft issue; no pull-before-touch review cleanly passes. Overall 19/24 native
  pairs match the inspected obligations, with five false assignment blockers.
- [x] Retain correct two-blocker detection in all six both-missing cases, but record
  that all six consolidated repair sets add an unsupported temporal/causal demand.
  One clarified native touch repair is minimal while its generic restatement
  reintroduces a trigger. Decision repairs remain within scope; no unconditional
  completed-entry requirement recurs. All six action-decision baselines pass.
- [x] Inspect all six explicit cause/order/canon controls: correct statuses and
  appropriate relation-specific repairs. Both canon controls now cite and quote
  the real Bible clause and require first-onset causation, but neither supplies
  its artifact-version ID. Better source grounding does not qualify the remedy.
- [x] Record 23 first-valid and 24 final-valid reviews. The single retry fixes a
  reference to a nonexistent assignment finding, preserving met/met and minor
  independent classification. Its advice loses the Optional label; revise was
  already present. All 23 final comparison objects validate: 22 consolidate,
  one remains minor craft. The 23 mandatory repair targets include five false
  native blockers; none is an extra duplicate. Verify response replay, source
  hashes and local evidence closure. No new full-suite run is claimed.
- [x] Test the symmetric compliance/craft boundary inside the existing critic:
  established assigned facts and supported relationships suffice for met; a
  preferred dramatic mechanism must not turn them into unmet. Keep optional
  craft advice out of mandatory repairs and inspect verdict/routing as well as
  classification. Preserve genuine omissions, explicit relations, applicable
  canon and indirect fulfillment. The implementation and bounded comparison are
  completed below, with partial improvement and two order-control regressions;
  the remedy and broader acceptance remain unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfilled assignments, optional craft and verdicts v54: 2026-10-11

**Implementation, local verification and bounded comparison COMPLETE; remedy NOT QUALIFIED.**
See the [implementation and diagnostic results](../docs/benchmark_reports/compliance-craft-v54-2026-10-11.md).

- [x] Add a focused rule to the existing critic: complete assigned facts and
  supported conditions require met; a preferred dramatic mechanism cannot create
  a missing obligation. Optional craft preferences stay out of mandatory native
  and repeated repairs, retain explicit optional scope through retries, and
  alone do not justify revise/reject. Genuine craft defects remain eligible.
- [x] Preserve exact v50-v53 rules, schemas, validators, consolidation, writer
  contract and graph routing. Prompt v54 / graph v9 / critic retry policy 17.
  This is model guidance, not a semantic validator or automatic verdict rewrite.
- [x] Pass 32 focused regressions, including twelve new delivery/retry/durable
  routing cases. Optional pass avoids revision; genuine craft and unmet assignment
  defects retain repair targets. Optional revise still reaches the writer despite
  zero mandatory targets, so diagnostics must inspect the verdict too.
- [x] Pass Python lint/format, strict mypy across 194 files, frontend format/lint/
  type checks, eleven frontend tests and the production build. Update the existing
  instruction-size test to separately cap the new rule at 1,400 characters while
  preserving the old limit; its focused rerun passes.
- [x] Complete the full Python run: 965 pass and one instruction-size test fails
  before its addition-aware update. That corrected test passes separately (1/1),
  covering all 966 cases across the two runs with no unresolved failure. No second
  clean full-suite execution is claimed. No production code changed after the
  full run started. Final `git diff --check` passes.
- [x] Replay all 25 previous responses to identical canonical results/audits or
  validation failures. Preserve 159 sealed prior evidence files, the previous
  report and source database. Freeze 24 matched wording probes at the same two
  seeds; only the 1,393-character system addition and invocation metadata change.
- [x] Obtain approval bound to the frozen plan and complete 24 probes in 25 calls,
  below the 48-call ceiling. Record 329,887 input / 30,351 output tokens and
  USD 0.05832458 at recorded October 8 rates, below the USD 0.31488 cap. Actual
  charges unknown. No writer/full-story calls or canonical changes.
- [x] Inspect all native checks, full generic/consolidated advice, summaries,
  scores and verdicts, including the rejected first response. Five false blockers
  persist. One clarified met/met review now retains Optional minor advice and
  passes, but its summary still calls the turn partially met. All six complete
  baselines pass and all six missing-fact cases retain their two blockers; all six
  native touch repairs and complete repair sets exceed the assigned minimum.
  Decision repairs do not demand unconditional completed entry.
- [x] Record the explicit-order regression: both controls acknowledge the draft's
  reversed chronology yet mark met/met and pass. Correct native pairs decline
  from 19/24 to 17/24; 22 matched pairs remain unchanged. Explicit causation and
  applicable canon still block correctly at both seeds. Canon reviews quote the
  actual Bible clause but omit its artifact-version ID; consolidated advice
  restores causal onset more clearly than the native after-touch wording alone.
- [x] Verify 23 first-valid and 24 final-valid reviews. The one canon retry repairs
  incomplete evidence IDs, retaining native statuses and raw reject; existing
  mandatory-check materialization produces revise. Optional-label retry behavior
  is not exercised live. All 21 generic comparisons validate: twenty consolidate
  and one remains minor craft. The 21 mandatory targets include five false
  blockers. Two fewer targets than v53 reflect missed real order violations,
  not fewer false complaints. Replay saved responses and seal source/evidence
  hashes. Local simulated craft routing is not live craft or story qualification.
- [x] Hold implementation fixed and isolate temporal order from causal permission:
  compare order alone, order plus a no-causation clause, and separately stated
  relationship conditions, with valid/reversed order and unconstrained-facts
  controls. The approved diagnostic is completed in the next section. A paired
  wording effect is observed, with repair-scope and repeatability limits.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Temporal order and causal permission under stable v54: 2026-10-12

**Preparation, approved comparison and evidence review COMPLETE; remedy NOT QUALIFIED.**
See the [comparison results and frozen design](../docs/benchmark_reports/order-causation-v54-2026-10-12.md).

- [x] Keep production v54 / graph v9 / critic retry policy 17 and runtime sources
  unchanged at merge `f891bb7`. This is a controlled diagnostic, not a new prompt
  rule or semantic validator.
- [x] Prepare sixteen paired cases: four wordings (order alone, order plus the
  original causal waiver, separately stated relationship conditions, unconstrained
  facts) crossed with reversed order or touch before delayed pull, at two seeds.
  The new ordered draft changes only two paragraphs; the entry decision remains
  action-based. A full minute without pull rules out immediate onset, not every
  possible delayed causal link.
- [x] Add four controls: the delayed draft under an explicit immediate-cause plan
  and the saved both-missing draft under unconstrained facts, each at both seeds.
  Twenty total probes, six exact historical v54 requests and fourteen new requests.
  Reverse execution order at the second seed; do not rerun valid judgments.
- [x] Verify all 161 sealed prior evidence files, prior report and source database.
  Replay 25 v54 responses to identical requests, results/audits or validation
  failure. Verify paired payload isolation, coherent synthetic artifact lineage,
  unchanged system/settings/budgets and exclusion of expected labels from requests.
- [x] Pass sixteen existing critic/probe regressions, `git diff --check` and
  UTF-8/LF checks. Preserve the prior full v54 quality-gate record; no new full-suite
  or frontend build run is claimed for this diagnostic-only change.
- [x] Obtain explicit approval bound to the plan and complete all twenty probes
  in twenty calls with no retries. Record 265,530 input / 22,791 output tokens and
  USD 0.04629060 at recorded October 8 rates, below the USD 0.26240 ceiling. Actual
  charges unknown. No writer/full-story, production or canonical changes.
- [x] Inspect all forty native checks, twelve generic complaints, full repairs,
  summaries, scores and verdicts. At both seeds, order alone blocks reversed
  chronology, the original causal waiver causes a false pass, and separately
  stating order/causation restores the correct blocker. All eight ordered core
  cases pass. Both immediate-cause controls and both missing-fact controls block
  correctly. Overall 16/20 native pairs and all twenty outcome checks are correct;
  this differs from the previous matrix and is not an accuracy-improvement claim.
- [x] Record remaining scope failures: both order-only full repairs invent
  causation; both unconstrained reversed-draft reviews falsely require dramatic
  linkage; both missing-touch repairs add timing/trigger demands. One immediate-
  cause repair offers onset upon release, weakening its timing guarantee. Both
  separated-relationship repairs permit noncausal order. Twelve generic reports
  consolidate into twelve native targets (ten real obligations, two false
  blockers) without duplicates. Correct detection does not qualify all advice.
- [x] Compare all six exact historical requests: five native pairs/verdicts repeat,
  but the previous seed-19103 optional pass becomes a false blocker under unchanged
  requests/settings and recorded model digest. No retry explains this variation.
  Replay all twenty responses and verify/seal production, source and evidence
  hashes. The result supports a wording-associated scoping failure in this case,
  not a general internal-mechanism or reliability claim.
- [x] Test a compact replacement for the critic relationship guidance: distinguish
  required facts, temporal and causal relations; apply each permission only to
  its named relation and carry those limits into repairs. Preserve complete-fact
  met, applicable canon and indirect evidence. Reuse the frozen matrix before
  claiming improvement. The implementation and approved comparison are completed
  below, with partial improvement but remaining judgment and repair failures.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Separate facts, order and causation in critic guidance v55: 2026-10-12

**Implementation, local verification and approved comparison COMPLETE; remedy NOT QUALIFIED.**
See the [implementation and comparison results](../docs/benchmark_reports/relationship-scope-v55-2026-10-12.md).

- [x] Replace the existing source-basis and minimum-repair rules: assess facts,
  temporal order/immediacy and causation separately; scope each permission to
  its named relationship. Optional causation preserves required order; order
  alone does not require causation. Carry these distinctions into native and
  repeated repair advice without adding timing, triggers or completed action.
- [x] Preserve complete-fact met, applicable canon, actions/indirect narration
  and optional-versus-independent-craft guidance. The two rules shrink from
  1,446 to 1,345 characters including their separator. Prompt v55 / graph v9 /
  critic retry policy 17; no new output fields, validators or workflow changes.
- [x] Pass 41 focused regressions and all 966 Python tests; pass Ruff, strict
  mypy, frontend formatting/lint/type checks, all 11 frontend tests and build.
  Existing tests exercise instruction delivery, retries and durable routing;
  these local checks do not establish live semantic improvement.
- [x] Verify all 133 sealed prior evidence files, source report and source
  database. Replay twenty saved v54 responses to identical canonical results
  and audits. Verify that only the two rule constants and prompt version change
  in runtime code; all twenty frozen inputs, payloads, schemas, settings, budgets
  and seeds match the prior matrix apart from the system-guidance replacement.
- [x] Freeze twenty matched probes: sixteen core wording/draft cases and four
  immediate-cause/missing-fact controls, at seeds 19101/19103. Preserve the case
  order and existing one-retry bound. Maximum forty calls / USD 0.26240 at recorded
  October 8 rates; actual charges unknown. Zero model calls during preparation.
- [x] Obtain explicit approval and complete all twenty probes in twenty-one calls.
  Nineteen first reviews and all twenty final reviews validate. Record 279,680
  input / 26,322 output tokens and USD 0.049684 at recorded October 8 rates, below
  the USD 0.26240 ceiling; actual charges unknown. No writer/full-story calls or
  canonical writes. Production and frozen inputs stay fixed throughout execution.
- [x] Inspect all responses and replay all twenty-one results/failures and audits.
  Both causal-waiver false passes become correct blockers on first review.
  Native pairs improve from 16/20 to 18/20 first and 19/20 final; all twenty outcome
  checks remain correct. The extra gain follows a 631-character assessment's
  structural retry, which changes unmet/revise to met/pass. The other unconstrained
  case retains its false blocker. All eight ordered core cases and four controls
  preserve correct native checks; no general reliability claim follows.
- [x] Record repair failures separately: both order-only reviews invent a trigger;
  one separated-relationship repair adds immediacy; both missing-touch repairs
  add order. A minor tentative craft suggestion enters a blocking repair without
  explicit Optional scope. The remaining false blocker also creates an unnecessary
  repair. Both immediate-cause repairs now preserve onset at contact. Eleven
  generic reports consolidate into thirteen native targets (twelve real, one
  false), without duplicates; full advice and summaries remain unqualified.
- [x] Verify and seal frozen code, source database, prior evidence and current
  requests/results. Keep local full-suite/build evidence distinct from limited
  live semantic findings. Step 19 acceptance remains incomplete.
- [x] Keep v55 fact checks stable and compare each mandatory repair and
  linked restatement against the exact supported requirement it repairs. Preserve
  optional craft suggestions outside blockers; test saved-response/local cases
  before a bounded live comparison. Track the remaining false blocker and retry
  drift separately. The v56 instruction-only experiment completed but regressed
  to 17/20 correct native pairs versus v55's 19/20 final. Its candidate was rejected;
  the operator retained v55 on main. This completes the experiment, not the remedy.
  No writer, full-story or cross-provider qualification yet.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Inspectable assignment repair conditions v57: 2026-10-12

**Implementation, local verification and approved comparison COMPLETE; candidate NOT QUALIFIED.**
See [ADR 0034](../docs/adr/0034-traceable-assignment-repair-conditions.md) and the
[implementation and comparison results](../docs/benchmark_reports/repair-condition-sources-v57-2026-10-12.md).

- [x] Start from retained v55 at `d6834f0`, keeping its complete-fact, relationship,
  minimum-repair and optional-craft rules unchanged. Require condition records
  for every model-written native assignment repair and linked generic addition,
  including minor restatements. Preserve independent craft's existing route.
- [x] Validate exact repair-text coverage, current source membership, exact quotes
  and bounded structure. Resolve source references to immutable artifact versions
  and original paths despite context filtering. Retain redacted records in audit
  schema 5 and bounded failure evidence. Prompt v57 / graph v9 / critic retry
  policy 18; no new inference pass, retry allowance, writer behavior or migration.
- [x] Pass 32 new tests, all 998 Python tests, Ruff, strict mypy across 197 files,
  frontend formatting/lint/type checks, all 11 frontend tests and build. Explicitly
  port historical simulated fixtures; no production auto-annotation fallback.
  Demonstrate that a source-valid but unsupported repair remains structurally
  valid: traceability does not establish entailment or atomic decomposition.
- [x] Verify all 136 v55 and 133 v56 sealed evidence files and the source database.
  Replay all 41 saved responses locally. Explicit test-only annotations preserve
  forty prior canonical results, including semantic errors, and the known prior
  structural failure. Do not count simulated citations as model evidence.
- [x] Freeze twenty matched v55 cases at seeds 19101/19103. Inputs, settings,
  budgets and order match exactly; new requests differ only by condition guidance,
  source catalog and output schema. Maximum forty calls / USD 0.26240 at recorded
  October 8 rates, actual charges unknown. Zero model calls during preparation.
- [x] Obtain explicit permission and complete twenty probes in thirty calls:
  589,000 input / 37,691 output tokens, USD 0.0975364 at recorded October 8 rates,
  actual charges unknown. No valid-response reruns, writer/full-story calls or
  canonical writes. Replay all thirty unmodified responses and verify frozen
  code, database and source evidence.
- [x] Inspect every condition, cited source and separate advice. All forty first
  and last native check pairs match inspected facts, including rejected responses.
  Only ten no-repair reviews validate; all ten repair-bearing reviews exhaust
  retry because condition text differs from the separate recommendation. All 41
  citations resolve, but 24 native texts mismatch and two generic additions lack
  records. Four final raw reviews retain unsupported causal/order demands; one
  also gains completed-entry advice on retry. No nonempty condition review was
  accepted, so neither usable repair delivery nor semantic improvement is qualified.
- [x] Record structural failure separately from correct raw detection, inspect
  summaries/scores and stable check/verdict labels, and seal evidence. Keep main
  at v55. Canon and independent-craft source behavior remain local-test evidence.
- [ ] Next, test one authored source of mandatory assignment repair advice:
  render canonical recommendations from the structured conditions, covering native
  and linked generic routes and rejecting conflicting extra advice. Preserve v55
  obligation semantics and independent craft. Prove deterministic coverage locally
  before a bounded live comparison; source support still needs semantic testing.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Rendered assignment repair advice v58: 2026-10-13

**Implementation, local verification and approved comparison COMPLETE;
candidate NOT QUALIFIED.** See
[ADR 0035](../docs/adr/0035-rendered-assignment-repair-advice.md) and the
[implementation and test report](../docs/benchmark_reports/rendered-repair-advice-v58-2026-10-13.md).

- [x] Start from retained v55 production plus documentation at `1cd2d53` on
  `codex/critic-rendered-repair-advice`; leave main at v55. Preserve the meaning
  of met, relationship scope, optional craft and actions/indirect evidence.
- [x] Make conditions the sole model-authored assignment repair advice. Validate
  coverage and citations, require null native/linked advice fields, render exact
  joined conditions and reject competing text. Keep existing consolidation,
  writer targets and historical advice. Record rendered origin in audit schema 6.
  Prompt v58 / graph v9 / critic retry policy 19; no added inference or migration.
- [x] Pass 44 new tests, 101 affected regressions and all 1,010 Python tests.
  Ruff, strict mypy across 197 files, frontend format/lint/type checks, all eleven
  frontend tests and production build pass. Preserve the deliberate source-valid
  but semantically unsupported counterexample; tests do not establish entailment.
- [x] Verify 300 sealed v55/v57 files and both reports/database. Replay all thirty
  saved v57 responses: ten unchanged no-repair passes, twenty extra-advice
  rejections. Explicit null-only counterfactual copies yield 28 passes and two
  missing-record failures; these are not new model evidence or semantic approval.
- [x] Freeze twenty exactly matched cases, seeds, settings, budgets and order;
  maximum forty calls / USD 0.26240 at recorded October 8 rates. Zero model calls.
- [x] Record explicit operator approval bound to the final plan hash. Two launch
  attempts fail before execution due to automatic review timeout/capacity; after
  operator retry guidance, the third launch passes review. No check is bypassed.
- [x] Complete twenty probes in twenty-two calls: 428,184 input / 27,168 output
  tokens, USD 0.07081296 at recorded rates; actual charges unknown. Eighteen first
  reviews validate, including eight native repairs. All first/final native pairs
  match the twenty controls; both missing-facts controls exhaust their retry.
- [x] Inspect all 25 conditions/citations and accepted advice. All sources resolve;
  no extra mandatory causal/order/entry demands appear in the conditions. Rationale
  still uses unsupported causal language in four order-only cases. No linked
  generic repair is accepted live; that route remains unqualified.
- [x] Isolate the two first failures locally: copying native records into missing
  linked-issue records makes both explicit counterfactuals validate, while
  duplicating rendered advice. Originals remain unchanged and are not counted as
  successes. Replay all twenty-two raw responses, verify frozen evidence and seal
  the report. Keep main at v55; full-story/preference/cost acceptance stays open.
- [ ] Next, test one condition set per consolidated finding, with declared
  restatements reusing that authority. Keep additional conditions inspectable in
  the authoritative set and preserve independent craft; no silent repair fallback.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Shared assignment repair conditions v59: 2026-10-13

**Implementation, local verification, offline replay and approved comparison COMPLETE;
focused shared-condition contract PASSES this matrix; writer/broader qualification OPEN.** See
[ADR 0036](../docs/adr/0036-shared-consolidated-repair-conditions.md) and the
[implementation report](../docs/benchmark_reports/shared-repair-conditions-v59-2026-10-13.md).

- [x] Start from `8939848` on `codex/critic-shared-repair-conditions`, retaining
  main's v55 production. Recover the previous candidate's rendering and test
  infrastructure, then make each native finding own one condition set. Keep
  complete-fact fulfillment, actions/indirect evidence and independent craft.
- [x] Require linked generic advice to stay null and reuse the exact validated
  finding recommendation. Reject separate issue records/advice, absent owners
  and missing native coverage. Preserve repeated descriptions/evidence; append
  no repeated repair text. Extra conditions belong in the native source-cited set.
- [x] Resolve boundary/native aliases with the existing exact consolidation
  validators. Boundary-only restatements reuse application policy. Preserve
  historical repairs and retry classification. Audit schema 7 records owner refs
  and boundary policy; prompt 59 / graph 9 / critic retry 20. No new calls or migration.
- [x] Pass Ruff and strict mypy across 198 files, frontend checks, eleven tests
  and production build. Full Python run: 1,025 passed, one outdated boundary
  advice assertion failed. Correct that test-only expectation; all 86 affected
  v43/v58/v59 tests pass afterward. Sixteen new v59 cases and the adapted durable
  mock workflow cover shared repairs. No full-suite rerun after the test-only fix.
- [x] Verify 443 sealed prior files and the source database. Replay 22 unmodified
  v58 responses: eighteen first reviews keep identical results; both failed first
  reviews now produce two exact single-copy repairs; the two saved retries remain
  invalid for separate advice or incomplete independent-craft comparison.
- [x] Freeze twenty matched cases. Drafts, context, settings, budgets and seeds
  are identical; the only first-request difference from v58 is condition guidance.
  Maximum forty calls / USD 0.26240 at recorded October 8 rates; actual charges
  unknown. Preparation and offline replay make zero model calls.
- [x] Obtain explicit permission and complete twenty probes in 21 calls: nineteen
  first reviews and all twenty final reviews validate; all first/final native
  check pairs match the controls. One 601-character assessment passes after the
  existing bounded retry. Four generic repetitions share native sets; both
  missing-facts controls produce two blockers each. No duplicate repair text.
- [x] Inspect all 25 citations and conditions, twelve final native sets, computed
  writer targets and explanatory prose. Source identity resolves and no unassigned
  mandatory condition appears in rendered repairs. Causal language still occurs
  in explanations; atomic cause/timing and downstream writer behavior remain open.
- [x] Reconstruct and replay all requests/responses unchanged, verify frozen code
  and source database, and seal evidence. Usage: 407,609 input / 25,902 output
  tokens; USD 0.06742606 at recorded rates, actual charges unknown. No writer,
  full-story or canonical changes; main remains v55.
- [x] Complete the fixed-v59 writer repair test below with approved private
  payloads, order-only and missing-fact feedback, and required-causation controls.
  Existing facts and indirect decisions are preserved in the inspected cases;
  the test also identifies unresolved endpoint expansion in two repairs.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 writer repairs: 2026-10-14

**APPROVED EXPERIMENT COMPLETE; REPAIR DELIVERY WORKS ON THESE CASES;
ENDPOINT PRESERVATION OPEN.** See the
[experiment results](../docs/benchmark_reports/writer-repairs-v59-2026-10-14.md).

- [x] Start from merged v59 at `72bed6f` on `codex/writer-repair-v59`. Keep all
  production code and the meaning of met fixed; no new schema, instruction,
  routing, retry allowance or canonical story change.
- [x] Verify 142 sealed v59 files, its report and the frozen source database;
  replay all 21 original responses unchanged. Build standard writer/critic
  requests with identical original repair tests and version-bound evidence.
- [x] Pass 34 relevant probe, repair-acceptance and v59 tests. Exercise all six
  writer requests plus retry recovery/exhaustion with nine fake responses and
  zero model calls. Check diagnostic formatting and syntax. No application changes
  require another full suite or frontend build.
- [x] Freeze six writer/critic pairs: order-only, missing-touch/decision and
  explicit immediate causation, each at two seeds. Add two unchanged-defect
  controls and one valid indirect-decision control with both feet outside.
  Maximum 30 calls / USD 0.19680 at recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit permission and complete all fifteen probes in fifteen calls,
  without retries or extra requests. All six revisions validate and receive critic
  passes; eight original repairs are satisfied. All three control pairs match:
  unchanged defects remain, and a valid indirect decision outside passes.
- [x] Inspect all whole revisions, diffs and reviews. All first eight paragraphs
  and approach-to-threshold passages remain exact; four existing action endings
  and four existing pull paragraphs remain exact. No new mandatory causal or
  entry demand appears, but causal readings remain in explanatory prose.
- [x] Record the unresolved scope concern: both missing-decision writers complete
  entry, and both critics accept it despite the threshold exit state. One calls
  this the decision's logical completion. Distinguish optional writer expansion
  and permissive boundary interpretation from a mandatory entry requirement.
- [x] Reconstruct/replay all fifteen requests/responses unchanged; verify frozen
  code, database and historical evidence; seal results. Usage: 214,224 input /
  18,607 output tokens; USD 0.03743416 at recorded rates, actual charges unknown.
  No second prose revision, full-story calls, canonical or production changes.
- [x] Keep v59 fixed and compare a valid indirect decision outside with
  completed entry under the original threshold wording, explicit outside-at-end
  wording and authorized entry. Keep decision fulfillment separate from endpoint
  compliance before changing code. The completed comparison below supports a
  permissive interpretation of the original wording in these tested cases.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 endpoint wording comparison: 2026-10-14

**COMPLETED; EXPLICIT ENDPOINT WORDING CHANGES THE BOUNDARY JUDGMENT.** See the
[comparison report](../docs/benchmark_reports/endpoint-wording-v59-2026-10-14.md).

- [x] Start from `c6739976` on `codex/endpoint-wording-v59`; keep production v59,
  the meaning of met, retry policy and all canonical story artifacts unchanged.
- [x] Freeze both previous missing-decision writer revisions and variants changing
  only their final entry sentence to the previously accepted outside-action ending.
  Cross all four drafts with original threshold, explicit outside-at-end and
  optional-entry wording at two paired critic seeds: twenty-four probes.
- [x] Keep the Scene Plan and embedded Blueprint plan consistent, updating only
  exit state and derived lineage. Verify wording-normalized requests are otherwise
  identical, including compaction, original repair tests and next-scene reservation.
  Reproduce two historical live requests exactly at their original seeds.
- [x] Verify 299 sealed files, both reports and the database; reconstruct/replay
  fifteen previous requests/responses unchanged. Confirm locally that a boundary
  blocker can coexist with met decision and original repair checks. Pass 45
  relevant tests and diagnostic formatting/syntax checks before cloud generation.
- [x] Declare twenty boundary controls and leave four original-wording entry
  cells descriptive. Require met decision/turning-point and original repairs
  independently of any new endpoint defect. Maximum 48 calls / USD 0.31488 at
  recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit approval and run all 24 critic probes in 24 calls, with no
  structural retries. All twenty declared boundary controls match. Both entered
  drafts pass under original wording and optional entry, but require revision
  under explicit outside-at-end wording at both critic seeds. Treat the four
  original-wording entry cells as descriptive, not graded successes.
- [x] Inspect all judgments and advice: decisions, turning points and both original
  repairs remain met in 24/24; all twelve outside endings pass. Each explicit
  boundary violation produces one blocker, with no generic duplicates, reopened
  repairs or new causal/completion requirements. Raw/final verdicts agree 24/24.
  No authored condition sets were exercised in these responses.
- [x] Reconstruct/replay all requests and raw responses; verify frozen sources and
  seal evidence. Usage: 508,700 input / 34,452 output tokens; USD 0.08499880 at
  recorded rates, actual charges unknown. No writer, full-story or canonical changes.
- [x] Keep v59 fixed and test one writer/critic repair per explicit-boundary
  finding, checking outside position while preserving fulfilled facts and an
  indirect decision. Inspect prose and verdicts, with saved outside variants as
  controls. The completed experiment below supports localized boundary repair;
  preservation of an independently valid indirect expression remains open.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 outside-boundary writer repairs: 2026-10-14

**COMPLETED; FOUR LOCALIZED BOUNDARY REPAIRS; INDIRECT STYLE PRESERVATION OPEN.**
See the [repair report](../docs/benchmark_reports/outside-boundary-repairs-v59-2026-10-14.md).

- [x] Start from `7adb3907` on `codex/outside-boundary-repairs-v59`; keep production
  v59, the meaning of met and canonical artifacts unchanged.
- [x] Prepare four writer/critic pairs from the four saved explicit-boundary
  findings, retaining exact canonical feedback and all three original repair
  tests. Add four controls using the saved accepted outside-decision prose under
  the same repair history. Freeze dependent critic construction from valid writer
  output only; allow one prose revision per case.
- [x] Verify 456 sealed files, source reports, database and code hashes. Reconstruct
  and replay all 24 endpoint requests/responses unchanged. Verify pair contracts,
  standard compaction and separate missing-decision versus boundary repair IDs.
- [x] Pass seven mock writer calls covering retry recovery/exhaustion and eight
  local critic fixtures separating the new boundary repair from met decisions
  and earlier repairs. No model calls or semantic success claimed.
- [x] Pass 45 relevant regression tests outside the sandbox after interrupting
  a stalled first sandboxed run; no application changes. Pass diagnostic Ruff
  checks and freeze the plan, eight initial requests and dependent critic builder.
- [x] Obtain explicit cloud approval for twelve probes, maximum 24 calls /
  USD 0.15744 at recorded October 8 rates.
  Actual charges remain unknown.
- [x] Run twelve probes in thirteen calls: four writer revisions, four follow-up
  critics and four controls. All writers preserve every word before the original
  final sentence and repair the boundary; all eight final critics pass with both
  native checks and all three repairs met. Two control reviews accept indirect
  decisions; the other two retain an explicit decision sentence.
- [x] Retain the one failed critic response: a mistyped boundary repair ID is
  rejected, then corrected by the existing structural retry. First attempts:
  11/12 valid. Native statuses, boundary and verdict do not change on retry.
- [x] Inspect prose and record the limitation: all four new endings use explicit
  decision narration. The original action partly conveyed the decision and was
  itself the overrun, so this does not isolate preservation of an independently
  valid indirect expression. No new mandatory advice or duplicate findings.
- [x] Reconstruct/replay all thirteen requests/responses, verify source/code and
  database hashes and seal evidence. Usage: 223,055 input / 18,028 output tokens;
  USD 0.03843890 at recorded rates, actual charges unknown. Production stays v59.
- [x] Keep v59 fixed and test an already accepted indirect outside decision with
  a separate forbidden-entry sentence appended. Check whether the writer removes
  only the overrun while preserving the independent decision expression. Prepare
  and approve that new matrix; the subsequent experiment below completes it.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fixed-v59 indirect-decision preservation: 2026-10-14

**COMPLETED — BOUNDARY REPAIRED; DELETION-ONLY PRESERVATION 0/2.**
See the [preservation report](../docs/benchmark_reports/indirect-decision-preservation-v59-2026-10-14.md).

- [x] Start from `50fabff6` on `codex/indirect-decision-preservation-v59`, keeping
  production v59, the meaning of met and canonical artifacts unchanged.
- [x] Retain one previously accepted indirect outside decision verbatim and append
  a separate forbidden-entry paragraph. Freeze two seeds, each with an initial
  critic, deletion-only control, writer and post-repair critic. Keep all fresh
  canonical feedback unedited; skip dependents if the overrun is not detected.
- [x] Freeze the deletion-only primary measure and separate checks for indirect
  expression, fulfilled facts, unrelated prose, actual advice and critic verdicts.
  One prose revision per seed; no replacement cases or valid-response rerolls.
- [x] Verify 591 prior sealed files, reports, code and database; reconstruct and
  replay thirteen previous responses. Pass thirteen no-network mock calls and
  45 regression tests; diagnostic Ruff checks pass.
- [x] Freeze the plan, baseline, two initial requests and dependent construction.
  Maximum eight probes / sixteen calls / USD 0.10496 at recorded October 8 rates;
  actual charges remain unknown.
- [x] Obtain explicit approval for the new private payload set.
- [x] Run eight probes in eight calls, all valid on the first attempt; no skips.
  Both initial critics identify one boundary blocker while keeping both native
  checks and earlier repairs met. Neither asks for explicit decision narration.
- [x] Inspect both revisions: forbidden entry removed, first 4,021 characters
  preserved, including preparatory action, motivation and fulfilled facts. Both
  replace the accepted final sentence with more explicit entering intention.
  Exact deletion-only preservation succeeds 0/2; semantic repair succeeds 2/2.
- [x] Both deletion-only controls and both post-repair critics pass, with native
  checks and all three repairs met. No duplicate findings or additional mandatory
  conditions. The original indirect ending was acceptable under the same history.
- [x] Reconstruct/replay all eight requests/responses, inspect actual writer
  contracts, reverify hashes and seal evidence. Usage: 143,523 input / 11,215 output
  tokens; USD 0.02457922 at recorded rates, actual charges unknown.
- [x] Test a compact writer-only clarification to preserve already fulfilled
  expression when deletion alone fixes a separate defect. Include a genuinely
  missing-decision control; keep the critic and meaning of met unchanged. The
  current result demonstrates extra rewriting, not its isolated cause. The v60
  comparison below found no preservation improvement.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer preservation during minimal repair, v60: 2026-10-14

**EXPERIMENT COMPLETE — NO PRESERVATION IMPROVEMENT; NOT PROMOTED.**
See the [implementation report](../docs/benchmark_reports/writer-minimal-repair-v60-2026-10-14.md).

- [x] Start from `a01c3327` on `codex/writer-minimal-repair-v60`; main stays v59.
  Add only a 292-character writer clarification: when deletion suffices, preserve
  already fulfilled wording, including indirect expression; permit necessary repairs.
- [x] Advance shared prompt metadata to v60; keep graph v9, critic instructions,
  meaning of met, schemas, validation, compaction, budgets and retry policy unchanged.
- [x] Update three current-version test expectations and the bounded writer-length
  cap. Full suite initially passes 1,022 with four stale-expectation failures;
  all four affected modules subsequently pass 85 tests. Ruff and strict mypy pass.
- [x] Pass frontend formatting, lint, types, all 11 tests and the production build.
- [x] Verify 725 sealed files and source hashes; replay all eight previous responses.
  Confirm identical critic messages/schema/results and only the writer paragraph
  difference for the exact saved inputs, feedback and seeds.
- [x] Pass seventeen no-network mock calls for the twelve-stage matrix and bounded
  failures. Freeze two preservation pairs plus two missing-decision chains and
  unchanged controls. Maximum 24 calls / USD 0.15744 at recorded October 8 rates;
  actual charges unknown. No model calls made during preparation.
- [x] Obtain explicit approval for the frozen twelve-probe matrix.
- [x] Run all twelve probes in twelve calls: four writer and eight critic calls,
  all first-attempt valid, with no retries, skips or second prose revisions.
- [x] Inspect full prose and diffs. Deletion-only repairs remain **0/2**, matching
  v59: both remove forbidden entry but replace the accepted last sentence with an
  explicit decision. Both preserve the preceding 4,021 characters, including the
  preparatory actions, motivation and fulfilled touch/pull facts.
- [x] Both missing-decision repairs succeed outside; both initial reviews and both
  unchanged controls correctly reject indecision. All four post-reviews pass with
  native requirements and historical repairs met. Inspect four supported condition
  records and three generic restatements; consolidation retains one outcome blocker
  per negative review without adding a duplicate repair identity.
- [x] Reconstruct/replay every request/response, reverify the frozen sources and
  seal evidence. Usage: 194,332 input / 15,807 output tokens; USD 0.03352928 at the
  recorded rates. Actual charges remain unknown. Main stays v59; do not promote
  this candidate on these results. Step 19 remains IN PROGRESS.
- [x] Isolate whether the already satisfied historical missing-decision complaint
  in writer context causes the unnecessary restatement. Retain the current boundary
  and genuinely unmet obligations, and keep the critic and its review history fixed.
  This is a proposed diagnostic, not a production-history removal policy; the current
  experiment does not establish the cause. The fixed-v59 comparison below found
  no preservation improvement when this one complaint was omitted.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Satisfied decision history in writer context, fixed v59: 2026-10-14

**EXPERIMENT COMPLETE — NO PRESERVATION IMPROVEMENT; PRODUCTION V59 UNCHANGED.**
See the [diagnostic plan](../docs/benchmark_reports/writer-satisfied-history-v59-2026-10-14.md).

- [x] Start from `20280f0b` on `codex/writer-history-diagnostic-v59`. Keep all v59
  production code and both roles unchanged; do not restore the v60 writer paragraph.
- [x] Prepare paired full-history and one-item omission requests at seeds 19101/19103.
  Omit only the satisfied historical missing-decision test from the writer projection.
  Keep immutable artifacts, current boundary, other tests and assignment/canon intact.
- [x] Add two missing-decision writer controls using exact saved drafts/feedback.
  Their latest status is unmet, so the same omission procedure retains the test.
  Keep all history and tests in every post-revision critic request.
- [x] Verify 902 sealed files and unchanged v59 implementation hashes; replay eight
  saved responses. Check exact projection differences and identical paired critic
  requests for an identical candidate. Counterbalance writer condition order.
- [x] Pass nineteen no-network fixture calls including retry recovery, permanent
  failures and missing-decision rejection. Pass 45 focused regression tests, Ruff
  and strict mypy. Freeze the matrix at twelve probes / at most 24 calls and
  USD 0.15744 at recorded October 8 rates. Actual charges remain unknown.
- [x] Obtain explicit approval for this new private payload set. No model calls
  made during preparation.
- [x] Finish all twelve probes in twelve first-attempt-valid calls: six writer and
  six critic calls, with no retries, failures, skips or second prose revisions.
- [x] Compare fresh paired prose: deletion-only preservation is **0/2 with full
  history and 0/2 with omission**. All four remove entry but add or rewrite explicit
  commitment. One full-history output retains the entire accepted passage and adds
  a decision sentence; neither omitted-history output retains the whole ending.
- [x] Both missing-decision writers repair the outcome while remaining outside and
  preserving preceding paragraphs. All six full-history critics pass, with both
  native checks and all original repairs met, no overrun, new issues or conditions.
- [x] Inspect complete prose/diffs and advice, reconstruct/replay all requests and
  responses, reverify sources and seal evidence. Usage: 166,130 input / 14,648 output
  tokens; USD 0.02911740 at recorded rates, actual charges unknown. Keep v59 unchanged;
  this result does not justify filtering production history.
- [x] Test the current boundary recommendation's request to restore both outcome
  and exit state when only the outside endpoint is unmet. Compare advice confined
  to the boundary while preserving the met outcome; keep other history and critic
  fixed, and include a genuinely unmet outcome control. The comparison below finds
  no deletion-only improvement; it establishes no cause or production change.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer boundary-advice comparison, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — NO PRESERVATION IMPROVEMENT; V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/writer-boundary-advice-v59-2026-10-15.md).

- [x] Start from `e2fe1bb0` on `codex/writer-boundary-advice-v59`; keep both roles and
  all v59 production code fixed. Change only the current boundary advice prefix
  in the diagnostic writer projection; retain all claims, evidence and other advice.
- [x] Pair current and endpoint-only advice at seeds 19101/19103 using exact saved
  drafts and full feedback. Keep all original tests in every post-critic request.
- [x] Add two fresh revision-zero controls combining explicit indecision with
  involuntary crossing. Require the critic to detect both defects and expose boundary
  advice before dependent writer/post calls; preserve any native outcome repair.
- [x] Pass 23 no-network fixture calls, including separate/consolidated advice,
  retry recovery, detection/exposure gates and permanent failures. Pass 45 focused
  regressions, Ruff and strict mypy. Retain earlier fixture-assertion failures.
- [x] Freeze the fourteen-probe matrix and exact requests; verify 1,095 sealed files,
  prior reports, the source database and v59 hashes, and replay eight saved responses.
  Maximum 28 calls / USD 0.18368 at recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit approval and complete all fourteen probes in fourteen calls:
  six writers and eight critics, all first-attempt valid. No retries, failures, skips
  or second prose revisions.
- [x] Compare paired prose: deletion-only preservation is **0/2 with current advice
  and 0/2 with endpoint-only advice**. All four remove entry and add explicit decision
  wording. One current-advice result retains the whole accepted passage but adds a
  decision paragraph; neither endpoint-advice result retains the complete ending.
- [x] Both mixed controls detect and repair the missing decision and forbidden entry.
  Native advice survives separately from boundary advice; generic Plot/Agency
  criticism consolidates into the native finding. All six post-critics pass with
  both native checks and every original repair met, no overrun or new conditions.
- [x] Inspect prose and advice, reconstruct/replay every request and response, reverify
  sources and seal evidence. Usage: 205,142 input / 17,933 output tokens;
  USD 0.03589308 at recorded October 8 rates, actual charges unknown. Keep v59 fixed.
- [x] Test whether a compact, draft-version-bound record of the latest review's met
  requirements and cited current passages helps the writer preserve valid expression.
  Keep genuinely unmet outcomes repairable, retain the unchanged critic, and use the
  mixed missing-decision/entry control. The comparison below improves preservation
  in both paired cases; broader transfer and production integration remain unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer fulfilled-evidence comparison, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — POSITIVE PAIRED RESULT; V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/writer-fulfilled-evidence-v59-2026-10-15.md).

- [x] Start from `54410412` on `codex/writer-fulfilled-evidence-v59`; leave production,
  critic and main at v59. Add only one diagnostic writer field; keep ordinary boundary
  advice, all original tests, claims, immutable inputs and role instructions intact.
- [x] Pair current/evidence writer context on the saved overrun at seeds 19101/19103.
  Reuse actual latest reviews and bind met checks/excerpts to exact draft and assignment
  versions. Keep post-critic requests identical for an identical candidate.
- [x] Reuse two mixed missing-decision/involuntary-entry drafts and saved initial
  reviews. Certify only their turning point; leave the missing decision and boundary
  repair obligations intact. No fresh initial critic calls are needed.
- [x] Pass 19 no-network mock calls and reject 13 invalid-provenance cases. Cover
  retries, failure skips, unchanged negative controls, necessary repairs and hook
  restoration. Retain two corrected preparation failures; no production fixes.
- [x] Pass 45 focused regressions, Ruff and strict mypy. The sandboxed test attempt
  stalled during Windows asyncio setup; the same tests pass outside the sandbox.
- [x] Verify 1,374 prior sealed files, source reports/database and v59 hashes; replay
  four saved initial reviews and freeze all six writer requests. Twelve probes,
  at most 24 calls / USD 0.15744 at recorded October 8 rates, actual charges unknown.
- [x] Obtain explicit approval for the frozen matrix and record its plan hash.
- [x] Complete all twelve probes in twelve first-attempt-valid calls: six writers and
  six critics, with no retries, failures, skipped stages or second prose revisions.
- [x] Both evidence-condition writers restore the exact accepted 720-word prose by
  deleting only the forbidden entry. Current context achieves 0/2 and rewrites the
  decision in both cases. All preceding paragraphs and other draft fields survive.
- [x] Both mixed controls repair the genuinely missing decision and remove entry.
  All six post-critics pass with native/historical checks met and no overrun or new
  conditions. Evidence-condition critics independently accept the retained indirect
  decision without receiving the added writer packet.
- [x] Inspect prose/advice, reconstruct/replay every request and response, reverify
  sources and seal evidence. Usage: 168,044 input / 14,870 output tokens;
  USD 0.02947416 at recorded rates, actual charges unknown. Keep v59 unchanged.
- [ ] Test transfer to another scene with valid indirect fulfillment and an independent
  defect, plus a genuinely unmet-requirement control. Keep this diagnostic projection
  and critic fixed. Later qualification must cover met evidence that overlaps another
  defect before production integration; no further cloud run is authorized here.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer fulfilled-evidence transfer, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — WRITER TRANSFER NOT MEASURED; INITIAL GATES FAILED.**
See the [diagnostic report](../docs/benchmark_reports/writer-evidence-transfer-v59-2026-10-15.md).

- [x] Start from `cdcc5488` on `codex/writer-evidence-transfer-v59`; keep production,
  critic and main at v59. Reuse the exact previous evidence projection and policy.
- [x] Prepare OH-V01-002's saved indirect verification passage with a separate
  forbidden match sentence. Preserve the decision outcome and move the existing
  no-match requirement to the exit state in both synthetic plan views.
- [x] Include the earlier missing-date draft with identical verification actions and
  the same overrun. Certify only its met outcome; its missing turning point must repair.
- [x] Freeze six initial requests and an 18-probe dependent protocol at two seeds:
  baseline critics, primary current/evidence pairs and unmet-requirement controls.
  Require suitable current reviews; skip failed/misclassified chains without rerolls.
- [x] Pass 24 no-network mock calls, ten invalid-provenance checks and four scheduler
  failure checks. Preserve all original advice and keep critic packets unmodified.
- [x] Pass 45 focused regressions, repository Ruff/formatting and strict mypy for
  198 source files. Verify 1,569 prior sealed files, source reports/database and v59.
- [x] Freeze the plan with maximum 36 calls / USD 0.23616 at recorded October 8 rates;
  actual charges unknown.
- [x] Obtain explicit approval and execute the bounded protocol. Six critic calls
  validate on first attempts; no retries or failures. Both baselines pass, all four
  overrun cases detect the match, and both negative controls detect the missing date.
- [x] Record that all four overrun reviews mark the already fulfilled decision unmet
  because the endpoint was exceeded. This exists in raw responses; it is not a
  validator-induced status change. All twelve writer/post-critic stages are skipped.
- [x] Replay every sent request and response; inspect actual actions, date evidence,
  advice and raw/canonical verdicts. Preserve the secondary duplicate-outcome finding
  in one review. Reverify sources and seal evidence. Usage: 115,472 input / 8,364 output
  tokens; USD 0.01951168 at recorded rates, actual charges unknown.
- [ ] Test scoped native fulfillment versus boundary compliance, retaining the valid
  decision as met while the separate exit violation remains blocking. Preserve
  genuinely unmet-fact/decision detection. Keep production v59 and the evidence
  projection fixed; writer transfer and necessary-repair success remain unmeasured.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic fulfillment versus endpoint compliance, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — NO IMPROVEMENT; PRODUCTION V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/critic-fulfillment-scope-v59-2026-10-15.md).

- [x] Start from `8f097792` on `codex/critic-fulfillment-scope-v59`. Keep production
  prompts, schemas, validators, writer and main at v59.
- [x] Prepare one diagnostic critic system-span replacement that distinguishes each
  requirement's own complete fact from a separate exit violation. Preserve indirect
  evidence, mandatory conditions within the requirement itself, and all blockers.
- [x] Pair current/scoped guidance for the six exact prior baseline, overrun and
  missing-date cases, plus a genuinely missing-decision control at both seeds.
  Sixteen independent critics; no writer or canonical changes.
- [x] Pass 19 no-network mock calls and verify all eight pairs, including structural
  retries. Replay six historical responses unchanged; do not impose desired semantics
  in validation. Verify 1,732 sealed files, reports, source database and v59 hashes.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 source files.
- [x] Freeze sixteen requests and the protocol. Maximum 32 calls / USD 0.20992 at
  recorded October 8 rates; actual charges unknown.
- [x] Obtain explicit approval and complete sixteen probes in sixteen first-attempt-valid
  calls. No retries, failures, skipped probes, writer calls or canonical changes.
- [x] Record no primary improvement: 0/4 fulfilled decisions remain met with overrun
  in either arm. Both arms block all overruns, accept 2/2 baselines, and detect 2/2
  missing dates and 2/2 missing decisions. Current-arm disputed classifications reproduce.
- [x] Replay and inspect all requests, responses, evidence, conditions and raw/canonical
  verdicts. Record duplicate outcome/boundary complaints in four current and three
  scoped cases. Reverify sources and seal evidence. Usage: 303,296 input / 21,590 output
  tokens; USD 0.05109744 at recorded rates, actual charges unknown.
- [x] Keep production v59; do not promote the unsuccessful guidance clarification.
- [ ] Test exact-requirement binding in the diagnostic check: each unmet assessment
  must identify the failed clause of its own requirement with current-draft evidence.
  Keep endpoint blockers and both negative controls. Source validation establishes
  traceability only; semantic support and writer transfer remain unqualified.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic own-requirement failed clauses, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — PARTIAL IMPROVEMENT; PRODUCTION V59 UNCHANGED.**
See the [diagnostic report](../docs/benchmark_reports/critic-failed-clause-v59-2026-10-15.md).

- [x] Start from `d44605aa` on `codex/critic-failed-clause-v59`. Keep production
  prompts, schemas, validators, writer and main at v59.
- [x] Prepare a diagnostic-only response extension: each native check carries its
  exact assignment binding; unmet identifies its own failed clause and current-draft
  evidence. Keep the existing complete-fact meaning of met and separate endpoint blockers.
- [x] Validate source/text identity, quote membership and evidence references in an
  isolated adapter; strip only added fields before unchanged v59 materialization.
  Preserve classifications and advice even when source-valid claims lack support.
- [x] Freeze the same four drafts, both negative controls and two paired seeds under
  ordinary and diagnostic guidance. Sixteen critics, at most 32 calls / USD 0.20992
  at recorded October 8 rates; actual charges unknown.
- [x] Pass 20 no-network mock calls, 13 malformed-field rejection checks and sixteen
  historical replays. Verify all eight pairs and 1,932 prior sealed files.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 source files.
- [x] Obtain explicit approval and complete sixteen probes in seventeen calls,
  including one structural link retry. No rerolls, writer calls or canonical changes.
- [x] Replay all seventeen responses and inspect clauses, evidence, advice and
  verdicts. Record 3/4 fulfilled decisions preserved with separate blocking overrun
  versus 0/4 current; both arms detect both negative controls and accept baselines.
- [x] Record the remaining unsupported own-clause claim: the later match is treated
  as contradicting a prior decision, importing an ending restriction. Traceability
  succeeds but does not establish semantic support. Do not promote the candidate.
- [x] Record the retry's valid links and unchanged classifications, plus its shortened
  date advice omitting explicit realization. Full writer repair remains untested.
- [x] Record 332,418 input / 24,794 output tokens, USD 0.05645612 at recorded rates,
  actual charges unknown. Reverify sources and seal results; production stays v59.
- [ ] Hold the diagnostic fixed and compare an explicit event requirement with an
  explicit terminal condition, retaining both negative controls. No further cloud
  test is authorized by this completed run.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Required event versus terminal condition, fixed v59 diagnostic: 2026-10-15

**DIAGNOSTIC COMPLETE — CLASSIFICATION CONTRAST REPRODUCED; REPAIR QUALIFICATION OPEN.**
See the [diagnostic report](../docs/benchmark_reports/critic-event-terminal-v59-2026-10-15.md).

- [x] Start from `15aedd38` on `codex/critic-event-terminal-v59`. Keep production,
  writer and main at v59. Reuse the sealed failed-clause diagnostic implementation.
- [x] Change only synthetic outcome wording and derived provenance: decision during
  the scene versus decided-but-unverified state at its end. Keep the separate
  no-match exit state, every draft and both negative controls unchanged.
- [x] Prepare four drafts × two wordings × two paired seeds. Freeze sixteen requests
  and the protocol. Maximum 32 calls / USD 0.20992 at recorded October 8 rates;
  actual charges unknown. No writer, full-story or canonical changes.
- [x] Pass 20 no-network mock calls and verify all eight pairs. Replay seventeen
  prior response attempts; verify 2,155 sealed files and unchanged critic hashes.
  Confirm source-valid semantic errors still validate rather than forcing statuses.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 source files.
- [x] Obtain explicit approval and complete sixteen probes in eighteen calls,
  including two structural link retries. No rerolls, writer calls or canonical changes.
- [x] Replay all eighteen responses. Record the correct classification contrast in
  all four paired overruns, retained blockers, both negative controls and baselines.
  All twelve final failed-clause claims have supported sources and draft evidence.
- [x] Inspect advice and record limitations: terminal reviews do not positively
  certify the fulfilled decision; three of four final date recommendations omit
  explicit realization. One retry drops that instruction while repairing links.
  Complete prose repair remains untested; do not promote the diagnostic.
- [x] Record 363,194 input / 28,208 output tokens, USD 0.06213036 at recorded rates,
  actual charges unknown. Reverify fixed implementations and sources; seal results.
- [ ] Keep production v59 and the diagnostic fixed; resume a gated writer-evidence
  transfer test with explicit event scope and both negative controls. Check actual
  decision preservation, overrun removal and complete date-plus-realization repair.
  No additional cloud run is authorized by this completed experiment.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Gated writer evidence with explicit event scope, fixed v59: 2026-10-15

**DIAGNOSTIC COMPLETE — DELETION-ONLY PRESERVATION AND BOTH REPAIRS SUCCEEDED.**
See the [diagnostic report](../docs/benchmark_reports/writer-event-evidence-v59-2026-10-15.md).

- [x] Start from `47966236` on `codex/writer-event-evidence-v59`. Keep production
  v59, the sealed failed-clause critic diagnostic and writer evidence projection fixed.
- [x] Replay eight saved event reviews, ten historical response attempts, as gates;
  retain both missing-date and missing-decision controls and all actual advice.
- [x] Freeze eight writer requests: current/evidence preservation pairs and
  evidence-only negative controls at two seeds. Prepare dependent post-critic
  generation with complete repair history and no writer evidence packet.
- [x] Set a sixteen-probe / 32-call limit, USD 0.20992 at recorded October 8 rates;
  actual charges unknown. One prose revision per case; no full-story/canonical changes.
- [x] Pass twenty-four no-network mock calls, provenance and dependency checks;
  verify 2,398 sealed source files and unchanged implementation hashes.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 files.
- [x] Obtain explicit approval and complete sixteen probes in sixteen calls, with
  no retries or skipped stages. Freeze every dependent critic request before sending.
- [x] Replay all sixteen responses and inspect all eight revisions/diffs. Record
  deletion-only preservation in 2/2 evidence cases versus 0/2 current cases; both
  arms retain the original decision. All six input overruns are removed and all six
  existing indirect verification passages stay verbatim.
- [x] Confirm complete date-plus-realization repair in 2/2 and genuine missing-decision
  repair in 2/2. Record the narrower saved date advice without claiming it is safe.
- [x] Confirm eight post passes, sixteen native met checks and ten historical met
  repair checks, with supported prose evidence. Record the distinction between edit
  restraint and assignment fulfillment; no blind story-quality result.
- [x] Record 212,392 input / 19,190 output tokens, USD 0.03741088 at recorded rates,
  actual charges unknown. Reverify fixed implementations and seal evidence.
- [ ] Keep production and diagnostic fixed; test the existing preservation exception
  when a cited fulfilled passage itself contains a defect requiring an edit. Retain
  a genuinely unmet control. No additional cloud run is authorized by this completion.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Writer preservation exception, fixed v59 diagnostic: 2026-10-15

**DIAGNOSTIC COMPLETE — PRESERVATION EXCEPTION SUCCEEDED; MINIMAL EDITING NOT ESTABLISHED.**
See the [diagnostic report](../docs/benchmark_reports/writer-preservation-exception-v59-2026-10-15.md).

- [x] Start from `12f8663d` on `codex/writer-preservation-exception-v59`. Keep
  production v59, the failed-clause critic diagnostic and writer evidence projection fixed.
- [x] Put the action-based decision and forbidden match in one evidence excerpt.
  Prepare a matched clean baseline and unchanged genuinely unresolved-decision control.
- [x] Freeze six initial critics at two seeds. Gate main current/evidence writer
  pairs on accepted baseline, expected classifications and an actual shared citation.
  Retain all feedback; never sanitize or fabricate the cited passage.
- [x] Bound the matrix to eighteen probes / 36 calls, USD 0.23616 at recorded
  October 8 rates; actual charges unknown. One prose revision per case; no full-story
  or canonical changes. Freeze dependent requests before sending.
- [x] Pass twenty-seven no-network mock calls, provenance and dependency checks;
  replay sixteen historical responses and verify 2,651 sealed source files.
- [x] Pass 45 focused regressions, Ruff/formatting and strict mypy for 198 files.
- [x] Obtain explicit approval and complete eighteen probes in nineteen calls,
  including one structural retry for duplicate recommendation text. All gates pass;
  no writer retry, skipped pair or semantic reroll.
- [x] Replay all nineteen responses and inspect all six full revisions/diffs. Both
  writer arms repair the shared passage and retain the decision; neither is clause-only.
  Both evidence arms preserve the original ending; current arms add verification language.
- [x] Confirm both genuinely missing decisions are repaired, all six date realizations
  remain fulfilled and all six post reviews pass. Record twelve native met checks and
  six historical met checks with supported resulting prose.
- [x] Record the initial critics' overstatement equating a match with accepting the
  warning; the explicit exit prohibition independently supports the blocker. Do not
  generalize the successful exception to all critic reasoning or minimal editing.
- [x] Record 284,316 input / 21,980 output tokens, USD 0.04859624 at recorded rates,
  actual charges unknown. Reverify fixed implementations and seal evidence.
- [x] Examine the smallest production handoff for the tested fulfillment-evidence
  packet, including current draft/assignment provenance and available validated audit
  storage. Retain mandatory repairs and the necessary-edit exception; keep the critic
  diagnostic separate. See the examination below. No integration or additional cloud
  run is authorized by completion.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment evidence production handoff examination: 2026-10-15

**EXAMINATION COMPLETE; IMPLEMENTATION NOT STARTED.** See the
[proposed integration](../docs/handoffs/fulfillment-evidence-production-design-2026-10-15.md).

- [x] Trace the existing writer task, successful critic audit, creator/input lineage,
  request fingerprint, retry/replay and persistence paths at `fbd726c4`.
- [x] Identify an optional native-met packet requiring exact draft/plan/shared-canon
  validation, with every mandatory repair and the tested necessary-edit exception retained.
- [x] Specify persisted snapshot/digest binding before calls, including stable retries,
  source eligibility, whole-packet omission and an explicit integrity-error path.
- [x] Inspect twelve validated critic receipts (22 met and two unmet native checks),
  excluding one failed attempt. Reconstruct all six records in four saved writer
  packets exactly from their audits, assignment text and evidence catalogs.
- [x] Verify all 288 sealed experiment files and its report hash unchanged. Keep
  production v59, graph v9 and both diagnostic components fixed; make no model calls.
- [x] Define local provenance, isolation and durable SQLite tests, followed by a
  gated comparison using ordinary production critic semantics. Separate traceability
  from semantic qualification; do not promote the failed-clause diagnostic.
- [x] Implement and locally verify the small handoff slice, version its request
  identity and document the accepted implementation. Completed 2026-10-16 below.
- [ ] Qualify writer behavior with eligible ordinary critic reviews and genuinely
  unmet controls before promotion or any broader story-quality claim.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Durable writer fulfillment handoff implementation: 2026-10-16

**LOCAL IMPLEMENTATION AND VERIFICATION COMPLETE; MODEL QUALIFICATION PENDING.**
See [ADR 0037](../docs/adr/0037-durable-writer-fulfillment-handoff.md). This executes
the approved local implementation slice following the October 15 examination.

- [x] Define prompt v61 / graph v9 and policy 1, explicitly supporting ordinary
  prompt-59/61 schema-7 critics. Freeze the new version in run input and checkpoint
  state; keep existing v59 requests, retry identity and replay on their prior path.
- [x] Add a typed pure projection and exact SQLite creator/input reader. Validate
  current review/draft/plan/shared authority, both native checks and exact evidence;
  preserve the tested policy, necessary-edit exception and all mandatory feedback.
- [x] Persist included or omitted snapshots and digests before submission. Reuse
  pinned snapshots across retries/recovery; reject changed sources, corruption and
  duplicate concurrent starts without issuing another model call.
- [x] Test whole-packet omission at the inclusive 16,384-byte UTF-8 boundary and
  retain security errors instead of redacting exact quotes. Budgets are unchanged.
- [x] Pass the full Python unit/integration/workflow suite: **1,096 tests**. After
  adding the final stale-prepared-attempt guard, pass **five focused retry,
  cancellation, interruption and graph-limit checks** (66 deselected).
- [x] Pass repository Ruff lint/format and strict mypy on **201 source files**;
  compare the public OpenAPI schema unchanged and pass `pnpm build`. The handoff
  module contains 71 test cases, including exact dependency identities, failed
  critic retry selection, omission pinning, concurrent-start rejection, accepted
  prior-scene identity, UTF-8 cap boundaries and the v59 legacy request path.
- [x] Record the accepted decision in ADR 0037 and preserve the original design,
  historical experiment reports, canonical artifacts and budgets. No dependency,
  persisted table or public API schema change was needed.
- [ ] Qualify actual writer behavior using ordinary critics in a separately frozen,
  authorized comparison. Local fake-gateway checks establish no live quality result.

The failed-clause diagnostic, canonical stories and sealed experiments remain
unchanged. Independent craft findings can still require edits to fulfilled passages.
Later story-quality work requires blind human review and the accepted rubric;
preservation rate and smaller diffs are not quality scores. No live model calls.

Verification used the installed uv environment (`--no-sync --extra api`) and
workspace-local cache/test directories. Windows sandbox restrictions blocked
asyncio's loopback socket; the successful integration tests ran outside that
sandbox with fake gateways. The production build used the pinned pnpm toolchain.
Frontend source and generated API contracts are unchanged.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Ordinary-critic fulfillment comparison preparation: 2026-10-16

**PREPARATION COMPLETE; LIVE COMPARISON COMPLETED BELOW.** See the
[frozen comparison plan](../docs/benchmark_reports/production-fulfillment-v61-plan-2026-10-16.md).
This prepares step 5 following the locally verified durable handoff; it is not
a model qualification result.

- [x] Freeze prompt 61 / graph 9 / handoff policy 1 at `c1bacab638e91dadfd69016ac9226b4885e0f10f`.
  Keep ordinary critic semantics and the production fulfillment projection fixed;
  do not import the failed-clause diagnostic or change production code.
- [x] Freeze six cases across OH-V01-001/002 at seeds 19101/19103: two clean
  baselines, separate and embedded defects, missing decision, and missing future
  date plus realization. Preserve full corpus constraints and declare the fresh
  revision-zero context, corrected inherited case metadata and synthetic identities.
- [x] Freeze twelve complete initial requests, dependent request builders/gates,
  source hashes and implementation hashes. Paired writers differ only by the
  fulfillment field; retain every actual craft finding and mandatory repair.
- [x] Bound the matrix to 36 probes / 72 attempts, one structural retry per probe
  and one prose revision per arm. Reserve 1,728,000 input / 576,000 output tokens;
  USD 0.47232 is the estimate at recorded October 8 rates, not known billed cost.
  Require explicit plan-bound approval before any live calls.
- [x] Verify 483 sealed source files and their reports; pass 36 offline stage
  fixtures, four paired comparisons, twelve retry-request checks, failure gates
  and two craft-feedback checks. Verify all twelve saved requests reconstruct.
- [x] Pass 91 focused regressions, repository Ruff lint/format, strict mypy for
  201 files, and private-script formatting/syntax checks. Document decisions,
  isolated-probe limitations and later blind story-quality evaluation.
- [x] Obtain approval for plan SHA-256
  `03da1a013fc86a4a1a142d561d11fc001ab219ee252c55b64c72b4c0ed60bf18`;
  verify the recorded model digest and execute only its eligible bounded stages.
- [x] Inspect and replay every response, report eligibility coverage and writer
  outcomes separately, account for all attempts, and seal the resulting evidence.

Preparation made no live calls, canonical database writes or historical evidence edits.
The comparison measures isolated production request behavior; full durable workflow
qualification remains the separately proposed step 6. Preserving wording is not a
literary-quality acceptance gate. **Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Ordinary-critic fulfillment comparison results: 2026-10-16

**BOUNDED EXPERIMENT COMPLETE; FULL BEHAVIORAL QUALIFICATION NOT ACHIEVED.** See
the [results and inspection](../docs/benchmark_reports/production-fulfillment-v61-results-2026-10-16.md).

- [x] Record explicit approval for the frozen plan and verify the expected model
  digest. Keep prompt 61 / graph 9 / policy 1, cases, settings, ordinary critic
  semantics and production request builders unchanged.
- [x] Validate the execution ledger with 39 fake calls, including retry and permanent
  failure, replay without extra calls, call-73 rejection and unknown-outcome rejection.
  Save full requests and reserve each live attempt before dispatch.
- [x] Finish twelve initial probes in fifteen calls: eleven validated reviews, one
  terminal structural failure. Only one of four paired cases qualifies; both Elena
  embedded reviews mark the existing decision unmet, and seed-19103 Elara never
  validates. Skip all twelve dependent stages for those three pairs.
- [x] Execute the one eligible current/evidence pair and all four independently
  eligible unmet controls: six writers and six post-critics, all valid first attempt.
  Total: **24 finished probes / 27 calls**, within the 72-call ceiling.
- [x] Inspect all six full revisions. Current context restores the clean Elara prose
  exactly (1/1); evidence adds unnecessary explicit decision language (0/1 exact
  restoration), despite retaining all cited excerpts. All four unmet controls repair
  their missing fact, preserve fulfilled facts and avoid a handwriting match.
- [x] Record six post-passes, twelve native-met and six historical-met post checks.
  No independent craft finding or embedded-passage repair was exercised live.
  Do not treat critic pass, quote retention or smaller word count as prose quality.
- [x] Replay all 27 raw responses and validators, reconstruct every actual request,
  reconcile all ledger slots and skips, and reverify frozen implementation and
  483 sealed source files. Document and seal results without changing production.
- [x] Record **428,797 input / 30,845 output tokens**, USD **0.07236958** at recorded
  October 8 rates; actual charges remain unknown. No extra or replacement calls.
- [ ] Resolve the incomplete ordinary-critic eligibility and unsupported preservation
  benefit through separately scoped follow-up before claiming broader qualification.
- [ ] Full workflow canary: **NOT STARTED**, explicitly excluded by the user.

The experiment is complete even though its qualification criterion was not met.
There is no positive promotion or story-quality recommendation from one evaluable
pair. Keep the result fixed for later investigation and blind quality comparisons.
No new prompt tuning, canonical changes or story-quality campaign was started.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment failure diagnosis and next experiment proposal: 2026-10-16

**DIAGNOSIS COMPLETE; FOLLOW-UP SINCE PREPARED AND RUN (2026-10-17).** See the
[diagnosis and bounded plan](../docs/handoffs/fulfillment-failure-diagnosis-next-experiment-2026-10-16.md).

- [x] Separate invalid critic output routes and assessment length from the valid but
  incorrect attribution of a separate endpoint defect to an already fulfilled event.
  Trace the repeated invalid anchor and the earlier repair-condition validation error.
- [x] Inspect exact writer requests and full prose. Positive policy arrived intact;
  every cited excerpt survived, but the uncited ending gained explicit restatement.
  Identify overlapping outcome/boundary framing as a hypothesis, not a proven cause.
- [x] Compare the earlier successful trial's revision history, repair ledger and
  evidence selection. Record why it is not an identical replication, and retain the
  unsuccessful scope-clarification and endpoint-advice diagnostics as counterevidence.
- [x] Propose a fixed-contract follow-up: ten critic cases at two seeds, plus three
  current/evidence writer pairs and their post-critics using one fixed validated
  saved review. Total: **32 probes / proposed 64-call ceiling**. Keep writer coverage
  independent of new critic eligibility; include complete-outcome negative controls.
- [x] Prepare and verify the new cases, full requests, scoring sheet and budget locally;
  present the [frozen manifest and plan](../docs/benchmark_reports/fulfillment-contrasts-v61-plan-2026-10-17.md)
  before live execution. No unused allowance from the completed experiment is carried forward.
- [x] Run and inspect the separately approved follow-up; see the October 17 results
  below. The diagnosis itself made no live calls or prompt/schema/runtime changes.
  Preserve independent craft and necessary edits; full-prose assistant inspection
  remains separate from pending blind human quality review.
- [ ] Full workflow canary: **NOT STARTED**, still excluded by the user.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment contrasts and writer replication preparation: 2026-10-17

**PREPARED AND VERIFIED; SUBSEQUENT APPROVED EXECUTION COMPLETE.** See the
[frozen plan](../docs/benchmark_reports/fulfillment-contrasts-v61-plan-2026-10-17.md).

- [x] Freeze ten complete critic cases at seeds 19201/19203: clean, separate result,
  embedded result, missing decision and complete-outcome controls for both stories.
  Preserve full constraints and consistent immutable diagnostic artifact references.
- [x] Freeze six writer requests at seeds 19201/19203/19205 using the exact saved
  successful ordinary review. Each current/evidence pair differs only by the packet.
  New critic classifications cannot gate these writer trials.
- [x] Save **26 full static requests**, the six conditional post-review builders,
  structural retry rules, 32-probe order, scoring/prelabels and **64-call ceiling**.
  Hash the plan, cases, requests, scoring and 115 code/dependency files. Plan SHA-256:
  `9d01888c27a0aa45eaa126cf47824540591ce3867aa5324c44dbc48fb8371b9e`.
- [x] Validate 32 stage fixtures and 26 static retry requests. Complete the final
  **71-fake-call harness**, covering all three retry roles, permanent failures,
  writer independence, post skip, zero-call replay, call-65/third-attempt rejection,
  unknown/incomplete work, transport/overage/cancellation stops and approval guards.
  Retain 691 hashed fixture files and unscored anonymous full-prose pair exports.
- [x] Replay all 27 prior attempts; reverify sealed sources. Pass **91 relevant
  regressions**, repository Ruff/format and strict mypy for 201 source files;
  private harness lint/format checks pass. Production remains unchanged.
- [x] Publish the frozen plan and seal preparation evidence. **Zero live model calls
  or provider discovery calls**; human review remains pending. Preserve independent
  craft and necessary edits; no quality claim from quote retention or smaller diffs.
- [x] Obtain explicit approval bound to the frozen plan before live execution;
  retain the additional explicit prose/context transfer approval for Ollama Cloud.
- [x] Execute, inspect and report the bounded comparison without tuning mid-run;
  see the results below. The frozen preparation report remains unchanged.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Fulfillment contrasts and writer replication results: 2026-10-17

**BOUNDED EXPERIMENT COMPLETE; BROADER QUALIFICATION INCOMPLETE.** See the
[results and full-text inspection](../docs/benchmark_reports/fulfillment-contrasts-v61-results-2026-10-17.md).

- [x] Execute the exact approved plan with the recorded cloud model digest and
  unchanged prompt 61 / graph 9 / policy 1. Retain all requests and durable
  reservations; no semantic rerolls, extra revisions or replacement probes.
- [x] Finish all **32 probes in 35/64 calls**, with no skips: 23 initial critic
  attempts, six writers and six post-critics. Thirty probes validate; two embedded
  Elena reviews fail after their allowed structural retry. All writer/post probes
  validate first attempt, independent of the new initial critic results.
- [x] Inspect all raw failures and native/normalized findings. Initial validity is
  17/20 first attempt and 18/20 final; classification matches are **16/20**. All
  ten Elara cases match. Both separate Elena results misclassify the fulfilled
  decision; both embedded cases fail routing. The recovered separate review changes
  from raw met to valid-but-wrong unmet. Compound outcomes remain unmet in 4/4.
- [x] Record supported advice separately from statuses: **15/20 sound reviews** on
  conservative assistant inspection, with one additional over-specific comparison
  condition documented transparently. No independent craft finding appeared.
- [x] Inspect all complete revisions and diffs: all six repair entry and retain
  fulfilled facts. Current context adds explicit decision restatement in **3/3**;
  evidence in **0/3**. Record three narrow preservation wins, no ties/losses/mixed
  tradeoffs. The prior evidence-only regression does not recur under these seeds.
- [x] Retain the shared limitation: **6/6 rewrite an adequate ending**, 0/6 exactly
  restore the clean text. Six post-passes, twelve native-met and six historical-met
  checks establish factual repair, not literary quality or durable workflow success.
- [x] Export three anonymous full-prose pairs and originals, with a separate private
  key. Complete assistant inspection separately; **blind human review stays pending**.
- [x] Reconstruct all 35 dispatched requests and replay all 32 receipts, including
  failed attempts; reconcile ledger, schedule, usage, approved hashes and model
  identities. Reverify preparation and historical seals; seal live evidence and
  report. Private inspection scripts pass lint/format; no production code changes.
- [x] Record **586,904 input / 41,345 output tokens**, 176.48 active dispatch seconds
  and USD **0.09870456** at recorded October 8 rates; actual charges unknown.
- [ ] Resolve ordinary-critic routing and attribution through a separately scoped
  proposal before broader qualification; do not tune from these results implicitly.
- [ ] Complete blind quality review and live craft-in-met-passage qualification
  separately. Preserve necessary edits and independent craft; never lock fulfilled prose.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**, as explicitly requested.

The comparison is complete even though broader qualification is not. No prompt,
schema, validator, runtime, canonical artifact or historical evidence was changed.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Remaining critic routes and shared ending rewrites: diagnosis 2026-10-17

**DIAGNOSIS COMPLETE; SUBSEQUENT LOCAL PREPARATION RECORDED BELOW.** See the
[diagnosis and bounded proposal](../docs/handoffs/fulfillment-routing-ending-next-experiment-2026-10-17.md).

- [x] Reverify 337 sealed live files, 44 preparation/operator files, frozen code and
  predecessor seals. Replay all 32 receipts / 35 attempts offline with network and
  gateway construction blocked. Preserve completed results and scoring unchanged.
- [x] Trace wrong outcome attribution separately from invalid conditions, anchors
  and links. Confirm all three retry requests omit rejected response bodies and
  retained classifications; one retry gains structural validity while losing the
  correct met judgment. Do not salvage failed reviews or relax validation.
- [x] Inspect the writer's actual negative-feedback channel: boundary category,
  outcome-framed claim and advice coexist with met evidence. Record adjacency and
  prospective-step wording as alternative hypotheses, not proven causes. Retain
  previous unsuccessful reminder, history-omission and advice-prefix experiments.
- [x] Propose independent critic and writer comparisons: 24 critic probes with an
  explicit route index; eight writers and eight ordinary post-critics comparing
  original versus boundary-only feedback framing, with evidence held constant.
  Include a fixed ordinary-review source whose cited passage contains the defect.
  Total **40 primary probes / proposed 80-call ceiling**; no prior unused allowance.
- [x] Keep first/final semantic correctness and advice support separate from output
  validity. Preserve full-prose judgment, required edits, independent craft and
  pending blind human review; no quality or promotion claim from smaller diffs.
- [x] User authorized local preparation of both comparisons; freeze full cases,
  projections, requests, scoring, schedule and budget, verify the harness and
  present the frozen plan below. Plan-bound live approval remains separate.
- [ ] Execute only after that approval; no candidate prompt, request projection or
  live call was made by this diagnosis. Full workflow canary: **ON HOLD; NOT STARTED**.

Production remains prompt 61 / graph 9 / policy 1. Live craft-in-met-passage and
complete-story quality qualification remain separate unfinished work.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic routes and writer boundary framing: local freeze 2026-10-17

**PREPARATION COMPLETE; APPROVED EXECUTION RECORDED BELOW.** See the
[frozen plan](../docs/benchmark_reports/fulfillment-routing-framing-v61-plan-2026-10-17.md).

- [x] Freeze six complete critic cases, both fixed ordinary writer sources, exact
  artifact versions, raw source reviews/audits and positive packets. Replay all
  32 prior receipts / 35 attempts and both writer sources; verify predecessor seals.
- [x] Freeze 24 critic probes comparing ordinary C0 with the sole added route-index
  field C1; eight writers comparing ordinary W0 with three boundary-framing fields
  W1, evidence held constant; eight conditional ordinary post-critics. Seeds 19301
  and 19303, counterbalanced arm order, no gating of writers by new critic results.
- [x] Freeze 32 exact static requests, all dependent/retry builders, request-difference
  records, schedule and scoring. Plan SHA-256:
  `cf143f6a1ee077a9c8c24b426b90009805b1d9897a517cb2782afdcf7cc4eb37`.
  Private bundle: `data/diagnostics/fulfillment-routing-framing-v61-2026-10-17/`.
- [x] Freeze **40 primary probes / 80 maximum attempts**, one structural retry per
  probe, nontransferable **48 critic / 32 writer-plus-post** block ceilings and
  16-attempt writer/post stage ceilings. Reserve at most 1,920,000 input / 640,000
  output tokens and 72,000 active seconds; historical-only estimate USD 0.52480.
- [x] Verify 40 stage fixtures, 32 static retry requests, 32 paired differences,
  four identical-output post pairs, 26 rejected source/view variants and four
  craft transmission checks. Required edits inside cited prose remain permitted;
  mixed/native/craft repairs cannot be hidden by the boundary projector.
- [x] Pass the final 87-fake-dispatch harness across independent ledgers: structural
  recovery, failed critic and wrong judgment independence, failed writer/sole post
  skip, zero-call replay, ceilings, ordering, source/request/model/approval guards,
  unknown/incomplete outcomes, transport/overage/cancellation stops. Bind 1,002
  fixture files and 121 code files. These calls are mocks, not live allowance use.
- [x] Pass 91 focused regressions, repository Ruff lint/format and strict mypy
  (201 files), private-script Ruff lint/format and documentation checks. Record the
  Windows sandbox temp/socket limitation and successful offline verification.
- [x] Preserve distinct scoring for routing validity, semantic correctness, advice
  support, factual repair, avoidable edits and genuine craft tradeoffs. Full anonymous
  pair exports remain human-review inputs; exact deletion is not a quality gate.
- [x] Record new approval bound to this plan hash and **full unpublished fictional
  prose/context sent to Ollama Cloud through the local daemon**, the 80-call ceiling
  and canary exclusion before gateway construction, discovery or inference.
- [x] Execute once after approval, inspect every attempt and full revision, report
  failures and limitations, update tracking and seal live evidence as recorded below.
- [ ] Blind human preference, live independent craft in a met passage and full-story
  quality qualification remain pending. Full workflow canary: **ON HOLD; NOT STARTED**.

Preparation made **zero live model, discovery or external network calls**. No
production prompt/schema/validator/runtime or canonical artifact changed.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Critic routes and writer boundary framing: completed comparison 2026-10-17

**COMPARISON COMPLETE; NEITHER CANDIDATE MEETS THE FROZEN SIGNAL.** See the
[results and inspection decisions](../docs/benchmark_reports/fulfillment-routing-framing-v61-results-2026-10-17.md).

- [x] Complete all 40 planned probes with **42/80 calls**: 26 initial critic calls,
  eight writers and eight ordinary post-critics. Respect the nontransferable
  48/32 block limits and one structural retry; no skips, replacements, semantic
  rerolls, transport retries or additional revisions. All three model checks match.
- [x] Record C0 **12/12 first-valid**, C1 **10/12 first-valid** and **12/12 final-valid
  in both arms**. Final classifications match **8/12 per arm**. Both falsely mark
  Elena's separate/embedded decision unmet at both seeds; retain correct clean,
  genuinely missing, complete compound and Elara controls.
- [x] Inspect both C1 embedded failures: illegal duplicate outcome route at 19301,
  conditions owned by a met outcome at 19303. Both retries change correct raw met
  to valid-but-wrong unmet. Preserve failed outputs; no salvaged writer evidence.
- [x] Audit advice separately: compound repair conditions are supported, with two
  control next-scene overclaims and one candidate support-rationale caution retained.
  No independent craft issue was reported. Structural validity is not semantic success.
- [x] Inspect all eight complete revisions and diffs. All repair entry and retain
  fulfilled facts; all eight ordinary posts pass, with sixteen native-met and eight
  original-repair-met checks. All four embedded revisions edit the cited defective
  sentence successfully. Exact excerpts remain descriptive, not protected spans.
- [x] Record W1 **0 preservation wins / 3 losses / 1 tie / 0 mixed**. W0 makes exact
  deletion-only repairs for both separate cases; W1 also rewrites their adequate
  endings. Embedded 19301 adds a new resolve/waiting beat and broader edits in W1;
  embedded 19303 is a tie. Preserve the alternative mixed interpretation for 19301
  if humans prefer its suspense; it still gives zero wins. No literary-quality claim.
- [x] Record six ending edits beyond the minimum, zero clear new explicit decision
  assertions and one ambiguous resolve beat. Separate factual retention, avoidable
  changes, benign wording and potential craft tradeoffs; do not count words as quality.
- [x] Export four full anonymous pairs/originals and a private order key. Complete
  assistant inspection separately; blind human review remains pending.
- [x] Reconstruct all 42 requests and replay all 40 probes / 42 attempts offline;
  reconcile reservations, outcomes, hashes, schedule and usage. Reverify 121 frozen
  code files and source/preparation seals. Seal live evidence, report and tracker
  snapshot. Private inspection scripts and documentation checks pass.
- [x] Record **686,223 input / 51,178 output tokens**, **292.13 active seconds** and
  USD **0.11654242** at historical October 8 rates only; actual billed charges unknown.
- [ ] Resolve critic attribution and retry stability through a separately scoped
  next proposal before further tuning or live calls. Do not promote either candidate.
- [ ] Complete blind human preference and live independent craft-in-met-passage
  qualification separately. Full-story quality qualification remains unfinished.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, validators, canonical artifacts and
historical evidence remain unchanged. No new application test/build claim is made
for this live execution; the full replay verifies the unchanged frozen path.
**Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.**

### Route-index and boundary-framing diagnosis: next proposal 2026-10-17

**DIAGNOSIS COMPLETE; EXPERIMENT PROPOSED, NOT PREPARED OR RUN.** See the
[diagnosis and proposed comparisons](../docs/handoffs/fulfillment-routing-framing-diagnosis-next-experiment-2026-10-17.md).

- [x] Reverify 407 sealed live files, 52 preparation/operator files, 121 frozen code
  files and predecessor seals. Replay all 40 probes / 42 attempts to the sealed
  audit with network/gateway access blocked; inspect complete raw failures and prose.
- [x] Separate persistent outcome attribution errors from incompatible routes and
  retry drift. Both C1 retries legalize wrong unmet outcomes. Two explicitly manual
  routing fixtures validate with the original met/boundary judgments untouched;
  preserve them as counterfactuals, never model successes or writer sources.
- [x] Explain the narrower writer result: factual repair succeeds throughout;
  boundary framing adds static-ending rewrites and one ambiguous resolve/waiting
  beat. Record salience and edit granularity as hypotheses, retain the mixed-reading
  sensitivity, and avoid attributing a paired difference to the unchanged packet.
- [x] Propose ordinary critic versus adjudication-only diagnostic output, retaining
  complete obligation semantics and context. Do not credit a smaller schema as
  routing success, generate a production Critique, or omit craft from production.
- [x] Propose ordinary full-scene writer versus exact model-selected text edits,
  with original feedback and evidence fixed. Permit broad and whole-scene edits;
  reject stale, ambiguous or overlapping patches instead of silently fixing them.
- [x] Include a synthetic repetition control inside fulfilled evidence, with two
  ordinary source critics and conditional paired writers/posts. Freeze eligibility;
  source failure skips its dependent pair without fabricated reviews or rerolls.
- [x] Specify **50 primary probes / proposed 100-call ceiling**, with nontransferable
  48 critic / 32 fixed-source writer-post / 20 craft-control limits, one structural
  retry, new seeds 19401/19403 and no transferred allowance. No new calls authorized.
- [x] Keep preservation, factual repair, craft editing and human quality separate.
  Record the full-story rubric/baseline requirements and pending blind human review.
- [x] Verify the offline evidence helper with Ruff and documentation/link/whitespace
  checks; seal the diagnosis and tracker snapshot. No application test/build claim.
- [x] User authorized local preparation. Freeze and verify all contracts, complete
  cases, conditional builders, requests, scoring and budget; present the frozen plan
  recorded below. Plan-bound live approval remains separate.
- [ ] Execute only after that approval; broader qualification remains unfinished.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, canonical artifacts, validators and
historical evidence are unchanged. This diagnosis made **zero new inference,
discovery or external network calls**. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Adjudication, exact edits and craft control: local freeze 2026-10-17

**PREPARATION COMPLETE; approved execution is now complete below.** See the
[frozen plan](../docs/benchmark_reports/fulfillment-adjudication-edits-v61-plan-2026-10-17.md).

- [x] Preserve the six complete critic cases and both fixed ordinary writer sources,
  full drafts, source receipts, original feedback and fulfillment packets. Add one
  explicitly synthetic craft draft by duplicating the bracing sentence beside itself,
  with a new exact version and recorded parent lineage. Canonical stories are unchanged.
- [x] Freeze J0 ordinary review versus J1 native/boundary adjudication only; J1 remains
  ineligible as a production Critique or writer source. Preserve complete obligation
  semantics, full context and current evidence identities; do not compare the smaller
  schema's validity as if it qualified full critic routing or craft assessment.
- [x] Freeze E0 ordinary full-scene writing versus E1 exact, model-selected edits.
  Verify base version/hash, occurrence selectors, Unicode and atomic application;
  reject stale/ambiguous/overlapping/out-of-order edits. Permit changes anywhere and
  whole-scene replacement; no protected passages, diff quota or automatic prose fix.
- [x] Freeze two ordinary craft-source critics and conditional paired writers/posts.
  Require supported native/boundary judgments, one independent actionable repetition
  finding, two ordinary tests and positive evidence covering both repeated ranges.
  Require source/plan-bound operator semantic inspection before dependent dispatch;
  ineligibility skips its pair without replacement, reroll or manufactured evidence.
- [x] Freeze **50 scheduled primary probes / 100 maximum attempts**, seeds 19401/19403,
  counterbalanced arms, one structural retry and nontransferable **48/32/20** block
  limits. Reserve at most 2,400,000 input / 800,000 output tokens and 90,000 active
  seconds; historical-only estimate USD 0.65600, actual billed charges unknown.
- [x] Freeze **34 exact initial requests**, conditional builders, 36 paired-difference
  records, scoring and schedule. Bind 128 code/dependency hashes and 1,287 fixture
  files. Plan SHA-256:
  `765fd0499eb2ddb87f97e32cdfcb65b338b544c9be2e452f34bc16e4da0368a2`.
  Private bundle: `data/diagnostics/fulfillment-adjudication-edits-v61-2026-10-17/`.
- [x] Pass 50 stage fixtures, 50 retry builders, six post-equivalence checks and 37
  negative contract/source checks. Verify both-copy evidence coverage so deleting an
  uncited duplicate cannot falsely qualify the craft-in-met-passage control.
- [x] Pass the actual operator harness with 100 fake dispatches across independent
  ledgers: 52 valid-matrix, 44 fault-matrix and four terminal-failure calls. Verify
  budget/order/source/request/model/approval guards, pending and failed craft gates,
  skips, unknown outcomes, cancellation, failed transport/usage and zero-call replay.
- [x] Replay all 40 predecessor probes / 42 attempts, both fixed sources and all 96
  completed fixture attempts under final validators. Reconcile complete exports:
  six valid-matrix and three fault-matrix anonymous pairs; human review stays pending.
- [x] Pass **75 focused regressions**, repository Ruff lint/format and strict mypy
  (201 files), seven private-script Ruff lint/format checks and documentation checks.
  Record Windows sandbox fixture/event-loop limitations and successful mocked checks.
- [x] Keep factual repair, preservation, craft editing and human literary preference
  separate. Preserve the accepted rubric, hard gates and future full-story/baseline
  qualification; no production promotion or added mandatory human story checkpoint.
- [x] Receive explicit approval on 2026-10-17 bound to this exact plan, 100-call
  ceiling, full unpublished prose/context sent to Ollama Cloud through the local
  daemon, and canary exclusion before gateway construction or model discovery.
- [x] Execute once after approval; inspect all attempts/full prose, reconcile usage,
  export blind pairs and document failures without tuning mid-run. Results below.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Preparation made **zero live model, discovery or external network calls**. Production
prompt 61 / graph 9 / policy 1, validators, runtime, canonical artifacts and historical
evidence remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Adjudication, exact edits and craft control: live results 2026-10-17

**BOUNDED RUN COMPLETE: 45/100 calls.** See the
[results and decisions](../docs/benchmark_reports/fulfillment-adjudication-edits-v61-results-2026-10-17.md).

- [x] Run all 24 critic probes in 27 attempts, eight fixed writers and eight ordinary
  post-reviews in 16 attempts, and both ordinary craft-source critics in two attempts.
  Account for all 50 slots: 42 completed probes plus eight dependent craft skips.
  No semantic rerolls, replacement cases, extra revisions or transport retries.
- [x] Confirm the frozen model digest at preflight and every phase. Match all 34
  static requests; save every actual request and reservation before dispatch. Replay
  all 45 attempts, including five invalid responses and two terminally invalid probes;
  reconcile all requests, response hashes, usage, outcomes, gates and skips offline.
- [x] Record J1's **12/12 valid supported shared judgments**, versus J0's **8/12**.
  J0 first/final validity is 9/12 and 10/12; both separate-match outcomes are falsely
  unmet and both embedded reviews remain invalid. J1 preserves clean, missing and
  compound controls. It meets the narrow diagnostic criterion, remains ineligible as
  a production Critique/writer source, and does not qualify craft, advice or routing.
- [x] Inspect all three ordinary structural retries: one compound review recovers;
  both embedded reviews fail terminally. Correct raw embedded judgments are not
  salvaged. This batch does not reproduce the earlier met-to-unmet retry drift.
  Record the separate-case advice overrestriction and next-scene acceptance overclaims.
- [x] Confirm **8/8 first-attempt factual writer repairs and 8/8 ordinary passing
  posts**, with four atomic E1 patches. Preserve complete prose/diffs. All revisions
  leave prose before the final main paragraph unchanged, but seven rewrite the ending
  beyond removing entry. E0 restores the clean scene once; E1 never does.
- [x] Score E1 preservation as **0 wins, 2 losses, 2 mixed**. Treating the smaller
  embedded loss as benign gives 0 wins, 1 loss, 1 tie, 2 mixed; the criterion still
  fails. Distinguish bodily embellishment, repeated bracing, new wait/commitment,
  benign wording and craft tradeoffs. These are operator judgments, not human scores.
- [x] Record **0/2 qualified craft sources**: both critics miss the adjacent duplicate,
  report only the boundary issue and score prose quality 5/5. Both also cite only one
  of the two repeated ranges as positive evidence. Skip four craft writers and four
  posts without replacements. Craft editing inside fulfilled evidence is **UNTESTED**.
- [x] Reconcile **696,412 input / 45,716 output tokens / 224.15 active seconds**;
  historical October 8 rate estimate **USD 0.11578408**, actual billed charges unknown.
  Respect the nontransferable block ceilings (27/48, 16/32, 2/20). Unused allowance
  does not authorize additional calls.
- [x] Save the sealed live bundle at
  `data/diagnostics/fulfillment-adjudication-edits-v61-2026-10-17-live/`, including
  all raw attempts, replay audit, operator assessment, complete prose/diffs and four
  anonymous primary pairs from six scheduled slots. Bind the unchanged preparation,
  new approval, dependency hashes, report and tracker snapshot in the final closure.
  New inspection scripts pass Ruff lint/format; documentation links/whitespace and
  evidence checks pass. The preparation's 75 regressions remain evidence against
  unchanged code, not a new test run. No production/client code changed.
- [ ] Human preference review remains **PENDING**; the exported review sheet is empty.
- [ ] Neither intervention is promoted. Future work requires a new bounded plan;
  full-story qualification still requires the accepted weighted rubric/hard gates,
  full intended Cloud corpus and comparable single-model baseline.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / fulfillment policy 1, validators, runtime, canonical
artifacts and historical evidence remain unchanged. **Step 19 IN PROGRESS; Step 20
NOT STARTED.**

### Exact-edit selection and missed craft: diagnosis 2026-10-17

**DIAGNOSIS COMPLETE; NEXT EXPERIMENT PROPOSED, NOT PREPARED OR RUN.** See the
[diagnosis and proposed 80-call comparison](../docs/handoffs/fulfillment-edit-selection-craft-diagnosis-next-experiment-2026-10-17.md).

- [x] Record the user's retention decisions: J1 remains promising diagnostic evidence;
  E1 remains mechanically successful but unqualified for preservation. Neither is
  promoted or given production authority.
- [x] Reverify 443 sealed live files, 58 preparation/operator files, 128 dependency
  hashes and predecessor seals; replay all 42 probes / 45 attempts offline. Preserve
  the prior reports, scoring and empty human-review sheet. Network connections and
  gateway construction are blocked during diagnosis.
- [x] Locate E1's failure in the model's edit choices: both separate-entry cases
  contain an unnecessary edit wholly before the defect. All four minimal-patch
  counterfactuals validate and restore clean prose. These operator-authored fixtures
  are not model results, writer sources, canonical edits or literary preferences.
- [x] Verify that both critics received all scene wording, including two distinct
  duplicate handles, in a 52-entry sentence catalog. The continuous prose field and
  paragraph layout are absent from actual messages. No text loss or output truncation
  explains the miss; the raw reviews already omit independent craft and score prose 5/5.
- [x] Verify that the ordinary schema retains an independent duplication issue on
  response copies without changing native checks. Distinguish model omission from
  application filtering, presentation effects and unproven assignment/reporting load.
  Critics receive no writer fulfillment packet.
- [x] Identify additional craft-control limitations: both-copy positive coverage is
  an instrumentation requirement, and ordinary projection creates a second mandatory
  test for major craft on revise but not minor craft. Both severities remain normalized
  issues. Do not raise severity or manufacture sources to force control eligibility.
- [x] Propose comparison A: six complete cases (base, accidental duplicate, functional
  recurrence, each with/without entry overrun), two seeds, ordinary catalog-only versus
  exact continuous prose plus the unchanged catalog. Keep system instructions, output
  schema and critic settings fixed: 24 primary probes / maximum 48 attempts.
- [x] Propose comparison B: unchanged E1 requests and the two fixed ordinary writer
  sources at temperatures 0.85 versus 0.2, two seeds, with ordinary unchanged posts:
  eight writers plus eight posts / maximum 32 attempts. This is a sampling diagnosis,
  not a low-temperature drafting policy or craft-editing qualification.
- [x] Keep the proposed ceiling at **80 calls / 40 primary probes**, nontransferable
  48/32 blocks and one structural retry; no semantic rerolls or replacements. Preserve
  full-prose scoring, functional-repetition specificity and blind human review. No
  craft writer control is claimed this round; useful edits inside fulfilled passages
  remain an explicit later qualification requirement with a separately frozen design.
- [x] Save local diagnosis and labeled counterfactual evidence under
  `data/diagnostics/fulfillment-edit-selection-craft-diagnosis-2026-10-17/`; verify
  helper lint/format, documentation links, whitespace and source seals.
- [x] Prepare and freeze the proposed cases, requests, scoring and budget after
  authorization; see the preparation record below for the sealed plan. Approved
  bounded execution is recorded below.
- [ ] Human preference, full-story quality and production qualification remain open.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

This diagnosis made **zero live model, discovery or external network calls** and
created no next-experiment prompt, request bundle or live plan. Production prompt 61 /
graph 9 / policy 1, validators, runtime, canon and historical evidence remain unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Critic presentation and E1 temperature: frozen preparation 2026-10-17

**PREPARATION COMPLETE; approved execution is now complete below.** See the
[frozen 80-call plan](../docs/benchmark_reports/fulfillment-presentation-temperature-v61-plan-2026-10-17.md).

- [x] Freeze six full-scene cases with distinct immutable draft versions: base,
  accidental adjacent duplication and functional recurrence, each with/without the
  entry overrun. Freeze construction rationales separately from model messages;
  legitimate criticism of the functional recurrence remains possible.
- [x] Freeze comparison A: ordinary P0 catalog versus P1 exact continuous prose
  alongside the unchanged catalog. Same ordinary instructions, schemas, evidence
  handles and settings; 24 primary probes / maximum 48 calls.
- [x] Freeze comparison B: unchanged E1 exact-edit instructions, two historical
  ordinary sources, full context, fulfillment packets and repair tests, at writer
  temperatures 0.85 versus 0.2. Eight writers plus eight ordinary P0 posts / maximum
  32 calls. No A result selects or gates the fixed B sources.
- [x] Freeze seeds 19501/19503, reverse arm order at the second seed, top-p 0.95,
  thinking disabled, critic temperature 0.2, and the nontransferable **80-call**
  ceiling. Reserve 24,000 input / 8,000 output tokens / 900 seconds per attempt;
  one structural retry, no semantic/transport rerolls or replacement cases.
- [x] Save 32 exact static requests and frozen dependent builders for eight posts
  and structural retries. Verify 32 paired attempt differences, all input lineage,
  exact prose inclusion, unchanged E1 instructions and identical ordinary posts for
  identical materialized prose. No context trimming. Largest static diagnostic
  token estimate 17,282; exact provider tokenization remains unknown until execution.
- [x] Freeze separate detection, native/boundary, advice-support, preservation and
  craft-tradeoff scoring; keep invalid results in scheduled denominators. Both minor
  and major independent craft findings can count as detection. Freeze pending
  assessment templates and four anonymous full-prose human-review pairs/export rules.
- [x] Verify all 40 scheduled slots through fake providers: 43 attempts with selected
  retries, 41 in the fault matrix and three terminal-error fixtures. Global, block,
  stage, token and time limits reject over-budget dispatch. A failed writer skips
  only its own post; critic failures do not block B. Completed replay adds zero calls.
- [x] Replay all 84 completed fixture attempts; reject request/response corruption,
  source mutation and six approval mismatches; verify 16 minor/major issue fixtures
  and complete/fault anonymous exports. Reverify predecessor seals and current source
  dependencies. Real gateway construction and external connections are blocked in
  offline checks.
- [x] Pass all 75 focused fulfillment/probe tests, repository Ruff/format and strict
  mypy checks across 201 files, and lint/format for six private helpers. No client or
  production changes require frontend tests/build. Save the plan, evidence hashes,
  verification, public report and tracker snapshot in the preparation closure.
- [x] Receive explicit approval for the frozen full-prose/context payload,
  Cloud-via-local-daemon destination and 80-call budget before model discovery or
  inference. Execute the frozen comparisons once; results are recorded below.
- [ ] Human preference, useful craft edits inside fulfilled passages, broader
  story-quality evaluation and production qualification remain open. No craft writer
  control is claimed in this round.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Private evidence: `data/diagnostics/fulfillment-presentation-temperature-v61-2026-10-17/`.
Preparation made **zero live model or discovery calls**. J1 remains promising diagnostic
evidence; E1 remains mechanically successful but unqualified for preservation.
Production prompt 61 / graph 9 / policy 1, canon and historical evidence are unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED.**

### Critic presentation and E1 temperature: live results 2026-10-17

**BOUNDED RUN COMPLETE: 43/80 calls; neither frozen success criterion met.** See the
[results and decisions](../docs/benchmark_reports/fulfillment-presentation-temperature-v61-results-2026-10-17.md).

- [x] Complete all 40 scheduled probes: 24 initial critics in 27 calls, eight writers
  and eight ordinary posts in 16 calls. Final validity is 38/40. Three structural
  retries yield one recovery and two terminal failures; five attempts are invalid.
  No skips, semantic rerolls, transport retries, replacement sources or extra revisions.
- [x] Match the frozen model digest at preflight and both phases, verify all 32 static
  requests and dependent builders, and reconcile every reservation, response, receipt,
  outcome and probe through offline replay. Preserve invalid results in denominators.
- [x] Record P1's improved raw duplication detection **4/4 versus P0 0/4**, but only
  **2/4 valid supported findings**. Both P1 duplicate-plus-overrun reviews remain
  invalid after retry. Native/boundary judgments are supported in every raw review;
  valid qualified tuples are P0 12/12 and P1 10/12. Neither arm makes an unsupported
  repetition-removal demand on its eight base/functional-recurrence controls.
- [x] Inspect every failed attempt: model-written boundary repair references and
  recommendation reuse cause the observed failures. Record empty craft-comparison
  references as an additional visible omission, without inventing a later validation
  result. Keep correct raw observations separate from usable production reviews.
- [x] Confirm all eight E1 patches validate immediately, repair the boundary and
  retain fulfilled facts; all eight ordinary posts pass immediately. Inspect complete
  prose, selected edits and diffs: all four separate-entry writers edit before the
  defect, and all four embedded writers add the same threshold image.
- [x] Score T1 temperature 0.2 relative to T0 0.85 as **0 wins, 1 loss, 2 ties, 1
  mixed**. Sensitivity with debatable additions neutral gives 0 wins, 1 loss, 3 ties.
  No embedded pair wins; one pair has byte-identical prose. The clear loss deletes
  compatible first-step preparation. These are operator judgments; human preference
  remains pending. Maximum post-review craft scores do not qualify literary quality.
- [x] Reconcile **765,309 input / 44,131 output tokens / 219.15 active seconds**;
  historical October 8 rate estimate **USD 0.12479566**, actual billed charges unknown.
  Respect nontransferable block ceilings (27/48 and 16/32) and every stage/per-attempt
  limit. The 37 unused calls authorize no additional calls.
- [x] Seal the live evidence at
  `data/diagnostics/fulfillment-presentation-temperature-v61-2026-10-17-live/`,
  including replay audit, per-axis assessment, full prose/diffs, four anonymous human
  pairs, final verification and tracker snapshot. Bind the unchanged preparation,
  approval, 134 dependencies and public report. Pass private helper Ruff lint/format,
  documentation links, UTF-8/LF, whitespace and evidence checks. Preparation's 75
  regressions and mypy checks are prior evidence against unchanged production code.
- [x] Retain J1 as promising diagnostic evidence and E1 as mechanically successful
  but unqualified for preservation. Retain P1's noticing improvement as diagnostic
  evidence only; neither comparison qualifies promotion. No production prompt change.
- [ ] Human preference review: **PENDING**; four anonymous pairs exported, sheet empty.
- [ ] Useful craft edits inside fulfilled passages, full-story quality and production
  qualification remain open. Keep the accepted rubric/hard gates, full intended Cloud
  corpus and comparable single-model baseline; no craft writer control is claimed here.
- [ ] Further experiments require a new bounded design; none prepared in this results task.
- [ ] Full workflow canary: **ON HOLD; NOT STARTED**.

Production prompt 61 / graph 9 / policy 1, validators, runtime, canonical artifacts
and historical evidence remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**

20. [ ] **Tune prompts and graph routing** based on blind human preference—not isolated attractive examples.

21. [ ] **Package the stable system with Tauri** and test crash/restart, offline, missing-model, invalid-key, provider-timeout, and low-disk-space behavior.

22. [ ] **Consider broader formats and hosted features only after the core is proven:** songs, poems, video scripts, collaboration, or hosted accounts.
