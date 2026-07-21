# Open Hollywood rewrite report

This document is the consolidated archive of the initial rewrite analysis. The focused documents in this directory and accepted ADRs contain the canonical, maintained wording for implementation.

## Executive conclusion

Open Hollywood can become a fully agentic creative-writing application. The
target is not an unconstrained swarm. It is a durable, bounded creative workflow in which an orchestrator delegates to registered specialist agents, persists meaningful artifacts, validates work, and pauses at deliberate human approval points.

The human supplies a premise and occasional direction. Agents develop the
story world, characters, structure, scenes, dialogue, revisions, continuity,
and final presentation. The user interacts through chat and artifact review,
not a conventional manuscript editor. Runs may use local, cloud, or hybrid
model profiles, and every potentially repetitive workflow has hard limits.

The legacy scene engine is a research prototype and source of useful ideas,
not the application foundation. Preserve its character isolation, director
role, emotional-arc tracking, visual identity, and dialogue experiment while
rebuilding the product infrastructure.

## Product definition

“Fully agentic” has three levels:

1. Autonomous planning: infer a creative brief from sparse user input.
2. Autonomous production: create structured story artifacts and a complete
   work through specialist passes.
3. Sparse human governance: pause at major approval points and allow revision, rejection, comparison, or branching.

The orchestrator chooses from registered capabilities. Every specialist has a typed input, typed output, allowed tools, model assignment, token budget,
attempt limit, rubric, and completion condition. Recursive, arbitrary agent
creation is prohibited.

See `what_fully_agentic_should_mean.md` and
`recommended_creative_workflow.md` for the canonical product and workflow
definitions.

## Technical direction

Build a local-first modular monolith:

1. React and TypeScript client
2. FastAPI API
3. Python workflow worker
4. Provider-neutral creative engine

Use LangGraph for explicit durable workflow execution, SQLite for local
persistence, SQLAlchemy and Alembic for domain storage, and an internal model gateway for Ollama and cloud providers. Package the stable browser-based system with Tauri later.

See `recommended_tech_stack.md` and `docs/adr/` for accepted decisions and
tradeoffs.

## Memory direction

Do not represent memory as an ever-growing transcript or one vector database. Maintain five layers:

1. Authoritative user intent
2. Structured canonical story bible
3. Immutable versioned artifacts
4. Durable workflow/checkpoint state
5. Ephemeral, bounded context packets per agent task

Use deterministic dependency selection first. Semantic retrieval may support
research notes and later long-form manuscripts, but it does not replace the
story model.

See `memory_and_context_architecture.md` for the canonical policy.

## Model and evaluation direction

Begin with three model profiles:

- Local baseline
- Hybrid economical
- Cloud quality

Record exact provider, model, profile, prompt version, artifact inputs,
settings, token use, latency, cost, retries, schema validity, evaluation scores, and human preference for every invocation.

Compare the agentic workflow blindly against a direct single-model baseline.
Human preference is the highest-weight quality signal; model critics are useful filters, not proof of human-level quality.

See `model_configuration.md` and
`product_contract_and_benchmarks.md` for the canonical experiment plan.

## UI direction

Use a three-panel workspace:

- Projects and artifacts on the left
- Chat and workflow timeline in the center
- Artifact inspection, versions, diffs, provenance, and evaluation on the right

There is no general-purpose editor. Revision happens through chat and targeted artifact actions. Agent activity is transparent but collapsible, and private reasoning is never exposed as chain-of-thought.

See `ui_ux.md` for the canonical experience definition.

## Guardrails and formatting

Every run has independent limits for graph steps, agents, revision cycles,
model calls, tokens, monetary cost, wall-clock time, retries, and schema
failures. Runs support cancellation, pause/resume, idempotency, and provider
circuit breaking. Budget exhaustion preserves partial work and pauses safely.

Formatting is deterministic. Prose uses structured Markdown/HTML; screenplays later use Fountain as a canonical intermediate format. Renderers—not language models—produce final PDF, DOCX, HTML, or other exports.

See `guardrails.md` and `formatting_strategy.md` for canonical requirements.

## Transformation sequence

The rewrite proceeds through:

1. Product contract and benchmarks
2. Technical foundation
3. Persistence and model gateway
4. Blueprint vertical slice
5. Draft production
6. Whole-work processing
7. Evaluation and experimentation
8. Desktop delivery

The first meaningful milestone is a durable blueprint workflow: premise to
structured blueprint, human revision/approval, restart recovery, and complete invocation/artifact/cost records. Autonomous drafting begins only after that foundation works.

Implementation status is maintained exclusively in
`step_by_step_implementation.md`.

## Final recommendation

Preserve the character-agent dialogue concept rather than the legacy
application shell. Use an explicit graph, make the story bible and artifact
lineage the center of memory, treat every call as budgeted and reproducible,
make local/cloud/hybrid profiles first-class, evaluate through blind human
comparison, and preserve the no-editor philosophy through excellent artifact
review and chat-driven revision.