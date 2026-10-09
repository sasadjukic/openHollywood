# ADR 0025: Link current findings to original repair obligations

- Status: Accepted
- Date: 2026-10-09
- Amends: ADR 0013's historical repair materialization and ADR 0024's scope.

## Context

The v40 writer-repair experiment consolidated current boundary and assignment
reports, but an unmet historical repair check still appended another issue for
the same defect. Different wording and current evidence produced new repair
targets on subsequent revisions. Category-only suppression or fuzzy text
matching could conceal independent defects.

## Decision

New executions identify production contract v41 / graph v9. A repair-bearing
critic response adds required `current_finding_refs` to each existing repair
check. References select current reports: `boundary`, `viewpoint`,
`assignment:<anchor>` or `issue:<zero-based raw issue index>`. The model identifies
the same original claim, category and severity and explains equivalence in its
existing assessment. Current evidence may differ. Met checks and checks without
a repeated current finding require an empty array.

The application tracks these routes internally while validating all current
findings. It rejects missing/nonexistent/duplicate references, links from met
checks, category or severity changes, competing ownership and partially linked
consolidated findings. All routes of a v40 consolidated finding must refer to
the same original repair. Raw craft issues cannot inject internal provenance.
Independent and unlinked findings remain; an unmet test always requires revision.

Replace explicitly linked current issues with one carried original obligation,
retaining its original claim, requested repair, category and severity. Union the
current evidence from its repair check and linked findings. Existing exact-text
repair lineage then retains the source test identity across subsequent reviews.
Distinct original test IDs remain distinct even when their original text agrees.
Internal route fields are removed before canonical critique validation.

Revision-acceptance audit schema 2 retains the exact candidate version, original
tests, link selections and bounded/redacted current assessments and linked
findings. This preserves current wording for inspection without creating a new
canonical repair target. Production execution and isolated probes share the same
audit helper. Failed-review evidence also retains bounded link references.

Only repair-bearing response schemas grow. The measured four existing diagnostic
requests add 784 characters each; their other message content and inputs remain
identical. No new role, inference call, provider dependency, migration, canonical
artifact field, API/client contract or retry/revision allowance is introduced.

## Limits and qualification

The application verifies link structure and provenance, not narrative semantic
equivalence. A model can wrongly link a different claim in the same category or
omit a distinct defect. Empty links do not invoke inferred deduplication. This
decision does not claim all revision-loop duplicates are eliminated.

The live unchanged-draft control correctly links the repeated tension and
outcome reports to their two original repairs. However, one repaired draft
produces invalid links on met checks on both allowed attempts. A missing-turn
control mentions that omission in assessment text without creating a separate
turn finding. An ambiguous draft also changes from REVISE in v40 to PASS in v41.
These failures remain open; this implementation is not evidence that technical
stabilization or critic reliability is complete.

Follow-up should first make the empty-link requirement for met checks explicit
in the schema's status alternatives, and verify the failed control with the same
bounded retry policy. Separate investigation is needed for missing-turn routing
and match-versus-authorship interpretation. Do not silently discard invalid
links or derive new blockers by keyword matching assessment prose.

## Verification

Twenty-eight new cases cover linked evidence, preserved source identity, independent
findings, invalid links, audit handling and two persisted manuscript revisions
with replay. Six cases additionally reproduce and fix malformed craft fields
being linked away before canonical validation. All 28 focused cases, Ruff,
strict mypy over 173 files, frontend format/lint/types, 11 frontend tests and
production build pass. Before that safeguard, the full 732-test suite passed.

Both subsequent full 738-test runs report 737 passes and the same worker shutdown
failure: one invocation remains running after cancellation. It reproduces in the
worker group, then that group passes unchanged. The final full rerun still fails.
The report retains the failure and limited HEAD-source comparison; its cause is
not established here. Final candidate verification is incomplete.

Five approved live critic probes use six calls: four validated reviews and one
failed probe after two attempts. Every request reconstructs and both valid and
failed responses replay exactly. The source database and prior evidence remain
unchanged. See the [live report](../benchmark_reports/linked-repair-findings-v41-2026-10-09.md).
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.
