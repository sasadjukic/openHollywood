# Output-contract failures: diagnosis and next bounded experiment

Date: 2026-10-18. **DIAGNOSIS COMPLETE; EXPERIMENT PROPOSED, NOT PREPARED OR RUN.**

F1's remaining failures are two different problems: an allowed comparison edit can
answer the wrong question, and an empty patch can be followed by an unwanted whole
report. B's assessment task was overwhelmed by output-contract errors, then one
response copied input material until truncation. These findings support testing a
clearer output interface before adding more feedback, output allowance or reviewers.
They do not establish the model's internal reasoning or qualify its literary judgment.

Source: [the 41/96-call results](../benchmark_reports/fulfillment-repair-surface-review-v61-results-2026-10-18.md).
Production remains prompt **61**, graph **9**, fulfillment policy **1**.
**Canary ON HOLD; NOT STARTED.** No prompt, gateway or validator changed; this
diagnosis makes **zero model, discovery or external network calls**.

## F1: correct location, inadequate meaning; correct no-op, wrong envelope

**a01, both seeds:** F1 patches the correct comparison field and supplies the
required boundary reference. But its assessment describes only Elara's prohibited
entry. It does not explain why the adjacent duplicated sentence remains after
removing entry. The surrounding minor duplication finding survives unchanged.

The adapter validates location, operation, reference coverage, schema and all
out-of-scope values. It cannot prove that the new explanation answers the issue's
counterfactual question. The prompt and structural diagnostic already request that
distinction, so this is not an absent rule. The output is consistent with focusing
on the referenced boundary finding instead of comparing that finding with the
target craft issue. The correct a03 explanations show the model can express the
distinction on a closely related source. They do not explain why a01 fails.

**a06, both seeds:** F1 returns the exact parent hash and `edits: []`, then appends
the ordinary report's fields at the top level. Those extra fields equal the frozen
parent exactly. The native no-match condition was not lost or reconsidered; the
output shape was violated. Local copies retaining only the two permitted envelope
fields both validate and preserve the parent exactly. They are operator-authored
counterfactuals, not recovered model successes.

The exact request contains a long ordinary critic system instruction to complete
checks, conditions, issues and scores, followed by the diagnostic patch instruction
that explicitly supersedes the whole-report shape. It also contains both the full
ordinary schema and the patch schema. This gives the model competing output cues
even though their intended precedence is stated. The observed hybrid output is
consistent with that conflict. Causation remains untested: a05 returns only the
empty patch under the same general arrangement.

Keep the two qualified a03 recoveries and the successful narrow corrections. Do not
count a01 as qualified because it passes validation, or diagnose a06 as a new story
comprehension failure. Its known inherited warning-acceptance overclaim also remains
a source caveat. A future production path should normally reuse an already valid
report without a model repair call; the no-op calls here deliberately challenge
identity preservation and are not a proposed production retry policy.

## B: output ambiguity and copying burden precede the judgment test

All **41 dispatched requests** have `response_schema=null`. The schema appears in
prompt text. The checked-in Ollama gateway only adds a wire `format` when that
request field is populated, and currently rejects schema-enforced requests on its
Cloud path. Thus these runs did not use decoder-enforced JSON; this was not a lost
schema in the diagnostic builder. No fresh provider-capability query was performed,
and this diagnosis makes no claim about features outside the checked-in adapter.

Unlike F1, B has one short comparative system instruction. Its confusion occurs
between a large input object and the requested output object inside that input:
`changed_units` is input data, while `change_assessments` is required output. Four
completed slots use the input-style name on both attempts. Other slots repeat JSON
keys, including one contradictory duplicate `fact_checks` value. The terminal
response goes further and emits input fields and catalogs rather than assessments.

The detailed evidence narrows what the citation failures mean:

- Of **136 mismatching citation occurrences** in the completed raw assessments,
  **134 are exact fragments of the correct catalog entry**. The remaining two
  combine text across entries. These counts describe the recorded raw projections;
  conflicting duplicate values remain separately preserved and unaccepted.
- The validator requires equality with the **entire** catalog entry. The prose
  instruction asks for exact version-bound quotes, but does not spell out that a
  correct shorter excerpt is invalid. Those fragments show copying-contract failure,
  not 134 invented facts or wrong-source references.
- The contract requires a nonempty `mandatory_failure_assessment` even when the
  flag is false; 13/16 responses supply null or empty text. Non-uncertain craft
  judgments require evidence even when their effect is neutral. The schema conveys
  these rules, but the response often follows more permissive conventions.
- Version IDs, record IDs, full sentences and references are repeatedly reproduced
  by the model even where the application already knows the immutable binding.

The schema itself is present and valid. Fake-provider fixtures proved that the
application could accept compliant responses and reject bad ones. They could not
prove that the live model would reliably produce this novel, verbose contract.

