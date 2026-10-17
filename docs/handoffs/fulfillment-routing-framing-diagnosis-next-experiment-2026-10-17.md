# Route-index and boundary-framing diagnosis; next experiment

Date: 2026-10-17. **DIAGNOSIS COMPLETE; EXPERIMENT PROPOSED, NOT PREPARED OR RUN.**

The route index did not solve obligation attribution or prevent inconsistent
reporting. Boundary framing made the endpoint more prominent but did not make
the writer's edit more selective. Stop adding reminders for now. Test whether
separating judgment from repair reporting helps the critic, and whether returning
explicit text edits helps the writer preserve adequate prose while still making
necessary and worthwhile changes.

Recommend two independent comparisons plus a craft control, **50 primary probes /
proposed 100-call ceiling**. This is a new proposal, not an extension of the closed
80-call experiment. Its unused 38 calls confer no allowance. No new candidate
prompt, schema, request bundle, model call or provider discovery was created by
this diagnosis. Production remains prompt 61 / graph 9 / fulfillment policy 1.
**Full workflow canary ON HOLD; NOT STARTED.**

## Evidence checked

The source is the [completed comparison](../benchmark_reports/fulfillment-routing-framing-v61-results-2026-10-17.md),
its [frozen plan](../benchmark_reports/fulfillment-routing-framing-v61-plan-2026-10-17.md),
and the [preceding diagnosis](fulfillment-routing-ending-next-experiment-2026-10-17.md).

At checkout `f3c209f841eeea6b9b0c7f2c8157db5d1280f173`, offline inspection reverified
407 sealed live files, 52 preparation/operator files, the results report, 121 frozen
code files and predecessor seals. All 40 probes / 42 attempts reproduce the sealed
audit after JSON serialization. Network connections and gateway construction were
blocked. Private evidence is in
`data/diagnostics/fulfillment-routing-framing-diagnosis-2026-10-17/`.

The inspection includes rejected responses, ordinary retry requests, native
conditions, complete before/after prose and all eight writer diffs. Historical
reports remain unchanged. The four exported blind human pairs remain unscored.

## Why the route index failed

| Observation | What it establishes |
| --- | --- |
| C0 ordinary: 12/12 first-valid; C1 index: 10/12 | The added map did not improve routing in this batch; the control had no routing failure to reduce. |
| Both arms finish with 8/12 correct classifications | Structural acceptance did not fix the false unmet decisions in Elena's separate and embedded overrun cases. |
| Both rejected C1 embedded responses initially say outcome met and boundary overrun | The model can identify the correct distinction, yet emit incompatible condition ownership or duplicate routes. |
| Both retries change met to unmet | A legal repair owner can be obtained by changing the judgment, rather than correcting only the route. |

### Attribution and representation are separate failures

Elena's deliberate journal comparison establishes her decision to verify. A later
match breaches the separate exit state; it does not erase that decision. All eight
wrong final outcomes use the later result to disqualify the earlier fact. Clean,
genuinely missing, compound-outcome and Elara controls retain their expected
classifications. The compound outcome actually contains the no-match restriction,
so its unmet judgment is correct. Do not simplify this into “decisions are always
met” or remove terminal clauses from compound obligations.

The index describes legal destinations. It supplies no new evidence or independent
adjudication of which obligation failed. The underlying representations still put
outcome and exit state together in the endpoint, while their native checks have
different ownership. This leaves the attribution problem intact. The
[failed scope clarification](../benchmark_reports/critic-fulfillment-scope-v59-2026-10-15.md)
and [partly successful failed-clause trial](../benchmark_reports/critic-failed-clause-v59-2026-10-15.md)
also show why another instruction or exact quotation is insufficient evidence of
sound semantics.

In C1 embedded 19301, the raw outcome is met, but the response also creates a generic
outcome violation, outcome conditions and an outcome-linked issue. In 19303, the
generic issue already links correctly to boundary; the remaining illegal part is
an `assignment:outcome` condition set owned by a met check. These are different
inconsistencies, not a missing boundary report. The index explicitly prohibits both.

