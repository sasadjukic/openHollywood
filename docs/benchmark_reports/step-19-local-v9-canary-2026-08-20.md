# Step 19 Local v9 canary — 2026-08-20

## Status

Diagnostic evidence only. This run is not part of a sealed formal benchmark.

The first six-case Local batch used a fresh plan pinned to scene-production
prompt v9. Five cases were production-runnable; OH-V01-006 retained its already
terminal Blueprint artifact-contract failure.

## Frozen execution

- Campaign ID: `f0190000-0000-4000-8000-000020260801`
- Plan SHA-256: `83ffb10a8a1ca02f115ac0e4077e7a514cd8362fed9894790cc353a8293521b1`
- Scene-production graph/prompt: `2` / `9`
- Story Blueprint graph/prompt: `4` / `9`
- Local model: `gemma4:e4b`
- Selection: `--target local --batch-size 6 --batch-number 1`
- Retry policy: normal bounded workflow repair only; no operator
  `--retry-failed`

## Results

| Prompt | Result | Terminal evidence |
|---|---|---|
| OH-V01-001 | Production failed | Initial continuity output populated re-check-only fields after its bounded Local repair. |
| OH-V01-002 | Production failed | Initial continuity output populated re-check-only fields after its bounded Local repair. |
| OH-V01-003 | Production failed | Initial continuity output populated re-check-only fields after its bounded Local repair. |
| OH-V01-004 | Succeeded | 3,365 words, within target, all automated hard gates passed. |
| OH-V01-005 | Production failed | Initial continuity output populated re-check-only fields after its bounded Local repair. |
| OH-V01-006 | Expected pre-production failure | Preserved Blueprint `artifact_contract_failed`; Production did not run. |

The runnable Production completion rate was 1/5 (20%). The v9 diagnostic
envelope and Local repair packet worked as intended: eleven failed specialist
tasks received field-focused repair guidance and seven recovered. The four
terminal Production failures nevertheless converged on the same contract error:
initial continuity findings contained `recheck_disposition`,
`repair_assessment`, or `revised_evidence`.

## Diagnosis

The canonical `ContinuityFinding` schema served both initial checks and
re-checks. Its re-check fields were optional, so the Local structured-output
grammar still advertised them during initial calls. The initial prompt also
included the re-check analysis requirement. Application validation correctly
rejected those fields after generation, but retry guidance could only ask the
model to leave schema-visible fields empty. That wording could not make them
unavailable.

This is a contract-shape regression, not evidence that another retry or broader
fallback is needed.

## Prompt v10 response

Scene-production prompt contract v10:

- derives an explicit `initial_check` or `recheck` schema variant from immutable
  input lineage;
- removes `recheck_disposition`, `repair_assessment`, `revised_evidence`, and
  their enum definition from the initial-check schema;
- keeps those fields in the re-check schema and supplies re-check instructions
  only when a previous Continuity Report is an input;
- uses the same selected schema in the prompt and Local provider grammar;
- records `output_schema_variant` in invocation settings and prompt payloads for
  replay diagnostics;
- keeps the canonical persisted `ContinuityReport`, bounded Local repair,
  Cloud behavior, and Hybrid-only stagnation escalation unchanged.

Because model-visible schema and instructions changed, v10 is a new prompt
contract. The completed v9 plan and report remain immutable diagnostic evidence;
the next canary requires a newly generated plan pinned to production prompt
`10`.