### Why the structural corrections did not recover B

The frozen validator returns the first encountered failure. For example, a retry
receives a duplicate-key location, or a generic missing-required-fields error at
`output`. It does not receive a complete inventory of the other errors underneath.
The retry still regenerates the complete large response.

Four duplicate-key parents cannot be parsed by the strict decoder and retain no
semantic leaves. Four parseable parents retain 95 leaves without drift, but their
change judgments are under the wrong key and outside the retention map. That
explains why a change label can vary despite correct enforcement of the retained
fields. It is not evidence that the retention comparison silently failed.

Offline copies of **15 unambiguous responses** collapse identical duplicate keys
and, where applicable, rename the wrong change container without altering its
records. **All 15 still fail**: null/empty required text, invented hidden-purpose
IDs, citation binding or missing craft evidence remain. The conflicting duplicate
response is not normalized. Therefore a field rename or permissive JSON parser
alone would not produce usable reviews. These copies remain ineligible evidence.

### Why the next call truncated

The minimal-control response reaches 8,000 output tokens while echoing input fields:
`changed_units`, `context_artifacts`, `diff`, claims, facts, fulfilled passage,
repair tests, `original` and part of `revision`. It includes the complete original
prose and emits none of the root assessment fields before the cutoff. It is not a
nearly complete review that simply needed a little more room.

The other completed B responses use only **1,292–3,102 output tokens**. The terminal
input uses 15,183 tokens, below the 24,000-token allowance. This points to task/output
confusion and input copying, not evidence that the intended review inherently
requires more than 8,000 output tokens. Raising the cap could merely extend copying.
The exact internal cause remains unknown. The frozen whole-run stop was correctly
enforced; its unused 55 calls remain unavailable for continuing that run.

Fixing delivery is also not enough to claim judgment quality. Even the raw text
confuses optional imagery with required repair, misses the mixed ending's concrete
losses, and in b01 promotes an unnecessary deletion when purposes are shown. The
no-op and within-cited-sentence controls were not reached. A usable interface must
still pass those substantive tests.

## Proposed A: separate the repair contract, then test issue-local focus

Use four exact existing parents: **a01** (wrong comparison meaning), **a03**
(successful masked-error comparison control), **a05** (genuinely missing decision,
valid native condition) and **a06** (valid compound condition, hybrid no-op output).
Keep full source prose/context, parent hash, allowed locations, ordinary validity
rules and the unchanged resulting-report validator.

1. **F1:** unchanged restricted-edit diagnostic baseline.
2. **F2:** one active patch-output contract. Preserve the ordinary rules and schema
   verbatim as clearly scoped references for the resulting report; they do not ask
   the model to emit a whole report. Put the diagnostic output contract after the
   reference material, with an answer-free shape illustration and explicit no-op
   envelope. Output schema, allowed changes and semantic requirements stay the same.
3. **F3:** F2 plus a local comparison-focus record derived from the diagnosed issue
   pointer: the exact issue description/evidence, the reported comparison targets,
   and the question of what defect remains after their minimal repair. No expected
   classification, reference selection, answer or new story allegation is supplied.
   The response contract remains unchanged.

Run F1/F2 on all four parents at two new seeds: **16 calls**. Run F3 only on a01/a03,
where a comparison is diagnosed: **4 calls**. For no-comparison controls, F3 is
defined to delegate to F2; reuse those observations explicitly rather than purchasing
duplicate calls or treating them as independent successes. Total **20**, no retries.

F2 is the primary protocol candidate. Require four qualified comparison corrections
and four exact valid native-control identities; report its paired improvement over
F1 separately, including no demonstrated advantage if both reach the ceiling.
F3 tests the additional semantic focus: require all four comparisons
supported, at least two extra qualified recoveries over F2, and no losses. If F2
already reaches the ceiling, record no demonstrated need for F3. Every explanation
is inspected for the target craft defect, not just coverage of the boundary ref.

F2 is a delivery/precedence package; it does not isolate each sentence or the effect
of moving a schema by itself. F3-F2 isolates the added local focus within that
package. Neither permits automatic semantic repair or production adoption.

## Proposed B: output delivery versus redundant metadata generation

Reuse all **nine frozen original/revision pairs**, including both no-ops, both
minimal repairs, the mixed ending and the synthetic craft edit inside a positively
cited sentence. Make no new writer calls. Use the same full prose, source context,
diff, task and fact checks, change judgments, literary axes and optional-task scope.
Keep purposes hidden in every arm; explanation influence waits until there is a
usable independent assessment interface.

- **V0:** unchanged purpose-hidden diagnostic baseline.
- **V2:** same output schema and required information, but clearly separate source
  material from one final active response contract. Show its shape without expected
  answers; explicitly state existing requirements for complete catalog quotations,
  evidence for neutral effects and nonblank negative-case explanations. Do not add
  new judgment criteria or a worked story example.
