# Critic fulfillment versus endpoint compliance, fixed v59 — 2026-10-15

Status: **DIAGNOSTIC COMPLETE — NO IMPROVEMENT; PRODUCTION V59 UNCHANGED.**

All sixteen approved probes completed in sixteen first-attempt-valid calls. The
clarification did not preserve the fulfilled decision when a later endpoint was
violated: **0/4** in the scoped arm, identical to **0/4** under ordinary v59 guidance.
Both arms blocked all four overruns, accepted both valid baselines, and detected both
missing-date and both missing-decision controls. Keep this as an unsuccessful
diagnostic; do not promote the candidate guidance to production.

The [writer evidence transfer](writer-evidence-transfer-v59-2026-10-15.md) stopped
before writer calls. Both baseline critics accepted Elena's deliberate handwriting
comparison as a decision to investigate. Adding a later forbidden match made all
four defective-draft reviews mark that fulfilled decision unmet, because the exit
state was violated. Both genuinely missing-date controls were correctly detected.

This diagnostic tests whether a compact clarification can preserve requirement-level
fulfillment while keeping the separate endpoint violation blocking. It also tests a
genuinely missing decision so the clarification cannot qualify by marking every
decision met. Production, validators, schemas and writer behavior remain unchanged.

Source commit: `8f097792589aa16a5e167cbc53150952251cf04e`.
Branch: `codex/critic-fulfillment-scope-v59`.
Production stays **prompt v59 / graph v9**; the diagnostic instruction variant is
`scoped_fulfillment_1`. Main is unchanged. Step 19 remains IN PROGRESS and Step 20
is NOT STARTED. Sixteen authorized critic calls completed; no writer calls or
canonical changes occurred.

## One diagnostic instruction replacement

The current critic instruction says:

> Overruns become blockers; still assess the complete assigned outcome independently in assignment_checks.

Only the diagnostic treatment replaces that span with:

> Overruns remain blockers. In assignment_checks, assess each named requirement's complete assigned fact; assess endpoint compliance separately in scene_boundary_check. A later breach of a separate exit-state limit does not itself undo an already fulfilled decision or fact. Use unmet only when that requirement's own fact or condition fails; any terminal-state restriction within the requirement still binds. Actions and indirect narration are valid evidence. Preserve these distinctions in repair advice: repair the violated endpoint or genuinely unmet requirement without demanding that a fulfilled decision happen again. A met check never cancels a separate blocker or authorizes a pass.

This adds 585 characters to the system message. Every other instruction, user
message, artifact, evidence handle, schema, setting and budget is identical within
each pair. The replacement persists during the existing structural retry. The v59
definition of met still requires the complete assigned fact; the clarification scopes
which requirement owns a condition. It does not introduce a keyword classifier,
force statuses, rewrite responses or suppress genuine endpoint failures.

No fulfilled-evidence writer packet is supplied. No production prompt or validator
file is edited. Exact messages, variant metadata and hashes identify the diagnostic
request even though the production prompt-version field remains 59.

## Paired matrix and controls

Run both ordinary v59 and scoped guidance at seeds **19101 and 19103** for each row:

| Draft | Required turning point | Required decision | Endpoint | Expected canonical verdict |
| --- | --- | --- | --- | --- |
| Accepted inconclusive investigation | Met | Met through actions | No overrun | Pass |
| Same prose plus definitive match | Met | Met through unchanged actions | Overrun | Revise |
| Missing future date plus definitive match | Unmet | Met through unchanged actions | Overrun | Revise |
| Future date, genuinely unresolved decision | Met | Unmet | No overrun | Revise |

The first three rows reuse the previous experiment's exact artifacts and seeds.
The six ordinary-v59 requests match its saved requests, including instructions,
schema, settings and budgets. Fresh calls provide a contemporaneous comparison;
the previous results remain sealed historical evidence.

The new negative draft removes the earlier search for forgery, journal retrieval,
comparison and replication. It retains the future date and no-match endpoint, and
explicitly leaves the choice to investigate unresolved. It therefore checks missing
decision detection directly, alongside the separate missing-date control. Other
prose remains unchanged; both arms receive the same synthetic draft.

The synthetic plan from the previous experiment is unchanged: the outcome is the
decision to verify; the separate exit state prohibits establishing a match. Fresh
revision-zero review context has no historical repair advice. No canonical story
or approved production Blueprint is modified.

Total: **16 independent critic probes**, four drafts × two guidance arms × two
seeds. Counterbalance arm order across seeds. Run all prepared probes regardless of
earlier judgments, allowing at most one existing structural retry per probe. Do not
reroll valid judgments, substitute drafts or use unused retry allowance for new
probes. There are no writer calls, full-story runs or canonical writes.

Maximum: **32 calls / USD 0.20992** at the recorded October 8 rates of USD 0.14/M
input and USD 0.40/M output, with 24,000 input / 8,000 output tokens per call. Actual
charges remain unknown. Use the existing `gemma4:31b-cloud` deployment and frozen
model digest; temperature 0.2, top-p 0.95, thinking disabled.

## Verification and interpretation

- Nineteen no-network mock calls cover all sixteen cases, one structural retry
  retaining the candidate guidance, and a permanent failure after two attempts.
- All eight pairs differ only in the declared system span, including when given
  the same structural-retry failure. All production request hooks are restored.
