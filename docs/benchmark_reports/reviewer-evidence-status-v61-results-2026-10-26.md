# NC/ES evidence-status comparison results — 2026-10-26

**Completed: 28/28 calls, fourteen per arm, zero retries. Frozen decision:
`retain_limited_evidence_no_advancement`.** ES improves delivery and some observed
labels, but recovers **none of the four known H/U relation failures** and loses
protected craft/citation assessments. Retain the evidence and local fixtures;
do not promote ES or infer better story quality from these results.

Production **prompt 61 / graph 9 / fulfillment policy 1** remains unchanged.
Further live calls are **PAUSED**; the full workflow canary remains **ON HOLD**.

## Approved scope and execution

The user approved the [frozen 28-call plan](../handoffs/reviewer-evidence-status-frozen-plan-2026-10-26.md),
including full fictional prose/context sent to Ollama Cloud through the local
daemon. Its SHA-256 is
`163f269e6c30650d4bac2c47a144628b4b8ab046fcb914f56de684aa6802950f`.
No case, claim, component, gold, request, setting, scoring rule or stop rule was
changed after freezing.

The seven families were H/U/X/Y plus three new pottery, railway-office and
reservoir-record scenes. Both source presentation orders were used. NC retained
its control contract; both historical H/NC wire payloads remained exact. ES changed
only the designated relation component to four evidence statuses and its
explanatory instructions. Other component labels, whole-claim aggregation,
qualified craft standards, the eight-reference union and summed reason limit
remained unchanged.

All 28 requests reached a normal stop with HTTP 200. The first-eight-call sentinel
had **4/4 valid in each arm** and continued. There were no terminal failures,
retries, extra probes or replacement calls. All **57 daemon-version observations**
matched **0.40.11**; selected DeepSeek tag/show metadata also matched the freeze.
This is execution evidence, not provider-causality evidence.

## Results under the frozen rules

| Measure | NC | ES |
| --- | ---: | ---: |
| Attempts | 14/14 | 14/14 |
| Structurally valid reports | 13/14 | 14/14 |
| Correct projected target labels | 7/14 | 10/14 |
| Usable targets: correct, grounded and complete | 7/14 | 10/14 |
| Correct whole-claim labels | 30/42 | 36/42 |
| Usable whole claims | 30/42 | 35/42 |
| Usable material components | 81/98 | 89/98 |
| Usable non-target components | 74/84 | 79/84 |
| H/U false-acceptance opportunities recovered | Control: four opportunities | **0/4** |

Invalid delivery remains in the scheduled denominators and earns no partial
semantic credit. Whole-claim usability requires correct material components and
complete, source-grounded reasons/citations; a correct whole label is insufficient.

ES passed the delivery floor and all ten required X/Y/fresh target controls. It
failed the recovery screen and protected-loss screen. The higher overall usable
count does not override those predeclared conditions.

| Family | NC usable targets | ES usable targets | NC usable whole claims | ES usable whole claims |
| --- | ---: | ---: | ---: | ---: |
| H: observatory status versus consultation/resolve | 0/2 | 0/2 | 3/6 | 2/6 |
| U: greenhouse status versus authorization/resolve | 0/2 | 0/2 | 4/6 | 3/6 |
| X: same-instant door contradiction | 2/2 | 2/2 | 6/6 | 6/6 |
| Y: explicitly unresolved photograph timing | 0/2 | 2/2 | 4/6 | 6/6 |
| F1: dark then lit bench | 1/2 | 2/2 | 2/6 | 6/6 |
| F2: same-instant intact/shattered pane | 2/2 | 2/2 | 6/6 | 6/6 |
| F3: explicitly unresolved inspection timing | 2/2 | 2/2 | 5/6 | 6/6 |

Seven whole-claim gains and two losses account for ES's net gain of five:
two Y uncertainty-label gains, two endpoint-label gains, three claims made
available by one delivery gain, minus the H/RO craft and U/OR citation losses.
None is a recovery of the known H/U target relation.

## What the source inspection found

### Four-status vocabulary did not correct the known relation error

