# Local assessment completion and export rehearsal

Date: 2026-11-12. Status: local rehearsal COMPLETE; general completion publisher absent.
Production prompts unchanged; live calls **PAUSED**; canary **ON HOLD**.

The existing intake, scope, result-binding, completion and rendering components
compose successfully for the six selected claims. The registered archive exporter
correctly refuses these authored completions. Local inspection artifacts are saved
separately; no new adapter or production eligibility change was made.

## Scope and selection

Rehearse exactly six existing pending whole-field claims in four unchanged work
items. No model, input-count, catalog, daemon or user database call is authorized
or performed. Responses are **authored local fixtures**, not model observations,
new semantic gold or new story-quality evidence.

| Review | Active units | Coverage exercised | Existing holds | Unselected fields |
| --- | --- | --- | ---: | ---: |
| N06 | Q001 / P07 | Compound endpoint obligation and depicted crossing | 1 | 10 |
| N07 | Q004 / P08; Q005 / U01 | Endpoint comparison and unavailable future-start authority | 0 | 10 |
| N10 | Q003 / P12; Q007 / U02 | Craft-source factual comparison and unavailable future-start authority | 2 | 10 |
| N11 | Q003 / P13 | Visible historical repair assertion and current correction | 1 | 11 |

The six units retain **51 complete report fields, four holds and 41 unselected
fields**, as well as the entire original messages, current prose, provenance,
scope declarations and work briefs. Unit IDs remain local to each source work;
identical IDs in different reviews are never merged. Selection and input hashes
are recorded before response construction.

The baseline fixtures supply four supported labels and two uncertainty labels to
exercise both structural paths. Those labels are authored examples; this rehearsal
does not re-establish the prior admission judgments. Additional deliberately false
or inadequate fixtures exercise the boundary without becoming negative gold.

## What is being exercised

The existing intake compiler revalidates each saved source/plan and pending work.
The existing scope/brief preview, response schema, result binder, completion
validator and literal renderer operate on the unchanged native work. A hashed
offline input document binds each fixture receipt to exact work, declarations,
briefs, active batch and schema. It explicitly says it is not a provider request
or model input. No production prompt or request adapter is changed.

The local fixture wrapper labels every response, native result and rendered view
as authored. Native `model_assessment` and delivery-receipt fields contain synthetic
test inputs only. Their token fields remain null and their zero active time is a
fixture value, not a measurement of inference. Zero live calls is recorded separately.

Each work exercises 28 cases: baseline, uncertainty, authored unsupported labels,
inadequate and outside-declaration citations, malformed/duplicate/missing/extra
slots, unknown/duplicate/missing evidence, forbidden identity, hidden provenance,
stale work/request/units/raw digest, failed terminal states, missing batches,
unbound and duplicate receipts, and stale declarations/briefs. N11 additionally
tests the eleven-location/eight-citation boundary. Stop on any unexpected
disposition, changed source, network or database access.

Full-context input, baseline and inadequate-citation views are saved alongside the
unchanged intake and all scenario records. Intake dispositions are included with
the rendered results so held and unselected fields remain visible. No fixture
result is written back into the original pending intake.

## Confirmed boundaries and integration gap

**Location binding is not evidence adequacy.** A valid reference can bind even if
it supplies only the assignment while the claim also concerns depicted prose, or
lies outside the declaration's listed scope. Definite labels with no evidence are
rejected; insufficient but valid locations remain structurally bindable and
semantically unassessed. This is the documented ADR 0042/0043 contract, not a new
model failure. Declared scope is not a citation whitelist or automatic proof.

**Delivery and binding remain separate.** A synthetic valid receipt alone can
produce `complete_delivery=true` with `binding=unresolved`. Only the binder's
derived receipt gives complete binding. Even then factual support, evidence
adequacy, whole-relation credit, edit necessity, craft and writer permission do
not become approved. A future caller must not route from the delivery boolean alone.

**Source-scope inventory differs from response citation selection.** N11 declares
eleven locations, including nine historical repair-test fields. The baseline
explicitly selects five visible locations: complete current prose, assigned exit
state, historical claim, original quotation and requested repair. Sending all
eleven exceeds the eight-citation response limit. No silent truncation or limit
increase is applied, and the selected five are not automatically certified adequate.

