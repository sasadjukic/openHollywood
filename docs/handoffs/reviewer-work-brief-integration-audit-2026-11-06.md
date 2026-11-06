# Work-brief regressions and read-only integration check

Date: 2026-11-06. Local integration complete. Live calls remain PAUSED;
the full workflow canary remains ON HOLD.

The tracked assessment component now provides an **authored work-brief preview**
bound to the unchanged claim, scope declarations and full context. It keeps
obligation existence, observed fulfillment and repair necessity separate. The
preview does not generate model input, establish semantic truth or authorize edits.

This completes the recommended local work from the
[U/B results](../benchmark_reports/reviewer-work-brief-v61-results-2026-11-06.md).
Production prompts, profiles, graph, routing and acceptance gates are unchanged.
No inference, input-count, catalog or daemon requests occurred. No credential
retrieval or application database access was required.

## Preserved evidence

The private bundle preserves **433 exact files** and verifies **727 historical
source fingerprints**, including the frozen 61-file plan and sealed execution
analysis. It retains all 24 requests, final responses, receipts, original gold,
144 slot inspections, materiality notes and the original publication snapshots.
Archived Python is retained as data and is not imported or executed by this audit.

The previous score is unchanged: **U 71/72; B 72/72 grounded**, or **143 grounded
and one semantic scope failure**. All **217 witness bindings** recheck exactly.
All **72 U/B pairs, 72 repeat pairs and 72 presentation-order pairs** are preserved.
These are different pairings of the same observations, not independent samples.

The principal regression is Q002, “Elena must decide to verify the handwriting.”

| Capture | Original judgment | Preserved interpretation |
| --- | --- | --- |
| `EB-2-S2-U-CP` | Unsupported; semantic failure | Correctly notices the assignment and purposeful comparison, but substitutes outstanding repair for the selected obligation question. |
| `EB-2-S2-B-CP` | Supported; grounded | Assesses the explicit assignment requirement without claiming another decision sentence is needed. |
| `EB-1-S2-U-CP` | Supported; grounded | Passing control with exactly the same generation/count bodies as the failing U repeat. |

Both U prose-first controls and all four B answers remain available. So do every
temporal, compound, attributed-negation, optional-action and unavailable-source
control. The original **14 ancillary-context notes** remain unchanged; this audit
does not tighten their scoring after seeing responses. The separate “genuine
endpoint repair” wording remains an unqualified repair-scope observation.

The valid S232 exit-state citation is retained even though the illustrative gold
set names S527. Declaration references and gold examples do not become citation
whitelists. No new semantic judgments or model accuracy claims were created.

## Integration and decisions

The new [assessment_work_brief.py](../../engine/open_hollywood_engine/evaluations/assessment_work_brief.py)
extends the existing pure read-only component. [ADR 0044](../adr/0044-read-only-assessment-work-brief-previews.md)
records its contract and limits.

- Authored question, temporal scope, source authority and evidence obligation bind
  to an existing selected unit through exact work and scope-declaration hashes.
  Original field, pointer, quote, offsets, full report and all source documents
  remain present. Editing a declaration invalidates its previous brief binding.
- Every active unit stays visible. Missing briefs, missing declarations, unresolved
  qualifiers, different declared predicates, incomplete material coverage and
  editorial scope remain review findings. The component does not silently choose
  a reading or replace a hard whole claim with an easier claim.
- The renderer recomputes checks and displays literal full context, including
  embedded Markdown as data. It may display an independently validated native
  result. It does not turn historical quote-witness captures into native receipts.
- Obligations, fulfillment and repair necessity remain separate and unassessed.
  The original result/completion contracts and response schema are unchanged.
  Even complete delivery and a supported model label grant no writer permission.

The private bridge renders all **24 full works / 144 declarations**. All 144 are
`declared_consistent` under the **explicitly authored** mapping of the frozen scope
and evidence criteria. That includes the unit whose model answer failed: declaration
consistency is not model correctness. Endpoint state and interval occurrence remain
different in the explicit temporal text; neither is silently promoted into normative
endpoint compliance. Compound material clauses remain in the declarations.

Each brief's four B text fields are copied unchanged into the local preview. A preview
attached to a U capture is explicitly **post-hoc local audit material**, not text
the U model saw. All twelve U/B generation/count request pairs still differ only
by the original brief member; exact repeat bodies remain equal.

Briefs remain `model_input: false`. No production caller, API, CLI, persistence,
migration, dependency, exporter eligibility or workflow behavior was added. There
is no automatic scope classifier, brief author or new human checkpoint.

## What the check cannot prove

Identity validation cannot determine whether a brief asks the right question,
covers every material qualification or leaks an answer. A tracked test deliberately
replaces the obligation question with a repair question: its structure is valid,
but semantic interpretation and brief neutrality remain explicitly unverified.
The component preserves that distinction rather than advertising an automated
semantic guard.

