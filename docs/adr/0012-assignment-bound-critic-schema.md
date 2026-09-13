# ADR 0012: Bind critic choices to the approved scene assignment

- Status: Accepted
- Date: 2026-09-13

## Context

The v29 Cloud canary's OH-V01-009 critic exhausted response repair after
reporting a hard POV violation with no assigned viewpoint. OH-V01-008 recovered
the same error. The application already knew that this finding was inapplicable,
but the model-facing schema still offered the violation branch. Assignment
findings likewise offered anchors that were empty in the approved scene.

Step 2 of the production-improvement work removes these impossible choices,
without increasing prompt length, retries, budgets or revision limits.

## Decision

New requests use prompt contract v30 with production graph v7 unchanged.
Build each production critic schema from the exact current scene assignment:

- With no assigned viewpoint, point_of_view_check permits only the status-only
  aligned object. It cannot select the hard violation branch.
- With an explicit assignment or the existing single-character fallback,
  preserve the existing aligned/violation schema and narrative-policy guidance.
- Assignment violations may select only populated supported anchors.
  The separate POV route remains excluded from assignment_violations.
  Bound the number of entries to the applicable anchor count.

This is schema specialization, not a new literary rule or a silent correction of
a rejected response. Existing materialization still rejects inapplicable POV
findings, same-character allegations, empty anchors, duplicate anchors and
invalid evidence handles. A provider that ignores the schema can still fail
response validation; no failed response becomes a passing review automatically.

Do not restrict POV subject IDs to a closed approved-character roster merely to
exclude the assigned character. That would prevent findings about unexpected
characters and introduce an additional narrative restriction. The existing
same-character validator remains authoritative. Whether another character's
private access is authorized or contextually attributable inference remains a
model judgment under the unchanged policy; no keyword interpretation is added.

The production executor and isolated probe runner use the same specialization.
The generic schema remains available internally for template/boundary tests.
Both Local structured-output requests and Cloud prompt-embedded schemas receive
the specialization. Existing input catalogs, approved style, prompt prose and
canonical artifacts are unchanged. The schema is equal in size or shorter for
the same inputs; no explanatory prompt expansion or new model response fields.

## Compatibility and evidence

No SQL migration or API/client contract regeneration is needed.
Keep v29 requests, reports and canary snapshots immutable. New probes use new
diagnostic directories, preserve source artifact hashes/model/seed/per-call
budgets and identify v30 explicitly. Do not resume a historical canary under the
new contract or count a successful isolated review as a completed story.

Step 1's bounded failed-review evidence remains active. Schema specialization
does not relax response validation, manuscript hard gates, continuity review,
adjudication eligibility, writer revision behavior or mandatory Blueprint
approval. Repair criteria, critic adjudication and continuity-policy changes
remain later work.

## Verification

Offline controls cover explicit, unassigned and single-character fallback POV
on Local and Cloud; populated/empty assignment anchors; exact schema delivery;
unchanged source artifacts; no schema growth; rejection of impossible findings;
preservation of real POV, assignment and craft blockers; and a migrated SQLite
production run with replay and no duplicate calls. Existing failure-evidence
tests continue to cover rejected-review isolation and bounded recovery.

A focused OH-V01-009 Cloud probe uses the failed scene-2 critic invocation's
frozen inputs. Its result is recorded separately in the implementation tracker
and local diagnostic files; it is not a new full-story canary result.

