# K2/L1 source-obligation audit

Date: **2026-10-28**. **COMPLETE — local work only; no inference or daemon calls.**

The four K2 failures are preserved. The audit confirms a narrower problem than a
failure to notice missing timing: the responses describe the missing evidence
correctly, but return the wrong label for the frozen source-sufficiency claim.
Whole-claim aggregation preserves that raw error; it does not create it.
K2's contrast with L1 remains confounded, so negation, object type or surrounding
story cannot be named as its cause.

This follows the [completed SE/BS/ER results](../benchmark_reports/reviewer-source-sufficiency-v61-results-2026-10-28.md).
The [next proposal](reviewer-source-obligations-proposal-2026-10-28.md) changes the
measurement task: obtain separate identity, literal-opposition and timing judgments,
then derive event and source-sufficiency labels separately. It is not a frozen or
approved experiment, and the local algebra is not a production fix.

## Preserved evidence

Private bundle: `data/diagnostics/reviewer-source-obligations-audit-v61-2026-10-28/`.
It retains **36 byte-identical raw captures, 252 component regressions**, exact
requests/source bindings and sealed historical adjudications. The prior analysis
seal remains `7900144c3535b127ae3362806177b5ac478d4879889a93a34640aa39f8943816`.

| Exact capture | Raw target C02.A01 | Frozen target gold | Conditional A02 | Application C02 |
| --- | --- | --- | --- | --- |
| C-SE-K2-OR | Uncertain | Unsupported | Supported | Uncertain |
| C-SE-K2-RO | Uncertain | Unsupported | Supported | Uncertain |
| C-BS-K2-OR | Uncertain | Unsupported | Supported | Uncertain |
| C-BS-K2-RO | Uncertain | Unsupported | Supported | Uncertain |

All four deliveries are valid. `k2-source-claim-failures.json` binds each raw
assessment, conditional, whole result, source witnesses and historical score.
The corresponding intact captures are under `captures/<capture ID>/raw-response.json`.
Thinking is retained opaquely in the raw response but is not semantic evidence.
No label is repaired and no historical gold or score is changed.

`k2-l1-contrast.json` preserves the twelve K2/L1 × SE/BS/ER × OR/RO records.
`source-obligation-audits.json` contains six family/form audits with full packet
identities, exact source offsets, claim maps, neighboring qualifications and
explicitly authored premise judgments.

The two qualified craft concerns remain separate in `qualified-craft-fixtures.json`:
SE/L2/RO's before/until wording and SE/L1/OR's hand-guidance attribution. Neither
is converted into proven event invention. The prior annotation clarification and
sensitivity are preserved; accepting both still leaves the target failures and
no-advancement decision unchanged.

## What K2 and L1 share, and what differs

| Feature | K2 costume room | L1 bicycle workshop |
| --- | --- | --- |
| Referent | One brass hook beside the mirror | One wheel-stand latch |
| Recorded predicates | Occupied by a coat / holding no object at all | Fully open / fully closed |
| Literal scope | Explicitly physical descriptions | Explicitly physical descriptions |
| Observation time in the full packet | Absent | Absent |
| Neighboring C03.A02 | Same hook, not two hooks | Same latch, not two latches |
| SE result, both orders | Uncertain: wrong source label | Uncertain: wrong source label |
| BS result, both orders | Uncertain: wrong source label | Unsupported: correct source label |
| ER result, both orders | Uncertain: correct event label | Uncertain: correct event label |

K2 revision R012 identifies the hook; R013–R015 supply the two literal states.
R016's erased price does not date either observation. Later staircase, torch and
afternoon actions do not date them either. L1 R011 identifies the latch;
R012–R014 supply the states. R015's thumbprint, the later brake demonstration and
the fair's afternoon setting do not date the ledger observations. Both originals
contain the same relation passages. Both contexts supply assignments, story facts
and the same C005 uncertainty/voice policy, with no missing observation timestamp.

These are findings from review of the complete source packets, not deductions
from the cited lines alone. Claims under assessment cannot supply story evidence.
No amount of repeating the supported conditional establishes its antecedent.

The BS change produces **two L1 label recoveries and zero K2 recoveries**, from
two valid contemporary opportunities in each family. The explanations already
recognize source insufficiency; these are not new grounding recoveries.

K2 uses an asymmetric occupancy predicate and a universal negative; L1 uses
parallel adjectival antonyms. Family, object, predicates, claim syntax, source
positions and surrounding narrative were not independently crossed. Both have
a referent qualifier rather than a neighboring timing answer. This rules out
neither a wording effect nor a family effect; it establishes neither one.
The captures do not reveal an internal reasoning path or a provider cause.

## Source sufficiency and event uncertainty are different outputs

