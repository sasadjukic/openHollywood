# Step 19 Local v12 canary — 2026-08-25

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v12-canary-2026-08-25`
- Plan SHA-256: `b6e25db3c372676bb2973db6305aa360ddc06ee8c4c95189f273f570842be396`
- Production graph: `3`
- Production prompt contract: `12`
- Model profile: Local, `gemma4:e4b`
- Batch: size 6, number 1
- Run policy: no implicit retry of terminal cases

The campaign database was copied from the approved pre-production snapshot and
migrated from schema revision 0006 to 0007 before the plan was frozen.

## Outcome

OH-V01-001 through OH-V01-005 all reached Production and failed at continuity.
OH-V01-006 retained its earlier terminal Blueprint artifact-contract failure.
The five runnable cases therefore completed 0 of 5.

Across the 24 persisted continuity invocations, 9 succeeded and 15 failed:

- 10 failures rejected evidence that was not an exact candidate-draft excerpt.
- 3 failures rejected a reference absent from `canonical_source_catalog`.
- 2 failures reached the 8,000-token output ceiling and returned truncated JSON.

The terminal Production cause was exact evidence for OH-V01-001, OH-V01-003,
and OH-V01-005, and canonical source selection for OH-V01-002 and OH-V01-004.
The repair path sometimes corrected one field and then failed another, showing
that bounded retry was active but the model-facing allowed output space remained
too broad.

## Diagnosis

Prompt v12 correctly added initial-check enforcement that v11 lacked, exposing
previously accepted invalid evidence rather than demonstrating a general writing
regression. Its Local schema still allowed arbitrary non-empty strings for
evidence and canonical references, while application validation later required
exact draft substrings and exact catalog membership. Later-scene prompts also
presented the candidate and prior accepted drafts under one `input_artifacts`
collection even though only the candidate could provide valid evidence.

The source catalog contained broad raw IDs and paths but not the exact canonical
claim supported by each reference. Repeated entity IDs at multiple paths were
collapsed to the first path. This made precise provenance selection dependent on
model attention rather than the Local structured-output grammar.

## Prompt v13 response

Prompt contract v13 retains production graph v3 and makes the following
model-facing changes:

1. One explicitly labeled candidate draft is the sole evidence source; earlier
   accepted drafts are labeled context-only.
2. Candidate prose is exposed as deterministic exact-excerpt handles. Blocking
   findings select enum-constrained handles, which the application materializes
   into canonical `evidence` and `revised_evidence` strings.
3. Canonical provenance is a bounded claim catalog containing exact statements,
   immutable artifact versions, source paths, canonical owner IDs, and related
   IDs. `canonical_source_refs` selects only catalog handles.
4. Due requirement IDs and canonical World Rule IDs use call-specific enums.
   Requirement branches are absent when that basis has no due requirement.
5. Advisory findings cannot emit evidence. Application-owned report lineage is
   absent from model output, and findings are capped at eight.

The v12 campaign remains immutable evidence and must not be resumed under the
v13 build. The next canary requires a new campaign plan pinned to production
graph 3 and production prompt 13.
