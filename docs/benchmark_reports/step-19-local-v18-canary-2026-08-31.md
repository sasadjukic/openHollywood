# Step 19 Local v18 canary — 2026-08-31

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v18-canary-2026-08-31`
- Production graph: `3`
- Production prompt contract: `18`
- Plan SHA-256: `1fa2bb6ecf0364e0dcd2a8041eda6fdf75174c7a82f68e382fa4950fdd957ca1`
- Batch: first Local canary batch, six cases

The report contains three successful production cases. OH-V01-002 completed at
3,308 words, OH-V01-003 at 3,799 words, and OH-V01-004 at 3,285 words. All
three passed the implemented completeness, ending, central-fact, placeholder,
and critic-note gates. OH-V01-006 retained its earlier terminal Blueprint
failure and never entered production.

V18 therefore completed three of five production-runnable cases, up from two
under v17. It accepted 18 scenes, up from 13, and eliminated revision-limit
failures. OH-V01-003 is the strongest semantic result: v17 stopped it after
continuity promoted intended dramatic and pacing choices to World Rule
blockers, while v18 accepted all five scenes and completed the story without a
writer revision.

The remaining two production cases failed during initial continuity checks:

- OH-V01-001 accepted three scenes, then both continuity attempts for scene 4
  ended with `missing_requirement_used_as_contradiction` because one
  contradiction reused a keyed missing requirement's repair text.
- OH-V01-005 accepted one scene. Its first continuity attempt for scene 2 ended
  with `world_rule_source_mismatch`; the Local retry then ended with
  `missing_requirement_used_as_contradiction`.

The final `report.json` retained only the last error, so the first OH-V01-005
failure remained visible only in SQLite. Across the five runnable cases, 76 of
83 production invocations succeeded, compared with 81 of 87 under v17. More
importantly, continuity structured-output success fell from 22 of 26 (84.6%)
to 18 of 25 (72.0%). The missing/contradiction exclusivity check fired six
times across four of five runnable cases; OH-V01-002 and OH-V01-003 recovered
on retry, while OH-V01-001 and OH-V01-005 did not.

SQLite integrity passed and no workflow or invocation remained active.

## What v18 established

V18 improved semantic routing. Its satisfaction modes, companion requirements,
and World Rule conflict policy converted OH-V01-003 from a false revision-limit
failure into a complete story, preserved both v17 successes, raised accepted
scene count, and produced no revision-limit terminal result. The remaining
failure surface is narrower and primarily structural.

The run also exposed two redundant model responsibilities:

1. a World Rule ID and its canonical source reference represented the same
   application-known fact, yet the model had to return both consistently; and
2. keyed requirement coverage already created the canonical missing blocker,
   while a second free-form contradiction could repeat its language.

The v18 exclusivity validator was over-broad: equality of either the normalized
summary or the recommended repair was enough to terminate the call. Sharing a
general repair sentence did not prove that an otherwise exact evidence-backed
contradiction represented the same defect. The Local repair packet named the
failed location but did not give an exact structural action or required key set.

## Implemented response: prompt v19, graph v3

Prompt contract v19 retains production graph v3 and the bounded call and
revision policies:

1. World Rule contradictions expose only enum-constrained `world_rule_ids` to
   the model. The application deterministically derives their exact canonical
   source references and validates the resulting provenance. Non-world
   contradictions still select exact canonical source handles.
2. Keyed missing blockers and free contradictions are consolidated in
   application code. An exact repeated summary-and-repair pair keeps only the
   keyed missing blocker; a shared summary or repair alone no longer terminates
   an independently evidence-backed contradiction.
3. Local repair policy v2 adds issue-specific directives and exact required
   requirement or prior-finding key sets without persisting or echoing the
   failed story response.
4. Failed benchmark results carry a backward-compatible ordered
   `failure_history` containing every safe persisted failed invocation: its ID,
   node, specialist, operation, schema variant, attempt ordinal, error code,
   exact redacted message, and provider finish reason. The terminal
   `error_message` remains the concise final cause.
5. Regressions cover the two v18 duplicate shapes, deterministic World Rule
   provenance, schema compactness, exact Local repair directives, and report
   serialization of attempt history.

Ruff and formatting pass over 133 files, strict mypy passes over 133 source
files, all 238 pytest tests pass, frontend formatting, lint, and type checking
pass, all 10 Vitest tests pass, and the production build succeeds.

The completed v18 campaign remains immutable diagnostic evidence. No v19
canary was started as part of this implementation change.
