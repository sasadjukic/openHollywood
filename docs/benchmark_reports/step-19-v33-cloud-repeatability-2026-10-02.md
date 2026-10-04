# v33 Cloud repeatability: protocol and evidence register

Prepared 2026-10-02; assessment completed 2026-10-04. **Item 5 is COMPLETE as an
executed, reviewed and sealed repeatability assessment. Product Step 19 remains
IN PROGRESS.** The protocol below was declared before the first new model call.
The September 29 campaign remains a historical reference and does not count as
one of the three prospective repeats.

**Final checkpoint — 2026-10-04:** all three campaigns and **34 eligible human
comparisons** are reviewed, sealed and independently verified. Cloud completed
**12/12, 12/12 and 10/12** stories; all **36 baselines** completed. Cloud's weighted
means are **4.05, 4.1167 and 4.16**; preference rates are **54.17%, 37.5% and 45%**.
No repeat meets the unchanged 60% preference criterion, repeat 3 misses technical
acceptance, and cost remains unknown. Repeat 3 retains its authorized **Ollama
0.35.1** exception to the original **0.35.0** freeze. Repeated acceptance has not
been demonstrated. See the [consolidated assessment](#consolidated-three-repeat-assessment--2026-10-04)
and [reviewer observations](#reviewer-observations-and-implications--2026-10-04).
Earlier dated entries below retain their historical checkpoint context.

## Fixed scope and endpoint

Run **three independent fresh Cloud-first campaigns**, each covering all twelve
frozen OH-V01 premises in both the agentic Cloud and direct-model baseline arms.
This is 36 agentic attempts plus 36 baseline attempts, with up to 36 eligible
human A/B comparisons. Handle one campaign at a time. Each campaign has a fresh
identity, database, Blueprint set, approvals, baseline generations and production
history. No completed story, approved Blueprint or checkpoint is copied into it.

After three campaigns and human review, summarize and seal the observed result.
Do not add repeats to obtain a favorable outcome, replace terminal failures, or
select the best manuscript from several attempts. Environmental interruptions
remain in raw accounting; durable recovery within the same campaign is not a
new repeat. A recurring blocker or environment drift can pause the sequence for
investigation, with incomplete coverage reported explicitly.

This is repeated execution on a fixed small corpus and model configuration. It
can describe consistency across these attempts; it does not establish population
reliability, independent remote weights or a general guarantee of literary quality.

## Frozen conditions

- Model: `gemma4:31b-cloud`, provider-reported `gemma4:31b`, through the existing
  local Ollama service, for both arms and every specialist role.
- Production prompt v33 / graph v9; Blueprint prompt v9 / graph v4; baseline
  prompt v1 / workflow v2; dialogue subgraph v2.
- Original twelve corpus prompts, versions, constraints and per-prompt seeds.
- Unchanged model settings, context limits, output limits, structured-response
  repair, revision allowances, graph budgets and 900-second transport timeout.
- Sequential cases, direct baselines followed by three four-case production
  batches (001–004, 005–008, 009–012), matching the reference generation order.
- Runtime file hashes, full model/profile snapshots, host/runtime metadata and
  provider alias metadata checked before generation. Remote weights and actual
  seed enforcement are not independently pinned. Provider metadata drift must
  be recorded and resolved before a run is treated as matching the series.

Fresh Blueprints stop at the mandatory human approval checkpoint. The prior
evaluation used approval as generated without editorial reading or edits; retain
that method if the user approves the new exact versions. No previous approval
authorizes these new versions. Any requested edits or actual plot exposure must
be recorded and reflected in comparability and review limitations.

At setup, Ollama is **0.35.0**, compared with **0.34.4** in the historical
reference. All three prospective campaigns are pinned to 0.35.0. The Cloud alias
digest is unchanged (`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`).
This environment difference qualifies comparisons with September 29; it is not
attributed to a prompt or workflow change. The setup commit is
`acf97b8087370acb713857e568e59a1722039bbc`; its 123 frozen runtime/configuration
files must match the reference before launch.

## Budgets and human review

Each campaign retains the existing configured ceilings: twelve Blueprint runs
at $0.50, twelve baseline calls at $2 and twelve production runs at $5. The
configured amounts sum to $90 per campaign and $270 for the series. They are
accounting settings, **not measured charges or verified provider-spend caps**;
Ollama Cloud supplies no supported per-call dollar evidence. Cost acceptance
therefore remains unknown unless supported evidence becomes available.

The maximum first-pass allowance is 1,308 calls per campaign, or 3,924 across
three campaigns, including up to eight scenes and existing bounded repairs.
These are upper bounds, not expected usage. The reference used 382 calls. The
first phase starts only repeat 1's Blueprint preparation (at most 144 calls).
No terminal-case retry or budget increase is authorized by this protocol.

Package every eligible pair with a fresh private blinding key per campaign.
Keep provenance, diagnostics and answer keys separate from reviewer-facing
texts. Every pair needs real human scores using the existing rubric, hard gates
and preference form; previous reviews and automated opinions cannot fill them.
Use the same reviewer and approval method where possible, and record actual
exposure to Blueprints, prior stories or labels. Familiarity with the frozen
premises and one-reviewer coverage limit claims about blinding and generality.

## Assessment and sealing

Report each campaign separately before any pooled totals. For each of the twelve
prompts, show all three Cloud outcomes, accepted/planned scenes, recovered and
terminal failures, revisions, adjudication, token usage, elapsed time, cost
coverage, output identity and human results. Pay particular attention to the
reference OH-V01-012 request-size failure and recovered continuity-response
errors; preserve their exact inputs and failure evidence if they recur.

Apply the existing criteria to each campaign without changes:

| Criterion | Threshold |
| --- | --- |
| Cloud technical completion | At least 95%; requires 12/12 within each campaign |
| Severe-continuity-free human assessments | At least 80% of reviewed Cloud stories |
| Mean weighted Cloud score | At least 3.5, before rounding |
| Lowest Cloud dimension mean | At least 2.5 |
| Agentic preference | At least 60% of eligible comparisons |
| Median Cloud cost | At most $2, only with complete supported cost evidence |

Preserve failed cases in all technical denominators, even where only one arm
produces a reviewable story. Report missing paired coverage, ties, hard-gate
failures and any per-case regression alongside averages. Pooled totals across
36 attempts are supplementary and cannot hide a failed campaign or establish
independence among repeated premises. Report spread across campaigns and exact
case outcomes; do not invent a new statistical pass threshold after seeing them.

Distinguish **completed repeatability assessment** from **repeatable acceptance**.
The former requires all three planned campaigns, actual review of every eligible
pair, verified individual seals and a consolidated evidence register. The latter
requires the existing criteria to be met consistently across those campaigns;
an unknown criterion remains unresolved. Step 19 stays open wherever acceptance
or cost qualification remains unmet, even if item 5's assessment is finished.

After review, use the existing canonical import, summary, seal and independent
verification commands for each campaign. Preserve the original CSV and packet
digests, generation summaries, failed attempts and archive hashes. Hash the
consolidated register against those individual seals. No runtime or writing-tic
change is included in this series.

## Evidence locations and execution status

The series register and setup receipts are local under
`data/benchmarks/v0.1/v33-cloud-repeatability-2026-10-02/`.

| Repeat | Local campaign directory | Initial status |
| --- | --- | --- |
| 1 | `data/benchmarks/v0.1/formal-cloud-v33-repeat-1-2026-10-02/` | Empty database prepared; generation not launched at protocol freeze |
| 2 | `data/benchmarks/v0.1/formal-cloud-v33-repeat-2-2026-10-02/` | Empty database prepared; generation not launched |
| 3 | `data/benchmarks/v0.1/formal-cloud-v33-repeat-3-2026-10-02/` | Empty database prepared; generation not launched |

| Repeat | Campaign ID | Canonical plan SHA-256 |
| --- | --- | --- |
| 1 | `c2d73024-80f4-4edd-aa8e-084620e5ec06` | `a879a128c9c4a958d7d00fb73607c7b41887cec0e01c56ceba097f1c1dc7227a` |
| 2 | `8967ce6a-d0d9-4ab8-b3c3-d42d825fa2db` | `460dd77b6143994b5985599ee67db0a2b5651d1b4dff7190182ac02558907b1d` |
| 3 | `11ea6cf8-ceaa-475d-943f-c871649fb2b9` | `e94d2255b4a11a42c328dc8450330c8b5b73226e8579660ee07eb050660021f9` |

`series.json` binds the three identities, input equivalence, reference evidence
hashes and operator helpers. `protocol-at-freeze.md` preserves this protocol's
pre-generation text while this tracked report can receive dated status updates.

Each directory has a phased `run-campaign.ps1`. Its default `Verify` phase makes
no inference calls. Run `PrepareBlueprints`, then `PackageBlueprints` and record
the checkpoint before obtaining the user's exact-version approval. Subsequent
phases are `ApproveBlueprints`, `RunBaseline`, `RunProduction` for batches 1–3,
`Summarize`, `PackageBlindReview`, then, after actual human scoring,
`ImportReviews`, `SummarizeReviewed` and `Seal`.

Reference documents: [formal execution and review](step-19-formal-cloud-v33-execution-2026-09-29.md),
[formal setup](step-19-formal-cloud-v33-setup-2026-09-29.md),
[scoped-campaign contract](../adr/0016-scoped-benchmark-campaigns.md), and
[cost-evidence contract](../adr/0017-evidence-based-cost-acceptance.md).

## Repeat 1 Blueprint checkpoint — 2026-10-02

The first generation phase completed successfully and stopped at the required
human approval boundary. The twelve new Blueprints have been packaged with exact
version IDs and content hashes. This is preparation success, not completed-story
or human-quality evidence.

| Measure | Result |
| --- | --- |
| Blueprints awaiting approval | 12/12 |
| Terminal preparation failures | 0 |
| Model calls | 74: 72 succeeded, 2 failed and recovered automatically |
| Recorded input tokens | 189,277 |
| Recorded output tokens | 71,889 |
| First workflow start | 06:50:28 UTC / 08:50:28 Europe/Belgrade |
| Last workflow pause | 06:57:45 UTC / 08:57:45 Europe/Belgrade |
| Elapsed preparation | 437.646 seconds, about 7m 18s |
| Persisted human decisions | 0; approval form remains blank |
| Baseline / production runs | 0 / 0 |

Both failed calls belonged to OH-V01-003: `world_builder` and
`character_architect` received **HTTP 502 / provider_unavailable** during parallel
specialist execution. Each recovered within the existing allowance. These were
service failures, not invalid structured responses or rejected story content.
Their persisted token fields are zero because the failed requests returned no
usage; those values do not establish that the provider performed no work. Token
totals above cover recorded usage, and dollar-cost acceptance remains unknown.

The canonical Blueprint packet SHA-256 is
`a43b8d3c2ad0a210566104642f17e9aa12876a8515359c55fbd05a1838bf1b7c`.
Under repeat 1's local directory:

- `blueprints/approval-manifest.md` identifies the exact twelve versions without
  exposing plots, supporting the user's existing approval-as-generated method.
- `blueprints/packet.json`, `guide.md` and `approvals.csv` retain the full canonical
  packet, optional editorial dossier and blank approval form.
- `blueprint-generation-authorization.json` binds the user's start request to
  this campaign and the frozen series register; it grants no Blueprint approval.
- `blueprint-checkpoint.json` preserves all case/run/version identities, the
  failed calls, timing, usage and checkpoint-file hashes.
- `private/blueprint-evidence-verification.json` records the offline audit.
- `private/blueprint-snapshot.db` preserves the database at this boundary; its
  SHA-256 is `c80632b45aa5ea2f6a548c1a2b5c4582a1fa24ec721b5d50c8d99ea901dc7800`.

Verification recomputed all **155 artifact content hashes**, validated the twelve
Blueprint/critique packet references and canonical blank form, checked SQLite
integrity and foreign keys, and passed the database secret-export audit. All
123 runtime hashes and frozen operator helpers remain unchanged. Repeats 2 and
3 still have zero projects, workflows, invocations and human decisions. The
reference inputs, reviewed scores and sealed archive retain their original hashes.

Helper Ruff lint/format checks, PowerShell parsing, documentation links and
whitespace checks passed. No application runtime code changed, so the application
regression/build suite was not rerun for this evidence-only work.

Next: obtain approval for the exact repeat-1 packet, import the decisions, then
run its twelve baselines and three production batches under the frozen settings.
Formal human scoring and evidence sealing remain future phases for every repeat.

## Repeat 1 approval and generation — 2026-10-02

The user explicitly approved the presented exact set: "I approve 12 blueprints
as generated". Import verification at **07:05:01 UTC / 09:05:01 Europe/Belgrade**
confirmed twelve durable human decisions and zero added model calls. The original blank
form is preserved as `blueprints/approvals.blank.csv`; authorization and import
receipts bind the decisions to packet
`a43b8d3c2ad0a210566104642f17e9aa12876a8515359c55fbd05a1838bf1b7c`.
This is approval for autonomous production, not a human literary score.

Generation started at 07:05:08 UTC, with the direct baseline arm first. The
sequential runner then executes production batches 001–004, 005–008 and 009–012,
preserving a campaign-report snapshot after each phase. It neither retries
terminal cases nor imports human scores or seals unreviewed results. Frozen
verification runs before every model-executing phase.

## Repeat 1 generation results — 2026-10-02

**All 24 planned cases completed.** Cloud technical completion is **12/12, 100%**,
meeting this campaign's at-least-95% criterion. The original generation summary
retains zero human reviews and five then-unresolved quality/preference/cost criteria. The
repeat's successful completion is evidence for the prospective series; neither
repeatability nor literary quality is concluded from this attempt alone.

| Phase | Outcome | Calls | Failed calls | Recorded input tokens | Recorded output tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| Blueprint preparation | 12 prepared; all subsequently approved as generated | 74 | 2 | 189,277 | 71,889 |
| Direct baseline | 12/12 completed | 12 | 0 | 2,888 | 32,881 |
| Scene production | 12/12 completed; 64/64 scenes | 290 | 1 | 2,923,952 | 244,220 |
| Entire campaign | 24 terminal successes | 376 | 3 | 3,116,117 | 348,990 |

The complete agentic arm used **364 calls, 3,113,229 recorded input tokens and
316,109 recorded output tokens**, including Blueprint preparation and recovered
failures. All three failed invocations recovered; no terminal case was rerun.
The two HTTP 502 responses returned no usage, so recorded zero tokens for those
calls do not establish zero provider work. No dollar-cost pass is inferred.

| Production batch | Stories | Scenes | Calls / failed | Prose revisions | Elapsed |
| --- | --- | --- | --- | ---: | --- |
| 1: 001–004 | 4/4 | 21/21 | 91 / 1 | 2 | 6m 06s |
| 2: 005–008 | 4/4 | 21/21 | 102 / 0 | 6 | 7m 30s |
| 3: 009–012 | 4/4 | 22/22 | 97 / 0 | 3 | 6m 51s |

Elapsed batch values use persisted first-start and last-completion timestamps,
rounded to seconds. Baselines ran **07:05:12–07:08:20 UTC**, about 3m 09s.
Production ran **07:08:25–07:29:01 UTC** (09:08:25–09:29:01 Europe/Belgrade),
about 20m 36s including inter-batch gaps. Blueprint preparation duration remains
the earlier 7m 18s to the approval pause; the later approval wait is not model
generation time. No recorded invocation latency exceeded 60 seconds.

There were **11 prose revisions across 11 distinct scenes**, all within existing
allowances, and zero adjudication calls. Revision counts are separate from
retries of unsuccessful model requests. Completion does not certify the
correctness of substantive critic or continuity judgments.

### Recovered errors and the prior request-size failure

- OH-V01-003, Blueprint preparation: `world_builder` and `character_architect`
  each received HTTP 502 / `provider_unavailable`. Both recovered on the same
  task within the existing allowance.
- OH-V01-002, production: `continuity_supervisor` supplied an invalid exact-draft
  evidence reference for `requirement_coverage.required_element_1`. Application
  materialization rejected it with `schema_validation_failed`; the same-task
  retry succeeded. The original invocation, request inputs and failure evidence
  are preserved. This remains a structured-response reliability issue.
- OH-V01-012 completed all six scenes. Its final critic request used **23,515
  input tokens**, below the unchanged **24,000** cap by only **485 tokens**.
  This was also the largest production input in this campaign. September's
  27,542-token failure did not recur, but the narrow remaining margin does not
  establish that request sizing is solved.

The September reference completed 11/12 Cloud stories and accepted 64/65 scenes;
this repeat completed 12/12 and accepted 64/64. Fresh Blueprints can change the
planned work, and Ollama changed from 0.34.4 to 0.35.0. Preserve those differences
when comparing outcomes; this is not a controlled claim of a runtime improvement
or an equal-work speed comparison.

### Human review packet and preserved evidence

At generation close, all **12 eligible pairs** were in repeat 1's `public/guide.md`
and `public/packet.json`, with a canonical blank `public/review.csv`. The public bundle SHA-256 is
`8979ce12f2c3dcea3b7c712f56c8dbdf20b817c1a6c68a2bfc57392736f77806`.
The randomized candidates were supplied for scoring before private provenance or
answer-key inspection. Human scoring was pending at that checkpoint; the completed
review and seal are recorded below.

Private evidence includes all 24 case dossiers, exact artifacts and invocations,
phase report snapshots, `technical-results.json`, `completed-snapshot.db`, the
original blank review form, generation summary and blind-package verification.
`generation-evidence-manifest.json` binds 81 files by SHA-256 and byte length at
generation close. It is a generation receipt, **not the reviewed formal seal**.
The eventual human-edited CSV will differ from its preserved blank version.

Verification checked **620 artifact content hashes**, all twelve exact approval
lineages, manuscript assembly from accepted scene versions, complete call/token
accounting, unchanged budgets/versions, SQLite integrity and foreign keys, and
the database secret-export audit. Automated blind-package reconstruction matched
both the public packet and its separately stored mapping without printing labels
or story content. The blank scoring form matches the canonical rendering.

All reference inputs and the September reviewed seal retain their hashes; all
123 runtime files and the frozen operator helpers are unchanged. Repeats 2 and
3 still had empty story-state tables at generation close. Review import, reviewed
summaries and formal sealing awaited actual human scores at that checkpoint.

## Repeat 1 human review and seal — 2026-10-02

The user completed all **12 comparisons / 24 candidate assessments**. The
canonical parser validated all packet/campaign/comparison identities, complete
coverage exactly once, all 192 dimension values, 168 hard-gate values and twelve
preferences. Scores use 3 and 5 only, all gates are true, and all optional notes
are empty. No invalid values, missing required cells or free-text spelling errors
were found. The submitted CSV was preserved byte for byte; no subjective score
or preference was changed. A stated preference between equally scored candidates
is valid: the rubric's discrete scores do not encode every comparative judgment.

### Reviewer calibration addendum

The reviewer clarified two interpretations with this submission:

- **Originality and specificity:** assess the generated text given the supplied
  premise, rather than judging whether the fixed premise itself is novel.
- **Dialogue:** assess the canonical qualities with less reliance on personal
  stylistic preference; occasional overlength can be a minor editing issue when
  the dialogue otherwise satisfies the published anchor.

This does not change the rubric, weights, 1–5 anchors, hard gates or acceptance
thresholds, and does not make length irrelevant to pacing or dialogue quality.
Carry this interpretation consistently into repeats 2 and 3. It differs from the
reviewer's September reference calibration, so the higher numeric scores cannot
be attributed to an engineering improvement. Do not pool historical and current
literary scores as identically calibrated evidence. Preserve both submissions.
The unchanged runtime and disclosed Ollama-version difference remain relevant.

`reviewer-calibration-2026-10-02.json` in the series directory is a dated addendum;
it does not replace `series.json` or `protocol-at-freeze.md`. Its SHA-256 is
`6de15ae37bb8e47561e3707ade333d5073f045cb54a69c789d3171a1c61c4032`.
The review verification receipt binds this addendum, the original CSV and the
verified seal. The addendum is external metadata, not a canonical archive member.

### Results using the unchanged criteria

| Criterion | Repeat 1 result | Status |
| --- | --- | --- |
| Cloud technical completion ≥95% | 12/12, 100% | Pass |
| Severe-continuity-free human assessments ≥80% | 12/12, 100% | Pass |
| Mean weighted Cloud score ≥3.5 | 4.05/5 | Pass |
| Lowest Cloud dimension mean ≥2.5 | 3.0 | Pass |
| Cloud preference ≥60% | (5 wins + 0.5 × 3 ties) / 12 = 54.1667% | Not met |
| Median Cloud cost ≤$2 | 0/12 cases have supported complete dollar cost | Unknown |

Cloud won five comparisons, baseline won four, and three were ties. Ties retain
the canonical half-credit rule and stay in the denominator. The baseline mean
weighted score is **4.15**, versus **4.05** for Cloud. All 24 candidates pass every
human hard gate. Neither the one-win preference difference nor these descriptive
averages establish a general quality advantage. This is one reviewer scoring
repeated familiar premises, not twelve independent reviewers.

| Dimension | Cloud mean | Baseline mean |
| --- | ---: | ---: |
| Causal coherence and structure | 5.0000 | 5.0000 |
| Character depth and consistency | 3.0000 | 3.3333 |
| Dialogue | 4.1667 | 4.3333 |
| Originality and specificity | 3.8333 | 4.0000 |
| Voice and prose quality | 3.0000 | 3.0000 |
| Emotional and thematic impact | 3.5000 | 3.5000 |
| Pacing and tension | 5.0000 | 5.0000 |
| Continuity and constraint adherence | 5.0000 | 5.0000 |

Character depth and voice/prose remain the lowest Cloud dimensions. These scores
are consistent with the user's earlier concerns; they do not identify a causal
defect or justify changing the frozen series mid-run.

| Prompt | Cloud weighted | Baseline weighted | Preference |
| --- | ---: | ---: | --- |
| OH-V01-001 | 4.50 | 4.30 | Cloud |
| OH-V01-002 | 4.00 | 4.50 | Baseline |
| OH-V01-003 | 4.00 | 4.00 | Cloud |
| OH-V01-004 | 3.70 | 3.70 | Cloud |
| OH-V01-005 | 4.00 | 4.00 | Tie |
| OH-V01-006 | 3.70 | 3.70 | Tie |
| OH-V01-007 | 4.50 | 4.50 | Cloud |
| OH-V01-008 | 4.50 | 4.80 | Baseline |
| OH-V01-009 | 4.00 | 3.70 | Cloud |
| OH-V01-010 | 4.00 | 4.00 | Tie |
| OH-V01-011 | 4.00 | 4.60 | Baseline |
| OH-V01-012 | 3.70 | 4.00 | Baseline |

### Reviewed evidence preservation

Canonical import, summary, sealing and independent archive verification passed
with **zero additional model calls**. All 123 frozen runtime hashes still match.
The campaign database remains at 24 projects, 36 workflows, 376 invocations and
12 human Blueprint decisions. The original blank form, generation summary,
81-file generation receipt and completed database snapshot remain preserved.
The older generation receipt binds the then-blank CSV and pre-review summary;
their expected later changes do not invalidate its historical meaning.

Under repeat 1's directory:

- `private/human-review-input-hashes-2026-10-02.json` preserves input digests and
  CSV validation; `public/reviews.json` is the canonical imported review.
- `summary.json` is the reviewed canonical summary.
- `private/human-review-verification.json` records per-case and per-dimension
  results, unchanged input hashes, database counts and calibration/seal binding.
- `private/evidence.zip` is the canonical reviewed archive. SHA-256:
  `0d5611771cd993023338039ebb76becea719900f5e9519ae89e8fb63d15ed43d`.
- Canonical archive manifest SHA-256:
  `f4391c6ff2778beaa5b5ab53fbe04b07dc4acccf9c9fd2ece2572c6d9ae7abe7`.
- Submitted CSV SHA-256:
  `4fb18463e4e4ba2d5b65c3cc25cf1a78d9ae95dea874abd82e1713a44677f58e`.

Repeat 1 is complete as an executed, reviewed and sealed evaluation. Its
preference criterion is not met and its cost criterion is unresolved. **Item 5
and Product Step 19 remain IN PROGRESS.** Repeat 2 preparation is the next
predeclared campaign; no extra attempt has been added to seek a passing result.

## Repeat 2 Blueprint checkpoint — 2026-10-02

After the submitted repeat-1 reviews passed validation, the user's instruction
to continue authorized preparation of the next predeclared campaign. Empty-state,
frozen-runtime, operator-helper and provider checks passed first. The twelve
fresh Blueprints are now paused at the mandatory human checkpoint. Repeat-1
approval does not approve this new set. No baseline or production has started.

| Measure | Result |
| --- | --- |
| Blueprints awaiting approval | 12/12 |
| Terminal preparation failures | 0 |
| Model calls | 73: 72 succeeded, 1 failed and recovered automatically |
| Recorded input tokens | 195,649 |
| Recorded output tokens | 75,262 |
| First workflow start | 15:04:58 UTC / 17:04:58 Europe/Belgrade |
| Last workflow pause | 15:12:59 UTC / 17:12:59 Europe/Belgrade |
| Elapsed preparation | 480.882 seconds, about 8m 01s |
| Human decisions / baseline runs / production runs | 0 / 0 / 0 |

OH-V01-012's first `blueprint_integrator` response omitted required
`scene_number` values at `scene_plans.1` through `scene_plans.5`. Structured
validation rejected it with `schema_validation_failed`, including a downstream
minimum-valid-scene-count error. Its provider finish reason was `stop`. The
same task recovered within the existing bounded repair allowance; no terminal
case was rerun. The rejected call recorded 4,992 input and 2,909 output tokens,
which remain in the totals. This is a structured-output preparation failure,
separate from the historical production critic request-size failure. Dollar
cost remains unknown.

The canonical packet SHA-256 is
`86888a4837922cd88eac4c537c9f30cd3b784048367f214929940306d6a5be87`.
Under repeat 2's local directory:

- `blueprints/approval-manifest.md` identifies the twelve exact versions and
  content hashes without exposing the generated plots.
- `blueprints/packet.json`, `guide.md` and `approvals.csv` retain the full packet,
  optional editorial dossier and still-blank canonical approval form.
- `blueprint-generation-authorization.json` binds the start authorization to the
  series, repeat-1 reviewed seal and dated reviewer calibration.
- `blueprint-checkpoint.json` retains case/run/version identities, invocation
  failures, timing, recorded usage and checkpoint hashes.
- `private/blueprint-evidence-verification.json` records the offline audit.
- `private/blueprint-snapshot.db` preserves the exact database at this boundary;
  SHA-256: `f35b6e3ce3d203f46f6a7d4bb73b0abc0801fabd3e52e73c44486dd3a3ccfac0`.

Verification checked all **161 artifact content hashes**, exact packet references
and canonical blank form, SQLite integrity and foreign keys, and the database
secret-export audit. All 123 frozen runtime hashes and original operator helpers
remain unchanged. The September reference, repeat-1 scores, reviewed seal and
completed snapshot retain their hashes. Repeat 3 still has zero story-state rows.
No model call remains running. Helper Ruff lint/format checks and documentation
link/whitespace checks passed; no application runtime changed, so the application
regression/build suite was not rerun for this evidence-only work.

Next: obtain the user's approval of this exact repeat-2 set, import its twelve
decisions, then run the twelve baselines and three production batches using the
same frozen configuration. **Item 5 and Product Step 19 remain IN PROGRESS.**

## Repeat 2 approval and generation — 2026-10-02

The user approved the exact new set: "I approve all 12 blueprints for Repeat 2".
Import verification at **15:17:36 UTC / 17:17:36 Europe/Belgrade** confirmed
twelve durable human decisions, twelve successful Blueprint workflows and zero
model calls added by import. The preserved blank form, completed form and
authorization/import receipts bind approval to packet
`86888a4837922cd88eac4c537c9f30cd3b784048367f214929940306d6a5be87`.

Baseline generation started at 15:17:36 UTC, followed by the declared sequential
production batches 001–004, 005–008 and 009–012. Each phase verifies the frozen
configuration and preserves a terminal-report snapshot. No terminal case is
rerun and no reviewed seal will be created before the new human scores arrive.

## Repeat 2 generation results — 2026-10-02

**All 24 planned cases completed successfully.** Cloud technical completion is
**12/12, 100%**, meeting this campaign's at-least-95% criterion. The canonical
summary has zero human reviews; all five quality/preference/cost criteria remain
unresolved. No terminal case was retried or replaced.

| Phase | Outcome | Calls | Failed calls | Recorded input tokens | Recorded output tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| Blueprint preparation | 12 prepared and subsequently approved | 73 | 1 | 195,649 | 75,262 |
| Direct baseline | 12/12 completed | 12 | 0 | 2,888 | 30,960 |
| Scene production | 12/12 completed; 64/64 scenes | 283 | 3 | 2,833,701 | 233,880 |
| Entire campaign | 24 terminal successes | 368 | 4 | 3,032,238 | 340,102 |

All four failed invocations recovered on the same task within the frozen
allowances. The complete agentic arm, including Blueprint preparation, used
**356 calls, 3,029,350 input tokens and 309,142 output tokens**. Cost remains
unknown for every case; recorded token counts do not establish a dollar-cost pass.

| Production batch | Stories | Scenes | Calls / failed | Prose revisions | Elapsed |
| --- | --- | --- | --- | ---: | --- |
| 1: 001–004 | 4/4 | 21/21 | 94 / 1 | 3 | 7m 36s |
| 2: 005–008 | 4/4 | 21/21 | 97 / 1 | 4 | 7m 13s |
| 3: 009–012 | 4/4 | 22/22 | 92 / 1 | 1 | 7m 41s |

Durations use persisted workflow timestamps, rounded to seconds. Baselines ran
**15:17:40–15:20:18 UTC**, about 2m 38s. Production ran
**15:20:22–15:43:08 UTC** (17:20:22–17:43:08 Europe/Belgrade), about **22m 46s**
including inter-batch gaps. Blueprint preparation took the earlier 8m 01s;
its later human-approval wait is excluded from preparation time.

Production made **8 prose revisions across 7 distinct scenes**, with zero
adjudication calls. These are separate from failed-request retries. The longest
recorded production call was 15,475 ms; none exceeded 60 seconds. Technical
completion does not establish literary quality or validate every critic judgment.

| Prompt | Accepted / planned scenes | Production calls | Failed calls | Prose revisions |
| --- | --- | ---: | ---: | ---: |
| OH-V01-001 | 5/5 | 20 | 0 | 0 |
| OH-V01-002 | 5/5 | 24 | 1 | 1 |
| OH-V01-003 | 6/6 | 24 | 0 | 0 |
| OH-V01-004 | 5/5 | 26 | 0 | 2 |
| OH-V01-005 | 4/4 | 16 | 0 | 0 |
| OH-V01-006 | 5/5 | 20 | 0 | 0 |
| OH-V01-007 | 6/6 | 24 | 0 | 0 |
| OH-V01-008 | 6/6 | 37 | 1 | 4 |
| OH-V01-009 | 6/6 | 24 | 0 | 0 |
| OH-V01-010 | 5/5 | 24 | 1 | 1 |
| OH-V01-011 | 5/5 | 20 | 0 | 0 |
| OH-V01-012 | 6/6 | 24 | 0 | 0 |

### Recovered errors and request sizes

The earlier OH-V01-012 Blueprint integration failure remains in the totals.
Three additional calls failed with `schema_validation_failed` during production:

- **OH-V01-002, scene critic:** `repair_checks` failed exact repair-test coverage
  validation (`repair_test_coverage_invalid`) during application materialization.
- **OH-V01-008, continuity supervisor:** `findings.0.summary` was missing,
  rejected during domain validation.
- **OH-V01-010, continuity supervisor:** the coverage result for
  `scene_plan_time_context` lacked valid exact candidate-draft evidence references
  (`requirement_coverage_evidence_invalid`) during application materialization.

Each failed request has its original invocation, inputs, validation evidence and
successful same-task retry preserved in its private dossier. All four failed
calls reported provider finish reason `stop`; these were structured-response
validation failures, not reported output-token truncations or service errors.
The exact repair-check and evidence-reference failures show remaining contract
reliability weaknesses even though the bounded repairs recovered them.

OH-V01-012 completed all six scenes without a production call failure. Its
largest recorded input was **20,104 tokens**, leaving **3,896** below the unchanged
24,000 cap. The campaign's largest production input was **21,042**, an OH-V01-009
critic call, leaving **2,958**. The historical request-size failure did not recur;
two successful repeats still do not prove that future requests cannot exceed
the cap. No runtime, prompt, retry, budget or limit was changed.

### Human review and preserved evidence

All **12 eligible randomized A/B pairs** are packaged in repeat 2's `public/guide.md`
and `public/packet.json`; `public/review.csv` contains the blank canonical scoring
form. `public/scoring-notes.md` carries the reviewer's agreed originality/dialogue
calibration. Review the public texts before inspecting private diagnostics or
the answer key. The public bundle SHA-256 is
`3bc594778be73a766f45340a48643d952bbb2031c4540a96faf8967dde043e73`.

Verification checked **617 artifact content hashes**, exact approval lineage,
manuscript assembly from accepted scene versions, call/token accounting, frozen
budgets and versions, SQLite integrity/foreign keys, and the database secret-export
audit. Independent blind-package reconstruction matched the packet and its private
mapping without revealing labels. The blank CSV matches the canonical rendering.
No workflow or invocation remains active. The database contains 24 projects,
36 workflows, 368 invocations, 12 human decisions and no run controls.

All 24 completed manuscript hashes differ from their Repeat 1 counterparts.
All twelve baselines and all eleven comparable Cloud manuscripts also differ
from the September reference. This verifies distinct outputs, not literary
originality. All 123 runtime files, original operator helpers, September reference
evidence and Repeat 1's human scores and verified seal remain unchanged.
Repeat 3 still has zero story-state rows and model calls.

Repeat 2's private evidence includes 24 full case dossiers, per-phase report
snapshots, `technical-results.json`, `generation-detail-analysis.json`, the completed
database snapshot, original blank review form, generation summary and blind-package
verification. `generation-evidence-manifest.json` binds **84 files** at generation
close; it is not a reviewed formal seal. Key file hashes:

- Generation manifest:
  `f530400f815e93c84125e5c6d003a652594b43c4d5b7f93f8d9bff34cbbe9de2`.
- Completed database snapshot:
  `beb79aa8a5097d5b7d2487ac8ca79155df992a5d362eb30a7641dbb6fbc961a4`.
- Campaign report:
  `5afcacdc5ba31f62dc6411a55ffdd8fa0a52370b1dfc739823261f41fa658558`.
- Original blank review CSV:
  `7e1bf8ec0b09d9c691fe92775b07779df0a335b475ea305d40c782ef442d8bd2`.

Evidence-helper Ruff lint/format, PowerShell parsing and documentation checks
passed. No application runtime changed, so application regression/build checks
were not rerun for this evidence-only work. The next checkpoint is actual human
review, followed by repeat 2's reviewed summary and seal. **Item 5 and Product
Step 19 remain IN PROGRESS.** Repeat 3 has not started.

## Repeat 2 human review and seal — 2026-10-03

The user completed all **12 comparisons / 24 candidate assessments**. Canonical
validation confirmed the exact campaign, public packet and prompt identities,
coverage once per comparison, all 192 integer scores, 168 boolean hard gates and
twelve valid preferences. Scores comprise 84 values of 3 and 108 values of 5.
All gates are true and optional notes are empty. No correction was needed; the
submitted CSV, scores and preferences are preserved byte for byte.

The October 2 originality/dialogue calibration remains in effect, with no further
interpretation change reported. The rubric, weights, anchors and thresholds are
unchanged. Comparisons with September's scores retain the earlier calibration
qualification. Before import, all 83 other files from the 84-file generation
receipt still matched their hashes; only the completed public CSV had changed.

| Criterion | Repeat 2 result | Status |
| --- | --- | --- |
| Cloud technical completion ≥95% | 12/12, 100% | Pass |
| Severe-continuity-free human assessments ≥80% | 12/12, 100% | Pass |
| Mean weighted Cloud score ≥3.5 | 4.1166666667/5 | Pass |
| Lowest Cloud dimension mean ≥2.5 | 3.0 | Pass |
| Cloud preference ≥60% | (1 win + 0.5 × 7 ties) / 12 = 37.5% | Not met |
| Median Cloud cost ≤$2 | Supported complete dollar cost unavailable for all 12 cases | Unknown |

Cloud won **1** comparison, baseline won **4**, and **7** were ties. Ties stay in
the denominator and receive the canonical half credit. The baseline weighted
mean is **4.1583333333**, versus **4.1166666667** for Cloud. All 24 candidates pass
every human hard gate. The seven ties are part of the result; they are neither
Cloud wins nor evidence of statistically established equivalence.

| Dimension | Cloud mean | Baseline mean |
| --- | ---: | ---: |
| Causal coherence and structure | 5.0000 | 5.0000 |
| Character depth and consistency | 3.0000 | 3.0000 |
| Dialogue | 5.0000 | 5.0000 |
| Originality and specificity | 3.6667 | 3.8333 |
| Voice and prose quality | 3.0000 | 3.0000 |
| Emotional and thematic impact | 3.3333 | 3.5000 |
| Pacing and tension | 4.8333 | 4.8333 |
| Continuity and constraint adherence | 5.0000 | 5.0000 |

| Prompt | Cloud weighted | Baseline weighted | Preference |
| --- | ---: | ---: | --- |
| OH-V01-001 | 4.50 | 3.80 | Cloud |
| OH-V01-002 | 3.80 | 4.00 | Baseline |
| OH-V01-003 | 4.00 | 4.00 | Tie |
| OH-V01-004 | 4.00 | 4.00 | Tie |
| OH-V01-005 | 4.00 | 4.00 | Tie |
| OH-V01-006 | 4.00 | 4.00 | Tie |
| OH-V01-007 | 4.50 | 4.50 | Tie |
| OH-V01-008 | 4.30 | 4.50 | Baseline |
| OH-V01-009 | 4.00 | 4.50 | Baseline |
| OH-V01-010 | 4.00 | 4.00 | Tie |
| OH-V01-011 | 4.00 | 4.30 | Baseline |
| OH-V01-012 | 4.30 | 4.30 | Tie |

Character depth and voice/prose remain at 3.0 for both arms. The two reviewed
repeats show successful technical completion and quality means above the existing
floor, but neither meets the preference criterion. Preserve these per-campaign
outcomes. The remaining repeat and consolidated assessment are still required;
the fixed endpoint is not changed because of the results.

Canonical review import, summary, sealing and independent archive verification
passed with **zero new inference calls**. A second verification bound the unchanged
CSV and generation inputs to the reviewed archive and dated calibration addendum.
Database counts remain 24 projects, 36 workflows, 368 invocations and 12 human
Blueprint decisions. The original blank form, generation summary and database
snapshot remain intact. Local evidence under repeat 2's directory includes:

- `private/human-review-input-hashes-2026-10-03.json`: parser validation and source
  hashes, with the unchanged calibration digest.
- `public/reviews.json` and `summary.json`: canonical review and reviewed results.
- `private/human-review-verification.json`: per-case and dimension results,
  unchanged source digests, database counts and calibration/seal binding.
- `private/evidence.zip`: verified reviewed archive, SHA-256
  `669eb4271dede30804419db802a58762ae91bd2f92d03b07e65090a85008bad2`.
- Canonical archive manifest SHA-256:
  `4854c81df5265eeac1eb760f8e132eb1ab8a1fb885e27cb22c84ec8e3205bc6c`.
- Submitted CSV SHA-256:
  `c8a7a75402c50cfb4b9ad915a9fb92943b79e4d3d3375be8d012bd1fe7901554`.

## Repeat 3 environment preflight — 2026-10-03

After repeat 2 validation, the next campaign's `--require-empty --check-provider`
preflight stopped with **Ollama version drift**. The daemon reports **0.35.1**;
the frozen campaign declares **0.35.0**, used for repeats 1 and 2. The cause of
the version change has not been established. No generation was launched.

Read-only follow-up verified all 123 frozen runtime files, original input/operator
hashes, schema and empty repeat-3 state. The model still reports alias
`gemma4:31b-cloud`, remote model `gemma4:31b`, and the same alias digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Matching alias metadata does not demonstrate unchanged remote weights or rule
out an effect from the daemon update. The September reference and both completed
repeats' scores and reviewed seals retain their hashes.

`preflight-environment-drift-2026-10-03.json` in repeat 3's local directory records
expected/observed metadata, all three database counts, prior archive hashes and
the failed check. Repeat 3 still has **zero projects, workflows, invocations and
human decisions**. Its frozen files and checks were not altered or bypassed.

Before generating its Blueprints, resolve whether to restore the declared
0.35.0 environment or explicitly authorize 0.35.1 as a documented environment
deviation. The latter would require a pre-generation addendum and qualified
comparisons, while preserving the original freeze and completed evidence. The
series remains at its existing three-campaign endpoint. This stop comes from
the frozen provider check and protocol, not a new human editorial requirement.
Any new Blueprints will still require their own exact-version human approval.

**Item 5 and Product Step 19 remain IN PROGRESS.** Review/evidence helper lint and
format checks and documentation checks passed. No application runtime changed;
the application regression/build suite was not rerun for this evidence-only work.

## Repeat 3 authorized environment addendum — 2026-10-03

The user resolved the daemon-version decision: **"We should proceed with
0.35.1."** The authorization was recorded before any repeat-3 inference call,
at **13:07:38 UTC / 15:07:38 Europe/Belgrade**. The user expects that the Windows
update will not change the existing `gemma4:31b` service. That expectation is
recorded as the user's rationale, not independently established provider behavior.
The model alias, digest and remote-model name match; remote weights remain unpinned.

The accepted exception applies only to repeat 3's Ollama daemon version:
**0.35.0 → 0.35.1**. Campaign identity/plan, all 123 application runtime hashes,
corpus, profile, alias checks, seeds, prompts, graphs, budgets, retries, scoring
criteria, human checkpoints and the three-campaign endpoint are unchanged.
Keep the version difference visible in comparisons and the final consolidated
assessment. Do not infer equivalence of daemon behavior from its patch number.

The original `series.json`, `protocol-at-freeze.md`, `preflight.json`, setup hashes,
operator helpers, failed-preflight receipt and both earlier reviewed seals remain
unchanged. The local addendum `environment-amendment-2026-10-03.json` binds the
authorization, original/accepted versions, prior seals, empty database counts and
new operator-file hashes. Its SHA-256 is
`4bd2e765ee1089e85c1d3c7b8a7022ef03ed8370ef40dbc9658db3ca72ee8eaa`.

Use repeat 3's **`run-campaign-approved-environment.ps1`** for subsequent phases.
It retains the original phase arguments and calls `verify_approved_environment.py`.
That verifier runs the original frozen input/runtime/database checks and strictly
checks **0.35.1**, the unchanged alias digest and remote-model name before each
model-executing phase. It also verifies the added operators against the addendum
and preserves the earlier evidence hashes. A later version change still fails
preflight; this is not an unrestricted provider-version exception. The original
runner remains intact as evidence of the initial freeze.

`blueprint-generation-authorization.json` binds the next generation to this
addendum and the original series. The approved-environment empty-state/provider
check passed with zero inference requests before Blueprint preparation started.
Preparation will stop at the exact-version human approval checkpoint; the
environment authorization does not grant Blueprint approval. Baseline and scene
production remain unstarted. **Item 5 and Product Step 19 remain IN PROGRESS.**

## Repeat 3 Blueprint checkpoint — 2026-10-03

The authorized run prepared **12/12 Blueprints**, all paused at the mandatory
human approval interrupt, with **zero terminal failures**. Preparation ran from
**13:07:44 to 13:14:04 UTC / 15:07:44 to 15:14:04 Europe/Belgrade**, taking
**379.57 seconds (6 minutes 20 seconds)**. It used **73 model calls**, comprising
72 successful calls and one failed attempt, with **195,239 input tokens** and
**75,152 output tokens** including that failed attempt. Dollar cost remains unknown.

The failed call was OH-V01-012's `blueprint_integrator`. Its structured response
omitted `scene_number` from scene-plan indices 1–5; validation also reported that
too few valid scene plans remained. The existing bounded retry recovered and the
case reached approval. This is a structured-output failure, not a failed story or
a production critic finding. The same missing-field pattern occurred during
repeat 2 preparation. Preserve both observations; they do not establish whether
the daemon change affected behavior. No retry allowance or prompt was changed.

Campaign `11ea6cf8-ceaa-475d-943f-c871649fb2b9` has packet SHA-256
`c32e2a59867a536d9c6926f7565f5713b515d1f41c8252eda5fb2cb2b5d86c96`.
Its identifiers-only `blueprints/approval-manifest.md` lists all exact generated
versions without exposing plots. The full optional dossier is `blueprints/guide.md`;
the approval CSV remains blank. The user's earlier approval method—accepting the
generated versions without editorial changes—can be retained, but requires a new
explicit approval for this set. Ollama-version authorization does not supply it.

Local evidence in `data/benchmarks/v0.1/formal-cloud-v33-repeat-3-2026-10-02/`:

- `blueprint-checkpoint.json`: per-case identifiers, exact artifact references,
  invocation outcomes, usage, timing and approval-boundary checks.
- `private/blueprint-evidence-verification.json`: **158 canonical artifact hashes**,
  database integrity/foreign-key checks, secret-export audit, packet/file hashes,
  original frozen inputs/operators and both earlier reviewed seals verified.
- `private/blueprint-snapshot.db`: preserved source database, SHA-256
  `4e1878403e9b2adb7fcdc903c0ee19d29f7db1e340051857f19b70209394be3c`.

Repeat 3 contains 12 projects, 12 Blueprint workflows, 73 invocations and **zero
human decisions**. No baseline or production workflow has started. After exact-set
approval, use `run-campaign-approved-environment.ps1` for the twelve baselines and
the three unchanged four-case production batches, then prepare twelve eligible
blind pairs if all cases complete. Actual human reviews, the reviewed seal and
the consolidated three-repeat assessment remain outstanding. **Item 5 and Product
Step 19 remain IN PROGRESS.**

The final provider check still reports **Ollama 0.35.1** and the frozen alias
identity. Evidence-helper Ruff lint/format checks, the PowerShell parser,
documentation UTF-8/link checks and `git diff --check` passed. The amended runner
differs only in its verifier selection; all original phase arguments are intact.
No application runtime changed, so the application regression/build suite was
not rerun for this evidence-only work.

## Repeat 3 approval and generation — 2026-10-03

The user approved the presented set: **"I approve the 12 blueprints."** The
approval applies to all twelve exact versions in packet
`c32e2a59867a536d9c6926f7565f5713b515d1f41c8252eda5fb2cb2b5d86c96`,
without editorial changes, continuing the approval-as-generated evaluation method.
The original blank form is preserved in `blueprints/approvals.blank.csv`; the
completed canonical form and `blueprint-approval-authorization.json` record the
authorization. Canonical import persisted **12 human decisions**, completed all
12 Blueprint workflows and added **zero model calls**, verified at **13:18:19 UTC
/ 15:18:19 Europe/Belgrade** in `blueprint-approval-import.json`.

The approved-environment provider check passed again before the twelve baselines
started. Production will follow in the three predeclared four-case batches.
The daemon exception remains limited to Ollama 0.35.1. All other frozen conditions
and both prior reviewed seals remain intact. Generation, fresh human A/B review,
the reviewed repeat-3 seal and consolidated assessment are still underway or
pending. **Item 5 and Product Step 19 remain IN PROGRESS.**

## Repeat 3 generation complete; human review pending — 2026-10-03

All 24 planned case attempts are terminal: **10/12 Cloud stories succeeded** and
**12/12 direct baselines succeeded**. Cloud accepted **56/64 planned scenes**,
including one accepted scene in each failed story. Both failures remain in the
technical denominator; no case was restarted, substituted or granted additional
retries. The ten successful Cloud stories yield **10 eligible A/B comparisons**.
OH-V01-002 and OH-V01-010 are excluded only from paired human review because
their Cloud manuscripts are incomplete; their baselines and partial Cloud
evidence remain preserved.

Production ran from **13:21:22 to 13:39:59 UTC / 15:21:22 to 15:39:59
Europe/Belgrade**, about **18 minutes 37 seconds** including checks between
batches. Baselines took **2 minutes 32 seconds**, from 13:18:23 to 13:20:54 UTC.
Blueprint generation took the previously recorded 6 minutes 20 seconds; its
workflow completion time also includes waiting for the separate human approval.

| Phase | Outcome | Calls | Failed calls | Input tokens | Output tokens |
| --- | --- | ---: | ---: | ---: | ---: |
| Blueprint preparation | 12/12 reached approval; all subsequently approved | 73 | 1 | 195,239 | 75,152 |
| Direct baselines | 12/12 succeeded | 12 | 0 | 2,888 | 28,513 |
| Cloud production | 10/12 succeeded; 56/64 scenes accepted | 267 | 6 | 2,681,227 | 226,627 |
| Entire campaign | All 24 case attempts recorded | **352** | **7** | **2,879,354** | **330,292** |

Whole agentic accounting, including Blueprint preparation and failed attempts,
is **340 calls, 2,876,466 input tokens and 301,779 output tokens**. All seven
failed calls were structured-output validation errors. Three recovered through
their existing same-task retries; four unsuccessful attempts account for the two
terminal production failures. There were **11 prose revisions across 10 distinct
scenes** and **zero adjudication calls**. No budget, revision allowance or prompt
changed. Supported dollar cost remains unavailable.

| Production batch | Completed stories | Accepted/planned scenes | Calls | Failed calls | Elapsed |
| --- | ---: | ---: | ---: | ---: | --- |
| 1: 001–004 | 3/4 | 17/21 | 84 | 2 | 5m 42s |
| 2: 005–008 | 4/4 | 21/21 | 96 | 0 | 6m 55s |
| 3: 009–012 | 3/4 | 18/22 | 87 | 4 | 5m 51s |

### Terminal failure evidence

**OH-V01-002 — scene 2, revision 2, continuity recheck.** Both attempts returned
`continuity_issue_45120e1ba552c1ab` in `prior_finding_rechecks`, although the exact
current partition required no prior model findings. Continuity report version 1
contains that blocking finding; version 2, the latest input report, contains no
findings. Both reports were in the supplied input lineage. The model therefore
reintroduced an older finding into the keyed recheck partition after the latest
report had cleared it. Both responses failed `prior_finding_partition_mismatch`
at `application_materialization`, exhausting the existing response-repair attempt.
The case stopped with **1/5 scenes accepted**, after two prose revisions of scene 2.

The preserved lineage identifies version 1 as
`f591d8e7-54ee-453d-9263-19bf3f33fa7c`, version 2 as
`4d428e48-683b-430d-b171-fcbaf91b3e25`, and the attempted candidate as
`66281002-712f-41a7-9cb9-5905992ae15e`. This supports investigating how historical
findings are distinguished from currently eligible rechecks. It does not by
itself settle whether the attempted criticism describes a real story defect.

**OH-V01-010 — scene 2, initial draft, continuity review.** The first response
omitted `findings.1.summary` and failed `domain_validation`. Its retry then used
invalid exact candidate-draft references in
`requirement_coverage.scene_plan_time_context.evidence_refs`, failing
`application_materialization`. The case stopped with **1/5 scenes accepted**.
The two errors occurred on the same task; no valid continuity response was accepted.

All four terminal failed review responses have captured, untruncated allowlisted
review evidence, candidate/input version references and selected evidence in the
invocation diagnostics. They are explicitly marked `unvalidated_review_response`
and `manuscript_defect_established: false`. Keep these protocol failures distinct
from validated critic findings or human quality judgments.

The three recovered failures are OH-V01-012's missing Blueprint scene numbers,
OH-V01-009's attempted rewrite of immutable resolved-thread history during a
story-bible update, and OH-V01-012's invalid exact repair-test coverage in a scene
critic response. The latter two each succeeded on their single existing retry.
The failed critic response also retains its unvalidated review evidence.

### Verification and next checkpoint

The largest production input was **21,289 tokens**, an OH-V01-012 scene-critic
call, leaving **2,711 tokens** below the unchanged 24,000-token cap. The longest
production call was **16.860 seconds**; none exceeded 60 seconds. All 22 completed
manuscripts differ in content hash from their corresponding outputs in repeats
1 and 2. The 21 comparable outputs from the September reference also differ.
Content differences demonstrate fresh outputs, not a quality improvement.

Verification covered **585 canonical artifact hashes**, exact approved Blueprint
lineage, invocation accounting, assembled accepted-scene text, frozen production
budgets, SQLite integrity/foreign keys and the secret-export audit. The database
contains 24 projects, 36 workflows, 352 invocations and 12 human decisions, with
no run-control interventions. All 123 frozen application runtime hashes, original
setup/operators, Blueprint checkpoint, the September reference and both earlier
reviewed seals remain unchanged. The final provider receipt still reports the
authorized **Ollama 0.35.1** and unchanged alias metadata. Preserve that environment
qualification; these results do not isolate an effect of the daemon update.

The public packet was rebuilt independently from the report and fresh blinding
key and matched the canonical output. The blank ten-row CSV matches the canonical
form. `public/scoring-notes.md` retains the same originality/dialogue calibration.
Read the public candidates and complete `public/review.csv` before inspecting
private diagnostics or answer mappings. Human scores have not been supplied.

Evidence remains under
`data/benchmarks/v0.1/formal-cloud-v33-repeat-3-2026-10-02/`:

- `private/diagnostics/`: complete per-case invocation/event/artifact evidence,
  including partial story evidence for both failed cases.
- `private/technical-results.json` and `private/generation-detail-analysis.json`:
  usage, timings, revisions, failures/recovery, maxima and finding lineage.
- `private/completed-snapshot.db`: SHA-256
  `71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
- `private/review-package-verification.json`: validated ten-pair packaging,
  exclusions, unchanged prior seals, calibration and environment addendum.
- `private/generation-evidence-manifest.json`: **82 preserved files**, SHA-256
  `5304f86eae2321c9b74a0751ef5cd034e719beb9b310a11f58f8750c13f18d44`.
- Canonical public-bundle SHA-256:
  `decaaa85f9b65ac389da63697e6b6af74138adae0fb882d2093b9aafa40e6eea`.

This is the preserved generation record; the formal reviewed seal remains pending.
Cloud technical completion is **83.33%**, so the unchanged **≥95% criterion is
not met**. Four human quality/preference criteria remain pending and cost remains
unknown. The three prospective repeats now have technical completion of **12/12,
12/12 and 10/12**; aggregate Cloud completion is **34/36 (94.44%)**, with **36/36
baselines**. Preserve the individual outcomes and the authorized environment
change rather than treating the aggregate as identical-condition evidence.

Finish the ten human comparisons, import and verify them, seal repeat 3, then
consolidate the fixed three-repeat assessment. Do not add a fourth campaign or
retry these failed stories to change the endpoint. **Item 5 and Product Step 19
remain IN PROGRESS.**

Final evidence-helper Ruff lint/format checks, documentation UTF-8/link/anchor
checks, `git diff --check` and re-verification of all 82 manifest entries passed.
No application runtime changed; the full application regression/build suite was
not rerun for this campaign-execution and evidence work.

## Repeat 3 human review and seal — 2026-10-04

The user completed all **10 eligible comparisons / 20 candidate assessments**.
Canonical validation passed all identities, coverage, 160 integer scores, 140
boolean gates and ten preferences. Scores contain 68 values of 3 and 92 values
of 5; every gate is true and optional notes are empty. No correction was needed.
The submitted CSV remains byte-for-byte unchanged, including uppercase A/B
preferences accepted by the canonical parser. Repeated scores are valid.

Cloud's weighted mean is **4.16/5**, versus **4.15/5** for the baseline. There are
**1 Cloud win, 2 baseline wins and 7 ties**. The canonical half-credit calculation
is `(1 + 0.5 × 7) / 10 = 45%`, below the unchanged 60% criterion. OH-V01-011's
baseline preference is preserved even though Cloud's weighted score is 4.30 and
baseline's is 4.20: preference is a separate judgment, not an automatically
derived winner. All 20 reviewed candidates pass every hard gate.

| Criterion | Repeat 3 | Status |
| --- | --- | --- |
| Technical completion ≥95% | 10/12, 83.33% | Not met |
| Severe-continuity-free review ≥80% | 10/10 reviewed Cloud stories | Pass |
| Weighted Cloud score ≥3.5 | 4.16 | Pass |
| Lowest Cloud dimension mean ≥2.5 | 3.0 | Pass |
| Cloud preference ≥60% | 45% | Not met |
| Median Cloud cost ≤$2 | Complete supported dollar evidence unavailable | Unknown |

The two failed Cloud stories retain their failed technical results; no human
score is imputed for them or their unpaired baselines. The October 2 reviewer
calibration remains unchanged. The new qualitative feedback below is additional
evidence, not a retrospective change to weights, anchors, gates or thresholds.

Review import, canonical summarization, sealing and independent verification
completed with **zero new inference calls**. Before import, all 81 other files
in the 82-file generation manifest retained their hashes. The original generation
summary, blank form, completed database snapshot and all prior seals remain intact.
The final review receipt still counts 24 projects, 36 workflows, 352 invocations
and 12 Blueprint decisions. The reviewed archive was verified at 11:11 UTC /
13:11 Europe/Belgrade on October 4.

- Submitted CSV SHA-256:
  `8cf4938ea7484578a1e897274b6a1c9cf05562128ea1c84d68baa4381d74ba1c`.
- Reviewed archive SHA-256:
  `f0f74505f17bd08b0480aa9f675a4a604c0b9f1e27c7208b5ac2e7ff37d907af`.
- Canonical archive-manifest SHA-256:
  `418b578711afc75268d81e1b4936317765323b4b90cd3ca6c5b8948acd23c5c8`.
- Local receipts: `private/human-review-input-hashes-2026-10-04.json` and
  `private/human-review-verification.json` under repeat 3's directory.

## Consolidated three-repeat assessment — 2026-10-04

**The predeclared assessment is complete. Repeated acceptance is not established.**
All three fresh campaigns reached terminal outcomes, every eligible pair received
actual human review, and all three reviewed archives were independently verified.
No fourth campaign, replacement story or terminal-case retry was added.

| Measure | Repeat 1 | Repeat 2 | Repeat 3 |
| --- | ---: | ---: | ---: |
| Ollama daemon | 0.35.0 | 0.35.0 | 0.35.1, authorized exception |
| Cloud completion | 12/12 | 12/12 | 10/12 |
| Baseline completion | 12/12 | 12/12 | 12/12 |
| Accepted/planned scenes | 64/64 | 64/64 | 56/64 |
| Reviewed pairs | 12 | 12 | 10 |
| Weighted Cloud / baseline | 4.0500 / 4.1500 | 4.1167 / 4.1583 | 4.1600 / 4.1500 |
| Cloud wins / baseline wins / ties | 5 / 4 / 3 | 1 / 4 / 7 | 1 / 2 / 7 |
| Cloud preference, ties at half credit | 54.17% | 37.50% | 45.00% |
| All-phase model calls | 376 | 368 | 352 |
| Failed calls / recovered failed calls | 3 / 3 | 4 / 4 | 7 / 3 |
| Prose revisions | 11 | 8 | 11 |
| Adjudication calls | 0 | 0 | 0 |
| Input tokens | 3,116,117 | 3,032,238 | 2,879,354 |
| Output tokens | 348,990 | 340,102 | 330,292 |
| Production elapsed | 20m 36s | 22m 46s | 18m 37s |
| Supported monetary cost | Unknown | Unknown | Unknown |

Technical acceptance passes in two campaigns and fails in the third. The three
human quality criteria pass in every campaign; preference fails in every campaign;
cost remains unknown throughout. Zero adjudication calls means this series supplies
no live execution evidence for that branch, even though its implementation has
separate failure-path verification.

Supplementary totals are **34/36 Cloud completions (94.44%)**, **36/36 baselines**,
**184/192 accepted scenes**, and **34 reviewed pairs / 68 candidate assessments**.
The pooled reviewed means are **4.1059 Cloud / 4.1529 baseline**. Preferences are
**7 Cloud, 10 baseline and 17 ties**, giving **45.59% Cloud preference** with half
credit. All 68 scored candidates pass all seven gates. The entire series used
**1,096 calls**, **9,027,709 input tokens**, **1,019,384 output tokens**, 30 prose
revisions and zero adjudications. Ten of fourteen failed calls recovered; the
remaining four attempts belong to the two failed repeat-3 stories.

These are descriptive aggregates over repeated premises and one reviewer, not
independent population estimates or a substitute for the per-campaign criteria.
The apparent increase in mean Cloud score also changes cohort in repeat 3.
Restricted to the ten prompts reviewed in all three campaigns, Cloud means are
**4.06, 4.16 and 4.16**; baseline means are **4.13, 4.19 and 4.15**. This does not
support a claim that quality continued improving from repeat 2 to repeat 3.

### Per-prompt outcomes

Each cell gives **accepted/planned Cloud scenes; Cloud/baseline weighted scores;
human preference**. Every baseline completed; unpaired cases have no submitted
paired quality score. A preference may legitimately differ from score ordering.

| Prompt | Repeat 1 | Repeat 2 | Repeat 3 |
| --- | --- | --- | --- |
| OH-V01-001 | 5/5; 4.50/4.30; Cloud | 5/5; 4.50/3.80; Cloud | 5/5; 4.50/4.50; tie |
| OH-V01-002 | 5/5; 4.00/4.50; baseline | 5/5; 3.80/4.00; baseline | Failed 1/5; unpaired |
| OH-V01-003 | 6/6; 4.00/4.00; Cloud | 6/6; 4.00/4.00; tie | 6/6; 4.00/4.00; tie |
| OH-V01-004 | 5/5; 3.70/3.70; Cloud | 5/5; 4.00/4.00; tie | 5/5; 4.00/4.00; tie |
| OH-V01-005 | 4/4; 4.00/4.00; tie | 4/4; 4.00/4.00; tie | 4/4; 4.00/4.00; tie |
| OH-V01-006 | 5/5; 3.70/3.70; tie | 5/5; 4.00/4.00; tie | 5/5; 4.00/4.00; tie |
| OH-V01-007 | 6/6; 4.50/4.50; Cloud | 6/6; 4.50/4.50; tie | 6/6; 4.50/4.30; Cloud |
| OH-V01-008 | 6/6; 4.50/4.80; baseline | 6/6; 4.30/4.50; baseline | 6/6; 4.30/4.50; baseline |
| OH-V01-009 | 6/6; 4.00/3.70; Cloud | 6/6; 4.00/4.50; baseline | 6/6; 4.00/4.00; tie |
| OH-V01-010 | 5/5; 4.00/4.00; tie | 5/5; 4.00/4.00; tie | Failed 1/5; unpaired |
| OH-V01-011 | 5/5; 4.00/4.60; baseline | 5/5; 4.00/4.30; baseline | 5/5; 4.30/4.20; baseline |
| OH-V01-012 | 6/6; 3.70/4.00; baseline | 6/6; 4.30/4.30; tie | 6/6; 4.00/4.00; tie |

Cloud completed OH-V01-012 in all three repeats, with its largest critic inputs
remaining within the existing 24,000-token cap. That addresses the observed
September request-size failure on these attempts, without establishing a general
context-growth guarantee. OH-V01-002 and OH-V01-010 regressed from two completions
to terminal continuity-response failures. Their exact diagnostics are retained
above and in the register; favorable pooled averages do not remove them.

| Cloud dimension mean | Repeat 1 | Repeat 2 | Repeat 3 |
| --- | ---: | ---: | ---: |
| Causal coherence and structure | 5.0000 | 5.0000 | 5.0000 |
| Character depth and consistency | 3.0000 | 3.0000 | 3.0000 |
| Dialogue | 4.1667 | 5.0000 | 5.0000 |
| Originality and specificity | 3.8333 | 3.6667 | 3.8000 |
| Voice and prose quality | 3.0000 | 3.0000 | 3.0000 |
| Emotional and thematic impact | 3.5000 | 3.3333 | 3.4000 |
| Pacing and tension | 5.0000 | 4.8333 | 5.0000 |
| Continuity and constraint adherence | 5.0000 | 5.0000 | 5.0000 |

Character depth and prose remain the clearest repeated weaknesses in these human
scores. High coherence and continuity scores apply to reviewed completed stories;
they do not imply the failed review protocols are reliable or every unreviewed
partial draft is sound.

### Evidence register and limitations

The local `v33-cloud-repeatability-2026-10-02/consolidated-register-2026-10-04.json`
under `data/benchmarks/v0.1/` binds all three archive and manifest digests, submitted
CSVs, reviewed summaries, technical diagnostics, original generation manifests,
snapshots, frozen series/protocol, calibration and the environment exception.
Its SHA-256 is
`1a15ce8db3619122776c943778c9b0586899c798f970eb44e7c3952293f1876a`.
It includes all 72 case records with per-case calls, failures/recovery, revisions,
adjudications, tokens, timing, cost coverage, output identity and linked human
results. All original generation-file hashes were verified using the preserved
blank forms and generation summaries where later human review intentionally
created new versions. All three canonical archives were verified again.

| Repeat | Reviewed archive SHA-256 |
| --- | --- |
| 1 | `0d5611771cd993023338039ebb76becea719900f5e9519ae89e8fb63d15ed43d` |
| 2 | `669eb4271dede30804419db802a58762ae91bd2f92d03b07e65090a85008bad2` |
| 3 | `f0f74505f17bd08b0480aa9f675a4a604c0b9f1e27c7208b5ac2e7ff37d907af` |

The original freeze remains immutable. The October 2 calibration addendum and
October 3 environment exception are separate, hash-bound records. Repeats 1–2
used Ollama 0.35.0; repeat 3 used authorized 0.35.1. Remote weights and enforcement
of the fixed seeds are not independently pinned. September's differently
calibrated reviews remain outside the prospective aggregates. These limitations,
the small repeated corpus and reviewer familiarity prevent broad causal or
population claims. All completed per-prompt outputs have different text hashes
across repeats; that verifies fresh output identity, not literary variety.

## Reviewer observations and implications — 2026-10-04

The reviewer considers the writer's work decent overall and says the
[September manual-review summary](../september_2026_manual_test_reviews/review-summary.md)
still describes the repeated runs: limited character depth, recurring AI tics
and weak group dynamics. The original manual summary is preserved unchanged.
The dated local `reviewer-observations-2026-10-04.json` records the new feedback;
its digest and the manual summary's digest are bound by the consolidated register.
The incomplete extra example under point 2 was omitted after the user clarified
that it was probably a typo.

The following are **the reviewer's observations**, not newly measured frequency
counts or a systematic recoding of every story:

- Stories increasingly resembled one another, making similar grades appropriate.
  Priest/criminal stories repeated similar protective dynamics. The reviewer
  suggested a corrupt priest, a culpable protected person, or protection going
  badly wrong as possibilities that would materially change the conflict.
- Across six stroller stories the reviewer recalls one female protagonist and
  several bereaved fathers, with no siblings searching for a brother or sister.
  The six identification stories repeatedly used a brother/sister pairing and
  similar physical identity evidence. Memory-currency stories were enjoyable
  but reused similar characters and settings.
- Characters frequently belonged to financially secure professional worlds.
  The six romantic dramedies repeatedly used architects, designers or comparable
  occupations. The desired breadth includes different economic pressures, moral
  positions, social relationships and dealings; no occupation is prohibited.
- Shorter dialogue tended to work better; extended exchanges could lose quality.
  This is a specific craft observation alongside generally high dialogue scores,
  not a request to change those scores or impose a dialogue-length cap.

The frozen corpus leaves these choices open. OH-V01-001 does not require a parent
protagonist; OH-V01-005 does not fix sibling genders; OH-V01-006 does not prescribe
occupations or financial security. OH-V01-004 already requires conflicting moral
reasons, changing leverage and agency for the protected person, and explicitly
rejects purely virtuous/cruel central characters. The review therefore identifies
an opportunity to develop the available premise more fully, rather than a need
to abandon its core constraints.

This series deliberately reused premises, the same model configuration and
per-prompt seeds to assess repeatability. Each campaign had fresh artifacts and
no prior story memory copied into it. Increasing familiarity can reveal recurring
choices without showing that the model learned to become less varied over time.
A separate diversity experiment would need its own predeclared conditions, with
varied seeds and additional premises; it must not retroactively alter this series.

There is also a length difference to keep visible. Median completed Cloud lengths
were **3,744, 3,926 and 4,031 words**; baseline medians were **2,118.5, 2,007.5 and
1,855.5**. Respectively 10, 11 and 12 baselines were below their advisory word
targets, while no completed Cloud story was below its target. The established
policy permits scoring these outputs and does not turn length into a new hard
gate. The comparison does not isolate dialogue length as a cause of preference.

### Proposed next corrective work

First examine the two observed continuity-response failure paths using the saved
inputs and regression cases: eligible current findings versus historical findings,
and required summaries/exact evidence references during response repair. Preserve
validation and the existing bounds while finding the smallest supported fix.

For literary quality, inspect where character and relationship choices first
enter the existing brief/character/scene-plan passes. A different name or job is
insufficient: economic pressure, private motives and unequal obligations should
change what people can do, what they conceal and how a scene ends. Group dynamics
need decisions that change alliances or costs for other characters. Dialogue
should earn its space through a changed position, new information, a consequential
choice or a revealing action; repeated explanations can be tightened. Prose review
should address clustered repetition in context while retaining useful sensory
detail, contrast and rhythm.

These are proposed directions for a separately scoped change and evaluation, not
implemented behavior or new acceptance criteria. They preserve the user's position
against bans, higher retry limits and longer prompts. No general manuscript
editor, new agent swarm or hidden cross-project memory is introduced.

**Item 5 is COMPLETE as an assessment and evidence-sealing task. Product Step 19
remains IN PROGRESS** because technical acceptance is inconsistent, preference
does not meet its threshold and monetary cost remains unqualified. Step 20 has
not started. The next action is a scoped corrective plan informed by these results,
not another run added to obtain a better outcome.

Final review/consolidation helper lint and format checks, documentation UTF-8,
48 link/anchor checks and `git diff --check` passed. Canonical archive verification
and original generation-evidence verification passed for all three campaigns.
The local `assessment-closure-2026-10-04.json` binds this final report, the tracker,
the consolidated register, reviewer observations and three reviewed seals by hash.
No application runtime or schema changed; the full application regression/build
suite was not rerun for this review and documentation work. All submitted scores
and the original manual-review summary remain unchanged.
