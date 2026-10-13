# Shared assignment repair conditions v59 — 2026-10-13

Status: implementation, local verification, offline replay and approved cloud
comparison complete. The focused shared-condition contract passes this matrix;
writer and broader semantic qualification remain open. Main remains v55
production plus documentation.

## Scope and implementation

The branch `codex/critic-shared-repair-conditions` starts from `8939848`. It
recovers the v58 condition rendering and regression fixtures from `66d66cf`,
then replaces per-restatement authorship with shared native ownership. Historical
v55/v57/v58 reports and sealed evidence remain unchanged.

Each native assignment finding has one condition set. Linked generic issues keep
null recommendations and reuse the exact recommendation rendered for their
validated target. Extra mandatory conditions must be authored and source-cited
in the native set. Per-issue condition records and separate advice are rejected.
Repeated descriptions and distinct evidence survive consolidation; repair text
is no longer appended a second time. Independent craft remains a separate route.

The application resolves boundary/native aliases through the existing validators,
including the exact anchor/evidence rule. Boundary-only restatements reuse the
existing application policy. A consolidated boundary/native finding retains
that policy plus its one native set. There is no semantic deduplication, inferred
condition, silent upgrade or truncation. Old canonical repair advice is unchanged.

Prompt 59 / graph 9 / critic retry policy 20 / boundary audit schema 7. The audit
records each restatement's native owners and boundary-policy participation.
Source validation, null advice, bounds and rendering come from v58. The v55
meaning of met and its evidence/relationship rules remain unchanged. No new call,
retry allowance, writer instruction, provider dependency, schema migration or
public API change is introduced. See [ADR 0036](../adr/0036-shared-consolidated-repair-conditions.md).

## Local evidence

The new direct-wire tests cover multiple restatements at every severity, two
distinct native findings, both aliases of a consolidated boundary finding,
separate evidence, other native routes, invalid/missing owners, competing advice,
independent craft and classification retention. The simulated durable workflow
checks that a malformed first review triggers only the existing critic retry;
two declared restatements then produce one writer repair with exact condition
text. Historical fixtures are adapted only in tests.

Focused tests initially exposed loss of prior classification metadata when a
later link became invalid. Diagnostic rendering now leaves unresolved links
invalid while retaining prior validated choices. A prompt-length check also
caught an overlong addition; the guidance was shortened within the existing
1,950-character bound. These failures were local, with no model calls.

Local verification:

- Ruff check and format check pass; strict mypy passes across 198 source files.
- The full Python run reports 1,025 passed and one failed in 293.10 seconds.
  That failure is an old v43 assertion expecting boundary-only repeated advice
  to be appended. The assertion was updated to require exact reuse of the
  application policy. All 86 affected v43/v58/v59 tests then pass in 14.57 seconds,
  including the durable mock workflow. No production change followed the full
  run; the entire suite was not rerun after this test-only correction.
- Sixteen new v59 direct-wire cases complement the 44 adapted v58 rendering
  tests and existing regression coverage.
- Frontend formatting, lint, type checks, all eleven Vitest tests and production
  build pass. UTF-8/LF and Git whitespace checks pass.
- The frozen requests and runtime hashes were reverified after these checks.

## Saved-response replay

Verified 443 sealed evidence files (136 v55, 164 v57, 143 v58), their report
hashes, and the immutable source database. Replayed all 22 unmodified v58
responses against v59 without model calls or production backfill:

| Saved responses | v59 local result |
|---|---|
| 18 previously valid first reviews | Valid; identical canonical critiques |
| 2 previously rejected missing-facts first reviews | Valid; two blockers, one exact native repair per blocker |
| First missing-facts retry | Still rejected: non-null separate generic advice |
| Second missing-facts retry | Still rejected: independent craft comparison omits current findings |

All twenty saved first responses now validate. The recovered two responses
already contained their native conditions and correct declared links. Nothing
was copied, inferred, removed or re-authored in the raw responses. Their new
canonical recommendations exactly match the native condition strings joined
with one space. The two remaining failures demonstrate that sharing conditions
does not bypass unrelated contracts. Historical replay is not fresh model
evidence or semantic qualification.

## Approved matched comparison

Private bundle: `data/diagnostics/shared-repair-conditions-v59-2026-10-13/`.
Twenty fixed cases reuse the exact v55/v58 OH-V01-001 inputs, drafts, synthetic
wordings, seeds 19101/19103, settings, budgets and call order. All source catalogs
and output schemas match v58; the only first-request content difference is the
shared-condition guidance paragraph. No expected labels enter model messages.

The sixteen main cases cross reversed or delayed-ordered drafts with order-only,
order with a causal waiver, separately defined relationships and unconstrained
facts. Four controls cover explicitly immediate causation and two missing facts.
The implementation and complete requests are frozen before approval.
Plan SHA-256: `2b45a15c9043e25d4a89907af74ea1fa86d0a543ba3eeea8bbe6f332ce2d82a8`.

- Maximum twenty probes / forty calls, at most one existing structural retry each.
- Per-call ceiling: 24,000 input / 8,000 output tokens.
- Published-rate ceiling: USD 0.26240 using recorded October 8 rates of USD 0.14/M
  input and USD 0.40/M output tokens. Actual charges remain unknown.