For an offline counterfactual only, copies of those two rejected responses had the
illegal generic violation/condition records removed and issue references reduced
to their reported boundary finding. Their native and boundary checks were untouched.
Both copies validate as **revise** under the unchanged ordinary validator. This
demonstrates that the contract permits the correct combination. It does not prove
the model will select it, authorize automatic repair of model outputs, or make the
failed originals eligible writer sources. The copies are labelled manual fixtures.

### Retry permits semantic drift

Both retries regenerate a complete review with structural feedback. They contain
neither the rejected response nor a preserved native-status contract. Existing
classification retention concerns eligible generic issue metadata; it does not
pin these native judgments. See `_schema_repair_guidance` and
`_critic_retained_classifications` in
[production_model_executor.py](../../apps/api/open_hollywood_api/services/production_model_executor.py),
and [ADR 0036](../adr/0036-shared-consolidated-repair-conditions.md).

The observed recovery changes correct met judgments into wrong unmet judgments
whose condition ownership is legal. That is a concrete failure mode of full-review
regeneration. It does not establish that validation caused the initial attribution
error: all four ordinary Elena overrun probes were already wrong on their first,
valid response. Nor does it justify freezing an unvalidated met answer; an initial
answer can itself be wrong.

The best next diagnostic is to ask whether native and boundary adjudication improves
when the model is not also asked to generate repairs and their routes. This tests
task separation before proposing a staged production critic or changing retry rules.
The small, unmatched-length index comparison cannot prove a general causal effect
of extra tokens, field ordering or cognitive load.

Keep advice support separate as well. Three compound-review rationales contain
overclaims or overly narrow language even though the mandatory conditions are
supported. Correct statuses and valid references do not make every review sound.
No independent craft issue appeared in this run.

## Why boundary framing worsened preservation

All eight writers repair entry and retain the fulfilled facts; all eight ordinary
post-critics pass. The failure is additional revision unsupported by the supplied
repair, not factual loss or failure to stop outside.

Within each pair, W1 changes only the category, claim opening and first advice
sentence to emphasize the exit state. Prose, positive evidence, source feedback
and the rest of the repair contract are held constant. At both separate-entry
seeds, W0 deletes the forbidden paragraph and restores the clean scene exactly.
W1 additionally replaces the compatible prospective-first-step sentence with a
static poised-at-the-threshold ending. The preceding prose already establishes
that both boots remain outside.

That pattern is consistent with interpreting the reframed task as composing a
clearer ending state, rather than removing only the established entry. It is a
hypothesis about the changed emphasis, not access to the model's internal cause.
Three fields changed together, and there is no length placebo. The two W0 exact
restorations are identical text, not two distinct literary examples.

The embedded case also exposes a granularity problem. A single cited sentence
contains both a valid prospective step and a forbidden completed step. Both arms
often replace more of this local ending than necessary. W1 at 19301 additionally
changes the bracing sentence and adds a waiting/resolve beat. That is neither a
clear new assertion that the decision occurred nor an established factual reversal;
the full context still supports intent to enter. At 19303 the arms make substantively
equivalent repairs, with a minor wording difference. Across all eight outputs,
everything before the final paragraph remains unchanged.

The narrow tally remains **0 W1 wins / 3 losses / 1 tie**. Treating the 19301
psychological beat as a possible human-preferred tradeoff yields **0 wins / 2 losses /
1 tie / 1 mixed**. Neither reading favors promotion. Six endings change beyond
minimum deletion, but minimal deletion is not a literary quality standard.

The positive packet cannot explain the paired W1 deterioration because it is held
constant. The run also rules out a universal inability to make deletion-only repairs
and shows that cited text can be edited when it contains a real defect. It does
not isolate all causes of shared ending rewrites or establish quality preferences.
Uniform post-critic praise cannot settle whether a human prefers the new endings.

