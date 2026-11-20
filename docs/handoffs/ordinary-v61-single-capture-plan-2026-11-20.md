# Approval plan for one ordinary v61 critic review

**Frozen on November 20, 2026. Awaiting approval.** The proposed call would acquire
one provider-generated review of the first saved scene in the September 29 formal
cloud campaign. The registered dispatch slot is ready. Live calls made during
preparation total **zero**. [Source selection and design](saved-review-isolated-capture-design-2026-11-20.md)

## What approval would send

| Item | Frozen value |
| --- | --- |
| Destination | One `POST http://127.0.0.1:11434/api/chat` to the local Ollama daemon for Ollama Cloud |
| Model and role | `gemma4:31b-cloud`, ordinary `scene_critic`, initial critique, prompt 61, graph 9 |
| Payload | 65,218 HTTP body bytes. The system and user messages contain 10,997 and 50,272 characters. |
| Story context | Complete unpublished scene prose in the ordinary draft evidence catalog, exact Scene Plan, scoped approved Blueprint context, Story Bible, assignment and native critic instructions |
| Generation settings | Temperature 0.2, top-p 0.95, seed 19101, thinking off, streaming off |
| Budget | **One generation attempt, zero count calls, zero retries.** 24,000 input tokens, 8,000 output tokens, 32,000 context, 300-second outer generation deadline |
| Cost | USD 0.20 application reservation. The adapter reports cloud billing as unknown. Ollama reports actual token usage after dispatch. |

The 40 catalog entries matched the saved version’s evidence IDs and excerpts in order.
Together they reproduce the complete draft after whitespace normalization. The Scene
Plan and Story Bible matched their saved contents. The approved Blueprint uses the
ordinary critic’s scoped presentation. The wire body matched the earlier rehearsal
byte for byte.

| Approval identity | Value |
| --- | --- |
| Approval manifest SHA-256 | `273a0c918e2b4458722bb9adac1ce959a242784abe1ee18cc58ae4dcb7597170` |
| HTTP request body SHA-256 | `35452ffd86fe44f4639f3fada86b7d00a97c1aaece16911dcba5e6195392bc51` |
| Ordinary message hash | `2a6de460883c71b08c6f5c6a7e89405385d1802bb88227affbc282c2dbec96f7` |
| Dedicated run | `986c416f-9bf6-40f1-800c-4d7c07b843fd` |
| Draft version | `b74efc96-dbe6-4147-8dd3-a1c24f295321` |
| Scene Plan version | `b5179ac9-5585-5e5b-9555-20ca70b68f6a` |

The local approval bundle is `data/diagnostics/ordinary-v61-single-capture-2026-11-20/`.
`plan.json` is the approval target. It also pins the Blueprint and Bible versions,
all four content hashes, source database and sidecars, detached database seed, task
and implementation. `request.json` contains the exact outbound bytes. `verify` is the
read-only CLI operation. The live entry point requires the approval digest and explicit
full-prose authorization. [Single-use harness](../../scripts/ordinary_v61_capture.py)

The operator can inspect the registered slot offline with
`python scripts/ordinary_v61_capture.py verify`. After approval, the single invocation
uses `run --approved-plan-sha256 <manifest SHA-256> --send-full-prose` on the same
script. Provider availability was not probed during preparation.

## Execution and stop rules

1. Verify the approval, frozen sources, implementation and request. Claim the single
   row in the registered SQLite ledger with a conditional committed update. Only the
   winner can open a new output directory and copy the seed into it.
2. Call the ordinary critic on that private workspace. At the transport boundary,
   compare method, URL and exact body hash. Commit the dispatch intent with SQLite
   full synchronization **before** forwarding the POST. The live path uses one fixed
   directory, disables HTTP retries and redirects, and never creates a missing ledger.
3. Stop after the first response or interruption. A timeout, HTTP error, truncation,
   malformed review, wrong model, failed native validation or budget overrun consumes
   the slot. Preserve the available HTTP and terminal evidence. Missing usage stays
   unknown. An interrupted process can leave an open intent and no terminal receipt.
   Preserve that state for inspection. A restart cannot reclaim the slot.
4. On success, verify the sole invocation, new critique version, exact draft and plan,
   prompt hash, native audit and read-only intake. Save the private database, export
   and receipt. A revision verdict ends the capture. A writer, assessor or graph
   continuation would need separate authorization.

## Local verification

Twelve full-case scenarios used isolated copies of the approval bundle and
socket-blocked mock transports. For the hard-crash cases, the process exited
immediately, bypassing exception handling and cleanup. A fresh process then opened
the same ledger and attempted the same approved run.

| Injected condition | POSTs received by mock | Result |
| --- | ---: | --- |
| Death immediately after the dispatch commit | 0 | Fresh process refused. Zero additional sends. |
| Death immediately after mock receipt, before any reply | 1 | Fresh process refused. Zero additional sends. |
| Two simultaneous processes | 1 total | One captured, one refused. Later restart also refused. |
| Ordinary success | 1 | Native export and saved-review intake accepted the new critique. Restart refused. |
| HTTP 500 or transport timeout | 1 per case | Stopped. Usage unknown in both. The HTTP error body was retained when received. |
| Malformed review, length finish, wrong model or over-budget usage | 1 per case | Each stopped. Each restart refused. |
| Wrong approval or changed frozen request | 0 | Refused before claiming the slot. |

The receipt count is measured at this application's transport boundary. A hard exit
after dispatch can leave the provider outcome unknown. The durable record prevents a
second application POST in that situation. The regression tests also cover concurrent
claims, ledger reissue and endpoint drift. [Regression tests](../../tests/api/test_ordinary_v61_capture.py)

Private test evidence is under `data/diagnostics/ordinary-v61-harness-verification-2026-11-20/`.
`probes/verification.json` records each scenario, process exit codes and observed POST
counts. Fixture usage and judgments are excluded from assessment results.

All 2,605 Python tests passed, including the five single-use regressions. Repository
Ruff lint, formatting and strict mypy passed across 328 Python files. The final
read-only inspection confirmed that the approval bundle matches the qualified copy
and the live slot is still ready.

**Decision requested.** Approve one generation under this digest and destination to
acquire the review. If it yields a substantive whole factual claim, freeze independent
gold from the original evidence before opening assessor output. Genuine review
acquisition and gold are pending. Production prompts remain unchanged and the full
workflow canary is on hold.
