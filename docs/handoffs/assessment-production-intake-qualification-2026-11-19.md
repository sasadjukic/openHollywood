# Supported production-review intake and completion qualification — 2026-11-19

## Outcome

Supported saved-review intake and the native completion primitives work together in
an explicitly authored local rehearsal. The positive v61 review/draft pair reaches
complete structural binding. Missing delivery stays incomplete; a missing terminal,
wrong selected version, mismatched request, altered source or invalid response supplies
no completion credit. A newer draft with identical content does not inherit the old
review's assessment.

**A separate saved-review completion adapter is justified and still required.** The
current runtime completion `SourcePin`, source collector and downstream presentation
contracts accept diagnostic-probe sources. They correctly refuse `saved_review`.
This qualification adds test fixtures and regressions, not a production admission
override or assessment attachment. No model reliability or story-quality claim follows.

Production prompts, runtime code, API/UI contracts and existing registrations remain
unchanged. Live calls remain **PAUSED**; the full workflow canary remains **ON HOLD**.

## Contract audit

| Boundary | Current behavior and finding |
| --- | --- |
| Saved production source | The existing read-only exporter admits a successful ordinary `scene_critic`, prompt v61, graph 9 and native audit schema 7, with matching run contract, exact critique/target/plan inputs, canonical hashes and original messages. |
| Review representation | Intake retains the saved normalized critique and native audit under `saved_normalized_and_audit`. It does not recover or invent raw critic response bytes. |
| Whole-claim intake | Explicit authored selection, interpretation, scope and work brief produce pending work. Full messages, draft, whole review, evidence registry, holds and unselected fields remain available. |
| Native assessment work | `scope_for_batch`, `bind_assessment_result` and `complete_work` can bind the unchanged work to an exact request and complete response. These functions do not authenticate a database, transport or provider on their own. |
| Runtime completion source | `expected_pin` rejects saved-review origin with `source_origin_not_qualified`; the existing publisher's manifest validator also rejects it before producing an output directory. |
| Compact presentation and transport | They carry the existing probe-specific `SourcePin`. Changing only the collector's origin check would not qualify a saved-review transport or publication path. |
| Inspector | Identity and eligibility remain separate. The six historical v33 reviews stay unsupported, with missing captured assessment. The seven diagnostic consumer works remain unassociated. |

Relevant code: [saved review exporter](../../apps/api/open_hollywood_api/services/review_evidence_export.py),
[intake adapter](../../apps/api/open_hollywood_api/services/assessment_intake.py),
[source pin](../../engine/open_hollywood_engine/evaluations/assessment_completion.py),
[completion collector](../../apps/api/open_hollywood_api/services/assessment_completion.py),
and [compact manifest](../../engine/open_hollywood_engine/models/assessment_openai_compact_manifest.py).
This preserves [ADR 0047](../adr/0047-read-only-ordinary-review-intake.md),
[ADR 0049](../adr/0049-source-bound-assessment-completion-publication.md) and
[ADR 0064](../adr/0064-read-only-artifact-provenance-inspector.md).

The original critic's stored success is not evidence that a later assessment was
delivered. Conversely, no later assessment delivery is needed merely to inventory
a compatible normalized critic review. These are different provenance obligations.

## Local fixture qualification

Added [the test-only bridge](../../tests/production_assessment_fixtures.py) and
[integration regressions](../../tests/api/test_production_assessment_qualification.py).
The source is a disposable migrated SQLite workspace populated by the existing
production executor fixture and fake gateway. No production database, provider client,
real worker or full-workflow canary is used. HTTP is blocked; socket connections are
blocked after Windows creates the event loop's local socket pair.

One review is admitted through the existing `saved_review` adapter. Its inventory has
**14 whole explanatory fields**; one authored structural placeholder is selected and
the other **13 remain unselected**. Five context documents and both original messages
remain intact. The selected field is the existing fixture's “Simulated fulfilled
obligation, not semantic evidence.” This is deliberately a binding fixture, not a new
semantic benchmark or defensible factual gold. Neither its `supported` response label
nor its authored declaration establishes that an actual story obligation was fulfilled.

The native context retains `canonical_review_id=null`. Original production-format
identity is carried separately in the fixture's source manifest: review invocation,
project, logical review/draft, exact versions/hashes, source collection, intake bundle,
work, request, batch and attempt. Source admission does not silently convert a derived
diagnostic work into a canonical assessment artifact.

Fixture setup owns the source/file pins. Each audit re-collects the source, checks the
local physical database identity, exact selected relationship, original intake members,
request bytes and manifest. Successful binding is followed by another source and
journal check. Source changes during binding are refused. No active-head fallback or
same-text substitution is allowed.