Do not repeat preservation reminders, history omission, advice-prefix changes or
this framing bundle. Do not solve the symptom with locked spans, a maximum diff
size or mandatory explicit decision language. The next writer test should change
how revisions are expressed, with the actual feedback held constant.

## Proposed experiment

Prepare locally only after authorization, present a sealed plan, and obtain approval
of that exact plan before any live inference or discovery. The following specifies
the design; it does not implement candidate prompts or output contracts.

### A. Ordinary review versus adjudication only

Use the same six complete cases: Elena clean, separate match, embedded match,
missing decision, complete compound outcome; and Elara embedded entry. Use new
seeds **19401 and 19403**, with arm order reversed at the second seed.

- **J0:** fresh ordinary v61 critic, without the failed route index.
- **J1:** diagnostic adjudication only: emit the existing native turning-point and
  outcome checks and existing boundary comparison, with their original field
  meanings, bounds and evidence identities. Do not generate repair conditions,
  generic issues/links, scores, POV/other-assignment reports or an overall verdict.

Keep all story/artifact context, assignment, due-now scope, endpoint/next reservation
and evidence/source catalogs identical. During preparation, freeze an explicit
allowlist of output-contract/instruction changes: preserve the existing complete-
obligation, indirect-evidence and boundary semantics; remove instructions to produce
fields absent from J1. Do not add the failed-clause intervention, an answer key,
gold status, new semantic rule or simplified compound outcome. Record this as a
combined task/output-contract ablation, not a one-word prompt comparison.

J1 uses a strict diagnostic validator for its retained fields and source identities.
It produces **no production Critique or writer evidence**, no inferred empty craft
list and no pass verdict. Its smaller response naturally has fewer ways to be
malformed; comparing whole-response validity as if the schemas were equal would
be misleading. Compare native/boundary judgments, their support and retry drift
on the shared fields. Report full-review validity separately for J0. Improvement
would support reducing simultaneous tasks; it would not distinguish removal of
routes from removal of scoring/craft tasks or shorter output as the causal factor.

Run all **24 primary critic probes**, at most **48 attempts**, independent of writer
results. Permit one structural retry per probe, with no semantic reroll or forced
status retention. Score first and final shared-field results, including extractable
judgments from invalid attempts as explicitly unvalidated observations.

A useful signal requires **12/12 supported, structurally valid J1 final tuples**,
including both missing-decision and compound negatives, all boundary classifications,
and all clean/cross-story controls; it must also improve final semantic correctness
over the concurrent J0. If J0 is perfect, report non-reproduction, not a treatment
win. If J1 retains the attribution error, repair-route generation is not necessary
for it under this test. If J1 improves, task separation merits a later integration
test; this does not qualify routing, advice, retry stability generally, or craft.

These six cases do not test genuinely missing turning points. Do not generalize
the all-met turning-point results into missing-turn detection.

### B. Full-scene output versus explicit edits

Reuse the two fixed, validated ordinary sources from the completed comparison:
separate entry `s19101-elara-separate-initial` attempt 2, and embedded entry
`s19201-elara-embedded-initial` attempt 1. Keep their original outcome-framed repair
tests and exact positive packets. Do not use new J0/J1 results or the rejected C1
responses as sources.

- **E0:** ordinary v61 full-scene writer with fulfillment evidence.
- **E1:** same complete context, feedback, evidence and substantive writer rules;
  replace the output representation with model-selected exact text edits against
  the immutable input draft. Preserve the ordinary non-prose output fields.

The proposed edit contract identifies the base draft version/hash and an ordered,
bounded list of exact old/new text replacements with an explicit occurrence
selector for repeated text. Preparation must freeze the representation and validator.
Resolve every selector against the original text, verify exact occurrence matches,
reject overlap and apply atomically; no fuzzy matching, silent repair or partial
application. Then validate the materialized full Scene Draft through the ordinary
writer lineage and structure checks. Semantic repair remains the critic's and
inspection's job, not the patch applicator's.

