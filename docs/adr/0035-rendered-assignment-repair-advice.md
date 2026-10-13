# ADR 0035: Render assignment repair advice from structured conditions

- Status: Accepted
- Date: 2026-10-13
- Supersedes: ADR 0034's independently authored recommendation and equality check.
- Amends: ADR 0024/0030 consolidation inputs and ADR 0033 review wire contract.

## Context

The operator retained v55 production on main and merged only v57 documentation.
In the v57 comparison, every repair-bearing review failed because its condition
strings differed from the separately authored recommendation. Source-valid
citations also accompanied unsupported requirements. The next focused change
removes the second authored advice channel; it does not redefine compliance.

## Decision

Start from v55 production. Keep its complete-fact meaning of met, relationship
scope, minimum-repair and optional-craft rules. Only the obligation rule's wire
field sentence changes. The critic remains responsible for judgments and for
proposing supported conditions in its existing call.

Require ADR 0034's `assignment_repair_conditions` array and source catalog, with
the same route identities and version/path/quotation validation. Every unmet
check, other assignment violation and viewpoint violation must have
`recommended_resolution: null`. Every generic issue with a non-null
`assignment_finding_ref` must have `recommendation: null`, at every severity.
Independent craft retains its ordinary recommendation and no condition record.

After validation, the application joins each route's condition strings with one
space, in listed order, into its existing canonical recommendation field. It
adds no prose, paraphrase, inferred condition or semantic correction. The joined
text must fit 600 characters; excessive text fails instead of being truncated.
Consolidation then follows the existing lossless route. Native and linked generic
conditions therefore remain visible in the combined writer-facing advice.

Reject any separately authored assignment advice, even if it equals the rendered
text. Require exactly one record for each current model-written assignment route,
or `[]` when none. Met checks, independent craft, application-authored boundary
policy and immutable historical advice receive no record. A linked model addition
to a boundary finding still requires one. Old canonical artifacts remain valid;
old raw responses are not automatically upgraded in production.

The bounds remain 70 records, eight conditions per record, three citations per
condition and 600 characters for each text field. Validate current source
membership, original version/path identity, exact contiguous quotations, object
shape and route coverage before downstream finding or repair-link validation.
Catalog content does not become mandatory merely because it is citable.

## Recovery and observability

Malformed conditions or extra advice are review errors. They cannot create a
canonical critique or initiate a writer revision. The existing structural retry
receives the required shape and current catalog without rejected advice. Valid
claim classifications remain preserved when their underlying condition/finding
structure validates; malformed conditions cannot establish valid hard findings
for classification retention. The retry allowance remains unchanged.

Invocation boundary audit schema 6 stores conditions, support assessments,
resolved source identities/quotes and exact rendered recommendations, marked
`repair_advice_origin: rendered_conditions`. Failure evidence retains bounded,
redacted unvalidated condition records. Neither becomes story canon.

Prompt version is 58, graph remains 9 and critic retry policy is 19. Canonical
critique and public API schemas, shared writer/critic repair tests, database,
specialist roles, writer behavior and inference allowance remain unchanged.
No migration or dependency is needed. Historical simulated tests use an explicit
test-only adapter; new boundary tests exercise actual wire validation directly.

## Qualification

Source validation establishes traceability, not applicability, entailment or
atomic decomposition. A genuine source quote can still accompany an invented
causal demand. Local tests deliberately preserve that structurally valid case.
The frozen twenty-case comparison must inspect conditions and computed advice
as well as raw checks, verdicts and structural validity before promotion.

The approved matched comparison completes in twenty-two calls: eighteen reviews
validate on their first attempt, including eight nonempty native repairs. All
first/final raw native pairs match the twenty controls. Both missing-facts cases
fail because repeated generic criticism lacks condition records; retries either
restore free-text advice or omit an independent-craft comparison. All 25 supplied
citations resolve, but some rationale still conflates order and cause. No generic
restatement is accepted live. A possible successor should share one condition
set per consolidated finding; that proposal is not part of this implementation.

The branch remains an unqualified candidate. Main retains v55. Step 19 remains IN PROGRESS;
Step 20 is NOT STARTED. See the
[implementation and comparison report](../benchmark_reports/rendered-repair-advice-v58-2026-10-13.md).
