# Evidence-namespace and relation-polarity pilot results — 2026-10-25

**Completed: 32/32 calls, zero retries, no infrastructure or terminal stop. Both
frozen decisions are `retain_limited_evidence_no_advancement`.** The registered
citation arm improved delivery but failed its delivery threshold. Complementing
the relation claims produced no target recoveries and did not meet the protected
control or uncertainty requirements.

This executes the approved [frozen plan](../handoffs/reviewer-namespace-polarity-frozen-plan-2026-10-25.md)
on **Ollama 0.40.11 / `deepseek-v4.1-flash:cloud`**, sending the approved full
prose/context through the local daemon to Ollama Cloud. Production remains
**prompt 61 / graph 9 / fulfillment policy 1**. Further live calls are paused;
the full workflow canary remains **ON HOLD**. No writer was dispatched.

## Results under the frozen rules

| Measure | CA control | NC registered citations | CV control | CP complemented target |
| --- | ---: | ---: | ---: | ---: |
| Attempts | 8 | 8 | 8 | 8 |
| Structurally valid reports | **3/8** | **6/8** | **8/8** | **8/8** |
| Correct primary whole-claim labels | 9/22 | 13/22 | 18/24 | 18/24 |
| Grounded, complete, usable primary claims | **9/22** | **13/22** | **17/24** | **16/24** |
| Primary opportunities lost to invalid delivery | 13 | 4 | 0 | 0 |
| Fully usable reports, including secondary gold | 3/8 | 3/8 | 1/8 | 2/8 |

The N pilot has 44 primary and four secondary whole-claim opportunities; P has
48 primary opportunities. Invalid reports receive no salvaged claim or component
credit. Both B/C03 orders remain secondary in each N arm, with historical gold
unchanged; all four reports containing them are invalid. This classification
does not exempt B/C03 from the delivery boundary.

Among delivered reports, CA has **9/9** usable primary claims and NC **13/18**.
These are different selected subsets, not a causal comparison of semantic
accuracy. CA has **22/82** correct component labels over all attempted components;
NC has **43/82**. Among valid deliveries those counts are **22/22 and 43/50**.
A correct application-owned aggregate cannot conceal an incorrect component.

| Pilot/family | Control valid | Candidate valid | Control usable primary | Candidate usable primary |
| --- | ---: | ---: | ---: | ---: |
| N/H — observatory | 0/2 | 2/2 | 0/6 | 2/6 |
| N/W — fresh letterpress | 1/2 | 2/2 | 3/6 | 5/6 |
| N/B — costume workroom | 0/2 | 0/2 | 0/4 | 0/4 |
| N/V — instrument conservation | 2/2 | 2/2 | 6/6 | 6/6 |
| P/N — floodgate | 2/2 | 2/2 | 4/6 | 2/6 |
| P/X — fresh foundry | 2/2 | 2/2 | 5/6 | 6/6 |
| P/U — greenhouse | 2/2 | 2/2 | 4/6 | 4/6 |
| P/Y — fresh glass-negative archive | 2/2 | 2/2 | 4/6 | 4/6 |

## N: registered citations helped delivery, but did not qualify

CA fails on H in both orders, B in both orders, and W/RO. All five responses have
HTTP 200, normal `stop` completion, parseable JSON, the required fields and ordered
component IDs, and no duplicate JSON members. Their strict rejection is
**`unknown reference`**. There are **twenty forbidden-reference occurrences in
sixteen component evidence arrays**. All values exist elsewhere in the input:

- H uses the consultation task identifier and `story_blueprint`.
- W/RO uses the scene-plan artifact version ID.
- B/OR uses edit-group IDs and scene-plan/assignment artifact IDs.
- B/RO uses an edit-group ID, `scene_boundary` and the retention task identifier.

CA B/C03 also has unions of **twelve OR / eleven RO** distinct refs, including
eight valid prose refs in each. Those counts are inventory findings, not repaired
answers. No invalid response was trimmed, relabeled or partially accepted.

NC uses only valid registered refs in all eight captures, including its two
invalid reports. Those two reports fail **`whole-claim evidence union exceeds
eight`**: each B/C03 returns **fourteen valid refs**, eight prose plus six context
refs. Individual component arrays comply; their combined union does not.
The same eight-ref whole-claim limit applies to the combined O/R/C namespace.
Neither the output-token cap nor truncation caused these failures: the largest
output in the entire experiment is 950 reported tokens against an 8,000 cap.

NC has **three paired delivery gains**: H/OR, H/RO and W/RO. Only the two H gains
count toward the required four gains across at least two inherited families.
Contemporary CA provides sufficient opportunity in H and B, both orders, but B
does not recover. NC therefore fails both **7/8 minimum delivery** and the
**inherited delivery-gain screen**, although it delivers both fresh W orders.

No protected paired loss occurs where both arms deliver valid reports. This
does not imply that the newly delivered NC reports are semantically sound:

- **H, both orders:** C01.A04 still falsely endorses a contradiction between
  “not yet consulted” and rotation **before** consultation. Both statements keep
  consultation absent. The separate prohibition is genuinely violated. C01.A03
  and C03.A02 abstain on defensible craft readings because they are not compelled
  interpretations; the frozen standard requires defensibility, not unanimous
  reader agreement. These yield four whole-claim abstentions, including two on
  supported C03 controls. H/C02 remains usable in both orders.
