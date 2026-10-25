# CV/MC material-claim comparison — 2026-10-24

**Completed: 36/36 approved calls, zero retries. MC does not advance.** The
unchanged CV control delivered **42/50 usable primary judgments**; MC delivered
**41/50**. Both arms delivered **17/18 structurally valid responses**. The extra
material-claim instruction produced one paired semantic recovery, two distinct
paired losses, and no fresh-family recovery. Production remains **prompt 61 /
graph 9 / fulfillment policy 1**. Further inference is **PAUSED** and the full
workflow canary remains **ON HOLD**.

This executes the [frozen plan](../handoffs/reviewer-material-claims-frozen-plan-2026-10-24.md)
after explicit approval to send full unpublished prose, context and claims to
Ollama Cloud through the local daemon. The
[preceding local audit](../handoffs/reviewer-whole-claim-audit-2026-10-24.md)
and all historical scores remain unchanged. This comparison concerns judgments
about supplied claims, not writer behavior, full-review integration or improved
story quality.

## Execution and evidence

Nine families × two arms × two source orders produced **36 completed attempts**,
eighteen per arm, with three claims per response. H/B/G/K/L/M and their eighteen
claims were unchanged; N/P/Q were fresh floodgate, bookbinding and seed-archive
scenes. CV preserved its historical wire payloads. MC added only the frozen
material-premise assessment message, using the existing reason field and schema.

