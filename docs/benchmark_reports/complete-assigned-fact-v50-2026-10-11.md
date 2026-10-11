# Complete assigned fact means met v50: 2026-10-11

The focused instruction change, local checks and twelve approved live probes are
complete. All four v49 false passes become correct turning-point blockers; all
six valid drafts remain accepted. Four probes need a structural retry, including
two whose first responses still select met while acknowledging the wrong fact.
This supports the final judgments in this frozen sample, not a general reliability
claim. Step 19 remains IN PROGRESS; Step 20 is NOT STARTED.

## Problem and change

The [v49 comparison](mandatory-assignment-checks-v49-2026-10-11.md) retained four
false passes on missing-turn controls. Separate required checks exposed an
interpretation problem: the critic could acknowledge the wrong date yet mark a
general date-realization action as met. Another assessment accepted a supposed
future origin instead of the specifically assigned future date. All valid unmet
checks produced blockers, so the next change targets the meaning of met.

Production prompt v50 / graph v9 refines the existing obligation instruction:

- Compare the complete assigned fact or state, including every explicit
  condition, with what the cited draft establishes.
- Select met only when that whole obligation holds. Performing a named action,
  noticing an object or serving a similar dramatic purpose cannot substitute for
  different or missing required content.
- Use broader context to interpret the draft, without replacing an absent or
  contradictory required fact. An absent or contradicted required condition is
  unmet even if the scene achieves its intended dramatic effect.
- Actions, embodied reactions and indirect narration remain valid evidence when
  they establish the assigned fact. Literal plan wording, explicit decision
  sentences and promises to continue afterward are not required. Do not add
  conditions or demand more explicit prose.

The existing assessment field carries this concise comparison. Its 600-character
bound, evidence handles and met/unmet status remain unchanged. No schema field,
keyword classifier or model-specific story example is added. The same instruction
reaches initial reviews, revision reviews and structural retries for local/cloud
profiles. Critic retry policy advances to 17 because its operation rule and
targeted check directive now carry the refined meaning; other specialists retain
policy 10.

This is a prompt refinement within [ADR 0033](../adr/0033-independent-mandatory-scene-checks.md).
Canonical artifacts, runtime validation, blocker routing, consolidation, original
repair links, classification retention and diagnostic schemas are unchanged.
Writer instructions and call/revision allowances are unchanged. No migration,
dependency, specialist or API/client change is needed.

## Local verification

Eight new regressions verify initial/revision delivery for local/cloud profiles,
exact assignment preservation, the unchanged evidence-bound schema and structural
retry delivery without promoting review-format errors into manuscript defects.
Existing instruction-size checks continue to bound the other critic guidance.
These tests verify delivery and compatibility, not model understanding.

All required checks pass: **934 Python tests**, **11 frontend tests**, Ruff lint
and formatting, strict mypy across **190 files**, frontend formatting/lint/type
checks and the production build. Frozen request/code/source and database hashes
verify. No API/client contract regeneration is needed.

All **15 saved v49 responses** replay without edits: twelve identical canonical
results and three identical structural rejections, with the same diagnostic
audits and retained classifications. This includes the four incorrect passes.
The new definition instructs the model; it does not retroactively reinterpret a
valid response or derive a blocker from assessment wording. Semantic improvement
requires fresh model evidence.

## Controlled comparison

The twelve cases use the same v49 drafts, immutable artifact identities, historical
source lineage, synthetic endpoint, decision variants, seeds, order, settings
and budgets. Every first user message, including the output schema, compares
identically. Only the system instruction changes, growing by **719 characters**
per first request. This is a measured sample delta, not a universal token estimate.
The changed rule also appears in any bounded structural retry.

The six future-date cases test continued acceptance of valid indirect/action-based
fulfillment. The six present-day controls test whether the exact missing temporal
condition is now treated as unmet across implicit, prior-decision and later-decision
wordings. The assessment separately inspects required versus observed facts in the
cited evidence, outcome checks, original no-match repairs, boundary checks and
generic complaints. First-attempt validity and final results after retry are
reported separately.

