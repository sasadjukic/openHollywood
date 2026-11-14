# ADR 0053: Versioned compact diagnostic assessment presentation

- Status: Accepted; read-only local preparation and verification
- Date: 2026-11-14
- Extends: ADRs 0049 and 0051; does not replace their formats or frozen requests

## Context

The four-work smoke stopped at its first input count, above the application
reservation. A subsequent local audit found that operator provenance and the
expanded evidence registry dominated the diagnostic packet. Local factoring
preserved exact reconstruction, but was not an application-owned presentation.

## Decision

Add `assessment_compact_presentation` as a separate provider-neutral domain
component, registered-source application exporter and operator CLI. The existing
version-one presentation, OpenAI mapper, manifests, journals and smoke remain
unchanged. There is no implicit fallback or automatic conversion on a live route.

1. `assessment-intake-presentation-2` has an explicit new diagnostic instruction
   and presentation identity. Preserve the original native work, batch, active
   claims, source pins, response schema, scope declarations, briefs, all dispositions
   and complete original messages. Production prompts and writer dispatch do not change.
2. Render complete source and review documents as structured objects. Retain
   their original identity, version and exact content hash. No summaries, excerpts,
   source filtering, new gold or narrower claims are introduced. Historical
   `model_input` labels describe original visibility, not this new presentation.
3. Present every existing evidence ID in ordered rows with explicit columns:
   reference, document identity and JSON Pointer. Explain pointer escaping, array
   indexing, whole-field scope and the difference between a location and adequate
   evidence. Reconstruct quotes, hashes and offsets deterministically from the full
   visible source. Initially admit only complete-field locations; refuse paragraph
   or partial-field layouts and noncanonical document serialization.
4. Retain only the recognized `operator-provenance-not-visible-authority` scope
   document body in a separate, exact local file. Keep its identity/version/hash
   and an explicit local-only marker in the model view. Do not move other scope or
   source documents silently. The native registry must still bind only to visible
   source documents. The diagnostic instruction makes local archive contents
   unavailable to the model and does not promote provenance into story authority.
5. Reconstruct the original version-one packet exactly and revalidate its native
   work, scope and registry. Consistency is not authentication: acceptance also
   regenerates the candidate from the authenticated current intake. Rehashed but
   changed schema, instructions, declarations or provenance cannot bypass this check.
6. Use the existing registered probe collector and immutable publisher. Export
   exact intake, source receipt, local provenance, each batch presentation, literal
   view and a manifest written last. Recollect sources before publication; reject
   protected/linked paths, drift, secrets and partial/changed/extra exports. Exact
   repeats preserve bytes and mtimes. A read-only verify command regenerates the
   export against the registered source without creating or repairing it.

The strict version-two bundle and presentation schemas describe local records.
The native work view is not a new `AssessmentWork`, and neither the export nor a
self-consistent hash proves provider delivery or semantic support. Source collection
is the application's trust boundary. The pure reconstruction function alone is not.

## Limits and next boundary

This slice has no provider settings, request bodies, transport, credential lookup,
input-count calls, delivery receipts, database route or writer permission. Native
binding is exercised with unchanged, explicitly authored responses locally; that
does not make them model observations or semantic gold. No new human checkpoint.

A separate version-two provider mapping/manifest must be qualified before freezing
new live requests. Any future smoke requires exact new endpoint bodies, reviewed
resource ceilings, stops and approval. Byte reductions are not token measurements.
The old one-shot smoke remains closed. Editorial judgment and story quality remain
separate from factual delivery/binding.

See the [implementation report](../handoffs/assessment-compact-presentation-2026-11-14.md).
