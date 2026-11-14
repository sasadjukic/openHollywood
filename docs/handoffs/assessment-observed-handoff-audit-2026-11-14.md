# Observed assessment regressions and downstream export audit

Date: 2026-11-14

Status: local regression preservation and bounded downstream audit **COMPLETE**.
**Zero new provider, input-count, metadata or generation calls.** Production
prompts unchanged; live calls **PAUSED**; full workflow canary **ON HOLD**.

The four [observed compact-smoke deliveries](assessment-openai-compact-smoke-results-2026-11-14.md)
replay exactly through the native binder, completion validator and literal renderers.
The supported smoke audit already publishes their complete observed records. The
remaining integration boundary is admission of those records into the general
read-only completion component: its publisher accepts authored submissions only.
A bare native receipt or view cannot replace the observed terminal envelope.

## Preserved regressions

Freeze the same N06/N07/N10/N11 selection before replay. Preserve original request
preparations, full prose/context, 19 journal files, exact finals/receipts, observed
usage, source versions and the prior manual inspection. No response is repaired,
relabeled as authored or resubmitted through a mock transport. Negative variants
are explicitly local authored mutations, distinct from the four real deliveries.

| Work | Active claims | Recorded labels | Held fields | Unselected fields |
| --- | --- | --- | ---: | ---: |
| N06 | Q001 | Supported | 1 | 10 |
| N07 | Q004, Q005 | Supported, uncertain | 0 | 10 |
| N10 | Q003, Q007 | Supported, uncertain | 2 | 10 |
| N11 | Q003 | Supported | 1 | 11 |

All **six active claims, 51 original fields, four holds, 41 unselected fields and
3,658 evidence locations** remain intact. Exact replay preserves the original
judgments and explanations; it is not another model repeat or a new semantic score.
The earlier source inspection remains separate from software acceptance and human
story-quality judgment.

Private root: `data/diagnostics/assessment-observed-handoff-2026-11-14/`.

- `plan.json`: fixed four-work selection, original work/request/final hashes,
  recorded labels, checks and zero-call boundary.
- `captures/`: byte-identical journal, four preparation bundles and prior results
  annotations. `capture-pins.json` binds the copies; original registered sources
  and earlier sealed closures remain at their existing locations.
- `verified/smoke-audit/`: supported three-file export, byte-identical to the original
  observed export. Its exact repeat preserves all bytes and modification times.
- `verified/N06`, `N07`, `N10`, `N11`: native result and work-brief views. These are
  local projections of observed captures, not independent delivery envelopes.
- `replay.py`, `checks.json`, `summary.json`: executable local regression checks,
  exact outcomes and scope inventory. Socket, HTTP, real smoke execution, fixture
  dispatch and SQLite operations are blocked in the actual replay.

The replay uses the supported audit against the **original fixed journal**. It does
not point an observed-origin journal copy at a new location or bypass the frozen
implementation/source checks. Copies are regression evidence; they are not a new
live run. A later implementation change may require explicit compatibility
qualification before this frozen audit can authenticate again. No archived Python
is imported or executed.

## Downstream compatibility

| Boundary | Result | What must remain outside a bare native result |
| --- | --- | --- |
| Compact smoke `audit` | All four works authenticate, bind and complete; original export reproduced exactly | Nothing needs to be dropped: this export retains full intake, terminal exchanges, origin, usage and completion |
| Native `bind_assessment_result` / `complete_work` | All four original works replay exactly | Caller remains responsible for delivery authentication and terminal accounting |
| Native result renderer | All source documents, report fields, selected claims, final text and locations retained | Transport origin, endpoint IDs/evidence, cached usage, accounting holds and intake dispositions |
| Work-brief renderer | Also retains unchanged declarations and briefs; all four views bind | Still not a full observed-delivery/intake envelope |
| Authored completion publisher | Observed terminal records rejected by its submission parser | Existing contract requires `authored_fixture`, an author and offline input binding; do not synthesize them for a model delivery |
| Compact fixture-journal path | Observed smoke headers rejected by the fixture header contract | Injected-fixture origin cannot substitute for observed transport |
| Registered native B archive exporter | All four N identifiers refused; a valid B-shaped identifier still cannot register the smoke archive | The November 7 B archive trust root, layout and trial namespace remain distinct |

