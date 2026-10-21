# Gemma and DeepSeek reviewer diagnostic results

Date: 2026-10-20. Status: **COMPLETED AND INSPECTED — 48/48 CALLS**.

**Gemma with C1 is promising diagnostic evidence under the frozen decision rule.**
Its valid reports increased from 5/12 to 12/12, and its usable supported assessments
increased from 4/12 to 7/12. DeepSeek did not benefit from this interface: valid
reports fell from 10/12 to 7/12 and usable assessments from 6/12 to 5/12.
Neither deployment is qualified as a production editorial gate or a measure of
human story preference. Production prompts remain unchanged; the full workflow
canary remains **ON HOLD**.

The [frozen plan](../handoffs/reviewer-gemma-deepseek-frozen-plan-2026-10-20.md)
remains an immutable preparation-time record. The user subsequently approved the
48-call execution and transmission of full unpublished prose/context to Ollama
Cloud through the local daemon. The approval and execution bind preparation seal
`40554c152746bbc9a6e718473a0e146beeec6221d15100455d548fb131fc7258`.
No prior budget was reused.

## Scope and execution

The matrix used twelve original/revision pairs, two interfaces and two deployments:
`gemma4:31b-cloud` and `deepseek-v4.1-flash:cloud`. There were four existing Elara
controls, four constructed assignment/endpoint failures, and four permissible
variation or craft controls. The twelve pairs derive from **three scene families**.
Only r04 is a saved actual writer revision; the other pairs are no-op or constructed
controls using saved prose. This was a reviewer diagnostic, with no writer calls.

V2 required version IDs, catalog references and exact quotations. C1 accepted short
catalog references and let the application bind versions and quotes. System judgment
instructions and complete source messages were identical across interfaces; only
the diagnostic delivery contract differed. Both models used temperature 0.2,
top-p 0.95, seed 20261020 and explicit `think: false`. This comparison does not
describe DeepSeek with its advertised high-thinking default.

All 48 reserved cells were dispatched exactly once, captured and replayed. There
were **34 valid reports, 14 invalid reports, no truncated outputs, no retries and no
terminal stop**. Every response finished with `stop`. Model metadata checks,
request seals, usage bounds and the prohibition on unexpected thinking held.

## Frozen primary results

Each entry below has a denominator of **12 scheduled cells**, including invalid
delivery. A usable assessment requires valid delivery, every frozen label correct,
and supported textual claims after coordinator inspection.

| Deployment and interface | Valid delivery | All frozen labels correct | Usable supported |
| --- | ---: | ---: | ---: |
| Gemma V2 | 5/12 | 4/12 | **4/12** |
| Gemma C1 | 12/12 | 7/12 | **7/12** |
| DeepSeek V2 | 10/12 | 6/12 | **6/12** |
| DeepSeek C1 | 7/12 | 6/12 | **5/12** |

C1 adds three usable Gemma cases: r08, r09 and r12. It loses no previously usable
Gemma case, has no paired loss in fact or mandatory-failure accuracy, and introduces
no unsupported mandatory flag on permissible controls. It therefore meets the
frozen **promising diagnostic** criterion. Seven additional reports became valid;
four of those recoveries, r05, r07, r10 and r11, still fail scoring.

DeepSeek/C1 gains usable r01 and r09, but loses usable r04 and r12 to citation-count
failures and r06 to an unsupported comparative explanation. It fails the frozen
improvement criterion. Both models total 11/24 usable assessments across interfaces;
there is no overall model winner on this small matrix.

### Dimensions kept separate

Counts below require valid delivery. “Facts” means both required fact labels are
correct for that case, rather than the number of individual facts. Invalid answers
are missing usable assessments, not evidence that their underlying labels were wrong.

