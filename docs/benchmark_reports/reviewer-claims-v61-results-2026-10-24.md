# Fixed-claim verification results — 2026-10-24

Status: **24/24 approved attempts complete; descriptive evidence only**.
The [frozen plan](../handoffs/reviewer-claims-frozen-plan-2026-10-24.md) was executed
without prompt, source, scoring, budget or stop-rule changes. Production remains
unchanged; further live calls are paused and the full workflow canary stays
**ON HOLD**.

DeepSeek delivered **22/24 valid responses**, **49/72 correct claim labels** and
**7/24 fully usable responses**. It retained supported criticism, but did not
reliably reject the supplied false premises. Several explanations identified
the relevant distinction and still approved the claim by accepting a looser
interpretation. The frozen outcome is **`complete_descriptive_only`**, which
records completion, not qualification or advancement.

## Execution and evidence boundaries

The user's approval was bound to plan SHA-256
`8c02702da5d54df9b3a074f87463e6a7fb97a87e3fbef734f83dedd5b911fff7`,
covering full unpublished prose/context/claims to Ollama Cloud through the local
daemon, with a 24-attempt ceiling and zero retries. All **24 calls completed**;
there was no terminal failure, truncation, unexpected thinking or retry.

Preflight matched **Ollama 0.40.10** and the selected
`deepseek-v4.1-flash:cloud` digest/capabilities. All **49 initial/before/after
version observations** matched. The first-eight sentinel continued with **7/8
valid responses** and no repeated structural-failure stop. All exact requests,
wire payloads, source versions, reservations, captures and validation receipts
are retained. The execution manifest binds **366 live JSON files** and approval.

The run used six families, three claims each, both source orders and two exact
repetitions. It contains **18 unique claims**, not 72 independent examples.
Three historical packets and nine historical claims were unchanged; three fresh
scenes and nine authored claims were frozen before inference. Settings remained
temperature 0.2, top-p 0.95, seed 20261022 and thinking=false.

All **22 valid responses / 66 returned reasons** received source inspection
against the complete original/revision and assignment. Notes bind exact reason
text, source hashes, versions, offsets and quotations. They were sealed before
decoding source-order/repetition IDs. This is assistant factual adjudication;
families and wording are recognizable, so it is not fully blind or a new human
preference test. The two invalid captures were inspected separately and never
repaired or awarded semantic credit.

## Frozen primary results

| Measure | Result |
| --- | ---: |
| Attempts / valid complete deliveries | 24 / 22 |
| Correct claim labels, all attempted judgments | **49/72** |
| Correct labels among valid deliveries | 49/66 |
| Correct labels with grounded reasons and citations | **48/72** |
| All three labels correct within one response | 8/24 responses |
| All three claims fully usable within one response | **7/24 responses** |
| Unsupported claims accepted as supported | **13/32 opportunities** |
| Uncertain answers against definite gold | **4/72**, all on unsupported claims |
| Claim judgments lost to invalid delivery | **6/72** |
| Supported controls rejected as unsupported | **0** |

All **37 supported controls in valid deliveries were labeled supported**. Three
more supported-control opportunities were lost to invalid delivery, giving
37/40 on the attempted denominator. Of 32 unsupported-claim opportunities,
12 were correctly rejected, 13 accepted, four received uncertainty and three
were lost to invalid delivery. Thus **49 correct + 13 false acceptances + four
abstentions + six delivery failures = 72**.

Reason/citation inspection finds **52 supported and 14 unsupported justifications**
among the 66 valid claim records. Thirteen overlap wrong whole-claim approvals;
one adds a narrow overstatement despite a correct rejection. These are not
fourteen additional independent model failures. A justification can contain
true observations and still fail to support its judgment of the entire claim.
Representative citations were assessed with the complete sources; no new rule
requiring every ancillary observation to have its own separate citation was
introduced after the run.

| Family | Valid responses | Correct claim labels | Fully usable responses | Main result |
| --- | ---: | ---: | ---: | --- |
| H: observatory, historical | 4/4 | 8/12 | 0/4 | All four accept the false status contradiction |
| B: coat, historical | 3/4 | 3/12 | 0/4 | Both unsupported claims accepted in all three valid responses |
| G: ferry, historical | 4/4 | 8/12 | 0/4 | Four abstentions on the imported earlier-choice premise |
| K: concert hall, fresh | 3/4 | 6/12 | 0/4 | All three valid responses accept the false status contradiction |
| L: pottery, fresh | 4/4 | 12/12 | **4/4** | Explaining versus deciding/action distinguished; genuine endpoint loss retained |
| M: railway, fresh | 4/4 | 12/12 | **3/4** | Version ownership distinguished; one overbroad explanation |

