# CW-013: ordinary-review premise admission preparation

Date: **2026-10-31**. **COMPLETE — bounded local design and harness preparation.**
This follows the [diagnostic-export recommendation](reviewer-probe-export-results-2026-10-30.md).
Model/daemon budget **zero**; no live requests are prepared or authorized.
Production **prompt 61 / graph 9 / fulfillment policy 1** is unchanged. Inference
is **PAUSED**, the full workflow canary **ON HOLD**.

## Decision and unanswered question

Prioritize [CW-013](../../issues/013-unsupported-review-explanations.md): a
consequential factual premise in an ordinary critic explanation may be unsupported
even when another part of the criticism is valid. The next question is how to
**identify that premise without changing its meaning or losing the supported
repair basis**, before asking whether the source supports it.

The source-obligation experiments assessed supplied claims and authored obligation
maps. They did not qualify extracting consequential premises from complete
ordinary reports. A proposed new diagnostic should measure that admission gap,
not repeat a source-label rename or presume that exact evidence binding solves it.
Here, *admission* means identifying the exact allegation and its source scope for
assessment; it is not permission to repair prose or admit a claim to production.

The local work prepares a complete field inventory, six inspected examples and a
binding harness. It does **not** implement automatic semantic extraction, classify
all report text, or treat a field as one atomic claim. There is no new model result.

## Why this differs from previous tests

| Prior work | What it tested or established | Remaining distinction |
| --- | --- | --- |
| [Fixed CV claims](../benchmark_reports/reviewer-claims-v61-results-2026-10-24.md) | 49/72 correct labels; 7/24 fully usable responses on supplied claims | Claims were supplied, not recovered from a complete critic report |
| [CV/MC](../benchmark_reports/reviewer-material-claims-v61-results-2026-10-24.md) | Added premise guidance produced one recovery and two losses | Another materiality reminder would repeat this approach |
| [Production-scope audit](reviewer-production-scope-audit-2026-10-28.md) | Source/view identities are available; arbitrary obligation creation remains unsolved | A typed assignment or selected quote cannot create PO's semantic premise map |
| [BS/PO/ER](../benchmark_reports/reviewer-source-obligations-v61-results-2026-10-28.md) | PO recovered five BS target failures with correct inspected primitives | Identity/opposition/time was an authored map for one relation type |
| [BS/PO generalization](../benchmark_reports/reviewer-provenance-v61-results-2026-10-29.md) | All twenty PO targets usable, three BS recoveries; precision concerns remained | Generalization still used supplied claims and scopes |
| [PO/EX](../benchmark_reports/reviewer-exactness-v61-results-2026-10-30.md) | Both arms handled all tested semantic contrasts; receipts added no demonstrated precision benefit | Another receipt prompt is not justified; application copying checks are already available |
| [Materiality audit](reviewer-retention-materiality-audit-2026-10-30.md) and [exports](reviewer-probe-export-results-2026-10-30.md) | Deterministic binding and prospective materiality bookkeeping work on inspected inputs | Neither extracts or verifies a consequential premise automatically |

Thinking, attribution, negation, event/endpoint and complete-source distinctions
remain requirements from the completed investigation. They are not newly discovered
failure classes here. The hypothesis worth designing is narrower: **explicit,
complete verbatim field coverage may prevent consequential premises from being
omitted or softened during claim selection**. Whether a model can then judge them
correctly is a separate outcome. The present local checks do not prove either gain.

## Frozen local evidence and harness

Private bundle: `data/diagnostics/cw013-preparation-v61-2026-10-31/`.

- `plan.json`: zero-call scope, boundaries, prospective scoring requirements and stops.
- `candidate-inventory.json`: all twelve previously exported captures; **163
  candidate prose fields and 219 explicitly classified metadata/reference strings**.
- `inspection-cases.json`: six authored source-inspection cases with exact report
  and witness offsets, version/field/source/view hashes and prospective dispositions.
- `prepare.py`, `cases.py`, `test_prepare.py`, `verify.py`: offline builders,
  binding checks, regressions and sealed verification; no inference runner or
  automatic writer route.
- `source-baseline.json`, verification records and preparation/publication seals:
  preserved source identities and actual local-check results.

The twelve captures are exactly the prior selection: **October 16 Gemma ordinary-v61
diagnostic probes**, not new DeepSeek responses or persisted production reviews.
The two families supply 52 Elara and 111 Elena candidate fields. These are field
instances, not 163 independent claims, errors, scenes or new model observations.

The census includes summaries, score rationales, strengths, issue descriptions,
assignment/repair assessments, boundary comparisons and condition/support wording.
It does not preselect negative verdicts or discard favorable statements. Categorical
labels, handles and quoted source text remain explicitly accounted for in the raw
record; they are not mislabeled as newly generated allegations. An unknown string
field stops preparation instead of being silently omitted. Compound fields remain
whole, with selected subspans linked back to their exact surrounding text.

Every candidate starts **support unreviewed / materiality unreviewed**. The three
application-rendered advice records remain separate from raw model fields. All
six recovered old prose bodies retain their visibility labels and the particular
historical repair quotations actually shown. The original exports still retain
complete requests, responses, normalized results, audits and dependency snapshots.

The saved export manifest is pinned to
`5d4406e5ec809321e138309bddab103de993726c8739773ce9baf99dd976f49d`.
Preparation re-reads the sealed archive through the existing adapter and requires
the twelve reconstructed snapshots to equal the exports. No historical Python is
executed and no saved review or score is changed.

## Six local inspection cases

These are authored factual-inspection examples using already known evidence.
They are **not new blind gold, model recoveries or a generalization sample**.
They cover five selected reviews, all in the familiar Elena family; A1/A2 share
one review and E1 is a related post-review. Fresh families are still necessary.

