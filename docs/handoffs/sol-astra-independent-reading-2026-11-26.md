# Independent reading of 16 Sol and Astra explanations

**Keep B as the default.** A fresh Codex reader agreed with the earlier factual-sufficiency reading on **16/16** explanations. Eleven adequately answered the whole claim without consequential overreach. On diagnostic completeness, the reader agreed with the sealed evidence grades on **13/16**. All three disagreements involved accurate X explanations for which the reader wanted a more precise passage reference. The original scores stand. [November 25 audit and selection](sol-astra-scope-score-audit-2026-11-25.md)

## Findings by case

Each cell shows the independent reader’s primary verdicts on **factual sufficiency / diagnostic completeness**. A 1 is a pass. A 0 is a fail. The returned model label was hidden. These numbers grade the explanation itself. X is the explicit-scope presentation and B is the ordinary brief.

| Case | Sol B | Sol X | Astra B | Astra X |
| --- | ---: | ---: | ---: | ---: |
| Wading Path SN · does the draft narrate a joint arrival? | 0/0 | 1/1 | 0/0 | 1/0 |
| Wading Path SE · did a visit occur at any time? | 0/0 | 0/0 | 0/0 | 1/1 |
| Planetarium ON · does the open draft narrate a projection? | 1/0 | 1/0 | 1/0 | 1/0 |
| Planetarium PE · did the confirmed projection occur at any time? | 1/0 | 1/1 | 1/1 | 1/1 |

**Three factual gains with X survived independent review.** On Wading Path SN, both B explanations converted the closing stop into an unwarranted denial of arrival anywhere in the scene. Both X explanations confined the conclusion to what the narrator recounts. On SE, Astra X distinguished the closing gap from the earlier period in which a visit remains unresolved. Sol X still denied a visit throughout the scene. This is corroboration of the earlier reading of saved answers. The generation history still contains one Astra X observation on this difficult request. [Sealed independent readings](../../data/diagnostics/scope-independent-reading-2026-11-26/reader/sealed-reading.json) · [Original Wading Path scores](wading-path-sol-astra-scope-results-2026-11-25.md)

**All eight planetarium explanations passed factual sufficiency.** In particular, Sol B located the projector casting the comet across the dome. That occurrence suffices for PE. Its explanation omitted the image going out before Kit returned, which the diagnostic explicitly required. Both readers therefore found the factual answer adequate and the diagnostic explanation incomplete. [Exact planetarium claims and criteria](../../tests/fixtures/planetarium_scope_gold.json)

## Where the readings differ

| Explanation | Prior diagnostic grade | Independent primary | Basis for the difference |
| --- | ---: | ---: | --- |
| Wading Path SN · Astra X | Pass | Fail | Astra names the pair’s entry and their stop short. The frozen criterion also names their sightline to the housing. The earlier grader accepted the account of the approach. The independent reader required a locator for the intervening view. |
| Planetarium ON · Sol X | Pass | Fail | Sol limits the blank dome to the closing interval. The earlier grader accepted that time boundary as a locator for the uncovered interval. The independent reader looked for where the draft summarizes the middle cues. |
| Planetarium ON · Astra X | Pass | Fail | Astra explicitly leaves an earlier projection unestablished. The independent reader accepted that factual conclusion but found no reference to the passage where the women work through the middle pages. |

The reader recorded the prior pass as a plausible alternative **on all three disputed diagnostic grades before unmasking**. There was also one factual alternative on Wading Path SE, Sol B. The primary reading found that “Their approach never reaches the housing” leaves the earlier-visit question unanswered. A narrower reading takes “their approach” as deliberately limiting the statement to the described route and accepts that as an implicit acknowledgment that arrival is unestablished. Under that alternative, factual sufficiency passes while diagnostic completeness still fails. Sol X’s categorical denial would then be a factual loss relative to Sol B on this pair. [All primary and alternative readings joined to the prior assessments](../../data/diagnostics/scope-independent-reading-2026-11-26/operator/comparison.json)

Across the eight selected B/X pairs, the two primary readings agree on **three factual gains, five ties and zero losses**. The independent reading counts **three diagnostic gains** (Sol SN, Astra SE and Sol PE), compared with six under the sealed grading. This distinction matters to routing. Evidence that X removed a false scene-wide assertion survived masking. Some apparent gains in diagnostic detail depend on whether describing an interval is enough to locate the relevant passage.

## Masking, sealing and verification

A new Codex reader started without this conversation’s history. Its sole evidence input contained the 16 verbatim explanations, the four exact claims and frozen criteria, and the three complete selected draft versions with their E1420 citation. Each explanation received a fresh opaque identifier. The rows were randomly shuffled. Model, presentation, returned label, dispatch order and prior grades were excluded. The operator kept the identity map separately. The claims and story wording were visible so the reader could judge the reasons against the actual prose. [Masked reader packet](../../data/diagnostics/scope-independent-reading-2026-11-26/reader/packet.json)

The packet SHA-256 is `90373e1c2d84ed2daa0b36b96ecfe721284d6a04001f6ed3664439f10fe5a130`. The reader sealed both verdicts, their bases, verbatim quotations and any alternative under `d8b68ba4321a079cd48457ce4a9aee20f8441b20f3dc9edbab377b41ccaedd47` before the join. Local replay verified all 16 identities against the original generation terminals, exact drafts, claims, frozen criteria and prior records. It checked 32 quotations and reproduced every joined verdict with network access disabled. Three tamper checks rejected an edited reader rationale, a reordered packet and a swapped map. All 26 focused source, scoring and regression tests passed. This is agreement between two readings of the same selected answers. It gives no estimate of how often a model will generate them again. [Offline replay](../../data/diagnostics/scope-independent-reading-2026-11-26/operator/replay.py) · [Source checks](../../data/diagnostics/scope-independent-reading-2026-11-26/operator/source-checks.xml)

## Recommended next step

**Resolve what counts as an equivalent passage reference locally.** Use the three disputed explanations and the Sol B factual alternative as four fixtures. For each, write one minimal change that explicitly supplies the missing sightline, summarized middle cues or earlier-event uncertainty. Freeze which parts of the explanation are necessary for factual sufficiency and which are additional diagnostic requirements. Then verify that an equivalent paraphrase passes and that an unsupported scene-wide denial fails. This directly addresses the disagreement without spending another generation or changing historical grades.

If model routing still warrants a test after that clarification, prepare the proposed Wading Path SE repeat. Four new observations per arm on the same hard claim, plus one confirmed and one excluded control per arm, would require **24 counts before up to 24 generations**, with zero retries and separate approval. Only fresh trials would count toward repeatability. B remains the production default, live inference is paused and the full workflow canary stays on hold.