Historical cases yield **19/36 correct labels and 0/12 usable responses**; fresh
cases yield **30/36 and 7/12**. These selected cases differ in wording and claim
composition. This is not evidence of a general fresh-versus-historical advantage
or a controlled improvement over the preceding D2/PC reviewer task.

## What the responses show

### Recognizing a distinction did not reliably determine the label

In H, acting before consultation agrees with the immediately preceding
not-yet-consulted status. It violates the separate consultation-first condition
and the character's stated resolve. The model accepted the supplied false
status-contradiction claim in **both orders and both repetitions**. Some reasons
repeated the false contradiction. Others defended the plausible abruptness
criticism or switched the contradiction to the resolve sentence, without
establishing the exact supplied factual premise.

The fresh K case shows the same failure. `CV-K-OR-1` and `CV-K-RO-1` explicitly
recognize that non-approval and acting before approval are compatible, then
excuse the wording as imprecise and endorse a supposedly supported core tension.
`CV-K-RO-2` simply calls the two status statements contradictory. This is direct
output evidence of inconsistent whole-claim judgment. It does not reveal the
model's internal cause.

### The same distinction succeeded in one family and failed in another

All three valid B responses accepted both the before-deciding/acting premise and
the compound claim's deferred-consultation premise. Their reasons often quoted
the actual before-explaining language, then still treated it as a condition on
earlier action. The true seam-endpoint violation and true duplicate cleanup did
not establish that additional condition.

In contrast, **all four L responses** rejected the invented condition while
recognizing the genuine intact-rim violation and allowing a grounded urgency
reading. The distinction is available in these outputs, but has not generalized
reliably across the selected historical and fresh claims. Claim wording,
composition and context remain confounded here; the run cannot identify which
causes the difference.

### Uncertainty and a narrow explanation failure remain separate

All four G responses avoided endorsing the earlier-choice premise outright,
recognized that it was not established, and chose `uncertain`. That is useful
diagnostic noticing, but the frozen contract grades the entire supplied claim
as unsupported; uncertainty earns no correct-label recovery. The supported
endpoint and qualified continuity controls remained accepted.

All four M responses correctly rejected importing an original-only cabinet
action into the revision and retained the supported endpoint/decision and
qualified restlessness readings. `CV-M-RO-1` nevertheless added that packing was
the revision's only plate-handling action. The source also narrates finding the
plate and loosening its attached screw with fingers. The main no-locking/no-
retrieval conclusion remains correct; this overbroad count makes that explanation
unqualified under the frozen whole-reason check. It does not establish damage
to the story or negate the correct version-ownership judgment.

### Supported criticism was not suppressed wholesale

Every valid supported-control judgment was retained, including genuine condition
and endpoint violations, optional duplicate cleanup, qualified voice/continuity
criticism and vividness that does not establish assignment compliance. There was
no observed blanket false rejection of these controls. The limitation is chiefly
accepting unsupported material within claims, with four additional abstentions,
rather than uniformly refusing interpretive criticism.

## Delivery failures and repeatability

Both rejected responses were **HTTP 200, normal `stop`**, with complete reported
usage and no truncation:

- **`CV-K-OR-2`: duplicated `evidence` key in C02.** Both arrays contain R012/R013.
  Its label says `supported`, while the reason ends by saying the claim is
  unsupported as stated. This label/reason conflict is preserved as diagnostic
  evidence inside an invalid response; duplicate removal would not itself
  reconcile it. No normalized or repaired answer receives credit.
- **`CV-B-RO-1`: nine refs in C03, above the frozen maximum of eight.** All refs
  belong to the packet. There is no namespace failure, but membership does not
  override cardinality. The array was not trimmed. This reopens no historical
  result and demonstrates that the compact interface still has delivery limits.

All twelve repeated wire-payload pairs were identical, while none of the raw
response contents was byte-identical. Among the **ten pairs with both deliveries
valid, all label triples matched**. The frozen scoring records three repeat
disagreements: B/RO and K/OR differ in delivery, and M/RO differs in full-reason
qualification. Stable labels include stable errors; repetition did not recover
the H/B/K failures. This small fixed-seed run does not establish determinism.

Source-order results were OR **24/36 correct labels, 4/12 usable responses** and
RO **25/36, 3/12**. Both orders had 11/12 valid deliveries and 24/36 usable claims.
These counts provide no demonstrated source-order remedy.

