# Step 19 Local v19 canary — 2026-09-01

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v19-canary-2026-09-01`
- Production graph: `3`
- Production prompt contract: `19`
- Plan SHA-256: `078e8e9caab6eeaa4a0790e7c84e8c8fe6026276f174df2ffac4361651f98bff`
- Batch: first Local canary batch, six cases

The run completed OH-V01-002 and OH-V01-003. OH-V01-001 and OH-V01-004
reached the continuity revision limit, OH-V01-005 ended on invalid JSON during
continuity, and OH-V01-006 retained its terminal Blueprint failure. V19
therefore completed two of five production-runnable cases, down from three of
five under v18, and accepted 15 scenes rather than 18.

V19 did improve call-level reliability. Across production-runnable cases, 95 of
98 production calls succeeded (96.9%), compared with 76 of 83 (91.6%) under
v18. Continuity improved from 18 of 25 successful calls (72.0%) to 26 of 29
(89.7%). The ordered, redacted `failure_history` added with v19 also preserved
failed-attempt details in `report.json` as intended. Those gains did not
translate into more completed stories because the remaining semantic blockers
survived valid retries and consumed the revision budget.

## What v19 exposed

The two revision-limit cases were false semantic blockers rather than missing
draft evidence:

- OH-V01-001's final draft explicitly placed the scene in early afternoon and
  described long shadows, yet continuity continued to block on time context.
- OH-V01-004's final draft explicitly used dusk light, yet continuity continued
  to block on the same class of requirement.

Their non-World-Rule contradiction provenance was not semantically constrained.
The selected canonical handles could point to unrelated material such as a
scene-one timeline entry or Scene Plan titles including “Debate in the Dust.”
The handles proved that a source existed, but not that the source expressed a
claim of the right category or shared the finding's entity/scene lineage.

OH-V01-005 exposed a second semantic ambiguity. A Scene Plan goal with
`satisfaction_mode=pursue` was judged as though achievement were mandatory,
even though pursuit was the contract and the planned outcome was separately
present. The shared `covered`/`missing` vocabulary did not force the model to
apply the satisfaction mode it had been given. Positive coverage also lacked an
exact evidence selection, making an incorrect negative judgment harder for the
application to distinguish from unsupported assertion.

V19's exact summary-and-repair consolidation was too dependent on free-form
wording. Two findings arising from the same requirement could evade
consolidation by paraphrasing. Rechecks also repeated complete prior findings,
keeping the Local grammar larger and asking the model to reproduce provenance
and identity already persisted by the application.

## Implemented response: prompt v20, graph v3

Prompt contract v20 retains production graph v3, the existing revision limit,
and all bounded call, persistence, and provider-neutral execution guarantees.
It changes the continuity contract in six focused ways:

1. Non-World-Rule contradictions select typed `canonical_claim_ids`. Each claim
   declares its allowed continuity categories and exact related entity/scene
   IDs. The application derives canonical source references and rejects
   category or lineage mismatch. Unstructured Scene Plan fields such as titles
   are not selectable contradiction claims.
2. Scene Plan requirement claims carry their exact requirement ID. When a keyed
   negative coverage result and a contradiction select the same requirement
   lineage, the application deterministically keeps the keyed missing blocker
   even when their summaries and repairs are worded differently.
3. Requirement coverage uses satisfaction-mode-specific statuses: for example,
   `attempted`/`not_attempted` for `pursue`, `achieved`/`not_achieved` for
   `achieve`, and `established`/`not_established` for `establish`. Every positive
   result must select exact current-draft evidence; the application owns the
   severity of every negative result.
4. Negative `entry_state` and `time_context` coverage is advisory. Only an
   independently evidenced affirmative contradiction can block on those
   dimensions, preventing omitted emphasis from overriding explicit text such
   as early-afternoon shadows or dusk light.
5. Rechecks return only a status, current assessment, and revised-draft evidence
   for each prior blocker. The application rehydrates identity, basis, category,
   provenance, and repair from the persisted report instead of requiring the
   Local model to reproduce the complete finding.
6. Local repair policy v3 supplies exact typed claim IDs, categories, and
   lineage for non-world provenance failures. Regressions cover the v19 time
   evidence, pursue semantics, irrelevant-title provenance, exact requirement
   lineage, compact recheck grammar, and advisory entry/time behavior.

Ruff and formatting pass over 125 files, strict mypy passes over 125 source
files, all 246 pytest tests pass, frontend formatting, lint, and type checking
pass, all 10 Vitest tests pass, and the production build succeeds.

The completed v19 campaign remains immutable diagnostic evidence. No v20
canary was started as part of this implementation change.
