# Context

`open_hollywood_engine.context` compiles deterministic, task-scoped context for
one registered specialist call. It does not retrieve from an unbounded chat
history and does not perform semantic search.

Each specialist role has a versioned `AgentDependencyManifest` declaring:

- Required and budget-optional artifact kinds with cardinality limits
- Exact canonical story-bible sections
- Minimum and maximum nearby summaries
- The structured output artifact kind

The compiler validates exact immutable artifact-version inputs, rejects
undeclared or ambiguous dependencies, selects story-bible sections in manifest
order, and keeps only the most recent permitted summaries. Its canonical JSON
packet contains the assignment, user constraints, direct dependencies, story
bible, preceding summaries, output JSON Schema, and evaluation rubric.

Mandatory content fails closed when it cannot fit. Optional artifacts and
summaries are considered in deterministic priority order and omitted with an
observable reason when the packet budget is exhausted. Every result records the
token-counter version, estimated use, SHA-256 digest, exact included artifact
version IDs, and enough information to construct the model invocation lineage.

`Utf8ByteTokenCounter` is the conservative provider-neutral fallback. Inject a
model-specific `TokenCounter` when an exact tokenizer is available; the stable
counter identifier is retained for reproducibility. `ContextTokenBudget` also
reserves space for system prompts and provider message framing.
