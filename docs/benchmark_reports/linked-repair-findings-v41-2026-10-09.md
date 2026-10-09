# Linked historical repair findings: implementation and live diagnostic

Date: 2026-10-09. Production contract v41 / graph v9.

**The original duplicate-reporting case now retains two original obligations
instead of four repeated issues. The five-probe experiment also exposes a new
response-format failure and unresolved semantic judgment problems.** The
consolidation mechanism is implemented and tested; the live results do not
qualify the reviewer as stable or justify a full-story campaign yet.

## What changed

In v40, current findings and unmet historical repair checks could describe the
same defect using different evidence and wording. Both became canonical issues,
potentially producing new repair IDs. v41 adds `current_finding_refs` to each
repair check so the critic can explicitly identify the current reports that
repeat that exact original obligation. The application validates references,
category, severity and ownership before replacing linked reports with the
original claim and requested repair, supported by the combined current evidence.

Unlinked findings remain separate. A satisfied historical repair cannot clear a
current blocker, and an unmet test still requires revision. Current wording is
retained in the version-bound audit; it does not become a newly worded repair
target. Distinct original obligations remain distinct. There is no fuzzy
matching or blanket suppression of issues in the same category. The application
does not prove that two narrative claims mean the same thing.

See [ADR 0025](../adr/0025-linked-historical-repair-findings.md). This changes the
repair-bearing response schema and materialization, with no new role, call,
canonical schema, migration or retry/revision allowance. Initial-review schemas
are unchanged. The four reused requests grow by 784 characters each; their other
message content, artifact inputs and sampling settings are exactly unchanged.

## Fixed experiment

The user approved five isolated critic probes, at most ten calls and an estimate
of USD 0.06560 using recorded October 8 rates. Each probe allows one structural
retry. There are no new writer calls, semantic rerolls, second revisions or
full-story runs. The allocation is a ceiling, not permission to add cases after
seeing results.

Four cases reuse the exact OH-V01-002 inputs from the
[v40 writer-repair experiment](consolidated-overrun-writer-repair-2026-10-09.md):
the unchanged scene and three saved writer revisions. The fifth copies revision
19103 and changes its future date/realization to the current birthday. Its
handwriting comparison remains unchanged. The control should therefore retain
the repaired outcome while reporting the missing future-date turn independently.

Every case retains full standard story context, the next-scene reservation and
the synthetic outcome: **"Elena decides to verify the handwriting. No handwriting
match is established by the end of this scene."** This synthetic diagnostic plan
does not replace the approved canonical Blueprint. The frozen source critiques
and their original repair IDs are reused without rewriting the advice.

Before inference, four old responses were replayed with manually added synthetic
link annotations. Counts changed from 4 to 2 for the unchanged draft and 3 to 2
for revision 19104; the two passes remained at 0. Verdicts and original repair
targets were preserved. These annotations test the wiring only; they are not
model-generated links or additional live observations.

## Observed results

| Frozen case | Calls | Valid final review | Canonical issues | Observation |
|---|---:|---|---:|---|
| Unchanged draft, 19102 | 1 | REVISE | 2 | Repeated tension and outcome reports link to their two original repairs |
| Saved repair 19102 | 2 | None | Not applicable | Both attempts mark repairs met but supply invalid current-finding links |
| Saved repair 19103 | 1 | PASS | 0 | Original outcome repair met; empty links |
| Saved repair 19104 | 1 | PASS | 0 | Ambiguous prose accepted, unlike its v40 REVISE result |
| Missing-turn control, 19103 | 1 | REVISE | 1 | Reopens the outcome repair; missing turn appears only in assessment text |

Four probes validate on their first calls. The other exhausts its one structural
retry, giving **six calls, four valid reviews and one failed probe**. A failed
review is not a manuscript rejection and is not counted as an accepted PASS.

### Original duplication: observed consolidation

The unchanged draft explicitly links `issue:0` to its original tension test and
both `boundary` and `assignment:outcome` to its original outcome test. v40's
current-route consolidation first combines boundary and assignment, then v41
combines those current findings with their linked historical obligations.
The final two issues retain original claims and repairs with current evidence.
Adding this critique to the history creates no extra repair target.

This is direct live evidence for the intended mechanism. The lack of duplicate
issues in the passing cases is not evidence of link use: those cases emit no
current findings and use empty links.

### Repaired draft: response failure, not failed writing

Revision 19102 still says Elena cannot bridge similar and identical and that
the evidence is not yet proof. Both raw reviews recognize the repair and propose
PASS. Both nevertheless link met tests to nonexistent current issues/routes.
The critic reports no current craft issue or assignment violation and a
no-overrun boundary, so those links have no valid target.

The application rejects both responses as `repair_test_links_invalid`. The
single retry receives the validation error but repeats the error. No critique is
accepted, no manuscript defect is established by that failure, and no writer is
called. This is a new live protocol-compliance problem introduced by asking for
links, despite correct deterministic rejection behavior.

### Ambiguous prose: verdict changes without a text change

Revision 19104 still contains apparent identity, "the very perfection of the
match" and doubts about forgery/authorship. v40 required revision. v41 now treats
the suspicion as sufficient to leave the match unestablished and passes it.
Its source draft, seed and semantic context are unchanged; the response schema
has changed. This is observed sensitivity, not proof that the new verdict is
correct or that this schema alone deterministically caused the change. It does
not resolve the distinction between an unconfirmed likeness and uncertain
authorship of a likeness already recognized as matching.

