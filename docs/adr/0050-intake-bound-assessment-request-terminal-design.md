# ADR 0050: Intake-bound assessment request and terminal evidence

- Status: Accepted; narrow fixture-only preparation, capture and read-only audit
- Date: 2026-11-13
- Extends: ADR 0049. Preserves ADRs 0046–0048.

## Problem

The six saved B deliveries qualify under their original archive contract, but none
matches the four current intake works. The authored completion publisher cannot
authenticate a model response by accepting a caller's origin label or receipt.
The missing boundary is a prospective link from authenticated intake through exact
assessment input and transport evidence to native binding and completion.

## Decision

Prepare one immutable request manifest per **existing batch**, and commit the
complete ordered set for the unchanged work before any dispatch. Recollect the
registered source and recompile the intake; retain the complete work, declarations,
briefs, active units, holds and unselected fields. No new selection, interpretation,
gold, batching or prompt is inferred by this boundary.

The manifest binds source pins and the source-verification receipt, exact rendered
assessment presentation and schema, renderer/adapter implementation identity,
provider/model/settings, exact destination/method/path, exact serialized body bytes
and canonical body hashes. Input-count and generation are distinct endpoints. An
adapter must establish how each body encodes the presentation and settings, rather
than accepting unrelated bodies with internally consistent hashes.

Use `payload_canonical_sha256` for the versioned request payload. Its wrapper does
not participate in that hash, avoiding self-reference. The whole-work plan commits
the ordered manifest identities, unique attempt IDs and budget slots; manifests do
not refer back to the plan. The native receipt's existing `request_sha256` slot
holds this payload identity **only for this versioned fixture adapter contract**. Do not rewrite
historical request identities or use a count/body/final hash interchangeably.

The application owns the dispatch journal. Persist each endpoint's intent before
send, compare the actual serialized destination/body with the frozen endpoint at
the transport boundary, then record response or failure. Intent without a response
means possibly sent: consume the relevant attempt and preserve unknown usage.
No automatic retry, repair or resume dispatch. Count and generation have separate
counters; failed/unknown count blocks generation. A cancelled pre-dispatch work has
no generation receipt. A missing journal is incomplete evidence, not a free retry.

Terminal evidence binds the manifest and attempt to the ordered endpoint records,
safe response metadata, exact final text, error chain and per-counter usage. Keep
the hash of the retained response separate from any observed raw HTTP-body digest.
The latter is not independently replayable if those bytes were not retained. Keep
missing provider IDs and unknown usage/billing null; do not substitute a count
estimate for generation usage. No credentials, arbitrary headers or reasoning text.
Source seals and captured metadata provide local integrity, not provider signatures.

Derive terminal receipts; never accept submitted success, binding, usage approval or
writer permission. Only complete, successful transport plus native parsing/binding
can yield `bound_unassessed`. Retain malformed, empty, refused, truncated, cancelled,
interrupted and non-200 outcomes without salvaging slots. A terminal audit record is
not a successful completion. Recompute whole-work completion over every original
batch; missing or failed batches cannot produce a successful subset publication.

Successful binding may coexist with unknown usage. Preserve both facts, stop further
dispatch pending accounting, and leave actual cost unknown. Known-token subtotals
must always be accompanied by unknown-usage counts; zero subtotal is not zero cost.
All semantic/evidence/editorial/craft qualifications remain unassessed and writer
permission false. No extra mandatory human checkpoint is added to the product.

## Design qualification and implementation boundary

The three `*-design-1` schemas are **fixture-only shape specifications**, not
application endpoints, authenticated provenance or approved provider requests.
The executable local prototype uses an `.invalid` destination and a synthetic model;
it deliberately cannot parse an `authenticated_model_delivery` origin. Full-context
fixture serialization checks the binding mechanism without choosing or changing a
production prompt. A real renderer/provider mapping needs its own versioned contract.

Implement `evaluations.assessment_delivery`, the corresponding application service
and `scripts/assessment_delivery.py`. Runtime contracts use new fixture-specific
versions; historical design inputs are not accepted. Preparation commits the whole
original request set. Capture uses an injected in-process `httpx.MockTransport`,
checks actual serialized method/URL/body at the boundary, and writes exclusive,
flushed/fsynced intent/outcome/stop records. Only host/content-length request headers
are admitted; no provider credential or default network transport is used.

The ordered journal has a header, exact authored fixture input, and up to 49 chained
events. Its original fixture input remains separate from observed response evidence.
Actual HTTP status takes precedence over body claims; unsafe/invalid observed
envelopes become capture errors without persisting their observed content. Preserve
safe error chains, raw-final and nullable usage, response IDs and distinct retained/
observed-body digests. Keep unobserved elapsed intervals explicitly unknown.

Preparation and audit reuse source collection and immutable publication from ADR
0049. Recollect/recompile sources before dispatch and publication, verify exact
output reuse and refuse path overlap, linked paths, partial or changed output.
Capture refuses every existing journal. Audit may export an interrupted prefix but
does not write to it or replay a callback. A malformed member is refused; no repair.
The whole-work audit exposes native binding facts separately from publication
eligibility, which also requires a final stop. All real model origins remain rejected.

Keep the authored completion publisher and registered B archive exporter unchanged.
One measured local refinement parses each source document once per native registry
validation, preserving every binding check and reparsing on subsequent validations.
There is no cross-call cache, prompt change, scope/gold change or acceptance relaxation.

Qualify real provider-specific rendering and response mappings locally before
proposing live inference. Current flush/recovery tests do not claim filesystem-wide
atomicity or a power-loss guarantee. Injected callbacks are trusted fixture code,
not an execution sandbox. There
is no live budget, provider/model selection, API route, database migration, workflow
gate or new authenticated-delivery branch in this implementation.

See the [design report](../handoffs/assessment-request-terminal-design-2026-11-13.md)
and [implementation and verification report](../handoffs/assessment-terminal-integration-2026-11-13.md).

The [OpenAI mapping qualification](../handoffs/assessment-openai-mapping-2026-11-13.md)
now verifies the shared request serializer and a separate assessment response
mapper against six original-work saved deliveries and authored failures. The
mapping preserves scope and separate byte/canonical hashes; missing usage and IDs
remain missing. Its in-memory injected replay has no provider client and does not
authenticate a new delivery. Production response parsing remains unchanged.
Integrating this mapping into an intake-bound provider manifest and durable journal
is still required before freezing live inference; fixture contracts remain fixture-only.

Step 19 IN PROGRESS; Step 20 NOT STARTED; prompts unchanged; live calls PAUSED;
canary ON HOLD.
