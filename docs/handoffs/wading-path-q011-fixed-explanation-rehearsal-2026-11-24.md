# The Wading Path · Q011 with a fixed explanation

**Changing only the original judgment to `uncertain` recovered B’s missing point. E recovered its judgment point and still failed evidence.** This is an offline edit to a copy of each answer. Sol’s two archived answers both returned `unsupported`. The rehearsal also tested whether a blanket uncertainty label would survive two endings that settle the characters’ position. [Observed answers and audit](wading-path-position-and-judgment-audit-2026-11-24.md) · [Local replay](../../data/diagnostics/wading-path-q011-fixed-explanation-2026-11-24/rehearsal.json)

## Fixed B and E explanations

Q011 is the ordinary critic’s claim that the draft fulfills **both** the assigned arrival at the breaker-panel housing and the assigned exit state of standing before the final barrier. B and E cited the same plan fields (`E0258`, `E0254`) and the same complete draft (`E1420`). The replay compared every field in each answer, replaced only `support` and carried forward the independent evidence decision sealed for that exact reason and citation list. Each score below is **judgment / evidence**, one point each.

| Original ending | Observed answer | Local label-only answer | What the explanation earns |
| --- | --- | --- | --- |
| Q011 B | `unsupported` · 0/1 | `uncertain` · **1/1** | B locates entry and the view of the housing, and says the draft does not establish the assigned standing position. This identifies a limit on proof. |
| Q011 E | `unsupported` · 0/0 | `uncertain` · **1/0** | E says the draft “depicts an earlier stopping point.” The entry and gaze establish no final distance. This factual overread survives the label change. |
| Q008 B, narrated-arrival control | `unsupported` · **1/1** | Replayed as delivered · **1/1** | The complete ending allows a definite judgment about whether the author narrated arrival. The answer confines its finding to the account. |

## Three endings and two obligations

The whole Q011 claim, critique v2, both assignments in plan v1, and all 4,804 characters of draft v1 were held fixed. Each authored version appends one final sentence in a new paragraph and receives a distinct local draft identity. The gold, full prose hashes and evidence rubric were frozen before writing the version-specific responses. The evidence worksheet binds the reason, citations, plan, and selected prose without the returned judgment. [Frozen gold and exact added sentences](../../tests/fixtures/wading_path_q011_endings.json) · [Evidence decisions](../../tests/fixtures/wading_path_q011_evidence_decisions.json)

| Ending | What the draft establishes about reaching the housing | What it establishes about standing before it at the cut | Whole-claim gold | Version-specific authored answer |
| --- | --- | --- | --- | --- |
| Original | Both reach the eastern wall and enter the plenum. They look deeper. Arrival at the housing is open. | The housing stands at the end. The pair’s final position is open. | `uncertain` | **1/1** |
| Explicit arrival | The final sentence places Elias and Maya at the named housing. | Both stand side by side before it. The preceding paragraph identifies it as the final barrier. | `supported` | **1/1** |
| Measured stop short | The final gap leaves any earlier arrival open. | Both stop three full strides short of the housing and stay there. This contradicts the required exit position and suffices to reject the conjunction. | `unsupported` | **1/1** |

As a separate check, we carried each literal `uncertain` answer, including its unchanged reason and citations, across to each authored ending. B and E each scored **0/0 on arrival** and **0/0 on the measured stop**. Both cite the original draft version and omit the new final observation. Even E’s mention of a stop supplies no evidence from the version that actually contains one. These four comparisons are local content checks. The observed deliveries stay bound to draft v1. [Replay and exact scores](../../data/diagnostics/wading-path-q011-fixed-explanation-2026-11-24/rehearsal.json)

## Verification

The local runner verifies the prior 46-member archive and replays all ten original slots before constructing the worksheet. Each authored version has a pinned full-prose hash. The final observation occupies character offsets 4806–4920 in the arrival draft and 4806–4945 in the stop draft (end exclusive). The cut in draft v1 is covered by 3995–4804. The regression tests also change the label on an otherwise adequate arrival explanation, and add “They never reached it” to the measured-stop explanation. The first retains its evidence point. The second requires a new evidence decision before it can be scored. Run `python -m scripts.wading_path_be.rehearsal` with the repository interpreter and private archive present. [Runner](../../scripts/wading_path_be/rehearsal.py) · [Regression tests](../../tests/evaluations/test_wading_path_q011_rehearsal.py)

All 46 focused tests passed, including nine for this rehearsal. Repository-wide Ruff lint, Ruff formatting and strict mypy passed across 428 Python files. A second local replay reproduced the saved worksheet and scores. [Verification record](../../data/diagnostics/wading-path-q011-fixed-explanation-2026-11-24/verified.xml)

## Readiness

**Ready to prepare a bounded observation-to-judgment comparison. Keep B as the default.** On the original, B’s evidence already licenses uncertainty and E’s unsupported stop is visible independently of its label. The authored and Q008 controls now distinguish correct recognition of an open endpoint from a tendency to answer every omission with uncertainty. These are local scoring results. Whether Sol itself can find the relevant observation and choose the right label on a new attempt remains open.

The next freeze could pair ordinary B with B supplied a short, version-bound list of **observations only** for each of the three Q011 endings. Preserve the full prose, the claim, both plan fields and the label definitions. Keep gold, relation labels and the operator’s explanation out of both requests. Replay Q008 on ordinary B as a narration control. That design would require seven counts before up to seven generations, zero retries, with separate approval. Report the original’s two scores independently and require both scores on the explicit-arrival, measured-stop and Q008 controls. A sound evidence account with the wrong label points to the judgment step. A recovery only with supplied observations would justify investigating evidence selection. This design measures assisted interpretation of one scene family. It provides no reason to rewrite its ending. Production prompts remain unchanged, live calls are paused and the full workflow canary is on hold.