- **V3:** same V2 delivery and judgments, but remove redundant model-generated
  original/revision version IDs and quote text. The model chooses side-specific
  evidence handles; an isolated adapter resolves each handle to its exact frozen
  version and complete catalog text. The application supplies the already-bound
  version envelope. Task, fact and change identities remain required. It does not
  choose evidence, fill missing references, reinterpret opinions or repair prose.

Unknown/stale handles, duplicate/missing records and unsupported textual claims
still fail. Check the expanded canonical assessment with the same identity/evidence
rules. The adapter's deterministic metadata resolution is declared in advance;
it is not a rescue of old outputs. Local tests must prove canonical equivalence
for valid fixtures and rejection of wrong references, versions and omissions.

**9 pairs × 3 arms × 2 seeds = 54 calls**, one attempt per slot. V2-V0 measures the
delivery package; V3-V2 tests the removal of redundant metadata generation. V3 is
the predeclared candidate, not whichever arm wins afterward. Report all structural
and semantic results separately, including output size and input-echo failures.

For V3 to qualify as a promising diagnostic assessor, require all 18 reports valid,
correct task/factual judgments in every cell, both no-op defects detected at both
seeds, no invented hard failure on minimal/craft controls, and all six actual
boundary-revision cells to distinguish extra changes from necessary repair. The
mixed case must acknowledge supported gains/losses or uncertainty. Correctly allow
the within-cited-sentence craft repair while retaining its fact. Favoring unchanged
prose or every smaller diff fails this test. Literary preference remains human work.

## Budget, stop rules and preparation boundary

| Comparison | Calls, including controls | Retries |
| --- | ---: | ---: |
| A: F1/F2 on four parents; F3 on two comparison parents; two seeds | 20 | 0 |
| B: V0/V2/V3 on nine prose pairs; two seeds | 54 | 0 |
| **Proposed total ceiling** | **74** | **0** |

Use proposed seeds **19801/19803**, temperature 0.2, top-p 0.95 and thinking disabled,
with the same pinned gemma4 Cloud identity through the local daemon. No discovery
has been performed. Keep the existing 24,000 input / 8,000 output / 900 active-second
per-call caps. Maximum reservations are **1,776,000 input tokens, 592,000 output
tokens and 66,600 active seconds**. Historical-rate estimate at that ceiling is
**USD 0.48544**; actual billed charges remain unknown. Blocks are nontransferable.

Freeze balanced arm rotations and case order before execution, interleaving
negative/craft controls early. A results do not select B cases. There is no semantic
or structural correction, fallback model, writer revision, source substitution or
canary call in this proposal. Keeping one attempt per slot makes output reliability
observable without another full-report correction loop.

One explicit change to the **future diagnostic** stop policy is proposed: a fully
captured `length` response with matching identity and known usage within its
reservation fails that cell without a retry, then allows the next already-frozen
cell. This ensures a known baseline truncation does not hide all controls. Unknown
outcomes, missing usage/captures, cancellation, identity drift, transport failure,
integrity failure or exceeded budgets still stop the entire run. This does not
retroactively change the old run's terminal stop and must be approved/frozen before
implementation or calls. No truncated output is parsed into a success.

If preparation is authorized, freeze all input versions and paired request deltas,
output adapters, scoring, schedule, budgets and this stop policy. Verify exact scope,
hostile source text as data, native-condition retention, empty patches, canonical
metadata expansion, unresolved placeholders, duplicate keys, unsupported citations,
captured truncation, unknown outcome, cancellation and restart using fake providers.
Check complete packets fit without silent trimming. Present that frozen plan before
seeking live approval. **None of these new prompts or harness changes exists yet.**

If V3 solves structure but misses the substantive controls, do not install a
self-approval loop: a separately bounded model crossover or human-calibrated
judgment test would then be justified. Preserve J1/P1/F1's narrow diagnostic gains,
E1's unqualified preservation status and W1's earlier limited gains. Broader story
quality still requires the [accepted weighted rubric, hard gates, full Cloud corpus
and comparable baseline](../../open_hollywood_bible/product_contract_and_benchmarks.md).
**Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**

## Local diagnosis evidence

`data/diagnostics/fulfillment-output-contract-diagnosis-2026-10-18/` contains the
offline audit, 17 labelled operator counterfactuals, findings, verification and
closure. It verifies 378 source live files, 108 preparation/operator files, 151
code dependencies, 40 completed attempts and the terminal capture. The source
closure remains
`0b18760f12ac580d7a75ecb26a133d78573c3d717d3a7b2055a277e486de7df4`.
Historical evidence and production code are unchanged. Local copies are never
counted as new model successes.
