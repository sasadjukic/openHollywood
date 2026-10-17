# Adjudication and exact edits: frozen comparison plan

Date: 2026-10-17. **PREPARATION COMPLETE; NOT AUTHORIZED FOR LIVE CALLS; NOT RUN.**

Both comparisons and the craft control are frozen and verified locally. They test
the [approved preparation proposal](../handoffs/fulfillment-routing-framing-diagnosis-next-experiment-2026-10-17.md)
following the [unsuccessful route-index and framing comparison](fulfillment-routing-framing-v61-results-2026-10-17.md).
Production remains **prompt 61 / graph 9 / fulfillment policy 1**. Candidate
contracts exist only in the private diagnostic bundle. **Full workflow canary
ON HOLD; NOT STARTED.**

Plan SHA-256:
`765fd0499eb2ddb87f97e32cdfcb65b338b544c9be2e452f34bc16e4da0368a2`

Source checkout: `4a6c9bdf0474e2f59fdc1c0c52d378ac1cd55242`.
Private bundle: `data/diagnostics/fulfillment-adjudication-edits-v61-2026-10-17/`.
There is no new `approval.json` or live-output directory. Previous approvals and
unused call allowances do not apply to this plan.

## Frozen matrix and budget

| Block | Primary probes | Maximum inference attempts |
| --- | ---: | ---: |
| A: six critic cases × two arms × two seeds | 24 | 48 |
| B: two fixed sources × two writers × two seeds, each with one post-critic | 16 | 32 |
| C: two ordinary craft-source critics, four conditional writers and four posts | 10 | 20 |
| **Total** | **50** | **100** |

Each probe permits **one structural retry**, never a semantic reroll or another
writer revision. The three block limits are nontransferable. Stage ceilings are
48 A-critic attempts, four craft-source attempts, 24 writer attempts and 24 post
attempts. Failed or unknown dispatches consume their reservations. Skipped slots
expire; they cannot fund replacement cases or extra attempts.

