# SE/BS/ER source-sufficiency comparison results

Date: 2026-10-28. **COMPLETE — 36/36 calls, twelve per form, zero retries.**
Frozen decision: **`retain_limited_evidence_no_advancement`**.

The direct bounded-source wording **BS recovers both contemporary SE label
failures in the fresh bicycle-workshop family L1, but neither failure in the
known costume-room family K2**. Correct and usable targets are **SE 8/12,
BS 10/12 and ER 12/12**. This is a limited, family-specific recovery signal.
The frozen requirement for recovery in both K2 and L1 is not met.

All **36 reports are structurally valid**. All **12 known-time targets** and
**36 conditional components** pass. The remaining target failures recognize
missing timing in their explanations while returning `uncertain` for a claim
whose prospective source-sufficiency gold is `unsupported`. More explicit
bounded-source wording therefore helps in one family and remains insufficient
in another. It is not qualified for production.

The [original freeze](../handoffs/reviewer-source-sufficiency-frozen-plan-2026-10-27.md)
was executed under the user's approved
[Ollama 0.40.12 amendment](../handoffs/reviewer-source-sufficiency-baseline-amendment-2026-10-28.md).
Production **prompt 61 / graph 9 / fulfillment policy 1** is unchanged. Selective
production thinking remains deferred; further inference is **PAUSED** and the
full workflow canary remains **ON HOLD**.

## Execution integrity

- **36 reservations, 36 dispatches, 36 completed responses**; no probe, retry,
  replacement, terminal failure, truncation or unused allocation.
- The first-twelve delivery sentinel passes: **4/4 valid for each form**, with
  no repeated blocking signature. All subsequent reports also validate.
