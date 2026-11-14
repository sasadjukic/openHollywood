# ADR 0054: Separate compact OpenAI mapping and manifest

- Status: Accepted; local injected-fixture qualification only
- Date: 2026-11-14
- Extends: ADRs 0051 and 0053; preserves version-one execution and records

## Context

The compact diagnostic presentation reconstructs the original assessment work,
source bindings and schema. It needs an explicit provider admission boundary before
new live requests can be proposed. The old smoke is closed after its first count
exceeded the input reservation. Its unused slots cannot be resumed or reassigned.

## Decision

1. Add `prepare_compact_wire`, which regenerates the exact version-two presentation
   from the supplied completion context before calling the existing internal wire
   serializer. Refuse version-one messages or arbitrary replacements. Application
   admission still authenticates the original registered probe source; pure mapping
   and self-consistent hashes do not authenticate it.
2. Add separate version-two request, request-set, fixture, journal, terminal and
   publication contracts. Preserve original work/batch/unit identity, source receipt,
   response schema and model/resource settings. Bind the exact compact export
   manifest and separate local provenance bytes into the new request identity.
   Neither local provenance nor request/journal metadata is added to endpoint bodies.
3. Reuse the unchanged OpenAI protocol serializer, response mapper, `Settings`,
   `Exchange` and low-level wire records. Their version-one discriminators describe
   shared protocol records, not the diagnostic presentation. The outer manifest is
   version two and cannot be accepted by the version-one path. Pin those shared
   implementations as well as the new modules and compact exporter.
4. Preserve strict count and generation bodies, disabled truncation and the native
   structured response schema. The count body contains the same model, messages,
   reasoning and text format as generation. It excludes generation-only settings
   according to the already qualified protocol mapping. No SDK or provider change.
5. Keep the version-two fixture lifecycle separate. Authenticate and regenerate
   sources, compact export and request preparation before dispatch/publication.
   Record durable intent before the injected transport callback and retain response
   hashes, terminal status, error chain, nullable usage and consumed pending intents.
   Refuse retries, repair, resume, unsafe destinations and changed publications.
6. Native binding and accounting are separate. Missing usage or observed usage above
   the input/output/context/cost reservation produces an accounting hold and stops
   later dispatch. The cost check uses a conservative local estimate, not billed
   cost. A structurally bound final remains available for read-only inspection with
   factual support, evidence adequacy and craft unassessed. Interrupted or failed
   whole-work coverage cannot be promoted to complete delivery.
7. Expose only `prepare`, `capture-fixture` and `audit` in the new operator CLI, with
   an explicit `--presentation` export required throughout. `capture-fixture` accepts
   only `httpx.MockTransport`; no client, authentication header, network route or
   live switch. Existing process-environment secret-refusal guards remain active.

The version-two lifecycle is an explicit derivative of the qualified version-one
fixture lifecycle. Sharing more orchestration now would change hashes underpinning
the frozen old run. Preserve that boundary in this slice, use matching conformance
tests, and leave any common-core refactor to a separately qualified change.

## Qualification and limits

Qualify N06/N07/N10/N11 using real registered source authentication and unchanged
authored finals. Exercise actual outgoing bytes through injected transport, native
completion, source/provenance drift, resource stops and immutable export reuse.
Fixture counts are invented transport data, not token measurements. No saved
provider capture is relabeled as a response to the new messages.

This is not a live runner or plan. A future smoke must qualify its real-transport
wrapper locally, freeze new exact endpoint bodies and stops, obtain approval, and
count all four requests before any generation. Production prompts remain unchanged;
the canary stays on hold. No database schema, UI route, dependency or human workflow
checkpoint is introduced. Story quality and editorial review remain separate.

See the [qualification report](../handoffs/assessment-openai-compact-qualification-2026-11-14.md).
