# VA/MA selected-premise assessment comparison — frozen plan, 2026-11-01

**Local preparation only: 0/16 inference calls used. Separate live approval is
required. Production prompt61 / graph9 / fulfillment policy1 remain unchanged;
the full workflow canary remains ON HOLD.**

This follows the [context-preserving handoff audit](reviewer-staged-handoff-audit-2026-11-01.md).
The narrow question is whether the existing assessor can judge the **actual saved
model-selected propositions**, including their larger workload and extra premises,
when complete source/report context is retained. It does not retest selection,
test fresh-scene generalization, or qualify autonomous repairs or literary quality.

## Frozen comparison

| Condition | Input | Calls | Assessment units |
| --- | --- | ---: | ---: |
| VA | Unchanged authored-span controls from the SA/VA freeze | 8 | 24 |
| MA | Same source/report/instructions/settings; replace only `admitted_spans` with the corresponding saved SO selections | 8 | 41 |

The eight VA **wire requests are identical** to their October-31 controls. In
MA, restoring only the admitted-spans message restores that same wire request.
No diagnostic system prompt, response contract or production prompt is edited.
Internal invocation metadata additionally binds MA to its saved selector receipt
and complete handoff; those application-side fingerprints are not prompt content.

Both arms receive the complete sources, declared scope, source citation registry,
saved report and field inventory. The assessment unit remains the **selected
proposition in its full field context**. Providing the whole field does not
silently widen the claim being judged. No expected labels, authored coverage links,
target IDs, rationales or witness sets enter model requests.

| Pair order | Family / source order | First condition | VA units | MA units |
| ---: | --- | --- | ---: | ---: |
| 1 | H1 / PC | VA | 3 | 7 |
| 2 | H2 / CP | VA | 3 | 5 |
| 3 | H1 / CP | MA | 3 | 7 |
| 4 | H2 / PC | MA | 3 | 5 |
| 5 | F2 / PC | VA | 3 | 4 |
| 6 | F4 / PC | MA | 3 | 4 |
| 7 | F2 / CP | MA | 3 | 4 |
| 8 | F4 / CP | VA | 3 | 5 |

PC presents prose before context; CP reverses those two messages. Each condition
runs first four times. H1/H2 cover decision-versus-boundary, temporal scope,
specific versus general handwriting verification, and contact/pull evidence.
F2 covers namesake attribution; F4 covers unavailable Appendix B and independent
endpoint obligations. **All four families have now been seen in prior diagnostics.**
Their original prose, assignments, report fields, registry refs and versions are
unchanged. No new selector calls or prose revisions are included.

All eight SO outputs are used exactly, in their saved selection order: **41 units
across 40 field instances**, including ten partial-field quotes and one inspected
overlapping premise. There is no semantic deduplication or substitution of the
three authored targets. Sixteen field/quote pairs exactly match VA controls;
equivalent wording elsewhere does not create additional identical pairs.

## Frozen judgments and scoring

Authored selected-unit labels are **31 supported / eight unsupported / two
uncertain** for MA, and **18 / four / two** for VA. These are expected judgments,
not model results. All 65 units, exact offsets, selected quotes, rationales and
evidence requirements are frozen locally. MA's gold retains the prior audit's
labels and adds explicit semantic rationales and illustrative component witnesses.
Other registry references remain acceptable when their content establishes the
same required evidence; the illustrative witnesses are not an exact whitelist.

Important interpretation decisions are fixed before inference:

- Purposeful action can establish a decision; a later boundary overrun does not
  erase an earlier decision or turning-point event.
- A general handwriting match does not by itself establish verification of the
  specifically planned private flourish. H1's “immediately” selection refers to
  resolution in the current scene, not an invented elapsed-time measurement.
- H2's contact/pull claim needs evidence of **both** events. A next-scene location
  identifier does not establish that the scene begins after entry. Preserve the
  valid current-scene prohibition even when the temporal subclaim is unsupported.
- Namesake quotation does not transfer speaker identity. An unavailable appendix
  is unresolved evidence; an independent obligation is not proof of its contents.
- F4/CP's shortened opening quote is assessed at that selected scope. The omitted
  violation clause remains visible but is not silently substituted as the unit.

Scoring separates delivery, label correctness and grounded usability:

1. **MA feasibility requires 8/8 valid deliveries and 41/41 grounded judgments.**
   Each must preserve meaning, use the correct support label, give a grounded
   reason and adequate citations, and introduce no material unsupported explanation
   or factualized literary opinion. All extras and overlaps receive inspection.
2. Report VA's 24 opportunities separately. The additional paired requirement is
   **all sixteen exact pairs evaluable and zero grounded VA-to-MA losses**.
   Invalid and unstarted units remain failures in fixed denominators; missing
   controls cannot satisfy the paired requirement by default.
3. Keep three explicit contextual-relation flags: H1/CP, H2/CP and F4/CP. Inspect
   whether a response actually assesses the complete relation and, if so, whether
   that explanation is grounded. Correct component labels do not automatically
   earn relation credit, and relation flags do not authorize repair dispatch.
4. A favorable bounded result requires MA feasibility and the paired requirement.
   It supports designing further staged evaluation only. Whole-report admission
   completeness, autonomous aggregation, preservation and story quality remain
   unqualified even if this test succeeds.

