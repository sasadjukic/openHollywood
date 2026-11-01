# VA/MA selected-premise assessment results — 2026-11-01

**Approved run complete: 16/16 calls, zero retries, all sixteen structurally valid
outputs. MA fails both frozen semantic gates. No production advancement.**

The authored-span VA control produces **24/24 grounded judgments**. Assessment of
the actual saved model selections, MA, produces **37/41 correct labels but only
30/41 grounded judgments**. Four judgments on additional claims are semantic false positives;
seven further judgments have substantively correct explanations but inadequate
citations. Four citation failures occur on exact claims that VA handles correctly.

Retain this as evidence that separate assessment can complete the actual selected
sets within the frozen delivery limits. It does **not** qualify a staged reviewer
or a writer handoff. Production prompt61 / graph9 / fulfillment policy1 remain
unchanged; further inference is **PAUSED** and the full workflow canary is **ON HOLD**.

## Execution and scope

The [frozen plan](../handoffs/reviewer-selected-assessment-frozen-plan-2026-11-01.md)
has SHA-256
`beeeeb915ca0d5a953e7e6c44b85f7174d9fec2fe48053d6a7c996d647c180b2`.
The user's approval authorized the exact full-prose/context/report/selection
payload to Ollama Cloud through the local daemon, within sixteen new calls.

All eight VA wire requests match their original controls exactly. MA changes only
the admitted selection list. Full sources, report fields, registry, assessment
instructions, response contract and model settings remain unchanged. All 41 saved
SO selections are assessed, including the overlapping premise and partial-field
quotes. There is no selector rerun, semantic deduplication or three-target substitution.

All calls use `deepseek-v4.1-flash:cloud`, high thinking, temperature 0.2, top-p 0.95,
seed 20261022, context 40,000, non-streaming and no format override. All **33 daemon
version observations** match **0.40.13**, and all **seventeen model checks** match
the frozen metadata. All sixteen inference responses are HTTP 200 with a stop
finish and nonempty thinking. No truncation, condition retirement, global terminal
stop, retry, repair, replacement or budget reallocation occurs.

H1/H2/F2/F4 are **previously seen cases**, each in both source orders, with one
attempt per cell. This is an assessment-stage diagnostic, not fresh generalization,
an end-to-end autonomous workflow test or a literary preference comparison. The
prior SA/SO ten calls and six retired cells, and the earlier SA/VA stop, are unchanged.

## Inspection and frozen decision

All **65 returned judgments** and their complete reasons/citations were inspected
against the source artifacts, full report fields and frozen selected-proposition
rules. Notes were sealed before decoding the shuffled review key. This was partial
assistant factual inspection: counts, unit identities and familiar cases reveal
provenance. It was not blind human review. Thinking text was excluded.

| Measure | VA: authored spans | MA: saved model selections |
| --- | ---: | ---: |
| Calls / structurally valid outputs | 8 / 8 | 8 / 8 |
| Assigned judgments | 24 | 41 |
| Correct support labels | 24/24 | 37/41 |
| Grounded usable judgments | 24/24 | 30/41 |
| Semantic false positives | 0 | 4 |
| Additional correct-label citation failures | 0 | 7 |

All sixteen exact field/quote pairs are evaluable. VA grounds **16/16** of those
matched units; MA grounds **12/16**, for **four paired grounded losses**. Therefore:

- **MA feasibility fails:** 30/41 grounded judgments versus the required 41/41,
  despite meeting the 8/8 valid-delivery requirement.
- **The paired requirement fails:** four losses versus the required zero.
- **Further staged evaluation is not qualified by this run's success rule.**
  Additional inference needs a materially different hypothesis justified locally.

The supplied selected propositions remain intact, and no new factualization of a
selected literary-opinion field was observed. That does not make the four semantic
inferences below valid. Quote identity, label correctness, citation coverage and
whole-relation reasoning remain separate measurements.

| MA case / order | Correct labels | Grounded judgments |
| --- | ---: | ---: |
| H1 PC | 6/7 | 6/7 |
| H1 CP | 6/7 | 2/7 |
| H2 PC | 4/5 | 2/5 |
| H2 CP | 4/5 | 3/5 |
| F2 PC | 4/4 | 4/4 |
| F2 CP | 4/4 | 4/4 |
| F4 PC | 4/4 | 4/4 |
| F4 CP | 5/5 | 5/5 |

