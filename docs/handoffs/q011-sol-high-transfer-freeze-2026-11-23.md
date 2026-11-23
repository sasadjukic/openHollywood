# Sol-high B/E transfer comparison · approval plan

**Ready for approval.** Eight admitted authored endings give sixteen paired assessments. The registered journal is unused. Approval would authorize sending the full prose and context at both OpenAI endpoints, with sixteen serial input counts before up to sixteen serial generations and zero retries. B remains the default. The five historical Q011 pairs stay offline. [Frozen manifest](../../data/diagnostics/q011-transfer-comparison-2026-11-23/plan.json) · [Exact request bodies](../../data/diagnostics/q011-transfer-comparison-2026-11-23/requests/) · [Prior transfer audit](q011-evidence-check-transfer-audit-2026-11-23.md)

## Cases, gold and order

The question is whether E helps Sol distinguish a character’s or an object’s *position at the cut* from motion toward that position. In *The Understudy’s Hem*, Iven fastens his cuff with the red pin. The second clause says he stands on the blue star at the cut. In *The Mended Burgee*, Runa hoists the mended pennant. The second clause says the skiff’s bow is level with the white post at the cut. Alignment can occur while the boat is moving.

| Ending | Stage case and order | Harbor case and order | Sealed whole-claim judgment | Decisive draft evidence |
| --- | --- | --- | --- | --- |
| Approach | T01 · B → E | T02 · E → B | `uncertain` | Direction is known. Final position is open. |
| Arrival | T03 · E → B | T04 · B → E | `supported` | The ending places Iven on the star or the bow level with the post. |
| Gap at the cut | T05 · B → E | T06 · E → B | `unsupported` | A board’s width or a boat length still separates the subject from the landmark. |
| Gap before renewed motion | T07 · E → B | T08 · B → E | `uncertain` | The same measured gap precedes further movement of unspecified extent. |

Both phases visit T01 through T08 in numerical order, using the arm order above. Each family has two B-first and two E-first pairs. Each ending type has one of each. The gold and exact packet bytes are copied from the prior admission, including witness offsets and draft versions. Gold was authored locally before inference. [Eight packets](../../data/diagnostics/q011-transfer-comparison-2026-11-23/packets/) · [Sealed gold](../../data/diagnostics/q011-transfer-comparison-2026-11-23/gold.json)

## What changes between B and E

Both arms use `gpt-6.1-sol` at `high` with the same system message, response schema, active claim, complete story context, plan and assessed draft. Both expose the same four citation locations for the outcome, exit state, full prose and closing paragraph. The closing-paragraph locator resolves to the original draft version and offsets. Gold, expected witnesses, sibling endings, scores and arm IDs are operator-only.

B asks the assessor to locate both plan fields and the relevant passage and explain what each part of the claim requires. E appends the following sentence in the stage family.

> Identify the draft observation your conclusion relies on, say when it applies, and explain whether it establishes, rules out, or leaves open Iven standing on the blue star at the scene cut.

The harbor version substitutes “the skiff's bow being level with the white post” for “Iven standing on the blue star.” Removing the sentence reproduces the complete B generation body in every pair. In all sixteen cells the count uses exactly the generation’s model, reasoning, messages and response schema. [Freeze implementation](../../scripts/q011_transfer/plan.py) · [Registered readback](../../data/diagnostics/q011-transfer-freeze-verification-2026-11-23/readback.json)

## Independent scoring and decision

