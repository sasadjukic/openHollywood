# One ordinary v61 Gemma critic capture — results, November 20, 2026

**The capture succeeded on its one authorized generation.** The ordinary production
critic returned a complete review, and both native export and saved-review intake
accepted it. One substantive whole claim now has independent, source-based gold.
There were zero count calls, retries, fallbacks, writer calls or assessor calls.
The full workflow canary remains on hold. [Frozen plan](ordinary-v61-single-capture-plan-2026-11-20.md)

## Execution

| Measure | Observed |
| --- | --- |
| Model and transport | Requested `gemma4:31b-cloud` through the local Ollama daemon. Response model `gemma4:31b`, HTTP 200, `done=true`, finish reason `stop`. |
| Version | The operator reported Ollama **0.40.16**. The frozen capture included no version probe. |
| Resources | 18,270 input tokens and 945 output tokens, within the 24,000 and 8,000 limits. Ollama reported 2.672 seconds total. The local harness recorded 3.655 seconds. |
| Cost | The application reserved USD 0.20. Actual billing is unknown. |
| Lineage | Run `986c416f-9bf6-40f1-800c-4d7c07b843fd`, invocation `a2893a10-cc21-4844-9393-65f56f044f4d`, critique version `2268e6e8-b82b-4cca-932f-55cc418a58b5`. |
| Request | The 65,218-byte body matched the approved SHA-256 `35452ffd86fe44f4639f3fada86b7d00a97c1aaece16911dcba5e6195392bc51`. The ledger records the slot as dispatched. |

The private workspace gained exactly one invocation and one artifact version. The
successful creator links to the four frozen input versions. The read-only export
recovered the original two messages, the normalized critique and its schema-7 audit
under prompt 61 and graph 9. The raw reply and normalized audit agree on the
assignment checks and scene boundary. This is a provider-generated review of a
saved scene through the isolated ordinary critic entry point.

## What Gemma saw in the scene

Gemma returned **pass**, marked the turning point and outcome met, and recorded
aligned viewpoint and no scene overrun. It listed no issues, violations or repair
conditions. It gave 5/5 for character consistency, dramatic progress and prose
quality. Those scores are Gemma’s editorial judgments. This run measured no human
preference or change in story quality.

The most revealing detail is the ending. The Scene Plan’s **outcome** asks that
Elias be drawn to the building’s entrance. The draft ends with him stepping past the
shoes and moving **“toward the dark, open threshold.”** Gemma’s outcome explanation
accurately describes those actions and their narrated motive. Its separate
`achieved_state` says he **“is entering the threshold,”** and its endpoint comparison
treats the plan’s **“stands at the threshold”** exit state as achieved. The final
sentence establishes his direction and attraction. It leaves his arrival or entry
unconfirmed. The no-overrun verdict can coexist with that overstatement.

The turning-point explanation also illustrates citation coverage. Its structured
references identify the red shoe (0027) and the circle around the stroller (0032).
The contact with something soft occurs in 0025, the blue sneaker in 0029, and the
explicit identification as children’s shoes in 0033. The full passage supplies
details beyond the two structured citations. Only the outcome field below was
admitted for independent assessment.

## Gold and read-only replay

**Q008, the complete 307-character outcome assessment, has frozen gold
`supported`.** Its two material obligations are independently checkable. The
standalone plan supplies the assigned outcome (evidence registry `E0233`). The
draft’s final sentence supplies the movement past the shoes, the direction of travel
and the motive quoted by the critic (`E0321`, draft excerpt 0040). The complete
version-bound draft is also available at `E0883`. Gold requires coverage of both
obligations and permits equivalent evidence from the same sources.

The verbatim field, offsets, review and source identities, exact witnesses,
rationale and expected label were written and hashed **before** local replay or any
assessor-output inspection. Gold file SHA-256 is
`5c22a997adb4b8a533c4e3442f4e779149fd0179dd79a20ab4aeac2580cafbb0`.
Replaying the saved-review intake on a byte-identical database copy reproduced the
captured export. Q008 was the sole pending unit. The replay retained the original
messages, all 12 explanatory fields, five context documents and 883 evidence
locations. A second intake export reused identical bytes. No assessor result exists
for Q008, so assessor accuracy remains unmeasured.

The original private receipts, SQLite workspace and native export are under
`data/diagnostics/ordinary-v61-single-capture-2026-11-20/output/`. The gold, intake
and verification receipt are under
`data/diagnostics/ordinary-v61-single-capture-results-2026-11-20/`. All six original
capture files retained their hashes through inspection.

## Recommended next steps

1. **Qualify this one genuine source locally.** Give the capture its own saved-review
   registration. Replay both exact artifact selections (critique and reviewed draft)
   through the downstream request mapping using fixtures. Verify that only Q008 is
   active, both source obligations and the full context arrive, and the gold stays
   outside the model input. Include wrong-version and incomplete-delivery controls.
   [Existing authored-fixture mapping](assessment-saved-review-openai-2026-11-19.md)
2. **If those checks pass, submit a one-claim assessor smoke for separate approval.**
   Use one input count followed by at most one Sol-high assessment generation, with
   zero retries. Score the whole-claim label and coverage of both witnesses separately.
   Keep the endpoint wording as a candidate for a later contrast. A single supported
   claim can test this delivery path but cannot establish general reviewer accuracy.

Production prompts remain unchanged. Further live calls are paused.