**There is no supported publisher for these completion envelopes yet.** The
tracked native archive exporter admits twelve registered B captures under their
frozen source, request and transport evidence. It does not accept arbitrary intake
completions or authored test receipts. The rehearsal tests refusal both for a local
review ID and for a syntactically valid B ID without its registered archive. No
trust-pin override, fabricated transport history or eligibility change is introduced.

The local artifacts use the existing native renderers and a separately labeled
private rehearsal manifest. They are not claimed as successful exports through
the registered B archive command. This is the specific interface gap found before
adding another adapter, as requested by the prior recommendation.

## Verification

All **113 authored scenario checks** match their frozen expectations:

| Disposition | Cases | Meaning |
| --- | ---: | --- |
| Bound, semantics unassessed | 20 | Five response variants for each of four works, including intentionally inadequate evidence |
| Correctly rejected | 85 | Malformed, stale, forbidden, structurally incomplete or failed-delivery fixtures, plus the eleven-citation case |
| Incomplete | 4 | Missing expected batch; zero delivered units |
| Binding unresolved | 4 | Synthetic valid receipt supplied without native evidence binding |

These are repeated software boundary checks on six unique claims, not 113 new
reviews or inference observations. The four baseline results cover all six active
units. Neither supported nor deliberately unsupported fixture labels grant factual
support, evidence adequacy, whole-relation credit or writer permission. The two
registered-export refusals also pass without creating output.

**472 applicable tests pass: 25 new composition tests and 447 existing tests.**
Ruff, formatting and strict mypy pass for **244 repository Python files plus the
private rehearsal helper**. The existing 56 Pydantic warnings are deliberate
mutation fixtures. Isolated SQLite/fake-gateway tests ran outside the Windows
sandbox because of its event-loop restrictions; the real six-claim rehearsal
blocks network and SQLite calls. No frontend/build change requires a frontend build.

All **27 private inspection files** verify byte/mtime-exact reuse. The four source
intakes, all 71 members of the prior qualification, earlier admission/intake seals
and 1,166 original source pins remain intact. Full context, whole claims, native
declarations and briefs are unchanged; the original pending intake still has null
assessment/completion fields. No historical script is imported or executed.

No production/domain/exporter code, dependency, database schema, prompt, model
profile, graph, acceptance gate, writer route or Blueprint checkpoint changes.
Tracked additions are authored integration tests and their fixture helper only.

Private artifacts:

- [Frozen local plan](../../data/diagnostics/assessment-completion-rehearsal-2026-11-12/plan.json).
- [Inspection index](../../data/diagnostics/assessment-completion-rehearsal-2026-11-12/rehearsal/index.md).
- [Acceptance](../../data/diagnostics/assessment-completion-rehearsal-2026-11-12/acceptance.json).
- [Verification](../../data/diagnostics/assessment-completion-rehearsal-2026-11-12/verification.json).

## Recommended next step

Do a **bounded local design pass for an intake-completion envelope and read-only
publisher**. Reuse the existing work, scope, binding, completion and rendering
components; define the missing application boundary before expanding inference:

1. Bind the exact authenticated intake, source versions, declarations, work brief,
   active batch and response to a single completion envelope. Preserve the original
   pending intake, holds and unselected fields.
2. Distinguish `authored_fixture` provenance from authenticated model delivery.
   A fixture must never become a model observation. A future live adapter must
   supply exact request/terminal evidence and honest usage; internal hashes alone
   do not establish that a model saw the context.
3. Recompute binding and completion before publication, expose semantic
   nonqualification, and provide literal JSON/Markdown, a manifest, secret checks,
   source-drift refusal and exact reuse. Keep all writer permission false. Qualify
   the design against these same six claims before adding a general CLI or route.

This would connect intake to an inspectable result while preserving the current
trust boundary. It does not require prompt changes, a live experiment, an automatic
assessment gate or another mandatory human checkpoint. No implementation beyond
this rehearsal or new inference budget is frozen here.

The natural-negative and fresh-family gaps remain. Authored unsupported labels
cannot fill them, and these related Elara scenes do not establish generalization.
Literary feel, flow, character, story-breaking effects and necessary editing still
need separate evidence; mechanically complete results cannot settle them.

Tracker and issue index updated; all fourteen issue bodies and posted URLs unchanged.
CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; live calls PAUSED; full workflow canary ON HOLD.**
