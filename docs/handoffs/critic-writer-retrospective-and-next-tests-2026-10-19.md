# Critic and writer dynamics retrospective and recommended tests

Date: 2026-10-19. Evidence through the completed 74-call comparison on this date.

Update 2026-10-20: the user has completed all nine pairs, reporting nine overall
ties and one promising story foundation. See the
[human findings and revised review process](critic-writer-human-review-results-2026-10-20.md).
The pending-review descriptions below record the preparation-time position. Future
human review will focus on overall feel, flow, character, and story-breaking issues,
with mechanical results prepared separately. The provisional experiments below
remain unprepared and unauthorized; editorial scoring must account for this feedback
before either is frozen.

We have improved the mechanics of the critic/writer loop and several individual
judgments, but we have not established reliable editing that fixes defects while
preserving or improving the story. The experiments separated problems that initially
looked like one problem: interpreting the assignment, noticing craft defects,
delivering a valid report, choosing appropriate edits, and evaluating their literary
effects.

The recommended next direction is to simplify responsibilities and obtain independent
editorial evidence. Another preservation reminder, explanation field, or retry
instruction is unlikely to resolve the entire dynamic. This is a synthesis and
proposal, not a frozen experiment or authorization for inference. Production remains
prompt 61 / graph 9 / fulfillment policy 1; the full workflow canary remains on hold.

## What we have tried

### Scene boundaries and repair ownership

We exposed the current endpoint and next-scene reservation, consolidated duplicate
complaints, preserved historical repair identities, and made mandatory advice
source-bound. Shared native conditions reduced duplicated or competing instructions
and eventually passed their focused matrix. These changes improved traceability and
repair delivery without proving that the critic interpreted every assignment
correctly. See the [shared repair conditions report](../benchmark_reports/shared-repair-conditions-v59-2026-10-13.md).

Earlier tests also exposed stronger-than-assigned advice: asking for causation when
only two facts were required, or completed entry when only a decision was assigned.
An instruction to request minimum repairs did not eliminate those errors. See the
[minimum assignment repairs report](../benchmark_reports/minimum-assignment-repairs-v52-2026-10-11.md).

### Direct preservation guidance

We tested a minimal-edit instruction, removed an already satisfied historical
decision complaint from writer context, and narrowed boundary advice to the violated
endpoint. These changes did not stop unnecessary explicit decision sentences or
ending rewrites. The behavior was not explained solely by one stale complaint.
See the [writer clarification](../benchmark_reports/writer-minimal-repair-v60-2026-10-14.md),
[history comparison](../benchmark_reports/writer-satisfied-history-v59-2026-10-14.md),
and [boundary advice comparison](../benchmark_reports/writer-boundary-advice-v59-2026-10-15.md).

### Positive fulfillment evidence

We showed the writer what the latest critic already considered satisfied, together
with the exact supporting passages. The first comparison achieved deletion-only
preservation in 2/2 evidence cases versus 0/2 controls. A transfer test initially
stopped at the critic gates: the critic treated a later forbidden match as undoing
an earlier decision to investigate. With explicit event scope and diagnostic
reviews, evidence-assisted transfer succeeded. The necessary-edit exception also
allowed repair inside a cited passage while retaining the fulfilled fact; minimal
editing was not established by that exception test.

Sources: [first evidence comparison](../benchmark_reports/writer-fulfilled-evidence-v59-2026-10-15.md),
[blocked transfer](../benchmark_reports/writer-evidence-transfer-v59-2026-10-15.md),
[event-scoped transfer](../benchmark_reports/writer-event-evidence-v59-2026-10-15.md),
[necessary-edit exception](../benchmark_reports/writer-preservation-exception-v59-2026-10-15.md).

We then implemented the durable, version-bound production handoff. Ordinary-critic
results were inconsistent. In the first run, only one of four paired cases was
eligible; the evidence arm added an unnecessary explicit decision while the control
restored the clean text. A replication avoided explicit restatement in all three
evidence arms, whereas all three controls added it. However, all six writers still
rewrote the adequate ending. Keeping cited quotations did not ensure preservation
of the surrounding expression.