All eight valid H/U reports—both arms and both orders—support the false factual
relation. NC returns `supported`; ES returns `established_true`. The underlying
distinction remains:

- Acting before consultation can violate a prohibition and undercut a stated
  intention to wait. It does not contradict the fact that consultation has not
  yet happened.
- Starting before authorization can violate a rule and undercut resolve. It does
  not contradict the fact that authorization has not yet been received.

The model locates the relevant statements but does not reliably judge their
specific relationship. In E-ES-U-OR/C02.A02, its explanation combines
“resolve/status,” although these are different relations. In E-NC-U-OR/C02.A02,
the explanation truthfully identifies the resolve conflict in R010 instead of
establishing the requested status contradiction; it also omits R010 from its
own citations. That is a true explanation of a different relation, with incomplete
target coverage, not a successful target judgment.

E-NC-H-RO/C01.A03 goes further: its craft explanation says the rotation reverses
both the prior resolve and the unconsulted state. Only the resolve is undercut.
The craft label alone therefore conceals a false factual premise. These findings
support the narrower diagnosis of **relation selection and scope failure**;
they do not identify an internal model mechanism or prove why it occurs.

### Explicit uncertainty worked in the tested scenes

ES returned `explicitly_unresolved` for both Y and both F3 targets, with correct
source reasoning. It preserved the fact that common timing was unresolved rather
than inventing simultaneous events or separate visits. Both arms also recognized
the actual X/F2 contradictions, and valid F1 responses correctly distinguished
sequential dark/light states from a contradiction.

NC returned `unsupported` in both Y responses while accurately explaining that
common timing was not established. Under frozen primary gold these labels are
wrong, but their reasons are not false timing assertions. Preserve the disclosed
legacy unsupported-as-unestablished interpretation. ES's Y gain is evidence of
better alignment with the explicit uncertainty contract in these cells, not proof
that it discovered a previously missed fact. NC already returned `uncertain` in
both F3 responses.

No ES target used `unestablished`. This comparison had no live gold cell requiring
that subtype, so it does not establish the model's general ability to distinguish
unestablished from explicitly unresolved evidence. Offline projection tests cannot
fill that empirical gap.

### Accurate violation explanations can carry the wrong label

E-NC-F1-OR/C01.A03 explains that the cup moves into the carrier and therefore fails
the required bench endpoint, but returns `unsupported` on the proposition that
the action violates that endpoint. E-NC-F3-OR/C01.A03 similarly explains the broken
seal correctly while rejecting the violation proposition. The application
faithfully propagates those false component labels into the whole claim.

ES correctly labels both violations. Retain these two observed endpoint-label
gains, but do not treat them as evidence that the application can safely repair
future verdicts from free-text reasons. The mismatch itself is a useful local
regression target.

### Craft abstentions and incomplete witnesses remain protected losses

ES abstains on H's mechanical/contrived reading and voice-strain reading in both
orders, even while describing those readings as defensible or plausible. A
qualified craft interpretation need not be uniquely compelled by the source.
This reflects a mismatch with the frozen craft standard, not demonstrated
improvement in literary judgment.

The paired H/RO loss includes C03.A02 and the usable C03 whole claim. The frozen
screen also records C01.A03's supported-label loss; that NC component was already
unusable because of its false “unconsulted state” premise. Do not describe all
loss flags as independent lost successes.

E-ES-U-OR/C03.A02 gives a defensible impatience explanation based on acting against
stated resolve, but cites only R013, the action. R010 supplies the resolve and is
missing from this component's witness set. A sibling component cites R010, but
the frozen rule requires complete evidence for each material component. Reusing
R010 would not increase the whole-claim union; this is not an unavoidable budget
conflict. The C03 whole label is correct, but the assessment is not usable under
the frozen completeness rule.

A similar missing-counterpart issue occurs in E-NC-H-OR/C01.A03: its cited
R014/R015 status/action pair does not witness the earlier resolve. The full source
contains a defensible reversal at R012/R015. The inspection records incomplete
citations without assuming that the phrase “after R014” necessarily asserts
R014 became false.

