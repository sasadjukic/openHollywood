# Frozen review-correction and comparative-assessment plan

Date: 2026-10-18. **PREPARATION COMPLETE; NO LIVE EXECUTION AUTHORIZED OR STARTED.**

This freezes the authorized local preparation from the
[diagnosis and proposal](../handoffs/fulfillment-repair-surface-review-diagnosis-next-experiment-2026-10-18.md).
Production remains prompt **61**, graph **9**, fulfillment policy **1**.
**Full workflow canary: ON HOLD; NOT STARTED.** J1/P1 remain diagnostic evidence;
E1 remains mechanically successful but unqualified for preservation.

Plan SHA-256:
`9793f119f39c64ba2cd92f869f1d356240dfc8da7c8cf7b2a4184e79c12d9c86`.

## Budget and frozen settings

| Block | Primary work | Maximum inference calls |
| --- | --- | ---: |
| A: review correction | 6 fixed parent reports × 2 arms × 2 seeds; one correction/identity challenge each | 24 |
| B: comparative assessment | 9 fixed prose candidates × 2 arms × 2 seeds; one structural correction permitted per assessment | 72 |
| **Total** | **60 primary requests, up to 36 B corrections** | **96** |

Blocks are nontransferable. A has no retry beyond its one correction challenge.
B retries only a structurally invalid assessment, once. A valid but wrong opinion
receives no retry. There are **no new writer calls**, live source selection, source
replacements, semantic rerolls, transport rerolls, extra revisions or canary calls.
All 60 primary slots are fixed; invalid A reports do not gate or change B's inputs.
Unused allowance from any earlier experiment is irrelevant.

Model: **`gemma4:31b-cloud`**, via **Ollama Cloud through the local Ollama daemon**.
Pinned digest:
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Future approved execution verifies model identity, digest and Cloud deployment at
preflight and before each phase. No discovery was performed during preparation.

Both comparisons use seeds **19701/19703**, temperature **0.2**, top-p **0.95** and
thinking disabled. At the first seed, cases run in ascending order and arm 0 runs
first; at the second seed, case order and arm order reverse. A precedes B. The
operator maintains separate durable attempt ledgers for each scheduled request.

Per attempt: **24,000 input tokens, 8,000 output tokens, 900 active seconds**.
Aggregate reservations: **2,304,000 input tokens, 768,000 output tokens, 86,400 active
seconds**. Historical October 8 rate estimate at the ceiling: **USD 0.62976**;
actual billed charges remain unknown. This estimate is not provider billing evidence.

## A: same parent and diagnostics, different correction surface

All source reports are immutable attempt-1 captures. Their full original context,
ordinary review semantics, exact parsed parent JSON, raw response hash, bounded R1
diagnostics and permitted correction locations are frozen.

| ID | Frozen parent | Role |
| --- | --- | --- |
| a01 | `s19603-elara-duplicate-overrun-initial-shared` | Missing independent-craft comparison coverage |
| a02 | `s19601-elara-recurrence-overrun-initial-shared` | Non-null recommendation on a linked boundary issue |
| a03 | `s19501-elara-duplicate-overrun-initial-P1` from the preceding presentation/temperature run | Boundary ownership error plus masked comparison error |
| a04 | `s19603-elara-duplicate-overrun-correction-R1` | New boundary ownership error after comparison was corrected |
| a05 | `s19601-elena-missing-decision-initial-shared` | Valid missing-decision native repair control |
| a06 | `s19601-elena-compound-outcome-initial-shared` | Valid native-plus-boundary control preserving the fulfilled decision |

- **F0:** return the exact parent response hash and a complete corrected report.
- **F1:** return that hash and only typed replacements/removals at the diagnosed
  locations, in their supplied order. The adapter applies them atomically to the
  immutable parent and then runs the unchanged full review validator.

Both arms must preserve every value outside the allowed locations. Comparison
references and their assessment may be corrected; a separately authored linked
recommendation may become null; only an explicitly diagnosed application-owned
boundary condition may be removed. Native condition records, judgments, issue
descriptions, classifications, severity, evidence and scores are otherwise fixed.
Valid controls require the identical report or an empty patch list.

The scope comes from the existing structural collector, not expected story labels.
No automatic reference insertion, default explanation, silent removal, semantic
reclassification or repair of model output is permitted. Stale parent hashes,
unknown locations, wrong operations, duplicate/incomplete patches and collateral
changes fail. Unsupported or incomplete diagnostic scope also fails closed.

