# Read-only ordinary-review intake — implementation and acceptance

Date: 2026-11-12. **Implemented and verified locally. Live calls PAUSED; canary ON HOLD.**

The tracked intake path now carries whole ordinary-review fields, explicit scope
declarations and full evidence into pending assessment work. It retains ambiguous
and editorial claims as visible holds. It creates no model request, assessment
result, completion receipt or writer permission.

The five previously admitted reviews supported by the existing probe contract
pass acceptance: **61 whole fields retained, six factual claims pending and three
interpretation holds preserved**. All 28 inventory/intake files are reused exactly
on repeat, without byte or modification-time changes. The other seven reviews
remain outside the registered source contract.

## Delivered path

- [Pure engine component](../../engine/open_hollywood_engine/evaluations/assessment_intake.py):
  versioned source, plan, choice, finding and result records; complete-field
  inventory; scope/brief checks; pending-work construction; literal renderer.
- [Application adapter](../../apps/api/open_hollywood_api/services/assessment_intake.py):
  existing authenticated probe and read-only SQLite exports, bounded IO, source
  rechecks, secret guards, immutable publication and manifest.
- [Operator CLI](../../scripts/assessment_intake.py): explicit source/selection,
  inventory without declarations, or intake with an authored plan. Errors omit
  source prose and validation inputs.
- [ADR 0047](../adr/0047-read-only-ordinary-review-intake.md): procedural/editorial
  policy, authority boundary, publication and operational limits.
- [Domain tests](../../tests/evaluations/test_assessment_intake.py),
  [adapter tests](../../tests/api/test_assessment_intake.py) and
  [authored fixtures](../../tests/assessment_intake_fixtures.py).

The existing assessment modules and ordinary/probe/native archive exporters are
unchanged. No new archive trust pins, dependencies, migrations, API/client schema,
production prompt/profile/graph/gate or Blueprint checkpoint changes were needed.

## Operator flow

Run the [README command](../../README.md) without `--plan` first. `index.json`
identifies each adjacent `review-NN.json`/`.md`. These contain the whole report,
full original messages, current prose, evidence registry and separately labeled
operator provenance. `plan.json` contains source/work fingerprints and empty
choices. The inventory has no pending assessment units.

Copy the plan outside that immutable directory before authoring it. Do not edit
the exported inventory, fingerprints, source text or raw captures. Each choice has:

| Field | Meaning |
| --- | --- |
| `field_id` | Exact displayed whole-field ID. No substring selection or rewriting. |
| `reading` | `factual`, `literal_procedure`, `editorial_effect`, `mixed` or `ambiguous`. |
| `interpretation` | Authored intended reading; structural checks do not verify its meaning. |
| `hold_reason` | Optional explicit reason to withhold a field from pending work. |
| `declaration` | Native whole-statement `ClaimScopeDeclaration`, including exact field pointer, predicates, material clauses, source references and observation basis. May be null for a hold. |
| `brief` | Native `AuthoredWorkBrief` with the same unit ID, question, temporal/source scope and evidence obligation. May be null for a hold. |

Set `authored_by` on each plan. Use the exact whole statement from the inventory
work for `declaration.statement`; use the matching report-field pointer. References
must come from that work's evidence registry. There is no answer/gold field.
The component does not generate interpretations or fill missing declarations.

For example, an unresolved field can be retained without inventing a declaration:

```json
{
  "field_id": "Q007",
  "reading": "ambiguous",
  "interpretation": "Literal completion of the named procedure or loss of its dramatic function; unresolved.",
  "hold_reason": "These readings have different evidence obligations.",
  "declaration": null,
  "brief": null
}
```

`Q007` here is illustrative; use the actual ID from the selected inventory. The
complete typed plan schema is available locally from
`IntakeBatchPlan.model_json_schema()` in the adapter module. Tracked authored
fixtures demonstrate complete factual and literal-procedure choices. The private
[acceptance plan](../../data/diagnostics/assessment-intake-integration-2026-11-12/operator-plan.json)
shows the six real factual choices and three holds with exact source bindings.

Repeat the same source/selection command with `--plan` and a new output directory.
The adapter authenticates the original records again, computes every disposition,
and rechecks sources after rendering. It refuses stale bindings, changed/partial
destinations and unsupported archives. Original sources are never overwritten.
Saved production reviews retain their original lineage in operator provenance;
their new assessment work remains a diagnostic, with no invented canonical ID.

## Scope clarified