| ID | Exact capture and report field | Inspected distinction |
| --- | --- | --- |
| A1 | `s19103-elena-embedded-initial`, `/assignment_checks/outcome/assessment` | “it bypasses the specific decision-making process” conflicts with the established purposeful journal-fetching action under the frozen event interpretation. The same field also contains valid boundary criticism. |
| A2 | Same capture, `/scene_boundary_check/current_endpoint_comparison` | The explicit match independently violates the no-match endpoint. Removing A1's unsupported basis must not clear this defect. |
| B1 | `s19101-elena-missing-decision-initial`, `/assignment_checks/outcome/assessment` | The draft explicitly leaves the choice unresolved: a genuine missing-decision control. |
| C1 | `s19103-elena-missing-date-initial`, `/assignment_checks/turning_point/assessment` | Both dates are 2024; the assigned ten-year discrepancy is genuinely absent. |
| D1 | `s19103-elena-clean-initial`, `/assignment_checks/outcome/assessment` | Purposeful action establishes the decision without literal assignment wording. |
| E1 | `s19101-elena-missing-date-post-evidence`, saved `/repair_checks/.../assessment` | The correction is supported by old/current source versions; recovered full old prose is distinct from the old quotations visible during review. The exact pointer is frozen in the case file. |

A1 is a material *review-basis* problem under the existing interpretation. It does
not establish that the premise caused a particular writer edit or harmed the
reading experience. A2 remains a real defect. A model must not receive credit for
rejecting the whole review, accepting the whole review because A2 is correct, or
inventing a different claim to make A1 easier to assess.

None of these event/assignment claims is automatically forced into PO's
identity/opposition/time template. All six record that admission as false.

## Verification, scoring boundaries and stops

**137 offline tests pass in 7.31 seconds: 54 preparation checks plus 83 unchanged
export/comparison checks.** Ruff lint/format and strict mypy pass on the four
local scripts. Tests block socket connection/DNS and SQLite connection attempts.
The builders reproduce their saved JSON exactly; identical publication preserves
modification times, while changed output is refused.

The verification command checks the eight sealed preparation files before and
after the checks. Missing or changed files stop verification; it does not rebuild
missing inputs. Run from the repository root:

```powershell
uv run --extra api python data/diagnostics/cw013-preparation-v61-2026-10-31/verify.py
```

Checks cover complete field accounting across all twelve reports, exact report
subspans and source witnesses, six case bindings, changed trial/unit/quote/offset/
version/hash/view/role, unsupported PO admission, writer authorization, historical
rescoring, ambiguous repeated quotations, unknown fields and zero-call policy.
A well-formed false assertion deliberately passes the **binding** boundary while
remaining semantically unverified. Changing an authored semantic judgment to
another allowed label also passes structural validation; it differs from the
frozen inspected note. This explicit negative control prevents a validator pass
from being reported as semantic correctness.

All **212 existing Python files, 33 prior-export artifacts, nine reviewed historical
reports and fourteen issue bodies/posted links** remain unchanged. The inherited
archive validator also checks its pinned preparation/live seals. The initial
local run exposed an incorrect secret-guard import; that was corrected. Initial
lint findings and the standalone mypy source-path configuration were corrected
before the passing checks. No production code was changed to pass verification.
The earlier 134-test pass is preserved; three seal-member regressions were added
before the final 137-test run.

The previous full application suite remains historical. No production, API,
frontend, persistence or dependency change was made here, so a new full workflow
suite or frontend build would not test this bounded local addition.

Stop on changed source/export identity, unknown field type, unresolved occurrence,
missing witness, altered frozen output or any attempted network/database access.
Unsupported or unreviewed semantics never becomes a pass, an event assertion or a
repair instruction. The local budget is **0 model calls / 0 daemon calls / 0 retries**.

Any later model comparison must score admission coverage separately from semantic
accuracy and preservation of supported findings. Invalid/missing answers remain in
attempted denominators. Correct labels with unsupported reasons earn no usable
credit; authored examples earn no model credit. Craft disagreement and incidental
precision remain separate from factual story defects and literary quality.

## Proposed next step

A materially different **premise-admission diagnostic** is justified for design,
not execution: compare a reviewer selecting consequential allegations from a full
ordinary report with the same reviewer receiving independently selected, exact
allegation spans from that report. Both receive the complete declared source and
the full report; the supplied spans are a diagnostic control, not model success.
Keep the semantic task/settings identical so selection and judgment failures can
be separated. Do not extend PO's special three-premise algebra to arbitrary claims.

A provisional small design is **six families × two admission conditions × two
source presentation orders = 24 calls, zero retries**. Retain two historical
families: Elena's mixed event/endpoint finding and Elara's actual-entry boundary
control. Add four fresh families with supported criticism beside unsupported
premises, plus attribution/modality and scope controls. Exact fresh cases, span
annotations, requests, token/time ceilings, delivery stops and outcome thresholds
must be prepared and sealed before asking for live approval. **This 24-call idea
is not a frozen request set or an approved allowance.** No model or daemon metadata
was queried; the old Ollama version is historical, not a verified current baseline.

If supplied-span judgment succeeds while report selection misses or changes
material premises, pursue admission coverage. If both conditions fail on the same
bound premises, the bottleneck remains semantic assessment. If both succeed or
the control offers too few failures, retain descriptive evidence without claiming
a recovery. No result by itself authorizes writer edits or closes CW-013/CW-006.

Human review remains focused on feel, flow, character and story-breaking details.
Mechanical inventories and source locations should support that review, not add a
manual counting burden. The nine earlier human ties remain intact. All fourteen
issues stay open; no external issue was edited. **Step 19 IN PROGRESS; Step 20
NOT STARTED.** Production prompts unchanged; inference paused; canary on hold.
