# Step 19 Local v10 canary — 2026-08-23

## Status

Diagnostic evidence only. This run is not part of a sealed formal benchmark.

The first six-case Local batch used a fresh plan pinned to scene-production
prompt v10. Five cases were production-runnable; OH-V01-006 retained its already
terminal Blueprint artifact-contract failure.

## Frozen execution

- Campaign ID: `f0190000-0000-4000-8000-000020260801`
- Plan SHA-256: `f985ae1b5976836952451a3011126c796e6e65773339f3b5b933bbfe5c24ee53`
- Scene-production graph/prompt: `2` / `10`
- Story Blueprint graph/prompt: `4` / `9`
- Local model: `gemma4:e4b`
- Selection: `--target local --batch-size 6 --batch-number 1`
- Retry policy: normal bounded workflow repair only; no operator
  `--retry-failed`

## Results

| Prompt | Result | Terminal evidence |
|---|---|---|
| OH-V01-001 | Production failed | Continuity remained blocking through the revision limit. The re-check cited prose that was not present in the revised draft and repeated its prior assessment despite changed evidence. |
| OH-V01-002 | Production failed | A blocking continuity finding omitted `recommended_resolution` after bounded Local repair. |
| OH-V01-003 | Production failed | Continuity remained blocking through the revision limit. The second revision included the requested “Flux Coefficient” and final thesis, but the re-check copied its stale assessment. |
| OH-V01-004 | Succeeded | 3,455 words, within target, all automated hard gates passed. |
| OH-V01-005 | Production failed | A blocking continuity finding omitted `recommended_resolution` after bounded Local repair. |
| OH-V01-006 | Expected pre-production failure | Preserved Blueprint `artifact_contract_failed`; Production did not run. |

The runnable Production completion rate was 1/5 (20%). Across the batch, 94 of
102 Production invocations succeeded and all used prompt v10. Initial continuity
calls succeeded 17 times and failed 4 times; re-checks succeeded 4 times and
failed once. The v9 initial/re-check schema regression did not recur.

## Diagnosis

The v10 split correctly made re-check-only fields unavailable during initial
continuity calls, but two independent contract gaps remained.

First, the provider-facing schema still exposed
`recommended_resolution: string | null` for every severity and exposed the
application-owned `blocks_approval` flag. Application validation derived the
flag and rejected an unresolved blocker without repair guidance only after
generation. An isolated `gemma4:e4b` grammar probe confirmed that Ollama accepts
severity-discriminated object branches, so this requirement can be guaranteed
before Local generation without forcing advisory findings to invent repairs.

Second, re-check validation required structured fields but did not prove that
`revised_evidence` was an exact excerpt from the revised draft or that an
assessment was fresh when its evidence changed. OH-V01-001 and OH-V01-003 both
received materially changed drafts, yet their second re-checks copied the prior
repair assessment byte-for-byte. OH-V01-001 also exposed a scoping leak: the
exact story-wide benchmark requirement “The new stroller remains central to the
plot.” had been copied into several non-final Scene Plan `required_elements`,
bypassing the deferred benchmark applicability packet.

Persisted prompt inputs contained the correct revised draft versions, so these
were output-contract and prompt-compilation defects rather than lineage or
routing defects.

## Prompt v11 response

Scene-production prompt contract v11:

- uses severity-discriminated initial and re-check finding schemas;
- requires a non-empty `recommended_resolution` in every error/blocking branch
  while allowing advisory branches to omit it;
- removes model-visible `blocks_approval`; the application remains its sole
  owner and derives it from severity;
- requires disposition, assessment, and non-empty revised evidence together in
  the re-check blocking branch;
- rejects every re-check evidence excerpt absent from the exact current draft;
- rejects a copied prior assessment when evidence changes and requires an
  explicit unchanged-passage explanation when evidence does not change;
- defers and redacts exact story-wide benchmark requirements copied into a
  non-final Scene Plan, while preserving all other immediate Scene Plan duties;
- leaves canonical persisted artifacts, bounded retries, Cloud behavior, and
  the audited Hybrid-only stagnation escalation unchanged.

Because the model-visible schemas, instructions, and continuity prompt view
changed, v11 is a new prompt contract. The completed v10 plan and report remain
immutable diagnostic evidence; the next canary requires a newly generated plan
pinned to production prompt `11`.
