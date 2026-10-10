# ADR 0030: Explicit comparison of assignment and craft claims

- Status: Accepted
- Date: 2026-10-10
- Amends: ADR 0028's restatement eligibility and ADR 0029's severity restriction.

## Context

The v44 ambiguous-revision probe recovered structurally but retained two reports
of the same alleged early verification. A major `Plot Pacing` issue used null
while an original blocking outcome repair covered the same state and remedy.
Null, different category and different severity did not establish independence.
Requiring nonblocking issues to use null also prevented them from declaring that
they repeated an assignment finding.

## Decision

New runs use production contract v45 / graph v9. Every generic critic issue
requires a wire-only `assignment_comparison` containing `finding_refs` and a
bounded assessment. The existing critic compares the underlying defective state
and required repair, using the current draft evidence already required for the
issue. It does not equate shared passages or category/severity labels with claim
identity.

For independent craft (`assignment_finding_ref=null`), the critic must explain
what distinct defect survives minimally correcting the reported assignment
findings. An automatic consequence of the same breach does not justify another
repair target. The comparison covers every distinct reported assignment finding;
one native route per consolidated finding suffices. With no current assignment
findings, it uses empty references and says so.

For a repetition, the comparison includes its exact selected target and explains
why both reports concern the same defect and repair. Any valid craft severity may
declare that repetition. The target must still be a validated blocking assignment
finding. Consolidation preserves its native severity and all source descriptions,
recommendations and distinct evidence. It neither promotes an independent craft
issue nor changes the model's reported source severity. Mixed criticism should
separate the repeated portion from the distinct craft claim.

The application validates exact current references, comparison coverage, bounded
nonblank text and normal issue fields before consolidation. It does not infer
semantic identity from keywords or assess whether the explanation is true.
Missing, malformed, stale or unreported references fail structurally. No default
comparison is added to production responses.

Original repair tests remain immutable and separate. Current generic repetitions
are not aliases for linking away an original craft obligation. A historical
craft repair may remain unmet with empty links; existing exact category/severity,
single ownership and complete native-route validation remain in force.

Scene-boundary audit schema 3 retains up to 16 current comparisons, their raw issue
indexes, references, source severity and redacted assessments. Canonical critique
fields stay unchanged. Failure evidence retains bounded comparisons for local
inspection, but their prose never becomes retry or story input.

Critic retry policy 12 supplies candidate-bound reported finding groups and static
comparison instructions when comparison structure fails. It retains v44's precise
link metadata and fixed bounds. Oversized or invalid hints fall back to generic
guidance. No inference call, retry allowance, writer instruction, system prompt,
story context, dependency, public API field or persistence migration is added.

## Qualification

Local regressions cover cross-severity repetitions, independent shared-evidence
claims, complete comparison coverage, both aliases of consolidated findings,
invalid metadata, original repair preservation, redacted audits and durable
propagation to the next writer and critic.

The eight v44 responses are replayed unmodified. Three valid empty-issue reviews
materialize identically; the duplicate-bearing valid response now requires a
comparison. Two explicitly annotated offline cases verify consolidation versus
independent retention without claiming new model evidence.

The user-approved five-probe campaign used six calls, producing four valid reviews
and one failed unchanged control. Its first response recognized a repetition but
returned malformed comparison structure; its retry reclassified the claim and
omitted required comparison references. All valid responses had empty generic
issue arrays, so successful live comparison remains unqualified. The missing-turn
control also gained an outcome complaint about verification text accepted in
another case. See the report for retained failures and local counterfactuals.

The model may still misclassify a claim or provide an unconvincing comparison.
Local fixtures cannot establish semantic accuracy, improved stories or repeatable
completion. Step 19 remains IN PROGRESS. See the
[v45 report](../benchmark_reports/claim-comparison-v45-2026-10-10.md).
