# The Wading Path · Sol-high B visit and cut-position comparison

**Frozen for approval.** Can Sol distinguish a gap that persists from the final stop onward from a gap that existed throughout scene four? Both drafts leave Elias and Maya three strides short of the breaker housing. Only the full-scene exclusion rules out an earlier visit. A third draft explicitly puts them at the housing at the cut and serves as the positive control for both claims. [Local rehearsal](wading-path-visit-position-rehearsal-2026-11-25.md)

## Six cases and fixed order

Every case uses `gpt-6.1-sol` at high reasoning with the same B work brief, the full selected draft at `E1420`, historical critic and story context, and one active factual claim. The visit claim asks whether both reached the master breaker panel housing at some time during scene four. The cut-position claim asks whether both are at the housing at the final narrated instant. The matched stop and exclusion drafts present the claims in opposite orders. All six count slots precede every generation slot.

| Count | Generation | Case | Draft | Claim | Operator gold |
| ---: | ---: | --- | --- | --- | --- |
| 1 | 7 | S1-B | Measured stop | Visit during scene | Uncertain |
| 2 | 8 | X2-B | Full-scene exclusion | At housing at cut | Unsupported |
| 3 | 9 | A1-B | Explicit arrival | Visit during scene | Supported |
| 4 | 10 | S2-B | Measured stop | At housing at cut | Unsupported |
| 5 | 11 | X1-B | Full-scene exclusion | Visit during scene | Unsupported |
| 6 | 12 | A2-B | Explicit arrival | At housing at cut | Supported |

The explicit-arrival version is `02037781-6b73-5869-ba09-337008c50d4f`. Its last sentence (4806–4920) records the joint arrival and where both people stand. The measured-stop version is `2f9e80a0-29b4-579f-8075-b6e064788b24`. Its last paragraph (4806–4945) establishes the persistent final gap. The exclusion version, `4da86d35-9337-54d8-896b-c212ba05516c`, preserves every character of the measured stop and adds a retrospective sentence at 4947–5149 covering the opening huddle through the cut. Offsets are end-exclusive. Each count and generation share the same model, messages, reasoning and response schema. Gold, grading criteria and fixture answers remain local. [Exact request bodies](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/requests) · [Source versions and request hashes](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/plan.json)

## Independent scores and decision

**Judgment earns one point** for the exact whole-claim label. **Evidence earns one independent point** when the cited passage and explanation cover the people, housing and time required by the claim. Resolve each citation against its selected version, review the explanation with the returned label and dispatch order masked, and seal the evidence decisions before joining them to gold. Equivalent precise passages qualify. A whole-draft reference accompanied only by an explanation of the final gap earns zero evidence for the exclusion visit. Report both scores for each eligible delivery and both axes as unscored for any ineligible slot. [Frozen gold](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/gold.json) · [Evidence criteria](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/evidence-criteria.json) · [Scoring rules](../../data/diagnostics/wading-path-sol-high-visit-position-2026-11-25/scoring.json)

Compare S1 with X1 for the visit and S2 with X2 for the cut. Report A1 and A2 separately as the positive controls. Any missing eligible delivery makes the comparison inconclusive. A miss on either axis of either arrival control holds the control. With both controls passing, any other miss holds the claim scope. Six joint passes establish discrimination on these three drafts. The earlier original-ending failures R1 and P1 are outside this comparison.

## Endpoints, budget and stops

Approval would authorize full unpublished prose and context at `POST https://api.openai.com/v1/responses/input_tokens` for six serial counts and at `POST https://api.openai.com/v1/responses` for up to six serial generations with `store=false`. Every count must return HTTP 200 and a positive admissible count within the frozen limits before any generation begins. Zero retries, replacements or fallback.

| Resource | Ceiling |
| --- | --- |
| Per generation | 160,000 input tokens and 4,096 output tokens including reasoning |
| Aggregate generation | 960,000 input tokens and 24,576 output tokens |
| Estimated generation cost under the frozen catalog | $0.44096 per generation and $2.64576 total |
| Time | 120 seconds per count, 300 seconds per generation, 42 minutes overall |

The first technical failure stops dispatch. Stops include a timeout, transport or capture failure, non-200 response, malformed or duplicate-key JSON, model mismatch, refusal, truncation, invalid output, wrong claim or citation, missing required usage, and a budget breach. The single-use journal records intent before send. Interruption consumes the registration and preserves unknown usage and untouched slots. An eligible semantic miss is recorded and the schedule continues. [Runner](../../scripts/wading_path_visit_position/run.py)

## Verification and approval

**Approval SHA-256** `e6274e578c2036d5be76318b0e30cb16d9e61f47791ec20102c72b5d2c1bcbb6`. Offline readback rebuilt 12 request bodies, checked 16 frozen members and 46 implementation files, and found the journal ready with all 12 slots unattempted. The read-only command is `python -m scripts.wading_path_visit_position.run verify --approved-plan-sha256 e6274e578c2036d5be76318b0e30cb16d9e61f47791ec20102c72b5d2c1bcbb6`. [Registered readback](../../data/diagnostics/wading-path-visit-position-freeze-verification-2026-11-25/registered-readback.json)

All **41 focused tests passed**. Mock transport exercised the complete schedule, an over-budget sixth count, incomplete delivery, invalid citation, wrong claim and interrupted dispatch with rejected restart. Replaying the rehearsal fixtures through the frozen scorer gave all six grounded answers both points. A negative visit answer citing only the final gap earned judgment 0, evidence 0 on the measured stop and judgment 1, evidence 0 on the full-scene exclusion. Repository-wide Ruff lint, formatting and strict mypy passed across 452 Python files. B remains the default, production prompts are unchanged and the full workflow canary stays on hold. No provider calls were made. [Fixture score readback](../../data/diagnostics/wading-path-visit-position-freeze-verification-2026-11-25/scorer-readback.json) · [Request and scoring tests](../../data/diagnostics/wading-path-visit-position-freeze-verification-2026-11-25/requests-and-scoring.xml) · [Injected transport tests](../../data/diagnostics/wading-path-visit-position-freeze-verification-2026-11-25/injected-transport.xml)
