# Formal Cloud-versus-baseline evaluation: execution

September 29, 2026. **Generation finished: 12/12 baselines and 11/12 agentic
Cloud stories completed.** Production accepted **64/65 planned scenes**. The
remaining story, OH-V01-012, failed the input-token budget check on its final
scene's critic call. No terminal case was rerun or replaced.

Cloud technical completion is **91.7%**, so the formal **at least 95% criterion
is not met**. The pooled 23/24 completion count must not replace the Cloud-arm
denominator.

**Human review completed September 30, 2026:** all eleven eligible randomized
pairs have submitted, validated human scores. Item 4's execution and review are
complete, and this campaign's reviewed evidence is sealed and verified.
**Product Step 19 remains IN PROGRESS**: technical completion, weighted quality
and agentic preference fall below their acceptance thresholds; cost is unknown
and independent repeatability work remains outstanding.

## Human review completed — 2026-09-30

- [x] Review all 11 eligible A/B pairs (OH-V01-001 through OH-V01-011).
- [x] Import the completed `public/review.csv` against the canonical packet.
- [x] Recompute acceptance using the actual human scores.
- [x] Seal and verify this campaign's reviewed evidence.

The user supplied all scores as `primary-reviewer`. The harness accepted eleven
comparisons with no ties; all seven hard gates passed for both candidates in
every reviewed pair. The failed Cloud case, OH-V01-012, remains in the technical
denominator and is excluded only from paired quality/preference scoring.

| Acceptance criterion | Observed result | Status |
| --- | --- | --- |
| Cloud technical completion at least 95% | 11/12, 91.7% | Not met |
| Severe-continuity-free rate at least 80% | 11/11 reviewed Cloud stories, 100% | Met |
| Mean weighted Cloud score at least 3.5 | 3.4818 | Not met |
| No Cloud dimension mean below 2.5 | Lowest mean: 3.0 | Met |
| Agentic preference at least 60% | 4/11, 36.4%; baseline preferred in 7/11 | Not met |
| Median Cloud cost at most $2 | No supported dollar-cost evidence | Unknown |

The weighted score is below 3.5 before rounding. Completing review does not
change the acceptance thresholds or turn a failed criterion into a pass.

This is one reviewer's assessment of one campaign. The user reported completing
the randomized grading before the assistant inspected the A/B identities on
September 30. The reviewer was also the operator; Blueprint approval was given
without editorial reading or edits. No independent reviewer is claimed. The
CSV notes are empty. In conversation, the user described the stories as good
first drafts, with remaining weaknesses in character depth, conflict, endings
and recurring prose patterns. Those comments are qualitative context, separate
from the submitted numeric scores.

The user's **22 manual story reviews are also complete** and now live in
[`docs/september_2026_manual_test_reviews`](../september_2026_manual_test_reviews/),
alongside the [review summary](../september_2026_manual_test_reviews/review-summary.md)
and [AI-pattern observations](../september_2026_manual_test_reviews/AI-patterns.md).
All 24 copied files match the proofread originals. These qualitative reviews
cover the September 12 and 13 manual runs and remain separate from the eleven
formal comparisons.

Offline import, summarization, sealing and verification made **zero model
calls**. All 123 frozen runtime/configuration files remained unchanged; database
integrity, foreign keys and recorded row counts passed verification. The
completed CSV and generation inputs retained their pre-import hashes.

The reviewed archive is `private/evidence.zip`, containing all 24 terminal case
results and eleven human comparisons. Its SHA-256 is
`47114e19760c5ad5b308251772e61e96147f5cdd41555d512d8b85265db6119c`;
the verified manifest SHA-256 is
`f390f93fca522d7a7dd5c1b8f3b2c8aa2b2a59560d7e8c381b2f9befe8705215`.
This seal establishes evidence integrity. Item 5 remains open for independent
repeatability; sealing this campaign does not establish a passing benchmark.

## Results across all phases

| Phase | Outcome | Calls | Failed calls | Input tokens | Output tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| Fresh Blueprint preparation | 12/12 prepared and explicitly approved | 74 | 2 | 197,928 | 77,883 |
| Direct baseline | 12/12 completed | 12 | 0 | 2,888 | 32,257 |
| Scene production | 11/12 completed; 64/65 scenes accepted | 296 | 6 | 2,982,456 | 247,854 |
| Entire campaign | 24 terminal case results | 382 | 8 | 3,183,272 | 357,994 |

Seven of the eight failed invocations recovered within existing automatic
allowances. One was terminal. Failed calls and the unfinished story remain in
the totals. The complete agentic arm, including preparation, used **370 calls,
3,180,384 input tokens and 325,737 output tokens**. Production-only accounting
must not be presented as the full cost of that arm. Dollar charges are unknown
for both arms; no zero-dollar estimate is treated as measured spend.