The limit is twelve probes and **24 calls**, with at most one structural retry per
probe and no rerun of a valid judgment. Per-call ceilings remain 24,000 input /
8,000 output tokens. The maximum estimate is **USD 0.15744**, using recorded
October 8 rates of USD 0.14/M input and USD 0.40/M output. Actual provider charges
remain unknown. Preparation made no model calls. The user subsequently approved
the exact frozen plan: "Yes, run the twelve v50 probes".

Private evidence is under `data/diagnostics/complete-assigned-fact-v50-2026-10-11/`:
`experiment.py`, `plan.json`, `approval.json`, `prepared/*.json`,
`offline-verification.json`, `live/`, `assess.py`, `assessment.json`,
`postcheck.json`, `record_semantics.py`, `semantic-assessment.json` and
`closure.json`. The plan pins code, source, request and database hashes. Historical
v49 evidence hashes verify against its sealed closure. Approval is bound to the
v50 plan. All sixteen saved responses replay without edits, with exact request
reconstruction and matching canonical results or structural errors. Original
repair tests remain intact; each negative case introduces exactly one new repair
target. There are no writer calls, canonical changes or full-story runs.

## Live results

The twelve probes use **16 calls**: eight valid first responses and four successful
bounded structural retries. No retry is exhausted and no valid response is rerun.
All twelve final judgments agree with the inspected assigned facts.

| Draft condition (two seeds each) | v49 final result | v50 final result | v50 retries |
| --- | --- | --- | --- |
| Future date, implicit decision | 2 passes | 2 passes | 0 |
| Future date, decision before test | 2 passes | 2 passes | 0 |
| Future date, decision afterward | 2 passes | 2 passes | 0 |
| Present-day date, implicit decision | 2 turning-point blockers | 2 turning-point blockers | 1 |
| Present-day date, decision before test | 2 false passes | 2 turning-point blockers | 1 |
| Present-day date, decision afterward | 2 false passes | 2 turning-point blockers | 2 |

All six negative cases cite the card's present-day date and Elena's recognition
that it is today, then identify the missing ten-year future date. Each yields one
blocking `scene_assignment:turning_point` issue. All six positive cases cite the
2034 card date, the 2024 current date and the ten-year realization.

All twelve outcome checks remain met, as do the original no-match repair checks.
In all four implicit-decision cases, the critic cites Elena retrieving her journal
and trying to reproduce the handwriting as evidence of a decision, together with
the inconclusive comparison. No explicit decision sentence or additional promise
to continue is demanded. All twelve boundary checks report no overrun. No extra
outcome complaint, independent craft defect or duplicate repair target appears.

**First-response reliability did not improve:** valid first responses fall from
9/12 in v49 to 8/12 in v50. The four retries matter to interpreting the result:

- Both present-day/decision-after first responses select met despite acknowledging
  that today's date contradicts the assigned future date. Seed 19103 still invokes
  a similar dramatic purpose; its assessment exceeds 600 characters. Seed 19104
  fails the met/null-repair requirement. Both also contain a generic comparison
  string instead of the required object. Each retry produces a concise unmet
  turning-point check and one blocker. These were rejected responses, never
  accepted passes; runtime validation did not infer the fact from prose.
- Seed 19104's present-day/decision-before and implicit cases already have correct
  unmet native checks, but their generic repeated complaints use comparison text
  instead of an object. Existing retry instructions retain the valid assignment
  classification. Both retries return the required comparison object and link;
  consolidation leaves one blocker per case.

Usage totals **216,532 input / 21,654 output tokens**. At the recorded October 8
rates, the estimate is **USD 0.03897608**, below the USD 0.15744 cap. Provider
receipts report cost basis unknown; their zero estimate is not evidence of zero
charges. Actual billing remains unknown.

## Remaining qualification

Keep v50 stable and test transfer before adding more instruction or schema. The
next focused comparison should use a different scene, pairing a complete assigned
fact shown through actions or indirect narration with a similar dramatic effect
that omits or contradicts a required fact. Include a genuinely missing decision
beside a valid action-based decision, and track first and final responses separately.
No further model calls are authorized or made by this report.

This comparison involves one scene/model, two paired seeds, six textual variants,
synthetic decision sentences and an explicit endpoint. It has no missing-decision
negative control. The result establishes improvement in these final judgments;
it does not establish cross-provider reliability, writer improvement, full-story
repeatability, human preference or cost acceptance. Residual first-response
inconsistency remains visible and should not be hidden by the successful retries.