Sources: [production design](fulfillment-evidence-production-design-2026-10-15.md),
[ordinary-critic results](../benchmark_reports/production-fulfillment-v61-results-2026-10-16.md),
[replication](../benchmark_reports/fulfillment-contrasts-v61-results-2026-10-17.md).

### Fulfilled events and forbidden endpoints

We tested scope guidance, exact failed-clause identification, event-versus-terminal
wording, and a route index. Clause inspection and clearer requirement wording helped
in some tests. The route index did not solve attribution or reporting: some retries
recovered a legal output by changing a correct fulfilled-event judgment into an
incorrect unmet judgment.

J1 reduced the task to adjudication and achieved 12/12 supported shared judgments
versus 8/12 ordinary reviews. This supports further testing of smaller responsibilities,
but J1 removed several tasks together. It supplied neither complete repair advice nor
craft assessment, and was not a production Critique or writer source.

Sources: [failed clauses](../benchmark_reports/critic-failed-clause-v59-2026-10-15.md),
[event versus terminal](../benchmark_reports/critic-event-terminal-v59-2026-10-15.md),
[route index](../benchmark_reports/fulfillment-routing-framing-v61-results-2026-10-17.md),
[J1](../benchmark_reports/fulfillment-adjudication-edits-v61-results-2026-10-17.md).

### Boundary framing and exact writer edits

Boundary framing produced zero preservation wins, three losses and one tie. E1 exact
edits applied successfully and repaired the factual defects, but still selected
unnecessary adjacent changes. Lowering writer temperature produced no clear
preservation win. These interventions controlled execution or variation without
reliably improving editorial selection. E1 remains mechanically successful and
unqualified for preservation.

Sources: [framing](../benchmark_reports/fulfillment-routing-framing-v61-results-2026-10-17.md),
[exact edits](../benchmark_reports/fulfillment-adjudication-edits-v61-results-2026-10-17.md),
[temperature](../benchmark_reports/fulfillment-presentation-temperature-v61-results-2026-10-17.md).

### Continuous prose and independent craft detection

P1 added uninterrupted scene prose alongside the sentence catalog. Raw accidental
duplication detection improved from 0/4 to 4/4, without unsupported removal demands
on functional recurrence controls. Only 2/4 became valid usable findings because
duplication-plus-overrun reports violated the output contract. This was a noticing
gain with a separate delivery failure. It did not isolate paragraph layout from
redundancy, salience, or input length. See the
[P1 results](../benchmark_reports/fulfillment-presentation-temperature-v61-results-2026-10-17.md).

### Retry feedback and restricted report corrections

Expanded structural feedback added no qualified recovery over ordinary feedback:
both recovered 2/3 failed initials. F1 restricted corrections subsequently improved
failed-parent recovery from 4/8 to 6/8. It still sometimes answered the boundary
question instead of the craft comparison question, and failed compound native
controls by emitting a hybrid patch and whole report. Correct location and legal
structure did not establish correct meaning.

Sources: [expanded feedback](../benchmark_reports/fulfillment-reporting-edit-purpose-v61-results-2026-10-17.md),
[restricted corrections](../benchmark_reports/fulfillment-repair-surface-review-v61-results-2026-10-18.md).

### Edit purposes and comparative assessment

Per-edit purposes produced two primary preservation wins, three ties and one mixed
result, but only four of eight purpose claims were fully supported. Some explanations
treated compatible preparation as a boundary violation or used a desired tonal
change to justify a supposedly necessary edit. Both writer arms successfully removed
the optional duplicate control.

Reviewing originals and revisions did not solve the editorial problem. Comparative
reviewers missed concrete losses or labeled optional replacement imagery as required
repair. Showing writer purposes sometimes encouraged an unsupported necessity claim.
The first comparative-assessor run also produced invalid reports and stopped after
input copying exhausted an output allowance.

Sources: [purposes and craft repair](../benchmark_reports/fulfillment-reporting-edit-purpose-v61-results-2026-10-17.md),
[comparative assessment](../benchmark_reports/fulfillment-repair-surface-review-v61-results-2026-10-18.md).

