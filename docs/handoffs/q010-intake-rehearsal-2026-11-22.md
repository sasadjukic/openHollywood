# Q010 ending-claim rehearsal and smoke readiness

**Ready to prepare one Sol-high smoke for separate approval.** The original Elias critique yielded one factual target, Q010. Grounded uncertainty passed on both an excerpt citation and a precisely located full-draft citation. Both confident readings of the ending failed. Elara’s Q016 stayed held and produced zero assessor requests. All responses in this rehearsal were authored fixtures. There were zero live counts, generations or writer calls. [Frozen gold and exact sources](q008-q013-ending-claim-audit-2026-11-22.md)

## Q010 request and gold exclusion

The source was *The Pristine Lure*, Gemma invocation `a2893a10-cc21-4844-9393-65f56f044f4d`. The selected artifact was critique v2 (`2268e6e8-b82b-4cca-932f-55cc418a58b5`), assessing draft v1 (`b74efc96-dbe6-4147-8dd3-a1c24f295321`) with Scene Plan v1 (`b5179ac9-5585-5e5b-9555-20ca70b68f6a`). The entire 87-character achieved-state field was active. The other eleven fields remained available as review context.

> What does the draft establish about Elias's movement and position when the scene ends?

The work brief directs the assessor to locate the relevant passage and address both parts of the critic’s claim. The scope supplies the complete draft reference, `E0883`. The original review also exposes the critic’s own citation. A future result will measure performance with those source clues available.

| Model-facing body | Bytes | SHA-256 |
| --- | ---: | --- |
| Input count | 263,928 | `2ee4c9e4617f6b8c7cc203af1d4491c9ec85c916ea3b9c68c2fa3971f16dcb46` |
| Generation | 264,075 | `b30c0697f7aca46f7ae7075ad17a2c15cfc13c4a6c0fd8458d7425a743a35bb5` |

Both bodies reproduced byte-for-byte with access to the scorer files blocked. They carried identical messages, original critic context, complete draft and plan, and a strict response schema with only Q010. All 883 evidence references resolved to their original fields. A separate inspection checked the serialized bodies against the source and the frozen gold. Injecting either an expected-label field or the scorer’s rationale into either body triggered rejection in all four controls. The schema retains all three permitted labels. [Shared packet renderer](../../apps/api/open_hollywood_api/services/saved_review_openai_fixture.py)

## Grounded uncertainty and the two overreads

The frozen whole-claim label is `uncertain`. The last sentence establishes that Elias passed the shoes and moved toward the threshold. His precise position at the cut remains unresolved. Each fixture went through the in-memory OpenAI response mapping and native claim binder. We compared its returned label with gold and inspected the explanation against its actual citation. Evidence credit requires locating the final movement, crediting the first clause and respecting the limit on the second.

| Authored answer | Citation | Claim label | Evidence | Reason |
| --- | --- | --- | --- | --- |
| Uncertain, with the final excerpt | `E0321` | Pass | Pass | Locates the movement and explains what remains open. |
| Uncertain, with the complete draft | `E0883` | Pass | Pass | Identifies and quotes the final sentence within that draft. |
| Supported because he crossed | `E0321` | Fail | Fail | Adds a crossing to the cited approach. |
| Unsupported because he stopped outside | `E0321` | Fail | Fail | Adds a stop that the same sentence never depicts. |
| Uncertain because the draft is missing | `E0229` | Pass | Fail | Cites the plan’s assigned exit state. The complete draft was supplied. |
| Supported, paired with the grounded uncertainty explanation | `E0321` | Fail | Pass | The label changed. The citation and reasoning still meet the evidence obligations. |

The six structurally valid finals all bound to Q010. The evidence judgments are recorded against the exact fixture-response hashes. A future live response needs its own passage-level inspection. The binder also rejected an extra Q016 result in a Q010 reply and a receipt carrying the old Q008 request digest. [Native result binding](../../engine/open_hollywood_engine/evaluations/assessment_result.py)

## Q016 hold

For *The Impossible Card*, the intake retained the complete 253-character endpoint comparison from critique v3. Q016 was the sole mixed hold, with sixteen unselected fields and zero pending units. It produced no work batch, count body or generation body. In a separate control, a mechanically consistent source declaration and brief were supplied and the explicit hold reason removed. The mixed reading alone kept Q016 held. Whether Elara’s handwriting test conveys continuing obsession remains a reader judgment.

## Verification and next step

All **193 focused regressions** passed across intake, claim scope, result binding, saved-review wire mapping and the existing Q008 smoke journal. The claim-scope tests emitted 13 Pydantic serialization warnings. All 24 original registration files and seals retained their bytes and modification times through replay. The private evidence is in `data/diagnostics/q010-intake-rehearsal-2026-11-22/`. Run `prepare.py`, `verify_requests.py`, `inject.py` and `score.py` in that order with the repository Python. The directory contains the rendered payloads, bound fixture responses, separate scores and JUnit report.

**Next, prepare the Q010-specific approval manifest and single-use journal.** Use the critique v2 selection, one input count, at most one generation and zero retries. Bind both payload hashes and the frozen scoring criteria. Verify that a failed or over-budget count stops generation and that a restart after a generation intent cannot dispatch again. The existing Q008 registration and spent approval target its older outcome claim. The Q010 rehearsal used the shared renderer with a fresh intake and work identity. Actual Q010 count, usage, latency and Sol’s judgment remain unmeasured. The full workflow canary remains on hold.