The parent is explicitly untrusted diagnostic data. This isolated adapter departs
from production's rejected-prose replay policy in both arms; production remains
unchanged. F0 is therefore **not unchanged production R1**. Both arms receive the
parent, so the comparison isolates full-object emission versus restricted correction,
not the effect of parent visibility alone. The full ordinary schema appears once
per request: inside F0's report schema or beside F1's patch schema. Local paired
checks prove the ordinary contract and remaining context are equal.

The a06 source retains its documented next-scene explanation caveat about warning
acceptance. Its explicit no-match constraint independently supports the actual
judgment and narrow repair condition. Preserve and report that known source caveat;
do not certify every inherited explanation or count it as a newly introduced error.

**Frozen success criterion:** F1 must recover all eight failed-parent cells and
preserve all four valid-control cells, with supported retained findings/conditions
and comparisons, no collateral changes, at least two additional qualified recoveries
over F0 and zero paired losses. Structural validity alone cannot qualify a comparison
explanation. If both arms recover every case, report no demonstrated relative
advantage. These are fixed error challenges, not estimates of natural failure rates
or proof of improved critic noticing.

## B: full-prose assessment with purposes hidden or visible

Both arms receive the complete original and revision, version-bound quotation
catalogs, exact diff, mechanical change alignment, assignment and boundary context,
applicable source critique, mandatory repair tests and requested optional craft task.
They also receive the relevant fulfilled passage. Change alignment identifies text
ranges, not preclassified semantic changes; assessors must consider the full sentence
and scene. Source/arm/seed provenance and operator labels remain outside messages.

- **V0:** full comparative assessment with purpose claims hidden.
- **V1:** the identical task, schema, context and settings with the frozen claims
  visible as untrusted assertions to verify against the actual changes.

The only model-message difference within each pair is `editorial_claims`. V0 is
predeclared as the candidate independent assessment; V1 tests explanation influence.
Both are separate calls to the same model, so correlated blind spots remain possible.
The earlier ordinary P0 posts are historical reference evidence, not fresh paired
controls. No production reviewer or automatic approval gate is installed.

| ID | Original/revision comparison | Provenance and scoring focus |
| --- | --- | --- |
| b01 | W1 separate-entry revision, 19601 | Actual output; unsupported adjacent rewrite |
| b02 | W1 separate-entry revision, 19603 | Actual output; lost concrete preparation and a plausible emotional tradeoff |
| b03 | W1 embedded-entry revision, 19601 | Actual output; necessary entry repair plus additional imagery |
| b04 | W1 optional-duplication repair, 19601 | Actual output; successful local craft repair |
| b05 | Minimal separate-entry repair | Labelled operator construction; preserves adjacent preparation |
| b06 | Minimal embedded-entry repair | Labelled operator construction; preserves compatible wording |
| b07 | Optional-duplication no-op | Labelled operator construction; duplicate remains despite an attached removal claim |
| b08 | Boundary no-op | Labelled operator construction; entry remains despite an attached removal claim |
| b09 | Phrase duplication inside one fulfilled sentence, then repaired | Labelled synthetic craft control; changes wording inside positively cited evidence |

The actual outputs retain their source purposes. Minimal repairs use the appropriate
direct-repair claim. No-op claims are deliberately attached operator challenge data,
not falsely attributed as new model outputs. All construction provenance is frozen
in the operator ledger. Synthetic control b09 has an explicit optional task and no
fabricated critic source or mandatory craft test.

For b09, the original bracing sentence repeats “to carry herself through” adjacently.
Its revision removes one phrase while preserving the bracing action, purpose and
surrounding scene. The changed range lies inside the one cited sentence. Local
checks verify that editing only an uncited second sentence cannot satisfy this task.
This is a narrow craft control, not proof of broad literary improvement.

Assessments contain separate task checks, fulfilled-fact checks, per-change necessity
and preservation judgments, purpose checks when visible, and supported observations
about voice, tension, agency and naturalness. Exact quotes and current version/ref
identities are validated. Substantive support still requires inspection. The required
fact checks cover the assigned turning point and outcome; losses of other prose
meaning remain part of preservation and craft assessment.

A review correction must preserve individually valid judgments and assessments by
unique current record identity, even if the first response ordered its records
incorrectly. Bad or missing identity fields cannot establish retained judgments.
Ambiguous duplicate identities, oversized retention or incomplete evidence stop
automatic continuation. The model cannot erase criticism or change a valid opinion
to repair formatting. Evidence references may be corrected against the frozen catalog.
Every raw attempt remains available, and first/final results are scored separately.

