# Exact-edit selection and missed craft: diagnosis and next experiment

Date: 2026-10-17. **DIAGNOSIS COMPLETE; NEXT EXPERIMENT PROPOSED, NOT PREPARED OR RUN.**

Retain J1 as promising diagnostic evidence and E1 as a mechanically successful,
unqualified preservation candidate, as the user decided. The latest evidence points
to a writer choosing unnecessary changes, not a patch application failure. The craft
miss originates in the model's response, not downstream filtering. A newly inspected
detail matters: the critic reads an ordered sentence catalog with no continuous
prose field or paragraph layout. Both copies were present, but their reading context
was different from the original scene.

Recommend two independent comparisons totaling **40 primary probes / at most 80
calls**: ordinary critic presentation, and E1 revision temperature. No instruction
text or output-schema change is proposed for either comparison. New requests and
settings would be isolated diagnostic candidates, requiring preparation and a fresh
approval before any provider discovery or inference. Production remains prompt 61 /
graph 9 / fulfillment policy 1. **Canary ON HOLD; NOT STARTED.**

## Evidence and scope

The source is the [completed 45-call comparison](../benchmark_reports/fulfillment-adjudication-edits-v61-results-2026-10-17.md)
and its [frozen plan](../benchmark_reports/fulfillment-adjudication-edits-v61-plan-2026-10-17.md).
Offline inspection reverified **443 live files, 58 preparation/operator files,
128 dependency hashes**, the source report and predecessor seals. All **42 probes /
45 attempts** replayed, including rejected reviews. The source closure hash is
`628f9108c682a0c108319f61109cbc48b715a0350c2c0c0669dae2678d36255b`.

Private diagnosis evidence is under
`data/diagnostics/fulfillment-edit-selection-craft-diagnosis-2026-10-17/`.
It records actual request projections, exact patch ranges, complete prose inspection,
four minimal-patch counterfactuals, two response-copy craft fixtures and four
minor/major projection checks. All fixtures are explicitly operator-authored,
noncanonical, not model results and ineligible as writer sources. No source bundle
was edited. Gateway construction and external connections were blocked during the
checks; there were **zero model, discovery or external network calls**.

## Why E1 did not preserve the ending

### Established: accurate application did not produce selective editing

All four E1 responses matched their bases and applied on their first attempts.
The requested changes, including the unwanted embellishments, are already in the
model's `old_text`/`new_text`; the application neither invented nor expanded them.
In both separate-entry cases, E1 emitted one deletion for the forbidden paragraph
and a second edit wholly before that paragraph. Thus even an entirely separable
defect did not prevent voluntary rewriting of adequate preparatory prose.

| E1 output | What changed beyond repairing entry |
| --- | --- |
| 19401 separate | Bracing purpose becomes a hammering-heart sensation; outside wording changes. |
| 19401 embedded | The repaired composite sentence repeats bracing/intention already expressed immediately before it. |
| 19403 separate | Two preparatory sentences become weight shifting/readiness, losing the conditional future step. |
| 19403 embedded | Bracing purpose becomes cold-concrete sensation; the endpoint is expanded while the future step remains. |

Four offline minimal patches, one for each exact request/base, validate through the
same edit and ordinary draft contracts and restore the clean scene. For separate
entry, deletion alone suffices; for embedded entry, replace the offending semicolon
clause with the sentence-ending period. This establishes that the protocol allowed
the intended repair. It is not evidence that the model generated those patches or
that exact restoration is always the best prose.

The model selected the scope and replacement wording. Exact matching constrains
*where* supplied edits apply; it does not constrain the artistic or causal purpose of
their content. The protocol deliberately allowed editing fulfilled evidence and even
whole-scene replacement. Those permissions are necessary for some genuine craft
repairs; their presence does not prove they caused these particular changes.

### Plausible contributors, not established model internals

- **Ending repair is being treated as ending composition.** Both output modes change
  the same final area, and the fixed source feedback is framed around restoring the
  planned outcome/exit state. The writer retains the fact while choosing a new way to
  finish the scene. This fits the observed edits; no internal rationale was captured.
- **Revision sampling may contribute.** Both full-scene and exact-edit writers used
  temperature **0.85**, and their embellishments vary across seeds. Sampling is a
  testable contributor, not an established cause; this run contains no temperature
  comparison. There is no basis yet for a general low-temperature writing policy.
- **The post-review is not a preservation oracle.** All eight posts pass the factual
  repair and give favorable craft ratings. They do not identify the unnecessary
  adjacent changes. Passing those gates cannot certify that the repair preserved
  voice, immediacy or agency better than its alternative.

Do not collapse the differences into one restatement count. E1's bodily sensation,
physical repetition and added tactile detail differ from E0's new wait/commitment
beat. Some changes have possible artistic benefits; the two mixed pairs remain
mixed and blind human review remains pending. The recorded 0 wins / 2 losses /
2 mixed, including its sensitivity analysis, is retained unchanged.

## Why both ordinary critics missed the duplication

### The wording arrived, through a sentence catalog

