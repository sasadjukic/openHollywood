# ADR 0024: Consolidate overlapping current-review assignment routes

- Status: Accepted
- Date: 2026-10-09
- Amends: ADR 0022's materialization of current-review overrun findings.

## Context

The explicit-endpoint experiment recovered overrun detection, but all three
positive responses reported the same outcome breach in `scene_boundary_check`
and `assignment_violations`. Both routes cited the same current-draft evidence
handles. Normalization created two blocking issues and therefore two repair
obligations for that overlap. Instructions already prohibit this duplicate route;
the application should handle it without discarding supported findings.

## Decision

New executions identify production contract v40 / graph v9. Writer and critic
semantic instructions, response schemas, model settings, call budgets and
revision/retry limits remain unchanged. The version increment identifies changed
response materialization and downstream repair packets.

Validate the boundary response and every assignment violation before accepting
the critique. A valid boundary overrun is consolidated with an assignment finding
only when both target the same current assignment anchor and cite the exact same
set of current-draft evidence handles. Handle order is immaterial. Resolved text
alone is insufficient: identical sentences at different positions are different
evidence. Subsets, partial overlaps and different anchors remain separate.

The consolidated issue remains blocking and forces REVISE. Retain the boundary
comparison, application repair policy, assignment explanation and assignment
repair together in that issue. Shared evidence does not establish semantic
equivalence; preserving both assessments avoids silently dropping a different
claim expressed through the same anchor and evidence.

Invalid handles, malformed fields, empty/inapplicable anchors and repeated
anchors within `assignment_violations` still fail response validation. A
no-overrun result does not clear independent assignments. Craft, viewpoint and
other hard gates remain independent. Raw response data and input artifacts are
not mutated; the existing boundary audit is unchanged.

The resulting canonical critique feeds the existing version-bound repair tests.
A consolidated issue creates one shared writer/critic repair test; a separate
missing turn still creates its own. No new role, call, provider dependency,
canonical artifact field, migration or API/client contract is introduced.

## Scope limits

This consolidates two routes in the same current review. It does not change
ADR 0013's historical repair-check materialization or deduplication across
review versions. Live testing shows that a newly reported current overrun and
an unmet historical repair can still produce two outcome issues. Their evidence
sets differ in the observed cases. Combining them requires a separate decision
about provenance and independent obligations; neither fuzzy wording matching nor
category-only suppression is introduced here.

The explicit unresolved endpoint remains a synthetic diagnostic plan. This
change does not alter real approved Blueprints or teach the integrator to
generate stronger scene endpoints.

## Verification

Thirteen new tests cover lossless consolidation, fallback anchors, reversed
handle order, distinct obligations/evidence, identical text at different handles,
invalid-route isolation, preserved craft/POV/turn blockers, and persisted shared
repair tests with replay. All twelve previous responses replay offline: three
duplicate pairs consolidate, and the other nine results are identical.

Full verification passed: Ruff, strict mypy over 172 files, 710 Python tests,
frontend formatting/lint/types, 11 frontend tests and production build. The first
full Python run encountered one SQLite-lock worker failure; the worker group and
then the complete suite passed unchanged on rerun. This transient is recorded,
not represented as a first-run clean gate.

The approved live test used three writer/critic pairs and an unchanged-draft
control. Two revisions pass; one retains ambiguous match/authenticity language
and requires revision. Two critic responses need one evidence-format repair each.
No second prose revision, continuity review or full-story run was performed.
See the [implementation and live report](../benchmark_reports/consolidated-overrun-writer-repair-2026-10-09.md).
Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.
