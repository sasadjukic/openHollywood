# Output-contract comparison attempt, 2026-10-19

**STOPPED BEFORE INFERENCE — 0/74 model calls; both comparisons remain unrun.**
The approved [frozen plan](fulfillment-output-contract-v61-plan-2026-10-18.md)
passed its local integrity checks. The operator then failed to connect to the local
Ollama endpoint during model discovery. No experimental response exists to score.
Production prompt 61 / graph 9 / fulfillment policy 1 remain unchanged.
**Step 19 IN PROGRESS; Step 20 NOT STARTED; canary ON HOLD.**

## What happened

The user's October 19 approval was recorded against plan SHA-256
`c8fb871abe6a9e9f4d432dd7a7a47a696dce0547cf671ccd372318a369c426c9`,
the 74-call ceiling, full unpublished fictional prose/critic/context payload,
Ollama Cloud through the local daemon, and canary authorization false.

The unchanged frozen operator ran its `all` phase. Before dispatching any model
request, `model_check()` called `OllamaGateway.list_models()`. Its catalog request
was `GET /api/tags` at the adapter's configured local base URL,
`http://127.0.0.1:11434`. The transport raised
`httpx.ConnectError: All connection attempts failed`; the adapter surfaced
`ModelGatewayError: Ollama is unavailable` (`PROVIDER_UNAVAILABLE`). The process
exited with code 1 and removed its operator lock.

This establishes that the configured local service was unreachable from that
execution. It does not distinguish a stopped daemon from another local connectivity
problem. No catalog response arrived, so the pinned model's availability/digest
could not be verified. This is not a Cloud model refusal, malformed critic output,
truncation or semantic failure.

The error occurred before `run_matrix()` and before any request/reservation write.
There are **zero inference requests, reservations, outcomes, response captures or
completed probes**, and no successful model-check or phase-completion record.
There was one catalog-discovery operation; this is separate from the inference
budget. No fictional prose/context was transmitted by this attempt.

## Results and budget accounting

| Comparison | Planned calls | Dispatched | Responses | Unobserved |
| --- | ---: | ---: | ---: | ---: |
| A: F1/F2 repairs and F3 focus | 20 | 0 | 0 | 20 |
| B: V0/V2/V3 comparative reviews | 54 | 0 | 0 | 54 |
| **Total** | **74** | **0** | **0** | **74** |

F1/F2 each have eight unobserved cells; F3 has four. V0/V2/V3 each have eighteen.
F3's four delegated F2 native-control observations are also unavailable; they are
not extra cells. No arm has an observed success or failure rate, paired improvement,
preservation finding or literary-quality result. Qualification is **not evaluated**.
The earlier fake-provider verification remains harness evidence only.

Inference input/output tokens, active inference seconds and inference reservations
are all zero. No inference charge is inferred; account billing was not queried.
All 74 inference slots are unused, but the frozen stop rule does not authorize an
automatic restart. The run made no retry, fallback-model request, writer call,
prompt change or canary call.

## Stop decision and next boundary

The frozen plan explicitly makes transport failure a whole-run stop and permits
no transport retry. The adapter's generic `retryable=True` classification does
not override that experiment-specific rule. The sole continuation exception is a
fully captured, correctly identified, in-budget `length` inference response;
that exception does not apply to this discovery failure.

Consequently the attempt is closed at zero inference calls. A fresh preflight
requires the local Ollama service to be available and an explicit go-ahead to
retry after this stop. The same frozen cases, requests, scoring and cumulative
74-call ceiling can be retained; no experiment or production-prompt redesign is
justified by this infrastructure failure. Do not poll, restart the operator or
substitute a direct Cloud endpoint automatically.

## Evidence and verification

Private evidence is under
`data/diagnostics/fulfillment-output-contract-v61-2026-10-18-live/`:
the copied operator failure log, per-cell unobserved inspection record, terminal
run status, offline audit, verification, tracker snapshot and closure. The approval
record is in the frozen preparation directory; sealed preparation files were not
modified. The original operator log also remains under
`data/diagnostics/fulfillment-output-contract-live-2026-10-19.log`.

The offline audit verifies the frozen plan, all 116 sealed preparation files and
159 code dependencies, the approval, the failure location and empty inference
ledgers. It classifies all 74 cells as unobserved and confirms lock cleanup and
unchanged production/source evidence. Documentation and audit checks introduce
no additional discovery or inference. Preparation's 75 regressions and four fake
matrices remain prior checks of the unchanged execution code; they are not new
live results.

Independent human preference and the accepted broader story-quality evaluation
remain pending. No J1/P1/F1 diagnostic evidence or earlier preservation candidate
is promoted or downgraded by this unavailable-service outcome.