- **W/RO:** C01.A03 correctly locates the tray endpoint and satchel action, then
  rejects the violation claim because the change is a failure to retain the
  required state. That is precisely the alleged violation. This is a new
  candidate error, not a paired semantic loss: CA/W/RO is invalid. W/OR is fully
  usable, and the empty-then-filled satchel relation is correctly rejected in all
  three delivered W reports.
- **V:** both arms correctly reject the “only handling” overclaim, retain the
  actual endpoint violation and preserve the qualified travel interpretation
  without inventing abandonment of the consultation plan, in both orders.

**Retain the bounded namespace-delivery evidence. Do not promote NC.** The
observed reduction in wrong-namespace citations supports the interface change
as a diagnostic direction; it does not establish a semantic repair or identify
which part of the registry/enum/instruction bundle caused the effect.

## P: consistent polarity reversal preserved the underlying mistakes

All sixteen reports deliver validly. The target results repeat in both source
orders:

| Family | CV raw target | CP raw target | CP normalized to original | Frozen target outcome |
| --- | --- | --- | --- | --- |
| N — absent authorization / opening | Supported | Unsupported | Supported | Both wrong |
| U — absent authorization / starting | Supported | Unsupported | Supported | Both wrong |
| X — same door, same instant, shut/open | Supported | Unsupported | Supported | Both correct |
| Y — common photographic time unresolved | Unsupported | Supported | Unsupported | Neither meets primary uncertain gold |

There are **two both-correct pairs, six neither-correct pairs, zero only-CV,
zero only-CP, zero delivery-unavailable pairs and zero target abstentions**.
No pair endorses both opposite assertions. Normalized target labels match in all
eight pairs. Thus this run does **not** show simple agreement with whichever
assertion is supplied; the false relation judgment survives logical complementation.
It does not reveal the model's internal reasoning mechanism.

CV falsely accepts the N/U relation in all four required cells, giving sufficient
contemporary opportunity. CP supplies **zero grounded target corrections**.
On N, its explanation still calls “not yet authorized” incompatible with acting
before authorization. On U it additionally narrows the complement of the whole
assertion to a denial of the action itself. U/RO explicitly says the false
contradiction premise is true; U/OR restates the true event/order without resolving
the asserted relation. An action can breach a rule or resolve while remaining
compatible with a fact that permission has not arrived.

The genuine same-instant contradiction in X is correctly identified in both
formulations and orders. That success matters: the model can reject the
complement of an actual incompatible-state claim. It does not rescue the N/U
errors, and the missing-time control does not pass.

### Correct labels did not always have usable explanations

CP changes only C02, but its unchanged **N/C01** control loses usability in both
orders while keeping the correct supported label:

- **OR:** after correctly describing unauthorized opening and the unchanged
  lamp, it says this “satisfies the mandatory authorization-before-opening test.”
  That reverses the explicit acceptance condition. This is a false explanation.
- **RO:** it accurately restates intention, authorization status, action and lamp,
  but stops at matching the claim's factual premises. It does not evaluate the
  material contractual-violation conclusion. This is incomplete coverage under
  the frozen rule, not an invented event.

CV **X/RO C03** has a defensible reason and correct label, but its structured
citation array omits the shut-door counterpart R011; it supplies only R012/R013/R017.
The reason mentions R011 in free text. That reference is not silently inserted
into the evidence array, so the complete relation lacks sufficient selected
citations. X/OR's sketch citation includes pressing hard enough to mark the bench,
which is itself tactile evidence; it is not rejected merely for omitting the
separate sound-in-teeth sentence.

These distinctions explain **18 correct labels versus 17 usable claims in CV,
and 18 versus 16 in CP**. The coverage and citation judgments are inspectable
assistant annotations, not deterministic truth tests. Even treating both marginal
omissions leniently would leave the unequivocal false N/OR explanation, all four
target failures and the failed Y calibration; neither pilot decision would change.

### Y: preserve the disclosed uncertainty limitation

The source explicitly leaves open whether the lamp photographs depict the same
instant or different visits. CV's unsupported answers explain that a same-time
contradiction is **not established**. That is a true account of the evidence and
fits the alternative meaning of unsupported disclosed before inference. It is
not credited against the unchanged primary **uncertain** gold and is not called
a fabricated timing fact.

CP's supported answers likewise say the depictions are **not asserted** to
contradict. That true observation does not establish that the complete assertion
is false: absence of support is not proof of its complement. Both CP reasons are
recorded as true but partial, with insufficient support for the complemented
target. No gold, prompt or historical score is changed after seeing the results.

P fails the **framing-signal, fresh uncertainty-control and protected-explanation
screens**, despite passing delivery. Retain these counterexamples; do not promote CP.

## Inspection, reproducibility and budget