The model chooses the spans. Allow edits anywhere, including fulfilled evidence,
and allow a whole-scene replacement. Set a resource bound such as 64 operations,
not a character-change quota. Express insertion with an anchored replacement;
empty replacement is deletion. Do not preselect the faulty span, supply the desired
replacement, add a stronger minimal-edit reminder, or silently fall back to full
generation. A bad patch is a structural failure with the one permitted retry.

This tests edit representation/application as a bundle, not prompt phrasing alone.
All untouched bytes survive mechanically, but the model can still select needlessly
broad edits. That is why the outcome must include both repair and preservation.
Application of a candidate edit is local diagnostic materialization, never a write
to a canonical story or manuscript-editor feature.

Use both seeds for both sources and both arms: **eight writers and eight ordinary
post-critics**, at most **32 attempts**. Counterbalance arms. Post-critics receive
the complete materialized prose and original tests, without the edit protocol,
candidate label or fulfillment packet. No second writer revision.

### C. Craft inside fulfilled evidence

Add one explicitly synthetic, noncanonical control derived from the embedded Elara
draft: duplicate one existing embodied-decision sentence immediately beside itself,
while preserving the decision, turning point and entry overrun. The proposed target
is the bracing-against-the-jamb sentence. Freeze the exact complete draft, parent
lineage and expected facts during preparation. This is an obvious repetition
stress test, not a claim that all repeated language is poor prose.

At each seed, run **one ordinary v61 source critic**, without the route index,
special craft hint or expected-answer metadata. A source qualifies only if ordinary
validation succeeds, native facts remain correctly met, the boundary overrun is
correctly reported, and a supported actionable **independent craft** finding identifies
the repetition. It must survive ordinary projection into a separate writer test;
the edit needed for that test must overlap the critic's positive native evidence.
Check complete prose and exact resolved ranges, not just matching words.

Use each qualifying source unchanged for that seed's paired E0/E1 writers and their
ordinary post-critics. Preserve full original tests and an exact ordinary-source
fulfillment packet. The model may consolidate the repeated sentences while retaining
their fulfilled meaning; exact quotation retention is not required.

This adds at most **two source critics, four writers and four posts: 10 primary
probes / 20 attempts**. If the source critic misses the craft issue, returns wrong
native judgments, cites nonoverlapping evidence, adds an unsupported repair or fails
structurally, record the specific qualification failure and skip that dependent
pair. Do not author a replacement critique, edit a packet, supply a preferred answer,
reroll or substitute another case. The unused slots expire. The primary A/B blocks
remain independent and still run. Both craft pairs must qualify and complete before
claiming this control passed; otherwise report it as untested or failed as applicable.

### Scoring and interpretation

Freeze scoring before calls; keep the following separate:

1. Response/patch validity, provenance, source eligibility and first/final retry drift.
2. Complete native fulfillment, boundary repair, original repair-test satisfaction,
   unsupported advice and newly introduced factual defects.
3. Full-prose preservation: necessary changes, avoidable restatement, new psychological
   beats, benign wording and changes with a plausible craft benefit. Exact restoration,
   quote retention, word count and diff size are descriptive measures only.
4. Craft-control repair inside met evidence, retaining the fulfilled meaning.
5. Blind human preference on complete original/A/B passages, with private randomized
   arm order. Assistant inspection and model ratings are not human preference.

A promising writer signal requires at least **two of four primary preservation
wins, including an embedded-case win, with no preservation loss**, all four candidate
primary repairs valid and factually sound, and both candidate craft controls repaired
without factual loss or added unsupported changes. Separate-case ties are acceptable
because the control already demonstrated exact repair there. If the baseline also
makes minimal adequate repairs, report the ceiling/ties rather than replacing seeds.
Count source failures and invalid writers in the full scheduled denominator; a
smaller surviving subset cannot qualify. A failure skips its dependent post only.

