# Step 19 Local v13 canary — 2026-08-25

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v13-canary-2026-08-25`
- Plan SHA-256: `323c3a91850be72a4c09ef6911e39ccb59c0f27abfc3abf1441270a164c01a98`
- Production graph: `3`
- Production prompt contract: `13`
- Model profile: Local, `gemma4:e4b`
- Batch: size 6, number 1
- Run policy: no implicit retry of terminal cases

## Outcome

OH-V01-001 through OH-V01-005 all reached Production and failed at continuity.
OH-V01-006 retained its earlier terminal Blueprint artifact-contract failure.
The five runnable cases therefore completed 0 of 5.

Prompt v13 eliminated every v12 failure involving non-exact draft evidence,
invalid canonical-source handles, invalid due-requirement IDs, or length-
truncated JSON. Across the 13 failed continuity calls, the persisted diagnostics
were:

- 6 missing `companion_rule_assessment` values;
- 3 missing or invalid `world_rule_ids` values;
- 2 invalid `condition_explicitly_authorized` values;
- 1 use of world-rule analysis fields on a non-world finding; and
- 1 continuity re-check stagnation failure.

Writer and critic calls were otherwise productive: all 14 critic calls
succeeded, 14 of 15 writer calls succeeded, and the two attempted Story Bible
updates succeeded. This isolates the canary's terminal problem to the
continuity contract rather than to general Local prose generation.

## Diagnosis

Prompt v13 constrained evidence and provenance selections successfully, but a
single schema branch still represented both world-rule and non-world blockers
for each basis. The canonical artifact validator required all three world-rule
analysis fields when `category=world_rule` and rejected those same fields for
every other category, while the model-facing grammar left them optional in the
shared branch. The Local model therefore remained able to produce combinations
that the durable boundary had to reject.

The benchmark adapter also read `WorkflowRun.error_message`, which contained
the bounded retry wrapper, even though each failed `AgentInvocation` already
held the exact redacted field-level validation diagnostic. Consequently the
immutable v13 `report.json` says only that structured output was invalid while
SQLite preserves the actionable cause.

## Prompt v14 response

Prompt contract v14 retains production graph v3 and makes two focused changes:

1. Contradiction, missing-requirement, and forbidden-shortcut blockers each
   have separate world-rule and non-world branches in both the initial-check and
   re-check schemas.
2. A world-rule branch fixes `category` to `world_rule` and requires one or more
   call-valid `world_rule_ids`, a non-empty `companion_rule_assessment`, and
   `condition_explicitly_authorized=false`. Its paired non-world branch excludes
   `world_rule` from the category enum and removes all world-rule fields.
3. Advisory branches remain non-blocking and cannot emit world-rule analysis.
4. Benchmark failure assembly prefers the latest failed production invocation's
   redacted diagnostic, including its exact validation location and message,
   then falls back to the workflow-level cause for failures without a failed
   model invocation.

The v13 campaign remains immutable evidence and must not be resumed under the
v14 build. The next canary requires a new campaign plan pinned to production
graph 3 and production prompt 14.