- Model: `gemma4:31b-cloud`, through the **local Ollama daemon to Ollama Cloud**.
- Frozen digest: `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
- Seeds: **19401 and 19403**. Critic temperature 0.2; writer temperature 0.85;
  top-p 0.95; thinking disabled.
- Per attempt: at most **24,000 input / 8,000 output tokens / 900 active seconds**.
- Aggregate reservations: **2,400,000 input / 800,000 output tokens / 90,000 active
  seconds**. These are ceilings, not predicted usage or elapsed duration.
- Historical October 8 rate estimate at those token ceilings: **USD 0.65600**.
  Actual billed charges are unknown; this is not a current-price guarantee.

No discovery, inference or external network calls occurred during preparation.
Model identity must be checked after approval and before each live phase; a
different digest stops execution rather than silently updating the freeze.

## A. Ordinary critic versus adjudication only

The complete six cases, artifact versions, constraints and source catalogs are
reused exactly from the sealed preceding comparison:

| Case | Expected native turn / outcome | Expected boundary |
| --- | --- | --- |
| Elena clean | met / met | no overrun |
| Elena separate match | met / met | overrun |
| Elena embedded match | met / met | overrun |
| Elena genuinely missing decision | met / unmet | no overrun |
| Elena complete compound outcome | met / unmet | overrun |
| Elara embedded entry | met / met | overrun |

**J0** is ordinary v61 with no route index. Its complete request, including retry
construction, matches the ordinary production builder.

**J1** returns only `assignment_checks` and `scene_boundary_check`. Their existing
field shapes, status meanings, evidence identities and bounds remain. It generates
no repair conditions, issues/links, scores, POV/other-assignment findings or verdict.
It yields a diagnostic `judgment`, explicitly ineligible as a production Critique
or writer source. Missing craft output does not become an inferred empty craft list.

J1 retains the complete-obligation rule, requirement-basis distinctions, indirect
evidence and decision semantics, relevant completion distinction, native compliance
semantics, endpoint comparison, due-now scope and advisory length policy. It removes
instructions to generate absent fields. All input artifacts, assignment, endpoint,
scope, rubric and source catalogs remain identical to J0; no expected answer or
new semantic rule enters the messages. Its schema is a strict subset of the ordinary
response shape, with current-draft evidence enums. Nonblank assessments/comparisons,
coverage, null advice, bounds and exact references are checked locally.

On a J1 structural retry, the original context and diagnostic schema are supplied
again with the actual validation errors. No rejected response body or pinned native
status is supplied. Ordinary full-review retry directives are replaced so they do
not require absent J1 fields. A valid wrong judgment does not trigger another call.

At seed 19401, run J0 then J1 for each case in the table's order. At 19403 reverse
the arm order. All 24 probes run independently of semantic results, subject to
global stop rules. None selects the fixed writer sources.

Score first and final validity, shared native/boundary tuples, source support,
extractable unvalidated raw judgments and retry drift. A promising signal requires
**12/12 supported, valid final J1 tuples** and more correct final tuples than J0,
with all controls retained. Perfect J0 means non-reproduction, not treatment benefit.
J0 advice and verdicts remain separate audit axes; J1 does not qualify those axes.
Do not treat the smaller schema's validity rate as a routing improvement. The
combined task/schema change cannot isolate removal of routes from fewer tasks or
shorter output. Missing turning-point detection is outside this all-met-turn matrix.

## B. Full-scene output versus exact edits

The writer sources remain independent, fixed, successful ordinary reviews:

| Case | Source trial | Attempt |
| --- | --- | ---: |
| Separate entry | October 16 `s19101-elara-separate-initial` | 2 |
| Embedded entry | October 17 `s19201-elara-embedded-initial` | 1 |

Their full drafts, raw reviews, validated receipts, original outcome-framed repair
tests and exact ordinary fulfillment packets are frozen. The failed boundary
reframing is absent. Neither new J0/J1 output nor a rejected historical review can
be substituted as writer evidence.

**E0** is the ordinary v61 full-scene writer with its fulfillment packet.
**E1** receives identical substantive instructions, complete context, feedback and
evidence, but returns the ordinary non-prose fields and this diagnostic edit shape:

```json
{
  "base_draft_version_id": "<exact immutable draft version>",
  "base_prose_sha256": "<exact UTF-8 prose digest>",
  "edits": [
    {"old_text": "<nonempty exact original text>", "occurrence": 1, "new_text": "<replacement>"}
  ]
}
```

The display omits ordinary title/scene/revision/completion fields for brevity; the
frozen schemas retain them. E1's new `edit_base` payload field carries only the
version and digest, not a selected defect span or suggested replacement.

Occurrence is one-based, counting exact matches left to right in the original text,
including overlapping matches. Resolve every edit before applying any; require
original-position order and nonoverlapping selected ranges. Empty replacement
deletes. Anchored replacement permits insertion. Whitespace and Unicode edits are
allowed. Apply atomically, with no fuzzy matching, auto-correction, partial application
or fallback to full-scene generation. A malformed patch receives only its permitted
structural retry.

The model chooses up to **64** spans, anywhere in the scene, including fulfilled
evidence. A whole-scene replacement is explicitly allowed. There is no maximum
diff size, protected passage or stronger preservation reminder. Zero edits can be
structurally valid, but cannot count as repairing these defective scenes. The
materialized complete Scene Draft passes ordinary writer lineage/structure checks;
semantic success is assessed separately. Materialization never writes to canon.

Run both seeds for both cases and arms, E0/E1 at 19401 and E1/E0 at 19403. Immediately
post-review each valid writer using an **ordinary critic**, complete resulting prose
and original acceptance tests. Posts receive no edit protocol, treatment label or
fulfillment packet. A terminally invalid writer skips only its own post. No second
writer revision is included.

## C. Independent craft inside fulfilled evidence

The new noncanonical case derives from the complete embedded Elara draft. It
duplicates exactly this sentence once immediately beside itself:

> She braced her free hand on the jamb to carry herself through.

All other prose and context remain unchanged. The new draft has its own deterministic
version and recorded parent version/hash. The native decision and turning point
remain present, and the completed-entry overrun remains. This is an obvious repetition
stress test, not a general rule against repetition or a story-quality benchmark.

At each seed, an ordinary v61 source critic receives the complete case without a
craft hint, answer key or diagnostic output treatment. A source qualifies only if:

- Ordinary validation succeeds; native facts are correctly met; the boundary overrun
  is correctly reported; no other assignment/POV repair is introduced.
- It reports exactly one supported, actionable **independent craft** finding about
  the repetition. Any other generic entries must repeat the boundary finding. There
  must be exactly two ordinary projected repair tests: boundary and independent craft.
- Positive native evidence covers **both exact repeated sentence ranges**, and the
  craft finding cites an overlapping repeated range. Sequential catalog resolution
  distinguishes identical quotations by their actual positions and UTF-8 ranges.
- Operator inspection confirms the full-prose native facts, boundary, independent
  repetition, advice support/no extra requirement and ability to repair inside met
  evidence. The saved assessment binds the plan hash, source trial, raw response hash,
  craft issue and exact overlap refs, with explicit rationales.

Requiring both repeated ranges is a preparation decision: if only one were cited,
deleting the uncited copy could satisfy the complaint without exercising an edit
inside positive evidence. This strict control may be ineligible; that outcome stays
visible rather than being replaced with favorable evidence.

A qualifying source supplies both E0/E1 writers at its seed, unchanged through the
ordinary projection, followed by their ordinary posts. Missing or unsupported craft,
wrong judgments, extra repairs, insufficient overlap or structural failure makes
that source ineligible and skips its two writers and two posts. No manufactured
critique, edited packet, replacement case or reroll is allowed. Pending operator
assessment stops dependent dispatch without spending a call. This is evaluation
inspection by the task operator, not another required human product checkpoint.

Both craft pairs must qualify and complete before claiming this control passed.
Its failure does not cancel or select results from A or the fixed-source B block.

## Scoring, inspection and decision rules

The frozen scoring record keeps response/patch validity, fact retention, boundary
repair, original-test satisfaction, advice support, independent craft and prose
preservation separate. Review every rejected attempt and full scene, not just a
selected excerpt or the final accepted response.

For the writer, a promising signal requires **at least two of four primary preservation
wins, including an embedded-case win, with no preservation loss**, all four candidate
primary repairs valid and factually sound, and both candidate craft controls qualified
and repaired without factual loss or added unsupported changes. Separate-case ties
are acceptable because the control has already demonstrated exact repairs there.
Invalid outputs, failed sources and skipped pairs remain in scheduled denominators;
they cannot make a smaller surviving subset qualify. Incomplete repair cannot earn
a preservation win.

Necessary changes, unnecessary restatement, benign wording, new psychological beats
and plausible craft tradeoffs receive distinct full-prose rationales. Exact restoration,
quote retention, word counts and diff size are descriptive, not literary scores.
The exporter emits complete originals/revisions/diffs and six scheduled anonymous
pair slots, with a private randomized order key. Unavailable pairs stay accounted
for. Human review sheets remain empty until a human completes them. Assistant
inspection and critic ratings never become human preference evidence.

Neither candidate is promoted automatically. J1 cannot replace a production critic
that must also assess craft. E1 must permit useful changes within fulfilled passages.
Later story-quality work still requires the accepted weighted rubric/hard gates,
full intended Cloud corpus and comparable single-model baseline. Constraint adherence
is only 5% of that rubric. These small diagnostic comparisons do not start Step 20.

## Freeze contents and verification

The bundle contains seven scripts: `contracts.py`, `experiment.py`, `execute.py`,
`local_check.py`, `harness_check.py`, `source_replay.py` and `score.py`. It freezes:

- Complete seven-case data, two fixed ordinary writer sources and packets, scoring,
  all 50 schedule slots and the exact 100-attempt budget.
- **34 exact initial requests**: 24 A critics, eight fixed writers and two craft
  source critics. Four craft writers, twelve posts and retries use hashed conditional
  builders; their future response-dependent bytes are not falsely represented as
  already known. Each actual request is saved and reserved before dispatch.
- **36 paired request-difference records**, including retry views and two fixture
  craft-source pairs. Ordinary controls match their production builders. These
  craft fixture requests are verification evidence, not substituted live sources.
- **128 code/dependency hashes**, **46 plan-bound JSON files** and **1,287 fixture
  evidence files**. The preparation closure additionally binds this report and the
  authoritative tracker snapshot. Historical bundles remain unchanged.

Verification completed:

- Reverified predecessor seals and replayed all **40 prior probes / 42 attempts**,
  plus both fixed ordinary writer sources, with network access blocked.
- Passed **50 stage fixtures**, **50 retry builders**, six identical-output post
  equivalence checks and **37 negative contract/source checks**. Covered stale/missing
  references, duplicate JSON, malformed advice, edit ambiguity/overlap/order, Unicode,
  no-op behavior, whole-scene edits and deficient craft evidence/assessments.
- Exercised the actual operator with **100 fake dispatches across independent ledgers**:
  52 in the valid matrix, 44 in the fault matrix and four terminal-failure fixtures.
  Verified retries, semantic failure without reroll, source rejection, dependent
  skips, ordering, all ceilings, approval/source/request/model guards, unknown and
  incomplete outcomes, transport/cancellation/usage failure stops and zero-call replay.
- Replayed all 96 completed fixture attempts under the final validators. Exported
  six complete anonymous fixture pairs for the valid matrix and three for the fault
  matrix; all six scheduled slots remain recorded. These are not live results.
- **75 focused regressions passed**. Repository Ruff lint/format and strict mypy
  passed for 201 files. All seven private scripts pass Ruff lint/format. No client
  or production code changed, so frontend/build checks are not applicable.

The initial sandbox test run could not create pytest temporary fixtures, and Windows
asyncio initialization stalled there. Final mocked tests used a fresh workspace
temporary directory and permitted local event-loop wakeup initialization. During
the fake harness exercise, external connects and real gateway construction were
blocked. Preparation used **zero live model, discovery or external network calls**.

## Execution boundary

After approval of this exact plan and payload/destination, execute once in this order:
preflight identity check; A judgments; B fixed writers/posts; C ordinary source critics;
inspect and record source eligibility; then eligible C writers/posts. Persist and
reconcile every attempt, including failures. Stop on identity, integrity, transport,
cancellation, unknown-outcome or budget failure. Do not tune prompts mid-comparison.

The payload would include **full unpublished fictional prose, critique, Blueprint,
Scene Plan, Story Bible and diagnostic context sent to Ollama Cloud through the local
Ollama daemon**. A new approval must bind this plan hash, the 100-call ceiling and
canary exclusion before gateway construction or discovery. Local preparation is
complete; that approval has not been given.

**Step 19 remains IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
