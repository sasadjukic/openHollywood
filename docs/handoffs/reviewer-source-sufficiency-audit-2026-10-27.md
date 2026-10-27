# Local forbidden-field, temporal-wording and K2 source-sufficiency audit

Date: 2026-10-27. **LOCAL WORK COMPLETE; zero inference or daemon calls.**

The [ER/SE comparison](../benchmark_reports/reviewer-claim-form-v61-results-2026-10-27.md)
exposed two different limits: closed-schema delivery errors and uncertain labels
for K2's source-entailment claim despite accurate missing-time explanations.
This audit preserves those results, adds local regressions and narrows the next
hypothesis. The [proposed follow-up](reviewer-source-sufficiency-proposal-2026-10-27.md)
is a **36-call SE/BS/ER comparison**, not prepared, frozen or approved for inference.

## Preserved evidence and delivery fixtures

The private bundle contains byte-identical copies of all **24 raw responses**, all
**154 valid component regressions**, exact cases and source bindings, and the prior
sealed source annotations. Historical scores remain SE **10/12 valid, 8/12 correct
target labels, 7/12 usable targets** and ER **12/12, 12/12, 11/12**. The frozen
decision remains **`retain_limited_evidence_no_advancement`**.

| Capture | Local regression |
| --- | --- |
| SE/J2/OR | Reject `claim_id_note` with values C01/C02/C03 in the three whole-claim objects |
| SE/K3/OR | Reject an empty `components_note` in each whole-claim object |
| Earlier TH/F3/RO and EC/J3/RO | Preserve duplicate `claim_id` keys as separate strict-parser failures |

The new failures are **six forbidden-field occurrences across two reports**, not
duplicate keys. Both returned HTTP 200, a normal stop and parseable JSON. Neither
field name occurs in the 24 frozen requests. Empty content or a redundant value
does not make an undeclared field valid. Tests also inject forbidden fields at
root, whole-claim and component levels with empty, null, false, object and string
values; all are rejected while the intact valid control still passes.

No captured output is repaired or rescored. No delivery cause is established by
the field names, and no provider explanation follows from these fixtures.

## Temporal wording: preserve the qualification

The SE/J2/RO and ER/J2/RO explanations both describe the lamp as lit “and then
unlit.” Their source places a lit entry before an unlit entry without observation
times. Both responses also acknowledge unknown timing, and their separate C03
qualification explicitly says presentation order does not establish observation
time. The original **uncertain precision annotations** remain intact: this is not
a proven invented chronology or a demonstrated failure to notice uncertainty.

Twelve authored local contrasts distinguish:

- Entry order from observation order, including an explicit entry-only use of
  “then” and a genuinely ambiguous use.
- Explicit earlier/later observations from reversed entry order with timestamps.
- Explicit same-instant observations from absent or expressly unresolved timing.
- An unrelated later torch action from the time of the inventory observations.
- A supported literal conditional from proof that its antecedents occurred.
- Failure of a bounded source to establish simultaneity from evidence that the
  observations occurred at different times.

These are manually adjudicated fixtures, not a keyword rule that flags every
“then,” a new model result, or a literary-style restriction. The previous
sensitivity check also stays unchanged: accepting both qualified explanations
would yield SE **8/12** and ER **12/12** usable targets, without changing the
no-advancement decision.

## K2: the evidence and the question being judged

The complete original/revision/context packet identifies one brass hook and two
inventory entries. Revision R012 identifies the hook; R013 says a coat occupies
it; R014 says it holds no object; R015 makes both descriptions literal. Neither
entry has an observation time. R016 concerns an erased price. The later staircase,
afternoon sunlight and torch actions do not date either inventory observation.
The original contains the same inventory passage. Context supplies assignments,
story facts and literal voice, but no missing inventory timestamp.

Let P mean that these two particular descriptions concern the same hook at the
same instant. Under the previously frozen, fully reviewed source scope:

| Claim object | Appropriate judgment | What it does not establish |
| --- | --- | --- |
| P, the observation relation | Uncertain | Neither matching nor different observation times is proved |
| The supplied source establishes P | Unsupported | Rejecting source sufficiency does not refute P itself |
| If the literal opposite states held together, they could not both hold | Supported | The conditional does not supply a matching time |

The SE target is exactly:

> These particular inventory entries establish that they describe the same single brass hook as occupied by a coat and holding no object at all at one and the same instant.

