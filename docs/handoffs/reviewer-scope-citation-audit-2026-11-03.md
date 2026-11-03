# Assessment scope and citation-section audit

Date: **2026-11-03**. **LOCAL AUDIT AND REGRESSION PRESERVATION COMPLETE.**
No inference, token-count, model-discovery, daemon or database calls. Production
**prompt 61 / graph 9 / fulfillment policy 1** and active profiles are unchanged;
live calls remain **PAUSED**, and the workflow canary remains **ON HOLD**.

The two problems have different boundaries. **Active scope is an application
contract that can be constrained and checked exactly. Citation adequacy still
requires understanding the selected claim and its evidence.** A valid source ID
does not establish that its passage supports the reason, and a correct reason
does not establish that the cited passage contains it.

The [DeepSeek/Luna results](../benchmark_reports/reviewer-assessment-workload-v61-results-2026-11-02.md)
remain unchanged. This audit finds no source-index shift or context loss in the
saved requests. It preserves the model failures without converting a local
prototype, a corrected example or a citation lookup into a model recovery.

## Preserved regressions

The private bundle is
`data/diagnostics/reviewer-scope-citation-audit-v61-2026-11-03/`.
It preserves **422 byte-identical files**, including all 35 attempted cells,
their requests, responses, usage, terminal/completed records, original plans,
work/context records, inspection packets and notes, scores and public snapshots.
It also verifies **3,153 historical source fingerprints**. Copied Python remains
inert evidence; the new reader does not import it.

Original plan SHA-256:
`2b38d6547dd5304ef2bc12e9b9fe2209fbdb915ba953cad660d29473137c2702`.
Original results-seal SHA-256:
`c006ee04758066d80472955068eea418020f88d4a7165a4c8395461ba17535e7`.
The original issue-index/tracker snapshots are preserved before this task's
authorized progress updates; they are distinguished from their current versions.

| Regression group | Preserved expectation |
| --- | --- |
| DeepSeek `D-NA-H1-CP-batch-001` | Two active selections, seven returned; complete HTTP-200 stop with 8,219 generated tokens. Reject extra scope, withhold semantic credit, retain five consumed calls and 25 retired calls. |
| All valid deliveries | 34 valid responses, 128 judgments, every expected active pair exactly once. Re-encoding saved values in the local slot prototype is not a new model output. |
| Positive grounding controls | All 109 grounded judgments remain positive fixtures, including the observed fresh contrasts and four Luna citation recoveries. |
| Citation-only failures | All twelve retain correct material explanations but inadequate cited coverage. Seven are in NA and five in MA. |
| Semantic failures | All seven remain failures, including the shared private-flourish and next-scene timing mistakes and the H2/PC NA loss. Three also miscite source content. |
| Unavailable work | All 96 slots remain unavailable: two active in the invalid response and 94 unstarted. No partial-final salvage or reopened allowance. |
| Whole relations | Four observed contextual slots and four unavailable slots remain separate from component labels; no automatic whole-relation credit. |

The complete-case receipts replay through the existing tracked component:
DeepSeek has two complete work items, one MA and one NA; Luna has sixteen, eight
per arm. Support, edit necessity and craft remain unassessed, with writer
permission false. Neither original workload outcome is promoted or rescored.

## Audit 1: active assessment scope

All **60 frozen requests** preserve their corresponding MA sources, full report,
field inventory, source registry, system instruction and response-contract text.
Only the selection message changes in NA. It carries the active `admitted_spans`
and the full original list as `original_admitted_spans_context_only`. The actual
provider wire messages match those prepared messages. No trimming or accidental
selection change explains the observed DeepSeek failure.

There are three distinct boundaries:

1. The instruction says to assess each active pair once and only those pairs.
2. The frozen structural schema allows **zero to twelve** assessments, uses the
   **full report-field enum**, and allows a free exact-quote string. It does not
   encode the request's exact active pairs or exact active cardinality. Every one
   of the sixty schemas includes report fields outside its active field set.
3. The application validator enforces the exact requested field/quote pairs,
   uniqueness and completeness. It rejected DeepSeek's extra selections correctly.

Thus a schema-conforming object can still be out of task scope. DeepSeek's seven
returned pairs reproduce the context-only list and fit the broad response shape;
the failure is at the active-task boundary. This is consistent with scope
confusion, but does not prove an internal cognitive mechanism. Ollama's historical
route supplies this schema in prompt text; Luna used native strict schema. Neither
fact means the broad schema itself expresses the active set.