| Dimension | Gemma V2 | Gemma C1 | DeepSeek V2 | DeepSeek C1 |
| --- | ---: | ---: | ---: | ---: |
| Requested task correctly classified | 5/12 | 12/12 | 10/12 | 7/12 |
| Required facts correctly classified | 5/12 | 12/12 | 9/12 | 7/12 |
| Mandatory failure correctly classified | 5/12 | 12/12 | 10/12 | 7/12 |
| All necessity labels match frozen expectations | 4/12 | 7/12 | 8/12 | 6/12 |
| Supported task/fact/mandatory explanations | 5/12 | 12/12 | 9/12 | 7/12 |
| Supported necessity explanations | 5/12 | 10/12 | 9/12 | 7/12 |
| Supported comparative explanations | 5/12 | 12/12 | 8/12 | 6/12 |
| No-op comparative invariance, three cases | 2/3 | 3/3 | 2/3 | 2/3 |

Necessity explanations and necessity labels differ: a reviewer may accurately
describe a requested optional edit while selecting a label that the frozen key
rejects. Gemma/C1 also has one unresolved necessity interpretation in r05; it is
excluded from supported counts and from usable success. No new human adjudication
or answer-key change was used to resolve that ambiguity.

### Results by case group

Every cell shows **valid delivery / usable supported**, each out of four cases.

| Group | Gemma V2 | Gemma C1 | DeepSeek V2 | DeepSeek C1 |
| --- | --- | --- | --- | --- |
| Existing controls r01–r04 | 4/4 · 3/4 | 4/4 · 3/4 | 4/4 · 3/4 | 3/4 · 3/4 |
| Clear failures r05–r08 | 1/4 · 1/4 | 4/4 · 2/4 | 3/4 · 1/4 | 1/4 · 0/4 |
| Permissible controls r09–r12 | 0/4 · 0/4 | 4/4 · 2/4 | 3/4 · 2/4 | 3/4 · 2/4 |

The [48-cell table](../../data/diagnostics/reviewer-crossover-v61-2026-10-20-live/inspection/cell-results.md)
records every failure, inspection ID and explanation. No invalid answer is salvaged
into the primary results.

## Delivery failures

| Arm | First rejection reasons | Interpretation |
| --- | --- | --- |
| Gemma V2, seven invalid | Three citation-binding mismatches; three missing craft citations; one missing task citation | Quote copying and empty evidence remain substantial burdens. The last case also contains other defects. |
| Gemma C1, zero invalid | None | Application-owned binding plus this delivery contract removed observed structural failures in this draw. |
| DeepSeek V2, two invalid | One citation-binding mismatch; one duplicate `purpose_checks` key | The duplicate values were both empty, but the frozen strict parser correctly rejected the object. |
| DeepSeek C1, five invalid | Evidence arrays exceed the six-reference maximum | The answers supplied seven or eight references in one or more fields. Short references made fuller evidence lists cheap to emit, but the bound remained six. |

DeepSeek/C1's oversized arrays occurred in r04, r05, r07, r08 and r12. These were
complete responses with known references, not truncation or an inability to produce
JSON. Reducing evidence-copying work exposed a different contract problem. The
observed arrays explain rejection; they do not establish why the model ignored
the bound. No references were dropped and no array limit was relaxed after the run.

Some V2 mismatches combine the correct story passage with the wrong catalog index.
For example, a truce quotation is attached to R054 even though the explicit
concession is in R053. Catalog segmentation also splits the following speech
across entries. C1 prevents quote/ref disagreement mechanically, but cannot ensure
that the selected locator is the strongest support for the claim. Weak contextual
locators are recorded in the inspection notes.

Separately inspected raw answers had correct task and mandatory-failure labels in
all 48 cells and correct paired fact labels in 46/48. Both fact-label misses were
DeepSeek/r08, once valid and once invalid. These are **raw observations only**:
they do not validate reports or establish that all explanations are correct.
The [invalid-output audit](../../data/diagnostics/reviewer-crossover-v61-2026-10-20-live/inspection/invalid-raw-observations.json)
preserves all detected citation issues, duplicate keys and semantic observations.