- Replay all six previous raw responses and audits exactly. Their old canonical
  outputs, including the disputed unmet judgments, still materialize unchanged
  under the candidate's validators. Local validation does not predetermine semantics.
- Verify 1,732 prior sealed files, their reports, the source database and v59 code.
- Forty-five focused regressions pass in 28.60 seconds. Repository Ruff, formatting
  and strict mypy pass for 198 files; diagnostic formatting/error checks pass.

The frozen assessment protocol required reconstructing and replaying every request
and response, and inspecting raw
checks, cited evidence, mandatory conditions, source support, generic comparisons,
canonical findings and verdicts. The primary result requires **both** preservation
of the fulfilled decision and blocking of the forbidden endpoint. A met status alone
does not qualify if the advice demands restating the decision, drops the boundary
repair or the raw verdict incorrectly passes. Check the baseline and both negative
controls independently; record duplicates and first/final validity separately.

If ordinary-v59 calls no longer reproduce the earlier classification, report that
non-reproduction and the fresh paired result. Do not attribute all changes to the
clarification. This is one scene/provider and two seeds with a synthetic plan and
fresh review context. It does not establish writer repair success, general story
quality or behavior when a terminal restriction is part of the outcome's own text.
That restriction remains in the guidance but is not a new live matrix cell here.

## Live results

| Observation | Ordinary v59 | Scoped guidance |
| --- | ---: | ---: |
| Valid baseline accepted with both native facts met | 2/2 | 2/2 |
| Fulfilled decision remains met while the later overrun is blocked | **0/4** | **0/4** |
| Later endpoint violation detected and blocked | 4/4 | 4/4 |
| Genuinely missing future date detected | 2/2 | 2/2 |
| Genuinely unresolved decision detected | 2/2 | 2/2 |

All eight paired cells agree on native check statuses, boundary status and canonical
verdict. The fresh ordinary-v59 arm reproduces the disputed classification from the
previous experiment. The treatment was delivered as frozen: replay confirms that
the actual sent scoped requests contain the replacement, with every non-system
message and all artifacts/schema/settings unchanged within each pair.

Both arms accept the journal comparison and replication as evidence of the decision
in the baseline. In all eight overrun reviews across the arms, the critic acknowledges
those same actions but marks the decision unmet because the later match exceeds the
endpoint. The distinction failed in the raw model response; canonical rendering did
not erase a met judgment.

The structured conditions make the support mismatch inspectable. For example,
`s19101-preserve-scoped` marks the outcome unmet but its only repair condition is to
end before a match is established, citing **only the exit-state sentence**. The
remaining scoped overrun reviews generally combine the decision and no-match
endpoint in their outcome repair conditions. Thus the extra guidance did not reliably
separate fulfillment, failure attribution or mandatory advice.

The negative controls remain useful. All four missing-date reviews across both arms
require the actual ten-year relation. All four unresolved-decision reviews cite the
explicit indecision and require a decision, without prescribing dialogue, immediate
causation or completed verification. These are correct detection and advice results;
no writer repair success was tested.

Duplicate reporting also remains: four current-arm and three scoped-arm overrun
reviews retain separate canonical outcome/boundary complaints about the same match.
All generic criticisms in this matrix concern assignment defects; no independent
craft defect was identified. This secondary variation does not rescue the primary
result.

Raw verdicts were four `pass`, nine `reject` and three `revise`. Existing v59 handling
normalizes repairable rejects, leaving four canonical passes and twelve revisions.
No defective draft passed in either raw or canonical judgment. This correct blocking
behavior is separate from the incorrect native fulfillment classification.

All sixteen requests, raw responses and audits replay exactly. No retries, failures,
skipped probes or extra calls occurred. Usage: **303,296 input / 21,590 output tokens**;
**USD 0.05109744** at recorded October 8 rates, with actual charges unknown. Sources,
production hashes and canonical artifacts remain unchanged.

## Next focused recommendation

Keep production v59 and do not add this unsuccessful paragraph. Test a diagnostic
check that carries its exact assigned requirement and, for `unmet`, identifies the
specific clause that is missing or contradicted with current-draft evidence. Keep
the separate endpoint check blocking and retain both negative controls. This makes
the asserted failure directly inspectable rather than relying on the global scope
reminder alone.

Validating the cited requirement would establish traceability, not semantic support.
Do not force met statuses in application code, reinterpret the response to obtain a
preferred result or remove legitimate endpoint blockers. No further cloud test is
authorized by this completed run. Writer transfer remains unresolved.

## Private evidence

Bundle: `data/diagnostics/critic-fulfillment-scope-v59-2026-10-15/` (ignored locally).
It contains the runner, replay/assessment script, no-network fixtures, check receipts,
all sixteen frozen requests, predeclared protocol, explicit approval, live receipts,
replay assessment and independent semantic inspection.

Plan SHA-256:
`bc7de682c74fde36c742c1c0905d369aa327c46828ba3ffafc24882059b6e1be`.

Prior transfer closure SHA-256:
`32dd762e7a15eaf638914ab23614f0c32940a2fbac084ecf73db5969f3409a9e`.

Explicit approval is recorded against the frozen plan. The final closure hashes
the report and private evidence bundle. Production promotion is not warranted.
