# Critic/writer investigation: evidence and production direction

Evidence reviewed through **2026-11-02**, including the stopped MA/quote-witness
comparison and the [local workload/headroom audit](reviewer-workload-headroom-audit-2026-11-02.md).
This synthesis adds **no live calls** and changes no historical scores or production
prompts. Full workflow canary **ON HOLD**.

The investigation has produced useful engineering improvements and several real,
bounded model gains. It has **not yet qualified an autonomous critic-to-writer
repair loop that improves the reading experience**. The strongest next production
step is to give the application explicit ownership of assessment work, provenance
and completeness, while keeping factual support, edit necessity and literary
judgment separate. We should then test whether that boundary improves completed
reviews and actual repairs, rather than continue treating every better diagnostic
score as evidence of better stories.

## What we have tried and what it showed

The experiments changed tasks, models, modes, sources and scoring contracts over
time. Their calls are not one homogeneous benchmark. Reused families, repeated
orders, retries, component judgments and local fixture replays are not independent
story samples. The table summarizes the major lines of investigation, with the
original reports retaining exact denominators and limitations.

| Line of work | Observed result | What it does and does not establish |
| --- | --- | --- |
| Fulfillment evidence and ordinary critic handoff | Early repair examples improved, but the ordinary-critic comparison had only one of four eligible cases. Evidence sometimes added restatement; a later replication avoided it in all three evidence revisions while all three controls added it, yet all six rewrote the ending. | Preserving successful obligations is useful context, but the critic's eligibility and the writer's edit choices remain separate problems. See the [early retrospective](critic-writer-retrospective-and-next-tests-2026-10-19.md). |
| Narrow adjudication, boundary framing and repair prompts | J1's narrow adjudication achieved 12/12 versus 8/12 for its ordinary comparator. Boundary framing produced zero wins, three losses and one tie. Minimum-edit reminders and removing stale advice did not reliably prevent unrelated changes. | A simpler diagnostic can succeed without qualifying a production critic. More explicit boundary wording can still encourage an ending rewrite. [Retrospective](critic-writer-retrospective-and-next-tests-2026-10-19.md). |
| Exact edits, lower temperature and per-edit purposes | Exact patch application worked mechanically; edit selection still expanded beyond the repair. Lower temperature showed no clear preservation benefit. Only four of eight inspected purpose claims were fully supported; expanded retry feedback added no recovery beyond the control. | Constraining how an edit is applied does not establish whether it should be made. A fluent purpose can justify an unnecessary change. [Retrospective](critic-writer-retrospective-and-next-tests-2026-10-19.md). |
| Duplication and combined critic tasks | Continuous prose improved raw duplication noticing from 0/4 to 4/4, but only 2/4 reports were usable. Restricted correction improved validity from 4/8 to 6/8 without eliminating wrong task scope. Later raw duplication explanations still failed parent binding. | Noticing, valid delivery and correct routing are distinct. Genuine repetition and accidental duplication need different controls. [Retrospective](critic-writer-retrospective-and-next-tests-2026-10-19.md), [output-contract results](../benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md). |
| Schema, identity and response layout | V2 delivered 15/18 valid comparative reports versus V0's 0/18; V3's fingerprinted handles delivered 1/18. Later C2 delivered 0/32 valid Gemma reports, all with a duplicate key, versus 32/32 valid DeepSeek reports, of which 22 were usable. | Interface details materially affect delivery. Shorter output or valid JSON is not necessarily more useful judgment. [Output-contract results](../benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md), [C2 repeat](../benchmark_reports/reviewer-interface-repeat-v61-results-2026-10-21.md). |
| Gemma versus DeepSeek | In the first matched comparison, each model produced 11/24 usable reports overall, with different strengths across V2/C1. Later C2 strongly favored DeepSeek delivery. | Evidence for model/interface interactions, not a universal ranking or a claim that one model cannot write. [Initial comparison](../benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md). |
| Requirement ownership, whole claims, components and evidence policy | We separated event fulfillment from later overrun, mandatory scope from optional criticism, parts from their relation, and compatible transitions from contradictions. Component and label changes still left unsupported whole-claim explanations and delivery failures. | Some failures belonged to our task definitions and interfaces; clearer primitives alone did not guarantee correct relations. [Ownership results](../benchmark_reports/reviewer-ownership-v61-results-2026-10-23.md), [whole-claim audit](reviewer-whole-claim-audit-2026-10-24.md), [aggregation audit](reviewer-aggregation-cardinality-audit-2026-10-25.md). |
| Thinking mode | High thinking recovered all eight contemporary target relation failures across four families/both orders. Usable whole claims rose from 48/72 to 62/72. Median paired latency and generated-token ratios were 3.83× and 4.81×. | Strong evidence for selective use on this task; uncertainty and protected explanation losses still blocked qualification. It is not evidence to enable thinking for every role. [Thinking results](../benchmark_reports/reviewer-thinking-mode-v61-results-2026-10-26.md). |
| Explicit source obligations and provenance | PO achieved 16/16 grounded targets versus BS's 11/16, then 20/20 versus 17/20 in generalization. The primitive obligations were supplied and inspected. | A meaningful gain that transferred to fresh settings, but automatic extraction of those obligations from arbitrary ordinary criticism was not tested by those comparisons. [Source obligations](../benchmark_reports/reviewer-source-obligations-v61-results-2026-10-28.md), [generalization](../benchmark_reports/reviewer-provenance-v61-results-2026-10-29.md). |
| Exact copying versus semantic retention | PO/EX both achieved 112/112 semantic component judgments and 48/48 whole claims. EX gave no demonstrated precision gain; literal comparisons moved to application-rendered evidence. | The model can preserve meaning through paraphrase in these controls. Exact string identity is a mechanical question; lack of identity is not automatically an assignment failure. [PO/EX results](../benchmark_reports/reviewer-exactness-v61-results-2026-10-30.md). |
| Admission, selection and staged assessment | Combined selection/assessment hit empty-final length failures. Selection-only delivered 8/8 valid with all 24 primary propositions retained, plus extras. Later broader MA assessment grounded 30/41 judgments, versus 24/24 for VA's supplied units. | Splitting tasks can preserve admission, but selection is not support or efficiency. The differing judgment sets do not isolate a pure workload effect. [SA/SO](../benchmark_reports/reviewer-selection-only-v61-results-2026-11-01.md), [VA/MA](../benchmark_reports/reviewer-selected-assessment-v61-results-2026-11-01.md). |
| Paragraph excerpts, repeatability and quote witnesses | MA controls first recovered all earlier failures, then identical-wire repetition yielded 60/72 grounded judgments with six citation and six semantic failures. WB located 23/23 witnesses and recovered one paired citation, but the latest comparison stopped after four calls at MA's length failure. | A successful rerun is not stable reliability; correct location is not entailment. WB remains incomplete evidence. [MA/PE](../benchmark_reports/reviewer-paragraph-excerpts-v61-results-2026-11-01.md), [repeatability](../benchmark_reports/reviewer-baseline-repeatability-v61-results-2026-11-02.md), [MA/WB](../benchmark_reports/reviewer-quote-witness-v61-results-2026-11-02.md). |

