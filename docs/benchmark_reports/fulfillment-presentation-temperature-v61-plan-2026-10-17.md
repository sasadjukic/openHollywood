# Frozen critic-presentation and E1-temperature comparison

Date: 2026-10-17. **PREPARED; LIVE EXECUTION NOT AUTHORIZED OR STARTED.**

This implements the locally authorized preparation from the
[diagnosis and proposal](../handoffs/fulfillment-edit-selection-craft-diagnosis-next-experiment-2026-10-17.md).
J1 remains promising diagnostic evidence. E1 remains mechanically successful but
unqualified for preservation. Production stays at prompt **61**, graph **9**,
fulfillment policy **1**. **The full workflow canary remains ON HOLD.**

## Frozen scope and budget

| Comparison | Primary probes | Maximum calls, including structural retries |
| --- | ---: | ---: |
| A: six scenes × two critic presentations × two seeds | 24 critics | 48 |
| B: two fixed sources × two temperatures × two seeds, each with one post-review | 8 writers + 8 critics | 32 |
| **Total** | **40** | **80** |

The 48/32 blocks are nontransferable. Stage caps are 48 initial critics, 16 writer
attempts and 16 post-review attempts. There is at most one structural retry per
probe. A semantically wrong but valid response cannot trigger a retry. There are
no transport rerolls, replacement cases, replacement sources or extra revisions.
Unused budget from any previous experiment is irrelevant.

Each attempt reserves 24,000 input tokens, 8,000 output tokens and 900 active seconds.
Aggregate ceilings are **1,920,000 input tokens, 640,000 output tokens and 72,000
active seconds**. The historical October 8 rate estimate is **USD 0.52480** for the
ceiling; actual charges are unknown and this is not an enforceable billed-dollar cap.

The intended model is `gemma4:31b-cloud`, through **Ollama Cloud via the local Ollama
daemon**, with the previously captured digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
No provider discovery was performed during preparation. Future approved execution
must verify this identity before each phase; a mismatch stops the run.

## A: critic reading presentation

- **P0:** ordinary v61 sentence catalog, unchanged.
- **P1:** the exact continuous current-draft `content.prose` added alongside the
  unchanged catalog. All paragraph breaks and source wording are retained. The
  ordinary system instructions, output schema, evidence IDs, settings and validator
  are identical to P0. No repetition hint, gold label or J1 judgment is supplied.

Six complete scenes have distinct, content-bound immutable draft versions. Each
contains the full original story context, not an ending excerpt.

| Prose condition | Within boundary | Entry overrun | Purpose |
| --- | --- | --- | --- |
| Base | `elara-base-within` | `elara-base-overrun` | No inserted repetition; legitimate other craft criticism remains possible. |
| Adjacent accidental duplicate | `elara-duplicate-within` | `elara-duplicate-overrun` | The bracing action is repeated immediately with no intervening event. |
| Functional recurrence | `elara-recurrence-within` | `elara-recurrence-overrun` | The same thought recurs at a later moment with a changed role. |

The accidental duplicate repeats this exact sentence beside itself:

> She braced her free hand on the jamb to carry herself through.

The recurrence retains the earlier sentence:

> Her body belonged to her; the insistence did not.

It adds the same sentence after the later bracing action, followed by:

> This time she let the thought steady her hand instead of shaking the pull away.

The first occurrence follows resistance to the external pull; the later one is
intended to turn that thought into steadiness for her chosen approach. This rationale
is frozen before results, but **authorial intent does not certify literary success**.
A specific supported objection to the recurrence can be legitimate. Only an
unsupported demand to remove it merely because wording repeats counts as the
targeted false positive.

Within each pair, the sole prose difference is the entry clause: replace
`; she stepped across the sill and entered the building.` with `.` to obtain the
within-boundary case. The assigned turning point and decision remain fulfilled in
all six. Expected native/boundary tuples are met/met/no_overrun or met/met/overrun.
No blanket pass verdict is required when another supported craft issue exists.
Case names, expectations and construction rationales are absent from model messages.

Use seeds **19501 and 19503**, critic temperature **0.2**, top-p **0.95**, thinking
disabled. Run P0 then P1 at the first seed and P1 then P0 at the second. Both arms
see all six cases. A results cannot select or gate B's writer sources.

## B: E1 revision sampling

- **T0:** the existing E1 exact-edit request at temperature **0.85**.
- **T1:** the same request at temperature **0.2**.

Both use seeds 19501/19503, top-p 0.95 and thinking disabled. T0 precedes T1 at the
first seed; T1 precedes T0 at the second. The historical ordinary critic sources
for `elara-separate` and `elara-embedded` are pinned exactly, including raw responses,
validated receipts, full inputs, fulfillment packets and original outcome-framed
repair tests. These are the same two sources used in the completed E1 comparison.
New A cases and critiques do not replace them.

The E1 system instructions, edit schema, exact original selectors, occurrence rules,
base-version/hash checks and atomic materialization remain unchanged. The writer can
still edit fulfilled evidence or replace an entire scene when warranted. No protected
spans, diff quota or preservation-only objective is introduced.

Each valid writer output receives one ordinary **P0** post-critic at temperature 0.2.
The post-critic does not inherit the presentation treatment. A writer that fails both
structural attempts skips only its own post-review; its scheduled pair remains in
the denominator. Critic failures and semantic results cause no extra writer calls.

