# BS/PO/ER source-obligation comparison results

Date: 2026-10-28. **COMPLETE — 48/48 calls, sixteen per arm, zero retries.**
Frozen decision: **`retain_source_obligation_recovery_signal_only`**.

**PO passes the frozen bounded recovery screen.** Its sixteen target assessments
have correct, source-supported primitive judgments and correct source/event
projections. BS has **11/16 usable targets**, PO **16/16**, and ER **16/16**.
PO recovers all **five contemporary BS target failures**: both known K2 cases,
both fresh M1 cases and the original-first M2 case. All **48 PO primitive
judgments** pass independent source inspection. No protected paired loss occurs.

This is evidence for the combined **model premise assessment plus application
projection** approach. PO does not ask the model to emit the final source verdict.
It therefore demonstrates a successful division of responsibility on these cases,
not that the model has learned to make the direct BS judgment reliably. The
remaining BS failures already explain the missing timing accurately.

Retain PO as a promising diagnostic candidate. **Do not promote it to production,
authorize writer edits, or claim improved story quality.** The
[frozen plan](../handoffs/reviewer-source-obligations-frozen-plan-2026-10-28.md)
and its scoring were executed unchanged. Production **prompt 61 / graph 9 /
fulfillment policy 1** remains unchanged; further live calls are **PAUSED** and
the full workflow canary remains **ON HOLD**.

## Execution integrity

- **48 reservations, 48 dispatches and 48 completed responses**. All validate;
  no probe, retry, replacement, truncation, terminal failure or unused allocation.
- The first-twelve delivery sentinel passes with **4/4 valid per arm**. No
  semantic early stopping or changes in response to intermediate outputs.
- All **97 runtime daemon-version observations** match **Ollama 0.40.12**.
  Selected `deepseek-v4.1-flash:cloud` metadata remains unchanged, including digest
  `e04da138d31e0c9468e982e1ae9503d06cb7e170caa16a90c17d931c4aa140f8`.
- Every request retains high thinking, temperature **0.2**, top-p **0.95**,
  seed **20261022**, non-streaming delivery, context **40,000** and no format
  override. Every response contains nonempty thinking. Thinking text was excluded
  from semantic inspection; its presence does not establish an internal cause.
- All **eight historical K2/L1 BS/ER wire controls** remain byte-exact. Cases,
  claims, obligations, scopes, requests, gold, scoring, schedule and stops are
  unchanged. No old result is rescored.
- The preparation's **106 sealed artifacts / 6,548 historical fingerprints**
  verify. Plan SHA-256:
  `c4bb1cb9824ae410db133f89b924bba864f3b9ec7ecb13bc53046a4aae7a1bd5`.
  The user's explicit approval is recorded against that seal and the full
  prose/context payload to Ollama Cloud through the local daemon.

## Frozen scores

“Usable” requires correct judgments, adequate explanations and citations, complete
material coverage and the correct claim scope. PO additionally requires all three
primitive statuses to be correct and grounded, the visible source to be reviewed,
and **both** derived projections to be correct. A correct projection built from
wrong premises receives no target credit. All attempts remain in the denominators.

| Measure | BS | PO | ER |
| --- | ---: | ---: | ---: |
| Valid reports | 16/16 | 16/16 | 16/16 |
| Correct targets under each arm's contract | 11/16 | 16/16 | 16/16 |
| Usable targets | 11/16 | 16/16 | 16/16 |
| Usable whole claims | 42/48 | 48/48 | 48/48 |
| Usable components | 106/112 | 112/112 | 112/112 |
| Usable non-target components | 95/96 | 96/96 | 96/96 |
| Completely usable reports | 10/16 | 16/16 | 16/16 |

One qualified BS craft-wording concern affects the strict non-target counts,
described below. It does not affect target counts, recoveries or the decision.

| Family and source condition | Direct BS target | PO source / event projections | ER target |
| --- | --- | --- | --- |
| K2: hook occupancy; no observation timing | Uncertain in both orders; fails | Unsupported / uncertain; both orders pass | Uncertain; both pass |
| L1: latch open/closed; no observation timing | Unsupported; both pass | Unsupported / uncertain; both pass | Uncertain; both pass |
| M1: cubby contains flag/no object; no timing | Uncertain in both orders; fails | Unsupported / uncertain; both pass | Uncertain; both pass |
| M2: hatch raised/lowered; no timing | Uncertain in OR; unsupported in RO | Unsupported / uncertain; both pass | Uncertain; both pass |
| M3: same lamp, authoritative context clock key | Supported; both pass | Supported / supported; both pass | Supported; both pass |
| M4: same lever, explicitly distinct times | Unsupported; both pass | Unsupported / unsupported; both pass | Unsupported; both pass |
| M5: declared source S includes unavailable appendix | Uncertain; both pass | Uncertain / uncertain; both pass | Uncertain; both pass |
| M6: distinct bolts, explicitly identical instant | Unsupported; both pass | Unsupported / unsupported; both pass | Unsupported; both pass |

OR means original-first presentation; RO means revision-first. The two orders
are repeated observations of one scene family, not independent stories or
sufficient replication to establish an order effect.

