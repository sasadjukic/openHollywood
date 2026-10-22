# Proposed isolated reviewer comparisons after the local C2 audit

Date: **2026-10-22**. Status: **PROPOSAL ONLY — NOT FROZEN OR APPROVED FOR INFERENCE**.

The [local audit](reviewer-delivery-semantics-audit-2026-10-22.md) supports testing
three narrow hypotheses separately. Recommend a provisional ceiling of **48 calls**:
three independent 16-call pilots. The previous 64-call allowance is closed and
cannot fund these calls. No requests, new prompts or approval file have been frozen
for this proposal. Production prompts remain unchanged and the canary stays on hold.

## Why these tests are warranted

Gemma's identical output sequence across 32 failures, combined with conflicting
schema presentation orders, supplies a specific delivery hypothesis. The local
prototype preserves the contract and all archived positive controls. A new model
answer is required to learn whether layout affects generation; replay cannot do so.

DeepSeek's remaining failures fall into at least two different semantic problems:
scope over time, and fulfillment terminology that sounds like textual relevance.
Changing both in one arm would make the next diagnosis less informative. The
[explicit contrast design](reviewer-semantic-contrast-design-2026-10-22.md) supplies
unchanged historical failures and fresh positive/counterexample controls.

## Matrix: one changed factor per pilot

Every pilot uses four complete original/revision packets, two arms, both labeled
presentation orders and one shared seed: **4 × 2 × 2 × 1 = 16 calls**. O always
means original and R revision; only their display order changes. This is not a
Gemma-versus-DeepSeek ranking: the models serve different experiments.

| Pilot | Model | Unchanged control arm | Candidate factor | Cases |
| --- | --- | --- | --- | --- |
| D: delivery | Gemma `gemma4:31b-cloud` | Exact C2 instructions and schema presentation | Canonical schema order only; same properties, required membership, judgments and evidence policy | Historical h02, h03; fresh F01 observatory and F04 pottery no-op |
| T: temporal scope | DeepSeek `deepseek-v4.1-flash:cloud` | Exact C2, including existing schema layout | One diagnostic instruction addition distinguishing event, continuing state, final state, express cause and same-time contradiction | Historical h03, h04; fresh F01 permitted departure and F02 true tram contradiction |
| R: request fulfillment terminology | DeepSeek `deepseek-v4.1-flash:cloud` | Exact C2, including existing schema layout | Rename the relation field and its labels to express fulfillment rather than topic relevance; preserve intended decisions and other fields | Historical h03, n03; fresh F05 bakery repair and F06 ferry root/cleanup groups |

The shared h03 packet is intentional, making both semantic failure classes traceable
without modifying its prose. Reused packets do not become independent story samples.
The D layout is **not** carried into T or R. T's instruction is **not** carried into
R. Separate paired results prevent a formatting success from being credited to a
semantic change or vice versa.

T is a test of one temporal-scope instruction, not proof of which sentence in that
instruction causes an effect. Its exact wording remains to be drafted and reviewed
at preparation. It must not include case names, expected answers or a blanket rule
that later text always wins. The unchanged system instruction remains the control.

R's proposed reversible vocabulary mapping is:

| Existing C2 | Candidate vocabulary | Intended judgment |
| --- | --- | --- |
| `request_relation` | `request_fulfillment` | Does this complete edit carry out the request? |
| `direct` | `fulfills` | Carries out the requested change |
| `adjacent` | `supports_other_edit` | Supports another change; does not independently authorize it |
| `unrelated` | `does_not_fulfill` | Does not carry out the request, including an edit that opposes it |
| `uncertain` | `uncertain` | Evidence or grouping does not support one clear judgment |

Apply this mapping consistently to the diagnostic system wording, schema and
validator; leave `edit_support`, `dependency`, task judgments, evidence, prose and
all other instructions alone. Normalize only these declared field/enum aliases for
paired analysis after strict validation. Never normalize duplicate keys, malformed
IDs or unsupported evidence. Any R gain may show a better interface vocabulary,
not new ability to judge permission or better fiction. Historical C2 scores stay
unchanged. If local review finds the proposed mapping changes the intended answer
space rather than naming it, resolve that before freezing R.

## Proposed ordering and systemic-delivery stops

Freeze a deterministic, balanced schedule. Interleave the two arms within each
case/order block; counterbalance which arm is dispatched first. Do not run every
control first and every candidate later. Archive and verify model metadata before
dispatch using the existing reproducibility rules.

For each pilot, the first **eight calls** cover two different families, both arms
and both display orders:

- D sentinel families: h02 and F01.
- T sentinel families: h04 and F02.
- R sentinel families: n03 and F05.

After the complete sentinel block, stop that pilot if **either arm has 0/4 valid
answers**, or if **one arm has the same blocking structural signature in at least
3/4 answers spanning both families**. Signature examples include the same duplicate
root key or the same required-evidence omission. A completely failing unchanged
Gemma control can therefore stop D even if its candidate succeeds: those four
paired cells already provide a useful delivery signal, and the remaining cells
are not necessary to establish that the control is still systematically failing.