The offline inspection exporter withholds the trial key and resource data, then
requires complete source-bound notes sealed before decoding. This is **partial
assistant factual inspection, not blind human review**: familiar cases, selection
counts and unit identities can reveal provenance. Thinking text is excluded from
semantic inspection. Humans retain authority over feel, flow, character and
story-breaking details; this comparison produces no new story prose.

## Model, resources and accounting

Fresh **metadata-only** capture confirms **Ollama 0.40.13**, unchanged
`deepseek-v4.1-flash:cloud`, digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Version, selected tag, capabilities and thinking settings are pinned. The initial
sandbox-blocked version attempt is preserved alongside the successful capture;
neither was an inference request.

- Thinking **high**, temperature **0.2**, top-p **0.95**, seed **20261022**,
  context **40,000**, non-streaming, no format override.
- **16 new attempts maximum**, eight per condition; zero retries, repairs,
  replacements or budget reallocation.
- Per attempt: **24,000 input tokens / 16,000 combined generated tokens /
  600 active seconds**. Thinking shares the generated-token allowance.
- Aggregate reservations: **384,000 input / 256,000 generated / 9,600 seconds**.
  Archived-rate reference **$0.42240**, planning allowance **$0.50**. These are
  historical planning values, not a verified current tariff or billed-cost cap.
- Payload, if separately approved: full unpublished prose, assignments, story
  context, saved critiques and exact selected spans to **Ollama Cloud through
  the local Ollama daemon**. No inference endpoint is called in preparation.

Report input/generated tokens, active latency, provider timing and observed
thinking availability per attempt. Do not infer reasoning/final token splits when
the provider does not report them. Resource comparisons require all eight complete
valid pairs for aggregate paired statistics; otherwise report completed pairs
descriptively. **There is no efficiency threshold**, since the workloads differ.

The historical selector cost stays visible: **eight calls / 63,000 input /
80,000 generated / 245.31 active seconds**, archived-rate reference $0.1149.
Add MA's assessment cost to it when describing the staged path. Do not treat
selection as free, count those calls again as new inference, or compare that staged
total with an authored-span control as proof of end-to-end savings. New terminal
attempts retain consumed calls/reservations; unknown usage remains explicit.

The prior SA/SO run remains **10/16 used**, with six SA cells retired. The earlier
SA/VA terminal stop and its unused allowance are also unchanged. This is a new
16-call authorization boundary; neither old allowance can be borrowed.

## Stops and recovery policy

- A trustworthy **HTTP-200 length finish**, including an empty final with verified
  usage, immediately retires that condition. Preserve raw counters, gateway error
  chain and version observations. It receives no usable-output or semantic credit.
- After each condition's four H1/H2 attempts, retire it for **zero valid outputs**
  or the **same blocking validation signature in both historical families**.
  The other condition may finish only its already scheduled cells.
- **Global terminal stop:** non-200/transport, unknown or conflicting usage,
  excess limits, missing thinking, invalid timing, metadata drift, tampering,
  ambiguous dispatch, cancellation or an unexpected gateway failure.
- No semantic early stop, reallocation, automatic repair or global-stop resumption.
  A clean pause at a fully sealed cell boundary can resume only the unchanged
  remaining schedule. Locks, receipts and ledger replay prevent duplicate calls.

The harness retains the prior non-200/unknown-usage terminal export path, persists
version observations before validating them, and replays condition-retirement
decisions before further dispatch. Synthetic tests exercise these branches;
their outputs are not live model evidence.

## Freeze and verification

Local bundle: `data/diagnostics/reviewer-selected-assessment-v61-2026-11-01/`.
It contains the exact cases, admitted spans, source provenance, 65-unit gold,
sixteen exact pairings, relation flags, sixteen prepared requests and wire payloads,
response schemas, scoring/stops/budget, raw metadata and source fingerprints.
`plan.json` seals these files, the public plan and the completed local verification.

The freeze binds **1,108 historical/runtime source fingerprints**. Verification
passes **236 offline tests**: 89 new comparison tests, 22 existing gateway/contract
tests, 41 staged-handoff regressions and 84 delivery/usage regressions. Ruff
lint/format and strict mypy pass on **eleven local scripts**. A final explicit-import
typing fix references the same existing module; seventeen payload/budget checks
were repeated and every prepared request rebuilt identically. The prior SA/SO
result replay also passes without changing its evidence or conclusions.

Preparation records retain the interrupted sandbox check, initial type-check
failures and corrected answer-leakage test. That test initially rejected legitimate
`rationale` fields already present in source context; the corrected test checks
the newly supplied admitted list while preserving the original source bytes.
No failed check is counted as a pass, and no request was changed to satisfy it.

Verification covers exact control parity, selection provenance, no answer leakage,
all-unit validation, citation and explanation failures, condition/global stops,
terminal usage, ledger tampering, resume rules, inspection sealing and scoring.
Ruff, strict mypy, offline test counts and source-preservation results are recorded
in the verification report, preparation closure and authoritative tracker.

```powershell
.venv/Scripts/python.exe -X utf8 data/diagnostics/reviewer-selected-assessment-v61-2026-11-01/freeze.py verify
```

No live approval file or live-run directory is created during preparation. Live
execution must bind a new explicit approval to this plan hash, payload, destination
and ceiling. **Step 19 IN PROGRESS; Step 20 NOT STARTED; production prompts
unchanged; inference PAUSED pending approval; canary ON HOLD.**
