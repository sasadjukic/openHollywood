# Isolated reviewer pilots: interrupted execution, 2026-10-22

**The approved run stopped after 10 of 48 allowed inference attempts.** Nine returned complete responses; the tenth returned HTTP 500 with no answer or usage. The frozen global stop rule ended execution. No retry, replacement, budget transfer or later pilot dispatch occurred. This is an incomplete comparison, not a completed 48-cell result.

Gemma's D1 schema-layout candidate produced four valid, label-correct, supported reports against four invalid C2 controls across two families and both presentation orders. Retain this as limited delivery evidence. DeepSeek's one T1 response had correct labels but repeated an unsupported contradiction claim. Its paired C2 request failed at the provider boundary, so no T1 comparison is available. R1 was never reached. **All three frozen advancement decisions are `incomplete_no_advancement`.**

Production remains **prompt 61 / graph 9 / fulfillment policy 1**. Production prompts, schemas, routing and human checkpoints are unchanged. The full workflow canary remains **ON HOLD**; Step 19 is **IN PROGRESS**, Step 20 **NOT STARTED**.

## Authorization and frozen design

The user approved the [frozen three-pilot plan](../handoffs/reviewer-isolated-pilots-frozen-plan-2026-10-22.md), including full unpublished prose/context to Ollama Cloud through the local Ollama daemon. Approval was recorded against preparation seal:

`7256b677fab8fa4f226a0a3e0595339809c6f2af35147e751055df8fe6595cbe`.

Each pilot owned 16 slots: four families × two arms × two presentation orders, seed 20261022, temperature 0.2, top-p 0.95, `think:false`, one attempt per cell. D compared Gemma C2/D1 schema presentation; T compared DeepSeek C2/T1 temporal scope; R compared DeepSeek C2/R1 fulfillment vocabulary. C2 controls were unchanged. The prepared cases, requests, scoring, budgets, stop rules and runner were not changed during execution or inspection.

Preflight matched both exact deployments and archived metadata before inference, followed by per-cell metadata checks. The exact sent payloads match all ten frozen requests. Local digests and a seed do not guarantee immutable remote weights or independent replications.

## What ran and what stopped

| Pilot / arm | Sent | Complete responses | Strictly valid | Correct frozen labels among valid | Supported usable reports |
| --- | ---: | ---: | ---: | ---: | ---: |
| D / Gemma C2 | 4 | 4 | 0/4 | Not scored | 0/4 |
| D / Gemma D1 | 4 | 4 | 4/4 | 4/4 | 4/4 |
| T / DeepSeek C2 | 1 | 0 | No answer | Not scored | No answer |
| T / DeepSeek T1 | 1 | 1 | 1/1 | 1/1 | 0/1 |
| R / DeepSeek C2 | 0 | 0 | Not observed | Not observed | Not observed |
| R / DeepSeek R1 | 0 | 0 | Not observed | Not observed | Not observed |

Each arm was planned for eight cells. Fractions above describe only observed responses and do not replace the frozen qualification denominators. Invalid responses receive no semantic success credit; the HTTP failure is not a semantic judgment.

Pilot D completed its first eight sentinel cells: historical duplicate removal `h02` and fresh permissible departure `F01`, each in OR and RO order. The control was **0/4 valid**, with the same `duplicate_key:$.endpoint_check` signature in all four answers across both families. Either condition required a stop. The candidate's success did not override that rule. D's remaining eight cells (`h03`, `F04`) were not sent.

Pilot T then sent `T-h04-T1-RO`, which completed, followed by `T-h04-C2-RO`, which returned HTTP 500. That terminal stop left T's other fourteen cells and all sixteen R cells unstarted. Thus **38 cells were never dispatched: eight stopped by D's sentinel, thirty by the global terminal condition**. Unstarted cells are neither passes nor observed failures. No allowance was transferred or spent on retries.

## D1: a bounded improvement in delivery

All four C2 responses repeat the root `endpoint_check` after `overall_assessment`, matching the earlier delivery pattern. In every new capture, both endpoint occurrences are identical. Lossless inspection retains both occurrences; none is selected, collapsed or repaired. Each root occurrence was also checked independently for schema, task/fact/group identity and evidence-reference defects; no additional defect of those kinds was found in these four responses. This does not make the complete objects valid.

D1 changes schema presentation only: a consistent root layout and matching nested property/required ordering. Its four responses contain unique keys and pass the unchanged constraints. Across the two observed families, this supports schema layout as a useful generation factor. It does not isolate root order from nested order, demonstrate reliability on harder cases, or resolve delivery for other interfaces and models.

The four valid reports also pass source-grounded inspection:

- On `h02`, they recognize the removal of one literal duplicate, retain touch/pull and the decision to enter, and distinguish that decision from actual entry. Both boots remain outside at the endpoint. No extra causal requirement is imposed.
- On `F01`, they recognize the permitted exit after the agreement while the record comparison remains pending. Earlier staying followed by leaving is treated as a compatible transition. The added actions support their local craft interpretations; the claimed agency/naturalness gains remain debatable aesthetic judgments, not human preference findings.

D1 has only **4 of its planned 8 responses**, and neither its harder `h03` case nor its no-op `F04` case ran. The frozen requirement for a complete pilot and 8/8 candidate delivery is unmet. Retain the observations; do not call the candidate qualified or the issue closed.

## T1: correct labels with an unsupported explanation

The sole T1 answer on `h04`, in RO order, correctly preserves the earlier discovery and truce and correctly rejects the later departure against the required locked-room endpoint. Its task, fact, endpoint, mandatory-failure and group labels all match the frozen key.

