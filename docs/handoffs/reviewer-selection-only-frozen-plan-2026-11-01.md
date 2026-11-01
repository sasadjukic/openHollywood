# Frozen SA/SO premise-selection comparison — 2026-11-01

**Prepared locally; 0/16 inference calls used. Separate live approval is required.**
Production prompt61, graph9 and fulfillment policy1 are unchanged. Live inference
is paused and the full workflow canary remains **ON HOLD**.

This implements the [local delivery/citation/workload audit's proposal](reviewer-admission-delivery-audit-2026-11-01.md).
It is a new experiment. The stopped SA/VA experiment's six consumed attempts,
terminal evidence, original global stop and eighteen unused slots remain intact.
Those unused slots cannot be spent under this plan.

## Question and controlled contrast

Can selection alone deliver faithful consequential-premise selections within the
same per-call limits, while requiring less generation than combined selection
and assessment? The preceding SA/VA comparison did not answer this: SA stopped
with a 16,000-generated-token, empty-final response before any fresh family ran.
Its two complete control pairs showed greater generation and latency, but did
not establish why. This comparison tests task separation directly.

| Condition | Frozen task | Attempts |
| --- | --- | ---: |
| SA | Exact prior combined selection-and-assessment wire requests | 8 |
| SO | Select exact report field/quote pairs, without support judgments, citations or reasons | 8 |

Both receive the same complete prose, context, saved report, report-field inventory
and source citation index. All eight SA wire payloads exactly match their previous
frozen counterparts. SO changes only the task instructions and response contract;
its source/report messages and sampling settings are identical to SA. The SO
contract admits zero to twelve uniquely bound, exact contiguous quotes with only
`field_id` and `quote`. It receives no gold labels, target IDs, expected evidence
or authored selections. All source/report text is treated as data.

SO preserves attention to consequential factual premises, valid criticism and
qualified literary opinion. Selecting a quotation does not establish its truth
or faithful meaning in the complete report field. This experiment adds no second
assessment call and produces no story revisions.

## Cases and schedule

| Family | Provenance and contrasts | Primary targets per order |
| --- | --- | ---: |
| H1 | Historical Elara report: decision through action; entry boundary; ten-year dates | 3 |
| H2 | Historical Elara report: outside endpoint; preparation/decision; touch and observed psychic pull | 3 |
| F2 | Previously frozen, never sent: Mira attribution/namesake; box boundary; conservator request | 3 |
| F4 | Previously frozen, never sent: unavailable Appendix B; envelope boundary; complete-appendix request | 3 |

F2/F4 are **fresh to inference, not newly authored scenes**. Full cases and gold
are unchanged from SA/VA; its saved execution records contain no F2/F4 dispatch.
This is a narrow follow-up with limited scene diversity, not a fresh generalization
or whole-story benchmark.

PC means prose before context; CP means context before prose. Fixed pair order:

| Calls | Family/order | Condition order |
| --- | --- | --- |
| 1–2 | H1 PC | SA, SO |
| 3–4 | H2 CP | SA, SO |
| 5–6 | H1 CP | SO, SA |
| 7–8 | H2 PC | SO, SA |
| 9–10 | F2 PC | SA, SO |
| 11–12 | F4 PC | SO, SA |
| 13–14 | F2 CP | SO, SA |
| 15–16 | F4 CP | SA, SO |

Each condition runs first in four pairs. Stopping one condition leaves the other
condition's original cells in this order. No replacements or reordered cases.

## Model, metadata and budget

Metadata-only reads on 2026-11-01 independently verified **Ollama 0.40.13** and
`deepseek-v4.1-flash:cloud`, with the same selected tag/capability metadata as SA/VA.
Digest: `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Version, tags and show responses are retained with raw bytes/hashes. The first
sandbox-blocked version request is also retained; it dispatched no inference.
Metadata continuity does not prove an unchanged remote model implementation.

Fixed settings: **high thinking**, temperature 0.2, top-p 0.95, seed 20261022,
40,000 context tokens, non-streaming, no format override. Thinking remains opaque
for semantic inspection. The provider's combined generated count includes thinking
and final output once; no inferred token split or second thinking allowance.

| Limit | Per attempt | Whole comparison |
| --- | ---: | ---: |
| Attempts | 1 per cell | 16; 8 per condition |
| Input tokens | 24,000 | 384,000 reserved |
| Total generated tokens | 16,000 | 256,000 reserved |
| Active generation time | 600 seconds | 9,600 seconds reserved |
| Retries, repairs, replacements, reallocation | 0 | 0 |

The archived reference rates of $0.30 input/$1.20 output per million give a
**$0.42240** maximum reference reservation and **$0.50** planning allowance.
These are not verified current tariffs or an enforceable billed-cost ceiling.
Actual billing remains unknown. Failure never releases or transfers a reservation.

Any future dispatch requires approval bound to the final plan hash, all sixteen
requests, the length-retirement policy and transmission of full unpublished
fiction/context and saved reports to **Ollama Cloud through the local daemon**.
No approval file or live execution directory has been created during preparation.

## Scoring and inspection

Each condition has **24 primary target opportunities**, twelve in F2/F4: eighteen
supported, four unsupported and two uncertain propositions. These historical
labels describe the target set; SO is not asked to judge them. All sixteen planned
cells remain in delivery and admission denominators, including unstarted cells.

1. Validate exact field/quote bindings and the appropriate output schema. Reject
   unknown/extra fields, duplicate JSON keys, repeated exact selections, ambiguous
   quote occurrences and non-exact quotes. Empty valid selections are omissions.
2. Export results for a partially masked source audit, withholding condition/order
   labels, token counts, timings and all thinking text. Output fields and familiar
   cases can reveal the task; this is not an independently blinded human study.
3. Inspect **every returned selection**, including extras, in its full report field
   and source context. Annotate faithful meaning, material errors, factual-premise
   relevance, opinion factualization and semantic duplicates. Inspect all three
   targets independently; substring matching alone cannot award coverage.
4. Keep SA support labels, reason grounding and citation adequacy separate from
   admission. Preserve H2's touch-plus-pull citation distinction. SO's judgments
   and citations are **not requested**, never credited as correct.
5. Seal all notes before decoding arm/resource comparisons. Bind notes to exact
   source/result hashes. Extra valid premises are retained, not penalized merely
   for being outside the three-target set; duplicates cannot inflate target credit.

**Selection-feasibility screen:** SO must deliver 8/8 valid reports with 24/24
faithful primary admissions, with no meaning distortion, material error or false
factualization of literary opinion across all selections. Report extra premises,
omissions and duplicates separately. This does not establish whole-report admission
completeness: the authored target set is deliberately bounded.

**Resource screen:** require all eight complete, valid SA/SO pairs, a median paired
SO/SA total-generated-token ratio at most **0.75**, and no primary admission losses.
A zero control denominator makes the ratio unavailable. Report paired input/output
counts and active latency; latency is descriptive, with no superiority threshold.
Report faithful admissions per planned and attempted call and all invalid/terminal
attempts. If controls stop early, retain SO feasibility and observed delivery
contrasts only; do not claim a complete comparative cost benefit.

Even a favorable selection result supports only designing a staged follow-up.
It cannot qualify end-to-end cost, subsequent support judgments, writer preservation
or story quality. Human review retains authority over feel, flow, character and
story-breaking details; mechanical binding/counting stays with the harness.

## Stops and evidence handling

This experiment explicitly changes the diagnostic stop scope, without changing
the old runner or production gateway:

- A hash-bound **HTTP 200 length finish with trustworthy counters**, required
  thinking, valid timing and matching metadata immediately retires **only the
  affected condition**. The other condition can finish its fixed allowance.
  Empty or partial final output is consumed and unusable, even if partial JSON
  could validate. There is no retry or budget release.
- Preserve the known empty-final gateway error chain. The narrow local handler
  accepts only the verified length envelope and the known empty-content rejection;
  it captures post-call version evidence before recording retirement. It does not
  turn the attempt into a successful model response. Other gateway failures stop
  globally. Nonempty length outputs are equally unusable.
- After each condition's fourth historical H1/H2 cell, retire that condition if
  none was valid, or if the same blocking validation signature occurred in both
  historical families. Immediate length retirement can occur earlier. A signature
  seen only within one family is not this stop. No semantic early stopping.
- **Stop the whole comparison** for non-200/transport failure, unknown/conflicting
  usage, excess resources, missing required thinking, invalid timing, metadata
  drift, tampering, ambiguous dispatch, cancellation or unexpected gateway failure.
  Global terminal stops cannot resume under this plan.

Persist the reservation before dispatch, exact wire and raw response before parsing,
and version observations before interpreting them. Each completed attempt and
retirement decision is sealed and replayed before later dispatch. Clean completed
cell boundaries can continue without duplicates; unsealed or ambiguous cells cannot.
The operator lock prevents concurrent execution. Model/version checks occur at
preflight and before each call; version is checked again afterward.
Raw counters and successful delivery remain separate;
unknown global-terminal usage stays unknown with an independently labeled raw-usage
supplement where available.

## Local verification and artifacts

The private bundle is
`data/diagnostics/reviewer-selection-only-v61-2026-11-01/`. It contains all sixteen
prepared requests and exact wires, four full cases, target gold, response schemas,
authored offline examples, schedule, scoring, stops, budget, metadata captures and
the separate runner/inspection code. Diagnostic fixtures and full prose remain
local under the repository's existing ignored-data convention.

Verification covers complete mocked execution, restart and exact-wire checks;
retirement in either condition; replay of the real historical empty-final envelope;
partial-length rejection; unknown usage, non-200, timing, cancellation and metadata
failures; tampering; zero-selection omissions; H2 citation separation; and sealed
inspection with fixed target denominators. **267 offline tests pass**: 68 new
comparison tests, 22 gateway/contract tests, 84 prior audit tests and 93 prior
SA/VA tests. Ruff lint/format and strict mypy pass on all ten new scripts. Real
HTTP is blocked in the test suites. Windows asyncio's internal socket pair
required running verification outside the sandbox socket restriction; no real
model transport was enabled. Earlier static/import/type corrections and the
sandbox-blocked attempts are retained. Final hashes and verification evidence
are recorded in the tracker and local `preparation-closure.json`.

Reverify locally, without generation:

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-selection-only-v61-2026-11-01/freeze.py verify
```

The freeze binds this public plan, exact requests, implementation, verification
evidence and historical source fingerprints. No production/API/frontend code
changes are included. CW-008/CW-013 and all other issues remain open. Step 19 stays
**IN PROGRESS**; Step 20 stays **NOT STARTED**. The next decision is separate live
approval for this plan; no calls are authorized by its preparation.