### Output contracts and evidence metadata

The final completed comparison used all 74 authorized calls. V2 improved valid
comparative reports from 0/18 under V0 to 15/18. F2 and F3 failed parent-hash binding
in all twelve responses. V3, which delegated quotation and version expansion to an
adapter, produced only 1/18 valid reports: seventeen responses used bare references
instead of fingerprinted handles. F3's focused raw explanations correctly identified
the independent duplicate in all four comparison cells, but failed bindings kept
them from becoming qualified corrections.

Valid structure still did not establish editorial support. Reviewers missed the mixed
ending's losses, sometimes called optional imagery necessary, and one V2 review
reported deterioration despite byte-identical original and revision prose. The
truncated V0 outputs copied input material; they were not nearly complete assessments
that merely needed more output space. See the
[completed output-contract comparison](../benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md).

## Evidence to retain

| Component | Supported result | Limit |
| --- | --- | --- |
| J1 | Better narrow assignment adjudication | No complete advice or craft review |
| Fulfillment handoff | Some successful preservation and necessary repairs | Inconsistent ordinary-critic eligibility and preservation |
| E1 | Reliable exact patch application | Unnecessary edit selection remains |
| P1 | Better raw duplication noticing | Combined reports still fail delivery |
| F1 | Additional qualified failed-report recoveries | Incomplete coverage and control failures |
| Writer purposes | Some paired gains and successful optional craft repair | Unsupported necessity claims and mixed trade-offs |
| V2 | Substantial comparative-report delivery gain | Editorial judgment remains inadequate |
| F3 | Correct focused raw craft comparisons | Invalid parent binding in every tested cell |

These are bounded observations. None demonstrates the complete critic/writer
behavior needed for production qualification or a general improvement in story quality.

## Why overall improvement has stalled

**Several independent failures share the same visible symptom.** A critic can
understand the defect and produce an invalid report, or produce a valid report with
an incorrect interpretation. A writer can repair the assignment while weakening
useful expression. A post-critic can accept that revision without evaluating what
disappeared. Fixing delivery does not automatically fix interpretation or editing.

**Correct execution does not establish good editorial selection.** E1 applied the
requested edits accurately. The model nevertheless selected unnecessary changes.
Removing a forbidden entry does not require replacing purposeful preparation with
a bodily sensation or a new metaphor. Those choices may have artistic value, but
that value is a separate question from repair necessity.

**Explanations can rationalize a replacement.** A true statement about the old defect
does not justify every part of the new sentence. Purpose fields did not reliably
distinguish defect removal from optional imagery, deleted preparation, or changed
timing. The explanation is evidence to inspect, not proof of editorial necessity.

**Editorial feedback is not yet independent enough.** Ordinary post-critics often
saw the revision without the complete original and difference. Later comparative
reviewers received that information and still missed losses. The recent comparisons
used the same model deployment. A shared preference for explicit resolve, bodily
tension, or metaphor is a plausible explanation for some agreement, but remains a
hypothesis about the behavior rather than an established internal cause.

**The reporting task imposes substantial non-editorial work.** The latest requests
contained roughly 14,000–23,000 input tokens and required intricate routing and
metadata. Copying errors could invalidate useful observations. J1 and V2 support
testing simpler interfaces; neither proves that length alone caused the failures.
Increasing output allowance would not directly address the observed input copying.

**Reader preference remains unresolved.** The reports still mark independent blind
human review as pending. Much of the recent work concentrates on related scenes and
endings. We can establish that a concrete detail disappeared or a necessity claim
is unsupported without knowing that every reader would prefer the original.
The [accepted complete-story rubric](../../open_hollywood_bible/product_contract_and_benchmarks.md)
allocates only 5% to continuity and constraint adherence; it also requires a comparable
single-model baseline and blind human evaluation.

## Approaches still worth testing

1. **Let the application own identity binding completely.** V3 attempted part of
   this, but still required fingerprinted handles in model output. A new contract
   could accept short request-local references while the application binds the
   request, parent, versions, and exact quotations. Unknown references would still
   fail. This would be a declared new interface, not retrospective repair of failures.