Nine protected-loss flags describe overlapping checks in **two paired cells**:
H/RO and U/OR. They are not nine independent failures.

### One delivery failure remains rejected

E-NC-F1-RO finishes normally but repeats `claim_id` at the beginning and end of each
of its three claim objects. The repeated values are C01/C01, C02/C02 and C03/C03.
Strict parsing rejects the entire report for duplicate JSON keys. It is one
failed delivery with three duplicate members, not three failed calls.

There was no trimming, loose-JSON salvage, repair or retry. ES's paired valid
delivery is retained as a limited observation. One such pair does not establish
that the status treatment fixes delivery reliability.

## Inspection, verification and usage

All **27 valid reports, 81 whole reasons and 190 component reasons** were inspected
against the full original/revision/context. Masked notes were sealed before trial
key decoding. Known scenes and ES's status vocabulary can reveal the arm; masking
was partial. This is assistant factual adjudication, not independent human story
preference. Source truth, citation support, completeness and labels remain
separate dimensions. The one invalid report stays outside semantic scoring.

**55 post-run offline tests pass**, including exact replay of all 28 captures,
duplicate-key rejection, budget/version accounting, sealed inspection bindings,
source tampering, uncertainty interpretation, endpoint label/reason disagreement,
wrong-relation substitution, incomplete craft evidence, denominators and the
exact frozen decision. Ruff lint/format and strict mypy pass on three analysis
scripts. Real HTTP is blocked in those tests. The previously frozen 336-test
preparation remains intact; no production code or prompt changes were made.

Usage was **232,418 input tokens, 10,753 output tokens and 44.818 active inference
seconds**. Maximum single-call usage was **9,395 input / 527 output tokens /
2.920 seconds**, within the 24,000 / 8,000 / 300 reservations. Archived-rate
arithmetic estimate: **$0.082629**; actual billed cost remains unknown. The estimate
is not a new pricing claim or billing confirmation.

Private, ignored evidence:

- [Frozen cases, requests and rules](../../data/diagnostics/reviewer-evidence-status-v61-2026-10-26/).
- [Exact execution captures and ledger](../../data/diagnostics/reviewer-evidence-status-v61-2026-10-26-live/).
- [Sealed source inspection and results](../../data/diagnostics/reviewer-evidence-status-v61-2026-10-26-analysis/).

The approval, execution manifest, inspection export/notes, analysis and this
report are bound by hashes. The frozen plan/public plan and **3,110 historical
source fingerprints** verify. All fourteen issue bodies and user-posted GitHub
links remain preserved; no issue is closed or externally edited.

## Recommended local work before another experiment

1. Preserve the new duplicate-claim-ID capture, the two endpoint label/reason
   disagreements, all eight H/U target failures, craft abstentions and incomplete
   witnesses as local regressions. Retain the genuine-conflict, sequential-state,
   explicit-uncertainty and qualified-craft successes alongside them.
2. Audit the relation object explicitly: the two assertions being compared,
   whether the comparison concerns factual compatibility, an obligation or an
   intention, and whether the reason actually addresses that pair. Test any
   application-owned consistency checks locally, without rewriting model labels
   or treating a model-produced relation type as ground truth.
3. Require a materially different hypothesis before more inference. A possible
   later mechanism probe would contrast the same factual assertion pair in the
   complete scene versus an isolated, faithfully extracted pair, with real
   contradiction and unresolved controls. This could test whether adjacent
   rule/resolve material contributes to the error. It would be a diagnostic of
   context sensitivity, not a proposal to strip story context from production.
   Design and freeze any such comparison separately; **no new live budget is
   proposed for execution or approved here**.

Do not continue enum or wording variants by default. Retain ES's observed delivery,
endpoint and uncertainty-label gains as limited evidence while keeping the failed
recovery and preservation screens explicit. No writer revision or new human
preference evidence was produced. The nine earlier human ties remain unchanged;
future human review should assess feel/emotion, flow, character and story-breaking
details with machine-prepared mechanics. Provider attribution remains deferred.