ER removes “establish that they.” C02.A02 separately supplies the literal
conditional. Whole C02 is the conjunction of those two components. Both K2 SE
responses output **uncertain for A01 and supported for A02**. Their application
aggregate is therefore uncertain. This mismatch exists in the model's raw A01
label; aggregation did not create it or substitute the conditional for A01.

Both SE target reasons accurately identify the missing common-time premise and
retain their sealed `source_insufficient` scope annotation. SE/OR also cites C005,
the voice rule preserving unresolved uncertainty. That rule does not establish
either temporal alternative. Its mention is observable; a causal effect on the
label or the model's internal interpretation is not observable from this output.

The factual definitions remain: unsupported requires a refuted material premise;
uncertain covers a proposition neither established nor refuted. The prospective
SE gold treats **the sufficiency assertion about this fully inspected finite text**
as refuted. That is distinct from treating an absent story fact as false. An
incomplete source review cannot certify source-wide non-entailment. The audit
does not change historical gold, silently translate labels, or claim that the
existing instructions explicitly teach every level of this distinction.

## Comparison with successful forms

Twelve source-bound records retain both forms across all six families, their
whole claims, component maps, source scopes and exact witnesses. The four
unknown-timing families differ in more than their objects:

| Family | Timing in source | SE wording | Neighboring C03.A02 claim |
| --- | --- | --- | --- |
| J1 pool | Explicitly unresolved | “Actually establish” plus a source/conditional clarification | Common timing explicitly unresolved |
| J2 bakery | Absent | “Actually establish” plus a conditional clarification | Entry order does not establish observation timing |
| K1 ferry | Explicitly unresolved | “Establish that they record” | Common timing explicitly unresolved |
| K2 costume room | Absent | “Establish that they describe” | Same hook, not two hooks |

J1 and K1 succeed in both orders. J2/RO has the correct target label, while J2/OR
is invalid. K2 fails the SE label in both orders. **The neighboring timing claim
is an additional confounded factor**, not a newly established cause. C03 is a claim
to assess, not authoritative evidence that may supply a missing source fact.

K1's success rules out the simple claim that the shorter syntax always fails.
J2's valid result rules out the simple claim that absent timestamps always lead
to uncertain SE labels. Family, phrasing and the neighboring qualification were
not independently crossed. The shared C005 voice text and unchanged conditional
also do not explain why only K2 has this valid-label pattern by themselves.

The supported diagnosis is narrower: the output does not reliably map recognized
source insufficiency to the frozen source-entailment label. Nested claim wording,
neighboring cues and family effects remain hypotheses. The captures do not prove
a missing capacity to recognize unknown time, an aggregation bug, a provider
fault, or a particular internal reasoning process.

## Verification and next decision

**124 offline tests pass: 80 current audit checks plus all 44 preceding execution
checks.** Ruff lint/format and strict mypy pass on four local scripts. The initial
run passed tests but found two long lines and a missing local module search path;
both were corrected, with the initial and successful records preserved.

Checks replay exact captures and requests, reject forbidden fields and duplicate
keys separately, preserve all labels/source notes, verify temporal source offsets,
reproduce K2 aggregation, protect conditional/craft controls and reject incomplete
or mismatched source scopes. All **5,697 historical fingerprints** verify. Real
HTTP is blocked in tests. The algebra consumes authored source judgments; a
negative control demonstrates that it cannot discover a false supplied premise.
Neither hashes nor these tests establish natural-language truth automatically.

The next proposed test changes only C02.A01's source-sufficiency phrasing and its
matching whole-claim text, within each family, while retaining the old SE and ER
controls. Keeping C03 fixed within each comparison prevents its different wording
from causing a within-family treatment effect. It does not independently estimate
the effect of changing C03; that remains a separate possible later experiment.

Private bundle: `data/diagnostics/reviewer-source-sufficiency-audit-v61-2026-10-27/`.
No application code, dependency, production prompt or routing changes were made;
application/frontend build checks are inapplicable. The tracker and issue index
are updated; all fourteen issue bodies and posted GitHub links remain unchanged.
No external issue was edited or closed.

Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval and
the nine prior human ties remain unchanged. Human review continues to assess
feel/emotion, flow, character and story-breaking details, with machine-prepared
mechanics. No story-quality gain or writer-edit permission follows from this
audit. **Step 19 IN PROGRESS; Step 20 NOT STARTED; live calls PAUSED;
full workflow canary ON HOLD.**