## What we learned about the application

We gave some generative interfaces responsibilities that the application can own
more reliably: artifact identity, exact quotation location, literal comparison,
required-field validation, evidence limits, budget accounting and completion.
The evidence supports moving these operations into deterministic code. It does
not support replacing semantic judgment with string matching.

Several concrete improvements already exist:

- The [durable fulfillment handoff](../adr/0037-durable-writer-fulfillment-handoff.md)
  binds fulfilled requirements to the exact review, draft and planning context.
  It is fallible review evidence, not canonical story truth or proof that a repair
  is necessary. Source mismatch rejects the handoff rather than silently mixing
  versions.
- [Ordinary-review export](../adr/0038-read-only-review-evidence-export.md) and the
  [separate diagnostic-probe export](../adr/0039-diagnostic-probe-review-export.md)
  expose provenance and application-rendered literal evidence. They already have
  tracked implementations; creating another generic exporter is not the next task.
  The ordinary saved-review audit found **zero compatible records among 54
  candidates**, while the separate adapter exported the **same twelve diagnostic
  probes**, with 55/55 excerpt bindings. These probes are not production-qualified
  reviews. [Ordinary inspection](reviewer-copy-export-results-2026-10-30.md),
  [probe exports](reviewer-probe-export-results-2026-10-30.md).
- Local fixtures preserve duplicate keys, forbidden fields, invalid references,
  length and empty-final outcomes, provider error chains and unknown usage. A
  failure remains a counted failed attempt; inspection/export need not repair it
  or quietly permit another call. [Terminal support](reviewer-terminal-evidence-support-2026-10-22.md),
  [admission delivery audit](reviewer-admission-delivery-audit-2026-11-01.md).