All **25 valid reports, 75 whole-claim reasons and 72 component reasons** were
reviewed against complete original/revision/context packets. Notes bind exact
assessment, source, claim, component-map and registry hashes plus source quotes
or context leaves. Arm/order/trial IDs were masked; notes were sealed before the
mapping key was read. Source contents, known case design and response structure
can identify family/treatment, so this is a **partially masked assistant factual
audit**, not an independent blind human preference study. All seven invalid
captures also received an offline delivery audit without repair or semantic credit.

| Accounting | N | P | Combined |
| --- | ---: | ---: | ---: |
| Reserved / dispatched / completed calls | 16 / 16 / 16 | 16 / 16 / 16 | **32 / 32 / 32** |
| Reported input tokens | 102,932 | 58,612 | **161,544** |
| Reported output tokens | 8,522 | 3,912 | **12,434** |
| Active inference seconds | 29.161 | 17.593 | **46.754** |
| Archived-rate arithmetic estimate | $0.041106 | $0.022278 | **$0.063384** |

Actual billed cost remains unknown. The estimate uses the frozen reference rates;
it is not a billing statement or a newly checked price. All attempts stayed below
24,000 input / 8,000 output tokens / 300 active seconds; observed maxima were
**8,859 / 950 / 2.946 seconds**. Aggregate reservations were 768,000 / 256,000
tokens, 9,600 seconds and $0.53760 reference cost, with a $0.70 planning allowance.
There was no retry, reallocation, unreserved call or inference during analysis.

Both eight-call sentinels correctly continued: N had CA 1/4 and NC 4/4 valid;
P had 4/4 for both arms. Neither candidate repeated a blocking signature across
both sentinel families. Later B cardinality failures were recorded normally;
semantic outcomes never triggered adaptive stopping.

The initial and before/after-cell version observations are **65/65 matching
0.40.11**. Selected-model metadata/digest remains
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
Temperature 0.2, top-p 0.95, seed 20261022, thinking=false, stream=false and the
frozen schema-in-prompt requests remain unchanged. Preflight is metadata only.

**56 post-run offline tests pass**, together with Ruff lint/format and strict
mypy on three analysis scripts. Checks replay all 32 captures, reject all seven
invalid reports, verify budgets/stops/version observations and frozen sources,
reproduce sealed annotations/decisions, reject tampered bindings/quotes/context,
and preserve all fourteen issue bodies and posted GitHub links. Real HTTP is
blocked during tests. The earlier **230 preparation tests** remain recorded as
preparation evidence; they were not represented as fresh post-run tests. No
production/API/worker/frontend change requires a new application build.

Private evidence is retained locally and ignored by Git:

- `data/diagnostics/reviewer-namespace-polarity-v61-2026-10-25/`: unchanged frozen
  cases/requests/scoring/stops, plus the explicit approval record.
- `data/diagnostics/reviewer-namespace-polarity-v61-2026-10-25-live/`: all raw
  requests/responses, reservations, version observations, receipts and cell seals.
- `data/diagnostics/reviewer-namespace-polarity-v61-2026-10-25-analysis/`: execution
  manifest, masked export, sealed source notes/key, invalid-delivery audit in
  `results.json`, replay tests, verification, analysis seal and documentation closure.

Frozen plan SHA-256:
`c7f1793e4eb56912be0e2be4fc8d960b14c3d5ce4f160ed18460da234782a084`.
The frozen public plan and all 2,477 historical source fingerprints remain intact.

## Recommended local work before another live proposal

1. **Audit whole-claim evidence budgeting using both B/NC captures.** Preserve
   their fourteen-ref failures. Trace which refs establish each material component
   and which duplicate contextual obligations. Evaluate an application-owned,
   bounded citation-plan representation locally; do not trim model evidence or
   weaken the historical eight-ref contract. Valid identifiers and a sufficient,
   bounded evidence set are separate problems. Include W/RO's correct-source,
   wrong-violation label and H's craft abstentions as regressions.
2. **Make relation and negation scope explicit in local fixtures.** Preserve
   N/U's compatible status facts versus real rule/resolve violations, X's actual
   same-time contradiction, and U's whole-assertion versus event-only negation.
   Check that true event restatements and correct label inversion cannot pass a
   false relation. Add N/OR's reversed acceptance explanation and the incomplete
   control/citation cases without retroactively changing this run's scores.
3. **Resolve the epistemic label contract before proposing more inference.**
   Distinguish false, unestablished and explicitly unresolved claims, including
   their complements. Evaluate whether the application should own that mapping
   after separately receiving evidence sufficiency and relation judgments.
   Decide it locally, then freeze any later comparison with unchanged controls,
   fresh families and both orders. No next live budget is approved by this report.

These are diagnostic interface and evaluation recommendations, not a mandate to
make prose more literal or uniformly cautious. Preserve room for intention changes,
subtext, ambiguous timing and defensible craft interpretations. Future human review
should continue to judge feel/emotion, flow, character and story-breaking details,
with machines preparing mechanical evidence. This run contains no writer revisions
or new human preference results and changes none of the nine prior human ties.
All fourteen issues remain open. Provider attribution remains deferred; these
captures do not establish a provider cause. **Step 19 remains IN PROGRESS;
Step 20 NOT STARTED; production prompts unchanged; canary ON HOLD.**
