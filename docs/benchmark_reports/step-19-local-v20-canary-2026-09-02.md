# Step 19 Local v20 canary — 2026-09-02

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v20-canary-2026-09-02`
- Production graph: `3`
- Production prompt contract: `20`
- Plan SHA-256: `3c53dce80965bf61ec56effb7348b8faa9d62532a01bb9dfa5193ddf8e644935`
- Batch: first Local canary batch, six cases

No production-runnable case completed. OH-V01-001 and OH-V01-003 ended on
structured continuity validation, OH-V01-002, OH-V01-004, and OH-V01-005
reached the continuity revision limit, and OH-V01-006 retained its terminal
Blueprint failure. V20 therefore completed zero of five production-runnable
cases, down from two under v19 and three under v18. Accepted scenes fell to two,
from 15 under v19 and 18 under v18.

Call-level reliability also regressed. V20 completed 48 of 53 production calls
and 14 of 19 continuity calls. V19 completed 95 of 98 production calls and 26
of 29 continuity calls; v18 completed 76 of 83 and 18 of 25 respectively. The
ordered `failure_history` continued to expose each safe underlying structured
output failure in `report.json`, including the provider finish reason, schema
variant, specialist, operation, node, and invocation ID.

## What v20 exposed

V20's typed source and satisfaction contracts were semantically stricter but
too large and too easy for the Local model to misuse. The successful initial
continuity requests carried roughly 21.3 KB of schema and successful rechecks
roughly 27.8 KB, compared with approximately 9.7 KB and 10.7 KB under v19. The
largest failed recheck response reached 45,204 characters and ended with
`finish_reason=length`. Adding more type vocabulary improved theoretical
precision while reducing practical grammar reliability.

Scene Plan requirements were represented twice: once in the keyed requirement
coverage partition and again as selectable non-World-Rule contradiction claims.
That let requirement gaps be laundered into contradiction findings with a
canonical-looking handle. OH-V01-002 selected an unrelated canonical source for
an entry/time complaint despite explicit temporal evidence. OH-V01-004 used
character claims to support a complaint about the Scene Plan goal. OH-V01-005
produced three blocking entry-state contradictions plus an advisory coverage
finding for the same obligation. The application could validate the selected
IDs structurally, but it could not prevent the model from making the wrong
semantic comparison.

The satisfaction-mode-specific status vocabulary multiplied schema branches
without producing a useful distinction. For continuity, the durable semantic
question is whether an obligation is `met`, `partial`, or `absent`. Partial
coverage and qualitative Scene Plan dimensions should remain visible without
spending a revision. Only an absent hard obligation should block. Exact positive
or partial evidence and an explicit negative search result make those outcomes
auditable without inventing an excerpt for absence.

V20 also continued asking the model to author deterministic metadata such as
category, source references, lineage, and IDs. This created category and lineage
validation failures after otherwise parseable output. Rechecks could rephrase or
renumber the same semantic issue, causing an already-persisted blocker to return
as a nominally new finding.

## Implemented response: prompt v21, graph v3

Prompt contract v21 retains production graph v3, the existing revision limit,
and the bounded writer/critic/continuity call plan. It narrows the continuity
boundary in seven focused ways:

1. Scene Plan obligations are available only in the exhaustive keyed coverage
   partition. They cannot be selected as contradiction claims.
2. Coverage uses one shared `met`/`partial`/`absent` schema. `met` and `partial`
   select exact current-draft evidence; `absent` reports either the closest
   selected passages or that no related passage exists, without fabricating an
   excerpt.
3. Partial coverage is advisory. Absence blocks only for an application-owned
   hard requirement. The six qualitative Scene Plan scalar dimensions—entry
   state, time context, purpose, goal, conflict, and exit state—remain advisory
   and qualitative judgments stay with the critic.
4. Non-World-Rule contradictions select exactly one compact, self-describing
   canonical claim ID. World Rule findings select rule IDs from a separate
   compact catalog. The application derives category, canonical source refs,
   entity/scene lineage, and other deterministic metadata.
5. The prompt no longer repeats the full canonical source catalog, output
   requirements, or repair instructions. Local repair policy v4 sends only the
   failed path, exact allowed keys or enums, and a narrow correction action.
6. Findings receive stable semantic IDs derived from their rule, claim, or
   requirement identity. Semantically repeated findings consolidate even when
   the Local model changes wording or reports a prior blocker as new.
7. Persisted findings retain `coverage_status` and exact `coverage_evidence`, so
   partial and absent judgments remain inspectable after application
   materialization.

Ruff and formatting pass over 133 files, strict mypy passes over 85 source
files, all 252 pytest tests pass, frontend formatting, lint, and type checking
pass, all 10 Vitest tests pass, and the production build succeeds.

The completed v20 campaign remains immutable diagnostic evidence. No v21 canary
was started as part of this implementation change.
