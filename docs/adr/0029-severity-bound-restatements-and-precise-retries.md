# ADR 0029: Severity-bound restatements and precise structural retries

- Status: Accepted
- Date: 2026-10-10
- Amends: ADR 0028's restatement schema and ADR 0008's structural retry projection.

## Context

The v43 unchanged-draft control failed both attempts. Its generic major tension
issue supplied an invalid assignment reference. Behind that failure, the outcome
repair omitted the boundary route of its consolidated finding, and the retry
changed the tension category's spelling. The schema allowed nonblocking issues
to select non-null references even though materialization rejected them.

Critic retry input intentionally omitted rejected values and failure prose to
keep reviewer mistakes from becoming manuscript defects. It consequently reduced
all failures to locations and generic instructions, losing the structural facts
needed to repair these links within the existing single retry.

## Decision

New executions use production contract v44 / graph v9. The generic issue schema
adds severity alternatives without duplicating the full issue definition:

- Blocking issues may use null for independent craft or a valid explicit
  reference for a repetition of a reported blocking assignment finding.
- Note, minor and major issues require a null restatement reference.

Runtime validation enforces the same rule before evidence materialization. It
does not promote severity, clear references or change categories automatically.

After a critique fails materialization, an application diagnostic pass may add
independently discoverable link failures to the same rejected response. It reuses
the existing viewpoint, assignment, boundary and consolidation validators on a
diagnostic projection with an empty craft list. That projection is never returned
as a critique. Craft metadata is examined only for structural references and
compatibility, not for the truth of its allegation.

The existing bounded failure record can retain a small `repair_hint` containing
the candidate version and typed structural facts. The critic retry packet binds
it again to its exact current draft and original repair tests. Known fields can
provide allowed references, exact original category/severity, all routes of a
selected consolidated finding, missing routes and competing original owners.
Categories and severities of original repairs are read from those immutable
tests, not copied from a rejected allegation.

Retry policy 11 applies to the scene critic. Other specialists keep policy 10.
Rejected descriptions, recommendations, assessment text and arbitrary diagnostic
fields remain excluded. These facts concern review structure, never manuscript
truth. The retry cannot infer a story defect from them, escalate a craft issue to
make a link legal, or rename a different defect to fit an original repair.
Compatible category/severity is necessary but does not establish the same claim.

The diagnostic pass never makes a rejected response valid. Existing validation,
ownership, canonical materialization and retry/revision limits remain. Valid
responses skip it entirely. Hints are limited to 500 serialized characters each
and the existing 12-issue limit; craft inspection is capped at 64 entries and
reference lists at 16. Oversized, malformed, stale or inapplicable hints fall back
to location-only guidance. Unvalidated hard routes do not produce hints. No full
rejected response is replayed to the model.

No role, model call allowance, canonical field, migration, dependency or public
API change is introduced. Writer and critic system instructions and story context
remain unchanged. Local and cloud schema delivery use their existing paths.

## Qualification

Local tests cover both deployment modes, severity choices, exact/null references,
category mismatch, missing consolidated routes, competing owners, stale/malformed
hints, bounded redaction and a persisted retry without a new draft or writer call.
The two real v43 failures stay rejected and produce two and three precise retry
directives respectively. The four valid v43 results materialize identically.

The user authorized and completed the same five diagnostic cases using eight
calls. Initial requests grow by 162 characters each, solely for the severity
branches. Four cases produced valid reviews. Both missing boundary links were
corrected on retry, but the unchanged draft's retry introduced an invalid major
restatement reference and remained rejected. The ambiguous revision recovered
structurally while retaining a generic pacing duplicate, demonstrating that null
does not establish semantic independence. Reviewer reliability and narrative
correctness remain unqualified. Step 19 remains IN PROGRESS.

See the [implementation and diagnostic report](../benchmark_reports/restatement-retries-v44-2026-10-10.md).
