# BS/PO source-provenance generalization results

Date: **2026-10-29**. **40/40 approved calls completed; zero retries.**
Production **prompt 61 / graph 9 / fulfillment policy 1** unchanged. Full workflow
canary **ON HOLD**; further inference **PAUSED**.

**PO answered all twenty target cases correctly and recovered all three BS target
failures.** All sixty PO premises were independently inspected as correct and
grounded, including the eight fresh families in both presentation orders. The
frozen overall screen nevertheless returns **retain limited evidence, no
advancement**: explanation-precision annotations prevent the required perfect
assignment/craft grounding and no-loss result. These annotations concern claims
of verbatim textual identity, not lost story events or demonstrated writing-quality
regressions. The distinction matters when interpreting this useful target result.

The [frozen plan](../handoffs/reviewer-provenance-frozen-plan-2026-10-29.md) and
[preceding local audit](../handoffs/reviewer-production-scope-audit-2026-10-28.md)
remain unchanged. The earlier [BS/PO/ER comparison](reviewer-source-obligations-v61-results-2026-10-28.md)
retains its own scores and 0.40.12 baseline.

## Execution and inspection

The user approved full fictional prose/context to Ollama Cloud through the local
daemon. The runner reserved and dispatched exactly **forty** calls, twenty per arm,
with no retry, replacement, repair or reallocation. The first eight historical
sentinels delivered **4/4 valid responses per arm**, permitting continuation. All
forty responses finished normally and validated. No terminal stop fired.

Every call used `deepseek-v4.1-flash:cloud`, high thinking, temperature 0.2,
top-p 0.95, seed 20261022, context 40,000, non-streaming and no format override.
All **81 daemon-version observations** matched **0.40.13**; every selected-model
metadata check matched the frozen baseline. The digest remained
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
The eight historical K2/M5 wire requests replay exactly. This does not make their
earlier 0.40.12 execution runtime-identical to this run or test the daemon update's
effect.

Execution records were sealed before exporting the masked inspection packet.
All **40 final reports, 280 component reasons and 60 PO primitive judgments** were
read against complete original/revision prose and supplied context. Notes were
sealed before opening the trial key. Arm/order/trial identifiers were hidden, but
ledger shape and familiar scenes can identify treatment or family: this is an
assistant source audit with partial masking, not fully blind human review. Model
thinking was not used as semantic evidence.

## Target judgments and controls

| Measure | BS | PO |
| --- | ---: | ---: |
| Valid deliveries | 20/20 | 20/20 |
| Correct and grounded targets | 17/20 | 20/20 |
| Historical targets | 3/4 | 4/4 |
| Fresh targets | 14/16 | 16/16 |
| Correct non-target component labels | 120/120 | 120/120 |
| Usable non-target components, conservative primary inspection | 118/120 | 115/120 |
| Fully usable reports, conservative primary inspection | 17/20 | 17/20 |

PO also passes **60/60 primitive judgments**, both source/event projections for
**20/20 targets**, and all sixteen fresh targets. Across both arms, the actual
endpoint violations are recognized **40/40**, all **40 conditionals** are usable
(36 supported and four unsupported), and all **80 craft/qualification components**
are usable. All four historical M5 targets retain uncertainty about the unavailable
appendix. The seven conservative precision flags are confined to discovery/decision
explanations; all **240 non-target labels** remain correct.

| Family / source contrast | BS usable targets | PO usable targets |
| --- | ---: | ---: |
| K2: missing observation time | 1/2 | 2/2 |
| M5: unavailable appendix in declared S | 2/2 | 2/2 |
| N1: identity and common time in separate records | 2/2 | 2/2 |
| N2: logging time, not observation time | 2/2 | 2/2 |
| N3: planned timing, not observed compliance | 2/2 | 2/2 |
| N4: lossy summary cannot replace unavailable full appendix | 2/2 | 2/2 |
| N5: equally authoritative conflicting clocks | 0/2 | 2/2 |
| N6: coat/no-scarf predicates are compatible | 2/2 | 2/2 |
| N7: nonunique name does not establish identity | 2/2 | 2/2 |
| N8: separate record establishes different observation times | 2/2 | 2/2 |

