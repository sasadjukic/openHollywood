# Step 19 Local production v7 regression diagnostic

Date: 2026-08-19

This diagnostic compares the first six Local cases from the approved August 1
pre-production snapshot under scene-production prompt contracts v1 and v7. It
is engineering evidence only and must not be sealed as final benchmark
evidence.

## Outcome comparison

| Prompt | v1 outcome | v7 outcome | v7 terminal cause |
| --- | --- | --- | --- |
| `OH-V01-001` | Failed | Failed | Continuity revision exhaustion/stagnation |
| `OH-V01-002` | Succeeded | Failed | Repeated blocking story-wide requirements in Scene 1 |
| `OH-V01-003` | Succeeded | Failed | Repeated blocking story-wide requirements in Scene 2 |
| `OH-V01-004` | Succeeded | Succeeded | Completed at 3,406 words |
| `OH-V01-005` | Succeeded | Failed | Blocking story-wide requirements and revision exhaustion |
| `OH-V01-006` | Blueprint failure | Blueprint failure | No production run |

Among runnable production cases, completion fell from 4 of 5 under v1 to 1 of
5 under v7. The model identifier, run seed, temperature, top-p, and thinking
settings remained unchanged. The production prompt contract and exact prompt
hashes changed.

## Persisted evidence

The v1 Local successes emitted no blocking continuity findings. Under v7:

- `OH-V01-002` Scene 1 received four blockers requiring the story's final card
  origin, ten-year causal resolution, and irreversible choice even though its
  approved Scene Plan intentionally ends with initial resistance.
- `OH-V01-003` Scene 2 was blocked for not resolving the displacement's final
  cause and consequence even though its Scene Plan calls only for preliminary
  structural data.
- `OH-V01-005` Scene 1 was blocked for not resolving the dead man's identity
  and the father's fate even though its Scene Plan intentionally ends in a
  sibling stalemate.

The v7 prompt described story-wide scope in prose but continued to expose the
full frozen benchmark constraints to every scene. The smaller Local model
treated those constraints as immediate gates. Once revision began, the v7
stagnation validator inferred progress from changed summary/evidence/resolution
text even though the artifact schema had no explicit repair-assessment field.
Hybrid could recover through its bounded cloud retry; Local correctly remained
fail-closed.

## v8 corrective contract

Scene-production prompt v8 keeps the useful v7 lineage, feedback, safe retry,
and Hybrid fallback behavior while changing the shared continuity contract:

1. Non-final continuity calls receive only opaque IDs for deferred story-wide
   benchmark requirements; their exact text is intentionally omitted.
2. The final scene receives the exact required-element and forbidden-shortcut
   text as due-now gates against the completed story.
3. Exact Scene Plan requirements remain due in their own scene.
4. A forbidden final explanation is distinguished from a character temporarily
   considering and rejecting that explanation.
5. Re-check blockers carry typed `recheck_disposition`, `repair_assessment`, and
   `revised_evidence` fields. Reusing an exact quotation is valid when the
   assessment states that the writer left the offending passage unchanged.
6. Local remains fail-closed; only Hybrid may use the existing persisted,
   bounded continuity-stagnation escalation.

The v7 database and report remain preserved under
`data/benchmarks/v0.1/formal-2026-08-19/`.

The unexecuted v8 canary is prepared under
`data/benchmarks/v0.1/v8-canary-2026-08-19/`. Its database is schema 0007 with
zero production runs, and its 48-case frozen plan has canonical digest
`2e1a76a7fec7cec9b408e08c5e65632d0aabf62f7f93a4c1734734bb5298c788`.
No report exists because no v8 model execution has started.
