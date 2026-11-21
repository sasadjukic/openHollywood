# Q013 Sol-high smoke results

**Claim correctness passed. Evidence coverage passed.** For *The Impossible Card*, Sol returned `supported` on Gemma’s complete turning-point explanation. Its single citation pointed to the full draft. Its reason located the inscription on the card and quoted the passage giving the current date, Elara’s attention to the numbers and the ten-year interval. The run used one input count and one generation, with zero retries. [Frozen approval plan](q013-sol-high-smoke-plan-2026-11-21.md)

## Both slots

The journal opened on November 21, 2026 at 20:39:39 UTC under approval SHA-256 `ca0314f557dc4a8b4e23085cc974dfd4d7c51abbc30c510d6f1e6f9149342ee3`. Both OpenAI endpoints received the approved full prose and story context for critique v3 (`ca5915a5-5b82-4bad-82ce-e5c31a519dc0`) and reviewed draft v1 (`c3689bce-e108-4761-bafe-390f6e7ea1b3`).

| Slot | HTTP | Observed result | Endpoint elapsed |
| --- | ---: | --- | ---: |
| Input count · `/v1/responses/input_tokens` | 200 | 62,835 input tokens. The count passed the 96,000-token limit and admitted generation. | 9.841 s |
| Generation · `/v1/responses` | 200 | `gpt-6.1-sol`, high reasoning, completed. The response bound to the frozen request and sole active claim Q013. | 17.974 s |

Generation reported **62,835 input tokens and 427 output tokens**, including **255 reasoning tokens**. Its input usage matched the preliminary count. The frozen rate card gives an estimated generation cost of **$0.1613575** against a $0.60 ceiling. Actual billing was unavailable. Both slots mapped without errors. The read-only audit verified their intent/outcome chains and closing receipt, and marked the delivery eligible for scoring. The journal is spent.

## Independent scores

| Judgment | Score | Basis |
| --- | --- | --- |
| Claim correctness | **Pass** | The observed label `supported` matches the independent gold for the complete 185-character claim. |
| Evidence coverage | **Pass** | Sol cited `E0920`, named the correct draft version and located the relevant passage precisely. All four obligations below were established within that citation. |

Sol’s only citation was `E0920`, the complete 3,435-character `/prose` field in draft v1. The references below are the scorer’s independently frozen locations inside that draft. [Gold and source provenance](second-family-ordinary-v61-capture-results-2026-11-21.md)

| Obligation | What Sol located in the cited draft | Scorer’s location |
| --- | --- | --- |
| Date on the card | Elara turns over the card. A date is scrawled at the bottom right, followed by “October 14th, 2034.” Sol explicitly tied the date to that inscription. | `E0282`, `E0284` |
| Scene’s present date | Sol quoted “Today was October 14th, 2024.” | `E0288` |
| Elara notices the numbers | Sol quoted “Elara stared at the numbers until they blurred.” | `E0286` |
| Ten-year relation | Sol quoted “The card was dated exactly ten years into the future.” | `E0290` |

Sol also mentioned Elara’s immediate reaction and her later return to “2034.” Both occur in the same version. The scorer found no material misattribution. The work brief directed the assessor to check these obligations and supplied the complete-draft reference. The result establishes one successful guided factual assessment in this second scene family. It leaves broader reviewer accuracy and editorial quality unmeasured. [Input qualification](assessment-saved-review-q013-qualification-2026-11-21.md)

## Local evidence

The original HTTP outcomes and closure are in `data/diagnostics/q013-sol-high-smoke-2026-11-21/output/`. The sibling `q013-sol-high-smoke-results-2026-11-21/` directory contains the reconstructed `audit.json`, the independent operator `score.json`, and the offline `score_and_verify.py` replay. The replay checks the frozen request digests, both slot chains, usage, whole-claim identity and the scored passages against their exact draft offsets. Production prompts are unchanged. Further live calls are paused and the full workflow canary remains on hold.
