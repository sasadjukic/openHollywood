# ADR 0058: Authored-source OpenAI mapping and fixture journal

- Status: Accepted; local injected-fixture qualification
- Date: 2026-11-15
- Extends: ADRs 0054 and 0057

## Decision

Add separate `assessment_openai_authored` model-boundary records and an
`assessment_openai_authored_delivery` application service/CLI. Preserve all
existing source, presentation, compact mapping, journal and observed-publication
implementations and their frozen bytes. Do not fabricate a saved-review
`CompletionContext` or probe `SourcePin` for authored controls.

Regenerate the registered F01/F02/F03 authored presentations and require exact
messages/schema before invoking the existing internal OpenAI serializer. Reuse
the qualified endpoint/response mapping, `Settings`, `Exchange`, conservative
resource checks, native binder and completion. Shared protocol discriminators
describe protocol records, not source origin. New outer contracts explicitly
identify `authored_diagnostic` source and `injected_fixture` delivery.

The request set admits exactly three registered works in F01/F02/F03 order, each
with its three original active claims. Bind each source pin, full work, source
receipt, presentation, resource settings and implementation to its request
identity. Count all three before any generation, with three fixed count slots,
three fixed generation slots and zero retries. This is a local fixture allowance;
every preparation retains `live_authorized=false`.

Retain both exact endpoint bodies and their byte/canonical digests. Both endpoints
receive the same complete source-bearing input, reasoning and structured response
schema. The count body excludes generation-only settings under the existing
protocol contract. Truncation remains disabled. Do not add gold, alter diagnostic
instructions, trim context or rebind original local source identities.

## Durable fixture lifecycle

Expose only `prepare`, `capture-fixture` and `audit`. Accept only `httpx.MockTransport`;
do not construct an HTTP client, authentication header, live transport, credential
setup or provider metadata request. Keep process-environment secret-refusal guards.

Authenticate all three registered sources and regenerate the exact preparation.
Write and fsync intent before calling injected transport; check actual outgoing
bytes, headers and destination. Recheck source/preparation/implementation and
fixture bytes before intent and again after intent, before dispatch. A drift or
interruption after intent leaves a consumed, unknown slot; never resume it.

Maintain an exclusive hash-linked intent/outcome/stop journal. Refuse existing
journals, retries, repairs, substituted replies, unregistered sources, mixed
origins and out-of-order slots. Replay all recorded outcomes during audit.
Preserve consumed pending intents, unknown elapsed time, undispatched slots,
mapped error codes, raw-response digest availability and nullable usage. Original
HTTP bytes are not retained as observations; authored fixture inputs remain visible.

Count failure, resource admission failure, unsafe/invalid final, transport error,
cancellation, missing usage, reservation violation or cumulative known fixture
transport time at the cap stops later dispatch. The cap is checked between
fixture exchanges; this is not qualification of real HTTP timeout/cancellation
behavior. A future live wrapper must qualify its real deadlines separately.

Completion eligibility requires a closed `complete` journal, all three native
works complete and bound, no pending intent and no accounting hold. Structurally
bound finals remain inspectable when usage is missing or exceeds a reservation,
but cannot grant publication eligibility. Report unknown usage separately from
known excessive usage. Preserve input/output/reasoning/cached-input counters and
null actual billing; authored usage is neither measured demand nor billed cost.

## Read-only export and limits

Use existing bounded reads, secret checks, linked-path/overlap refusal, exclusive
writes and manifest-last immutable exports. Reauthenticate before writes and reuse.
Preparation has ten members; each audit has fourteen, including full source
envelopes, request set, journal, audit and separate evidence views for all families.
Rebind authority only in derived renderer inputs; retain original scope/authority
inside the unchanged source. Failed and partial runs retain every original work.

Factual support, evidence adequacy, editorial effect, edit necessity and craft
remain unassessed. Writer permission remains false. Local fixture success does
not register an observed delivery or establish model reliability/story quality.
No production prompt, graph, database schema, dependency, UI or human checkpoint
changes. Live calls remain paused and the canary on hold.

Next, qualify a real-transport wrapper and explicit observed-delivery audit locally,
then freeze a three-work smoke proposal for approval. See the
[qualification report](../handoffs/assessment-authored-openai-qualification-2026-11-15.md).
