# Evidence coverage on The Pristine Lure

Five of six saved Sol explanations passed under the primary reading. The original ending's physical-position explanation was flagged. One of the five passes depended on how the explanation's conclusion was read. All six primary decisions agreed with the historical evidence scores when those scores were opened after annotation. [Saved explanations](../../tests/fixtures/pristine_lure_coverage_masked.json) · [Joined results](../../data/diagnostics/pristine-lure-coverage-transfer-2026-11-25/joined.json)

## What was frozen and masked

This Elias scene comes from a different family than *The Wading Path*. We included all six archived Sol-high B generations from its Q011 scope comparison. Two concern the original saved draft. Four concern two authored endings on that draft. All six claims are diagnostic. Each asks whether Elias is drawn to the entrance. The second clause asks either where he stands at the cut or what the complete closing paragraph depicts. The plan establishes the two assignments. The assessed draft establishes their fulfillment. [Original comparison design](q011-sol-high-scope-freeze-2026-11-23.md)

Before reading the six explanations, we froze the claim texts, both plan fields, the three draft versions, receipt hashes and exact source spans. In all three versions, the approach is at `/prose [3129,3222)` and the attraction at `[3224,3283)`. The original closing paragraph ends at offset 3284. One variant adds “Elias stood at the threshold” at `[3285,3314)`. The other adds his planted feet a full stride short of the sill at `[3285,3372)`. [Source and scope freeze](../../tests/fixtures/pristine_lure_coverage_freeze.json)

The annotation packet contained only the claim, draft version, citations and verbatim explanation, sorted by an opaque content ID. The returned label, prior judgment and evidence scores, adjudication notes and dispatch order were excluded. An operator marked exact clauses for each assertion and the evidence it invoked. The primary and alternate readings and their resulting decisions were sealed before joining the archived scores. This was one operator's analysis of plausible readings. Independent-reader agreement remains unmeasured. [Masked packet](../../tests/fixtures/pristine_lure_coverage_masked.json) · [Sealed annotations](../../tests/fixtures/pristine_lure_coverage_readings.json)

## Results

| Ending | Claim after the attraction clause | Primary coverage | Other plausible reading | Historical judgment / evidence |
| --- | --- | --- | --- | --- |
| Original approach | Physical position | Flag | Flag, different reason | Fail / Fail |
| Original approach | Paragraph depiction | Pass | — | Pass / Pass |
| Explicit arrival | Physical position | Pass | — | Pass / Pass |
| Explicit arrival | Paragraph depiction | Pass | — | Pass / Pass |
| Measured stop short | Physical position | Pass | — | Pass / Pass |
| Measured stop short | Paragraph depiction | Pass | Flag | Pass / Pass |

**The measured-stop depiction answer changed outcome.** It says the complete paragraph ends with Elias stopping a full stride short. It then concludes that his “final narrated position contradicts the assertion that he stands at the threshold.” Read together, those sentences explain what the paragraph depicts in place of standing at the sill. That earned the primary pass. If the first sentence is read as locating the evidence and the conclusion is read strictly as a statement about physical position, the depiction question goes unanswered. That reading was flagged. Both readings used the same sentence, source version and citations. The point of disagreement was what the explanation answered. [Masked answer and rationale](../../tests/fixtures/pristine_lure_coverage_readings.json)

**The original position answer stayed flagged.** “At the final narrated instant, he is approaching” can assert that Elias is physically short of the threshold. The draft gives a direction of travel and leaves his final position open. The narrower reading takes the explanation to mean that the last depicted action is approach and the plan cannot prove arrival. That reading avoids the unsupported physical inference but still leaves the actual position question unanswered. In contrast, the companion depiction answer explicitly limits its conclusion to what the paragraph shows and passes. [Verbatim explanations](../../tests/fixtures/pristine_lure_coverage_masked.json)

## Verification and implication

The replay uses the same assertion-and-scope check as the Wading Path rehearsal, with witnesses bound to this family's plan and drafts. It verifies the exact request and receipt bytes and resolves each used witness against its cited source. Tests restrict which files packet construction can open, replay the archived cases with network access blocked, and exercise a borrowed stop, plan-only citations, changed answer text and a changed pre-join decision. [Rehearsal](../../scripts/q011_scope/coverage_transfer.py) · [Regression tests](../../tests/evaluations/test_pristine_lure_coverage_transfer.py) · [Verification record](../../data/diagnostics/pristine-lure-coverage-transfer-2026-11-25/verified.xml)

All 31 focused tests passed, including the earlier Wading Path controls. Repository-wide Ruff lint, formatting and strict mypy passed across 469 Python files.

The rehearsal supports using the check to direct an operator to a specific sentence. The measured-stop case shows why an ambiguous explanation alone is insufficient grounds for a writer revision. If this check advances, the smallest next step is a second masked reading of the two disputed explanations, with the four stable explanations mixed in as controls. This family tests depiction and endpoint coverage. Whether a negative claim about an entire scene transfers remains open. B remains the default, live calls are paused and the canary is on hold.
