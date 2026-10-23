# Proposed DeepSeek delivery-layout comparison

Date: **2026-10-23**. **PROPOSED ONLY: not frozen and not approved for inference.**
Production prompts remain unchanged; live calls are paused and the canary is
**ON HOLD**. This follows the [local delivery/aggregation audit](reviewer-delivery-aggregation-audit-2026-10-23.md).

## Question and isolated comparison

Does aligning schema field order improve complete report delivery, and does
placing the group identity first add anything beyond the archived D1 layout?
The latest DeepSeek failures repeat `group_id` before following the required
field sequence. D1 aligns the schema's two lists but leaves that identity fourth;
the proposed D2 puts it first. Local schema equivalence cannot answer whether
either presentation changes generated answers.

Use **48 attempts maximum: eight cases × three layouts × both presentation
orders**, sixteen attempts per arm. Compare the same DeepSeek model against
concurrent controls; Gemma's D stop remains intact.

| Arm | Intervention |
| --- | --- |
| C2 | Exact archived C2 control renderer and contract |
| D1 | Exact archived D1 presentation; aligned property/required order |
| D2 | D1 with record identities first; for these schemas only group order changes |

No M1 ownership card, temporal cue, vocabulary change, evidence-policy change,
schema relaxation, repair pass or additional judge. Keep the original model
aggregate and explanation in all arms. Compute the application-owned aggregate
only after strict validation as a separate local diagnostic view; it does not
change primary scores or add calls.

## Proposed case matrix

| Packet | Purpose |
| --- | --- |
| Historical A00 | Recognition loss plus forbidden broadcast; all four recent C2/M1 reports invalid; three edit groups |
| Historical B10 | Correct discovery plus prohibited alteration; unknown-reference capture and unsupported consultation-before-action premises |
| Historical CN | Real contradiction outside a narrow mandatory test; exposes aggregate/task disagreement without hiding the defect |
| Historical DB | Explicitly mandatory contradiction; includes duplicate-group output and an unsupported pre-existing-contradiction claim |
| Fresh E-clean | Retained discovery, decision and endpoint with one successful optional cleanup |
| Fresh E-compound | Same new family: earlier discovery lost, endpoint violated and independent cleanup succeeds; three complete edit groups |
| Fresh F-narrow | New genuine same-time contradiction outside a narrow retention test |
| Fresh F-broad | Identical F prose with consistency explicitly mandatory |

Historical packets, versions and withheld labels would be carried unchanged.
Fresh E/F require new characters, setting, action structure and prose, not renamed
copies. These are **six scene families**, with related variants inside E/F, not
eight independent stories or 48 independent observations. OR/RO swaps display
order while preserving original/revision identities and source catalogs.

Before freezing, inspect the fresh cases for unambiguous endpoint intervals,
independent optional success, actual same-referent/same-time contradiction and
supported motivation. Bind complete source packets and paragraph groups; do not
pick group boundaries after seeing model output. Avoid treating changed word
count, edit size or one literary preference as the correct answer.

## Scoring and provisional decision rules

Retain strict unique-key JSON, full schema, evidence-reference/source binding and
complete-report validation. Invalid answers get no semantic credit. Record
delivery separately from supported event, endpoint, task, aggregate and group
judgments; inspect every assessment field for unsupported premises. Keep real
craft-defect detection and permitted optional edits visible. A correct target
label does not make a complete report usable.

Create arm/order-masked exports, inspect each valid answer against the complete
source, and seal field-bound notes before decoding. Condition-revealing wording
limits masking; this is factual operator inspection, not independent human
literary preference. Preserve uncertainty. The two CN aggregate errors in the
historical record remain errors even if the separate application view disagrees.

Provisional candidate screen, to be made executable and frozen before inference:

- At least **15/16 valid** candidate reports, including **7/8 fresh-case cells**.
- At least **four paired C2-invalid → candidate-valid-and-usable recoveries**,
  spanning two families and including one case recovered in both orders.
- No loss of a concurrently valid C2 report, usable report, supported target
  judgment or detected real contradiction; no lost successful optional-edit
  control. Count each dimension separately rather than allowing gains to cancel
  losses.
- Both orders and all scheduled cells must complete for a qualified screen. A
  stopped/incomplete run cannot advance. If C2 produces too few failures to test
  recovery, report that limitation; do not add cases, calls or retries.

Evaluate D1 and D2 separately against C2 under the same rules. If both pass,
prefer the already specified D1 unless D2 also provides at least **two paired
valid-and-usable recoveries over D1 with no losses** under the same dimensions.
This is a conservative diagnostic decision, not a significance test or evidence
of production/story-quality qualification. A valid D2 answer paired with invalid
C2 is a delivery recovery, not proof of improved underlying reasoning.

## Budget and stops to freeze

Use `deepseek-v4.1-flash:cloud` through the local Ollama daemon, full prose/context,
the archived temperature **0.2**, top-p **0.95**, seed **20261022**, `think=false`
and `stream=false`. Retain **24,000 input / 8,000 output tokens and 300 active
seconds per attempt**: at most **1,152,000 input / 384,000 output tokens and
14,400 active seconds**. These are reservations, not usage forecasts. At the
previously archived reference rates the reservation is **$0.80640**, with a
proposed **$1.00 planning allowance**; actual charges remain unknown and this is
not a fresh price check.

The local freeze should pin the previous daemon **0.40.8**, full model digest
and capabilities, exact adapter wire requests, source/runtime fingerprints and
durable dispatch accounting. Only subsequent live approval permits discovery
and dispatch. A version/model/capability mismatch must stop for review rather
than silently refresh the baseline. An automatic daemon update during execution
must also stop the run; do not resume across it under the same freeze.

Proposed initial sentinel: **A00 and fresh E-clean, all arms and both orders**
(twelve calls, four per arm), with balanced deterministic arm/order scheduling.
Stop the entire comparison if any arm has zero valid reports, or one structural
failure signature occurs in at least three of its four responses across both
families. Normal-stop invalid reports otherwise remain failed cells, without
repair. Freeze the exact signature classifier and schedule before running.

Any non-200/transport failure, length finish, missing/unknown usage, unexpected
thinking, exceeded reservation, version/digest drift or evidence-integrity
failure stops all further dispatch. Reserve before sending; every attempted
request counts, including failed or interrupted requests. Preserve terminal
gateway chains and unknown usage via the supported audit/export path. No automatic
retry, replacement, arm transfer or optional continuation. Unspent calls from
earlier experiments remain unavailable; this would be a separate 48-call budget.

## Decision requested next

If this design is selected, prepare the fresh packets, exact 48 requests,
gold/source inspection, scoring, order schedule, stops, budget and mocked harness
locally, then present the frozen plan for approval before any live call. Current
layout prototypes are not that freeze and grant no dispatch authorization.

Reliable report delivery would make later semantic and writer tests more
interpretable. It would not establish that the critic recommends necessary edits
or that those edits improve emotion, flow or character. Keep those questions
separate; retain the nine human ties and require grounded complete reviews before
returning to reviewer-driven writer changes. No new human checkpoint or
production gate is proposed. The full workflow canary stays **ON HOLD**.