## Remaining judgment failures and scoring sensitivities

**A later event was treated as erasing an earlier event.** Both DeepSeek interfaces
said the r08 departure loses or dissolves the truce. The departure violates the
locked-room endpoint, but the explicit agreement still occurred; leaving together
does not establish revoked cooperation. C1 did not recover this distinction in the
invalid raw answer. Gemma retained the truce and identified the separate endpoint
violation.

**An existing flaw became a new comparative loss.** DeepSeek/V2 r01 correctly noticed
the unrepaired duplicate and called the overall comparison a tie, yet assigned
`naturalness.effect = loss` to identical prose. Its own explanation says the defect
is unchanged. Nine of ten valid no-op reports were invariant; the two remaining
no-op cells were invalid. This is a contradictory comparative label, not evidence
that a reader was harmed by repetition.

**Correct boundary criticism acquired an unsupported chronology claim.**
DeepSeek/C1 r06 correctly found the forbidden handwriting match and retained the
earlier decision. It then argued that the preceding reflection was already
“after the comparison,” making the added completion out of order. The original
only places the journal beside the card to check it; it does not establish a
completed comparison. This factual premise is unsupported even though the real
boundary failure and a preference for a less abrupt ending remain defensible.
This cell passed every frozen label and failed semantic inspection.

**The necessity taxonomy conflates different questions.** Six valid reports label
a requested optional cleanup `optional_craft` where the key expects `direct_repair`:
Gemma r04 in both arms, Gemma/C1 r10, and r11 in Gemma/C1 and both DeepSeek arms.
Their prose generally recognizes that the request was addressed and does not
invent a mandatory production obligation. These remain frozen failures, but should
not all be described as justifying an unnecessary rewrite. The task's optional
status and the edit's direct relationship to that task are separate dimensions.

DeepSeek r05 is more concerning: both raw interfaces describe deletion of the
required future date as destructive, yet label the deletion itself `direct_repair`.
Gemma instead calls the core deletion unsupported but labels its later callback
adjustments `required_adjacent`. Those callback changes are conditional consistency
work after a bad edit. The system permits concrete grammatical dependencies, while
the frozen key allows only `unsupported` for every fragment. The primary score is
unchanged; the report does not infer approval of the whole rewrite from recognition
of a local dependency.

**Token fragments encourage misleading explanations.** The r07 ending replacement
is split into eleven changed units. Gemma/C1 calls the isolated `returning.` → `room`
fragment a simplified room description, although the old phrase describes the
pragmatist returning. Both models identify the lost truce, but fragments of a
sentence do not reliably represent independent editorial decisions. Treating
`can't` → `cannot` as a local optional register change is also plausible even
though the frozen whole-edit key rejects it.

The pre-inspection method noted another ambiguity: r09's `a` → `an` is grammatical
support for `study` → `exercise`. DeepSeek/V2 calls it `required_adjacent`, which the
frozen key excludes. That cell is independently invalid because of its duplicate
JSON key. No score is changed by this sensitivity.

There are also overbroad explanations, such as DeepSeek/V2 r11 extending Elias's
avoidance of abstraction into a claim that the narration avoids that register.
The source narration contains abstract descriptions. These are reasons to inspect
the explanation's factual basis; they do not dictate whether a reader should prefer
the shorter sentence.

## What this means for story quality and the next decision

Retain **Gemma/C1 as a promising diagnostic interface candidate**, with the observed
7/12 usable limit and unresolved necessity scoring. Retain DeepSeek's additional
observations as diagnostic evidence, without promoting either of its interfaces
or treating agreement between models as independent human validation.

The tests show meaningful strengths: both models notice the deliberately missing
date and truce, identify endpoint overruns, preserve many fulfilled facts, and often
allow ties for unchanged or near-equivalent prose. The remaining problem includes
delivery design and category interpretation as well as faulty narrative reasoning.
More preservation reminders alone would not address all three.

