# v26 canary diagnosis and selective repairs

Date: 2026-09-08. Step 19 remains **IN PROGRESS**.

## Evidence

Source directories under `data/benchmarks/v0.1/`:

- `v23-canary-2026-09-04`: pinned report SHA-256
  `b8e1dcce97f8e41b1632482db841e9ec2d182f552a660a11666da347574f2a4a`.
- `v25-canary-2026-09-07`: pinned report SHA-256
  `7eed2294159d076fc6bdf69471d8d5c79ce0a686b55e0c62b18de1346451dc6f`.
- `v26-canary-2026-09-08`: report SHA-256
  `0987187583c1a0b4e75e8bb08eaca8825b94e71df2231718fc9cf6246e275af1`.

Reports, database invocation records, immutable drafts, and source-bound review
artifacts were inspected read-only. Approved Blueprint hashes and frozen case,
profile, and seed snapshots match. The inherited Local OH-V01-006 missing-beats
Blueprint failure is unchanged and excluded only from the runnable denominator.
The operator-confirmed dual-boot clock discrepancy remains environmental.

| Measure | v23 | v25 | v26 |
|---|---:|---:|---:|
| Runnable completions | 6/9 | 6/9 | 3/9 |
| Local completions | 2/5 | 2/5 | 0/5 |
| Cloud completions | 4/4 | 4/4 | 3/4 |
| Accepted scenes | 32/44 | 38/44 | 16/44 |
| Accepted Local scenes | 11/23 | 17/23 | 0/23 |

Only Cloud OH-V01-001, 003, and 004 completed v26. There were no new successes.
Local 001 and 004 and Cloud 002 lost their v25 completion. Every runnable Local
case stopped before accepting scene one; v25 Local 002/003 had accepted 3/4 scenes
respectively before their late Bible failures.

## Root causes

All nine initial writer prompts match v25. All five initial Local prose outputs
are byte-identical to v25. Cloud prose differs despite matching prompts, so the
Local causal comparison is more controlled than the Cloud comparison.

Five terminal failures (Local 001/002/004/005 and Cloud 002) exhausted critic
repair on `point_of_view_check.draft_evidence`. All nine runnable cases hit the
new viewpoint contract. Critic attempt validation fell from 51/51 in v25 to
24/47 in v26: 22 invalid exact-evidence responses and one applicability failure.
The other failed production attempt was a released-finding recurrence response.
All 24 failures were classified as application materialization, not transport.
Failed response bodies were not retained, so the exact malformed quotations
cannot be reconstructed from the response hashes alone.

Local 002's persisted critic explicitly said no prose change was needed while
creating a blocking assignment issue about its own metadata. Local 003 retained
both a likely false POV gate against the assigned investigator's own deductions
and a continuity allegation that drifted from an unapproved ratio to objections
against the approved prime-factorization relationship. The latter cited a hallway
fixture constraint while explaining a World Rule. Source identity was valid, but
the selected assertion did not substantiate that mathematical contradiction.

The terminal adjudicator ran zero times: the remaining critic blocker made
Local 003 ineligible. The continuity-only final message concealed the co-blocker.
Local 005 did identify a plausible genuine other-character private perspective,
so deleting all viewpoint protection would not be an acceptable fix.

No live Local Bible update was reached, so v26's fix for the two v25 late failures
was not tested by this canary. For the three Cloud successes common to v25/v26,
calls increased 70 to 81 and input tokens 616,881 to 740,648 (20.1%). Lower overall
consumption reflects early failures, not demonstrated efficiency. Human review is
pending; completion does not establish literary quality.

## Implemented selective repair

Developed on `codex/v26-production-contract`; new executions are graph v7 / prompt
v27 to preserve old evidence. `main`, v25, and historical canaries are not retagged.

1. Aligned viewpoint checks require no quote. Real breaches select current-draft
   evidence IDs, a typed violation, and a different subject character. Current
   prose is supplied once as an evidence catalog rather than duplicated.
2. Reviewer repair omits prior error prose and rejected values from critic input.
   The separate repair packet states that no manuscript defect has been
   established. Alternate raw assignment-issue routes are rejected.
3. Explicit approved-style guidance permits assigned-character interiority,
   inference, and free indirect narration. Assignment origin (explicit,
   single-character fallback, unassigned) is visible and not confused with a
   declared external-camera narrative mode.
4. Rechecks and adjudication receive an application-built first-allegation ledger
   with exact selected source assertions and scope. Source relevance and semantic
   incompatibility remain model judgments to measure, not guarantees inferred
   from successful schema validation. No new redundant certificate gate was added.
5. Successful viewpoint audits retain bounded diagnostics. Invalid evidence has
   a specific reason and bounded rejected/expected values. Terminal errors expose
   critic and continuity blockers plus why adjudication was skipped or completed.
6. Offline regression controls and opt-in isolated probes cover the corrected
   boundaries. The resolved-thread reducer, hard World Rules/requirements,
   bounded adjudication, profile routing, cancellation, and revision caps remain.

## Isolated test before another full canary

`benchmarks/v0.1/production-probes-v27.json` predeclares eight saved-input probes:
all five Local initial critics, Cloud 002's initial critic, and the first failing
v25 Local 002/003 Bible updates. These are **prepared, not live-run results**.

`scripts/production_probe.py inspect` compiles the current request and verifies
input hashes without contacting a model. `run` makes at most two sequential model
calls for one selected critic/Bible task and records exact request, schema,
version, inputs, usage, response hash, bounded failures, and validated output in a
new directory outside protected canary evidence. It never runs the writer or
production graph, writes canonical state, or fabricates canary/human scores.
Bible outputs also pass the real deterministic reducer in memory. Cloud requires
`--allow-cloud`; existing output directories cannot be reused or overwritten.

The operator should inspect both successful and failed semantic assessments:

- Recover critique response reliability without metadata-based story revisions.
- Do not hard-block Local 002 first-person interiority or Local 003's approved
  deductions merely for being internal.
- Preserve detection of a genuine unauthorized other-character perspective,
  including reviewing the approved style before judging Local 005.
- Verify both historical Bible failures preserve original resolved-thread lineage
  while accepting the new delta. Never invent a resolution to pass validation.
- Treat a validated critic response as a technical result, not proof its judgment
  is correct. These probes are not independent full canaries, nor fresh v25 reruns.

Only after these checks should a separately authorized clean 6-Local/4-Cloud
canary be staged. Compare against both pinned baselines, recover v25's six
completions and 38/44 scene coverage, and seek additional success without weakening
gates. Repeatability and blind quality evidence remain required for promotion.

## Verification status

Verification completed:

- Python Ruff lint and formatting: pass.
- Strict mypy: pass, 149 source files.
- Full pytest suite: 396 passed, including real persisted workflow tests and
  four protected probe integration tests with simulated providers.
- Frontend formatting, lint, and type checks: pass.
- Frontend tests: 11 passed.
- Production build: pass.
- All eight historical probe selections load and compile read-only with verified
  input hashes; both baseline comparisons and the v26 report digest are unchanged.
- `git diff --check`: pass.

No live probe or new canary has been launched. Semantic improvement remains to be
measured in the isolated live tests before another full canary is considered.