The original `IntakeResult` still has null assessment/completion fields. Rendering
does not mutate pending intake, discard held claims or create a production workflow
route. The full smoke row combines the unchanged intake with separately derived
terminal and completion records. This is the existing working read-only route for
these observations; another archive exporter is not needed merely to inspect them.

Relevant boundaries are the [native result component](../../engine/open_hollywood_engine/evaluations/assessment_result.py),
[native completion](../../engine/open_hollywood_engine/evaluations/assessment_work.py),
[authored publisher](../../apps/api/open_hollywood_api/services/assessment_completion.py),
[registered B exporter](../../apps/api/open_hollywood_api/services/assessment_archive_export.py),
and [observed smoke audit](../../apps/api/open_hollywood_api/services/assessment_openai_compact_smoke.py).
Accepted [ADR 0049](../adr/0049-source-bound-assessment-completion-publication.md)
already separates authored publication from the deferred observed-delivery branch.

## Material findings

**Origin belongs to the authenticated outer record.** Native `AssessmentReceipt`
and `BoundAssessmentResult` do not carry delivery origin. The shared compact
terminal reducer currently returns its fixture-specific discriminator and
`model_evidence=false`; the smoke audit deliberately excludes those fixture labels
and supplies its own observed origin from the validated fixed journal. Directly
exporting the reducer's object would therefore mislabel a real delivery. The
current smoke export does not make that mistake. Do not convert labels ad hoc or
mistake a self-consistent object for authenticated provider evidence.

**Native completion is not an accounting release.** The native receipt retains
input/output/reasoning usage, but has no cached-input counter or accounting-hold
field. `Completion` summarizes known input/output and counts unknown input/output;
it is not a summary of every transport counter. In four authored variants, cached
usage is changed to unknown while the valid final stays intact. Native delivery and
binding remain complete, and native `unknown_usage_attempts` stays zero; the outer
terminal correctly retains an accounting hold. Four known-over-budget input
variants also retain complete binding and an outer hold. Neither condition occurred
in the actual smoke. This is a proven downstream distinction, not a retrospective
claim that those four observed requests exceeded their budgets.

The smoke audit's `completion_eligible` flag checks journal closure and complete
native delivery/binding; it does **not** include accounting clearance. Thus that
flag must also remain separate from permission to release a completion downstream.
The existing compact fixture tests explicitly preserve the combination of complete
binding/eligibility and an accounting hold. A future consumer must check the outer
hold and budget findings as well, not just this flag. The actual four works have
no such holds.

**Intake dispositions and declared obligations need their own fields.** The native
result view preserves all report fields as context, but does not encode which
unselected fields were held or the reasons for those holds. The work-brief view
preserves declarations/briefs but still lacks the complete intake disposition record.
Keep the original intake alongside the result, as the smoke audit already does.
Every attempt to add one of the four held fields to the active output is refused.

**Correct binding cannot approve a reason.** Four explicitly authored false-reason
variants still bind structurally, with factual support/evidence adequacy unassessed
and writer permission false. These are expected controls for the boundary; they are
not new model errors. The model's actual four supported/two uncertain judgments and
the prior inspection remain unchanged. Factual checking, editorial effects and
necessary revision still require separate qualification.

The local journal remains application-owned evidence, not provider-signed
attestation. Raw HTTP response bytes were not retained by the original run; safe
mapped responses, exact final text, IDs and digests were retained. This audit does
not recreate missing bytes, infer actual bills or claim cryptographic provider proof.

## Verification

All **97 local scenario checks pass**:

