# ADR 0042: Active assessment results and evidence locations

- Status: Accepted
- Date: 2026-11-03
- Extends: ADR 0041; retains ADRs 0038 and 0039's read-only/provenance boundaries.

## Context

The [local audit](../handoffs/reviewer-scope-citation-audit-2026-11-03.md) found
that broad response schemas permitted context-only claims outside the active
assessment batch. It also found correctly mapped source indices with incorrect
or incomplete model-selected evidence. Those are separate failure classes.
The user authorized integrating the verified scope contract and literal evidence
renderer into the tracked read-only component. Live inference remains paused.

## Decision

Add `evaluations.assessment_result` beside the existing assessment-work module.
Keep the existing work/context/receipt/completion contracts unchanged. The new
module has no provider, SDK, filesystem, database or workflow operations, and
does not add a CLI or production caller.

`assessment-active-scope-1` binds an exact work fingerprint, batch, adapter-supplied
request fingerprint and ordered active unit IDs. Generate a closed response
schema with one required property per active unit. Models provide only support,
evidence IDs and reason; the application supplies report field, exact quotation
and offsets from the work record. The local contract admits at most twelve
active units, eight distinct evidence IDs per unit, 1,200 characters per reason,
8,000 reason characters in total and 64,000 raw-final characters. These are
response tooling limits, not manuscript constraints or inference budgets.

`assessment-evidence-registry-1` is an explicit registry document inside the full
work context. Each location binds a source document identity, version and exact
JSON-text hash, a JSON pointer, exact field hash, Unicode code-point offsets and
quotation. A null paragraph denotes the complete field; a positive ordinal
denotes one exact nonempty paragraph. Paragraph splitting uses the pinned
blank-line rule `\r?\n[ \t]*\r?\n`, preserves spaces and selects repeated text by
occurrence. Reject ambiguous/missing registries, duplicate IDs, wrong versions,
sections, hashes, offsets or text. Validate all entries, including uncited ones.
This registry is distinct from the production v61 excerpt catalog and earlier
private registry shapes. No legacy registry is silently reinterpreted.

Binding requires a successful receipt with the exact work, batch, request and
active-unit set. On this new boundary, `result_sha256` hashes the **exact raw final
UTF-8 text**, including whitespace. Historical receipts are not changed or
converted. Reject duplicate JSON keys, malformed output, missing/extra slots,
model-authored identity, unknown/duplicate evidence and failed delivery, even
when a failed response contains a parseable object. Definite labels require at
least one evidence reference; uncertainty may have none. Do not repair or filter
an invalid response into an accepted subset.

`assessment-bound-result-1` retains the unchanged raw final and original delivery
receipt, separately exposing a derived receipt with complete location binding for
the existing `complete_work` function. It preserves model judgments explicitly as
model-authored data. Successful binding leaves evidence adequacy, factual support,
edit necessity and craft unassessed. Whole-relation credit and writer permission
remain false. Unknown usage stays unknown and missing batches stay incomplete.

The renderer recomputes binding from work/scope/receipt/raw final; it does not
trust a caller-supplied resolved result. It renders the full work, all context,
original selected statements, raw final, original and derived receipts, model
judgments and application-resolved source locations as literal fenced JSON.
Embedded Markdown/HTML cannot escape the fence. No source is trimmed, shifted,
normalized or semantically promoted.

Revalidate caller-created records at every boundary and retain validated scope
snapshots. An unchecked Pydantic instance with mutable containers must not keep
an alias into the returned result.

## Trust and qualification

The supplying adapter must authenticate the source archive, completeness and
model visibility of the context/registry, the actual prepared wire, terminal
status and usage. Internal hashes detect inconsistency; they are not signatures
or proof that the model saw the supplied content. Provider compatibility with the
new schema is **unverified**. No provider request is created by the engine module.
Exporting/persisting callers remain responsible for the existing credential guard;
the pure component does not read environment secrets.

Authored tracked tests cover the two-active/seven-returned failure, missing and
duplicate slots, identity/receipt drift, malformed/terminal responses, incomplete
compound evidence, wrong planned sections, repeated paragraphs, exact Unicode,
escaped/list pointers, literal rendering and completion/unknown-usage integration.
False private-flourish and opening-time claims are retained without semantic
acceptance. Private captures and original experiment scores remain unchanged.

No migration, dependency, public API/client schema, profile, prompt, graph,
acceptance gate, writer route or human checkpoint changes. The next optional
citation experiment must isolate evidence selection from active-scope changes.
See the [implementation record](../handoffs/assessment-result-integration-2026-11-03.md).