For these specified observations, audit three obligations separately:

1. They concern the same entity.
2. Their descriptions are literal and mutually incompatible if simultaneous.
3. They concern the same observation instant.

Both K2 and L1 have the authored status vector **established, established,
unestablished**. A complete review of these finite packets can reject the claim
that the source establishes all three while leaving the underlying relation
uncertain. Absence of a timing statement is not proof of different times.

| Reviewed premises and scope | Event relation | Source-sufficiency assertion |
| --- | --- | --- |
| All three established by reliable witnesses | Supported | Supported |
| Same object/opposite states; time unestablished; full scope reviewed | Uncertain | Unsupported |
| Different time or entity explicitly established; full scope reviewed | Unsupported | Unsupported |
| Time unestablished; declared source partly unavailable | Uncertain | Uncertain |
| Timing not reviewed, or unresolved conflicting authorities | Uncertain | Uncertain |

The last two rows prevent an unwarranted source-wide conclusion. For incomplete
scope, **S** means the declared record including an unavailable appendix; **V** is
the visible subset. “S establishes P” is not interchangeable with “V establishes
P.” Merely omitting context while continuing to claim about the complete visible
packet would not create a valid incomplete-scope contrast.

The existing factual contract says unsupported requires a refuted material
premise, while uncertain covers an unresolved proposition. Historical source
gold treats the assertion about the sufficiency of the fully reviewed finite text
as refuted. This audit retains that contract and gold. It does not claim the
current instructions explicitly teach every level of this distinction.

## Local regression boundaries

`obligations.py` implements only an algebra over independently authored premise
statuses and explicit source/review flags. Exact packet, claim and observation-pair
bindings are required. Unknown fields/statuses and mismatched identities fail.
Unreviewed or conflicted evidence cannot become an automatic negative. The helper
never authorizes a writer, changes a captured label or judges literary quality.

There are **42 authored contrasts**: 32 combinations of setting, predicate form,
timing and entry order, plus ten boundary examples. They include context-only
timing, incomplete source scope, incomplete review, different/unknown referents,
figurative descriptions, conflicting time authority and compatible negation.
Six predicate controls preserve these distinctions:

- A coat is an object; no object entails no coat. No coat does not entail no object.
- Not fully open does not entail fully closed when intermediate states are possible.
- A coat and no scarf are compatible descriptions.

These expected relations are authored fixtures, not natural-language reasoning
performed by the code. The algebra's tests deliberately supply a false but
well-formed K2 time premise; it produces a wrong supported result. That negative
control demonstrates the limit: hashes, schema validity and correct arithmetic
cannot establish that a model's premise judgment is true.

## Why another wording repeat is not justified

Earlier work already tested a [premise-check instruction](reviewer-premise-comparison-proposal-2026-10-24.md),
[component-to-whole aggregation](reviewer-component-assessment-proposal-2026-10-25.md)
and [evidence-status categories](reviewer-epistemic-status-proposal-2026-10-26.md).
Typed epistemic algebra also already exists locally. None is newly discovered here.

The proposed new measurement is narrower: **independently obtain the three
primitive statuses inside the remaining composed relation target**, retain their
evidence, and derive two different claim objects from them. Earlier component
maps still asked for a composite relation verdict; the evidence-status arm still
classified that composite relation. Another rename or reminder would not meet
the materially different hypothesis requirement.

The locally justified question is whether the model can deliver accurate primitive
judgments when its composed source label fails. The captures' grounded missing-time
reasons make this plausible, but do not prove it will work. If the primitives are
wrong, aggregation merely relocates the failure. A correct derived label with
wrong premises must receive no usable recovery credit.

## Verification and disposition

**164 offline tests pass: 107 current audit checks plus all 57 preceding execution
checks.** Ruff lint/format and strict mypy pass on four scripts. The initial
163-test run passed; adding explicit S/V scope checks triggered one lint finding,
corrected before the final complete rerun. Verification records are retained.
All **6,488 historical fingerprints** verify. Tests block real HTTP. Audit assets,
documentation and unchanged issue bodies are recorded in the local closure/seal.

No application code, dependencies, production prompts or routing changed;
application/frontend build checks are inapplicable. All fourteen issue bodies and
posted GitHub links remain intact; no external issue is edited or closed.

Production **prompt 61 / graph 9 / fulfillment policy 1**, Blueprint approval,
historical budgets and nine human ties remain unchanged. Human review retains
feel/emotion, flow, character and story-breaking judgments with machine-prepared
mechanics. No story-quality gain, writer-edit permission, production thinking
policy or provider conclusion follows. **Step 19 IN PROGRESS; Step 20 NOT STARTED;
live calls PAUSED; full workflow canary ON HOLD.**
