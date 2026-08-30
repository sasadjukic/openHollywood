# Step 19 Local v17 canary — 2026-08-30

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v17-canary-2026-08-30`
- Production graph: `3`
- Production prompt contract: `17`
- Plan SHA-256: `00332d402e1bf56ec305757dda3d1c018aa2bb16faed10be5773364e9ea34ad9`
- Batch: first Local canary batch, six cases

The report contains two successful cases. OH-V01-002 completed at 3,713 words
and OH-V01-004 completed at 3,185 words; both passed the automated completeness,
ending, central-fact, placeholder, and critic-note gates. OH-V01-006 retained its
earlier terminal Blueprint failure and never entered production. The other three
production-runnable cases stopped in continuity:

- OH-V01-001 failed after a first re-check assigned positional
  `continuity_new_002` through `continuity_new_008` identities and the following
  re-check generated the same positions as newly exposed. Application validation
  then correctly recognized the persisted IDs as prior blockers but rejected the
  application-derived `newly_exposed` disposition. One earlier attempt also used
  the same prior finding reference more than once.
- OH-V01-003 reached the revision limit after continuity treated a sensory
  variation and an intentionally pattern-breaking sound as World Rule blockers.
  Its own assessment called the sound the intended narrative pivot and said its
  concern was abruptness. The revised drafts passed critic review, so the
  remaining objections belonged to pacing/critique rather than canonical
  continuity.
- OH-V01-005 reached the revision limit after continuity required the characters
  to achieve their Scene Plan goal of finding conclusive evidence. The same Scene
  Plan's outcome and exit state required the argument to become personal and end
  without resolution, while the cited `evidence_weighting` rule made physical
  evidence neutral. The writer made the planned deadlock explicit and the critic
  passed the revisions, but continuity repeated both a World Rule contradiction
  and a missing-goal finding.

SQLite integrity passed and no workflow or invocation remained active. Across
the five production-runnable cases, 81 of 87 production invocations succeeded,
including 22 of 26 continuity calls. This improved on v16's 91 of 103 production
calls and 21 of 33 continuity calls by rate: 93.1% versus 88.3% overall and 84.6%
versus 63.6% for continuity. All v16 requirement-partition failures disappeared.
The v17 run accepted 13 scenes, fewer than v16's 18 because two false semantic
blockers stopped in their first or second scene, but v17 was the first recent
Local canary to complete production cases.

## What v17 established

V17 validated the keyed requirement-coverage direction. Exact due IDs were no
longer omitted, valid Scene Plan scalar obligations were accepted, and copied
changed-evidence assessments became advisory telemetry rather than terminal
schema errors. The remaining failures were narrower:

1. positional application IDs were not unique across consecutive re-checks;
2. every Scene Plan scalar used one generic performance interpretation, causing
   a character goal to be mistaken for a guaranteed scene outcome;
3. a World Rule branch could cite a location claim while separately naming an
   unrelated rule, and its semantic fields did not distinguish a logical rule
   breach from a critic concern; and
4. one absent obligation could still be reported twice as both missing coverage
   and an affirmative contradiction.

## Implemented response: prompt v18, graph v3

Prompt contract v18 retains production graph v3 and the bounded revision policy:

1. re-check output separates a schema-required `prior_finding_rechecks` object
   from `new_findings`. Every exact prior non-requirement blocker is classified
   once as resolved or still blocking; prior IDs are unavailable to new findings;
2. newly exposed findings receive revision-scoped application IDs, preventing a
   later re-check from colliding with a prior positional identity;
3. requirement catalog policy v2 gives each Scene Plan and benchmark obligation
   an explicit `satisfaction_mode` and companion IDs. A character goal is
   satisfied by meaningful pursuit, while outcome, turning point, and exit-state
   entries retain their own achievement or establishment semantics;
4. World Rule blockers must choose an explicit prohibition/required-condition
   violation kind, explain the direct logical conflict, and cite the canonical
   source belonging to every declared rule ID. Pacing, abruptness, atmosphere
   variation, and dramatic framing are explicitly critic concerns;
5. an exact missing summary or repair cannot be duplicated as a contradiction;
   and
6. regressions reproduce consecutive re-check identity, exhaustive prior-key
   coverage, pursued-but-unachieved goals, exact World Rule provenance, and
   duplicate requirement bases.

The completed v17 campaign remains immutable diagnostic evidence. A future v18
canary requires a fresh plan pinned to production graph v3 and prompt contract
v18.
