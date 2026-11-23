# Q011 Sol-high B and evidence-check comparison

**Ready for approval. The registered journal is unused.** This comparison asks whether one extra question helps Sol distinguish motion toward the sill from evidence of Elias’s physical position at the scene cut. It uses one observation per arm in the same five rehearsed versions of one scene. Approval would cover the full unpublished prose and story context at both OpenAI endpoints. [Approval manifest](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/plan.json) · [Twenty exact request bodies](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/requests/)

## Requests and five-case schedule

Every request assesses the whole claim “Elias is drawn to the entrance. At the scene cut he stands at the threshold.” B uses the rehearsed brief. E appends this single sentence to its evidence obligation.

> Identify the draft observation your conclusion relies on, say when it applies, and explain whether it establishes, rules out, or leaves open Elias standing at the threshold at the scene cut.

Within each pair, the system message, active claim, complete assessed draft, scene plan, blueprint, story bible, historical review, response schema, `gpt-6.1-sol` model and high reasoning setting are identical. Both arms return the existing support label, reason and citation IDs. Gold, rubric, scoring annotations and rehearsal answers stay with the operator. The two gap versions append the same two sentences to the genuine draft in opposite orders. [Source passages and versions](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/witnesses.json) · [Rehearsal](q011-position-gap-rehearsal-2026-11-23.md)

| Ending | Count slots in order | Generation slots in the same order | Frozen judgment | Evidence that decides position |
| --- | --- | --- | --- | --- |
| Genuine approach | 1 B, 2 E | 11 B, 12 E | `uncertain` | Elias moves past the shoes toward the threshold. The cut leaves his final position open. |
| Explicit arrival | 3 E, 4 B | 13 E, 14 B | `supported` | The last sentence places him standing at the threshold. |
| Explicit stop short | 5 B, 6 E | 15 B, 16 E | `unsupported` | His feet are planted a full stride short of the sill at the cut. |
| Gap at the cut | 7 E, 8 B | 17 E, 18 B | `unsupported` | The last observation places his boots a stride from the sill, even as he moves. |
| Gap before renewed motion | 9 B, 10 E | 19 B, 20 E | `uncertain` | He moves again after the measurement. The draft gives no final distance or stance. |

Arm order alternates across cases. Three pairs start with B and two start with E. The old AD-B, RD-B and SD-B paragraph-depiction deliveries are offline controls. The gold is the exact file sealed before the position rehearsal. [Frozen gold](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/gold.json)

## Separate judgment and evidence scores

1. **Score evidence first.** The worksheet shows each eligible reason and cited fields alongside the version-bound source passages. It masks arm, returned label and slot order. For either arm, credit the evidence only if the answer locates both plan obligations, credits the depicted attraction and explains what the draft establishes about standing at the cut. A physical negative requires an incompatible observation at that instant, or evidence that an earlier observation still holds. Equivalent wording earns credit. A correct earlier quote treated as a final measurement fails.
2. **Seal the evidence decision.** Record pass or fail, a passage-specific basis, the instant the explanation assigns to its observation, and the relation it asserts. Record the selected quote, citation ID, draft version and zero-based, end-exclusive offsets in the full prose. The checker validates the span within the cited draft or closing paragraph. An answer with no locatable draft evidence can receive a recorded failure. These are operator annotations. The semantic decision is made by inspecting the reasoning.
3. **Score judgment.** Compare the returned whole-claim label with the frozen gold and report both scores for every eligible arm. Each unused or ineligible generation is unscored on both axes. Show B-to-E gain, loss or retention on each axis for each case. Report the genuine approach, terminal gap and earlier gap individually. [Scoring rules](../../data/diagnostics/q011-evidence-check-comparison-2026-11-23/scoring.json) · [Scorer](../../scripts/q011_evidence_check/scoring.py)

With all ten arms eligible, E must pass both scores on the genuine ending, both timing cases, arrival and stop short. Any E miss yields `hold`. If E clears all five and B missed either score on the genuine case, record a genuine paired recovery. If B already passed both, record a baseline recovery. An incomplete comparison yields `inconclusive`, with eligible scores still reported. The experiment measures a factual assessment on this scene family. It gives no direct measure of literary quality.

## Budget and global stops

| Limit | Frozen value |
| --- | --- |
| Counts | Ten serial POSTs to `https://api.openai.com/v1/responses/input_tokens`. All ten must return HTTP 200 and a positive count within budget before the first generation. |
| Generations | Up to ten serial POSTs to `https://api.openai.com/v1/responses`, one per case and arm. |
| Tokens | At most 16,384 input and 4,096 output tokens per generation, including reasoning in the output ceiling. Aggregate generation ceilings are 163,840 input and 40,960 output. |
| Generation cost | At most $0.08192 per generation and **$0.81920** across ten at the rates in the frozen repository catalog. |
| Time | 120 seconds per count, 300 seconds per generation and 70 minutes for the serial schedule. |
| Retries | Zero. Each fixed slot can be sent once. |

The first failed count, non-200 response, timeout, transport error, malformed or duplicate JSON, model mismatch, refusal, incomplete output, invalid claim or citation, missing required generation usage or exceeded resource limit stops the run. Persist intent before send and retain terminal evidence and unknown usage. Cancellation or interruption consumes the single-use journal. A validly delivered semantic miss is scored and the schedule continues. No replacements, redirects, polling or fallback are authorized. [Runner and auditor](../../scripts/q011_evidence_check/run.py)

## Verification and approval

Local readback checked all 20 request bodies, 23 sealed members and 35 implementation files. All five B works matched the rehearsal. For the three previously run position cases, both B endpoint bodies also matched their archived bytes. Removing the one E sentence reproduced the B generation body for all five cases. Each count carried the same model, messages, reasoning and schema as its generation. The registered journal has zero attempts. [Readback record](../../data/diagnostics/q011-evidence-check-verification-2026-11-23/readback.json)

All **74 focused tests passed** with local captures and injected responses. A failed tenth count or exhausted wall deadline prevented every generation. The restart check refused a second dispatch after cancellation. A late HTTP failure preserved earlier eligible fixture scores in the scoring rehearsal. The scorer distinguished a genuine within-pair gain from a baseline recovery and rejected a quote attributed to the wrong draft version. Repository-wide Ruff lint, formatting and strict mypy passed across 396 Python files. [Verification results](../../data/diagnostics/q011-evidence-check-verification-2026-11-23/verified.xml)

| Item | SHA-256 |
| --- | --- |
| Approval manifest | `17addc2e72f399ee3e407050ebcb5a0345362fc911475fb49093c09c20520132` |
| Rehearsed gold | `a184380e82e1f8d7035e5af57c895d58efb5e692c2b1e1f00ecfa25712189005` |
| Scoring rules | `fe865be99ab7d1233f17c275ad775d1c6bb1bd78eb7eb7288f3fef9522d03886` |

To verify the registration without contacting either endpoint, use the local interpreter from the repository root.

```powershell
.\.venv\Scripts\python.exe -m scripts.q011_evidence_check.run verify --approved-plan-sha256 17addc2e72f399ee3e407050ebcb5a0345362fc911475fb49093c09c20520132
```

Production prompts are unchanged. Live execution awaits approval, and the full workflow canary is on hold.