However, its naturalness assessment says the departure “contradicts the immediately preceding sentence that they remained there.” Its edit-group explanation repeats that premise. The source first depicts remaining, then unlocking the door, then leaving. These are sequential states, not incompatible assertions about the same instant. The departure violates the assigned final state; that does not make the preceding state logically impossible.

Other concerns in the answer have separate support: the abrupt appended stage direction, the lost closing standoff, and the preemption of Maya's later planned exit on her own terms. The latter was checked against the supplied character arc and later scene plan. Elias's earlier dialogue about verifying the route is not an immutable simultaneous narrator assertion. None of these concerns rescues the false contradiction premise.

Accordingly, both group-explanation support and comparative-premise support fail; temporal-target correctness is false and the report is **not usable** under the frozen rule. T1's explicit temporal instruction did not prevent this particular failure. With no completed paired control, no second order and no fresh temporal contrast observed, this run cannot estimate whether T1 helps, harms or leaves the failure rate unchanged.

R1 has **no evidence** from this run. Its vocabulary hypothesis remains untested.

## Terminal failure and local reporting limitation

The failed cell preserves the sent request, reservation, model check and raw HTTP response. The body contains only an internal-server-error message, reference `af27859b-4eaa-4c6e-af8d-ea68d1a3128f`. It contains no model answer, finish reason or token usage. The capture identifies an HTTP error returned through the local daemon; it does not establish the underlying cause or whether cloud computation/billing occurred.

The runner's `ModelGatewayError` handler checks whether a captured response is an allowed length failure. Evaluating this HTTP-500 body raises `ValueError("non-success provider status")`, so `TERMINAL.json` records `ValueError` instead of the original gateway error. The raw HTTP status and error body preserve the cause visible to us. Execution still fails closed; no further request follows.

The normal ledger replay and inspection export require a receipt for every reservation. They therefore reject this unresolved cell. An **offline post-run audit** replays the nine sealed receipts, verifies the final failed dispatch separately, and exports the completed assessments for inspection. It neither creates a success receipt for the error nor makes the full ledger complete or resumable. The original reservation, captures, terminal marker and frozen runner remain intact.

Before another live run, the useful local follow-up is to add explicit non-200 terminal-evidence fixtures and a supported terminal audit/export path that preserves the gateway error chain and unknown usage. Any continuation policy must be specified and approved in advance, carry forward all ten attempts, and retain D's sentinel stop. The unused numerical allowance is not permission to override this run's terminal rule. No continuation, prompt change or new live plan was made here.

## Budget, inspection and verification

**10/48 attempts were reserved and dispatched: Gemma 8/16, DeepSeek 2/32.** The failed HTTP request counts as an attempt. Nine complete responses report **87,201 input tokens, 7,737 output tokens and 35.099 seconds of measured active inference time**. All nine are within their individual 24,000-input / 8,000-output / 300-second limits; none is truncated. Usage and active inference time for the failed request remain unknown. Its full reservation is retained, rather than reporting zero consumption. Actual billed cost is unknown.

Applying the already-frozen reference rates to the nine known usage records gives **$0.01838006**, excluding the unknown failed request. This is an estimate, not a bill or a dollar cap. The original maximum reservation estimate and $0.80 planning allowance are unchanged.

All five valid assessments were read against source prose, assignments, edit groups and relevant canonical context; all four invalid responses were separately read losslessly. The review export follows the frozen shuffle and removes model/arm/order identifiers. Notes were sealed before consulting its key. **Masking was limited:** terminal diagnosis had already exposed the sole T1 response and identity, and the Gemma delivery pattern can reveal condition even without the key. This is operator support inspection, not independent blind human validation.

Post-run verification passes **10 offline tests**, Ruff lint/format and strict mypy across three new private analysis scripts. Tests reproduce the audit, source-bound notes and frozen incomplete decisions; retain strict duplicate rejection; confirm normal replay still rejects the unresolved reservation; and reject altered raw bodies, payloads, receipts, terminal counts and illegal later dispatch. The initial test run encountered sandbox temporary-directory permissions; a fresh workspace test directory resolved that infrastructure failure. Its original XML is retained. The preparation's **152-test** evidence remains separate; those are not additional live calls.

The preparation seal, approval, ten wire requests, nine cell seals, D sentinel decision and inspection bindings reverify. No production source or client change requires a new application build in this documentation/diagnostic-evidence task. The tracker and local issue index are updated; all fourteen user-posted GitHub links and issue bodies are preserved. No GitHub issue was edited externally or closed.

## Evidence and story-quality boundary

Private, ignored local evidence:

- [Approval](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22/approval.json), [live bundle](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/), [terminal audit](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/terminal-audit.json), [results](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/results.json).
- [Lossless invalid-response inspection](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/raw-inspection.json), [operator notes](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/inspection/notes.json), [masking disclosure](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/inspection/masking-disclosure.json), [terminal marker](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/TERMINAL.json).
- [Post-run verification](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/verification.json), [evidence manifest](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/evidence-manifest.json), [execution closure](../../data/diagnostics/reviewer-isolated-pilots-v61-2026-10-22-live/closure.json).

These local links do not make private prose/captures publicly available. Public interpretation follows the [earlier audit](../handoffs/reviewer-delivery-semantics-audit-2026-10-22.md), [semantic contrast design](../handoffs/reviewer-semantic-contrast-design-2026-10-22.md), and [completed human review](../handoffs/critic-writer-human-review-results-2026-10-20.md).

The reader's nine overall ties remain valid. Report validity and supported local judgments do not establish better stories; byte preservation is not a quality proxy. Keep mechanical checks and assignment/request evidence machine-prepared, and reserve human evaluation for feel/emotion, flow, character and story-breaking concerns. This run qualifies no production critic, writer-selection policy or whole-story quality gain, and leaves the canary on hold.
