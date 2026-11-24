# The Wading Path · Sol-high B/E comparison for approval

**Five counts before up to five generations, zero retries.** This comparison asks whether one additional evidence question helps Sol judge physical position in an ordinary scene-four critique. Q010 and Q011 use opposite arm orders. Q008 uses the default B brief once to test the distinction between a narrated arrival and an unresolved physical position. All ten slots are unused. [Frozen approval manifest](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/plan.json) · [Exact endpoint bodies](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/requests)

## Schedule and source

| Count slot | Generation slot | Claim | Brief |
| ---: | ---: | --- | --- |
| 1 | 6 | Q010 · achieved standing position | B |
| 2 | 7 | Q010 · achieved standing position | E |
| 3 | 8 | Q008 · narrated arrival | B |
| 4 | 9 | Q011 · fulfillment of the planned endpoint | E |
| 5 | 10 | Q011 · fulfillment of the planned endpoint | B |

Every slot uses `gpt-6.1-sol` with high reasoning. Each request has one active whole field from critique v2 (`df932129-8005-49e8-bcf2-054546125288`). Both OpenAI endpoints receive the full reviewed draft v1 (`38e82829-604f-40df-b5a0-1c968718573e`), scene-four plan v1 (`152e58e1-57ee-5c48-8bb2-bf4f7e8e104e`), the complete saved review, and the historical critic messages and visible context, including the three earlier accepted drafts. The manifest binds the critique and all seven input versions. Operator gold stays in separate local files. [Read-only selection rehearsal](wading-path-read-only-selection-rehearsal-2026-11-24.md) · [Frozen selections and briefs](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/selections.json)

Within each pair E adds one sentence to B’s evidence obligation. It asks which draft observation the conclusion relies on, when it applies, and whether it establishes, rules out or leaves open the named position at the cut. Q010 names Elias and Maya standing before the master breaker panel housing. Q011 names them having reached the housing and standing before the final barrier. Removing this sentence reproduces the B request in each pair. Q008 asks what actions the conclusion narrates.

The native registry has 1,420 citation IDs. OpenAI documents a 1,000-value limit across schema enumerations, so the diagnostic response schema represents `E0001` through `E1420` with an exact five-character pattern. All original IDs and source pointers stay visible, and the application validates each returned citation against the native registry. Local checks compared the pattern with the registered set across every four-digit candidate. This representation is shared by both endpoints and all five assessments. [OpenAI Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) · [Diagnostic renderer](../../scripts/wading_path_be/plan.py)

## Independent scores

| Claim | Judgment gold | Evidence earning one point |
| --- | --- | --- |
| Q010 | **uncertain** | Credit both characters entering the plenum, locate their gaze deeper into it, and identify the housing as the thing standing at the end. Explain why their final position and posture remain open. |
| Q008 | **unsupported** | Locate the planned outcome and narrated entry. Account for the ending through its last line. It describes the housing at the passage end without depicting the pair arriving there. Their physical position remains open. |
| Q011 | **uncertain** | Locate both plan requirements, reaching the housing and standing before the final barrier. Use the draft to distinguish reaching the wall and entering the plenum from fulfilling those requirements. Identify the housing as the barrier and explain the unresolved endpoint. |

Each eligible response earns 0 or 1 for the returned whole-field judgment and independently 0 or 1 for its cited evidence and explanation. The evidence worksheet masks the arm, returned label and dispatch order. Record the cited passages and basis, accept equivalent version-bound locators, and seal all evidence decisions before joining judgments to gold. A panel-only citation, plan-only proof of fulfillment, or definite nonarrival inferred from omission fails the evidence criterion. Ineligible deliveries are unscored on both axes. [Sealed source gold and per-field criteria](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/gold.json) · [Scoring rules](../../data/diagnostics/wading-path-sol-high-be-2026-11-24/scoring.json)

Report both scores for each position arm, each axis gain or loss, and any joint baseline pass. Report Q008 separately. An incomplete comparison is inconclusive. A Q008 miss or any paired loss holds advancement. Otherwise a gain is evidence for this review. If both baselines already pass both axes, there was no room for recovery. Two fields from the same ending give one within-review comparison.

## Budget and stops

| Limit | Frozen value |
| --- | --- |
| Endpoints | Five serial POSTs to `https://api.openai.com/v1/responses/input_tokens`, followed by up to five to `https://api.openai.com/v1/responses`. Each count carries exactly the generation’s model, input, reasoning and output schema. |
| Tokens | 160,000 input and 4,096 output tokens per generation, including reasoning. Aggregate generation maxima of 800,000 input and 20,480 output tokens. |
| Generation cost | $0.44096 per generation and $2.20480 total using the frozen repository catalog’s conservative rate calculation. |
| Time | 120 seconds per count, 300 seconds per generation, 35 minutes total. |

The input allowance accounts for the full saved-review presentation. The frozen HTTP bodies are 378,854–379,623 bytes. Actual model token counts are pending. All five counts must be positive, in budget and HTTP 200 before generation can begin.

The runner checks the approval digest, frozen files and unused ledger, then persists intent before sending. The first technical failure stops the remaining schedule. Stops cover HTTP and transport errors, cancellation or deadline, invalid or duplicate-key JSON, model drift, refusal, truncation, invalid claim or citation, missing required generation usage, and exceeded budgets. A valid semantic miss is scored and the schedule continues. An interrupted dispatch consumes the journal. The audit retains terminal evidence, unknown usage and any untouched slots. [Runner and auditor](../../scripts/wading_path_be/run.py)

## Approval and verification

Approval SHA-256 is `81c56dda84c79e97de246c7afeb8a525531e4bd0244fa9ed104e09deba3f8e05`. Offline readback reconstructed all ten requests, verified the 14 sealed members and 31 implementation files, and found a ready journal with zero attempted slots. [Registered readback](../../data/diagnostics/wading-path-be-freeze-verification-2026-11-24/registered-readback.json)

The local fixtures exercise the fifth-count gate, cancellation after intent, a late HTTP error, wrong claims and citations, missing usage, length, timeout and rejection of a second dispatch. Scoring fixtures exercise a gain on either axis, control failure, regression, ties and incomplete delivery. [Freeze and selection tests](../../data/diagnostics/wading-path-be-freeze-verification-2026-11-24/focused.xml) · [Mapping, binding and source tests](../../data/diagnostics/wading-path-be-freeze-verification-2026-11-24/related.xml)

All 28 freeze and selection tests and 180 related tests passed. Repository-wide Ruff lint, formatting and strict mypy passed across 424 Python files. The comparison awaits live approval. B remains the default and the full workflow canary stays on hold.