- The recent source-map audit found **zero application mapping errors across
  3,924 presented reference entries**. That rules out a wrong reference map for
  those captures. It does not prove every renderer or application path correct.
  [Binding audit](reviewer-binding-semantics-audit-2026-11-02.md).

Our evaluation contract also needed refinement. A completed event can coexist
with a later boundary violation. A plan can support a claim about planned events
without proving that those events occurred. True components do not by themselves
establish contradiction, causation or a whole relation. A missing proof is not
always a disproof. These distinctions belong in typed work and explicit scoring,
not in an ever-longer free-form instruction alone.

Local tests demonstrate behavior on known fixtures and tampering controls. They
do not make a model more accurate, prove the inspector's semantic judgment, or
turn a hypothesized fix into an observed recovery. An authored regression is a
reproducible expectation, not another successful live test.

## What we learned about the models

The observed failures are not just transport or parsing errors. Valid final
answers sometimes assert an unsupported relation, confuse a later action with an
earlier obligation, overstate a plan's timing, or cite a neighboring passage while
giving an otherwise correct explanation. Some such errors recur with correct
source maps and valid evidence locations. The model's returned judgments are
therefore part of the problem on these tasks.

The evidence does **not** identify an intrinsic, unchangeable defect in DeepSeek,
its hidden reasoning mechanism, or Ollama as the cause. The comparisons used a
particular model route, mode, interface, resource cap and constructed workload.
Thinking and source-obligation improvements show that performance can change
materially under a different contract. Successful paraphrase, attribution and
source controls also rule out a blanket claim that the model cannot perform
semantic review. We have not run a matched alternative-provider test and are not
starting one here.

Reproducible requests do not guarantee reproducible answers. The same MA wire can
produce correct reasoning with the wrong reference, a semantic mistake with the
right reference, or a length stop. Latest H2/CP generation ranged from 8,885 to
16,000 tokens across unchanged requests. The current resource audit cannot divide
those totals into reasoning versus final tokens or attribute the variation to a
provider mechanism. [Headroom audit](reviewer-workload-headroom-audit-2026-11-02.md).

My interpretation is that the workflow is especially vulnerable when a single
response must select allegations, retain their scope, judge support, bind evidence,
complete several relations and obey a detailed output contract. The record is
consistent with that explanation; it has **not yet isolated simultaneous workload
as the cause**. The proposed workload comparison is designed to test that narrower
hypothesis while retaining full context.

## Why the investigation has not yet qualified better production

There are several different success conditions, and improvements in one have
often left the next unresolved:

| Question | Why the preceding success is insufficient |
| --- | --- |
| Did a complete, valid answer arrive? | Valid delivery says nothing about factual correctness. |
| Does the evidence point to the exact source? | A matching quotation may be irrelevant or cover only part of the claim. |
| Does the source support the entire claim? | A supported criticism may be optional, immaterial or already addressed. |
| Is the proposed edit necessary and properly scoped? | Correct repair intent does not prevent the writer from changing other prose. |
| Did the edit preserve obligations and improve the scene? | Fewer changes, mechanically correct patches or better diagnostic scores do not establish better reading. |

The writer experiments did not establish a dependable edit-selection policy.
The later reviewer work reduced some prerequisite uncertainties but mostly used
supplied claims, authored relation maps or narrow diagnostic reports. It has not
yet connected those gains to a qualified ordinary critic and a better repaired
scene. Repeatedly failing a strict overall screen also does not mean every partial
gain was useless or every explanation defect would harm a reader.

Some scoring ambiguity was ours. The human review interpreted “decides to enter”
as a call to investigate, while the older assignment contract asked for a
commitment to enter; neither interpretation requires a literal stock sentence.
Similarly, factual event completion and an editorial concern that suspense is
reduced need different judgments. Future criteria should resolve such distinctions
before inference, without rewriting earlier outcomes after seeing results.

## What the human review established

The user judged the eighteen versions as variations of one good story template.
The recorded review has nine overall ties and 45 dimension ties. That is useful
evidence that these small differences did not establish a meaningful reader
preference; it is not statistical equivalence or a fully independent blind study.
Blank fields meant no major concern. The review also included constructed controls,
so not every pair was a live writer revision.

