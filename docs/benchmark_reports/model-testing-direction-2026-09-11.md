# Testing direction: move from E4B tuning to 31B production evaluation

Decision date: **2026-09-11**. Status: accepted testing direction, not production
qualification. Step 19 remains **IN PROGRESS**.

## Decision

Open Hollywood's designated testing model is now `gemma4:31b`, evaluated through
Ollama Cloud as `gemma4:31b-cloud`. We are ending `gemma4:e4b` as the model
driving active development tests. Local, Hybrid and Cloud remain first-class
product options; no UI option or provider-neutral capability is being removed.

The priority is to establish whether 31B can complete the short-fiction
production workflow, what failures it recovers from, what interventions it
requires, and how humans judge the resulting stories. Further small-model
accommodation and narrow proofreading tuning are deferred. This decision does
not assert that every small model is unsuitable, or that 31B is already reliable
enough for production.

## Why pre-production success was not enough

E4B was useful for premise development, structured planning and Blueprint
creation. One earlier Local qualification/staging run reached approval on
**12/12** prompts. That was not a universal 100% success rate: the frozen
August 1 campaign reached approval on **11/12 Local Blueprints**, with OH-V01-006
failing integration after bounded repair. Cloud and Hybrid reached **12/12 each**.
Approval-stage success is not autonomous production completion.
See the chronological [Step 19 record](../../open_hollywood_bible/step_by_step_implementation.md).

Production adds a more demanding chain: generate a scene, interpret its assigned
POV and outcome, distinguish a real contradiction from an inference or preference,
prescribe a bounded revision, reassess the new draft, and update canonical story
memory without rewriting accepted history. A valid response at each boundary is
necessary, but its judgment can still be wrong. Errors can accumulate or recur
across this chain even when planning artifacts look convincing.

| Matched canary | E4B Local completions | 31B Cloud completions |
| --- | ---: | ---: |
| v23 / graph 3 | 2/5 | 4/4 |
| v24 / graph 4 | 0/5 | 4/4 |
| v25 / graph 5 | 2/5 | 4/4 |
| v26 / graph 6 | 0/5 | 3/4 |

The Local denominator excludes only the exact inherited OH-V01-006 Blueprint
failure. These are repeated canaries on selected cases, not independent model
benchmarks. Local and Cloud use different Blueprint artifacts and deployments.
The v23 Local pause coincided with an operator-confirmed dual-boot clock
correction; it is not attributed to model reasoning or an Open Hollywood defect.

## What the failures taught us

E4B sometimes completed short stories, but repeatedly encountered production
bottlenecks: unsupported continuity demands, recurring allegations after repair,
overbroad scene rewrites, and critics that passed an actual viewpoint or
assignment breach. Exact citations did not guarantee that the cited assertion
supported the criticism.

Focused tests exposed a reasoning/application weakness independently of full
workflow length:

- After a diagnostic schema incompatibility was corrected, a six-condition
  E4B POV test produced **6/6 valid responses but only 2/6 expected judgments**:
  three missed violations and one false accusation.
- In a subsequent matched frozen comparison, E4B produced **6/18 valid outputs**,
  **9/18 correct coarse decisions**, and **4/18 both valid and target-correct
  outputs**. 31B achieved **18/18** on all three measures.
- E4B missed direct narration of Cora's private feeling in the full/focused
  scene conditions, while wrongly rejecting explicitly attributed inference.
  Simply making the critic stricter would risk more false accusations.

These are supplied-context POV/logic tests, not a general intelligence score.
Quantization, inference placement and model size differ between the deployments;
the comparison does not isolate parameter count as the cause.

Not every production failure was a model failure. v24's keyword-based escalation
and Bible-output boundary, v25's handling of already-resolved threads, and v26's
evidence interface exposed application defects or contract friction. Those
deserved general fixes. We will continue fixing genuine application problems,
but will not keep adding model-specific exceptions to rescue E4B.

Longer stories would add continuity and coordination demands. The short-story
results give us reason to defer that expansion, not proof that E4B has failed a
novel-length benchmark we never ran.

## Cloud-first evaluation policy

Test 31B only through Cloud for now. Keep all three UI options, existing
runtime gates and immutable evidence; do not silently reroute Local, fall back to
E4B, or adopt the experimental critic instructions.

The next assessment must distinguish clean completions, recovered failures,
terminal failures and human intervention, then evaluate revision preservation,
usage and actual story quality. Closing the Cloud-first Step 19 phase requires
the full frozen 12-prompt corpus, a direct-model baseline, repeatability, and
the existing human-quality, hard-gate, preference and budget criteria. Local and
Hybrid qualification remain deferred until that phase is complete; no unfinished
historical all-profile campaign should be marked complete.

The operator reports roughly **4,000 31B requests per two weeks** as a planning
assumption, not an independently verified provider quota or spend cap. Check
availability before batches and record actual usage.

The [canonical evaluation policy](../../open_hollywood_bible/product_contract_and_benchmarks.md)
records the changed sequence. The [evaluation register](gemma4-31b-evaluation-register-2026-09-11.md)
and [deferred issue draft](../issue_drafts/gemma4-31b-critic-repair-follow-up.md)
preserve known weaknesses. Further proofreading microtests are not prerequisites
to the next Cloud production assessment; this does not justify suppressing
failures or accepting a defective final story.

Sources: [v23 diagnostics](step-19-local-cloud-v23-canary-2026-09-04.md),
[v24 diagnostics](step-19-local-cloud-v24-canary-2026-09-05.md),
[v25 diagnostics](step-19-local-cloud-v25-canary-2026-09-07.md),
[v26 diagnostics](step-19-local-cloud-v26-canary-2026-09-08.md),
and the source receipts in the evaluation register.
