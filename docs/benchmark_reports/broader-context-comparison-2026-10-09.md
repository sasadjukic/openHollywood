# Broader story guidance and current scene obligations

Date: 2026-10-09. Production prompt v39 / graph v9 unchanged.

**Removing the broader Blueprint context did not recover overrun detection.**
The frozen OH-V01-002 scene passes under all three tested seeds in both the full
and reduced context conditions. Every reduced-context review recognizes completed
handwriting verification but still accepts the decision-to-verify endpoint.
One even paraphrases the assigned outcome as verification itself.

The removed guidance is therefore not necessary for this observed failure when
the next-scene reservation is absent. This does not show that broader context
never influences reviews, or explain the model's internal reasoning. It shifts
the immediate diagnostic target toward faithful interpretation of the current
endpoint and the distinction between a decision and its completed result.

## Controlled comparison

The user approved twelve new, contemporaneous critic probes on the existing
Ollama Cloud Gemma4 deployment. Historical responses supply context, not either
side of the live comparison.

| Fixture | Seeds | Broader context A | Current scene context B |
|---|---|---:|---:|
| Original scene-1 overrun | 19102, 19103, 19104 | 3 | 3 |
| Inconclusive preliminary investigation | 19102 | 1 | 1 |
| Explicitly authorized verification | 19102 | 1 | 1 |
| Missing ten-year-future turning point | 19102 | 1 | 1 |

Both conditions omit the next-scene reservation, following the
[preceding comparison](reservation-context-comparison-2026-10-09.md).
Condition A otherwise retains the full v39 request and exactly reproduces the
previous no-reservation request content for each fixture.

Condition B projects the Blueprint's content to only `scene_plans` containing the
complete current plan, and `voice_and_style_guide`. It omits twelve fields:
`beats`, `central_conflict`, `characters`, `creative_brief`, `locations`,
`logline`, `potential_risks`, `relationships`, `thematic_thesis`,
`unresolved_decisions`, `world_rules` and `world_summary`.

This removes the story-wide journal/flourish verification assumption, the
requirement to verify handwriting through story action, the apartment's
verification function, and broader narrative and character context. The
reduction is **7,521 characters and 1,520 reported input tokens per pair**.

Every other request field remains identical within each pair: full current
scene plan, assignment and due-now contracts, exact draft evidence catalog,
system instructions, schema, rubric, viewpoint identities and style guidance,
advisory benchmark genre/length constraints, and the initial Story Bible. That
Bible has no established facts, accepted scenes, timeline entries, threads,
state entries or prohibited contradictions that could reintroduce the removed
story guidance. The current plan's broad goal and summary remain unchanged.

The same source artifact versions, hashes, settings and seed are used within
each pair. Three pairs run A then B and three B then A in an order fixed before
inference. Original seeds 19103 and 19104 extend the source seed of 19102; all
controls use 19102. Controls retain their exact synthetic v39 versions and remain
unapproved diagnostic fixtures.

The diagnostic process temporarily changes only prompt projections. Full source
artifacts stay immutable, and projections are restored between trials. Audits
and repair guidance reflect the absent reservation in both conditions. Offline
checks verify that the current endpoint can still produce a blocking overrun
under either projection. No production source, prompt version or workflow changes.

## Results

| Fixture | Broader context A | Current scene context B | Interpretation |
|---|---|---|---|
| Original overrun | PASS, 3/3 | PASS, 3/3 | Missed in both conditions |
| Inconclusive attempt | PASS | PASS | No false overrun |
| Authorized verification | PASS | PASS | No false overrun |
| Missing required turn | REVISE | REVISE | Independent assignment blocker preserved |

All twelve responses validate on their first calls. There are no structural
repairs, rejected initial responses, semantic rerolls or outcome-dependent
additions. All three original pairs therefore compare validated first calls.
Every response returns `no_overrun`, so correct outcomes on the legitimate
controls do not establish successful overrun discrimination.

All passes receive three 5/5 craft scores. The missing-turn control receives a
3.67 mean in A and 4.0 in B, while still requiring revision. These scores are
not evidence of a quality improvement: B lacks character/world detail used to
assess craft, and craft quality is not the endpoint of this experiment.

## How the critic treats the endpoint

The unchanged original assignment says **"Elena decides to verify the
handwriting."** The reduced-context responses expose three forms of the same
acceptance failure:

| Seed | Recognized draft result | Current endpoint comparison |
|---|---|---|
| 19102 | A journal comparison concludes a mathematical match | Restates the assigned outcome as "verifying handwriting" |
| 19103 | Handwriting has been verified against the journal | Quotes the decision-to-verify outcome but treats it as achieved without overrun |
| 19104 | Handwriting has been verified against the journal | Calls the decision-to-verify outcome achieved and the stopping point exact |

The 19102 response selects the sentence stating that the samples were identical.
Its evidence resolves correctly; the problem is its representation of the
planned endpoint. The 19103 response selects retrieving the journal and the
later evidence of Elena's own hand, narrower support than a full comparison of
the scene's achieved and permitted states. The 19104 response selects the
comparison of flourishes and later psychological consequences. Valid evidence
handles do not guarantee a faithful plan comparison.

Condition A continues to acknowledge verified handwriting while accepting the
decision to verify as satisfied. Thus omitting the larger context does not remove
the core decision/result conflation. This supports a failure to enforce the
endpoint in these reviews; it does not establish a general model mechanism.

The authorized-verification control correctly describes its changed current
outcome in both conditions. However, the same prose passes under the original
decision-only outcome as well. This still fails to demonstrate sensitivity to
whether verification is permitted.

Both inconclusive-test responses concentrate on the final decision to compare
journals, rather than the inserted failed attempt. Both missing-turn responses
correctly identify the date's contradiction with the assigned future-date turn.
They also add broad plot claims that removing the date gap eliminates the
speculative element. Those generalizations remain separate from the clearly
supported assignment violation; removing the Blueprint does not eliminate them.

## What remains unresolved

The preceding experiment found that the explicit next reservation was not
necessary for the failure. This experiment finds that the omitted broader
Blueprint fields are not necessary either, under the no-reservation condition.
Neither result proves those sources have no influence in other contexts or in
combination. The reduced request still includes the complete current plan, draft,
style guidance and normal review machinery.

Because B removes a bundle of fields and changes context length, a changed
verdict would not isolate a particular instruction or distinguish its meaning
from attention/context-load effects. Here no verdict changes, so there is no
demonstrated detection benefit from this reduction. The evidence supplies no
reason to remove useful story context from production as a fix for this defect.

The next focused test should make the intended terminal knowledge state explicit
in a synthetic current-plan control: Elena decides to compare the handwriting,
and **no handwriting match is established by the end of this scene**. Compare
that with the existing decision wording and the explicitly authorized-verification
control, keeping the same drafts and review policy. This would help distinguish
an interpretation of the outcome as a minimum achievement from inability to
enforce an explicit unresolved end state. It would test a stronger plan instruction,
not establish that the original wording was followed correctly.

That additional test or any production contract change is outside this batch.
The current goal of understanding the card and summary of attempting to debunk
it remain possible influences within the scene plan itself. Results from one
story and three requested seeds do not establish general reliability; seed
handling and remote weights are not guaranteed immutable.

## Verification and cost

Source commit: `2019a11d3a0259277d28160be47f6b29f4c19a46`. The original source
critic invocation remains `d2758b4f-7a66-4587-b7c6-fc5386ff20b6`. The read-only
benchmark snapshot retains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

The existing local Ollama daemon forwarded `gemma4:31b-cloud` to Ollama Cloud,
retaining alias digest
`c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`.
Each call retained limits of 24,000 input / 8,000 output tokens.

The twelve calls used **114,884 input / 8,325 output tokens**. At the recorded
October 8 [Gemma4 rates](https://ollama.com/library/gemma4:31b-cloud), assuming
uncached input at USD 0.14/M and output at USD 0.40/M, the estimate is
**USD 0.01941376**, within the approved maximum allocation estimate of
USD 0.15744 for up to twenty-four calls. Actual charges remain unknown; the
recorded rates are not a newly verified tariff or billing receipt.

Offline checks verified the Blueprint-only difference, unchanged current
obligations/evidence/schema/settings, both-arm blocking route, projection
restoration and exact historical inputs. All prepared/live request hashes,
source and code hashes, captured response hashes and audits verified. All twelve
requests reconstructed and validated results rematerialized exactly. The unchanged
probe and endpoint suites passed **36 focused tests**. Full application gates
were not repeated for this documentation and isolated diagnostic change.

Local evidence is in `data/diagnostics/broader-context-v39-2026-10-09/`:
`experiment.py`, `plan.json`, `prepared/`, complete `live/` responses and
`assessment.json`. Production remains v39 / graph v9; canonical stories, sealed
benchmarks and historical results are unchanged. **This comparison is complete;
Step 19 remains IN PROGRESS and Step 20 is NOT STARTED.**