### Missing turn: noticed but not made independently actionable

The control's review mentions the absent ten-year-future date in the boundary
comparison and original outcome test's assessment. It emits no
`assignment:turning_point` violation. Instead, it labels the unchanged
inconclusive handwriting comparison an outcome violation and links that report
to the original outcome repair. The canonical review carries just that original
outcome obligation; adding it to history creates no missing-turn repair target.

The overall REVISE verdict therefore does not mean this control succeeded. Its
expected separate turn obligation was not produced, and the old repair was
reopened despite identical handwriting prose passing in the paired base case.
No emitted turn finding was deleted by consolidation: that finding was never
emitted. Its mention remains inspectable in audit text but does not become a
dedicated writer/critic acceptance test. A no-overrun status also coexists with
prose describing an endpoint violation, showing inconsistency within the review.

## Interpretation and next work

The narrow duplicate path is addressed when the critic supplies valid, accurate
links. Deterministic tests protect independent reported obligations and source
identity. They cannot ensure the model reports each defect, correctly interprets
prose, or supplies a structurally consistent response.

The immediate follow-up should constrain met checks to an empty link array in
the response schema itself, using explicit status alternatives, while retaining
application validation and the existing one-retry limit. Verify the failed
passing control before expanding the live sample. Do not rescue inconsistent
responses by silently deleting their links.

The missing-turn result then needs a separate focused check of how an observed
current defect becomes its own assignment finding and repair target. Preserve
the paired repaired draft to expose mistaken reopening of historical repairs.
Match-versus-authorship ambiguity remains a distinct semantic target. New live
requests require a separately defined and authorized payload set; none of these
follow-ups is run in this batch.

No general critic success rate, model-agnostic semantic reliability, automatic
generation of explicit endpoints, story-quality improvement or full-story
acceptance follows from these five cases on one scene/model. Keep this branch
as an evaluated candidate with outstanding qualification issues rather than
treating the test-suite pass as readiness to close stabilization.

## Verification, provenance and cost

Base commit: `a75dde13da043fb101b9eb71705a0fc2c058735f`; branch:
`codex/linked-repair-findings`. Exact source, implementation, plan and prepared
request hashes are frozen. The read-only benchmark database retains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Prior requests, responses and results are unchanged.

All six actual requests reconstruct exactly, including the structural retry.
Every captured response hash verifies. All four valid outputs and their audits
rematerialize exactly; both failed responses reproduce their validation errors
and captured failure evidence. Original repair-test lineage verifies. The
missing-turn control's lack of a new test is recorded as a failed expectation,
not relabeled as successful lineage preservation.

The six calls consume **71,252 input / 6,353 output tokens**. At recorded October
8 rates of USD 0.14/M uncached input and USD 0.40/M output, the estimate is
**USD 0.01251648**, below the approved USD 0.06560 ceiling. Actual charges remain
unknown. Provider usage reports with unknown cost basis are not evidence of a
zero bill; this is a separate rate-based estimate, not a newly verified tariff.

Runtime is Ollama 0.35.1, alias `gemma4:31b-cloud`, remote model `gemma4:31b`,
with alias digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
An alias digest does not establish immutable remote weights or seed determinism.

Verification passes Ruff, strict mypy over 173 files, all **28 focused tests**,
frontend formatting/lint/types, **11 frontend tests** and production build.
The full 732-test suite passed before the final validation safeguard below.
Twenty-eight new regression cases include invalid-link isolation, distinct
original IDs, preserved independent findings, redacted audit/failure evidence,
two persisted manuscript revisions, bounded structural retry and replay without
new calls. Final code review found that linked craft findings needed complete
field validation before removal from the canonical issues array. Six regression
cases reproduced that gap, then passed after the correction. The original tested
executor is archived with its frozen hash; the final executor's hash is recorded
separately. The correction changes no request or schema. All six captured
responses replay identically under it, including both failures, without any new
cloud calls. The full Python gates are repeated after this correction.

The first full run after that correction reports 737 passes and one worker
shutdown failure: `test_worker_cancels_active_call_and_restarts_only_unfinished_work[False]`
finds an invocation still marked running after shutdown. The worker group
reproduces it once (4 passed / 1 failed), then passes unchanged (5 passed).
An intervening diagnostic loading modified production modules from HEAD in
memory also passes the worker group. This is not a complete separate baseline
checkout or proof of causality. No worker code changes are made; the intermittent
shutdown behavior remains a reliability concern rather than being hidden by
rerunning tests. Unlike the earlier v40 transient, this captured failure does
not report a SQLite lock error.

The final full rerun again reports **737 passed / 1 failed** in 168.72 seconds,
with the same shutdown assertion. The full gate remains failed; no further
reroll is used to obtain a clean result. Resolving this worker cleanup failure
is the immediate offline stabilization target before more cloud probes or
merging this candidate. The critic follow-ups above remain queued separately.

Local evidence is under `data/diagnostics/linked-repair-v41-2026-10-09/`:
`experiment.py`, `plan.json`, `prepared/`, `annotated-replays.json`, full `live/`
requests/responses, `assess.py`, `assessment.json`, `assessment-final.json`,
`postcheck.json`, the archived tested executor and `worker-head-overlay.json`.
Private diagnostics remain
local. Canonical stories and sealed benchmarks are unchanged.

**The fixed diagnostic batch is complete. The implementation candidate's final
verification and Step 19 remain IN PROGRESS; Step 20 is NOT STARTED.**
