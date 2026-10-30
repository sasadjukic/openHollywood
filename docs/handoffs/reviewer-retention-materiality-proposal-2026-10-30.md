# Proposed PO/EX semantic-retention and exact-copy comparison

Date: **2026-10-30**. **PROPOSAL ONLY — not prepared, frozen or approved.**
Maximum proposed budget: **32 calls**. Live calls **PAUSED**; canary **ON HOLD**.
Production prompts and historical scoring remain unchanged.

The [local audit](reviewer-retention-materiality-audit-2026-10-30.md) exposes a
new testable gap: all 80 recent discovery/decision assessments concerned 20 unique
sentences copied unchanged into their revisions. Those controls do not test
meaning-preserving rewrites or misleading copied text. The seven precision flags
also show why a comparison must explicitly identify its two sources.

**Hypothesis:** giving the reviewer application-owned, pair-specific exact-text
receipts can reduce false literal-comparison assertions while preserving correct
semantic and source judgments. The counter-hypothesis is that such receipts
encourage the reviewer to substitute text equality for semantic fulfillment,
especially when the same words appear in a quotation or about another actor.
This tests new information supplied to the reviewer and new semantic contrasts;
it is not another run to rediscover a known string mismatch.

## Design and controls

| Arm | Proposed treatment |
| --- | --- |
| **PO** | Unchanged source-obligation protocol, output schema and application source/event projection. Preserve exact historical PO requests for known anchors. |
| **EX** | The same PO protocol and response schema, with a bounded read-only input block containing application-owned original-to-revision and assignment-to-revision exactness receipts for the discovery/decision spans. |

The receipt block would state the selected pair, immutable source versions and
field/offset bindings, exact quotes, equality result and its text-only scope.
No semantic label, expected judgment, repair decision or materiality gold may
appear in the wire payload. Full surrounding prose remains visible in both arms.
Receipt source alignment is authored and audited during preparation. Its
correctness is checked mechanically; this comparison would not validate an
automatic alignment or claim-extraction system. Schema shape, evidence budgets,
reason limits, presentation format and all unrelated instructions stay fixed.
Any necessary explanatory text for the receipt is part of the frozen diagnostic
treatment, not a production prompt change.

Proposed matrix: **eight families × two arms × OR/RO = 32 attempts**, sixteen per
arm, one sample per cell. The two orders are paired presentations, not independent
stories or repeated seeds.

| Families | Required contrast |
| --- | --- |
| Known **N8 and N4** | Definite false comparison and ambiguous verbatim anchors. Four historical PO wires remain byte-identical, including their original sources and claims. |
| Fresh 1 | Complete discovery/decision preserved through substantive paraphrase; original-to-revision comparison differs. |
| Fresh 2 | Decision established through intentional action and dialogue; no copied decision sentence. |
| Fresh 3 | Exact decision sentence occurs in a fictional/rehearsal quotation; the actual decision is explicitly absent. |
| Fresh 4 | Exact words concern a different identified actor; the required protagonist's decision is explicitly absent. |
| Fresh 5 | Similar wording reverses a required polarity or prerequisite; the complete assigned fact is not retained. |
| Fresh 6 | Earlier actual decision is retained, including its copied sentence, but a later act violates a separately specified endpoint condition. |

Author complete fresh scene pairs, not six replacements of names in one template.
Keep enough coherent context to resolve attribution and scope without depending
on ambiguous literary interpretation. The fresh cases must include both positive
and negative semantic gold, exact and nonexact comparisons, and independent craft
and source-relation controls. Preserve source inventories and PO premises from
the established contract. Do not infer semantic gold from text equality, or label
an earlier decision absent solely because it is later reversed.

The first **eight calls** cover both known anchors, both arms and both orders.
Counterbalance arm order globally and within families. There are **zero retries,
repairs, replacements, extra probes or reallocations**. Reserve before dispatch;
an attempted call consumes its slot even if delivery or usage is unknown.

## Prospective scoring

Freeze independent semantic/source/copy gold and the explanation-truth and
materiality rubric before dispatch.
Keep the following outcomes separate; do not reduce them to a new blended score:

1. **Delivery and evidence binding.** Report every reserved cell, raw output,
   normal/abnormal finish and exact source binding. Invalid delivery receives no
   semantic recovery credit.