| Production batch | Stories completed | Scenes accepted | Calls / failed | Prose revisions | Elapsed |
| --- | --- | --- | --- | ---: | --- |
| 1: 001-004 | 4/4 | 22/22 | 97 / 0 | 3 | 12m 05s |
| 2: 005-008 | 4/4 | 21/21 | 99 / 3 | 4 | 11m 53s |
| 3: 009-012 | 3/4 | 21/22 | 100 / 3 | 4 | 9m 06s |

There were **11 prose revisions across 10 distinct scenes**, and zero formal
adjudication calls. Prose revisions are distinct from retries of invalid model
responses. All cases 001-011 completed; 012 is the sole terminal failure.
Per-case lineage, lengths, revisions and calls are retained in private diagnostics.

Elapsed values use persisted first-start to last-terminal timestamps per batch,
rounded to seconds; they include intra-batch workflow overhead. Baselines took
5m 18s, and Blueprint preparation took 6m 48s before the human checkpoint.
Production ran from 17:01:58 to 17:36:41 UTC (19:01:58-19:36:41 Belgrade), including
the gaps between batches. Two successful responses took about 203 seconds each:
one story-bible update and one critic response. Neither required interruption.

## Terminal failure: OH-V01-012

Five scenes were accepted. The writer also produced the sixth scene's draft,
but its critic call failed before an accepted critique was materialized:

- Invocation: `8913e116-86e1-4528-928d-a30cb810f9a6`.
- Provider-reported input: **27,542 tokens**, exceeding the unchanged **24,000**
  per-call cap by 3,542 tokens, approximately 14.8%.
- Provider-reported output: **523 tokens**. Both usage counts are persisted and
  included in the campaign totals.
- Invocation error: `budget_exceeded`; workflow error: `workflow_execution_failed`;
  benchmark result: `agentic_production_failed`.
- The adapter checks actual usage after receiving the provider response and marks
  this budget error non-retryable. No additional request was made for that task.

This was not a critic verdict rejecting the scene, revision exhaustion, a timeout,
or exhaustion of the story's total call allowance. The failed run used 23 of its
72 permitted calls and made no prose revision. The earlier invalid relationship
reference in a story-bible response had already recovered and was not the
terminal cause.

The request-composition diagnostic used `ceil(utf8_bytes/4)`, explicitly a
diagnostic estimate, and reported **21,995 estimated provider-input tokens**.
The serialized-message estimate was 23,269; the provider reported 27,542. Do not
mistake either byte-based estimate for the provider tokenizer or claim it is an
enforced pre-request token count.

| Request contribution | UTF-8 bytes | Diagnostic token estimate |
| --- | ---: | ---: |
| Artifact context | 64,635 | 16,159 |
| Inline schema | 10,727 | 2,682 |
| Control context | 8,428 | 2,107 |
| System instructions | 4,187 | 1,047 |
| Retry context | 2 | 1 |
| Gateway schema | 0 | 0 |

The component estimates are individually rounded; their sum can differ from the
aggregate estimate. Artifact context was the largest byte contribution. The
evidence identifies request sizing and token-estimate reliability as the next
engineering investigation, with the existing caps preserved. It does not isolate
which artifact subset can safely be reduced. No runtime fix was attempted during
this frozen campaign.

The six drafts and their reviews are preserved, with five accepted version IDs
explicitly identified. The sixth draft is partial evidence, not a completed
campaign manuscript. This case stays in the technical denominator and has no
eligible A/B pair, even though its baseline succeeded.

## Recovered failures and diagnostic limitations

Blueprint integration recovered twice, as detailed in the preparation report.
Production recovered five invalid responses:

- OH-V01-005: three continuity responses supplied missing or invalid exact draft
  references for scene-plan time-context coverage. All three recovered on a
  same-task retry. This repeats a validation pattern seen in the earlier v33 canary.
- OH-V01-009: one continuity response omitted a required finding summary, then
  recovered on retry.
- OH-V01-012: one story-bible response used an unknown relationship-state ID,
  then recovered on retry.

The raw invocations, exact task fingerprints, input artifact references and
validation evidence are retained. Successful recovery does not establish that
the model's substantive criticism was correct; that needs separate examination.

The terminal budget invocation has `latency_ms = null`, although its start/end
timestamps and provider token counts are available. The failed workflow also has
`completed_at = null`; its last update and terminal invocation timestamps establish
the end of this attempt. Batch 3 timing uses that workflow's terminal update.
Summed recorded provider latency therefore omits the budget-failed call's duration;
it must not be presented as a complete wall-clock measure. These are preserved
metadata limitations, not values silently filled into the database.

## Scope and approval