`production_model_executor._critic_prompt_inputs` replaces the current draft's
`content.prose` with `content.evidence_catalog`. `_draft_evidence_catalog` splits
paragraphs into ordered excerpts and strips their surrounding whitespace. In these
actual requests there are **52 entries**, including:

- `0050`: the first bracing sentence;
- `0051`: its identical adjacent duplicate;
- `0052`: the pending-step/completed-entry composite sentence.

The exact version-scoped handles are different. Offline reconstruction confirms
that all non-whitespace prose appears in order in the catalog. Neither duplicate
was deduplicated, truncated or hidden. However, continuous paragraph layout is
absent. Earlier descriptions of “complete prose/context” mean that the wording was
included; they should not be read as claiming a continuous manuscript view in the
actual critic messages. The writer, by contrast, receives its complete prose base.

This makes presentation a concrete hypothesis: adjacent repeated actions may be
easier to notice while reading a paragraph than while selecting evidence IDs from
a long catalog. It is not yet a causal finding. The duplicate is plainly available
in both representations, and a competent review should still be able to find it.

### The omission happens before validation

Both raw responses contain only the boundary-linked issue and award prose quality
5/5. They finish normally (`stop`), at **1,267 and 1,207 output tokens** against an
8,000-token allowance; there is no output-limit explanation. Neither has a structural
retry. Both requests contain **19,572 input tokens** and a **10,997-character system
message** heavily concerned with assignment semantics, conditions, routing and POV.
Those sizes describe this request, not a proven overload threshold.

The critic correctly finds the nearby entry overrun and cites the first bracing
sentence as positive evidence. That combination is consistent with assignment-first
attention or treating the ending as one boundary problem. It does not tell us whether
the duplicate went unnoticed, was noticed but considered trivial, or was omitted
while deciding how to report independent craft. No hidden reasoning is inferred.

The writer's fulfillment packet cannot explain the miss directly: it is **absent
from both critic requests**. Positive evidence is selected by the critic itself.
Nor is the failure a downstream deduplication rule: copies of both raw responses
accept an added, correctly referenced independent craft finding through the ordinary
validator, without changing native checks. It remains a separate normalized issue.
These copies test capability of the application, not capability of the model.

### The craft-control gate demanded more than detection

The original gate combined three different requirements:

1. A supported independent craft finding.
2. Positive native evidence covering both repeated copies, so removing either copy
   necessarily edits a positively cited passage.
3. Two ordinary mandatory repair tests: boundary and craft.

Both real reviews fail the first and also lack the second. A single citation is
reasonable evidence of a fulfilled bracing action; requiring both copies was an
instrumentation choice, not a standard for a good critic. The 1–3-reference bound
does not make both-copy coverage impossible, but the model used its three outcome
references for bridge reasoning, strap preparation and one bracing sentence.

There is a further limitation: under
[ADR 0013](../adr/0013-revision-acceptance-tests.md), only blocking issues and major
issues on a revise verdict produce mandatory repair tests. Offline copies with a
**minor** duplication finding retain two normalized issues but project **one** test;
changing only fixture severity to **major** projects **two**. Neither fixture fixes
the missing both-copy native coverage. This is a projection check, not an endorsement
of major severity for one duplicated sentence.

Therefore a future critic could correctly flag the repetition as minor and still
fail that particular control. Do not inflate severity, force redundant citations or
manufacture a critique just to obtain eligible writer runs. The actual miss remains
real—there was no craft finding at all—but the unexecuted writer control measures
neither craft-editing ability nor willingness to improve a fulfilled passage.

## Proposed next comparison A: ordinary critic reading presentation

Use the same model/digest, full assignment/context, ordinary v61 system instructions,
output schema, evidence IDs, validation, rubric and temperature 0.2. Compare:

- **P0:** the current sentence-catalog presentation, unchanged.
- **P1:** retain the exact continuous `content.prose` **alongside the unchanged
  catalog** on the current draft. This is the only content-rendering difference.
  The prose must equal the exact immutable source bytes; citation output still uses
  the same IDs. No special repetition hint, gold answer, repair span or J1 output.

Use a six-case factorial matrix: **three prose conditions × boundary absent/present**.
The prose conditions are the base scene without the accidental duplicate, the
adjacent duplicate, and a deliberately functional recurrence with narrative work at
distinct moments. Each case is a complete scene, with exact new versions where text
changes. Only the planned entry clause distinguishes each boundary pair. Prepare the
functional control's exact text and rationale before freezing; authorial intention
alone must not certify its quality. Do not label case families in model messages.

The two clean-of-duplication conditions are negative controls for indiscriminate
editing. They are not assertions that the scenes have no other possible craft flaws.
An evidenced criticism of the functional recurrence may be legitimate; a demand to
delete it merely because words repeat is the false positive being tested.

Run both arms on all six cases at seeds **19501 and 19503**, reversing arm order at
the second seed: **24 primary critic probes, maximum 48 attempts**. No semantic
result selects cases, triggers a retry or becomes a writer source in comparison B.

Pre-register these separate axes:

- Detection and supported, actionable independent advice on the four accidental-
  duplication probes per arm, regardless of justified minor versus major severity.