VA grounds all three assigned units in every cell. F2/F4 retain the namesake
attribution and unavailable-source contrasts, purposeful decisions and independent
boundary criticism. Their success is useful diagnostic evidence, not evidence of
general reliability on longer or unseen stories.

## Four semantic false positives

**H1, both orders:** MA supports the claim that establishing a general handwriting
match consumes the next scene's specific private-flourish verification. The source
provides a general match in S309 and a planned idiosyncratic flourish in S215.
The current draft does not depict that specific verification. The reasons treat
the later verification as redundant or preempted, rather than establishing the
exact asserted event/relation. The no-match endpoint criticism remains separately
valid; rejecting this extra allegation would not erase that criticism.

These are **M-MA-H1-PC Q006** and **M-MA-H1-CP Q007**. The PC response cites the
correct two source locations and still makes the unsupported inference. The CP
response additionally cites S308, which contains only the ten-year realization,
instead of the comparison in S309. Correcting citation placement alone would not
fix this semantic failure.

**H2, both orders:** MA supports the claim that the next scene begins with Elara
already inside. It infers that temporal state from the interior location and her
cautious/frightened entry state, S225 and S221. The complete available next-scene
summary, S228, says she enters during the scene; location/affect do not establish
starting after entry. The independent current-scene prohibition in S307 is valid,
but does not support the compound claim's temporal premise.

These are **M-MA-H2-PC Q005** and **M-MA-H2-CP Q005**. They repeat the same inference
in both presentation orders. They are extra MA premises absent from the exact VA
matched set, so this is not evidence that VA would answer them correctly if asked.

## Seven further citation failures

All returned reference IDs exist in the correct frozen registry. The problem is
what those references substantiate. The substantive explanations describe events
present in the full source, but their cited locations miss required evidence.
Erroneous paragraph numbering is treated here as citation/localization failure,
not a second independent semantic error. No citations were repaired for scoring.

| MA cell / unit | Returned evidence problem | Missing coverage |
| --- | --- | --- |
| H1 CP Q002 | S308 contains only the ten-year realization | Journal retrieval/comparison establishing the decision: S309 |
| H1 CP Q003 | S308 does not contain the asserted match | Definitive handwriting comparison: S309 |
| H1 CP Q005 | S299 is the assignment; S305 is reading the warning; S306/S307 supply dates | The observed “Ten years” realization quoted in the reason: S308 |
| H1 CP Q006 | S308 does not show verification | Current-scene journal/card comparison: S309 |
| H2 CP Q004 | S339 ends with both boots still outside | Actual crossing and entry: S340 |
| H2 PC Q001 | S340 supplies entry alone | The selected bridge reasoning and preparation: S339 |
| H2 PC Q002 | S337/S338/S340 cover pull, outside inspection and entry | Required handle contact: S336 |

These are evidence-content judgments, not an exact gold-ID whitelist. For example,
H2/CP Q002 passes because its returned S336/S337 already cover both contact and
pull, even though an extra citation does not locate the later magnetic wording.
H2/CP Q001 passes the selected decision claim because S339 covers its reasoning and
preparation. Conversely, actual entry alone does not substantiate a selected claim
about *how* a decision was established. For H1/CP Q005, citing the required turning
point and the two dates does not cite the explicit observed realization its reason
quotes; this specific component gap was frozen before inference.

The **four exact-pair losses** are H1/CP Q002 and Q005, and H2/PC Q001 and Q002.
Their VA counterparts cite sufficient evidence. This establishes a regression on
identical assessment units in the broader MA request. The design changes both the
number and composition of selected claims, and contains one attempt per cell; it
does not isolate cognitive workload, sampling variability or a provider mechanism.

## Context preservation and complete relations

The application preserved all full fields and source/report versions. The three
predeclared contextual flags nevertheless remain distinct:

- **H1/CP:** the match and no-match requirement are judged separately. Their
  endpoint relation is not explicitly assessed in those reasons. The unrelated
  Scene-2-consumption inference cannot supply that missing judgment.
- **H2/CP:** Q001 incidentally calls the later crossing a boundary violation, so
  an explicit relation assertion is recorded. Its S338/S339 citations cover
  outside inspection/preparation, not the S307 obligation and S340 entry. Separate
  component labels cannot automatically repair that citation gap.