- Destination: existing local Ollama daemon forwarding to Cloud `gemma4:31b-cloud`.
- No valid-response reruns, writer calls, full-story runs or canonical writes.
- Stop after the fixed matrix; do not tune code or prompts during the comparison.

Inspect first/final validity and judgments, retry drift, condition owners and
citations, repeated versus independent claims, computed writer repairs and final
verdicts. Check unsupported causal, temporal, immediacy, motivation and completion
demands in both conditions and explanatory prose. Source traceability alone does
not establish semantic support. Compare with both retained v55 and failed v58.

The operator explicitly approved this exact plan. The launch succeeded and the
fixed matrix completed without changes to the implementation or inputs. Every
request was reconstructed, every raw response replayed without edits, and the
code, source database and historical evidence hashes reverified afterward.

## Results

| Measure | Retained v55 | Prior v58 | v59 |
|---|---:|---:|---:|
| Probes / calls | 20 / 21 | 20 / 22 | 20 / 21 |
| Valid first reviews | 19 | 18 | 19 |
| Valid final reviews | 20 | 18 | 20 |
| First raw assignment pairs matching controls | 18 | 20 | 20 |
| Final raw assignment pairs matching controls | 19 | 20 | 20 |

These are historical matched comparisons with one model, one scene and two
seeds; they are not estimates of general reliability. In particular, correct
raw checks in a rejected response do not constitute an accepted critique.

All ten complete cases pass without repairs. All ten defective cases require
revision: six reversed-order cases, two immediate-causation controls and two
missing-facts controls. The latter produce two blockers each; all others produce
one. The final twelve native sets contain 23 conditions. Four reviews also
declare a generic repetition, using the native set rather than another record.
Each of those four yields exactly one blocker and one writer repair target.
Every final recommendation exactly equals its native condition strings joined
with one space; there are no appended restatement repairs or `issue:N` records.

The fresh missing-facts reviews omit generic repetitions, so their success alone
does not demonstrate recovery of v58's exact output shape. That recovery is
established by the unmodified saved-response replay; the four fresh repetitions
exercise the same ownership mechanism on the reversed-order cases.

All 25 citations across the 21 responses resolve to exact current Scene Plan
turning-point or outcome text. No unassigned mandatory causation, ordering,
immediacy, motivation or completed-entry condition was observed in the rendered
advice. Eighteen valid drafts' action-based entry decisions remain met; only the
two genuinely undecided controls receive an outcome repair. No independent craft
claim, viewpoint violation or boundary overrun was reported in this live matrix.
Their shared-condition behavior remains covered by local tests, not these calls.

### The one retry

`s19103-reversed-order_only` initially supplies a 601-character turning-point
assessment against a 600-character bound. The existing structural retry shortens
it to 383 characters; the complete response then validates. Both checks and the
raw reject verdict remain unchanged. The condition set changes from two order
statements to three fact/order statements. The generic issue keeps its target,
category and severity but expands its evidence from one handle to two.

The invalid hard check prevents establishing a new retained-classification
record, so this retry is not evidence that the retention mechanism preserved
its exact evidence set. It is a successful bounded response repair. No malformed
review becomes a manuscript finding, and no writer call is made.

### Remaining semantic limits

- The accepted first-seed order-only generic comparison describes touch as the
  cause of the pull, despite an order-only assignment. Several score rationales
  similarly use causal language. That language is absent from the native repair
  conditions; this does not establish that it cannot influence a later writer.
- Both delayed/order-with-waiver assessments describe permission as a condition
  satisfied by delay. Delay alone cannot determine whether contact caused the
  pull. These correct passes carry an imprecise explanation.
- The immediate-causation controls render "immediately upon" touch, while their
  support and source name immediate causation. Timing and cause are not separately
  expressed conditions. A writer might realize timing without causation; no
  writer test has established otherwise.
- Missing-facts repairs repeat the already fulfilled psychic-pull fact alongside
  the missing touch. This adds no unassigned requirement, but preserving existing
  fulfillment rather than unnecessarily rewriting it still needs a writer test.
- Two condition sets omit punctuation between their clauses. Exact space joining
  preserves content but does not improve that wording. The renderer deliberately
  does not edit the critic's advice.

The critic continues to give highly favorable prose/character scores and broad
praise. These controlled probes do not measure prose quality, human preference,
full-story quality or calibration of those scores.

## Usage and next step

The 21 calls report 407,609 input and 25,902 output tokens. At the recorded
October 8 rates the estimate is **USD 0.06742606**, below the approved USD 0.26240
ceiling. Provider receipts use an unknown cost basis with a zero placeholder;
that is not evidence of free billing. Actual charges remain unknown. The v59
estimate is below v58's USD 0.07081296 but above v55's USD 0.049684; the source
catalog and structured conditions still carry an input/output cost.

Keep v59 fixed for the next focused test: feed actual condition-rendered feedback
to the existing writer and review its revision. Include an order-only defect and
the missing-facts control, checking that repairs preserve fulfilled facts and
indirect decisions without inventing causation or completed entry. Include an
explicitly required causal relationship as a control. Do not change guidance
merely because all twenty critic labels are correct.

This establishes a usable shared-condition path on the tested matrix. It does
not close Step 19 or authorize full-story testing. No writer/full-story calls or
canonical changes occurred; main remains at v55. Step 19 is IN PROGRESS and
Step 20 is NOT STARTED. Private evidence is indexed by the bundle's `closure.json`.