Before another live experiment, prepare these changes for a separate proposal:

1. Audit the interface locally. Keep application-owned identities and exact quote
   expansion. Separate a request's mandatory/optional status from whether the edit
   addresses it; distinguish conditional grammatical cleanup from authorization of
   the larger edit. Use sentence or clause groups for explanation while preserving
   exact token differences in the machine appendix.
2. Decide explicitly how evidence cardinality should work. Keep a bounded contract,
   but test its usability rather than silently truncating returned references. The
   five captured DeepSeek outputs are useful offline fixtures; any altered-contract
   replay would be sensitivity analysis, not new live success.
3. If another live reviewer comparison is warranted, freeze a small repeat across
   the known failure classes, with unchanged controls and fresh scene families.
   Test event retention separately from final-state compliance, and inspect whether
   explanations invent facts while reaching the right verdict. Repetition and
   presentation-order controls would address uncertainties this single-draw pilot
   cannot estimate.

No new prompts, cases, budget or inference are authorized by these recommendations.
The proposed writer-selection diagnostic remains unprepared. Whole-story work
should continue to use overall feel/emotion, flow, character and story-breaking
concerns, with mechanics prepared automatically. The user's earlier ties remain
valid observations about those samples. Local craft preferences here are not
measured quality gains, and exact preservation is not the artistic objective.

## Usage and verification

| Model | Calls | Input tokens | Output tokens | Recorded-rate estimate |
| --- | ---: | ---: | ---: | ---: |
| Gemma | 24 | 371,554 | 30,099 | $0.06405716 |
| DeepSeek | 24 | 343,668 | 31,584 | $0.14100120 |
| Total | **48** | **715,222** | **61,683** | **$0.20505836** |

The estimate applies the rates frozen in the plan, with DeepSeek peak rates and no
cache discount. Actual provider charges remain unknown. Maximum observed input was
19,103 tokens, output 3,309 tokens and active generation time 26.19 seconds per call;
total active generation time was 323.40 seconds. All were within frozen limits.

C1 used 384,605 input and 21,579 output tokens across models, versus V2's 330,617 input
and 40,104 output. The short-answer format reduced output but did not reduce input:
its schema repeats catalog-reference allowlists. Do not equate a compact answer
interface with a compact request.

The sealed preparation's 70 local tests remain the pre-run harness evidence.
Post-run verification replayed all 48 cells without inference, checked the original
seal and source/runtime hashes, and checked the inspection coverage and aggregation.
The two new private analysis scripts pass Ruff lint/format and strict mypy.
Production application/frontend code was not changed; no additional application
test suite or frontend build was needed for evidence and documentation.

Inspection used shuffled normalized assessments with model/interface labels hidden
before consulting the key. It was performed by the coordinating assistant, familiar
with the cases and study design, not an independent blinded human. Cited fragments
were read with complete source context; plausible artistic differences were allowed,
while invented events and contradictory comparative labels were rejected. Frozen
labels were never revised. One uncertain necessity interpretation remains explicitly
unresolved and cannot count as success.

Evidence:

- [Approval](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/approval.json)
- [Aggregate and every-cell results](../../data/diagnostics/reviewer-crossover-v61-2026-10-20-live/summary.json)
- [Completed source inspection](../../data/diagnostics/reviewer-crossover-v61-2026-10-20-live/inspection/assessments.json)
- [Inspection method recorded before reading assessments](../../data/diagnostics/reviewer-crossover-v61-2026-10-20-live/inspection-method.md)
- [Frozen source casebook](../../data/diagnostics/reviewer-crossover-v61-2026-10-20/casebook.md)
- [Execution closure and integrity manifest](../../data/diagnostics/reviewer-crossover-v61-2026-10-20-live/closure.json)

Full prose and raw evidence remain in ignored local storage. Production prompt
**61**, graph **9**, fulfillment policy **1**, runtime routing, schemas and human
checkpoints remain unchanged. **Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