The three matched recoveries are **K2-RO, N5-OR and N5-RO**. All are label
recoveries; the corresponding BS explanations already identify the relevant
source facts. There are no protected target losses. The two orders are repeated
presentations of one family, not independent stories or repeated random seeds.

For **K2-RO**, BS says no supplied text fixes a common instant but labels the
complete source-sufficiency claim *uncertain*. Under the frozen contract,
complete-source insufficiency is *unsupported*, while the event relation remains
uncertain. PO reports established identity/opposition and unestablished time; the
application derives those two different labels correctly.

For **N5 in both orders**, BS accurately describes Red's common time and Blue's
different times with no precedence, then labels source sufficiency *unsupported*.
The frozen contract preserves that explicit unresolved source conflict as
*uncertain*. PO reports time as *conflicted* and derives uncertain source/event
projections. The observed advantage is therefore in the premise/status interface
plus application projection, not evidence that PO discovered facts BS overlooked
or that the model's internal reasoning mechanism has been identified.

## Why the overall screen remains unpassed

The primary inspection conservatively retains **seven precision annotations in
four reports**. They are not seven incorrect story judgments.

| Capture | Components | Finding |
| --- | --- | --- |
| C-PO-N8-OR | C01.A01, C01.A02 | Two definite false word-for-word comparisons with named assignment references |
| C-BS-N5-OR | C01.A01, C01.A02 | Two ambiguous uses of “verbatim” |
| C-PO-N2-OR | C01.A01 | One ambiguous use of “verbatim” |
| C-PO-N4-OR | C01.A01, C01.A02 | Two ambiguous uses of “verbatim” |

For the definite example, the response says R006 repeats C002 “word for word.”
The actual texts are:

- **C002:** “Luca notices that the repair form allows replacing the original tuning dial.”
- **R006:** “Luca noticed that the repair form allowed replacement of the original tuning dial.”

The assigned meaning is retained, but the asserted textual identity is false.
The second comparison likewise changes tense and includes an extra “the.” These
facts are machine-checkable and do not require a human story reviewer to find them.

The other five “verbatim” formulations have an ambiguous comparison target. Their
canonical assignment text differs, but the **original prose sentences are copied
exactly into the revisions**. That original-to-revision reading is defensible.
They receive qualified uncertain annotations in the conservative primary view,
not a claim that the model invented story content. Phrases such as “retains the
exact assigned discovery” without a literal-text identity assertion are evaluated
for the retained fact, not punished for a tense change in a paraphrase.

All seven findings preserve correct retained-meaning judgments. No finding says
these prose sentences need rewriting. Qualified craft readings remain accepted;
for example, an original-version unsigned sheet is valid evidence about that
version when a craft claim does not assert that the revision remains unsigned.
The unestablished-timing ledgers with empty citations also remain acceptable under
the frozen interface after full visible-source inspection; absence is not
converted into fabricated positive evidence.

| Interpretation | Usable assignment/craft components | Protected PO-loss pairs | Result |
| --- | ---: | ---: | --- |
| Conservative primary notes | 193/200 | 3 | Limited evidence; no advancement |
| Accept five ambiguous original-copy readings | 198/200 | 1 | Limited evidence; no advancement |
| Core retained meaning only; exclude all seven exactness assertions | 200/200 | 0 | Diagnostic generalization signal only |

The primary loss pairs are N2-OR, N4-OR and N8-OR. The machine report lists thirteen
overlapping whole/component grounding-loss entries for those three pairs; these
are not thirteen independent defects. Accepting ambiguous readings leaves only
N8-OR. The core-meaning-only view changes explanation treatment, **not any target
label, primitive status, source gold or matched recovery**. It is explicitly a
post-inspection sensitivity, not a replacement result or production qualification.
The two explicit text-equality errors remain recorded even in that sensitivity.

