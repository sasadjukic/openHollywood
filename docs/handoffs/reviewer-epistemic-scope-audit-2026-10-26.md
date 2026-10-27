# Local thinking-mode regression and epistemic-scope audit

Date: 2026-10-26. **Complete locally; zero inference and zero daemon calls.**

This follows the [thinking-mode results](../benchmark_reports/reviewer-thinking-mode-v61-results-2026-10-26.md).
The main finding is an evaluation-contract problem alongside a claim-scope
mismatch: the actual instructions allow `unsupported` for unestablished premises,
while the frozen gold expects `uncertain`. Many label failures therefore do not
isolate model reasoning. The conditional answer still fails the frozen observed-
instance target, but its wording admits an alternate reading that needs a clearer
future contrast. Historical outputs, scores and decisions remain unchanged.

Production **prompt 61 / graph 9 / fulfillment policy 1** remains unchanged.
Selective thinking has not been enabled. Further live calls are **PAUSED** and the
canary is **ON HOLD**. The [next 32-call proposal](reviewer-epistemic-clarity-proposal-2026-10-26.md)
is not a frozen plan or an authorization to run.

## Preserved regressions

Private bundle: `data/diagnostics/reviewer-epistemic-scope-audit-v61-2026-10-26/`.
It preserves byte-identical copies of **all 48 raw responses**, the original
receipts and complete source packets, **all 326 valid component assessments**,
their exact bindings, and the preceding sealed source judgments. Raw thinking is
preserved only as part of the original capture; semantic fixtures use final
content and existing source adjudication, never the thinking trace.

The fixtures include:

- Eight NC false acceptances paired with eight TH recoveries in H/U/G1/G2, plus
  their true rule violations and intention/action conflicts in both orders.
- All sixteen uncertain-source targets across Y/F3/G4/G5, with returned labels,
  frozen gold, reason truth and completeness kept separate.
- Five NC endpoint label/reason disagreements, their TH successes, and the two H
  craft explanation defects. All 59 captured craft components remain available.
- Twelve genuine same-instant target judgments and three valid sequential-state
  judgments, alongside the rest of the successful assignment/craft controls.
- **M-NC-F1-OR**, one invalid normal-stop report with three duplicate `claim_id`
  members. It remains rejected intact: no repair, retry or partial semantic credit.

These are component fixtures from the same 48 historical calls, not 326 independent
model observations. Tags overlap. No new model evidence was created.

## The actual label contract overlaps

All 48 prepared requests contain the same system definition. The audit retains
the exact text, its hash and substring offsets. Its relevant sentences are:

> Unsupported means it includes a premise the sources contradict or do not establish.

> Use uncertain when the supplied material does not permit a confident judgment.

The first sentence explicitly permits `unsupported` when a premise is not
established. The second also permits `uncertain` for the same evidential situation.
The component instructions preserve claim scope but do not remove that overlap;
the source-bound gold is deliberately withheld from the model and cannot act as
an instruction resolving it.

| Sixteen uncertain-source target responses | Count | Interpretation |
| --- | ---: | --- |
| `unsupported`, with an accurate explanation of unestablished timing | 14 | Fits the literal legacy unsupported definition; fails the frozen primary gold |
| `uncertain`, with grounded, complete reasoning | 1 | NC/F3/OR; matches frozen gold |
| `supported`, with a conditional explanation | 1 | TH/F3/RO; answers a different scope from the frozen observed-instance target |

Seven of those fourteen `unsupported` responses are NC and seven are TH. This
is not evidence that high thinking invented different event times in those seven
cases. Their explanations preserve the evidential limit. Calling these seven
TH outcomes straightforward failures to understand uncertainty would overstate
what the test establishes.

The original counts and `retain_limited_evidence_no_advancement` decision remain
the reproducible result under the predeclared scoring. This audit adds the
interpretation limit; it neither retroactively awards credit nor promotes TH.
The eight factual-compatibility recoveries remain meaningful: their compatible
facts, real rule violations and intention conflicts are different from this
unknown-label ambiguity.

## Prospective interpretation, without changing current prompts

For a separately prepared diagnostic, use disjoint factual definitions:

| Evidential situation | Prospective label | Complement of the proposition |
| --- | --- | --- |
| Evidence establishes the complete proposition | Supported | Refuted |
| Evidence refutes a material part of the proposition | Unsupported | Established for that complete proposition's negation |
| Neither side is established | Uncertain | Still uncertain |
| Source expressly leaves a material alternative unresolved | Uncertain | Still uncertain |

Keep `unestablished` and `explicitly_unresolved` as audit annotations rather than
introducing another response enum by default. The earlier local four-status
projection already represents both; this audit reuses it without rewriting
historical NC/ES judgments or adding a production schema.