- **F4/CP:** Q004's reason explicitly compares opening before officer attendance
  with the sealed-until-attendance rule, citing S008 and S001. This is a grounded
  complete relation explanation beyond its narrower selected event.

Only F4/CP supplies a grounded complete explanation for its contextual flag. This
credit comes from the actual reason and evidence, not from conjunction of supported
member labels. Full context prevents loss of access to meaning; it does not ensure
that the assessor uses that context correctly.

## Resources

| Observed resource | VA | MA | New comparison total |
| --- | ---: | ---: | ---: |
| Calls | 8 | 8 | 16 |
| Input tokens | 70,498 | 70,890 | 141,388 |
| Combined generated tokens | 23,979 | 52,178 | 76,157 |
| Active call seconds | 100.45 | 206.19 | 306.64 |
| Archived-rate reference USD | $0.0499242 | $0.0838806 | $0.1338048 |

All counters pass the frozen consistency checks. Observed per-call maxima are
**15,458 input / 12,970 generated tokens / 53.70 seconds**, within the respective
24,000 / 16,000 / 600 limits. All sixteen original reservations are consumed as
attempts; no unused live slot remains. Actual billing and reasoning/final token
splits are unknown; the dollar figures use the archived planning rates only.

Across eight complete pairs, median generated **MA/VA ratio is 1.742** and median
active-time ratio is **1.635**. These are descriptive; the plan sets no efficiency
threshold for unequal workloads. MA assesses 41 units versus 24, so these ratios
do not isolate per-premise reasoning cost or establish end-to-end savings.

Including the already-used SO stage, the observed **selection + MA assessment**
path costs **sixteen calls / 133,890 input / 132,178 generated tokens / 451.50 active
seconds**, archived-rate reference **$0.1987806**. Eight of those calls are historical
selection calls, not additional calls in this approved sixteen-call comparison.
The eight new VA controls are separate diagnostic overhead. This staged total must
not be compared with authored spans as if their human selection work were free.

## Verification and next work

The read-only verifier replays the approval binding, all sixteen frozen wires,
raw envelopes, receipts, model/version observations, counters, sealed inspection
export, annotations and frozen scores. All **63 frozen files / 1,108 source pins**
remain unchanged. **235 post-run offline tests pass**: 88 comparison checks,
22 gateway/contract checks, 41 handoff regressions and 84 delivery/usage regressions.
The one preparation-only test requiring absence of live approval is deselected
because approval now exists; actual approval binding and the completed ledger are
verified separately. Ruff lint/format and strict mypy pass on **eleven frozen and
three analysis scripts**. The annotation reproducer also preserves all sealed
judgments. No frozen code or scoring rule changed. The full local records live under
`data/diagnostics/reviewer-selected-assessment-v61-2026-11-01/` and its `-live`,
`-inspection` and `-analysis` siblings. The publication closure records final
offline checks and document fingerprints.

Before more inference, I recommend a bounded local follow-up:

1. Preserve the four failing MA outputs and their corresponding VA controls as
   regressions: all seven correct-label citation gaps, four semantic false positives,
   four exact-pair losses and the three contextual-relation outcomes. Retain the
   positive F2/F4 judgments and original raw evidence without repairing their scores.
2. Audit the actual source-to-paragraph-to-reference presentation. Check the
   one-based nonempty-paragraph map against frozen wire data, including adjacent
   references and short standalone paragraphs. Evaluate whether application-owned
   exact-excerpt lookup can expose the missing evidence without silently changing
   selected scope, trusting a wrong claim, or granting whole-relation credit.
3. Keep the two semantic contrasts separate: general match versus specific flourish,
   and scene location versus starting-after-entry. Citation placement cannot solve
   the correctly located H1 false positive. Require a materially different, locally
   justified hypothesis before freezing another live comparison.

No next live budget is prepared or approved. Mechanical checks belong in application
code where possible; humans retain feel, flow, character and story-breaking judgments.
Neither accurate factual assessment nor a supported obligation authorizes unnecessary
prose rewrites. No issue is closed; CW-007/CW-013 remain directly implicated, and this
run's successful delivery does not close CW-008. No production code, prompt, writer
route, story prose or mandatory human checkpoint changed. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; inference PAUSED; full workflow canary ON HOLD.**
