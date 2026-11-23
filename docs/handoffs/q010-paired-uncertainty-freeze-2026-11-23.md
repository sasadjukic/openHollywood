# Sol-high paired uncertainty diagnostic

**Decision requested.** Authorize up to 16 input counts followed by at most 16 generations using `gpt-6.1-sol` with high reasoning. Both OpenAI endpoints receive the complete admitted story packet and assessment brief for that case. Each slot can be used once. The approval covers only this diagnostic. Production prompts retain their current text. The workflow canary remains on hold.

## Question and single change

In the saved Q010 assessment, Sol correctly located Elias moving toward the threshold and recognized that the draft leaves the crossing unsettled. It nevertheless labeled the whole claim `unsupported`. This comparison asks whether one clarification helps Sol label that evidence `uncertain` while retaining the distinction between a contradiction, a fact left open in a complete scene, and a missing scene. [Q010 diagnosis](q010-label-audit-2026-11-22.md)

**B** uses the original diagnostic system message. Its definition reads “Uncertain means material evidence is unavailable and no supplied evidence decisively contradicts the claim.”

**C** inserts one sentence immediately after that definition.

> Material evidence can be unavailable even when the relevant source is complete but leaves the material fact undetermined.

The exact requests use the same versioned sources, whole claim, observation time, work brief, citation registry, structured output schema, model, settings and limits within each pair. The renderer checks the single substitution against the complete serialized bodies independently at both endpoints. The neutral user message includes the admitted packet and brief and a document view for resolving registered citations. Gold, case-state assignments, authored readbacks and prior Sol responses stay with the scorer. P01 preserves Q010’s original prose and claim in the admitted diagnostic packet, which also includes an authored eyewitness. Each arm receives a new, independent request. [Admitted cases and original seal](q010-endpoint-controls-2026-11-23.md)

## Cases and dispatch order

| Case | Scene family | Endpoint fact | Whole-claim gold | Order |
| --- | --- | --- | --- | --- |
| P01 | The Pristine Lure | Crossing remains open in the complete draft | uncertain | B, C |
| P02 | The Second Crescent | Wings explicitly motionless at the flash | unsupported | B, C |
| P03 | The Pristine Lure | Draft missing after an earlier witness saw Elias pass the shoes | uncertain | C, B |
| P04 | The Second Crescent | Wings moving at the flash | supported | C, B |
| P05 | The Pristine Lure | Leading foot crossing the sill at the cut | supported | B, C |
| P06 | The Second Crescent | Silver markings visible, wing movement unresolved | uncertain | C, B |
| P07 | The Pristine Lure | Both feet planted short of the sill at the cut | unsupported | C, B |
| P08 | The Second Crescent | Draft missing after an earlier witness saw Inez lift the cover | uncertain | B, C |

Read the table top to bottom for the count phase, then repeat the identical order for generation. Each arm appears first four times, twice per family and once per evidence state. Each case has one observation per arm. [Exact request bodies](../../data/diagnostics/q010-paired-uncertainty-2026-11-23/requests/) · [Slot order, destinations and body hashes](../../data/diagnostics/q010-paired-uncertainty-2026-11-23/plan.json)

To inspect one complete pair, open the Elias anchor’s [baseline count](../../data/diagnostics/q010-paired-uncertainty-2026-11-23/requests/P01-B-input_count.json), [clarified count](../../data/diagnostics/q010-paired-uncertainty-2026-11-23/requests/P01-C-input_count.json), [baseline generation](../../data/diagnostics/q010-paired-uncertainty-2026-11-23/requests/P01-B-generation.json) and [clarified generation](../../data/diagnostics/q010-paired-uncertainty-2026-11-23/requests/P01-C-generation.json).

## Independent scoring

1. **Evidence.** First inspect the evidence worksheet by opaque response ID. It exposes the case, citations and verbatim reason, with the returned label, arm and dispatch order withheld. Score pass or fail and record a passage locator and rationale before joining the label. A reason can reveal its author's conclusion. An equivalent precise locator or accurate paraphrase qualifies. A bare full-draft reference, material overread or attribution to the wrong source fails.
2. **Whole claim.** Compare the returned support label directly with the sealed gold. A sound reason cannot repair a wrong label. Likewise a matching label earns no evidence credit by itself.
3. **Report both outcomes.** Preserve each returned label, citations, reason, slot disposition, latency and known usage. Report both axes and the joint result for each B/C pair. Only complete, bound, in-budget observed generations in a closed journal qualify for scoring. Leave other outcomes unscored. A partial run can describe eligible deliveries but cannot satisfy the comparison gate.