- Raw versus validated findings, exact occurrence citations, native/boundary accuracy,
  unnecessary edits on negative controls and advice support. Do not merge a failure
  of the former craft-source gate into a detection failure.
- Scores and full-prose rationales as diagnostics, not human literary judgments.

A promising presentation signal requires **4/4 valid supported duplication findings
for P1 and improvement over P0**, no unsupported repetition-removal demands on the
eight other probes, and **12/12 supported native/boundary tuples**. Supported other
craft concerns remain separately visible. Perfect P0 is non-reproduction. A result
that merely adds complaints everywhere does not qualify.

Interpret the factorial pattern cautiously. Detection on duplication-only but not
duplication-plus-overrun supports a boundary-competition explanation. Improvement
from P1 with ordinary policy fixed supports a presentation effect. P1 also increases
input length and repeats the same text in two views, so this does not isolate paragraph
layout from redundancy/salience. If both arms still miss it, task/reporting burden
remains a hypothesis for a later, separately approved ablation.

## Proposed next comparison B: E1 revision sampling

Keep E1's exact edit schema, instructions, full context, ordinary historical source
reviews, original outcome-framed tests and fulfillment packets unchanged. Retain the
same two independent fixed sources used in the completed run. Compare only:

- **T0:** E1 with writer temperature **0.85**.
- **T1:** E1 with writer temperature **0.2**.

Use seeds 19501/19503, top-p 0.95 and thinking disabled in both arms. Reverse arm
order at the second seed. Both sources at both seeds yield **eight writers**, each
followed by **one ordinary P0 post-critic** if structurally valid: **16 primary probes,
maximum 32 attempts**. Post settings stay fixed at critic temperature 0.2. Comparison
A outputs cannot replace these fixed writer sources or change their tests.

Score repair, fulfilled facts, patch validity, edit selection, new resolve/physical/
sensory beats, avoidable repetition and plausible craft tradeoffs separately. Keep
complete scenes and anonymous paired human-review exports. A provisional preservation
signal requires all four T1 factual repairs, at least two clear paired preservation
wins including an embedded case, and no losses. Invalid results remain in scheduled
denominators. Temperature does not excuse missing repairs or reward no-op output.

This tests whether generation settings contribute to the observed embellishment
with edit representation and feedback held fixed. Improvement would not prove the
model's motive, establish that lower temperature is better for initial drafting,
or qualify it for creative revision. If both arms rewrite adequate endings similarly,
the edit-selection objective and interpretation of the repair remain unresolved.

**No craft writer control is claimed in this proposed round.** Its purpose is to
separate presentation/detection from writer sampling without making another primary
comparison depend on the fragile former source gate. Editing useful craft inside
fulfilled evidence remains an explicit later qualification requirement. A subsequent
control should distinguish optional/minor improvements from mandatory repairs and
measure actual overlap of the necessary edit with positive evidence. It must not
achieve coverage by raising severity or locking prose. That later control needs its
own frozen design and approval; this proposal does not authorize it.

## Budget, preparation and decisions

| Block | Primary probes | Maximum attempts |
| --- | ---: | ---: |
| A: 6 cases × 2 presentations × 2 seeds | 24 | 48 |
| B: 2 sources × 2 temperatures × 2 seeds, plus posts | 16 | 32 |
| **Total** | **40** | **80** |

Propose the existing `gemma4:31b-cloud` digest and local-daemon/Ollama Cloud route;
no discovery has been performed for this proposal. One structural retry per probe,
no semantic or transport rerolls, replacements or extra writer revision. Limits are
nontransferable between blocks. Reserve at most 24,000 input / 8,000 output tokens /
900 active seconds per attempt: **1,920,000 input / 640,000 output / 72,000 active
seconds** total. At the old October 8 rates only, the ceiling estimate is **USD 0.52480**;
actual charges are unknown. The previous run's unused allowance is not reused.

This remains a two-seed diagnosis in one scene family, not a population estimate or
evidence of general story-quality improvement. Both comparisons need broader and
human evaluation before any production recommendation.

If preparation is authorized, first construct and inspect the six full cases and
their labels; freeze requests, versions, scoring and budgets; verify that the added
prose fits without trimming context; prove paired deltas are only prose rendering
or writer temperature; test structural retries, invalid-writer post skips, provenance
and ceilings; then show the sealed plan before live approval. Actual dependent post
and retry bytes must be saved before dispatch. Identity, integrity, transport,
cancellation, unknown-outcome or budget failure stops execution.

This diagnosis creates no next-experiment prompts, schemas, case/request bundle,
approval record or runnable live plan. It does not change any accepted ADR or production
behavior. The existing blind human review remains pending. Later story-quality work
continues to use the [canonical rubric and hard gates](../../open_hollywood_bible/product_contract_and_benchmarks.md),
the full intended Cloud corpus and comparable single-model baseline. Continuity and
constraint adherence remain only 5% of the rubric; fewer edits or more detected
defects are not substitutes for better stories.

**J1 retained as promising diagnostic evidence. E1 retained as mechanically successful
but unqualified for preservation. Step 19 IN PROGRESS; Step 20 NOT STARTED; canary
ON HOLD.**