2. **Complete semantic judgments.** Inspect actor, modality, attribution,
   polarity, time and event-versus-endpoint scope against full sources. Require
   correct, grounded EX judgments on every new contrast in both orders; retain
   every actual valid PO-to-EX loss. Correct labels with unsupported premises
   cannot count as semantic success.
3. **Literal-comparison precision.** Mechanically verify assertions with an
   explicit pair. Inspect what comparison the explanation actually asserts;
   do not use a keyword detector to infer its referent. Report definite false
   assertions and ambiguous comparisons separately. Silence about copying is
   neither an exactness error nor proof of improved semantic reasoning.
4. **Explanation materiality.** Record false incidental exactness claims as
   report-precision defects even when semantic fulfillment is independently
   established. Record altered conclusions, invalid evidence scope and
   unnecessary repair implications as material review errors. Ambiguous
   referents remain unresolved. Preserve a strict explanation-grounding view
   alongside the scoped semantic view, both specified before the run.
5. **Protected controls and resources.** Require all EX PO premises and
   source/event projections, independent conditionals, assignment/endpoint and
   qualified craft controls to remain correct and grounded. Track input and
   combined generated tokens, active request latency and per-usable-report
   costs descriptively. Exact copying is not a craft-quality score.

Retain the receipt hypothesis as a diagnostic signal only if there is at least
one **actual contemporary matched definite-precision recovery**, no new EX
definite-precision error, no protected semantic/source/craft loss, and all EX
fresh semantic contrasts pass. Also require ambiguous-referent annotations not
to increase. A historical error that does not recur is not a recovery. If PO
already succeeds everywhere, record alignment with no demonstrated treatment
advantage. If EX eliminates false wording claims but fails the fresh semantic
contrasts, reject the receipt treatment as sufficient for this task. No outcome
alone qualifies production integration, prose editing or whole-story quality.

Export arm/order-masked final reports; inspect against full sources and seal
notes before decoding the trial key. Acknowledged partial masking is required:
known scenes or comments about receipts can reveal treatment. Model thinking is
not semantic evidence. Report original frozen scores without retrospective
changes, and do not treat this assistant audit as blind human preference.

## Budget, stops and preparation boundary

Proposed model: **deepseek-v4.1-flash:cloud**, high thinking, temperature **0.2**,
top-p **0.95**, seed **20261022**, context **40,000**, non-streaming, no format
override. **0.40.13 is the last captured daemon version**, not a current check;
this local audit made no metadata calls. During separately authorized preparation,
capture version/tags/show only and document any baseline change before freezing.
Do not quietly attribute a cross-version difference to the receipt treatment.

| Limit | Per attempt | 32-attempt reservation |
| --- | ---: | ---: |
| Input tokens | 24,000 | 768,000 |
| Combined generated tokens, including thinking | 16,000 | 512,000 |
| Active request time | 600 seconds | 19,200 seconds |

Actual billing, effective sampling and reasoning/final token splits remain
unknown unless directly reported. Do not invent a current tariff or count
thinking twice. Report receipt overhead as part of EX's real input cost.

Retain the established delivery sentinel: after eight calls, stop if either arm
has zero valid deliveries or the same EX blocking delivery signature appears in
both known families. Repetition within one family alone does not trigger that
signature stop. A single invalid response stays a failed cell; no retry. Global
terminal stops cover non-200/transport/gateway failure, truncation/non-stop
finish, absent high-thinking output, unknown or invalid usage/timing,
per-call/aggregate resource breach, changed daemon/model metadata, changed
plan/source/wire fingerprints, ledger gaps, ambiguous dispatch and user
cancellation. Preserve terminal error chains and unknown usage. Do not
resume a terminal stop automatically. No semantic early stop or extra calls
based on promising results. A clean completed-cell boundary can resume only
within its remaining frozen slots.

Before asking for live approval, separately prepare and verify all eight cases,
claims/components, two explicit comparison selections per discovery/decision,
independent semantic gold, thirty-two exact requests, masked-inspection rubric,
budget accounting and terminal/export tests. Replay the four historical PO wire
controls and the local context/materiality negative controls. Freeze the
application receipt implementation and schema, model metadata, scoring and stops
under one plan hash. Show that frozen plan for approval; this proposal authorizes
none of those live calls.

Production claim extraction, automatic source-scope assessment, selective
thinking integration, writer repairs and the full workflow canary remain outside
this experiment. Human review continues to own feel, flow, character and
story-breaking concerns, with exact mechanics prepared by the application.