## Frozen scoring

For A, score structural validity, native/boundary support, independent detection,
actionable advice, occurrence references, unsupported deletion demands, other
supported craft issues and score rationales separately. Inspect raw and normalized
results. A supported minor finding can count as detection; a major severity or two
mandatory repair tests are not required. Citation coverage under the previous craft
source gate remains a separate diagnostic.

The presentation signal requires P1 to produce **4/4 valid, supported, actionable
independent findings** on accidental-duplication probes, improve on P0, produce
**zero unsupported repetition-removal demands across the eight other probes**, and
retain **12/12 supported native/boundary tuples**. Invalid or uninspectable results
cannot qualify. Perfect P0 is non-reproduction. More complaints everywhere is failure.

For B, read complete original and revised prose. Score repair, fulfilled facts,
patch validity, unnecessary scope, resolve/wait/commitment beats, physical or sensory
additions, repetition, lost purposeful preparation and lost conditional future action.
Benign grammatical glue is neutral. A plausible craft gain accompanied by a meaningful
loss is mixed. Fewer changed words alone do not establish better prose.

The provisional preservation signal requires **all four T1 factual repairs and
fulfilled facts to hold**, **at least two clear paired preservation wins including
an embedded case**, and **no losses**. Mixed/tied or incomplete pairs cannot count
as wins. Keep all four scheduled pairs visible. Record a separate sensitivity view
that treats debatable additions as neutral without rewriting primary judgments.

The private assessment template requires exact trial/response/plan bindings,
evidence and rationales; all assessments start pending. The exporter produces four
full-prose anonymous pairs when complete, with a private deterministic arm key and
an empty human-review sheet. Assistant assessments and critic ratings are not human
preferences. No human review has been completed during preparation.

## Sealing and execution discipline

Private bundle:
`data/diagnostics/fulfillment-presentation-temperature-v61-2026-10-17/`.

- `cases.json`, `writer-sources.json`, `schedule.json`, `scoring.json` and
  `assessment-template.json` freeze the inputs, order and assessment rules.
- `prepared/` contains **32 exact static request snapshots**, including messages,
  model settings, schemas, artifact versions and hashes.
- `experiment.py` freezes request construction; `execute.py` freezes dispatch,
  reservation, retry, replay and skip behavior; `score.py` freezes full-prose export.
- Eight posts depend on future writer text. Their builders and provenance rules are
  frozen now; their exact bytes are saved before dispatch. Retry bytes similarly
  depend only on the allowed structural error metadata. Unknown future output is
  not represented as already-frozen request bytes.
- `plan.json` binds the budget, code and input evidence. The preparation closure
  binds this report, verification and the tracker snapshot. Historical bundles and
  their reports remain unchanged.

**Plan SHA-256:** `025dcc34f088f29e4eed35cf1fafbae9853c8ac0e9a763d809fad72bd682aa15`.

Before any provider discovery or inference, the operator requires fresh explicit
approval bound to this plan hash, the 80-call ceiling, the full unpublished prose,
critique and diagnostic story context, the Cloud-via-local-daemon destination, and
the canary exclusion. No approval record or live output directory exists now.

Every attempt saves the exact request and durable reservation before dispatch.
Unknown previous outcomes, altered evidence, changed model identity, transport
failure, cancellation or budget failure stop further dispatch. Completed probes
replay locally; they are not silently rerun. Execution order is preflight, A critics,
then B writer/post pairs, with no intervening semantic selection.

## Local verification and limits

All 32 paired attempt checks pass: P0/P1 differ only in the prose field, and T0/T1
only in temperature, on both initial and structural-retry construction. Historical
E1 instructions remain exact. Equal materialized drafts give identical ordinary
post requests. Six draft versions and the three boundary-only prose deltas are
verified, with no context trimming or rationale leakage.

The largest static estimate is **17,282 input tokens** using the diagnostic
UTF-8-bytes/4 method. This is not exact provider tokenization; provider-reported
usage is checked against the frozen limits during any later authorized execution.
No live tokenizer or discovery call was used to improve that estimate.

The fake-provider harness exercises all 40 slots, structural recovery, terminal
failure, zero-call completed replay, independent writer execution after critic
failure, failed-writer post skips, global/block/stage/token/time ceilings, unknown
outcomes, cancellation and approval/model guards. Full-prose exports and corruption
checks are verified locally. All fixtures are explicitly noncanonical and ineligible
as model evidence or writer sources.

Verification details and final counts are recorded in the private `verification.json`.
Production lint, format and strict typing pass. Focused fulfillment/probe regressions
and private helper checks pass. Frontend checks/build are not applicable because no
client or production implementation changed.

This is one scene family at two seeds. P1 also changes redundancy, salience and input
length; it cannot isolate paragraph layout alone. T1 tests revision sampling and does
not establish a general low-temperature writing policy. There is **no craft writer
control or craft-editing qualification in this round**. Broader story-quality work
still requires useful edits inside fulfilled passages, the canonical rubric, blind
human preference, the full intended Cloud corpus and comparable single-model baseline.

**Zero live model or discovery calls. Production prompts unchanged. Step 19 IN
PROGRESS; Step 20 NOT STARTED; full workflow canary ON HOLD.**
