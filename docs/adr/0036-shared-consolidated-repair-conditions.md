# ADR 0036: Shared conditions for consolidated assignment findings

- Status: Accepted
- Date: 2026-10-13
- Supersedes: ADR 0035's separate condition records for generic restatements.
- Amends: ADR 0030's concatenation of repeated repair recommendations.

## Context

Main retains v55 production and only the documentation from v58. Both v58
missing-facts controls correctly reported two unmet assignments and supplied
their native condition sets. They also declared two generic restatements with
null advice. Requiring another condition record per restatement rejected both
reviews. Copying the native records in an explicitly local counterfactual made
them validate but repeated each writer-facing repair.

## Decision

Use one model-authored condition set per native assignment finding. Keep
`assignment:<anchor>` and `viewpoint` identities, current source citations and
all v58 bounds. Every unmet check, other assignment violation and viewpoint
violation still requires exactly one set. Every authored assignment advice field
remains null. Reject `issue:<index>` condition records, duplicate native sets,
missing native coverage and separately authored recommendations.

A generic issue with a non-null `assignment_finding_ref` reuses its validated
finding's complete recommendation. The application resolves the target with the
existing hard-finding validators and exact anchor/evidence consolidation rules.
Both boundary and native aliases of the same consolidated finding resolve to
the same advice. A met, absent, stale or malformed target remains invalid.
Different anchors or evidence sets do not acquire shared ownership by inference.

All additional mandatory conditions raised by repeated criticism belong in the
one native set, with their own support assessments and citations. Generic
descriptions retain explanatory prose and evidence, but do not author another
repair. Consolidation retains those descriptions, comparisons, source severities
and distinct evidence without appending another copy of the recommendation.
Independent craft keeps its own advice, comparison and repair-link requirements.

The existing application-written boundary policy remains outside model-authored
conditions. Boundary-only restatements reuse that policy. A supported additional
assigned repair must be reported through its applicable native finding; generic
restatements cannot add free-text instructions or a separate boundary condition
record. Boundary/native overlap retains the policy plus one native condition set.
Immutable historical advice and original repair tests are unchanged.

## Recovery and observability

Malformed conditions and links are response errors, never manuscript defects.
The existing bounded structural retry uses the revised condition rule and schema.
Diagnostic rendering may leave invalid links unresolved solely to inspect other
valid classifications or retain previously validated choices. It cannot create
a critique, substitute advice for an invalid target or make an invalid new
classification eligible for retention. Production rendering rejects such links.

Boundary audit schema 7 retains one source-resolved condition record per native
owner. Each repeated issue records the referenced condition owners, whether the
application boundary policy applies, and the reused recommendation. It retains
the existing redaction and capture bounds. Failure capture remains bounded and
unvalidated. These records are invocation diagnostics, not story canon.

Prompt version is 59, graph remains 9, and critic retry policy is 20. The complete
v55 obligation semantics remain unchanged, including actions and indirect
narration as valid evidence. Canonical schemas, database, public API, specialist
roles, writer instructions and inference allowances do not change. No migration
or dependency is required. Historical test fixtures are explicitly ported; there
is no production upgrade of old raw responses.

## Qualification

Unmodified local replay accepts all twenty saved v58 first responses: eighteen
keep identical canonical results; the two previous failures now yield exactly
two blockers and one copy of each native repair. The two saved retries remain
invalid for separate advice or an incomplete independent-craft comparison.
These are historical response replays, not new model successes.

Source identity and exact quotations establish traceability. They do not prove
semantic support, applicability, atomic decomposition, correct classification
or the absence of instructions hidden in explanatory prose. The approved fresh
matrix completes in 21 calls: 19 first reviews validate, all twenty final reviews
validate, and every first/final assignment pair matches the controls. Four accepted
generic repetitions reuse one native set each without duplicate writer targets.
Both missing-facts controls yield two blockers. All 25 citations resolve; no
unassigned mandatory condition is observed in the rendered repairs.

The one retry repairs a 601-character assessment. Some supporting prose still
conflates order with causation, and immediate-cause advice is not atomically
separated from timing. Thus the focused ownership contract passes this matrix;
writer and broader semantic qualification remain open. Keep implementation fixed
for a bounded writer/critic repair test. Main is still v55; no promotion is made
by this task.

See the [v59 implementation and verification report](../benchmark_reports/shared-repair-conditions-v59-2026-10-13.md).
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.
