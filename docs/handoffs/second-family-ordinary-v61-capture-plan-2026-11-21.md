# Approval plan for one ordinary v61 critique of The Impossible Card

**Frozen November 21, 2026. Subsequently approved and executed once.** The slot is spent. [Capture results and frozen Q013 gold](second-family-ordinary-v61-capture-results-2026-11-21.md)

This capture was designed to acquire one ordinary Gemma review of a second story family. Elara receives a birthday card in her own handwriting dated ten years in the future. The intended result is a genuine saved critique that can be screened for one independently checkable factual claim. A valid critique may contain no such claim.

## Saved sources

I selected **OH-V01-002 — cloud**, scene 1, from the September 29 formal cloud campaign. I chose the earliest successful initial Gemma critique of a version-one first scene outside Q008’s benchmark assignment, ordered by start time and invocation ID. Selection used creator and input metadata. The Q008 premise concerns a stroller outside an abandoned building. Here the project, assignment and all four input version IDs and content hashes differ. [Prior source-gap audit](second-family-saved-v61-admission-2026-11-21.md)

| Saved version | Exact version ID | Content SHA-256 |
| --- | --- | --- |
| Scene Draft v1, *The Impossible Card* | `c3689bce-e108-4761-bafe-390f6e7ea1b3` | `7a54fd7472cb71b7fc67ad33b8e283cba5a21b2f4e97184a39c21e3e4d1f9582` |
| Scene Plan v1, *The Impossible Card* | `2a13f5a3-8a0b-561f-b889-05eb1af338a7` | `16d62399dc7c67f0b30ef5fd39fff32eeedcdec219aa49e369d29514f65b8918` |
| Approved Story Blueprint v1 | `7997c3e6-1b4b-4766-a33e-ff9b89d65eb3` | `287fcf112f046a38d0919b71dc10be10004e43617359748207132a29b34d2276` |
| Story Bible v1 | `95437e65-e363-5fc8-b68e-922b33967ceb` | `8047472b9d1249df33c6afe0cfb278476b6595402d1420615e6716faea1637a7` |

Historical v33 critic invocation `fb5e140f-720a-4b78-9cb4-24fd5268aa03` supplies the four input links. The source run records the approved Blueprint, and the scene writer in that run created the selected draft. The proposed v61 capture has its own detached run, `6380f22f-68ae-4dd7-876a-b08eb3d9000e`, and a separate single-use ledger.

## What approval would send

| Item | Frozen value |
| --- | --- |
| Destination | One `POST http://127.0.0.1:11434/api/chat` through the local Ollama daemon to Ollama Cloud |
| Model and role | `gemma4:31b-cloud`, ordinary `scene_critic`, initial critique, production prompt 61, graph 9 |
| Exact payload | 68,631 UTF-8 body bytes. The ordinary system and user messages contain 10,997 and 53,555 characters. |
| Story context | Complete unpublished draft in 43 ordered evidence excerpts, exact Scene Plan and Story Bible, current-scene view of the approved Blueprint, and the ordinary assignment, boundary and rubric |
| Generation settings | Temperature 0.2, top-p 0.95, seed 19102, thinking off, streaming off |
| Budget | **One generation attempt, zero count calls, zero retries.** 24,000 input tokens, 8,000 output tokens, 32,000 context, 300-second outer generation deadline. Application reservation USD 0.20. Actual cloud billing is unknown. |
| Request body SHA-256 | `03249a0141224241dadaf5998df2d09da75fa177097cff9c05a9edda233afb01` |
| Ordinary messages SHA-256 | `4c0c951627a82067d907985a5d4f0529c30632f678593d5301896823f9556030` |
| **Approval manifest SHA-256** | `f9e27da460d727b4bd864c07e6849d626a88e615dc5c5e1c6c9bd597edbca513` |

The private bundle is `data/diagnostics/second-family-v61-capture-2026-11-21/`. Its `request.json` holds the exact outbound bytes. Its `plan.json` pins the source files, four input versions, detached seed, task, request, implementation and limits. To inspect the registered slot locally, run `python -m scripts.second_family_v61_capture verify` in the project environment. [Second-family entry point](../../scripts/second_family_v61_capture.py) · [Single-use transport](../../scripts/ordinary_v61_capture.py)

## Dispatch and admission stops

1. Require explicit approval of the manifest and full story payload. Refuse changed sources, implementation, task, seed or request before sending. The real command can use only the fixed second-family directory.
2. Claim the one ledger row, then commit dispatch intent before forwarding the exact POST. Any consumed or ambiguous attempt ends the capture. A restarted process cannot send a replacement.
3. Stop on a timeout, HTTP error, unexpected model, incomplete or malformed response, failed native validation, or a reported budget overrun. Preserve the available response and usage. A crash can leave the provider outcome unknown.
4. On success, require one new critic invocation and its bound critique, schema-7 audit, compatible native export and saved-review intake. A revision verdict ends the run. The writer, assessor and workflow graph receive zero calls.
5. Inspect the original review and its source evidence for a whole factual claim. If one qualifies, freeze the verbatim field, exact versions, expected judgment, evidence locations and rationale **before viewing assessor output**. Otherwise record the claim gap. Story-quality judgments remain with human readers.

## Local verification

The operator manifest, request, task and seed matched the rehearsed bundle byte for byte. An independent read of the four saved versions reproduced every content hash. The 43 ordered evidence excerpts reproduced the entire draft after whitespace normalization. The Scene Plan and Story Bible matched the saved objects, and the Blueprint’s scene-plan list contained only the current scene. The Q008 and second-family registrations each rejected the other’s approval.

| Injected condition | Mock POSTs | Observed result |
| --- | ---: | --- |
| Successful ordinary critique | 1 | Exactly one new invocation and critique. The critic used all four expected versions. Native export and intake passed. |
| Process killed just after committing intent | 0 | The attempt was consumed. A fresh process sent zero additional POSTs. |
| Process killed just after receipt | 1 | The attempt was consumed. A fresh process sent zero additional POSTs. |
| Two processes launched together | 1 total | One captured and one refused. Reopening sent zero additional POSTs. |
| HTTP 500, timeout, malformed review, truncated reply, wrong model or over-budget output | 1 per case | All six stopped. All six refused restart. HTTP 500 and timeout retained unknown usage. |
| Wrong approval or changed frozen request | 0 per case | Both refused before claiming the slot. |

All 12 scenarios used injected transport with network connections blocked. The private verification evidence is under `data/diagnostics/second-family-v61-verification-2026-11-21/`. At freeze the operator slot was ready with zero live attempts. Q008’s original slot was already spent. Provider availability was not probed. Production prompts are unchanged and the full workflow canary remains on hold.

The full Python suite passed all 2,644 tests. Ruff lint, formatting and strict mypy checks passed across 346 Python files.
