# Q008 downstream assessment qualification

**Decision, 2026-11-20.** Q008 qualifies for preparation of a single Sol-high smoke
using the original critique selection. Selecting the draft exercises a second
inspector entry point for the same claim. A second assessment would repeat the
question. This qualification used in-memory responses throughout. The only observed
model output in the source is the previously captured Gemma critique.
[Gemma capture, claim admission and independent gold](ordinary-v61-single-capture-results-2026-11-20.md)

## Source and model input

Registration `saved-v61-q008-2026-11-20` binds Gemma invocation
`a2893a10-cc21-4844-9393-65f56f044f4d` to critique version
`2268e6e8-b82b-4cca-932f-55cc418a58b5` and reviewed draft version
`b74efc96-dbe6-4147-8dd3-a1c24f295321`. The source check matches the recorded
HTTP reply to the creator’s response digest, the successful terminal to the run
and critique, and the SQLite image to the terminal digest. Replay rebuilds the
intake from a disposable copy. This registration allows the exact 24,571,904-byte
database. Its seal is `ea59f333b71458477f3a6bf5e33a1f2906595caa721835ed4e59872cc683ae6d`.

At the mock transport boundary, the count and generation requests carried the same
307-character Q008 claim, original two critic messages with story context, source
declarations, work brief and all 12 field dispositions. Only Q008 was active. The
compact view represented all five context documents. The local provenance document
contributed its identity and digest. All 883 registry locations resolved back to
the original versions, field pointers, text, offsets and hashes.

| Selected artifact | Count body | Generation body | Request manifest SHA-256 |
| --- | ---: | ---: | --- |
| Original critique | 265,153 bytes | 265,300 bytes | `0aa8d63ce59895017f07750146b267997c85e2f54777f5d0e916e18954549b93` |
| Reviewed draft | 265,152 bytes | 265,299 bytes | `ab5816798cbe453ca1a4c4508e8950d6a9d159bfe61e4039495cc979961cf564` |

The selection is the only difference in the two model-facing packets. Both carry
the exact review/draft pair. The application used the existing `gpt-6.1-sol` high
mapping, strict claim schema and count-before-generation order. For the recommended
critique selection, the count body SHA-256 is
`9c29c18a3e2c9f3322785f25ccc61e8889898ae770e3ab78669c359870cfce1a` and the
generation body SHA-256 is
`6c05c8c449abb43de995b7f5bad490e9b30bb5c8428b3cc870c916d01dcc790e`.

## Gold exclusion and citation coverage

The source registration contains the accepted intake, offline work packet and
critic receipts. The scorer’s files live outside it. The qualification blocked reads
of those files while preparing requests, capturing mock exchanges and exporting.
Each intercepted request was independently compared with the admitted source. A
separate scorer-side check examined both endpoints for both selections for the gold
record, expected-label fields, scorer rationale, evidence-adequacy judgment, gold
digest and injected final. The scoring material was absent.

The work brief does tell the assessor **what to check**. It names the plan outcome
and asks for the actual final action, direction and motive. Its scope points to the
plan (`E0233`) and the full draft (`E0883`). The model can locate the final
sentence (`E0321`) through the registry. These are legitimate source clues. A
future result will measure assessment with that guidance already supplied.

Both injected completions returned `uncertain` with the scope’s two references.
Both bound to their own request and could be published and reused byte-for-byte
as fixtures. The independent frozen label is `supported`. The fixture demonstrates
delivery and citation binding only. Semantic support, citation adequacy and craft
remain unassessed. Each export records injected origin and zero live calls.

## Controls

| Control exercised for each selection | Observed behavior |
| --- | --- |
| Substitute a different immutable version while retaining the selected role and content digest | Refused before creating a journal or dispatching a request. |
| Use the other valid selection’s journal | Manifest binding failed. No publication. |
| Substitute the version in the count or generation body | The altered request never reached the mock transport. A valid prior count was retained when the alteration affected generation. |
| Inject a count of 96,001 | Count rejected and journal closed with zero generation attempts. No completion. |
| Interrupt after generation intent | One possibly-sent attempt, unknown generation usage, no bound result or publication. |
| Remove the closing record or alter the terminal bytes | Missing closure or failed terminal binding prevented publication. |
| Return a length-limited response or omit Q008 from a completed response | Both had terminal and closing records. The mapper rejected the incomplete response and the native binder rejected the missing claim. Neither produced a publication. |

## Readiness and next step

**Ready to freeze one smoke for separate approval.** Use the critique-selected
request, one OpenAI input count and at most one generation, with zero retries or
replacement slots. Both endpoints would receive the full story context. Prepare a
single-use observed-transport journal for this registration and qualify it with
injected interruption and error cases. Bind its approval manifest to the exact
request bytes above. A failed count or exceeded limit ends the smoke. A generation
intent spends the slot even if the terminal is lost. Preserve a refusal, truncated
response or incomplete claim as its own outcome. Publish an observed completion
only after verifying the returned model, both artifact versions and the single
Q008 result against that journal.

The local input reservation for Q008 is **96,000 tokens**, with **32,000** available
for output including reasoning and a **$0.60** ceiling. Four similarly sized
requests previously counted 62,243–66,729 input tokens. This is the basis for
raising the Q008 reservation above the authored fixture’s 24,000. Boundary checks
admitted 96,000 and rejected 96,001. At the repository’s pinned rates the maximum
reservation is $0.56. The actual Q008 input count, model acceptance, latency, usage
and billed amount are unknown. [Earlier measured counts](assessment-openai-compact-smoke-results-2026-11-14.md)

After an observed delivery, score the **whole-claim label**, **plan coverage** and
**draft-ending coverage** separately against the frozen gold. Equivalent
version-bound witnesses are eligible. For a full-draft citation, inspect whether
the explanation identifies the passage establishing the movement, direction and
motive. The claim describes Elias moving toward the threshold. An inference that
he arrived or entered would exceed the depicted action. This smoke can establish
one factual assessment through this path. Story quality and general assessor
accuracy require separate evidence.

## Local evidence and replay

The private workspace is `data/diagnostics/q008-downstream-2026-11-20/`. The two
selection files are `original_review.json` and `reviewed_draft.json`. The
`qualified/` directory contains both journals, fixture publications, control audits
and the receipts `verification.json` and `evidence-verification.json`. Additional
terminal controls are in `partial-responses/`. All six original capture files, all
11 registered members and the frozen gold retain their verified digests. Step 19 remains
in progress. Production prompts are unchanged and the full workflow canary is on hold.

The operator CLI independently reopened both complete journals and reused the
corresponding publications. The eight saved-review wire tests passed with portable
fixtures, including substitution of a different critic creator or response digest.
All 2,606 distinct Python tests passed with zero skips. The suite reported 56
Pydantic serializer warnings. Ruff lint, formatting and strict mypy passed across
328 Python files.

With the private registration present, the fixture CLI accepts either selection.
Use fresh journal and publication directories for a new replay.

```powershell
$root = 'data/diagnostics/q008-downstream-2026-11-20'
$source = 'saved-v61-q008-2026-11-20'
$selection = "$root/original_review.json"
$journal = "$root/operator-critique-journal"
uv run --extra api python scripts/saved_review_openai_fixture.py capture --source $source --selection $selection --scenario complete --journal $journal
uv run --extra api python scripts/saved_review_openai_fixture.py publish --source $source --selection $selection --scenario complete --journal $journal --output "$root/operator-critique-publication"
```
