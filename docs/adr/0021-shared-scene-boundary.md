# ADR 0021: A shared boundary for the current scene

- Status: Accepted
- Date: 2026-10-08

## Context

The [scene-1 acceptance trace](../benchmark_reports/scene-one-acceptance-trace-2026-10-08.md)
found that OH-V01-002's writer completed handwriting verification assigned to
scene 2, while scene 1's approved outcome was the decision to verify. The critic
passed the scene with three 5/5 scores and praised the verification. Neither
role could see the next scene's assignment, although the global story arc still
described its events. A reported assignment violation already forces revision;
the missed detection occurred before that gate.

## Decision

New requests use prompt v37 with graph v9 unchanged. The existing writer and
critic receive the same `scene_boundary` on initial and revision calls:

- The exact current Scene Plan version and a reference to the existing
  assignment contract's outcome and exit state, without duplicating their text.
- Only the immediately following scene's ID, central turn and outcome, tied to
  the exact approved Blueprint version already in invocation input lineage.
- A short policy reserving distinct later work while allowing setup,
  foreshadowing, guesses, incidental follow-through and approved overlap or
  intentional repetition. The current approved plan governs overlap.

Select the next plan by scene number, independently of collection order. Do not
substitute a more distant scene or invent a reservation when none is supplied;
ambiguous next-scene matches fail. Valid production Blueprints already require
unique IDs and contiguous scene numbers. The final scene has no next reservation.

For these two roles, remove `story_arc` from the scoped Blueprint projection
and defer `proposed_ending` until the final scene. Keep current plan, current
beats, applicable world rules, characters, style, canonical Bible and exact
artifact identities. Stored Blueprint contents remain immutable. The final
scene retains its approved ending.

The writer must stop at the current endpoint. The critic must compare the
achieved ending with the boundary in its existing summary and report supported
overruns through `assignment_violations`, anchored to the current outcome or
turning point. Achieving the current obligation does not excuse performing the
next scene's distinct work. Evidence validation and blocking normalization remain
unchanged; high craft scores cannot clear a reported blocker.

No new agent, call, response field, retry, revision allowance or budget is added.
Continuity, Bible updates and critic adjudication retain their previous duties
and context projections. Canonical schemas, API/client contracts and persistence
are unchanged; no migration is needed. Provider selection remains neutral.

## Verification and limits

Eleven focused offline cases cover shared Local/Cloud context, revision identity,
source immutability, next-scene ordering, final-scene handling, ambiguous/missing
reservations, simulated overrun blocking despite perfect scores, permitted
foreshadowing, correctly assigned verification, intentional overlap, and a
persisted revision/replay with no extra specialist calls.

Nineteen matched historical request projections are 145–633 characters shorter
than v36. Output schemas are identical. These measurements are not a universal
token-size guarantee.

The five authorized Cloud probes all validated on their first call. The critic
passed proper stopping, foreshadowing and correctly assigned verification, and
blocked the missing-turn control. **It still passed the original overrun with
three 5/5 scores.** This change establishes shared context, but improved overrun
detection is not demonstrated. A summary instruction does not enforce an actual
boundary comparison; the next candidate is an explicit evidence-backed boundary
assessment within the same critic call. That further change is not implemented.

See the [implementation and probe report](../benchmark_reports/scene-boundary-v37-2026-10-08.md)
for provenance, costs and validation. No fresh writer generation or full-story
rerun occurred. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.