Retain all attempted failures and all successful sentinel answers. Mark remaining
cells **unstarted due to the declared stop**, not failures or successes. Do not
reroll, repair, collapse duplicate keys or change the contract mid-run. An invalid
answer below the sentinel threshold still fails its cell. There are no additional
model calls to judge, repair or retry the outputs.

The pilots have separate allowances. A D stop does not itself block T or R, but
unused D calls cannot be transferred. Auth, transport, cancellation, missing
capture/usage, unknown outcome, identity drift, budget or source-integrity failures
stop the entire run for inspection. Reserve each dispatch durably before sending;
an unresolved reservation prevents a resume. In-budget truncation fails its cell;
never raise the output cap or retry it. These rules must be implemented and tested
before a live freeze.

## Budget proposal and preparation requirements

| Limit | Proposed maximum |
| --- | ---: |
| Total inference calls, including any failures | **48** |
| Gemma / DeepSeek | **16 / 32** |
| Attempts per scheduled cell | **1** |
| Retries, repairs, writers, other models, canary | **0** |
| Input / output tokens per call | **24,000 / 8,000** |
| Context reservation per call | **32,000** |
| Aggregate input / output reservation | **1,152,000 / 384,000** |
| Active call time per call / total | **300 / 14,400 seconds** |

Reuse temperature **0.2**, top-p **0.95**, thinking **false**. Select and freeze one
seed for every paired arm/order at preparation. One seed makes this a pilot; it
does not establish sampling robustness or a general order effect. Record observed
usage separately from the reservations. Recheck pricing and the planning allowance
at preparation; these token limits are not an enforceable billed-dollar cap.

Before requesting approval for live execution:

1. Assemble full packets, assignments, catalogs, task IDs and complete edit groups
   for F01/F02/F04/F05/F06. Preserve historical packet hashes exactly. Finish the
   scoped expectations and ambiguity audit, including F06 group boundaries.
2. Freeze exact diagnostic candidate wording and the R mapping. Prove that D changes
   only schema order, T only its declared instruction, and R only its declared
   vocabulary. Do not change production prompts or broaden mandatory obligations.
3. Freeze all requests, display/dispatch order, seed, per-case answer keys, support
   inspection rubric, budget and stop rules. Keep scoring and case labels out of
   model messages. Record the provider/model identity and capability requirements.
4. Verify the actual adapter wire requests with HTTP mocks, budget/receipt replay,
   interruption/resume and sentinel-stop behavior. Have no inference entry point
   bypass the frozen ledger or the approval check.
5. Present the final plan for approval, including full prose/context and the Ollama
   Cloud destination through the local daemon. This proposal is not that approval.

## Scoring and decisions

For every attempted cell, report separately: strict delivery, declared labels,
supported explanation and overall usable assessment. A report with correct labels
but an invented cause or contradiction is not usable. Schema success alone is not
semantic success. Inspect full prose under masked arm identities and seal notes
before unmasking. Preserve uncertain interpretations and sensitivity analyses.

For D, the primary contrast is paired strict delivery and the frequency of each
blocking signature. Report task/evidence defects even if endpoint duplication
disappears. Do not infer semantic superiority from invalid control answers.

For T, inspect event/endpoint separation and explanation support, including F01's
permitted transition and F02's actual simultaneous contradiction. Correctly finding
a contradiction does not make the still-satisfied endpoint fail.

For R, compare the declared alias-mapped fulfillment judgment while checking that
correct permission/dependency judgments remain correct. F05 must remain a permitted
optional repair. In F06 the valid duplicate repair must not be condemned merely
because the root change is bad, and callback consistency cannot license that root.

Proposed advancement rule: require **8/8 candidate deliveries**, no lost paired
control successes, every designated permissible/no-op control correct in both
orders, and improvement on the targeted failure in both orders of at least one
family. For semantic pilots, explanations must support those gains. Otherwise
retain a limited observation or stop; do not combine partial gains across pilots
to manufacture a pass. If a sentinel stops the pilot, describe it as incomplete
and do not apply the eight-cell advancement rule to four observed candidates.

Even a fully passing pilot only supports preparing a broader diagnostic repeat.
It does not qualify a production critic, select a writer, release the canary or
establish a complete-story benefit. The continuing-state contrast F03, explicit
causal requirements, requested-but-impermissible changes and ambiguous narration
remain documented follow-ups, not hidden extra calls in this budget.

Story quality remains an independent evaluation: machine-prepared mechanics and
evidence, followed by human judgments of feel, emotion, flow, character and
story-breaking details. Preserve the nine human ties and allow meaningful prose
variation. **Step 19 IN PROGRESS; Step 20 NOT STARTED.**