Future human review should focus on **feel and emotion, flow, character and
story-breaking details**. Machines should prepare counts, exact differences,
assignment evidence and source locations. Those mechanics can be reviewed after
the first reading rather than forcing the reader to hunt through near-identical
texts. Use fresh scenes and meaningfully different versions; avoid repeated
exposure to the same template. Preserve expressive paraphrase and intentional
repetition rather than optimizing for exact copying. See the
[human-review record](critic-writer-human-review-results-2026-10-20.md).

## Recommended next production step

**Build one tracked, read-only assessment work-item and completion boundary, then
evaluate it on saved evidence before connecting it to the writer.** This turns
the investigation into a reusable application capability while keeping unsupported
claims out of automatic repair decisions.

This is an extension/port of the existing
[premise-admission preparation](cw013-admission-preparation-2026-10-31.md),
[local staged-handoff prototype](reviewer-staged-handoff-audit-2026-11-01.md) and
new workload preview, using the existing exporters and binding helpers. The
prototypes already establish selection identity and complete-context retention.
What remains is a tracked, provider-neutral contract with explicit assessment
completion, tested in the repository and initially usable only for read-only
replay. It is not a second export system or a claim that automatic semantic
selection/grouping has been solved.

The proposed bounded implementation should deliver:

1. **Version-bound work items.** Carry the complete source/report context, exact
   whole selected statement, its field and scope, and separately declared dependency
   links. Preserve diagnostic versus production provenance. Unknown semantic links
   stay unknown; authored gold links are not smuggled into a production extractor.
2. **Separate result states.** Keep delivery, exact binding, factual support,
   materiality/edit necessity and craft judgment distinct. “Unassessed” or
   “delivery failed” must not mean “the story is defective.” A successful exact
   comparison must not imply semantic support.
3. **Explicit completion and resource accounting.** Require every expected work
   item exactly once against the same immutable scope; retain all failed attempts
   and unknown usage. A partial batch cannot become a complete review. Sum cost
   and latency across all batches needed for a case. Completion alone cannot
   authorize writer dispatch or infer a whole relation from component labels.
4. **A read-only regression gate.** Replay the preserved success, citation, semantic
   and terminal fixtures with HTTP/DB access blocked. Reject changed versions,
   incomplete coverage and mixed scopes. Keep unsupported source types explicit;
   do not relabel the twelve diagnostic probes as ordinary production reviews.
   Check in a small compatible synthetic fixture set with the tracked code;
   keep full unpublished captures in the existing private diagnostic archives.

This proposed slice does not change production critic/writer prompts, canonical
prose, graph routing or the single mandatory Blueprint approval. Any later durable
state or workflow integration must follow the repository's ADR, versioning and
migration rules. The present task implements only the local audit, not this port.

## What to test after that boundary exists

The next isolated inference candidate is the **provisional 30-call full versus
narrow-workload MA diagnostic** in the
[headroom audit](reviewer-workload-headroom-audit-2026-11-02.md): eight unchanged
full controls versus 22 batches, retaining full context and whole linked claims,
with 56 judgments per condition. This changes assessment workload, not evidence
representation, thinking and token limits simultaneously. It needs exact freezing
and separate approval. It is not already authorized and does not reopen retired
calls. Smaller batches may cost more; success must be judged per completed case.

If delivery and material factual coverage become adequate, the following question
should be **whether this produces a better repair**, not whether another renamed
label improves a familiar diagnostic. Prepare a small scene-repair comparison with
an unchanged baseline, genuine defects, clean/no-op controls and fresh story
families. Keep repair scope explicit, machine-check mandatory obligations and
unrequested changes, and obtain human judgments on the reading experience. Do
not make a new human checkpoint mandatory in the autonomous product flow; this
is evaluation of a candidate before deployment.

Before that comparison, predeclare which failures can change a repair decision:
source/version corruption, missing mandatory obligations and material unsupported
premises are different from a nonmaterial explanatory imprecision or a defensible
craft preference. Record all of them, but do not make literal similarity the
definition of good writing. This is a prospective evaluation design change, not
permission to forgive historical failures or promote an unqualified reviewer.

For now, all fourteen issues remain open. The local work passes
**251 offline tests**, lint, formatting, strict typing and historical score replay.
The tracker is updated; Step 19 stays **IN PROGRESS**, Step 20 **NOT STARTED**.
Production prompts are unchanged, live inference paused and the canary on hold.
