# Step 19 Local v15 canary — 2026-08-28

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v15-canary-2026-08-28`
- Production graph: `3`
- Production prompt contract: `15`
- Plan SHA-256: `96d9591d525e697d33fee666f0ce2ddab3a4c1e8f70cf0063c2ef13799cddd27`
- Batch: first Local canary batch, six cases

The report contains no successful case. OH-V01-006 retained its earlier terminal
Blueprint failure. The five production-runnable cases all reached continuity,
accepted four scenes between them, and then stopped:

- OH-V01-001: terminal continuity re-check rejection for `finding_006`;
- OH-V01-002: blocking continuity finding remained at the revision limit;
- OH-V01-003: terminal continuity re-check rejection for
  `continuity_finding_005`;
- OH-V01-004: continuity input used 20,163 tokens against the unchanged 20,000
  per-call ceiling; and
- OH-V01-005: terminal continuity re-check rejection for `finding_007` and
  `finding_008`.

SQLite integrity passed and no workflow or invocation remained active. Of 58
production specialist invocations, 45 succeeded and 13 failed. Eight failures
were continuity re-check contract rejections, one was the input-budget failure,
and four were critic outputs whose model-authored `overall_score` exceeded the
canonical upper bound; all four critic calls recovered on retry.

## What v15 established

V15 moved the system closer even though case completion remained zero. The
compact basis/category schema removed the v14 schema-size regression and the
explicit world-rule branch failures did not recur. More model calls completed,
four scenes became canonical, and the detailed terminal causes remained visible.
The remaining failures are therefore narrower contract-boundary defects rather
than a return of the earlier general structured-output instability.

The Local evidence shows three coupled causes:

1. Scene Plan omissions were still forced through the same finding union as
   affirmative contradictions. The model consequently cited unrelated canonical
   rules while describing absent time context, goals, turns, outcomes, physical
   state, or divergent theories.
2. The model declared `recheck_evidence_state`, while the application rejected
   an unchanged blocker for repeating an assessment even when its exact evidence
   had not changed. This converted a valid graph-v3 revision path into a schema
   retry and eventual terminal failure.
3. OH-V01-004's continuity context remained too broad. Its canonical source
   catalog alone was about 38.8 KB and 100 leaf entries, and full accepted prior
   drafts plus the previous report consumed additional context.

## Implemented response: prompt v16, graph v3

Prompt contract v16 retains production graph v3 and changes the model/application
boundary:

1. every due Scene Plan obligation receives a stable ID, category, and source
   field; the model must partition all required IDs exactly once between
   `covered_requirement_ids` and `missing_requirements`;
2. missing requirements are a separate top-level audit whose canonical finding
   ID, category, lineage, and blocking state are application-owned;
3. contradiction is restricted to affirmative current-draft conflicts against
   the bounded canonical source catalog, and Scene Plan obligation text is no
   longer available as a contradiction source;
4. re-check evidence change is derived from exact current and prior excerpts by
   the application. An unchanged blocker may keep an accurate assessment; only
   changed evidence paired with a copied assessment is rejected;
5. safe structured diagnostics use reason codes including
   `evidence_not_in_current_draft`, `copied_assessment_after_changed_evidence`,
   `missing_requirement_used_as_contradiction`, and
   `invalid_recheck_disposition`;
6. canonical claims are grouped instead of flattened by leaf, and continuity sees
   at most the immediately prior accepted scene ending rather than every full
   accepted draft; and
7. the critic no longer authors `overall_score`; the application deterministically
   computes the arithmetic mean of its bounded rubric scores.

The 20,000-token ceiling and production graph v3 remain unchanged so the next
canary measures the contract and context changes rather than a wider budget or
routing change. The completed v15 campaign is immutable diagnostic evidence and
must not be resumed under prompt v16.

The implementation passes Ruff and formatting over 133 files, strict mypy over
133 source files, all 226 Python tests, frontend formatting/lint/type checking,
all 10 Vitest tests, and the production build. No v16 canary was started.