| Outcome | Checks | Meaning |
| --- | ---: | --- |
| Bound, unassessed | 8 | Four exact observed replays plus four authored false-reason controls |
| Bound with accounting hold | 8 | Four unknown-cache and four excessive-input variants |
| Refused | 61 | Cross-work attachments, body/request hash confusion, changed finals, missing/duplicate/extra slots, hidden/unknown refs, held fields and incompatible exporter contracts |
| Failed, no credit | 4 | Authored length-truncated terminal state despite parseable final text |
| Incomplete | 4 | Missing original batch receipt |
| Binding unresolved | 4 | Valid delivery receipt without derived native binding |
| Contract limitation confirmed | 8 | Four native-view projections and four shared-reducer origin checks |

These are software scenarios over four observed responses, not 97 model calls or
semantic accuracy opportunities. Twelve cross-work attachments and eight body-hash
substitutions are specifically refused. No successful subset of an invalid active
output is accepted. Original declared sources and all returned literal locations
remain exact; no new evidence-cardinality or claim-interpretation rule is introduced.

**457 applicable existing tests pass** (889.80 seconds), with 22 existing Pydantic
serializer warnings from deliberate mutation fixtures.
Ruff, formatting and strict mypy pass on **282 files** (281 repository Python files
plus the private helper). Final helper formatting preserves the executed Python AST.
Supported audit publication and exact repeat reuse pass. Documentation links,
UTF-8/LF and `git diff --check` pass. No frontend/build or migration check applies:
there is no application, domain, route, persistence or tracked-test implementation change.

Preservation checks retain **1,725 earlier sealed members**, **636 archive source
pins**, **794 of 797 baseline files** outside README, issue index and tracker
updates, both closed smoke journals, all fourteen issue bodies and posted URLs.
New private snapshots and an acceptance seal retain the replay and documentation.
No credentials, production database, provider profile, graph, gate or human
checkpoint was changed. No external issue was edited.

## Recommended next step

Implement a **narrow observed-completion admission/publication branch in the tracked
read-only assessment component**, using these four saved deliveries without new
inference. Reuse the supported smoke audit and existing native binder/renderers;
do not build another transport, relabel an authored submission, or generalize the
B archive contract. Keep the existing full smoke export as the operator reference.

The concrete boundary should:

1. Accept registered source paths and an authenticated, closed observed audit,
   not caller-provided native receipts or approval flags. Bind the original intake,
   exact request set, compact presentation/local provenance and observed journal.
   Preserve the distinction between registered probe source and observed assessment.
2. Carry the **full original intake plus observed terminal envelope** into each
   read-only completion publication: declarations/briefs, active/held/unselected
   scope, full source context, raw final, endpoint/response identities, all usage
   counters, accounting holds, closure and whole-work completion. Keep absent values
   unknown. Neither native completion nor `completion_eligible` alone may authorize
   release; check accounting clearance separately. Preserve failure
   evidence separately and do not publish a successful subset as a complete work.
3. Use an explicit observed discriminator and provenance notice. Recompute binding,
   preserve unassessed semantics and false writer permission, enforce source/path/
   secret guards, and verify manifest-last exclusive publication and exact reuse.
   Qualify the four exact successes and these local failure/accounting/origin controls
   before exposing the new branch. Leave authored and B export behavior unchanged.

This is a concrete integration step supported by actual intake-matching deliveries,
unlike the earlier unrelated B archive captures. No new model experiment is necessary
to qualify this boundary. After it is verified, revisit prospective fresh-family
supported/contradicted/unavailable controls; no budget or live plan is frozen here.
Do not use another same-family smoke as evidence of broad story-quality improvement.

Human review continues to cover feel, flow, character and story-breaking effects.
Source binding and mechanical accounting stay application responsibilities.
CW-007/CW-013 remain open; CW-014 unqualified. Step 19 **IN PROGRESS**; Step 20
**NOT STARTED**. Production prompts unchanged; live calls **PAUSED**; full workflow
canary **ON HOLD**.
