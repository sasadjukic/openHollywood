# The Wading Path · Sol-high Q011 observation comparison

**Pending approval.** The question is whether supplying verbatim observations from the selected draft helps Sol assess the critic’s whole Q011 claim. In the original run, B identified the limit of the evidence and returned `unsupported`. The local rehearsal recovered the judgment point by changing only its label. This comparison gives the model the source passages and lets it make both decisions itself. [Observed failure](wading-path-position-and-judgment-audit-2026-11-24.md) · [Offline rehearsal](wading-path-q011-fixed-explanation-rehearsal-2026-11-24.md)

## Cases and dispatch order

All seven assessments use `gpt-6.1-sol` at `high` reasoning. B uses the ordinary work brief. O uses B with one added `exact_observations` list. Two pairs present B first and one presents O first. Q008 occupies the middle slot and runs once on B. All seven counts run serially before any generation.

| Count | Generation | Field and ending | Arm |
| ---: | ---: | --- | --- |
| 1 | 8 | Q011 · original | B |
| 2 | 9 | Q011 · explicit arrival | O |
| 3 | 10 | Q011 · measured stop short | B |
| 4 | 11 | Q008 · original, narrated-arrival control | B |
| 5 | 12 | Q011 · original | O |
| 6 | 13 | Q011 · explicit arrival | B |
| 7 | 14 | Q011 · measured stop short | O |

Q011 assesses the conjunction of reaching the breaker-panel housing and standing before the final barrier. Q008 assesses whether the ending **narrates** the characters’ arrival. The original Q011 B and Q008 B requests match their historical count and generation bodies byte for byte. For each authored ending, the original review and critic context retain their historical versions. Both arms receive the same brief identifying the selected diagnostic draft at `E1420`. They share the full prose, plan, claim, source registry, output schema and generation settings. [Exact requests](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/requests) · [Manifest and source versions](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/plan.json)

## Exact observations

O repeats the closing passage beginning “They reached the eastern wall” as three complete, consecutive paragraphs. They cover the pair entering the plenum, looking deeper, and the location and identity of the housing. The authored versions also repeat their one added final paragraph. Each list entry consists solely of a registered draft reference, exact version, start and end character offsets, and a verbatim quotation. Removing that list reproduces the paired B body. Gold, relation labels and operator evidence decisions stay local. [Frozen observation lists](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/observations.json)

| Selected ending | Draft version | Closing observation |
| --- | --- | --- |
| Original | `38e82829-604f-40df-b5a0-1c968718573e` | The three paragraphs run from 3995 through 4804, end exclusive. |
| Explicit arrival | `02037781-6b73-5869-ba09-337008c50d4f` | Adds “When the light steadied, Elias and Maya reached the master breaker panel housing and stood side by side before it.” at 4806–4920. |
| Measured stop short | `2f9e80a0-29b4-579f-8075-b6e064788b24` | Adds “When the light steadied, Elias and Maya stopped side by side three full strides short of the master breaker panel housing and stayed there.” at 4806–4945. |

## Independent scores and decision

Eligible responses receive one judgment point for the exact whole-field label. Evidence receives a separate point for a source-bound explanation meeting the case criteria. The evidence reader sees the case, claim, citations and reason. Arm, dispatch order and returned label are masked. Resolve the cited version and passage, record the basis, and seal every eligible evidence decision before joining labels to gold. Accept equivalent precise locators. Ineligible or unattempted generations stay unscored on both axes. [Gold and evidence requirements](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/gold.json) · [Scoring rules](../../data/diagnostics/wading-path-sol-high-observations-2026-11-24/scoring.json)

| Field | Judgment gold | Evidence earning one point |
| --- | --- | --- |
| Q011 original | `uncertain` | Locate both assignments and the pair’s entry and gaze. The housing stands at the end. The ending leaves arrival and standing there open. |
| Q011 explicit arrival | `supported` | Locate both assignments and the selected final sentence placing both people at the housing and standing before it. Identify it as the barrier. |
| Q011 measured stop | `unsupported` | Locate both assignments and the final, persistent three-stride gap. It contradicts standing before the barrier at the cut. Earlier arrival remains open. |
| Q008 original | `unsupported` | Locate the plan’s outcome, narrated entry, gaze and closing description. Explain why the complete ending omits a narrated arrival. A definite physical stop short overreads the account. |

Report both scores per eligible arm, per-axis movement for each ending and any original B recovery relative to its historical 0/1. A missing eligible arm makes the comparison inconclusive. A miss on either axis for either determinate arm or Q008 holds advancement. With those controls intact, an original B miss followed by an O joint pass is a within-scene recovery. Joint passes for both original arms leave no headroom. An original O miss holds advancement. One observation per arm in one family can guide the next diagnostic. B remains the default.

## Budget, stops and approval scope

Approval would authorize sending the full prose and context to OpenAI at **both** `POST /v1/responses/input_tokens` and `POST /v1/responses` on `https://api.openai.com`. This includes the selected draft, complete historical critic messages and review, scene plan, earlier accepted scenes and story context. The count carries the same model, input, reasoning and response schema as the corresponding generation.

| Limit | Frozen value |
| --- | --- |
| Requests | Seven input counts, then up to seven generations. Zero retries or replacements. |
| Tokens | 160,000 input and 4,096 output, including reasoning, per generation. Aggregate generation ceilings are 1,120,000 input and 28,672 output tokens. |
| Generation cost | Up to $0.44096 per generation and $3.08672 total under the frozen repository catalog. Actual usage would come from the terminals. |
| Time | 120 seconds per count, 300 seconds per generation, 49 minutes for the full schedule. |

Every count must return HTTP 200 with a positive, admissible input count. The first technical failure stops dispatch. This includes transport failure, timeout, non-200, invalid or duplicate-key JSON, model drift, refusal, truncation, invalid claim or citation, missing required generation usage, and a budget breach. Semantic misses are retained for scoring and the schedule continues. The runner claims the single-use journal and records intent before send. Interruption consumes the run. Audit preserves unknown usage and every untouched slot. [Runner](../../scripts/wading_path_observations/run.py) · [Scorer](../../scripts/wading_path_observations/scoring.py)

## Approval fingerprint and verification

Approval SHA-256 is `8ba8473e3496a68ccb250c05b31b3aae217bda7a84aec19051913e619fe3ae82`. Offline readback rebuilt the 14 request bodies, checked all 18 frozen members and 36 implementation files, and found the registered journal ready with all 14 slots unattempted. The bodies range from 379,051 to 380,928 bytes. Provider token counts await approval. The local read-only check is `python -m scripts.wading_path_observations.run verify --approved-plan-sha256 8ba8473e3496a68ccb250c05b31b3aae217bda7a84aec19051913e619fe3ae82`. [Registered readback](../../data/diagnostics/wading-path-observations-verification-2026-11-24/registered-readback.json)

All 61 focused tests passed, including 15 for this comparison. Injected fixtures exercised all 14 slots, an over-budget seventh count, an incomplete message, a bad citation and interruption followed by a rejected restart. The scoring fixtures independently varied the returned label and the evidence decision, checked missing arms and control misses, and distinguished a baseline recovery from an observation-assisted recovery. Repository-wide Ruff lint, formatting and strict mypy passed across 433 Python files. Production prompts are unchanged and the full workflow canary remains on hold. [Regression tests](../../tests/api/test_wading_path_observations.py) · [Verification record](../../data/diagnostics/wading-path-observations-verification-2026-11-24/verified.xml)
