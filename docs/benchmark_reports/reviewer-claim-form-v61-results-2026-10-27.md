# ER/SE claim-form comparison results

Date: 2026-10-27. **COMPLETE — 24/24 calls, twelve per form, zero retries.**
Frozen decision: **`retain_limited_evidence_no_advancement`**.

The [approved plan](../handoffs/reviewer-claim-form-frozen-plan-2026-10-27.md)
tested an event-relation claim (ER) against a source-entailment claim (SE), using
the same DeepSeek high-thinking reviewer, EC instructions and source packets.
**ER has 12/12 correct primary target labels; SE has 8/12.** This supports retaining
claim-form sensitivity as diagnostic evidence. It does not satisfy the complete
discrimination screen: SE adds forbidden fields twice and uses uncertain instead
of the prospective unsupported label in both fresh hook-inventory comparisons.

These forms ask different questions and have different prospective gold. Their
score difference is not a general model ranking, a historical rescoring or a
demonstration of better prose. Production prompts and routing remain unchanged;
selective production thinking is deferred and the full workflow canary is **ON HOLD**.

## Execution integrity

- Exactly **24 reservations / 24 dispatches / 24 completed responses**. No probe,
  retry, replacement, terminal stop, HTTP failure or truncated finish.
- The first-eight sentinel passes: **SE 3/4 valid, ER 4/4 valid**, without a repeated
  ER blocking signature. All remaining frozen cells execute.
