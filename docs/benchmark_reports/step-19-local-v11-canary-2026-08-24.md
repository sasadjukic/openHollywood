# Step 19 Local v11 canary — 2026-08-24

## Status

Diagnostic evidence only. This run is not part of a sealed formal benchmark.

The first six-case Local batch used a fresh plan pinned to scene-production
prompt v11. Five cases were production-runnable; OH-V01-006 retained its already
terminal Blueprint artifact-contract failure.

## Frozen execution

- Campaign ID: `f0190000-0000-4000-8000-000020260801`
- Plan SHA-256: `a71a83a87092f7d095b96918b5dc8503f90508e45d524c5220ab7ccdc6400489`
- Scene-production graph/prompt: `2` / `11`
- Story Blueprint graph/prompt: `4` / `9`
- Local model: `gemma4:e4b`
- Selection: `--target local --batch-size 6 --batch-number 1`
- Retry policy: normal bounded workflow repair only; no operator
  `--retry-failed`

## Results

| Prompt | Result | Terminal evidence |
|---|---|---|
| OH-V01-001 | Production failed | Continuity remained blocking through the revision limit after treating the pristine stroller as a decay-rule violation, although canonical rule `stroller_anchor` explicitly authorizes its unnatural cleanliness. |
| OH-V01-002 | Production failed | Final-scene continuity reported six blockers by copying requirement text as draft evidence. The terminal re-check exhausted structured repair because those quotations were absent from the current draft. |
| OH-V01-003 | Succeeded | 4,061 words; all automated hard gates passed. |
| OH-V01-004 | Succeeded | 2,992 words; all automated hard gates passed. |
| OH-V01-005 | Production failed | Critic-only revisions consumed the full revision allowance before the first continuity call. That call then treated evidence explicitly permitted by canonical `evidence_weighting` as a blocking world-rule violation. |
| OH-V01-006 | Expected pre-production failure | Preserved Blueprint `artifact_contract_failed`; Production did not run. |

The runnable Production completion rate was 2/5 (40%). Across the batch, 86 of
90 Production invocations succeeded. All 17 initial continuity calls produced
valid structured output. The initial/re-check schema split and blocking
resolution guarantee therefore held, but semantic basis and revision-routing
gaps remained.

## Diagnosis

The three Production failures exposed three related defects.

First, one generic continuity-finding shape was being used for contradictions,
missing requirements, and forbidden shortcuts. This let OH-V01-002 copy the
requirement text itself into `evidence`, inventing an apparent current-draft
quotation for content that was actually absent. It also treated all three
forbidden shortcuts as violations even though the completed draft did not adopt
them.

Second, world-rule blockers did not have to name every exact rule involved or
evaluate companion rules and exceptions. OH-V01-001 ignored the explicit
`stroller_anchor` authorization, and OH-V01-005 ignored the ambiguity permitted
by `evidence_weighting`.

Third, exact draft-evidence validation applied only to re-check evidence. The
invalid initial findings therefore became revision instructions before the
boundary could reject them. Separately, the graph routed directly from a
non-passing critic back to the writer, so OH-V01-005 reached revision two before
continuity evaluated any candidate.

The persisted `WorkflowRun.error_message` values already contained the safe
underlying causes, but the benchmark adapter replaced every thrown Production
failure with the same generic message in `report.json`.

## Prompt v12 and production graph v3 response

Prompt contract v12 and production graph v3:

- split blocking continuity output into `contradiction`,
  `missing_requirement`, and `forbidden_shortcut_violation` branches;
- require contradictions to quote exact current-draft evidence and cite an
  exact reference from a deterministic canonical-source catalog;
- require missing requirements to cite one exact due-now requirement ID and a
  coverage assessment while making draft evidence unavailable;
- require forbidden-shortcut violations to cite one exact due-now forbidden ID
  and an exact violating draft excerpt; absence produces no finding;
- require world-rule findings to identify exact canonical rule IDs, assess
  companion rules and exceptions, and declare whether the condition is
  explicitly authorized; an authorized or unevaluated condition cannot block;
- validate exact evidence on initial continuity calls as well as re-checks;
- run critic and continuity on every candidate, consolidate both outcomes, and
  increment the revision counter at most once after both have completed;
- preserve the existing per-attempt writer/critic/continuity budget envelope;
- surface the redacted persisted Production node and failure cause through the
  benchmark error recorded in `report.json`.

Because both the model-visible contract and durable routing changed, the next
canary requires a new plan pinned to scene-production graph `3` and prompt `12`.
The completed v11 plan and report remain immutable diagnostic evidence.
