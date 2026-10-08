# ADR 0022: Required evidence-backed critic boundary comparison

- Status: Accepted
- Date: 2026-10-08

## Context

The v37 shared scene boundary made the current endpoint and next reservation
available to writer and critic. Its summary instruction did not produce an
explicit comparison on the frozen OH-V01-002 overrun: the critic praised completed
verification while describing the ending as a decision to verify. The user
requested a required, inspectable comparison inside the existing critic call.

## Decision

New runs use prompt v38 / graph v9. Every critic response must include one
model-facing `scene_boundary_check` with exactly five fields:

- `achieved_state`: the state established by the draft.
- `current_endpoint_comparison`: comparison with the current assignment.
- `next_scene_comparison`: comparison with the next reservation, or an explanation
  that none is supplied.
- `draft_evidence_refs`: one to three distinct handles from the exact current
  draft's existing evidence catalog.
- `status`: `no_overrun` or `overrun`.

Each prose field is nonblank and limited to 600 characters. Evidence supports
the achieved state; it is not a demand to prove the absence of every violation.
These are short review conclusions, not a request for private chain of thought.

The application verifies fields, bounds, current evidence identity and route
applicability. An `overrun` requires an explicit immediately next reservation and
a populated current outcome or turning point. Otherwise the specialized schema
permits only `no_overrun`, and validation rejects an inapplicable overrun even if
the provider ignores that schema. Existing missing/replaced-assignment and POV
routes remain available. `no_overrun` does not certify that the current outcome
was achieved or clear independent blockers.

A valid `overrun` materializes as a blocking `scene_assignment:outcome` issue
(falling back to `turning_point` when necessary), with resolved current evidence,
the comparison and application-supplied repair guidance preserving the current
plan and reserving the distinct next work. It forces REVISE independently of
craft scores or a supplied PASS. Overruns belong in this check; other assignment
violations continue through their existing response field. No fuzzy semantic
deduplication or keyword interpretation is added.

Missing/malformed comparisons are review-response errors. They use the existing
bounded structural retry, never fabricate a manuscript defect, and cannot
produce a canonical critique. Repair guidance is version 10; call/revision
limits and graph routing are unchanged.

## Provenance, cost and compatibility

Successful invocation diagnostics retain a bounded, redacted
`scene_boundary_audit`: exact candidate/current-plan identities, next reservation
with its approved Blueprint identity, and the validated comparison. The probe
runner exports the same audit. Failed-response capture allowlists these fields
under its existing total bounds and redaction policy, marking them unvalidated.
Neither diagnostic record becomes story canon or retry evidence.

Canonical Critique and database schemas are unchanged. Only an actual reported
overrun becomes a normal canonical critique issue. No migration, API/client
contract, provider-specific rule or new role/call is required. The writer's v37
messages remain unchanged.

Remove model-authored target-kind/key/version fields from the critic schema on
initial calls, extending the existing revision behavior: the application already
binds all three to the exact task draft. This offsets most of the new comparison
schema. The five measured initial critic requests grow by 134 characters.
Seven revision requests grow by 134–912 characters; those with repair acceptance
tests already had this saving. These are sample measurements, not a universal
size guarantee. Existing call budgets remain fixed.

## Evidence and remaining limit

Twenty-three new cases cover schema delivery/applicability, required comparisons,
exact and stale evidence, malformed review isolation, high-score blocking,
independent hard gates, redaction, source identities and persisted revision versus
response-repair behavior. Full Python/frontend checks passed.

All five authorized frozen-input Cloud probes validated on their first calls.
All retained their v37 verdicts. The original overrun still passes, but its new
comparison explicitly acknowledges that verification exceeds the decision to
verify. It calls this a general match and treats scene 2's particular secret
flourish as still reserved. This exposes the model's stated interpretation;
successful structured output does not establish correct narrative judgment.

See the [implementation and probe report](../benchmark_reports/critic-boundary-v38-2026-10-08.md).
Improved overrun detection, fresh writer behavior and full-story recovery remain
unqualified. Step 19 is IN PROGRESS; Step 20 is NOT STARTED.