These are technical signals for further investigation, not production promotion or
literary-quality gates. Do not award a preservation win to an incomplete repair;
do not call a shorter or more literal ending better prose. Record mixed judgments
and sensitivity readings. A fixed replay must validate every materialized scene
and every post-review, not just the selected edit spans.

## Proposed budget and preparation sequence

| Block | Primary probes | Maximum attempts |
| --- | ---: | ---: |
| A: six critic cases, two arms, two seeds | 24 | 48 |
| B: two fixed sources, paired writers and posts, two seeds | 16 | 32 |
| C: two ordinary craft sources, paired writers and posts | 10 | 20 |
| **Total** | **50** | **100** |

Block ceilings are nontransferable. Stage ceilings are 48 A-critic attempts,
4 craft-source attempts, 24 writers and 24 posts. Every probe has at most one
structural retry. No transport retry, semantic reroll, replacement case, extra
writer revision, adaptive prompt or full workflow call is included.

Propose the same recorded `gemma4:31b-cloud` deployment/digest, via local Ollama to
Ollama Cloud, with critic temperature 0.2, writer 0.85, top-p 0.95 and thinking off.
Each attempt retains ceilings of 24,000 input / 8,000 output tokens and 900 active
seconds. Maximum aggregate reservations: **2,400,000 input / 800,000 output tokens /
90,000 active seconds**. At the previous October 8 rates only, the estimate is
USD **0.65600**; this is not current pricing or a billed-charge guarantee. Freeze the
exact digest and settings in the later plan. No identity query was made now.

1. Reverify source seals; build the diagnostic contracts, complete craft case and
   lineage in a new local bundle. Preserve production files and previous bundles.
2. Freeze cases, static requests, all conditional writer/post/retry builders, allowed
   pair differences, schedule, scoring, source-eligibility checks and ceilings. Source
   critics are selected by the frozen schedule, never by whichever result is favorable.
3. Verify locally with fake gateways: malformed shared judgments, false-met semantic
   fixtures, invalid/ambiguous/stale/overlapping edits, Unicode boundaries, whole-scene
   edits, necessary edits inside evidence, craft-source failure and dependent skips,
   no-op writer failures, retry ceilings, cancellation, unknown outcomes and replay.
   No-op output is structurally permissible where appropriate; it must fail semantic
   repair scoring on these defective cases, not receive an application-authored fix.
4. Present the sealed plan for approval, including full unpublished prose/context
   and the destination. Only then may discovery and the single bounded execution
   begin. Reserve before each dispatch; stop on integrity, model-digest, budget,
   transport, cancellation or unknown-outcome failure. Do not transfer unused slots.
5. Inspect all attempts and complete prose, export blind pairs, reconcile usage and
   report candidate failures as well as successes. No automatic deployment or canary.

## Decisions for later story-quality work

The critic ablation intentionally lacks craft assessment and cannot replace the
production critic. A positive result would justify a separately designed integration
that retains advice and independent craft; it would not authorize deleting those
capabilities. Do not pin arbitrary first judgments to obtain structural stability.

The edit protocol must permit useful revision anywhere. A repeated action is a
narrow craft control, not a proxy for voice, characterization, tension or a finished
story. Future quality work still needs blind human comparisons under the
[accepted rubric and hard gates](../../open_hollywood_bible/product_contract_and_benchmarks.md),
the full intended Cloud corpus and a comparable single-model baseline. Constraint
adherence is only 5% of that weighted rubric, although hard gates remain binding.
Keep human evaluation here separate from the product's single required Blueprint
approval checkpoint.

No ADR, production prompt/schema/validator, canonical artifact or runtime changed.
Offline evidence helper Ruff checks and documentation/link/whitespace verification
are recorded with the diagnosis. Application tests/builds were not rerun for this
analysis-only change. **Step 19 remains IN PROGRESS; Step 20 NOT STARTED.**