The five actual matched recoveries are **K2 OR/RO, M1 OR/RO and M2 OR**, out of
five valid contemporary opportunities. They are **label recoveries, not repairs
of missing source noticing**: the failed BS explanations already identify the
missing timing. M2 RO and the successful controls earn alignment credit only.
Known/fresh usable targets are BS **2/4 and 9/12**, PO **4/4 and 12/12**, and
ER **4/4 and 12/12**.

All **24 M3–M6 control targets**, **48 independent conditionals**, and both
retained L1 BS targets pass. There are **zero protected BS-to-PO losses** and
**zero separately reported BS-to-ER loss flags**. All assignment and qualified
craft primary labels remain supported.

The frozen unknown-time paired metric is **10/10**: eight complete-source PO/ER
pairs correctly separate insufficient source proof from unresolved event truth;
the two incomplete-source M5 pairs correctly keep both judgments uncertain.
The latter two are scope controls, not examples of different source/event labels.
Every frozen screen passes; the failure list is empty.

## What the primitive evidence shows

| Families | Same entity | Opposite literal predicates | Same observation instant |
| --- | --- | --- | --- |
| K2, L1, M1, M2 | Established | Established | Unestablished |
| M3 | Established | Established | Established |
| M4 | Established | Established | Refuted |
| M5 | Established | Established | Unestablished; declared source incomplete |
| M6 | Refuted | Established | Established |

Every row occurs in both source orders; **48/48 statuses and their explanations
and citations are usable**. The application binds each ledger to the exact
packet, target, observation pair, obligation map and declared source scope.

The controls matter to the interpretation:

- **M3:** both PO reports cite the authoritative clock key in context, which
  the prose explicitly identifies as the observations' timing source. They do
  not mistake a scene assignment for proof of an action. Observation time is
  distinguished from when an entry was written.
- **M4:** explicit different observation times produce `refuted`, rather than
  treating a negative witness as mere absence of evidence.
- **M5:** the visible packet is fully inspected, but declared source S includes
  an unavailable appendix. The host's frozen incomplete-scope flag preserves
  uncertainty; no hidden appendix contents are invented. This does not prove
  that a production system can infer source completeness automatically.
- **M6:** different actual bolts refute identity without changing the independent
  incompatibility of fully extended/retracted predicates **if applied to one
  bolt at one instant**. Both PO reports preserve that separation.

For K2, BS's two raw target judgments remain `uncertain`, alongside explanations
that no source establishes the common instant. PO returns independently supported
identity, opposition and missing-time statuses; the frozen application rule
projects source sufficiency to `unsupported` and event truth to `uncertain`.
The same treatment transfers to M1 and the failed M2 order. Ordinary whole-claim
aggregation faithfully retains BS's raw error; it is not the source of that error.

This supports a narrower diagnostic hypothesis: **extracting independently
checkable premises and applying an explicit claim/scope contract can avoid this
direct-verdict failure**. The treatment bundles a different response interface
with application-owned projection. The comparison does not isolate which part
would suffice alone, establish the model's internal reasoning mechanism, or
justify applying this algebra to arbitrary literary claims.

## Inspection and wording sensitivity

All **48 masked reports, 144 whole reasons, 336 component reasons and 48 additional
primitive reasons/statuses** were inspected against the complete originals,
revisions and source context. PO's target and whole reasons are application joins
of returned primitive/component reasons; they are not additional model explanations.
The assistant's notes were sealed before decoding trial identities. The view hid
trial/arm/order metadata, resources and thinking, but claim wording, schema and
recognizable scenes could identify treatment or family. This is a **partially
masked assistant factual audit**, not blind human literary-preference testing.

Adequate alternative witnesses are accepted. A hypothetical does not require its
antecedent to occur, a decision need not be carried out to have been made, and a
qualified craft reading need not be uniquely compelled by the prose.

One strict precision annotation is retained for **`C-BS-L1-OR`, C03.A01**. Its
participation interpretation is supported, but the explanation says Ivo is
“seating Tavi to watch.” R016 establishes fetching and positioning a stool where
Tavi could watch; it does not explicitly establish Tavi sitting. “Seating” can
also mean arranging a seat, so this remains a qualified wording concern, not a
proven invented event or a failed craft label. The accompanying phrase “guiding
him through the lever” is compatible with instruction and does not assert
physical hand guidance.

A sensitivity check accepts this explanation without changing labels, gold or
sources. BS then has **43/48 usable whole claims, 107/112 components, 96/96
non-targets and 11/16 completely usable reports**. PO/ER are unchanged. All five
target recoveries and the frozen decision remain unchanged. The positive result
therefore does not depend on penalizing this wording.

Some assignment explanations use “verbatim” for tense-adjusted paraphrases. Two
PO absence explanations loosely mention recording/entry times while also stating
that no shared observation time is established (`C-PO-M2-RO` and `C-PO-L1-OR`).
The full packets contain neither timing relation, and neither explanation uses
an entry timestamp to prove an observation timestamp. These are wording cautions,
not additional material failures. They should not be turned into claims that
the story is weak or requires revision.

