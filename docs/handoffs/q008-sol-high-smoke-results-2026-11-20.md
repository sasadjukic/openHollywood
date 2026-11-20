# Q008 Sol-high smoke results

**Q008 passed all three frozen judgments.** Sol returned `supported`, identified the assigned outcome in the standalone Scene Plan, and located the final action and its motive in the reviewed draft. The run used one input count and one generation, with zero retries. The journal is closed and spent. [Frozen approval plan](q008-sol-high-smoke-plan-2026-11-20.md)

## Both slots

The original critique was selected. Both OpenAI endpoints received the approved full prose and story context under plan SHA-256 `f447f66fa27d9731244304fbebd1a99426e7ed4b8794c0aaa23a3ed6f227e58a`. The journal opened at 21:03:24 UTC on November 20, 2026.

| Slot | HTTP | Observed result | Endpoint elapsed |
| --- | ---: | --- | ---: |
| Input count · `/v1/responses/input_tokens` | 200 | 58,894 input tokens, within the 96,000-token ceiling. Generation admitted. | 1.888 s |
| Generation · `/v1/responses` | 200 | `gpt-6.1-sol`, high reasoning, completed. One Q008 assessment bound to the frozen request. | 9.155 s |

Generation reported **58,894 input tokens and 345 output tokens**, including **165 reasoning tokens**. The input usage matched the preliminary count. The frozen rate card gives a generation estimate of **$0.150685** against the **$0.60** ceiling. Actual billing was unavailable. Both slots mapped without errors or accounting holds.

## Scoring against the frozen gold

The adjudication covers Gemma’s complete 307-character outcome explanation on critique version `2268e6e8-b82b-4cca-932f-55cc418a58b5`. The independent gold had been frozen before any assessor output. Sol cited exactly two evidence locations. [Claim and gold provenance](ordinary-v61-single-capture-results-2026-11-20.md)

| Frozen judgment | Score | Evidence inspected |
| --- | --- | --- |
| Whole-claim label | **Pass** | Sol’s `supported` matches the expected label for the entire Q008 explanation. |
| Plan evidence | **Pass** | `E0233` resolves to the outcome field of Scene Plan `b5179ac9-5585-5e5b-9555-20ca70b68f6a`. It assigns the scene outcome “Elias is drawn to the entrance of the windowless building.” Sol identified that version and obligation. |
| Draft-ending evidence | **Pass** | `E0883` resolves to the complete prose of draft `b74efc96-dbe6-4147-8dd3-a1c24f295321`. Sol located its final sentence, identified Elias stepping past the circle of shoes, and quoted both his movement “toward the dark, open threshold of the monolith” and his motive, the “silent promise of the thing that waited inside.” It explicitly left entry unconfirmed. |

The full-draft citation earned credit under the frozen rule because the explanation located the passage establishing all three details. The same sentence is the gold’s excerpt 0040 (`E0321`). Both citations point to the appropriate sources. The separate achieved-state field received no score.

This is one successful guided assessment on a genuine saved review. The work brief identified the two obligations and supplied the plan and complete-draft references. The result establishes delivery and evidence use for this case. General reviewer accuracy and story quality remain unmeasured. [Input qualification](assessment-saved-review-q008-qualification-2026-11-20.md)

## Evidence and project state

The read-only audit verified both intent/outcome chains, their frozen request hashes and the terminal stop. It marked the delivery eligible for scoring. The operator score is stored separately from that mechanical binding.

| Private evidence under `data/diagnostics/` | Contents |
| --- | --- |
| `q008-sol-high-smoke-2026-11-20/output/` | Header, two intents, two HTTP outcomes and closing receipt. |
| `q008-sol-high-smoke-results-2026-11-20/` | Reconstructed `audit.json`, adjudicated `score.json` and local `score_and_verify.py` replay. |

Step 19 remains in progress. Production prompts are unchanged. Further live calls are paused and the full workflow canary remains on hold.
