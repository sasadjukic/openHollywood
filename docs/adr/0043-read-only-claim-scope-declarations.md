# ADR 0043: Read-only claim-scope declarations

- Status: Accepted
- Date: 2026-11-05
- Extends: ADRs 0041 and 0042, retaining their diagnostic provenance boundaries.

## Context

The claim-scope/gold audit found event statements evaluated against obligation
criteria and causal statements evaluated for event occurrence alone. The following
Sol-high screen passed all 112 explicitly scoped slots across both orders and two
repeats. This justified a bounded read-only integration check, not production
promotion, a semantic parser or writer authority. The user authorized that check
and preservation of its repeat/order pairs; inference remains paused.

## Decision

Add the pure `evaluations.assessment_claim_scope` module beside the existing work
and result components. Keep their contracts, prompts, response schema, completion
behavior and callers unchanged. The new layer has no provider, filesystem,
database, workflow or production dispatch operation.

`assessment-claim-declarations-1` binds authored declarations to an exact work
fingerprint. Each declaration retains the original selected statement and report
field pointer, intended claim/evidence predicates, material components and their
declared coverage, unresolved qualifiers, source roles/references, evidence
requirement and observation basis. No model judgment or expected support label
belongs in this contract. It is a local sidecar, not added to model requests.

`audit_claim_scope` revalidates work, request-bound active scope and declarations.
It checks all supplied declarations for exact identity, including inactive units;
foreign or duplicate units, references, roles or predicates are rejected. Referenced
sections use the existing versioned evidence registry and its full validation.
Valid partial declaration sets are allowed, with a visible finding for each missing
active declaration. The application supplies the full report field and exact quote.

`assessment-claim-audit-1` distinguishes `declared_consistent` from
`needs_scope_review`. Findings expose missing source roles, different declared
claim/evidence predicates, an unreviewed whole claim, omitted material qualifiers,
editorial scope and unavailable-scope inconsistencies. They do not grade support.
Assignment obligations require declared assignment authority; endpoint claims need
both assignment and draft scope; defined procedures need definition and draft;
event/means/attribution claims need draft; plan claims need plan scope.

Absence in a complete current scope differs from explicit nonperformance and an
unavailable document. A declared absence review requires draft scope with complete
field coverage. The checker verifies all non-whitespace field content is covered
by the selected sections, allowing paragraph separators and surrounding whitespace.
It does not infer which field, procedure or reading is semantically appropriate.
An unavailable-document declaration can have no citation; none is fabricated.

Source roles, material inventories, observation bases and the claim interpretation
are **authored assertions**. Correct identity and consistency do not prove their
semantic correctness or completeness. Scope references describe the evidence
obligation; they are neither a whitelist of allowed model citations nor proof that
the model's selected evidence is adequate. There is no automatic claim splitter,
rewriter, classifier or gold generator.

`render_claim_scope` recomputes the audit and displays full work/context, original
fields, selections and located source sections as literal sorted JSON. Dynamic
fences preserve embedded Markdown/HTML as data. A native result may optionally be
shown alongside the audit, but it must pass the unchanged result-binding boundary.
Missing paired arguments, failed delivery or mismatched raw-final hashes are
rejected. The module does not convert historical diagnostic schemas or receipts.

Factual support, evidence adequacy, editorial effect, edit necessity and craft stay
unassessed. Whole-relation credit and writer authorization stay false, even when
every declaration is consistent and a native result binds correctly. Returned
records are validated snapshots rather than aliases into unchecked caller inputs.

## Integration and limits

Authored tracked tests cover missing/contradictory declarations, whole selected
claims within larger fields, source coverage, incomplete absence review, identity
drift, inactive declarations, literal rendering, native-result validation and
unchanged completion behavior. Tests deliberately accept the *declaration
consistency* of a false means claim while leaving its truth unassessed.

A private adapter replays all sixteen new reports and sixteen prior interpretation
reports from authenticated files. Historical final responses and scores remain in
their original contracts. It preserves 56 repeat pairs, 56 source-order pairs and
all 112 new judgments; reproduces the earlier twenty scope-review findings among
112 historical slots; and renders all 32 complete works. Archived Python is inert.

No persistence, migration, dependency, public API/client schema, production
exporter eligibility, prompt, profile, graph, acceptance gate, writer route or
additional human checkpoint changes. An ordinary-review adapter and any automatic
scope declaration would require separate qualification. See the
[integration and verification record](../handoffs/assessment-claim-scope-integration-2026-11-05.md).