This check does not resolve ordinary editorial judgments, determine necessary
edits, prove prose preservation or establish a story-quality benefit. B remains
promising diagnostic evidence based on one recovered failure, alongside a passing
identical U control. It is not qualified for autonomous production use.

## Verification

The full Python suite passes **1,417 tests**, including **23 new tracked tests**.
The separate private audit passes **50 tests**: **1,467 distinct passing tests**,
with nothing deselected. The 22 full-suite warnings are expected serializer
warnings from deliberately unchecked Pydantic fixtures (13 existing, nine new).
Repository Ruff, formatting and strict mypy pass for **228 Python files**;
separate checks pass for all **four private scripts**. Source preservation and
all previews replay deterministically; repository Python fingerprints match
before and after verification.

All focused tests block HTTP/socket/database access;
the private audit also blocks the application secret store. Verification subprocesses
receive an environment with provider credentials removed. Full-suite database tests
use their existing test fixtures, not the application database.

The new tests cover binding drift, duplicate/foreign/inactive units, missing briefs,
unresolved repair scope, literal full-context retention, rejection of failed or
stale native results, unknown usage and completion without semantic authority.
Private tests authenticate every saved request and response and preserve the
failure/recovery/control contrast. Frontend/build checks are inapplicable because
no frontend or generated API contract changed.

Verification used the uv-managed environment through `.venv/Scripts/python.exe
-X utf8 -m`, equivalent to the README Python tools. A minimal asyncio startup
probe hung inside the Windows sandbox and succeeded outside it, so the full
verification ran outside that sandbox. An initial full-suite attempt exceeded
the helper's four-minute limit; no passing result was claimed for it. With a
longer local timeout and progress logging, the full suite completed in **280.39s**.
These environment retries made no model calls and changed no production settings.

Private evidence: [audit index](../../data/diagnostics/reviewer-work-brief-integration-v61-2026-11-06/README.md),
[summary](../../data/diagnostics/reviewer-work-brief-integration-v61-2026-11-06/summary.json),
[pair regressions](../../data/diagnostics/reviewer-work-brief-integration-v61-2026-11-06/pair-regressions.json)
and [verification](../../data/diagnostics/reviewer-work-brief-integration-v61-2026-11-06/verification.json).
Unpublished prose remains in ignored local data, not in GitHub issue attachments.

## Recommended next step

Prepare a **broader ordinary-review U/B transfer comparison**, with admission
before freezing or inference. Reuse the existing twelve-capture / 163-field
inventory; do not redo that inventory or merely repeat these clear fresh controls.

1. Select up to **four saved review packets**, prioritizing previously untested
   whole explanatory fields and including post-review wording where historically
   visible sources suffice. Keep at most six whole fields per request, full reports
   and full visible context. Distinguish four report packets from four independent
   scene families: the existing pool has only two closely related families. These
   are ordinary-prompt diagnostic probes with synthetic unapproved context, not
   durable production reviews.
2. Author exact brief bindings and independent whole-field gold. Seek naturally
   supported, unsupported and uncertain claims, source attribution, obligations,
   fulfillment and temporal/compound qualifications. Preserve every excluded or
   unresolved field and reason. Missing older-draft visibility, missing next-entry
   authority, ambiguous editorial meaning or an evidence obligation beyond the
   existing citation limit blocks admission; do not simplify or invent evidence.
3. If four genuinely broader packets qualify, freeze a provisional **32-attempt
   Sol-high U/B comparison**: four packets × two conditions × two source orders ×
   two exact-body repeats. Keep the assessor controls, schema and resource limits
   unchanged; freeze all whole-claim and adequate-evidence judgments before calls.
   Report natural-error precision only if the admitted saved claims actually
   contain independently justified unsupported cases. Otherwise state that gap
   and revise the proposal before requesting live approval.

This is a proposal, not a frozen plan or call authorization. Do not fill a shortfall
with easy authored claims just to use a budget. The existing 71 factual candidates
are an admission pool, not 71 pre-qualified labels. The 82 editorial/mixed fields,
six unresolved interpretations and four authority gaps remain separate work.
The proposed comparison would test assessment under declared briefs; it would not
qualify autonomous brief authoring, which remains a separate production gap.

Only a reliably scoped factual layer should inform a later independent
edit-necessity and preservation study. Human story-quality review should continue
to focus on feel, flow, character and story-breaking details, with mechanics
prepared by the application. No extra routine human approval is introduced.

All fourteen issues remain open; original bodies and posted URLs are unchanged.
CW-007/CW-013 gain local regression/integration evidence; CW-014 remains unqualified.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts unchanged;
live calls PAUSED; full workflow canary ON HOLD.**
