# ADR 0041: Read-only assessment work and completion

- Status: Accepted
- Date: 2026-11-02
- Builds on: ADRs 0037, 0038 and 0039; diagnostic use of provider routing in ADR 0040.

## Context

The local staged-handoff and workload previews preserve complete source context
and exact selected statements, but do not provide a tracked completion boundary.
Live diagnostics show that valid delivery, correct quotation location and factual
support can disagree. A partial or well-formed assessment must not silently become
a complete review, a story defect or permission to rewrite prose.

The user authorized a small tracked component and preparation of independent
DeepSeek and Luna workload comparisons. Inference still requires approval of the
frozen plans. No production prompt, graph or writer-routing change is authorized.

## Decision

Add `engine/open_hollywood_engine/evaluations/assessment_work.py`, containing pure,
strict, versioned records and functions. It has no provider, database, workflow,
filesystem or inference operation. Its initial source provenance admits only
synthetic fixtures and diagnostic captures. Existing ordinary and diagnostic-probe
exporters remain unchanged; this component does not broaden their eligibility.

An assessment context retains complete immutable source/report documents, the
exact source presentation, report-field pointers, selected statement offsets and
quotes, and separately declared relation links. Verify document hashes, full-field
membership and exact Unicode offsets. Complete documents and source messages stay
present when the assessment workload is partitioned. A fingerprint detects scope
changes; it is not a signature or proof of source truth. The supplying adapter must
authenticate the source archive and the completeness of the supplied context.

Partition whole selected statements in stable order. Keep transitive declared
links together; reject a linked group larger than the limit rather than severing
it. No application inference creates semantic links. The diagnostic adapter uses
previously authored links and keeps their expected judgments out of model input.

A work record binds the entire context and exact-once batch coverage. A receipt
binds work, batch, actual prepared request and attempt identities. Successful
receipts require every expected selected unit; failed receipts cannot contain a
credited result. Duplicate attempts, unknown batches, mixed work scopes or changed
requests are rejected. No retries are admitted by this initial completion contract.

Completion requires all expected valid batches. Sum all known input/output usage
and active time; count unknown usage explicitly. Reasoning is part of output,
never a second token allowance. Missing or failed deliveries prevent completion.
Delivery and binding remain separate, and even complete binding leaves **support,
edit necessity and craft unassessed**. Whole-relation credit and writer permission
remain false. These functions aggregate delivery facts, not semantic judgments.

Render the entire work record as literal fenced JSON. Revalidate records at
partition/completion/render boundaries, including objects made through unchecked
Pydantic construction or copying. Callers retain responsibility for credential
guards before exporting or persisting data; the diagnostic harness uses the
existing secret guard. The engine component does not read environment secrets.

## Integration and qualification

The new private diagnostic harness consumes the tracked records directly and
authenticates saved source captures. It freezes MA full-workload controls and NA
narrow assessments with full context. Provider adapters serialize actual request
bodies in mocked transport checks before live approval. OpenAI receives its native
closed schema; the Ollama Cloud route retains the historical prompt-only schema.
These provider differences are recorded, not treated as a pure model comparison.

Tracked authored fixtures cover whole statements, transitive links, altered
sources/pointers/quotes, incomplete coverage, failures, unknown usage, literal
rendering and the absence of semantic/writer authority. Private tests additionally
replay twelve repeated MA controls and four latest MA/WB captures without changing
their historical semantic judgments. Full unpublished captures remain private.

No dependency, SQL migration, API/client schema, model-profile activation,
production prompt/graph change, writer route or additional human checkpoint is
introduced. There is no automatic admission or semantic dependency extractor.
Adding ordinary-production provenance, durable storage or workflow dispatch later
requires a separately reviewed adapter and migrations where applicable.

See the [implementation and verification record](../handoffs/assessment-work-integration-2026-11-02.md)
and [two-provider frozen plan](../handoffs/reviewer-assessment-workload-frozen-plan-2026-11-02.md).
