# PO/EX semantic-retention and exact-copy results

Date: **2026-10-30**. **32/32 approved calls completed; zero retries.**
Production **prompt 61 / graph 9 / fulfillment policy 1** unchanged. Further live
calls **PAUSED**; full workflow canary **ON HOLD**.

**Both arms correctly handled all tested semantic contrasts. The added EX text
receipts did not demonstrate a precision benefit.** Each arm delivered 16 valid
reports, 112/112 semantically usable components and 48/48 correct, grounded source
premises. EX added two ambiguous “verbatim” assertions in one report; PO reproduced
no definite literal error that EX could recover. The frozen decision is therefore
**retain limited evidence, no advancement**, with
`ambiguous_referents_increased` as its only failed screen. There are no protected
semantic/source/craft losses and no demonstrated prose-quality regression.

The [frozen plan](../handoffs/reviewer-exactness-frozen-plan-2026-10-30.md),
[preceding local audit](../handoffs/reviewer-retention-materiality-audit-2026-10-30.md)
and [historical BS/PO results](reviewer-provenance-v61-results-2026-10-29.md)
retain their original evidence, scoring and conclusions.

## Execution and inspection

The user authorized full fictional prose/context and the frozen receipt payload
to Ollama Cloud through the local daemon. Exactly **32 calls were reserved,
dispatched and completed**, sixteen per arm, with no retry, replacement, output
repair or reallocation. Both arms passed the first eight delivery sentinels,
4/4 each. Every response returned HTTP 200, finished normally and validated;
no terminal stop fired.

All calls used `deepseek-v4.1-flash:cloud`, high thinking, temperature 0.2,
top-p 0.95, seed 20261022, context 40,000, non-streaming and no format override.
All **65 daemon-version observations** matched **Ollama 0.40.13**. Initial and
per-call selected-model metadata matched the frozen baseline, including digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
The four historical N8/N4 PO wire requests remained exact. The sole experimental
request difference was EX's four version-bound text comparisons.

The execution manifest was sealed before exporting shuffled reports. All
**32 final reports, 224 component assessments and 96 primitive assessments**
were inspected against full original/revision prose, canonical context and
declared source scope. This includes **288 leaf reasons**: six ordinary reasons
and three source-premise reasons per report. Notes were validated and sealed
before opening the trial key. Arm/order/trial identifiers were hidden, but
familiar scenes or wording can reveal treatment: this is a partially masked
assistant factual audit, not blind human preference review. Model thinking was
retained as opaque capture evidence and excluded from semantic inspection.

## Semantic results

| Measure | PO | EX |
| --- | ---: | ---: |
| Valid deliveries | 16/16 | 16/16 |
| Correct and semantically usable components | 112/112 | 112/112 |
| Correct and grounded source premises | 48/48 | 48/48 |
| Correct source/event projection pairs | 16/16 | 16/16 |
| Semantically usable whole claims | 48/48 | 48/48 |
| Semantically usable complete reports | 16/16 | 16/16 |
| Strictly grounded components, including precision | 112/112 | 110/112 |
| Reports passing the strict explanation view | 16/16 | 15/16 |
| Definite false literal comparisons | 0 | 0 |
| Ambiguous literal-comparison assertions | 0 | 2 |

All **36 fresh assignment components per arm** were usable. Across both arms,
all 32 separate conditionals and 64 craft/factual-qualification components were
usable. Both source orders produced the correct semantic outcomes for every family.

| Family | Contrast correctly handled by both arms in both orders |
| --- | --- |
| N8 | Retained discovery/decision, violated unsigned endpoint; a separate calibration record establishes different observation times. |
| N4 | Retained discovery/decision, violated unsigned endpoint; the lossy summary cannot replace the unavailable full appendix. Complete-source sufficiency remains uncertain. |
| X1 | Paraphrased discovery and decision remain fulfilled; the ending respects the endpoint. Explicit simultaneous observations establish the relation. |
| X2 | Advice-seeking action expresses the assigned consultation decision; no removal is authorized. The observations occur at different times. |
| X3 | An exactly copied decision sentence belongs to a fictional heroine, while the real protagonist explicitly makes no such decision. Complete sources leave timing unestablished. |
| X4 | The quoted decision belongs to another person with the same name. The protagonist makes no decision; explicit common observation times are recognized. |
| X5 | “Decided not to consult” negates the assigned decision despite similar wording. The ending respects the boundary; observation times differ. |
| X6 | The real decision occurs, then is reversed. The earlier event remains true while the later sale violates the endpoint. Complete sources leave timing unestablished. |

X3 and X6 are especially useful controls: both contain exact assignment-text
matches, but only X6 narrates the protagonist's actual decision. Neither arm
mistook literal identity for fulfillment. Paraphrase and purposeful action were
also accepted without requiring the assignment's exact wording. These are useful
diagnostic abilities on authored cases; they do not establish automatic claim
extraction, production-source alignment or whole-story quality.

## The remaining precision finding

The sole affected report is **C-EX-N8-OR**, masked as `claim-review-031`:

- C01.A01: “R006 repeats the assigned discovery verbatim in the revision.”
- C01.A02: “R008 repeats the assigned decision verbatim in the revision.”

Each statement leaves the comparison source unnamed. The original prose and
revision are word-for-word identical at those passages. Their canonical assignment
wording differs. For example:

- **Assignment C002:** “Luca notices that the repair form allows replacing the original tuning dial.”
- **Original O006 and revision R006:** “Luca noticed that the repair form allowed replacement of the original tuning dial.”

The decision pair similarly changes *decides* to *decided* and adds *the* before
*repair*. Thus the original-to-revision reading is defensible, while an
assignment-to-revision identity assertion would be false. Following the frozen
rubric, the two findings remain **ambiguous**, not definite errors. Their strict
reason support is uncertain; their retained-meaning judgments have independent,
complete source support. No prose repair follows from these annotations.

The matched PO report makes ordinary retained-fact statements without “verbatim.”
The two EX annotations cause two strict component losses in **one matched report**,
not two independent scene failures. No source/event label or craft judgment is lost.

All other leaf reasons were also checked for text-identity claims. Statements
such as “repeats the discovery,” “exactly retains the decision” and “exactly
matching” an endpoint describe semantic retention or state compliance without
asserting word-for-word text equality. “Identical timestamp” describes the same
represented observation instant. The explicit adjudications record these
distinctions; no keyword-only classifier assigned precision failures.

There are **zero matched definite-precision recoveries** because the unchanged
PO control did not reproduce a definite literal error. Even accepting the two
ambiguous formulations would not demonstrate recovery. The observations do not
show that receipts reliably cause ambiguity, nor explain the model's internal
mechanism. They show that appending correct mechanical information did not ensure
explicit comparison scope in this one response. The absence of the earlier error
also does not prove that the underlying reliability problem is solved.

## Resources and limits

| Resource | PO, 16 calls | EX, 16 calls |
| --- | ---: | ---: |
| Reported input tokens | 159,648 | 195,816 |
| Reported combined generated tokens | 65,655 | 67,787 |
| Active request seconds | 294.93 | 316.15 |
| Median request seconds | 17.92 | 18.47 |
| Median generated tokens | 4,063 | 4,108 |
| Seconds per semantically usable report | 18.43 | 19.76 |
| Generated tokens per semantically usable report | 4,103.44 | 4,236.69 |

For equal call counts, EX used **22.65% more input tokens, 3.25% more generated
tokens and 7.20% more active request time**. Median paired EX/PO ratios were
**1.022 elapsed / 1.075 generated**. These are descriptive results from one small
comparison, not stable performance guarantees. Both arms used high thinking;
this run does not measure thinking-versus-nonthinking overhead.

Total usage was **355,464 input / 133,442 generated tokens / 611.08 active seconds**.
Per-call maxima were **12,930 input / 6,653 generated / 39.08 seconds**, within the
frozen **24,000 / 16,000 / 600** limits and all aggregate reservations. Active
request timing excludes metadata and fingerprint checks, waiting between requests,
and analysis work. All 32 responses had nonempty thinking; reasoning/final token
splits remain unknown and generated totals are counted once. Effective sampling
is unverified. The archived $0.30/$1.20-per-million reference gives **$0.2667696**;
it is not a verified current tariff or actual billed cost.

## Verification and next work

**65 post-run offline tests pass**, with Ruff lint/format and strict mypy on six
analysis scripts. Tests block real HTTP and replay every raw response, request,
cell seal, annotation binding, projection and resource total. They also reject
tampering with ambiguous-assertion spans, referents and materiality, and preserve
the separation between semantic success and an actual precision recovery.
The frozen preparation's **468-test** record remains intact; **95 frozen
artifacts and 8,294 historical fingerprints** verify unchanged. No production
code changed, so unrelated application and frontend build suites were not rerun.

Private evidence remains under:

- `data/diagnostics/reviewer-exactness-v61-2026-10-30/`: frozen inputs, approval,
  receipts, requests, scoring, budgets and stops.
- `data/diagnostics/reviewer-exactness-v61-2026-10-30-live/`: 32 reservations,
  exact wires, raw captures, metadata/version observations, usage and cell seals.
- `data/diagnostics/reviewer-exactness-v61-2026-10-30-analysis/`: execution manifest,
  source facts, masked export, explicit dispositions, sealed notes, results,
  statistics and verification evidence.

Retain **PO's semantic alignment as diagnostic evidence** and EX's result as a
negative result for the proposed precision benefit. Do not adopt the EX payload
or schedule another repeat on this evidence. Before further inference:

1. Preserve the N8 PO/EX pair as an ambiguity regression, alongside the successful
   fresh semantic contrasts. Keep the historical definite errors separate from
   this run's ambiguous wording.
2. Audit locally whether exact-copy statements should be rendered directly from
   application receipts with explicit source/target identifiers, instead of
   asking a model to restate mechanical results. Check the existing artifacts and
   interface without changing production prompts or rewriting prose.
3. Continue the production-scope work on how claims, source inventories and
   aligned spans would be obtained from immutable artifacts. These remain authored
   diagnostic inputs. Require a materially different, locally justified hypothesis
   before another live comparison.

No additional inference is needed to establish the literal comparisons above.
No writer calls, story revisions, selective-thinking integration or workflow
canary were performed. Human review retains feel, flow, character and
story-breaking details; the nine earlier human ties and Blueprint checkpoint
remain unchanged. All fourteen issue bodies and user-posted GitHub links are
preserved; no external issue was edited or closed. **Step 19 IN PROGRESS;
Step 20 NOT STARTED.**