Preflight matched **Ollama 0.40.10**, `deepseek-v4.1-flash:cloud`, and model digest
`e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
All **73** initial/before/after version observations matched. Temperature 0.2,
top-p 0.95, seed 20261022, thinking=false, stream=false and the other frozen
settings were preserved. The first-eight sentinel had four valid responses per
arm and continued. Every generation returned HTTP 200 with normal stop and
complete usage. There was no terminal failure, restart, retry or correction call.

| Resource | Observed | Frozen ceiling |
| --- | ---: | ---: |
| Calls / per arm | 36 / 18 | 36 / 18 |
| Input tokens | 141,640 | 864,000 |
| Output tokens | 10,828 | 288,000 |
| Largest input / output per call | 4,549 / 447 | 24,000 / 8,000 |
| Active generation time | 53.48 seconds | 10,800 seconds |
| Longest generation | 1.89 seconds | 300 seconds |

Archived-rate arithmetic is **$0.0554856**, below the $0.60480 token reservation
and $0.75 planning allowance. This uses archived input $0.30/output $1.20 per
million tokens without discounts; it is not verified billing or a fresh tariff
lookup. Actual cost remains unknown. Read-only daemon metadata checks and offline
inspection did not consume generation calls.

The frozen exporter masked arm/order/trial IDs. All **102 reasons in 34 valid
responses** were inspected against all nine complete original/revision/context
packets. Source-bound notes were sealed before decoding the key. Style and scene
content can reveal treatment or family, so this is partially masked assistant
factual adjudication, not blind human preference. The two invalid captures were
inspected separately, without repair or semantic credit.

## Frozen scores and paired decision

Each arm has **50 primary opportunities**: 32 supported controls and eighteen
unsupported claims. B/C03 and G/C03 remain four **secondary scope-sensitive
opportunities** per arm with unchanged historical gold. Invalid deliveries stay
in the attempted denominators; none of the 36 calls was left unstarted.

| Measure | CV | MC |
| --- | ---: | ---: |
| Valid responses | 17/18 | 17/18 |
| Fresh valid responses | 6/6 | 6/6 |
| Primary correct labels | 42/50 | 43/50 |
| Primary grounded reasons and citations | 42/50 | 41/50 |
| Primary usable judgments: correct label plus grounding | **42/50** | **41/50** |
| Primary false acceptances | 6 | 5 |
| Primary abstentions | 0 | 0 |
| Primary opportunities lost to delivery | 2 | 2 |
| Supported primary controls retained in valid deliveries | 31/31 | 31/31 |
| Secondary correct/usable judgments under historical gold | 0/4 | 2/4 |
| All-claim historical-gold usable judgments | 42/54 | 43/54 |
| Entire three-claim responses usable under historical gold | 9/18 | 10/18 |

The secondary difference is G/C03: CV abstained in both orders while MC rejected
the claim. It earns no primary recovery. B/C03 was accepted in each valid OR
response and unavailable in the invalid RO responses. Its deferred-consultation
language remains scope-sensitive; the notes allow a qualified craft reading
without changing historical unsupported gold. Neither secondary probe establishes
an improvement in literary judgment.

There were **six eligible CV primary failures across four families**, including
H/C01 in both orders and two fresh N/C02 failures. Thus the frozen recovery screen
had sufficient opportunity; lack of opportunity does not explain the outcome.

- **One recovery:** K/C02 in OR. CV falsely called unapproved descent a
  contradiction of non-approval status; MC correctly distinguished them.
- **Two distinct protected losses:** K/C02 in RO went in the opposite direction;
  Q/C03 in OR kept the correct label but added a false exhaustive handling count.
  Each loss appears under both usability and grounding in machine output: four
  flags describe two claim/order losses, not four independent defects.
- **No delivery gains or paired valid-delivery losses.** Both invalid responses
  occupy B/RO. MC met the delivery thresholds but failed the semantic screen.
- **No unchanged claim recovered in both orders, and no fresh recovery.** The
  required four recoveries across two families were not achieved.

The exact frozen outcome is **`retain_limited_evidence_no_advancement`**. MC is not
retained as a promising candidate under this screen. Neither arm is qualified for
production and neither can authorize writer edits.

| Family | Primary usable CV | Primary usable MC | Main observation |
| --- | ---: | ---: | --- |
| H — observatory | 4/6 | 4/6 | MC improved one label but not its entire explanation |
| B — costume workroom | 1/4 | 1/4 | False decision prerequisite; both RO deliveries invalid |
| G — ferry terminal | 4/4 | 4/4 | Endpoint and qualified continuity controls retained |
| K — concert hall | 5/6 | 5/6 | Opposite order-dependent outcomes, no net recovery |
| L — pottery workshop | 6/6 | 6/6 | Explaining/deciding and wish/prohibition contrasts retained |
| M — railway shed | 6/6 | 6/6 | Original-only action correctly excluded from revision chronology |
| N — floodgate, fresh | 4/6 | 4/6 | All four accept the false status contradiction |
| P — bookbinding, fresh | 6/6 | 6/6 | Both retain factual and qualified craft distinctions |
| Q — seed archive, fresh | 6/6 | 5/6 | MC adds an unsupported count despite correct rejection |

OR primary usability is **21/25 in both arms**; RO is **21/25 CV, 20/25 MC**.
Unchanged families total **26/32 in both arms**; fresh families total **16/18 CV,
15/18 MC**. There is one observation per arm/family/order, not an exact repetition
study. These selected, related claims do not support population estimates or
causal claims about presentation order.

## What the captures show

**Visible coverage did not ensure whole-claim correctness.** Coverage was annotated
complete for 48/51 valid CV reasons and 51/51 MC reasons; three CV reasons omitted
a material factual distinction. This describes what the explanations addressed,
not whether those assessments were true. MC-H-RO explicitly recognized that no
consultation and rotation before consultation are chronologically consistent. It
then called the contradiction wording loose and endorsed a defensible core of the
claim. That still accepts a supplied assertion the reason itself has undermined.

**Status, intention and obligation remain conflated.** Opening before authorization
breaches an authorization-first requirement and a resolve to wait. It agrees with
a statement that authorization has not arrived. Every N/C02 response nevertheless
called this a factual contradiction. K/C02 changed from wrong to right in one
order and from right to wrong in the other. This observed pattern does not identify
an internal reasoning mechanism or a provider cause.

**Correct rejection can overreach into craft.** MC-H-OR correctly rejected the
immediately-preceding-status assertion. Its explanation additionally treated
mechanically inserted/contrived judgments as unsupported because they were
stylistic interpretations. The abrupt intention/action reversal supports a
defensible reading of that kind; the frozen contract does not require unique
reader agreement or objective proof of taste. Consequently this was a correct
label with an unusable whole reason, not a semantic recovery. Even giving that
borderline explanation full credit would add only one recovery, leaving the
required count, both-order/fresh conditions and independent losses unmet.

**Correct version ownership can acquire a new invented fact.** MC-Q-OR correctly
rejected the alleged lock-then-retrieve sequence but asserted that the revision
contained only one handling of the packet. Earlier passages explicitly brush dust
off it and free its string before lifting it. This is the same general failure
class as the prior plate-handling explanation, now in a fresh scene. The other Q
reasons' only/bag wording was judged in the narrower locking/retrieval context;
that scope judgment is explicit in the sealed notes. A stricter reading of those
phrases would lower scores, not rescue MC's frozen decision.

**The before-explaining/before-deciding distinction remains context-sensitive.**
Both valid B/C02 answers accept the stronger invented decision prerequisite. MC's
reason explicitly restates it as a plan to consult before deciding. In contrast,
L and fresh P correctly reject the stronger prerequisite in both arms and orders,
while retaining the real endpoint failures and qualified craft controls. Those
successful controls were already successful in contemporary CV and cannot be
counted as MC recoveries.

**Delivery failed on evidence cardinality, not transport.** CV-B-RO and MC-B-RO
each supplied nine distinct, catalog-valid references for C03, exceeding the
unchanged eight-reference bound. Both were otherwise normal-stop JSON responses
with no duplicate members or unknown references in the inspected captures. Their
entire responses remain invalid: no truncation, normalization, discarded ninth
reference, retry or salvaged-claim credit. The rejected content also repeats the
before-explaining/before-deciding problem, but that observation adds no scored
semantic opportunities. Nothing here attributes the output defects to Ollama;
the user-requested provider investigation remains deferred.

## Recommended local follow-up

1. Preserve these two overflow captures and the H/K/N/Q contrasts as local
   regressions. Include supported craft interpretations beside false status
   contradictions and explicit exhaustive counts beside narrowly scoped summaries.
2. Audit whether the current single whole-claim judgment allows the explanation
   to acknowledge a false premise and still approve a different, plausible claim.
   Sketch application-owned aggregation over separately stated material factual
   assertions, with interpretation assessed separately. This is a design question
   to test locally, not an implemented production rule or a claim that decomposition
   will solve recognition errors such as N/C02.
3. Address evidence-budget policy separately from semantics. Both arms hit the same
   nine-reference boundary; silently clipping references or changing this run's
   cap would hide the delivery failure. Any later experiment needs a separate
   frozen design and approval after the local checks justify it.

No new inference budget is proposed or authorized by this report. No production
prompt, graph node, writer route or human checkpoint was changed. The nine earlier
human ties remain intact. Mechanical success and literal preservation do not
establish better stories: eventual reader evaluation should still focus on
feel/emotion, flow, character and story-breaking concerns, with machine-prepared
mechanical evidence. **Step 19 remains IN PROGRESS; Step 20 NOT STARTED.**

## Reproducibility and verification

Private, Git-ignored evidence:

- [Frozen preparation](../../data/diagnostics/reviewer-material-claims-v61-2026-10-24/)
  and [approval](../../data/diagnostics/reviewer-material-claims-v61-2026-10-24/approval.json).
- [36 live capture cells](../../data/diagnostics/reviewer-material-claims-v61-2026-10-24-live/cells/),
  with exact requests, raw responses, receipts, metadata and seals.
- [Analysis bundle](../../data/diagnostics/reviewer-material-claims-v61-2026-10-24-analysis/):
  execution manifest, masked export, sealed notes, decoded frozen decision,
  aggregate accounting, invalid-output audit and offline verification.

Plan SHA-256:
`2b83e01b80ba59cc59ad7cf1a388391b85062e8fb76642cd7da2e2ae0924e84e`.
The frozen public plan, 66 bound local files and 1,196 historical fingerprints
remain unchanged. Analysis seals bind the source adjudication separately from
the mutable tracker and issue index. Original issue bodies and all fourteen
user-posted GitHub links are preserved; no external issue was changed or closed.

Post-run verification checks actual schedule/wire equality, ceilings, 73 version
captures, sentinel replay, both untouched invalid outputs, all 102 source-bound
notes, paired scoring and tamper rejection. HTTP is blocked in these tests.
**16 post-run offline tests, Ruff lint/format and strict mypy on three analysis
scripts pass.** The first test attempt passed fourteen tests but could not create
the restricted Windows temporary directory for two tamper tests; the complete
suite passed using a new workspace temporary directory. Verification results are
recorded in the private bundle. No frontend/API/worker code changed, so unrelated
production builds are not applicable.