### Local response-slot design

A private, data-only prototype now creates **one required object property per
active application-owned unit ID**, with additional properties forbidden. Each
slot contains only model-authored support, evidence and reason. The application
supplies the bound report field, exact quote and offsets from the immutable work
record. The preview keeps the entire source/report context and retains existing
declared links; it never infers semantic dependencies or splits whole selections.

The validator rejects missing/extra/duplicate slots, wrong work/request identity,
changed context, model-authored identity fields, invalid evidence IDs, duplicate
references and malformed reasons. The renderer displays the complete context and
returned evidence literally. Unknown or out-of-scope content is rejected, not
filtered into an apparently successful result.

This is **not installed in production, not a provider request and not a changed
diagnostic prompt**. Provider support for the proposed schema has not been tested.
DeepSeek's prompt-only route could still emit an invalid response; local rejection
does not demonstrate improved delivery. All 34 valid historical responses can be
represented by the local slots, but all their semantic/citation failures survive.

The useful application result is narrower: exact scope can be declared by the
application instead of asking the model to reproduce claim identity. It does not
establish support, relation entailment, editorial necessity or authority to edit.

## Audit 2: citation selection and source sections

The audit independently reconstructs the **actual model-visible registry** from
each wire's complete source artifacts and its displayed field/paragraph index.
It verifies artifact identity/version, role, JSON pointer, source/field hash,
Unicode offsets and exact paragraph text. The one-based paragraph interpretation
agrees with the saved registry, including short paragraphs such as “Ten years.”

All sixty wire registries resolve exactly. Across eight case/order records there
are **1,564 registry entries**; reordered presentations are not independent
sources. All **240 cited-reference occurrences in 128 valid judgments** also
resolve. The record therefore supplies no evidence of an application off-by-one
shift, wrong source version or lost paragraph in this run.

The content audit retains **fifteen judgments with citation-content problems**:
the twelve primary citation-only failures plus three semantic failures with an
additional citation mismatch. This is not fifteen extra semantic failures.

| Location | Observed selection problem | Why a mechanical index correction is insufficient |
| --- | --- | --- |
| H1/CP NA Q003 | S307 is the current-date paragraph; the explanation describes the match in S309. | The chosen ID is two positions away, but correctly resolves to the date. |
| H1 NA match/endpoint judgments | S308 contains “Ten years,” while the material explanation needs S309's journal comparison. | Valid location does not supply the match; changing IDs automatically would invent the intended evidence choice. |
| H1 NA date/realization judgments | Some citations cover only warning/date material or the assigned turning point; observed current date and/or explicit realization are omitted. | A compound claim needs all its material observed components; a plan is not proof of their occurrence. |
| W1/CP MA Q005 | S026 is the current scene's touch/vibration turning point, while the reason describes the next scene's private test in S032. | This is a wrong planned section, not a prose-paragraph offset. |
| W1/CP NA Q005 | S057 is entry preparation; the performed tracing verification is in S056. | Here the selected paragraph is later, so a universal “add one” rule is wrong. |
| W2/PC MA Q001/Q004/Q005 | The selected prose paragraphs precede the reasoning/preparation, crossing or private-test nonperformance described in the reasons. | Neighboring passages remain different evidence even when the explanation is correct. |
| W2/PC MA Q002 | S054 establishes contact but omits S055's subsequent persistent vibration. | One correctly located component does not cover the complete proposition. |
| H2/CP NA Q005, already a semantic failure | Current-scene entry/location fields S306/S310 are cited for an explanation about the next scene; S307 correctly supplies the current prohibition. | A field-name resemblance does not preserve scene identity, and repairing references would still not establish already-inside timing. |

The four other semantic failures have relevant source locations yet still make
unsupported inferences. In particular, a general handwriting match does not
establish the specific private-flourish test under the frozen factual contract.
Separately, a reader may judge that a general match changes suspense. This audit
does not convert that possible craft judgment into a factual error in the story.

The adequate-evidence examples remain **illustrative, not an exclusive answer
key**. The local validator permits any valid registry reference and leaves
adequacy unassessed. It does not require a character to repeat assignment wording,
repair model citations, or manufacture entailment from a correct location.

## Verification

**401 offline tests pass**, comprising:

- **213 new checks:** all sixty scope previews, all sixty independently resolved
  wire registries, all 35 saved deliveries, all nineteen citation/semantic failure
  judgments, and adversarial scope, mapping, literal-rendering and preservation
  controls.
- **104 applicable frozen harness tests**, excluding only the preparation-time
  assertion that no approval files exist. Both historical approvals still exist.
- **38 tracked assessment-work tests** and **46 tracked review-evidence tests**.

Ruff lint/format and strict mypy pass for the **five new private scripts** and
**222 repository Python files**. Deterministic audit replay verifies preserved
bytes and source pins and reproduces the separate scope, citation and regression
records. HTTP, sockets, DNS and SQLite are blocked in the relevant audit/test
paths. No credential setup, model metadata refresh or database operation is needed.

Initial local typing/format findings in the new scripts were corrected before the
recorded successful verification. They did not change any capture, prompt or
historical score. Verification uses explicit current script/test paths so that
copied archive Python is never collected as runnable audit code. No product code,
API/client contract or frontend changed, so frontend/build checks and another
full repository test run are not part of this local audit.

Replay from the repository root:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-scope-citation-audit-v61-2026-11-03/scope_citation_audit.py verify
```

Use fresh record/temp paths to repeat the full local verification:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-scope-citation-audit-v61-2026-11-03/verify_local.py data/diagnostics/reviewer-scope-citation-audit-v61-2026-11-03/verification-next.json data/diagnostics/scope-citation-check-next
```

## Recommended next steps

**First, a small tracked local integration:** extend the existing read-only
assessment component with an active-result contract and literal evidence-location
renderer, based on the verified slot prototype. Keep source/context identity,
raw delivery, exact active coverage, evidence location, source support and writer
permission separate. Port authored adversarial fixtures into tracked tests; keep
unpublished captures in the private regression bundle. Do not add automatic ID
repair, semantic acceptance, production routing or a new human checkpoint.

If that work warrants another live diagnostic, prioritize a **provisional
16-call Luna MA/quote-witness comparison**, not another unchanged MA/NA repeat:

- Two historical families, **H1 and W2**, each in both presentation orders,
  plus two newly authored scene families in both orders. Use one full MA control
  and one treatment per case/order: eight paired cases, sixteen calls maximum.
- Preserve the historical Luna MA wires as controls. Change only the treatment's
  evidence output to bounded exact source quotations located by the application,
  reusing the earlier witness prototype after local schema/renderer verification.
  Do **not** combine this with the active-slot schema or smaller batches.
- Retain full context, whole claims, positive/negative private-test contrasts,
  plan-versus-event and opening-time distinctions, attribution, unavailable-source
  controls, and compound evidence requirements. No gold witnesses in requests.
- Test whether directly selecting source text reduces wrong-section/omitted-source
  citations. Luna now has completed full-workload controls on this route; the
  previous DeepSeek witness run stopped after four calls and never established
  this result for Luna. Prior witness success also showed that exact locations
  alone do not cure semantic inference.
- Provisionally retain the previous per-call envelope: **24,000 input / 16,000
  generated tokens including reasoning / 600 seconds**, zero retries. Reserve
  384,000 input / 256,000 generated / 9,600 active seconds across sixteen calls.
  Stop the entire proposed comparison on its first delivery, transport, unknown-
  usage, integrity, metadata or resource failure; retain unavailable denominators.
  Settings, metadata, exact budget and schedule still require a new freeze.
- Require at least two distinct paired citation recoveries, no paired semantic
  or grounding losses, grounded fresh controls and complete delivery. Publish
  total resources; do not claim production quality or repeatability from one
  attempt per cell. This is a citation-binding feasibility test, not a prediction
  that witnesses will fix the private-flourish or temporal inferences.

The DeepSeek active-scope hypothesis should remain a separate possible pilot,
after the local contract is tracked and its actual adapter serialization is
verified. It should not be bundled into the Luna citation treatment or consume
the 25 retired calls. **Neither pilot is frozen or approved, and no new requests
or live budget are created by this audit.**

The production direction remains deterministic provenance and readable evidence,
followed by a separately qualified factual/necessity decision before any writer
acts. Human assessment should focus on feel, flow, character and story-breaking
details when actual repair comparisons are ready. All fourteen issues remain
open; Step 19 is **IN PROGRESS**, Step 20 **NOT STARTED**, canary **ON HOLD**.