## Budget and verification

| Resource | Observed | Frozen ceiling |
| --- | ---: | ---: |
| Calls, including rejected output | 24 | 24 |
| Reported input tokens | 92,888 | 576,000 aggregate / 24,000 per call |
| Reported output tokens | 6,773 | 192,000 aggregate / 8,000 per call |
| Active generation seconds | 29.134 | 7,200 aggregate / 300 per call |
| Largest input / output | 4,281 / 389 | 24,000 / 8,000 |
| Longest active call | 1.506 seconds | 300 seconds |

Usage is complete. The archived-rate arithmetic estimate is **$0.035994**, below
the $0.40320 token reservation and $0.50 planning allowance. Actual billing is
unknown; this is not a newly verified tariff or provider-enforced spend limit.
Verification and metadata time are separate from active generation time.

The preparation had **125 passing offline tests**. **Sixteen post-run tests**,
Ruff lint/format and strict mypy pass on the three analysis scripts. They verify
the actual schedule, requests, usage and version evidence, source/claim binding,
sealed masked notes, tamper rejection, independent invalid-response diagnosis,
repeatability accounting and exact frozen score replay. Real HTTP is blocked
during these checks. Formatting adjustments preserve the sealed note text.
No production/frontend/API/worker code changed, so unrelated product builds and
broad suites were not rerun. Analysis made **zero additional inference calls**.

## Recommendation and next local work

Retain L's complete discrimination and M's correct version ownership as bounded
positive evidence. Retain G's improved noticing without upgrading abstention to
a correct verdict. **Do not add this verifier as a production gate or promote a
same-model verification layer from this run.** Supplying the claim and reducing
the review task did not reliably solve the targeted failures.

Before proposing more inference:

1. Extend local delivery fixtures with the actual duplicate-evidence and nine-ref
   captures, retaining both strict rejection and the label/reason disagreement.
   Do not treat deduplication or a larger evidence allowance as semantic repair.
2. Audit whole-claim adjudication locally: distinguish an explicit false factual
   clause, a genuine constraint violation, and a defensible literary inference.
   Preserve cases where a reason recognizes the error but accepts a different
   “core” claim. Any automated consistency check remains conditional; it must not
   silently choose a new label or claim to solve general semantic truth.
3. If those checks justify another live design, isolate whether explicit
   assessment of the factual clauses before a whole-claim verdict helps. Keep
   unchanged full-claim controls, fresh families, both orders and positive craft
   readings. Do not bundle this with enum, cardinality or provider changes, and
   freeze a separate plan before inference. No new live budget is approved here.

The likely diagnostic direction is failure to preserve the exact proposition
being judged when combining valid and invalid clauses. That is an interpretation
of the recorded reasons, not proof of an internal mechanism. A full-review
comparison would still be needed to establish useful integration; no writer
behavior or whole-story quality was tested here.

Provider investigation remains deferred. This run records no evidence attributing
the semantic errors to Ollama, and makes no provider-exoneration claim. Preserve
the **nine human ties** and future quality focus on feel/emotion, flow, character
and story-breaking concerns. Mechanical evidence and exact claim accounting help
review; minimal edits and report usability are not reader-preference measures.

## Local evidence and tracking

- [Frozen preparation and approval](../../data/diagnostics/reviewer-claims-v61-2026-10-24/)
- [Live capture ledger](../../data/diagnostics/reviewer-claims-v61-2026-10-24-live/)
- [Analysis bundle](../../data/diagnostics/reviewer-claims-v61-2026-10-24-analysis/),
  [readable inspection register](../../data/diagnostics/reviewer-claims-v61-2026-10-24-analysis/inspection-register.md)
  and [frozen decision](../../data/diagnostics/reviewer-claims-v61-2026-10-24-analysis/decision.json)
- [Invalid-response audit](../../data/diagnostics/reviewer-claims-v61-2026-10-24-analysis/invalid-response-audit.json)
  and [repeat audit](../../data/diagnostics/reviewer-claims-v61-2026-10-24-analysis/repeat-audit.json)

Full unpublished prose and raw captures remain local and ignored by Git. The
analysis seal binds this report, inspection and verification; a separate closure
binds the updated tracker and issue index. All fourteen original issue bodies
and user-posted GitHub links remain unchanged; no external issue was edited or
closed. Production stays **prompt 61 / graph 9 / fulfillment policy 1**.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; further live calls PAUSED; full workflow
canary ON HOLD.**