**Literal procedure is an event claim about specified means or steps.** It requires
both definition and depicted-performance scope. A general match does not establish
that a particular identifying flourish was checked. A temporal or causal qualifier
cannot disappear merely because a simpler event is supported.

**Editorial effect concerns what the scene does for the reader or story.** Claims
about suspense, pacing, emotional impact or consuming a later reveal are not
settled by counting occurrences or proving a named procedure absent. They remain
outside this factual intake. That boundary preserves their importance for future
story-quality work.

Mixed fields stay whole and held. Ambiguous fields stay unresolved. H03's claim
about achieving the private-flourish turn remains a hold; this policy does not
retroactively assign it contradicted gold. A literal reading could be declared in
a new diagnostic, but would need separate defensible gold and explicit labeling.

Purposeful action can still establish a decision. Missing future-state authority
does not prove a claim false. Stylistic praise is not a factual assertion that
repetition is absent. Exact copying and correct citations are not full evidence
or permission to edit. Human review remains focused on feel, flow, character and
story-breaking effects.

The intake checks declared structure, not semantic truth. A mistakenly authored
factual reading can pass those checks; the output explicitly leaves interpretation,
brief neutrality, support, evidence adequacy, editorial effect and craft unverified.
No automatic classifier or extra mandatory human checkpoint was added.

## Verification

**379 tests pass: 53 new intake tests plus 326 existing assessment/export tests.**
The new coverage includes procedure definitions, missing scope, unavailable
authority, mixed/ambiguous holds, exact whole-field identity, hidden-provenance
exclusion, malformed source bindings, multi-batch retention, source changes during
rendering, failed/partial/conflicting output, path/size limits, secret guards and
sanitized CLI errors. The saved-review tests use isolated migrated databases and
fake gateways; database and WAL bytes remain unchanged by intake.

The final checks pass repository Ruff, formatting and strict mypy for **240 tracked
Python files**, plus the private acceptance helper (241 checked files). The existing
56 Pydantic warnings come from deliberate mutation fixtures. Windows sandbox temp
and event-loop restrictions required the database tests to run outside the sandbox;
no provider request was involved. A test exposed a 16-versus-12 native batch-limit
mismatch, corrected before acceptance and covered by a 25-field regression.

Real-capture acceptance uses only N01–N05 from the prior admission audit:

| Review | Whole fields | Pending | Holds |
| --- | ---: | ---: | ---: |
| N01 Elena clean | 12 | 2 | 1 |
| N02 Elena embedded match | 13 | 1 | 2 |
| N03 Elena missing date | 11 | 1 | 0 |
| N04 Elara clean | 12 | 1 | 0 |
| N05 Elena missing decision | 13 | 1 | 0 |

Original whole-field text and declared semantic requirements are unchanged. Only
derived field/statement/work identities and exact location references are rebound
to the tracked inventory. All 61 fields and full context remain present; 52 fields
are unselected rather than assigned new gold. Prior supported labels are not
copied into pending work or re-established by these software tests.

The private acceptance blocks networking and SQLite access, exercises both CLI
modes, checks exact reuse, and verifies **all 1,293 private members of the earlier
admission audit remain intact**. No live call or application database access was
made for this five-capture check. No fresh model or human-quality evidence is claimed.

Private artifacts: [README](../../data/diagnostics/assessment-intake-integration-2026-11-12/README.md),
[intake index](../../data/diagnostics/assessment-intake-integration-2026-11-12/intake/index.md),
[acceptance record](../../data/diagnostics/assessment-intake-integration-2026-11-12/acceptance.json)
and [exact CLI arguments](../../data/diagnostics/assessment-intake-integration-2026-11-12/cli-arguments.json).
Unpublished prose remains in ignored local data. Tracked tests use authored material.
No frontend/build changes occurred, so frontend/build commands are not applicable.

## Recommended next step

Separately qualify the **two October 17 probe archive contracts**, then replay the
remaining seven already-audited reviews through this same intake path. That bounded
local step would verify real compound-obligation, repair-history and unavailable-
authority cases with their existing declarations and holds. Preserve their original
text and gold; do not relax archive authentication to obtain coverage.

Keep live inference paused. A later comparison still needs a materially different
question and defensible whole-claim contrasts. This implementation does not fill
the natural-negative or fresh-family admission gaps, establish necessary edits,
qualify writer preservation or prove better story quality.

Tracker and issue index updated; all fourteen issue bodies and posted URLs unchanged.
CW-007/CW-013 remain open; CW-014 unqualified. **Step 19 IN PROGRESS;
Step 20 NOT STARTED; production prompts unchanged; live calls PAUSED; canary ON HOLD.**