Campaign `042918c2-8a50-49fd-831b-c1a93553d4f6` follows the
[frozen setup](step-19-formal-cloud-v33-setup-2026-09-29.md) and
[fresh Blueprint preparation](step-19-formal-cloud-v33-blueprints-2026-09-29.md).
All calls use `gemma4:31b-cloud` through the existing Ollama service. Production
uses prompt v33 / graph v9; no runtime source, model settings, prompts, budgets
or retry allowances have changed.

The user explicitly approved all twelve versions in packet
`2027946824d2245f821bedb1f1b7b80dc3bbae9e0f7a85e7c0a7e965fbab0447`:
"I approve these blueprints." The choice was **approval as generated, without
editorial review or edits**, to observe autonomous production. The import wrote
twelve durable human decisions and made zero model calls. It is not a claim of
artifact fidelity or a human story-quality score.

The original blank CSV is preserved alongside the completed form and separate
authorization/import receipts. Checkpoint-time documents remain historical
snapshots, so their zero-approval counts are not current execution status.

The baseline uses one direct generation per frozen premise, without agentic
artifacts. The Cloud arm includes fresh Blueprint preparation and subsequent
scene production. Baseline and production ran consecutively on the same provider;
generation order was not randomized. Equal intended story length does not imply
equal computation. Report whole-arm accounting separately from production-only
accounting, including failed calls in both relevant totals.

## Evidence and review separation

All runtime evidence is under
`data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/`. The campaign database/report
are authoritative live state; the original preflight and hashes are immutable
setup receipts. Timestamped phase logs preserve the commands' outcomes.

The twelve approved scene plans contain 65 scenes in total. Existing bounds
allow up to 780 production calls across those plans, with two revision cycles
per scene. The configured $5-per-production-run amount is unchanged; it is not
a verified provider-spend cap. Ollama Cloud dollar-cost evidence remains unknown.

Private diagnostics retain exact per-case results, invocation metadata,
artifact versions, reviewer findings and failure evidence. Do not consult private
outputs, arm-specific word counts or the answer key before scoring the randomized
A/B packet if preserving label blinding. The reviewer-facing packet contains
only the frozen requirements and anonymized candidate texts under the canonical
rubric; the user's 22 earlier manual reviews remain a separate evidence set.

Generated evidence includes:

- `summary.json`: canonical acceptance summary with eleven human reviews and the
  criterion outcomes recorded above.
- `public/guide.md`, `public/packet.json`, `public/review.csv`: **11 randomized
  comparisons** for 001-011, with the completed human review form.
- `public/reviews.json`: validated, packet-bound import of those human scores.
- `private/review.blank.csv` and `private/generation-summary.json`: preserved
  blank review form and original zero-human-review generation summary.
- `private/human-review-input-hashes-2026-09-30.json`: pre-import hashes of the
  completed review CSV, public packet, campaign report and campaign plan.
- `private/answer-key.json` and `private/review.key`: private label mappings and
  randomization material, excluded from the public packet.
- `private/technical-results.json`: phase/batch/per-case accounting and lineage.
- `private/diagnostics/*-cloud.json` and `*-baseline.json`: all 24 case dossiers,
  containing invocation records, events and exact artifact versions.
- `private/diagnostics/partial-story-evidence.json` and `budget-failure.json`:
  focused evidence for the incomplete story and the terminal budget call.
- `private/completed-snapshot.db`: audited SQLite snapshot after all attempts.
- `private/*-completed-report.json`: baseline and batch-end report snapshots.
- `private/generation-evidence-manifest.json`: hashes of the captured generation
  evidence, including the then-blank review form; this remains a historical
  receipt rather than the later reviewed-evidence seal.
- `private/evidence.zip`: sealed reviewed campaign, verified September 30.

The canonical public bundle SHA-256 is
`e1875930d2a495041a2dc226dd14439515eb03f3b8e76cd996c4275885000681`.
The final campaign-report file SHA-256 is
`760b0ec3d503a2bf80ad87112c0ec4dd0694ff5cb0e344c156a2899ebf9968bb`.

All 24 expected case IDs have terminal results. Verification checked **622 artifact
version hashes**, exact approved Blueprint lineage, assembly of each completed
Cloud manuscript from its accepted scene versions, invocation/token accounting,
unchanged production budgets and versions, SQLite integrity and foreign keys.
The database secret-export audit passed. The final dataset has twelve human
approval decisions and no run-control interventions. The public packet contains
exactly the eleven eligible prompts; its private mapping digest and original
blank review form were validated at packaging. No model scores were substituted for human
review. The offline evidence helpers passed Ruff lint and formatting checks.

Technical completion does not establish literary quality or correct criticism.
Formal human scores are now recorded. Supported cost evidence, item 5's independent
repeatability work and the failed acceptance criteria remain unresolved. No fresh
repeat or prompt-tuning phase has been launched.