- All **49 daemon-version observations** match **Ollama 0.40.11**. Selected DeepSeek
  metadata remains frozen, including digest
  `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
- Both forms request and return nonempty high thinking. Thinking is excluded from
  semantic inspection; its presence does not prove a particular internal process.
- All four historical EC J1/J2 SE wires remain exact. Within each pair, only the
  target proposition and corresponding whole-claim wording differ.
- The plan hash is
  `156b310ae74f31cc37337e7b3824c0d4472064ecc1979b83d417cf0a0b5083a1`.
  All **74 preparation artifacts / 5,234 historical fingerprints** verify.

## Frozen scores

Invalid attempts remain in denominators and earn no semantic credit. “Usable”
requires the correct label plus an accurate, complete explanation and citation
assessment addressing that exact claim object.

| Measure | SE | ER |
| --- | ---: | ---: |
| Valid reports | 10/12 | 12/12 |
| Correct primary target labels | 8/12 | 12/12 |
| Usable targets | 7/12 | 11/12 |
| Usable whole claims | 27/36 | 35/36 |
| Usable components | 67/84 | 83/84 |
| Usable non-target components | 60/72 | 72/72 |
| Completely usable reports | 7/12 | 11/12 |

The strict unknown-timing discrimination result is **4/8 matched pairs**, from
J1 and K1 in both orders. Before the two qualified precision annotations, **5/8
pairs have the intended primary-label divergence**. Seven pairs have two valid
deliveries; J2/OR has an invalid SE response. Presentation orders are repeated
observations of the same families, not independent new stories.

| Family | Observed result |
| --- | --- |
| J1 pool, explicitly unresolved | Both orders: SE unsupported, ER uncertain; both usable |
| J2 bakery, timing absent | OR: SE invalid, ER uncertain and usable. RO: correct SE unsupported / ER uncertain labels, with a shared qualified “then” precision concern |
| K1 ferry, explicitly unresolved | Both orders: SE unsupported, ER uncertain; both usable |
| K2 costume-room hook, timing absent | Both orders: SE uncertain and ER uncertain; SE fails its prospective source-entailment gold while recognizing missing timing |
| K3 sluice, identical instant | SE/OR invalid; the other three targets supported and usable |
| K4 museum latch, different times | All four targets unsupported and usable |

The known-time controls are **7/8 usable**, with the eighth unavailable because of
invalid delivery. Conditional controls are **22/24 usable**, and **all 22 valid
conditional components pass**. All valid non-target components pass. The assignment
and defensible-craft controls remain supported; there is no observed conditional
substitution or new acceptance of an unestablished simultaneous event among valid
reports. Those findings do not supply semantic credit for invalid responses.

There are **no protected SE-to-ER paired-loss flags**. That is directional: it does
not erase shared concerns, SE-only failures, or the requirement that both forms
deliver all reports. The all-delivery, unknown-pair, known-time-control and
conditional-total screens fail. The frozen no-advancement decision therefore stands.

## Delivery failures

Both failures return HTTP 200 with a normal stop and parseable JSON. They violate
the closed claim-object schema by adding a forbidden field to **each of the three
whole-claim objects**:

| Capture | Forbidden field | Values |
| --- | --- | --- |
| `C-SE-J2-OR` | `claim_id_note` | `C01`, `C02`, `C03` |
| `C-SE-K3-OR` | `components_note` | Empty string in all three objects |

There are **six forbidden-field occurrences**, not duplicate JSON keys. Neither
field name appears in any of the 24 frozen wire requests. The delivery audit finds
no duplicate keys, unknown references, duplicate references, eight-reference-union
overflow or 2,000-character reason overflow in these two captures. The extra fields
are sufficient for rejection. They were not removed, repaired or semantically
credited. This is a recurrence of closed-schema delivery failure with different
surface fields; it does not establish the internal cause or a provider fault.

## Source inspection and precision limits

All **22 valid masked reports / 66 whole reasons / 154 component reasons** were
inspected against their original/revision/context sources. Notes were sealed before
key decoding. Arm/order/trial metadata, resources and thinking were excluded from
the review view. Claim wording remained visible, so masking was partial; these are
assistant source judgments, not blind human literary-preference ratings.

Two final explanations, **SE/J2/RO and ER/J2/RO**, say the lamp was lit “and then
unlit.” The source orders the entries without dating the observations. “Then” can
mean entry order or imply an unsupported observation chronology. Both explanations
also recognize missing timing, and both reports separately say presentation order
does not establish observation time. The audit therefore records **qualified
precision concerns**, not proven invented chronology or a demonstrated failure to
notice temporal uncertainty. Their primary target labels are correct.

A sensitivity check relaxes both concerns without changing labels, delivery or
gold. Usable targets become **SE 8/12 and ER 12/12** and unknown discriminating pairs
become **5/8**. The decision remains `retain_limited_evidence_no_advancement` because
the two K2 label failures and two invalid reports remain. The strict annotations
and this sensitivity are both preserved; neither replaces the frozen primary scores.

Complete, accurate alternative witnesses remain acceptable. Prose can support an
explicitly supplied discovery/decision component; the inspection also checks its
assignment leaf and unchanged original sentence. A literal conditional does not
require proof that its antecedents occurred. Qualified craft does not require one
uniquely compelled interpretation. In SE/J1/RO, R014/R015 completely establish the
unknown-timing limit even though the additional true unreadable-stamps detail is
in uncited R013. This is not a rule requiring exact withheld reference lists or
every redundant witness. No new factual defect is inferred from ambiguous wording
where a supported reading exists.

## What this supports, and what remains unresolved

The paired J1/K1 results provide direct evidence that claim form affects the
reviewer's labels under the same source and EC instructions. J2/RO also has the
intended primary-label difference. All eight ER unknown-timing targets are uncertain,
and the four ER known-time targets preserve supported/unsupported distinctions.
The reviewer is not simply choosing uncertain for every relation.

K2 shows the remaining limit: **recognizing missing timing does not reliably yield
the prospective source-entailment verdict**. Both SE reasons correctly describe the
missing evidence, yet the labels remain uncertain. This is a failure against the
frozen SE contract, not evidence that the model invented matching or opposite times.
The run does not reveal which proposition the model represented internally.

The historical J2 SE text includes “actually establish” and a further clarification
excluding a merely conditional reading. Fresh SE wording uses “establish that they
describe/record.” K1 succeeds with the shorter form while K2 fails. Scene family,
timing presentation and SE phrasing are not fully crossed here. A single wording
cause, an inherent inability to reason about source sufficiency, and a general
provider explanation are not established. Historical uncertain gold and prior
scores remain unchanged; SE's new gold was explicit before execution.

The current evidence justifies retaining explicit event/source claim objects in
diagnostic design. It does not qualify automatic label correction, writer dispatch,
selective production thinking or whole-story improvement.

## Resources

| Measure | SE | ER |
| --- | ---: | ---: |
| Input tokens | 111,892 | 111,692 |
| Combined generated tokens | 33,297 | 38,819 |
| Active seconds | 197.594 | 206.237 |
| Median call latency | 13.302 s | 17.256 s |
| Median generated tokens | 2,754 | 3,439 |
| Seconds per strictly usable complete report | 28.228 | 18.749 |
| Generated tokens per strictly usable complete report | 4,756.7 | 3,529.0 |

Total usage is **223,584 input / 72,116 generated tokens / 403.831 active seconds**.
The median paired ER/SE ratios are **0.977× latency / 1.051× generated tokens**;
these are medians of paired ratios, not ratios of the arm medians. All 24
reasoning/final token splits remain unknown. Per-usable-report figures include
failed deliveries and depend on the explicitly reported source annotations.

Observed per-call maxima are **9,516 input / 5,083 generated tokens / 35.306 active
seconds**, all within the frozen limits. At the archived reference rates, the estimate is
**$0.1536144**; actual billed cost is unknown. Both forms use high thinking, so this
run does not compare thinking modes or establish a production efficiency gain.

## Verification and recommended next work

**44 post-run offline tests**, Ruff lint/format and strict mypy pass on four analysis
scripts. Checks replay all exact raw/wire captures, rejection boundaries, source
bindings, sealed notes and scores, budget/version accounting, prospective gold,
denominators, the delivery-field audit and precision sensitivity. Real HTTP is
blocked. The frozen 393-test preparation remains unchanged. Analysis makes zero
additional model or daemon calls; application build checks are inapplicable because
application code, dependencies and production configuration did not change.

Before another live proposal:

1. Preserve the two forbidden-field captures as local closed-schema regressions,
   including the distinction between duplicate IDs, redundant ID notes and empty
   component notes. Retain the qualified “then” examples alongside explicit
   entry-order and observation-order counterexamples.
2. Audit K2's source-entailment claim and whole-claim composition locally against
   the successful J1/J2/K1 forms. Make the event proposition, bounded-source
   sufficiency proposition and unknown-event interpretation explicit without
   changing historical gold or silently correcting model labels.
3. Require a materially isolated hypothesis before more inference. If the local
   audit supports a phrasing contrast, cross the SE forms within the same families,
   preserve an unchanged ER anchor, include fresh positive/negative controls and
   both orders, then freeze a separate bounded plan for approval. No follow-up
   requests or budget are prepared or authorized here.

Keep future story-quality work focused on human feel/emotion, flow, character and
story-breaking judgments with machine-prepared mechanics. These samples and scores
do not measure those outcomes or replace the nine prior human ties.

Private evidence lives in `data/diagnostics/reviewer-claim-form-v61-2026-10-27/`,
its `-live/` sibling and its `-analysis/` sibling. Execution, inspection, analysis
and documentation are sealed. The tracker and issue index are updated; all fourteen
issue bodies and posted GitHub links remain intact. No external issue is edited
or closed. Production **prompt 61 / graph 9 / fulfillment policy 1** and Blueprint
approval remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
further live calls PAUSED; full workflow canary ON HOLD.**