The fixture capture writes an exclusive intent, terminal and stop chain using the
existing flushed file writer. The audit verifies fixture-owned member hashes, intent
and request identity, exact raw final and terminal chain, then derives the native
receipt. A submitted success label or relabeled origin cannot authenticate itself.
The source and journal are not rewritten by audit or repeat audit.

Here **authentication means local fixture integrity against test-owned pins**. No
provider response, HTTP delivery, signature, real usage or elapsed-time observation
is asserted. The input is the existing full-context offline fixture document, explicitly
`provider_request=false` and `model_input=false`; it is not an OpenAI wire payload or
a new assessment prompt. The rehearsal is not a production-ready adapter or a general
concurrency/crash-recovery qualification.

| Control | Required result |
| --- | --- |
| Exact review and reviewed draft selections | Same complete, bound fixture result |
| No assessment delivery | No result; zero completed batches |
| Intent only | Missing terminal; one possibly-sent fixture attempt; no completion |
| Wrong project, logical artifact, version, hash or role | Refused for either selected side |
| Captured request containing a different draft version | Refused despite a well-formed response |
| Newer identical-content draft | Old selection remains valid; new version cannot reuse its completion |
| Changed prompt, target, absent native audit or v33 contract label | Intake/source refusal; no result promotion |
| Copied source database | Does not inherit the fixture registration |
| Changed intake, request, manifest, terminal or stop | Refused; submitted evidence does not define its own trust pin |
| Missing response slot, unknown citation, empty or duplicate-key response | Failed delivery; no completed subset |
| Length, refusal or transport-error terminal | Failed delivery; no success salvage |
| Source/request drift during binding | Refused after binding; no verified result returned |
| Fixture relabeled as observed model evidence | Refused |
| Saved-review source passed to current runtime publisher | Refused; no output directory |

The positive result leaves factual support, evidence adequacy, edit necessity and craft
unassessed, whole-relation credit false, and writer/production attachment permission
false. Native token fields remain null and unknown-usage count is one. Known-token
subtotals and synthetic elapsed time are zero because this is authored test data;
they are not measurements, billing estimates or missing real provider telemetry.

## Verification and preservation

**28 new tests and 267 existing tests pass: 295 distinct tests.** Ruff, formatting and
strict mypy pass on **320 tracked Python files**, plus the private preservation helper
(321 total). The applicable suites cover the new source-to-completion rehearsal plus existing
review evidence, saved/probe intake, native result/work and completion publication.
No frontend, persisted schema, production runtime or generated contracts changed;
frontend builds and migrations are not applicable. Full-repository pytest is not run.

The production database, WAL and SHM remain byte- and mtime-identical; preservation
uses file hashing, not a SQLite connection. All earlier source artifacts, registrations,
prompts and journals are retained. Source/code preservation covers **3,620** earlier
sealed members, **64** separate authored controls, **636** archive pins, **1,788** source
files/mtimes, three closed journals, **88** consumer files, **23** association export
files and **864/867** baseline files outside the three intended documentation updates.
All fourteen issue bodies and posted URLs remain intact. Earlier evidence is neither
edited nor resealed.

Private root: `data/diagnostics/assessment-production-intake-qualification-2026-11-19/`.
The verified positive workspace and its exact intake, request, source manifest,
intent-only and complete journals are retained under `pytest-verified/`.
`qualification.json` in its positive test directory records the complete native result
and missing-delivery controls. `checks.json`, source snapshots, database pins,
preservation results and the new acceptance seal summarize the final evidence.
Earlier development-run folders are retained separately and are not final pass evidence.

## Recommended next step

Implement a **narrow, separately versioned read-only saved-review completion source
adapter**, initially with authored/injected fixtures only:

1. Bind an explicit supported review to its registered workspace/capture, original
   review/draft versions and source closure. Reuse the existing read-only source checks;
   retain normalized-critique/audit origin and raw-response availability accurately.
2. Produce a saved-review source pin and verification receipt that bind the unchanged
   intake, work, scope and briefs. Preserve existing probe/authored contracts and their
   saved bytes; do not relabel saved reviews as probes or broaden the historical v33
   registration. Recheck sources before completion/publication.
3. Qualify that new pin through local preparation, terminal auditing and read-only
   completion publication with these positive, missing-terminal and wrong-version
   controls. Preserve origin, unknown usage and whole-work coverage. Keep model judgments
   distinct from application-verified identity and citation facts.

Real provider mapping and any live smoke should follow only after that adapter passes
local checks and a separate plan is frozen. There is no inference budget or live approval
request in this task. Inspector assessment attachment and writer routing remain held.

This moves the working components toward usable production assessment without treating
structural success as necessary editing or improved prose. Feel, flow, character and
story-breaking effects remain separate quality targets. No extra mandatory human
checkpoint is introduced. CW-007/CW-013 remain open; CW-014 remains unqualified.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; prompts unchanged; live calls PAUSED;
full workflow canary ON HOLD.**
