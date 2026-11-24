# The Wading Path · ordinary v61 Gemma result and frozen position claims

**The capture produced qualifying position claims from a second story family.** In OH-V01-010, Gemma independently claimed that Elias and Maya arrived at the breaker-panel housing and stood before it. The exact draft establishes that they entered the service plenum. Its last paragraph places the housing at the passage end and leaves the pair’s final position unresolved. We froze gold for one whole field about what the ending narrates and two about the characters’ achieved position. All three come from one review of one ending. [Frozen capture plan](wading-path-ordinary-v61-capture-plan-2026-11-24.md) · [Field-by-field screen](../../data/diagnostics/wading-path-v61-results-2026-11-24/field-screen.json)

## What the source establishes

The scene-four plan assigns “They reach the breaker panel housing” (outcome, `E0258`) and “They are standing before the final barrier” (exit state, `E0254`). In the draft the pair reach the eastern wall, scramble into the service plenum and tumble into the narrow space (0063–0065). They gasp for air and look deeper into the shaft (0066–0067). The closing description reads “At the end of the narrow passage, partially submerged in the rising water, stood the heavy steel housing of the master breaker panel.” The following sentence identifies it as the final barrier (0068–0069).

The grammatical subject of “stood” is the housing. The pair’s last reported movement is into the plenum. The closing description supplies the position of the equipment. It also gives no final distance from it or conclusive observation of the pair’s posture. These distinctions matter because the first claim describes a narrated event and the other two concern the achieved physical state. The complete draft is registered as `E1420`. The verified closing sequence spans code points 3995–4804, with the end offset excluded. [Frozen gold, source spans and registered references](../../data/diagnostics/wading-path-v61-results-2026-11-24/gold.json)

## Whole fields and independent scoring

| Field and scope | Whole-claim gold | What earns the separate evidence point |
| --- | --- | --- |
| Q008 · outcome assessment · narrated arrival | **`unsupported`** | Locate the assigned outcome and credit the depicted entry. Account for the entire ending and identify who enters the plenum and what stands at its end. The assertion that the draft concludes by depicting the pair arriving there fails. Their actual distance at the cut remains open. |
| Q010 · achieved state · physical position | **`uncertain`** | Credit entry for both people. Locate their gaze and the housing. Explain why these observations settle neither the pair’s standing position before the housing nor a definite stop short. |
| Q011 · endpoint comparison · fulfillment | **`uncertain`** | Locate both requirements in the plan. Use the draft to distinguish reaching the eastern wall and entering the passage from reaching the housing and standing before it. Explain the unresolved fulfillment of those two requirements. |

The three verbatim fields are preserved together below. Their IDs are local to this critique.

**Q008 · `/saved_native_audit/assignment_checks/outcome/assessment`**

> The outcome requires the characters to reach the breaker panel housing. The draft concludes with the characters scrambling into the service plenum and arriving at the end of the passage where the 'heavy steel housing of the master breaker panel' stands.

**Q010 · `/saved_native_audit/check/achieved_state`**

> Elias and Maya have entered the service plenum and are standing before the master breaker panel housing.

**Q011 · `/saved_native_audit/check/current_endpoint_comparison`**

> The draft matches the outcome ('reach the breaker panel housing') and exit state ('standing before the final barrier') defined in the scene plan.

Q008 cites excerpt 0068. Q010 and Q011 share the boundary check’s citations to 0068 and 0069. Those citations locate and identify the panel. To assess the people, the earlier sentences about the wall, entry and gaze also matter. Each field can earn one point for the exact judgment and one independently for passage-specific evidence. Equivalent source-bound citations are acceptable. No assessor was run or scored.

All 12 whole explanatory fields were screened. The summary (Q007) mentions progression to the panel but also judges emotional power, tension and sensory effect, so the whole field stays with editorial review. Q009 concerns admission of failure and trust. Q012 concerns the draft ending before the breaker is tripped and the house goes dark. Both retain the default factual brief B. The six other fields are craft scores or strengths. B remains the default. Q010 and Q011 supply the new physical-position cases for a future local rehearsal, with Q008 available as a narrated-arrival contrast. [Prior distinction between position and depiction](q011-position-depiction-rehearsal-2026-11-23.md)

## Delivery and verification

| Measure | Observed |
| --- | --- |
| Transport | One 112,471-byte request with the seven frozen inputs through the local Ollama daemon to Ollama Cloud. The request named `gemma4:31b-cloud` and the receipt identifies `gemma4:31b`. |
| Usage | 34,174 of 40,000 input tokens, zero reported cached tokens, and 1,067 of 8,000 output tokens. |
| Terminal | HTTP 200, completed with `stop`. Ollama reported 3.781 seconds and the harness recorded 4.711 seconds. One generation, zero count calls, retries or fallbacks. The journal is spent. |
| Saved review | Critique v2 `df932129-8005-49e8-bcf2-054546125288`, invocation `5a6f3522-ece2-477c-b0a9-c55665dbc32e`. Gemma returned a pass, scored all three craft dimensions 5/5 and raised no issues. |
| Source versions | Draft v1 `38e82829-604f-40df-b5a0-1c968718573e` and scene-four plan v1 `152e58e1-57ee-5c48-8bb2-bf4f7e8e104e`. All seven input hashes are preserved in the gold record. |

The isolated database gained one invocation and one critique version. Local replay reproduced the compatible native export and intake on a disposable copy. It matched all 12 fields to the raw Gemma response and checked all 69 ordered draft excerpts. The gold was sealed on November 24 at 19:27:43 UTC before any assessor output for these claims was viewed. Replay reproduced its SHA-256, `ce5d97d7565455852b452a1792a10cc40acd5ae4cf115d552d43e254fe742956`. [Terminal receipt](../../data/diagnostics/wading-path-v61-capture-2026-11-24/output/terminal.json) · [Verification record](../../data/diagnostics/wading-path-v61-results-2026-11-24/inspection.json) · [Gold seal](../../data/diagnostics/wading-path-v61-results-2026-11-24/gold-seal.json)

All 13 focused source-binding and selection regressions passed. Live calls are paused and the workflow canary remains on hold. [Local regression results](../../data/diagnostics/wading-path-v61-results-2026-11-24/source-regressions.xml)
