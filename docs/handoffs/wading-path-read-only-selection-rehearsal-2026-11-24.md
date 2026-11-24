# The Wading Path · read-only selection and B/E readiness

**Ready to freeze a five-assessment Sol-high comparison.** The saved ordinary v61 review supplies two claims about where Elias and Maya are at the scene-four cut. A third claim about what the conclusion narrates provides a control using the same ending. B is the default factual brief. E adds one sentence asking which draft observation establishes, rules out or leaves open the named position, and when that observation applies. This rehearsal exercised selection only. All three claims remain unassessed. [Original capture and gold](wading-path-ordinary-v61-capture-results-2026-11-24.md)

## Selection against frozen gold

| Whole review field | Rehearsed briefs | Frozen judgment | What earns the independent evidence point |
| --- | --- | --- | --- |
| Q010 · achieved state | B and E | **uncertain** | Credit both characters’ entry into the plenum. Follow their gaze deeper into the shaft and identify the housing as the thing standing at its end. Explain why their final distance and posture remain open. |
| Q011 · endpoint fulfillment | E and B | **uncertain** | Locate both plan requirements, reaching the housing and standing before the final barrier. Credit reaching the eastern wall and entering the plenum. Identify the housing as the barrier and explain what the last view leaves unresolved about fulfillment of each requirement. |
| Q008 · narrated arrival | B only | **unsupported** | Locate the planned outcome and credit the narrated entry. Read through the last line. The ending locates the housing at the passage end without depicting the pair arriving there. Their physical position at the cut remains open. |

The selections retained each verbatim field and its full span in critique v2. Q010 uses the complete draft v1 (`E1420`). Q008 also uses the plan v1 outcome (`E0258`). Q011 uses both that outcome and the exit state (`E0254`). All five previews retain the full historical source context with exactly one active claim. Within each B/E pair, the work fingerprint, scope, whole-field text and source obligations matched. Only the arm identifier and the added sentence differed. [Five read-only previews](../../data/diagnostics/wading-path-selection-rehearsal-2026-11-24/previews.json)

## Local verification

The rehearsal reopened a byte-identical disposable copy of the archived database through saved-review intake. It built the work-brief previews before reading the sealed scoring key. The subsequent check matched the invocation, critique, draft, plan, seven input version hashes, and seven closing excerpts against their registered references and exact draft spans. Both full replays produced identical output with network access blocked. The nine checked archive and gold files retained their hashes. No assessor ran and no writer work was dispatched. [Gold verification](../../data/diagnostics/wading-path-selection-rehearsal-2026-11-24/gold-verification.json) · [Replay and integrity record](../../data/diagnostics/wading-path-selection-rehearsal-2026-11-24/verification.json)

Regression controls cover switching fields and returning to the original selection, a different source, a shortened claim, swapped field pointers, an omitted plan reference, an exchanged E question, an E brief on Q008 and an altered gold file. Run `python -m scripts.q011_transfer.wading_path_selection` from the repository root in the project environment to reproduce the previews and the operator-side gold check. [Replay script](../../scripts/q011_transfer/wading_path_selection.py) · [Regressions](../../tests/evaluations/test_wading_path_selection.py) · [Focused test results](../../data/diagnostics/wading-path-selection-rehearsal-2026-11-24/regressions.xml)

All 106 focused tests passed, including ten Wading Path selection regressions. The existing brief and claim-scope tests emitted 22 Pydantic serialization warnings. Repository-wide Ruff lint, formatting and strict mypy passed across 419 Python files.

## Proposed bounded comparison

1. Freeze five independent Sol-high requests in the rehearsed order of Q010 B, Q010 E, Q008 B, Q011 E and Q011 B. The two pairs reverse arm order. Q008 gets a single default brief because its factual target is narrated arrival. Keep full context, model settings and response schema fixed within pairs. Verify the exact paired request differences and exclude scoring gold from both endpoints.
2. Freeze token and time budgets for these assessor requests, the single-use journal and stops before seeking live approval. Propose **five input counts before up to five generations, zero retries**, for at most ten endpoint calls. Require every count to pass before generation and preserve each terminal result.
3. For every eligible response, score the exact whole-claim judgment and passage-specific evidence independently, one point each. Report the two position pairs separately and show the Q008 control on its own. A quote locating the housing alone cannot earn the evidence point. The plan establishes what was required. Inferring definite nonarrival from an omitted action also fails the evidence criterion. [Original scoring key](../../data/diagnostics/wading-path-v61-results-2026-11-24/gold.json)

A gain for E on either position claim, with both control scores passing and no paired loss, would support further investigation. Equal passing scores would show that B handled these cases. A failed control or loss on either score would limit any claim of benefit. The two position fields come from one review of one ending, so they cannot estimate a general success rate or the effect on story quality. B remains the default. Live calls are paused and the workflow canary stays on hold.