1. Inspect every fixed slot and retain eligibility, usage and terminal state. Score each complete, budgeted generation bound to its request in a closed observed journal. An ineligible slot receives two unscored entries.
2. Review evidence with arm, returned support label and dispatch order hidden. Check both plan assignments and locate the observed first action and final-position evidence in the cited draft. Record the exact first-action span and the position span, instant and physical implication. Credit equivalent grounded wording. The harbor hoist appears before the last paragraph, so a citation covering only that paragraph cannot establish the hoist. Seal these decisions before joining to gold. [Evidence form](../../data/diagnostics/q011-transfer-comparison-2026-11-23/evidence-form-schema.json) · [Scoring rules](../../data/diagnostics/q011-transfer-comparison-2026-11-23/scoring.json)
3. Score the returned judgment by exact gold-label match. Report both axes for each arm, gains and losses per axis, all B joint passes, each of the four unresolved pairs and each of the four determinate control pairs. A recovery requires B to miss at least one axis and E to pass both on the same unresolved case.
4. An incomplete comparison is **inconclusive**. Any E miss in a complete comparison yields **hold**. With eight E joint passes, call a **cross-family recovery** only if at least one unresolved case recovers in each family. Identify which ending types recovered in which families. Gains in one family remain family-specific. If B passes all unresolved cases, distinguish a perfect B from gains confined to determinate controls. [Scorer](../../scripts/q011_transfer/scoring.py)

## Budget and stops

| Frozen limit | Value |
| --- | --- |
| Counts, slots 1–16 | One POST per case and arm to `https://api.openai.com/v1/responses/input_tokens`. All sixteen must return HTTP 200 with a positive in-budget count. |
| Generations, slots 17–32 | At most one POST per case and arm to `https://api.openai.com/v1/responses`, in the same order. |
| Generation tokens | 16,384 input and 4,096 output per generation, including reasoning. Aggregate maxima are 262,144 input and 65,536 output tokens. |
| Generation cost | $0.08192 per generation and $1.31072 total at the frozen repository catalog rates. |
| Time | 120 seconds per count, 300 seconds per generation and 112 minutes for the serial schedule. |
| Attempts | At most 32 endpoint requests. Zero retries or replacements. |

Before dispatch the runner checks the approval digest, sources, implementation, exact request bytes and single-use journal. It writes intent before sending. The first failed count, transport or HTTP error, timeout, invalid or duplicate JSON, model mismatch, refusal, incomplete output, invalid claim or citation, missing required generation usage or exceeded resource limit stops the schedule. A valid semantic miss is scored and execution continues. An interruption consumes the journal. The audit preserves unknown usage and every untouched slot. Redirects, polling and fallback are disabled. [Runner and auditor](../../scripts/q011_transfer/run.py)

## Approval and local verification

Approval SHA-256 is `6ef2effd0f6d9cbfbc54962b0b984b0fcd49039af7a457db0f56341d46166588`. The registered readback verified 44 sealed members and 41 implementation files, all 32 bodies, the admitted context, plan and draft versions, and arm isolation in every pair. All 32 slots were unattempted.

All 37 focused tests passed. Injected responses verified the sixteenth-count gate, late HTTP stop, missing usage, invalid citation, cancellation, and rejection of a second dispatch. Scoring fixtures exercised both axes independently and all six decision branches. Reassigning the harbor hoist to the closing paragraph or the closing evidence to a different draft version failed validation. [Focused results](../../data/diagnostics/q011-transfer-freeze-verification-2026-11-23/verified.xml) · [Transfer test cases](../../tests/api/test_q011_transfer_freeze.py)

The full Python suite passed all 2,803 tests and reported 56 warnings. Repository-wide Ruff lint, formatting and strict mypy also passed across 405 Python files. [Full suite results](../../data/diagnostics/q011-transfer-freeze-verification-2026-11-23/python-suite.xml)

To check the registered freeze locally, run the following command from the repository root.

```powershell
.\.venv\Scripts\python.exe -m scripts.q011_transfer.run verify --approved-plan-sha256 6ef2effd0f6d9cbfbc54962b0b984b0fcd49039af7a457db0f56341d46166588
```

One generation per arm on two authored scene families can show a transfer signal. Ordinary-review reliability, effects on writer revisions and reader judgments of story quality require separate evidence. Live execution awaits approval. The full workflow canary remains on hold.