## Latency, tokens and limits

| Resource | BS, 20 calls | PO, 20 calls |
| --- | ---: | ---: |
| Reported input tokens | 190,540 | 209,308 |
| Reported combined generated tokens | 67,807 | 83,507 |
| Active request seconds | 338.17 | 412.55 |
| Median request seconds | 15.46 | 19.90 |
| Median generated tokens | 2,936.5 | 4,080.5 |
| Seconds per fully usable report, primary scoring | 19.89 | 24.27 |
| Generated tokens per fully usable report, primary scoring | 3,988.65 | 4,912.18 |

For equal call counts, PO used **9.85% more input tokens, 23.15% more generated
tokens and 21.99% more active request time**. Median paired PO/BS ratios were
1.317 for elapsed time and 1.417 for generated tokens. These descriptive measures
are not a stable performance guarantee. Both arms used high thinking; this run
does not estimate thinking-versus-nonthinking overhead.

Total usage was **399,848 input / 151,314 generated tokens / 750.72 active seconds**.
Per-call maxima were **10,790 input / 8,979 generated tokens / 46.59 seconds**,
within the frozen **24,000 / 16,000 / 600** limits and all aggregate reservations.
Active request timing excludes metadata/fingerprint checks and analysis work.
All forty reported nonempty thinking, but reasoning/final token splits remain
unknown; generated totals are counted once. Effective sampling is unverified.

The archived $0.30/$1.20-per-million reference gives **$0.3015312**. This is not a
verified current tariff or actual billed cost; billing remains unknown.

## Verification, evidence and next work

**76 post-run offline tests pass**, with Ruff lint/format and strict mypy on eight
analysis scripts. Tests block real HTTP and replay all forty raw responses, exact
requests, cell seals, version observations, inspection bindings, accounting,
projections and sensitivity invariants. The frozen preparation's **455-test**
record remains intact; its **102 artifacts and 7,489 historical fingerprints**
verify unchanged. The first post-run check passed all 76 tests but found one
strict-typing annotation issue in the note serializer; an explicit string
conversion fixed it without changing the notes. Both verification attempts are
retained. No application code changed, so unrelated application/build suites were
not rerun.

Private evidence:

- `data/diagnostics/reviewer-provenance-v61-2026-10-29/`: frozen plan, approval,
  sources, gold and exact requests.
- `data/diagnostics/reviewer-provenance-v61-2026-10-29-live/`: forty reservations,
  raw responses, usage, metadata/version observations, receipts and cell seals.
- `data/diagnostics/reviewer-provenance-v61-2026-10-29-analysis/`: execution
  manifest, masked export, source facts, explicit adjudications, sealed notes,
  results, precision sensitivity, resources and verification evidence.

Retain PO as **promising source-provenance diagnostic evidence**, while keeping
the primary no-advancement decision. Before more inference:

1. Preserve the three recovered BS/PO pairs and the definite/qualified precision
   captures as local regression evidence. Keep semantic failures, false textual
   equality and ambiguous phrasing distinct.
2. Audit the evaluation contract locally: distinguish semantic retention from
   exact copying, define when an explanation's precision error is material, and
   make actual text-equality checks application-owned where needed. Freeze any
   revised rubric prospectively; do not rewrite these results or ask humans to
   count wording differences.
3. Continue the production-scope audit on existing immutable artifacts. The
   successful comparison uses authored obligations, observation-pair IDs and
   source inventories. It does not validate automatic claim extraction, authority
   assignment, completeness detection or free-form production reviewer inputs.
   Require a materially new, locally supported hypothesis before another live run.

No additional inference is needed merely to confirm the word-for-word mismatches.
No writer calls, prose repairs, selective-thinking integration or workflow canary
were authorized or performed. Human assessment still owns feel, flow, character
and story-breaking details; the nine earlier ties and human checkpoint remain
unchanged. All fourteen issue bodies and user-posted GitHub links are preserved;
no external issue was edited or closed. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
