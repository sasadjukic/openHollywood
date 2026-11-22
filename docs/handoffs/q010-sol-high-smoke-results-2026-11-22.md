# Q010 Sol-high smoke results

**Whole-claim correctness failed. Evidence coverage passed.** Sol found the final sentence of *The Pristine Lure* and correctly described how far the narration follows Elias. It returned `unsupported` for Gemma’s ending claim. The frozen gold was `uncertain` because the scene leaves Elias’s precise position at the cut open. [Frozen approval and scoring rules](q010-sol-high-smoke-plan-2026-11-22.md)

## Both slots

The journal opened at 21:25:22 UTC on November 22, 2026 under approval SHA-256 `792d7f4b809bdbd5064f29c497bd15414bed606f297519a694badeaf7d2e1e45`. Both OpenAI endpoints received the frozen full prose and context for critique v2 (`2268e6e8-b82b-4cca-932f-55cc418a58b5`) and draft v1 (`b74efc96-dbe6-4147-8dd3-a1c24f295321`). There was one count, one generation and zero retries.

| Slot | HTTP | Observed result | Elapsed |
| --- | ---: | --- | ---: |
| Input count · `/v1/responses/input_tokens` | 200 | 58,662 input tokens. The count met the 96,000-token limit and admitted generation. | 2.216 s |
| Generation · `/v1/responses` | 200 | `gpt-6.1-sol` at `high` completed. The response bound to the exact request and Q010 alone. | 11.785 s |

Generation reported **58,662 input tokens** and **545 output tokens**, including **419 reasoning tokens**. Input usage matched the count. The frozen rate card gives a conservative generation estimate of **$0.152105** against a **$0.60** ceiling. Actual billed cost was unavailable. Both slots mapped without errors. The read-only audit verified both request and response chains and the closing record. The delivery was eligible for scoring and the journal is spent.

## Independent scores

Gemma’s entire achieved-state field reads “Elias has moved past the circle of shoes and is entering the threshold of the monolith.”

| Judgment | Score | Basis |
| --- | --- | --- |
| Whole-claim correctness | **Fail** | Sol returned `unsupported`. The first clause is established. The last narrated movement is toward the threshold, which leaves the second clause unresolved. The frozen rubric requires a material contradiction for `unsupported`. |
| Evidence coverage | **Pass** | Sol’s sole citation was the full draft, `E0883`. It named the correct version, located the final sentence, credited passing the shoes, and identified approach as the last depicted movement. It explained that the critic’s claim moves Elias “beyond the final narrated action.” That identifies the limit of the evidence without assigning him a definite stopping place. |

The scorer independently matched the passage to excerpt `E0321`, spanning characters 3129–3284 of draft v1. Sol quoted the opening of the final sentence through “threshold of the monolith.” Its quotation substitutes a period for the draft’s comma and omits the trailing clause about what draws Elias onward. The locator remains precise, and the omitted clause adds no further physical action. Sol cited only `E0883`. [Independent gold and exact draft witnesses](q008-q013-ending-claim-audit-2026-11-22.md)

For this guided claim, Sol had the relevant passage and recognized what it established. The error was choosing the label for that evidence. Its explanation supplies no passage that rules out beginning to enter. This single delivery leaves the frequency of that error and its effects on story quality unmeasured.

## Local evidence

Original intents, HTTP outcomes and closure are in `data/diagnostics/q010-sol-high-smoke-2026-11-22/output/`. The sibling `q010-sol-high-smoke-results-2026-11-22/` contains the reconstructed `audit.json`, independent `score.json` and offline `score_and_verify.py` replay. The replay verifies the frozen request bytes, response hash, usage, exact-version citation and the cited clause against the full draft. The observed final SHA-256 is `567e36524c111534f4fd791d7761fe973e621eacd4ebbb852cf9d65decdecd8f`. Q016 remained held. Production prompts stayed unchanged and the full workflow canary remains on hold.