- All **73 runtime daemon-version observations** match **0.40.12**. Selected
  DeepSeek metadata stays unchanged, including digest
  `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
- All forms request high thinking and return nonempty thinking. Thinking text
  is excluded from semantic inspection; its presence does not prove an internal
  reasoning process or establish the cause of a verdict.
- The original preparation used **zero calls**. Its seal remains intact. All
  **56 experimental input files**, including **36 prepared requests**, remain
  byte-identical under the amendment. All **12 historical SE/ER wire controls**
  remain exact. The changed version baseline adds no inference allowance.
- The amended plan binds **84 artifacts / 5,833 historical fingerprints**. Its
  SHA-256 is
  `9db25f8455d6a3aa69d4d17aaeab368cbbd8c57540126f10ca5558a0b5e5c539`.
  The original parent is
  `f584207f9f58be93cd4ae6341095dc6b35d31ff75c7aafcc38b2b1ca7a75a708`.

The version amendment changes the expected daemon version and its verification
fixtures and approval binding. It preserves cases, instructions, claims, gold,
scoring, stops, schedule and budget. Earlier 0.40.11 results remain historical;
this run does not isolate the effect of the daemon update.

## Frozen scores

“Usable” requires a correct label and complete, source-supported explanations
and citations addressing the exact claim object. All attempts remain in the
denominators. SE/BS assess source entailment or sufficiency; ER assesses the
event relation. Their prospective gold differs on unknown-timing cases.

| Measure | SE | BS | ER |
| --- | ---: | ---: | ---: |
| Valid reports | 12/12 | 12/12 | 12/12 |
| Correct primary target labels | 8/12 | 10/12 | 12/12 |
| Usable targets | 8/12 | 10/12 | 12/12 |
| Usable whole claims | 30/36 | 34/36 | 36/36 |
| Usable components | 78/84 | 82/84 | 84/84 |
| Usable non-target components | 70/72 | 72/72 | 72/72 |
| Completely usable reports | 7/12 | 10/12 | 12/12 |

Two qualified SE craft-explanation concerns affect the strict whole/component
counts below; they do not change any target label or target usability.

| Family and source condition | SE, both orders | BS, both orders | ER, both orders |
| --- | --- | --- | --- |
| K2: hook inventory; timing absent | Uncertain; fails source gold | Uncertain; fails source gold | Uncertain; passes |
| J2: bakery lamp; timing absent | Unsupported; passes | Unsupported; passes | Uncertain; passes |
| K1: ferry grille; timing explicitly unresolved | Unsupported; passes | Unsupported; passes | Uncertain; passes |
| L1: fresh wheel-stand latch; timing absent | Uncertain; fails source gold | Unsupported; passes | Uncertain; passes |
| L2: fresh transmit lamp; explicitly identical instant | Supported; passes | Supported; passes | Supported; passes |
| L3: fresh biscuit-box seal; explicitly two hours apart | Unsupported; passes | Unsupported; passes | Unsupported; passes |

BS has **two label recoveries in L1 out of two valid matched opportunities** and
**zero in K2 out of two**. Both L1 SE explanations already identify missing
timing accurately, so these are **label recoveries, not source-grounding
recoveries**. J2/K1 successes are alignment with successful contemporary controls;
they earn no recovery credit. The two orders are repeated observations of one
family, not two independently authored stories.

The BS/ER unknown-timing discrimination count is **6/8 matched pairs**. The
known-time controls are **12/12** and the conditional controls **36/36**. All
assignment and defensible-craft primary labels remain supported. There are
**no protected SE-to-BS or SE-to-ER paired-loss flags**; this directional result
does not erase SE-only concerns or the BS target failures.

The exact failed screens are **`all_BS_targets`** and
**`known_and_fresh_recoveries`**. The result is neither complete recovery nor
alignment without a reproduced failure: SE failures recur, and BS recovers only
one of the two required families.

## Source inspection and precision limits

All **36 valid masked reports, 108 whole reasons and 252 component reasons**
were inspected against the complete original/revision/context packets. Notes
were sealed before decoding trial identities. The review view excluded
arm/order/trial metadata, resource data and thinking. Claim form and recognizable
scene content remained visible, so this was a partially masked assistant factual
audit, not blind human literary-preference testing.

All target explanations identify the relevant source condition accurately.
For K2, both SE and BS say the supplied entries do not establish simultaneity;
their raw component judgments are nevertheless `uncertain`. The whole-claim
aggregation faithfully retains those judgments. It does not create the mismatch,
and the supported conditional is not substituted for proof of observed timing.
No output is repaired or silently relabelled.

Two craft explanations retain qualified precision annotations:

| Capture | Source and explanation | Treatment |
| --- | --- | --- |
| `C-SE-L2-RO`, C03.A01 | R018 says Ben lets go **before** Rosa raises the glass; the reason compresses this to helping **until** she raises it | Qualified timing concern; practical-care interpretation and primary label remain supported |
| `C-SE-L1-OR`, C03.A01 | O016–O018 show a stool, demonstration and Tavi copying the movement; the reason says Ivo guides **Tavi's hand** | Qualified attribution concern; figurative instructional guidance is possible, but physical guidance is not explicit |

These are not findings of proven invented events or weak stories. A sensitivity
check treats both explanations as adequate without changing labels, sources,
gold or delivery. SE then has **32/36 usable whole claims, 80/84 components,
72/72 non-target components and 8/12 completely usable reports**. BS/ER targets,
the L1-only recoveries and the no-advancement decision remain unchanged.

The inspection also records the word “verbatim” as overly strong surface wording
in assignment explanations for BS/L1/OR, SE/L3/RO and BS/L3/RO where phrasing or
tense differs. The underlying assigned facts are faithfully retained. This
indirect restatement is not scored as a different event or a missing material
claim part. Exact quotation bindings remain valid. This distinction prevents
small wording cautions from becoming claims about story quality.

Adequate alternative witnesses are accepted; there is no requirement to match
one withheld citation list. A literal conditional needs no observation of its
antecedent, and a defensible craft interpretation need not be uniquely compelled.

## What the evidence supports

**The bounded-source formulation has a real within-run recovery in L1.** With
the same packet, neighboring claims, settings and high-thinking model, the SE
target is uncertain and the BS target unsupported in both orders. The source
explanations agree about missing timing. The observed change is therefore at
the verdict level under this formulation.

**It does not generalize to K2 in this comparison.** Both K2 BS captures repeat
the same verdict/explanation mismatch. Calling the evidence set complete and
asking directly whether it is sufficient does not by itself resolve this family.
The successful conditional responses show that the model can state the literal
incompatibility under an assumed common instant. They do not explain why the
source-sufficiency verdict remains uncertain.

**A single neighbor-cue explanation is insufficient.** K2 and L1 both retain
referent qualifications, yet BS differs between them. J2/K1 retain timing
qualifications. Those cues are fixed within family and were not experimentally
crossed. Family, predicate wording, negation/occupancy language and other context
differences remain possible contributors; none is isolated as the cause here.

**Delivery succeeded throughout this run.** Earlier forbidden-field failures did
not recur. One clean batch does not establish a permanent delivery fix, nor can
it attribute the absence of failures to Ollama 0.40.12. No provider causal test
was conducted. The semantic failures are present in completed, valid final
responses with intact requests and unchanged model metadata.

ER's 12/12 usable targets remain useful diagnostic evidence for this narrower
event-relation task. These scores do not qualify an ordinary production critic,
rank overall model quality, demonstrate better writing, or authorize a writer
revision or a production thinking change.

## Resources

All forms use high thinking. Generated counts are the provider's combined
reported output totals, counted once. Reasoning/final-token splits and actual
billing remain unknown for all 36 responses.

| Measure | SE | BS | ER |
| --- | ---: | ---: | ---: |
| Input tokens | 112,408 | 112,588 | 112,272 |
| Generated tokens | 39,239 | 39,215 | 35,302 |
| Active call seconds, total | 174.887 | 174.445 | 153.611 |
| Active seconds, median | 14.466 | 12.897 | 10.631 |
| Generated tokens per completely usable report | 5,605.6 | 3,921.5 | 2,941.8 |
| Active seconds per completely usable report | 24.984 | 17.444 | 12.801 |

Totals: **337,268 input tokens, 113,756 generated tokens, 502.942 active seconds**.
Largest call: **9,681 input tokens, 5,336 generated tokens, 24.144 active seconds**,
all within the frozen 24,000 / 16,000 / 600 per-call limits and aggregate budget.
The rough preflight quarter-byte estimate was not an actual tokenizer count.

At the archived reference rates, the total estimate is **$0.2376876**, below the
**$0.95040** reference reservation. This is not an invoice or confirmation of
current pricing. Active time excludes local hashing, validation and audit work.
The three forms ask different questions; these descriptive resource figures
are not a thinking-on/off experiment or a production latency qualification.

## Verification and next work

The version amendment passes **419 offline tests**, Ruff lint/format and strict
mypy on fourteen scripts. The initial run of those checks caught stale 0.40.11
expectations in version-test fixtures; those were corrected and the entire suite
passed before inference. Post-run verification passes **57 offline tests**, Ruff
lint/format and strict mypy on seven analysis scripts. It replays all 36 captures,
requests and cell seals; checks approval/version/budget bindings, masked notes,
source offsets, denominators, recoveries and precision sensitivity; and verifies
the historical fingerprints. Post-run checks make no model or metadata calls.

Recommended local work before another experiment:

1. Preserve the four K2 source-claim failures, the two L1 SE failures and matched
   BS recoveries as explicit local regressions. Retain the two qualified craft
   wording captures separately from label failures and delivery errors.
2. Audit the K2/L1 contrast with authored minimal cases and an explicit account
   of object identity, opposite predicates, observation-time evidence and source
   completeness. Check whether occupancy/negation wording or scope-to-verdict
   mapping could explain the contrast. A generic missing-time keyword must not
   silently rewrite either an event verdict or a source-sufficiency verdict.
3. Require a materially different, locally justified hypothesis before more
   inference. One candidate to assess locally is an explicit typed claim and
   source-obligation representation, with any application-owned projection
   restricted to validated premises and complete source scope. This is a proposal
   for audit, not a production implementation or approved live experiment.

Preserve uncertainty when source coverage is incomplete. Keep interpretations of
emotion, flow and character separate from factual source obligations; a stylistic
reading must not become a mandatory rewrite merely because a mechanical check is
possible. The nine prior human ties and all historical scores remain unchanged.

Private bundles:

- Original: `data/diagnostics/reviewer-source-sufficiency-v61-2026-10-27/`.
- Amendment: `data/diagnostics/reviewer-source-sufficiency-amendment-v61-2026-10-28/`.
- Captures: `data/diagnostics/reviewer-source-sufficiency-amendment-v61-2026-10-28-live/`.
- Inspection, results, sensitivity and verification:
  `data/diagnostics/reviewer-source-sufficiency-amendment-v61-2026-10-28-analysis/`.

The authoritative tracker and issue index are updated in this change. All fourteen
issue bodies and user-posted GitHub links remain intact; no external issue is
edited or closed. **Step 19 remains IN PROGRESS; Step 20 NOT STARTED.**