## Resource observations

| Measure | BS | PO | ER |
| --- | ---: | ---: | ---: |
| Input tokens | 154,002 | 169,022 | 153,590 |
| Combined generated tokens | 63,633 | 70,825 | 56,737 |
| Active request seconds, total | 241.49 | 265.76 | 230.95 |
| Median request seconds | 15.64 | 15.70 | 13.26 |
| Median generated tokens | 3,962.5 | 4,203 | 3,073.5 |
| Generated tokens per completely usable report, strict | 6,363.3 | 4,426.6 | 3,546.1 |
| Active seconds per completely usable report, strict | 24.15 | 16.61 | 14.43 |

Totals: **476,614 input tokens, 191,195 combined generated tokens and 738.21 active
seconds**. The largest call used **10,794 input tokens, 7,407 generated tokens
and 28.92 active seconds** (these maxima need not belong to the same call).
All remain within the frozen per-call and aggregate limits. Active seconds measure
requests; they exclude local verification/sealing between calls and are not
end-to-end workflow latency.

PO uses **11.3% more generated tokens and 10.1% more active seconds in aggregate
than BS**, while producing more usable reports. Median matched PO/BS ratios are
**0.995 for generated tokens and 1.033 for request time**; variable case costs make
these differ from ratios of totals. With the qualified BS wording accepted,
BS's usable-report cost becomes **5,784.8 generated tokens / 21.95 seconds**;
PO's advantage on that denominator remains. This small batch is not a stable
latency forecast or a production efficiency qualification.

All arms use high thinking. This run does not estimate the effect of turning
thinking on versus off. Reasoning/final token splits remain **unknown in all
48 captures**. The archived $0.30/$1.20-per-million basis gives **$0.3724182**;
actual tariff and billed cost remain unknown. No new pricing claim is made.

## Local verification and retained evidence

The sealed preparation retains its **450 passing offline tests**. Post-run
verification passes **84 offline tests**, plus Ruff lint/format and strict mypy
on seven analysis scripts. Tests block real HTTP. They replay all 48 raw responses
against exact frozen requests, verify seals/version/accounting, bind every source
annotation, exercise PO scope and primitive tamper rejection, and recompute the
strict result and wording sensitivity. A changed primitive behind an otherwise
correct projection is explicitly denied usable credit.

The first post-run attempt passed 83 tests and type/format checks but caught one
overlong analysis-code line. That attempt is retained; after the formatting fix
and additional wrong-premise check, the complete 84-test rerun passes. No frozen
input, live response or score was changed. Application/frontend checks are
inapplicable because no application code, dependency or production route changed.

Private evidence roots:

- `data/diagnostics/reviewer-source-obligations-v61-2026-10-28/`: frozen plan,
  sources, claims, scopes, requests, gold, scoring/stops and approval.
- `data/diagnostics/reviewer-source-obligations-v61-2026-10-28-live/`: reservations,
  exact dispatched requests, raw responses, receipts, metadata and cell seals.
- `data/diagnostics/reviewer-source-obligations-v61-2026-10-28-analysis/`:
  execution manifest, masked export and sealed notes, explicit adjudications,
  results, precision sensitivity, resource summary and verification records.

## Recommended next work

1. **Preserve the five BS failures with their successful PO counterparts as local
   regressions**, together with the M3/M4/M5/M6 controls and the qualified wording
   sensitivity. Preserve the source/event distinction rather than retrospectively
   relabelling historical outputs.
2. **Audit the production applicability of source scope and obligation creation
   locally.** Here the obligations, observation pair and completeness declaration
   were authored and frozen by the experiment. Determine how real artifact versions
   would supply them without assuming an exhaustive source, confusing entry time
   with event time, treating an assignment as performed fact, or inventing a
   referent match. Retain abstention for unreviewed/conflicted evidence and test
   stale bindings, omitted context and false premises before any integration.
3. **Only then propose a fresh bounded generalization comparison if justified.**
   Its useful question would be whether the same explicit obligations and scope
   handling survive less convenient, distributed narrative evidence and genuine
   positive, negative, incomplete and conflicting controls. Keep an unchanged
   baseline and both orders. No new budget, case set or live run is authorized by
   this report, and the current data do not justify broader prompt tweaking.

This is a small, single-model diagnostic over eight authored scene families,
with six fresh families and one call per arm/order. It contains no generated
writer revision, production claim extraction, whole-story evaluation, provider
causal test or human preference measurement. A clean delivery batch does not
close historical delivery issues or establish an Ollama effect.

Future story-quality work must retain room for ambiguity, indirect decisions,
emotion and defensible interpretation. Factual source insufficiency should not
become automatic permission to rewrite prose. Humans retain feel, flow, character
and story-breaking judgments with machine-prepared mechanical evidence; the nine
prior human ties are unchanged.

The tracker and issue index are updated. All fourteen issue bodies and user-posted
GitHub links remain intact; no external issue is edited or closed. **Step 19 stays
IN PROGRESS; Step 20 NOT STARTED; production prompts unchanged; further live calls
PAUSED; full workflow canary ON HOLD.**