**Frozen V0 criterion:** all 18 cells must have correct task/factual judgments; both
no-op defects must be detected at both seeds; all six actual boundary-revision cells
must identify their extra changes and separate necessity from possible merit; clean
boundary repairs and both successful craft-control types must receive no invented
hard failure. The mixed b02 case must acknowledge the supported tradeoff/uncertainty,
without imposing a predetermined human literary preference. Invalid outputs cannot
qualify. A no-change bias or blanket protection of cited prose fails the controls.

**Frozen V1 comparison:** record every unsupported upgrade, factual miss, invented
objection and supported improvement relative to V0 across 18 pairs. Do not switch the
primary arm after seeing results. Valid references or fluent purposes do not establish
support. Retain an additions-neutral sensitivity analysis alongside the primary
preservation judgments. Passing this test could justify proposing a later review-
guided revision experiment; it does not authorize one.

## Frozen evidence and operator behavior

Private preparation:
`data/diagnostics/fulfillment-repair-surface-review-v61-2026-10-18/`.

The bundle includes six parent reports, nine candidate packets and provenance records,
scoring labels/rules, the exact 60-slot schedule, **60 complete static request snapshots**,
the frozen builder for up to 36 response-dependent structural corrections, input-size
checks, fake-provider ledgers, final verification and nine anonymous full-prose pairs.
The human review sheet is empty and **PENDING**. The closure binds the public report,
tracker snapshot, preparation files and **151 code dependencies**. No production,
client, schema migration or canonical story artifact changed.

The source live closure remains
`fbc4939b3ce2ddf1c19d74bb011426e15f587c5ca1cc5c71f32bacfffb224e3b`;
the diagnosis closure remains
`65a7b2142929a3f218e9ebf1c1cf7b653b850ace5b43abc3cfc69add7d273d45`.
Historical evidence is unchanged. Exact code/file hashes bind the task-start source
baseline and all diagnostic additions; source documentation retains its history.

Before dispatch, the operator validates approval against this exact plan, sources,
static/dependent requests, schedule, block/stage/aggregate budgets and prior outcomes.
It persists the full request and reservation before invoking the provider. Cancellation,
unknown outcomes, incomplete attempts, model/identity drift, transport failure,
truncation, token/time overruns or integrity failures stop dispatch. Completed attempts
replay without inference. Request, receipt, outcome, usage and summary bindings are
reconciled; no automatic retry of a possibly completed invocation is allowed.

All initial requests pass the frozen sizing check: maximum **19,184 estimated input
tokens**. A maximum-length retained semantic-payload test reaches **20,487 estimated
input tokens**, including bounded failure feedback. These UTF-8-size estimates are
not exact provider token counts. Requests exceeding the sizing limit stop before
dispatch; observed usage exceeding the hard allowance stops further dispatch. Context
is not silently trimmed.

## Verification and remaining boundary

- **60** valid contract fixtures; **389** rejection checks; **30** paired-delta checks.
- Fake matrices: **60** normal calls, **96** ceiling calls, **62** failure-matrix calls.
- **284** fake dispatches across matrix and fault/restart tests; **278** completed
  attempts replayed with final code. Completed replay made **zero** extra calls.
- Restart, cancellation/lock cleanup, unknown outcomes, all aggregate limits,
  model identity, malformed output, drift, stale references, scope violations,
  approval rejection and reordered-judgment retention checked.
- **75 focused regressions passed**. Repository Ruff/format and strict mypy passed
  across **201 files**; all **9 private helpers** pass Ruff/format. Client checks
  are inapplicable because no client or production code changed.
- External connections and real gateway construction were blocked during harness
  checks. Windows event-loop initialization used its local socketpair before those
  guards. **Live inference, provider discovery and external network calls: zero.**

The next action requires explicit live approval of this frozen plan and its payload:
full unpublished original/revised prose, rejected critic reports, critique, story
context and unverified purpose claims sent to Ollama Cloud through the local daemon,
within **96 calls**. No approval record or live run directory exists yet.

Future story-quality qualification still requires independent human review, the
accepted weighted rubric and hard gates, the full intended Cloud corpus and a
comparable single-model baseline. Factual repair, preservation and artistic improvement
remain separate. **Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**
