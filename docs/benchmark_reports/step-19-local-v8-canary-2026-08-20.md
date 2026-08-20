# Step 19 Local v8 canary — 2026-08-20

## Status

Diagnostic evidence only. This run is not part of a sealed formal benchmark.

The first six-case Local batch reused the approved August 1 pre-production
lineage through the isolated v8 canary plan. Five cases were production-runnable;
OH-V01-006 retained its already terminal Blueprint artifact-contract failure.

## Frozen execution

- Campaign ID: `f0190000-0000-4000-8000-000020260801`
- Plan SHA-256: `2e1a76a7fec7cec9b408e08c5e65632d0aabf62f7f93a4c1734734bb5298c788`
- Scene-production graph: `2`
- Scene-production prompt: `8`
- Story Blueprint graph/prompt: `4` / `9`
- Local model: `gemma4:e4b`
- Selection: `--target local --batch-size 6 --batch-number 1`
- Retry policy: normal bounded workflow repair only; no operator `--retry-failed`

The benchmark-critical preflight suite passed 57 tests. The harness exited zero,
the SQLite integrity check returned `ok`, and no workflow or invocation remained
active after report generation.

## Results

| Prompt | Result | Terminal evidence |
|---|---|---|
| OH-V01-001 | Production failed | Continuity structured-output validation exhausted both attempts; persisted detail collapsed to `$:ValueError`. |
| OH-V01-002 | Production failed | Continuity structured-output validation exhausted both attempts; persisted detail collapsed to `$:ValueError`. |
| OH-V01-003 | Production failed | Continuity recovered, then Story Bible repair emitted unknown character-state fact ID `c_006` and unknown location ID `the_utility_annex`. |
| OH-V01-004 | Succeeded | 3,579 words, within target, all automated hard gates passed. |
| OH-V01-005 | Succeeded | 3,621 words, within target, all automated hard gates passed. |
| OH-V01-006 | Expected pre-production failure | Preserved Blueprint `artifact_contract_failed`; Production did not run. |

The runnable Production completion rate was 2/5 (40%), compared with 1/5 (20%)
under the focused v7 regression and 4/5 (80%) under the earlier v1 Local run.
Prompt v8 therefore improved the canary and proved that Local can traverse the
new requirement-applicability contract through complete stories, but it did not
restore acceptable technical completion.

## Diagnosis

The two successful cases traversed final-scene continuity and Story Bible
updates, so v8's due-now/deferred requirement split is executable by the Local
model. The remaining failures exposed a separate observability and repair
problem:

1. ordinary application `ValueError` messages were intentionally omitted from
   persisted structured-output diagnostics;
2. the bounded retry therefore received only `$:ValueError`, even when the
   application validator had produced an actionable explanation;
3. Local retries had generic correction language but no role-specific rules for
   paired continuity re-check fields or canonical Story Bible identifiers.

No provider response body needs to be persisted or echoed to fix this problem.

## Prompt v9 response

Scene-production prompt contract v9:

- persists a redacted, bounded structured diagnostic envelope containing output
  field location, validation type, and actionable message;
- continues to retain only provider response hash, length, finish reason, and
  usage metadata—not the failed response body;
- passes the exact diagnostic envelope into the one bounded retry;
- adds a Local-deployment-only `local_schema_repair` packet with focus locations,
  common repair rules, and operation-specific continuity or Story Bible rules;
- does not attach Local repair guidance to Cloud retries;
- preserves the existing Hybrid-only cloud escalation for persisted continuity
  stagnation and removes Local guidance when that retry is routed to Cloud;
- remains fail-closed after the configured repair attempt.

Because model-visible instructions changed, v9 is a new prompt contract. The
completed v8 plan and report remain immutable diagnostic evidence; the next
canary requires a newly generated plan pinned to production prompt `9`.
