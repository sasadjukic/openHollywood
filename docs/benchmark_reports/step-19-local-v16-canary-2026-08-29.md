# Step 19 Local v16 canary — 2026-08-29

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v16-canary-2026-08-29`
- Production graph: `3`
- Production prompt contract: `16`
- Plan SHA-256: `ca12c88e04137ec9a79eaebd51284c1dde71b02b252f518b3c8c9109a95f57ec`
- Batch: first Local canary batch, six cases

The report contains no successful case. OH-V01-006 retained its earlier terminal
Blueprint failure. All five production-runnable cases reached their final scene
before continuity stopped them:

- OH-V01-001 omitted `required_element_1` and `required_element_2` from the
  exhaustive requirement partition;
- OH-V01-002 assigned `still_blocking` to two findings whose IDs were new;
- OH-V01-003 produced a valid missing Scene Plan scalar obligation that the
  application incorrectly restricted to `required_element` kind;
- OH-V01-004 omitted `required_element_2` and `required_element_3`; and
- OH-V01-005 first omitted all three final requirements, then ended after a
  changed-evidence assessment rejection and another incomplete partition.

SQLite integrity passed and no workflow or invocation remained active. The five
runnable cases accepted 18 scenes. Of 103 production invocations, 91 succeeded;
21 of 33 continuity calls succeeded. No critic or token-budget failure occurred.
The largest continuity input was 12,558 tokens, safely below the unchanged
20,000-token ceiling.

## What v16 established

V16 was a substantial positive movement despite zero case completion. Compared
with v15, accepted scenes rose from 4 to 18, successful production calls from
45 to 91, and successful continuity calls from 12 to 21. The prior critic-score
and context-budget failures disappeared, and every runnable story reached its
planned final scene. The remaining terminal failures were concentrated in four
precise contract boundaries rather than general Local instability:

1. parallel coverage arrays permitted the model to omit schema-valid IDs;
2. the model still authored re-check identity and disposition;
3. application validation accepted only benchmark `required_element` IDs for a
   missing requirement, rejecting valid Scene Plan scalar IDs; and
4. required omissions could still be duplicated as `constraint`
   contradictions. One changed-evidence assessment heuristic also converted an
   otherwise usable re-check into a terminal structured-output failure.

## Implemented response: prompt v17, graph v3

Prompt contract v17 retains production graph v3 and the 20,000-token ceiling:

1. the application builds one due requirement catalog, deduplicating exact
   benchmark/Scene Plan overlaps, while forbidden shortcuts remain separate;
2. `requirement_coverage` is an object whose schema-required property names are
   the exact due IDs, making omission structurally invalid;
3. every keyed entry is explicitly `covered` or `missing`; the application
   materializes missing identity, category, lineage, and routing state for any
   due required ID, including Scene Plan scalar obligations;
4. contradiction category details are nested inside the contradiction basis,
   and `constraint` is unavailable there. Forbidden-shortcut category is
   application-owned;
5. model-facing blockers no longer author canonical finding IDs or
   `recheck_disposition`. A re-check may reference one exact prior finding ID;
   the application derives stable identity and `still_blocking` versus
   `newly_exposed`;
6. copied assessment after changed evidence is non-terminal and is persisted as
   content-free advisory telemetry; exact current-draft evidence remains a hard
   contract; and
7. regressions cover the terminal v16 shapes: exact keyed coverage, final-scene
   deduplication, Scene Plan scalar omissions, application-owned re-check state,
   forbidden omission-as-contradiction categories, and bounded compact schemas.

The completed v16 campaign is immutable diagnostic evidence and must not be
resumed under prompt v17. A future v17 canary requires a fresh plan pinned to
production graph v3 and prompt contract v17.

Two zero-cost Local `gemma4:e4b` grammar probes then exercised the generated v17
schemas without starting a workflow. The 5,933-byte initial schema returned all
three exact keyed coverage properties, including one structurally complete
missing entry. The 5,571-byte re-check schema returned one contradiction with
the exact `prior_finding_id`, revised-draft evidence handle, canonical-source
handle, nested non-world category, and repair assessment, without a
model-authored disposition. Ollama reported 487/230 input/output tokens for the
initial probe and 621/234 for the re-check probe.
