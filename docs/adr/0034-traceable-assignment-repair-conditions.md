# ADR 0034: Traceable assignment repair conditions

- Status: Accepted
- Date: 2026-10-12
- Amends: ADR 0024/0030 consolidation inputs and ADR 0033 review wire contract.

## Context

The v56 instruction-only candidate asked the critic to quote requirements and
justify every native and consolidated repair condition. The matched comparison
regressed from v55's 19/20 final assignment pairs to 17/20. Correct quotations
still accompanied unsupported causal, temporal and motivational repairs. The
operator retained v55 on main. v57 starts from v55, preserving its semantic rules.

## Decision

Use the existing critic call with a required wire-only
`assignment_repair_conditions` array. Each entry identifies one current model-
written repair and lists one to eight individually justified conditions:

- `repair_ref`: `assignment:<anchor>` for an unmet mandatory check or other
  assignment violation; `viewpoint` for a POV violation; `issue:<zero-based index>`
  for a generic issue with a non-null assignment reference, at any severity.
- Each condition contains `condition`, `source_refs` and `support_assessment`.
  A citation contains a `source_ref` and a contiguous `exact_quote`.
- Condition strings joined with one space must exactly equal that route's
  complete `recommended_resolution` or `recommendation`. Thus unlisted repair
  text cannot bypass coverage merely through a valid consolidation link.
- Every required repair route appears exactly once. Met checks and independent
  craft use no entry. No model-written assignment repairs requires `[]`.

There are at most 70 entries, eight conditions per entry and three citations per
condition. Condition, quotation and assessment text are nonblank and at most 600
characters each. Existing native recommendation limits still apply.

The application supplies `repair_source_catalog` from exact input versions:
selected current Scene Plan assignment fields; currently visible Blueprint
world, character, relationship, location and voice/style content; and canonical
Story Bible facts, prohibitions, states, timeline and threads. It excludes draft
prose and reviewer allegations. Canon metadata identifiers are excluded. Broad
story intentions do not acquire mandatory force through catalog membership.

Each catalog reference hashes the version, original JSON Pointer and exact text.
Pointers retain original array positions when context filtering removes other
entities. The model selects references and quotations; the application resolves
artifact kind, version and path. Source validation checks current membership and
exact text, not applicability or semantic entailment. Current-scope rules and
canonical permissions/exceptions continue to govern the critic's judgment.

All model-written native repairs and linked generic recommendations are checked
before the critique is accepted. Consolidation remains lossless and canonical
repair text is unchanged by validation. Independent craft keeps its rubric and
comparison requirements. The existing application-written boundary repair and
carried immutable historical advice are not re-authored by this new response
field; generic additions to a boundary finding do require their own records.

## Failure handling and observability

Missing coverage, unknown/stale references, non-verbatim quotations, duplicate
routes, unlisted advice and malformed objects are review-format failures. They
cannot create a canonical critique or a writer revision. The existing bounded
retry receives static field/shape instructions and the current source catalog;
rejected advice and quotations are not replayed. Classification preservation
continues to apply. Critic retry policy advances to 18; allowance is unchanged.

Boundary audit schema 5 stores validated conditions and source quotations with
their resolved version/path identities, redacted and bounded by the wire limits.
Failure capture retains bounded unvalidated records and resolves selected source
references for inspection. These are invocation diagnostics, not story canon.
Canonical critique, shared writer/critic repair tests, database schema and public
API remain unchanged. No migration, role, provider dependency or extra model call
is introduced. Prompt version is 57, graph version remains 9.

Old raw responses are incompatible with the new mandatory wire field. Local
historical fixtures are explicitly annotated in a test-only adapter. Production
does not backfill missing conditions. Existing canonical artifacts remain valid
historical inputs.

## Qualification limits

Exact text coverage does not prove that each entry is an atomic condition or that
the model cited the clause which authorizes it. A correctly cited order clause
can still be used to justify an invented causal trigger. Tests deliberately
preserve that structurally valid but unsupported case. The writer sees the
validated repair text through the existing contract; inspectable source records
remain in the invocation audit.

Local tests cover malformed coverage, current-version identity, exact passages,
original source paths, independent craft, consolidation, redaction, and durable
review-only retry. The approved twenty-case historical comparison completed in
thirty calls. Only ten no-repair reviews validate; all ten repair-bearing reviews
fail the exact-text condition contract on both attempts. The 41 supplied citations
resolve, but separate advice still adds unsupported conditions. No nonempty
condition review is accepted live. The implementation remains an unqualified
candidate; main stays at v55. A future single-authority rendering contract requires
its own focused change and tests. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

See the [implementation and test report](../benchmark_reports/repair-condition-sources-v57-2026-10-12.md).
