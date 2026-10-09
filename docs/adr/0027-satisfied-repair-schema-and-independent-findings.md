# ADR 0027: Separate satisfied repair checks from independent current defects

- Status: Accepted
- Date: 2026-10-09
- Amends: ADR 0025's critic response schema and reporting guidance.

## Context

The v41 diagnostic returned nonempty current-finding links for satisfied repairs
on both attempts of one probe. Validation correctly rejected the responses, but
the schema still allowed that combination. Another probe mentioned a missing
turn only inside assessments, reopened the original outcome repair and never
reported an independent turn finding. There was no emitted turn issue for the
application to preserve or send to the writer.

## Decision

New executions use production contract v42 / graph v9. The shared
`RepairAcceptanceCheck` definition has two status alternatives:

- `met` requires `current_finding_refs` to be an empty array (`maxItems: 0`).
- `unmet` retains the existing bounded link format and validation requirements.

Both alternatives retain assessment and current-draft evidence. Original test
keys still reference one shared definition. Local deployments receive the schema
through the existing structured-output route; cloud deployments receive it
through the existing inline-schema route. The application still rejects invalid
links, including those supplied on a met check. It does not silently clear them.

The schema description and critic instructions keep each repair assessment tied
to its original claim. A different defect cannot reopen that repair. Report each
independent assignment failure through `assignment_violations`, with its own
anchor, evidence and repair. A missing turn needs its own finding even when an
outcome repair is already unmet. Mentions in boundary or repair assessments do
not count as actionable findings.

Existing materialization then gives the independent issue its own source-bound
repair test for the next writer and critic. There is no keyword extraction from
assessment prose, fuzzy deduplication or category-wide suppression. Existing
original repair identities, current-finding validation and audit behavior remain.

The critic instructions are compacted within their existing 3,887-character
limit. The five diagnostic requests each grow by 7 system-message characters and
1,056 user-message characters relative to v41, principally for the schema's two
alternatives. Initial-review schemas are unchanged; critic guidance applies to
both initial and revision reviews.

No role, inference call, dependency, migration, canonical artifact field,
API/client contract, or retry/revision allowance is added. Writer instructions
and approved story context are unchanged.

## Qualification

Local tests establish schema structure, continued rejection of met links,
independent issue preservation under either original-repair status, and persisted
propagation to the next writer and critic. Replaying all six old raw responses
preserves four validated results and two validation failures.

The five explicitly approved probes use six calls. Repair 19102 now passes on
its first call with empty met links. The missing-turn control keeps the original
repair met and emits an independent turn finding, but repeats it as a generic
plot blocker, creating two new repair targets. The unchanged control fails both
attempts by linking an outcome finding to its original tension repair as well as
its outcome repair. Existing category/severity and ownership validation correctly
rejects it. The other two saved repairs pass; the ambiguous match/authorship
interpretation remains unresolved.

Every valid and failed response replays exactly. This is observed improvement
on two targets with remaining failures, not general reviewer qualification. Two
coordinated contract changes were evaluated together; this is not a causal
ablation. Step 19 remains IN PROGRESS.

See the [implementation and diagnostic plan](../benchmark_reports/worker-cleanup-critic-v42-2026-10-09.md).
