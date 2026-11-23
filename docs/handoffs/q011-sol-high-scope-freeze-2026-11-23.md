# Q011 Sol-high freeze for physical position and paragraph depiction

**Ready for approval. All twelve live slots are unused.** The comparison asks whether `gpt-6.1-sol` at high reasoning can distinguish an unresolved physical position from a claim about what a complete paragraph depicts. It uses the rehearsed baseline B messages, one claim per request, and one observation per case. Approval would allow the full unpublished prose and story context at both OpenAI endpoints. [Approval manifest](../../data/diagnostics/q011-scope-comparison-2026-11-23/plan.json) · [Exact request bodies](../../data/diagnostics/q011-scope-comparison-2026-11-23/requests/)

## Cases, order and gold

Both claims begin “Elias is drawn to the entrance.” The **position** claim continues “At the scene cut he stands at the threshold.” The **depiction** claim continues “The complete closing paragraph depicts him standing at the threshold at the scene cut.” These are authored diagnostic claims derived from Q011. The historical critique v2 retains its original text and association with the genuine draft. [Local rehearsal](q011-position-depiction-rehearsal-2026-11-23.md)

| Count → generation | Case | Ending | Subject | Frozen gold | Decisive evidence |
| --- | --- | --- | --- | --- | --- |
| 1 → 7 | AP | Original approach | Position | `uncertain` | Elias passes the shoes and moves toward the threshold. His position at the cut remains open. |
| 2 → 8 | AD | Original approach | Depiction | `unsupported` | The complete paragraph ends with approach and supplies no observation placing him at the threshold. |
| 3 → 9 | RD | Authored arrival | Depiction | `supported` | “Elias stood at the threshold” appears in the closing paragraph. |
| 4 → 10 | RP | Authored arrival | Position | `supported` | That final observation establishes his position. |
| 5 → 11 | SP | Explicit stop short | Position | `unsupported` | Both feet are planted in the dirt a full stride short of the sill at the cut. |
| 6 → 12 | SD | Explicit stop short | Depiction | `unsupported` | The closing paragraph places him short of the sill and never depicts him standing at the threshold. |

Position goes first for the original and stop endings. Depiction goes first for arrival. Each pair holds the complete assessed draft, plan, blueprint, story bible, historical review, brief, schema, model and settings fixed. Only the claim text and its derived identifiers change. Both endpoints receive the same messages and schema. Gold, evidence decisions and scoring rules stay with the operator. [Frozen gold and source versions](../../data/diagnostics/q011-scope-comparison-2026-11-23/gold.json) · [Request readback](../../data/diagnostics/q011-scope-verification-2026-11-23/readback.json)

## Separate judgment and evidence scores

1. **Evidence.** For every eligible generation, inspect the reason and resolved citations against the assessed version. The worksheet withholds the returned label. Require both plan obligations (`E0233` and `E0229` or equivalent coverage), the depicted attraction, and an explanation of the final position or the complete paragraph, according to the active claim. A precise passage located in `E0883` (whole draft) or `D01` (closing paragraph) is adequate. For position, contradicting the claim requires an incompatible observation at the cut. For depiction, read the entire paragraph and allow equivalent wording. Inferring non-arrival from silence, searching for one verb, or relying on an earlier stop fails evidence. Record a passage-specific basis and seal the decisions before joining labels to gold. [Label-free source witnesses](../../data/diagnostics/q011-scope-comparison-2026-11-23/witnesses.json)
2. **Judgment.** Compare each returned whole-claim label with its frozen gold. Report the two scores for each eligible case. A provider response qualifies only when complete, within budget and bound to the correct active claim, request and citations in a closed observed journal. An unused or ineligible generation is unscored on both axes. [Scoring rules](../../data/diagnostics/q011-scope-comparison-2026-11-23/scoring.json)
3. **Decision.** Report the original two cases together, and the four clear controls separately. All six must pass both scores for `grounded_scope_split`. A complete run with any failed score yields `hold`. A missing eligible case yields `inconclusive`, with any eligible scores still reported. A positive result would establish a distinction on this passage only. [Scorer](../../scripts/q011_scope/scoring.py)

## Budget and stops

Six serial POSTs to `https://api.openai.com/v1/responses/input_tokens` must each return HTTP 200 and a positive count within 16,384 input tokens. Only then may up to six POSTs go to `https://api.openai.com/v1/responses`. Each generation is capped at 16,384 input and 4,096 output tokens including reasoning. The total generation ceilings are 98,304 input tokens, 24,576 output tokens and **$0.49152 at the frozen repository rates**. Count timeout is 120 seconds, generation timeout is 300 seconds and the serial wall limit is 42 minutes.

Stop globally on the first failed count, HTTP or transport failure, timeout, refusal, truncation, malformed or duplicate JSON, invalid claim or citation, model mismatch, missing required usage or exceeded budget. Preserve the terminal record and unknown usage. The runner persists intent before each send. Cancellation or interruption consumes the registration. There are zero retries, replacements, redirects or fallbacks. A complete, validly bound semantic miss consumes its slot and the schedule continues. [Single-use runner](../../scripts/q011_scope/run.py)

## Verification and approval identity

Independent readback verified 12 exact request bodies, 30 implementation hashes, all six rehearsal work fingerprints, each assessed draft and paragraph span, and the original critique binding. All three within-ending comparisons isolated the claim. The registered journal is ready with zero attempts. The private diagnostic files are required for byte-for-byte replay. [Readback record](../../data/diagnostics/q011-scope-verification-2026-11-23/readback.json)

All **186 focused tests passed** using local files and injected responses. Fixtures covered a failed sixth count, an exhausted wall deadline before generation, cancellation after intent, restart refusal, a late generation failure, separate scores and rejection of tampered files. The claim-scope and brief suites emitted 22 existing Pydantic serialization warnings. Repository-wide Ruff lint, formatting and strict mypy passed across 387 Python files. [Verification results](../../data/diagnostics/q011-scope-verification-2026-11-23/verified.xml)

| Frozen item | SHA-256 |
| --- | --- |
| Approval manifest | `cae13f5bb291064892d46bfd850e2ce7e77d7014af6ec58c6d412b4c70d48dd2` |
| Rehearsed gold | `b903a9bed15c12df89ab684653bb95829ce5d762d0b42649dd1669d1faa0fa92` |
| Independent scoring rules | `2cf30705783f33004500d946e16ef5376bc6d455d46151049d1f5418f2080cdc` |

To check the frozen registration locally, run the following from the repository root.

```powershell
.\.venv\Scripts\python.exe -m scripts.q011_scope.run verify --approved-plan-sha256 cae13f5bb291064892d46bfd850e2ce7e77d7014af6ec58c6d412b4c70d48dd2
```

Production prompts remain unchanged. Live calls await approval and the full workflow canary remains on hold.