2. **Test a separate craft review.** A craft-only pass could read continuous prose
   and report independent observations while another pass checks assigned events
   and boundaries. The application would combine validated records. J1 supports
   investigating smaller responsibilities; this complete arrangement is unqualified.
3. **Use a controlled model crossover on the same failures.** Compare the current
   deployment with an independently selected model family on identical frozen cases.
   Test whether it detects losses and rejects unsupported necessity claims, rather
   than simply generating more criticism. No alternative model is selected here.
4. **Separate repair selection from repair wording.** Compare model-selected edit
   regions with independently specified regions, using the same exact-edit machinery.
   This isolates choosing where and how much to change from writing the replacement.

For eventual production, distinguish mandatory repair proposals from optional craft
proposals so each can be assessed on its merits. Do not permanently lock fulfilled
passages or equate the smallest difference with the best fiction. Useful craft work
must remain possible inside passages that already satisfy their factual assignment.

## Recommended diagnostic sequence

### Human review before more inference

Review the existing anonymous original/revision pairs for agency, specificity, voice,
tension, naturalness, and overall preference. Record concrete gains and losses, then
check assignment compliance separately. This requires zero model calls. Existing
reports or recognizable prose can compromise blindness; reviewers should record
prior familiarity and, where possible, include an independent reader who has not
read the analysis.

### Reviewer diagnostic with a provisional ceiling of 48 calls

Use 12 fixed original/revision cases, two output contracts, and two model families:
12 × 2 × 2 = 48 calls, one attempt per cell. Compare V2 with a compact interface using
application-bound identities. Include new story contexts, unchanged-text controls,
minimal repairs, worthwhile craft changes, and attractive rewrites that lose concrete
meaning. Score delivery separately from supported editorial judgment. This is a
proposed pilot; cases, models, requests, scoring, token/time budgets and stop rules
still need to be selected, frozen, verified and approved before live calls.

### Writer selection diagnostic with a provisional ceiling of 24 calls

After a usable reviewer interface and human reference judgments exist, use six cases,
two scope conditions, and two writer models: 6 × 2 × 2 = 24 calls. Compare model-selected
repair regions with independently specified regions while holding the task and patch
machinery constant. Include a legitimate craft edit inside a fulfilled passage.
This isolates scope selection from replacement quality. It also requires a separate
frozen plan and approval; the provisional 48 and 24 counts are not an authorized
combined budget.

Prioritize these diagnostics over more preservation reminders, lower temperatures,
larger output caps, or additional explanation fields. Complete-story evaluation
against the accepted rubric and comparable baseline remains a later requirement.
No additional production human checkpoint is proposed; human reading here is evaluation.

## Prepared human review materials

A new local packet packages all nine original/revision pairs from the completed
output-contract comparison. It contains four actual writer revisions and five
constructed controls, all from the Elara scene family. It is a focused diagnostic
sample, not nine independent stories or a representative quality benchmark. This
composition and all source identities are withheld from the reviewer-facing files.

Start with the [blind reading packet](../../data/human_reviews/critic-writer-2026-10-19/reviewer/01-blind-reading-packet.md).
The [response form](../../data/human_reviews/critic-writer-2026-10-19/reviewer/03-response-form.md)
now contains the user's completed review and separately attributed recorded evidence.
After literary judgments are recorded, use the
[assignment checklist](../../data/human_reviews/critic-writer-2026-10-19/reviewer/02-assignment-checks.md).

The [coordinator source key](../../data/human_reviews/critic-writer-2026-10-19/coordinator/source-key.md)
reveals original/revision placement and provenance. Do not give it or this
retrospective to a blind reviewer before their responses are recorded. The packet
uses exact full prose, shuffled pair order, and randomized A/B placement. Blank
forms do not constitute completed human review. Historical exports remain unchanged;
new review materials stay in Git-ignored local storage.

Step 19 remains IN PROGRESS. Step 20 is NOT STARTED. The canary remains ON HOLD.