“The record does not establish that the readings were simultaneous” is different
from “the record establishes that they were not simultaneous.” A reviewer can be
confident that the record is inconclusive; confidence does not turn that finding
into a refutation of the underlying event claim.

Qualified craft has its existing standard: a reading can be supported because it
is defensible, without being uniquely compelled. Its factual premises still need
grounding. Non-unique interpretation, uncertain facts, incomplete citations and
abstention because of citation limits are different conditions. An unknown fact
or an evidence-budget problem is not by itself an instruction to rewrite a story.

## Conditional truth does not establish an observed instance

The F3 source identifies the same shutter and opposite literal records. It
explicitly leaves common timing unresolved. The frozen claim asks whether those
records contradict as descriptions of that shutter at the same instant.

TH/F3/RO acknowledges the unresolved timing, then reasons that opposite states are
incompatible at one instant. That is a valid conditional observation. It does not
establish that these particular records describe one instant. Its `supported`
label therefore fails the frozen observed-instance target; the existing source
judgment correctly separates true premises from incomplete relation coverage.

There is a design limit: the phrase **“as descriptions … at the same instant”**
can be read conditionally. We cannot identify whether the output arose from that
interpretation, a reasoning error or another mechanism. The future test should
state the observed-instance and conditional propositions separately in fresh
cases, identically in both arms. It should not claim a repaired reasoning ability
merely because a label changes.

Eight source-bound relation audits cover X/Y/F1/F2/F3/G3/G4/G5. Each retains the
exact two assertion excerpts, source/version bindings, identity witnesses, timing
witnesses and literal-state witnesses. For these specifically authored physical-
state contradictions, the observed claim requires all of:

1. The descriptions concern the same referent.
2. They concern the same instant.
3. They report mutually exclusive literal states.

The separate conditional rule supplies none of the missing observed premises.
X/F2/G3 establish them; F1 explicitly refutes common timing; Y/F3/G4 leave timing
expressly unresolved; G5 omits it. First/second ledger-entry order does not supply
measurement-time order. Unresolved source timing is not automatically a plot hole.

Twelve authored logic contrasts also cover different referents, absent identity,
hypothetical-only statements, identical states, illegible states and mixtures of
refuted and unknown premises. Negating an unknown conjunction leaves it unknown;
an established-false material conjunct can refute the conjunction even if another
part is unknown. These are local authored checks, not new model successes.

The small diagnostic utility validates exact authored claim scope and applies the
existing status algebra to supplied annotations. It does **not** infer semantic
truth from prose, classify arbitrary free-text explanations, automatically correct
model labels, or authorize writer changes. A negative test deliberately supplies
a false established-time annotation: the projection then produces a wrong
supported result. This preserves the limitation that application aggregation
cannot manufacture trustworthy semantic inputs.

## Correction to the preceding report's citation arithmetic

The previous report says R012 already occurs elsewhere in M-TH-H-RO/C01 and would
add zero references. The raw C01 union is actually **R014/R015**. R012 appears in
other claims, not in C01. Adding it to C01.A03 would increase this claim's union
from **two to three**, an incremental cost of **one**, still below eight.

This corrects the explanatory arithmetic without changing the missing-witness
finding, historical scores or the conclusion that the limit did not force the
omission. The prior report and its seal are preserved; this document is the
explicit correction. The other H fixture retains R013/R014 as witnesses against
the claim that R015 directly follows R012. It remains a review-explanation
precision issue, not a new judgment that a human would dislike the scene.

## Verification and next decision

**177 offline tests pass: 110 new audit tests plus all 67 preceding execution
tests.** Ruff lint/format and strict mypy pass on four new scripts. Checks cover
all 48 exact raw/wire replays, all 326 component bindings, paired recoveries and
controls, literal contract overlap, sixteen uncertain-source annotations, source
and scope tampering, conditional/observed counterexamples, false semantic inputs,
craft standards, duplicate delivery and corrected citation arithmetic. Real HTTP
is blocked. **4,521 historical fingerprints** verify, including the frozen requests,
raw captures, inspection and preceding report. No production code was modified.

The tracker and issue index record completion. All fourteen issue bodies and
posted GitHub links are preserved; no external issue is edited or closed.

The [proposed 32-call comparison](reviewer-epistemic-clarity-proposal-2026-10-26.md)
would hold high thinking fixed and test a disjoint factual-label definition
against unchanged TH controls. Fresh full-scene contrasts would make observed and
conditional scope explicit. This is a test of interface clarity first; semantic
recovery would need its own contemporary evidence.

Considering high thinking selectively for difficult factual relation review is
reasonable given the eight paired recoveries. Enabling it throughout the workflow
is not supported by this evidence. No production setting or routing was changed,
and no writer, whole-story preference or full workflow test occurred. The nine
prior human ties remain unchanged. Humans continue to assess feel/emotion, flow,
character and story-breaking details with machine-prepared mechanics.

**Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED; canary ON HOLD.**