All eight first actions are established. For a **complete draft**, evidence must locate the first action in S01 or S02 and the endpoint in S02. A contradiction requires an incompatible observation at the specified instant. On an open ending, the answer must explain what the depicted passage shows and what remains undetermined. For a **missing draft**, the answer must cite both S01 and S03 and explain why the earlier witness cannot establish the endpoint. S03 documents source availability. The frozen gold supplies exact versions, witnesses, spans and acceptable readings. [Scorer-only gold](../../data/diagnostics/q010-endpoint-controls-2026-11-23/frozen/gold.json)

**Decision after scoring.** Recommend a fresh repeat only if all 16 generations qualify, both open cases pass both axes in C, at least one of them missed an axis in B, and all six C controls pass both axes without a baseline-pass-to-fail change. Compare each control axis individually. A joint pass in both arms is a tie. If both open baselines already pass, record that the comparison had no recovery headroom. Treat incomplete delivery as inconclusive. Other outcomes hold the change. Two scene families and one observation per cell can justify a repeat. They cannot establish a production effect or an improvement in story quality.

## Budget and stops

| Resource | Frozen ceiling |
| --- | --- |
| Input counts | 16 serial POSTs to `https://api.openai.com/v1/responses/input_tokens` |
| Generations | 16 serial POSTs to `https://api.openai.com/v1/responses`, after all counts pass |
| Total network attempts | 32 across both endpoints, zero retries or replacement slots |
| Per generation | 8,192 input tokens and 4,096 output tokens including reasoning |
| Aggregate generation budget | 131,072 input and 65,536 output tokens |
| Cost at the pinned repository rates | Maximum estimated generation cost $0.06144 each, $0.98304 total, assuming uncached input. Actual billing is unknown. |
| Time | 120 seconds per count, 300 per generation, 1,800 seconds for serial dispatch |

Before dispatch, verify the approval digest, source and gold seals, request bytes, implementation and unused single-use journal. Each count must return HTTP 200 and a positive token count within input, context and estimated-cost limits. Stop globally on the first failed count. During generation, stop on a non-200, timeout, transport failure, refusal, truncation, model mismatch, ambiguous or malformed final, invalid claim/citation, missing required usage, or exceeded limit. Cancellation, drift or an interrupted dispatch blocks further sends. Retain all recorded terminals and unknown usage. A structurally valid semantic miss uses its slot and the scheduled experiment continues.

## Local verification and approval

The frozen manifest and the exact 32 request bodies are private workspace artifacts. The tracked [renderer and scoring contract](../../scripts/q010_uncertainty_plan.py), [single-use runner and offline audit](../../scripts/q010_uncertainty_run.py) and [local qualification tests](../../tests/api/test_q010_uncertainty_freeze.py) reproduce the check with the admitted archive present.

**Approval SHA-256** `3600fc37fcd142cd1fe733895f19c77a1ca4a1aa0595d18c4481524840869729`

- The issued manifest reproduced byte-for-byte. All 32 exact HTTP bodies matched their hashes, source versions, document fields and citation maps. Their sizes range from 7,328 to 14,922 UTF-8 bytes. The live ledger reads `ready`, with 32 unattempted slots and zero eligible deliveries.
- A separate injected transport exercised all 16 counts before all 16 generations, including structurally valid wrong answers. An over-budget 16th count prevented every generation. Duplicate count keys, HTTP 500, an absent-draft citation, missing usage and a mismatched model each stopped at the expected slot.
- Interrupting the first injected generation preserved its intent without a terminal. Every restart attempt was rejected. Changed request bytes, a mismatched approval and a damaged terminal chain were rejected. The evidence worksheet kept all 16 fixture identities distinct when tested in memory and excluded every injected delivery from the live scoring path.
- All 272 focused tests passed, including ten checks on this freeze. The existing work-brief tests emitted nine Pydantic serialization warnings. Repository-wide Ruff lint, formatting and strict mypy passed across 366 Python files. [Local regression results](../../data/diagnostics/q010-uncertainty-verify-20261123/local.xml)

To recheck the issued freeze locally, run `python -m scripts.q010_uncertainty_run verify --approved-plan-sha256 3600fc37fcd142cd1fe733895f19c77a1ca4a1aa0595d18c4481524840869729`. The `audit` subcommand lists all fixed slots. After an approved run, `evidence-sheet` exports the label-masked rows from eligible deliveries.
