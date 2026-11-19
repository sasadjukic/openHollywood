# Saved-review completion adapter — 2026-11-19

The operator can now prepare, audit and publish a completion for the registered
v61 saved-review fixture. Selecting the exact critique or the exact reviewed draft
reproduced the bound result from the preceding qualification, including its citation
to the original draft. This establishes that the application can account for the
assessment input and the authored response for that review.

## What the adapter binds

The first registration, `saved-v61-authored-2026-11-19`, names one closed SQLite
workspace and its previously sealed evidence. It uses the ordinary v61 critic,
graph 9 and native audit schema 7. The source is an authored workspace fixture.
The review representation is the saved normalized critique plus its native audit.
The source receipt records the original raw critic response as unavailable.

| Operation | Evidence and result |
| --- | --- |
| Prepare | Check the registered archive seal and member bytes. Replay saved-review intake on a disposable copy of the database. Verify the project, logical artifact, immutable version, content hash and role for both sides. Recompile the original plan and reproduce the exact intake and offline request. |
| Audit | Match the attempt to the source manifest and request. Check the terminal against the intent, its raw final and the closing record. Run the native assessment binder and whole-work completion check. Preserve the original terminal records beside the derived audit. |
| Publish | Require a bound result for every selected unit. Export the envelope and literal Markdown view outside the source tree. Revalidate source and journal before writes and before writing the manifest. Verify existing exports byte for byte on reuse. |

The registration covers review invocation `4ce742d3-0565-4468-8ed0-0f5e5b8f079c`,
critique version `ed49f50a-5be9-49e6-86c1-fb3dded0d425` and draft version
`95438a97-06fa-45f7-a2f8-ae784779a54d`. The source receipt binds the original
collection, intake, work, declarations, briefs and request. The request SHA-256 is
`00bc1b297163a1086d4306c2b700b3e198c36b117f0a8824be2828dd3bddfd93`.
It retains the five context documents, original messages and all 14 inventoried fields.
The single batch selects Q010. The other 13 fields retain their original dispositions.

## Local results

| Control | Observed outcome |
| --- | --- |
| Exact critique and exact draft selected independently | Both publications reproduced the previously sealed native result. Q010 bound to E0483 at the original draft version. The source receipt records which side the operator selected. |
| Explicit absent-delivery fixture | Audit returned `missing_delivery`, zero completed batches and no receipt. Publication was refused. |
| Intent without a terminal | Audit returned `missing_terminal`, one possibly-sent fixture attempt and no receipt. Publication was refused. |
| Wrong immutable identity | The adapter refused each of the five identity fields changed individually on either side, including a different version with the same content digest. Each refusal preceded output creation. |
| Truncated or structurally invalid final | Audit retained the failed status and raw capture. Publication was refused. |
| Changed source, mismatched intent or closing digest, or claimed provider origin | The adapter refused publication. A source change during finalization left the incomplete destination without a manifest. |
| Repeat and preservation | All six operator exports verified and reused with identical file bytes and modification times. The 33 members of the qualification seal and the production database, WAL and SHM kept their bytes and modification times across replay. |

The bound receipt carries null token observations and one unknown-usage attempt. Its
zero synthetic elapsed time is a fixture value. The result's support, evidence
adequacy, edit necessity and craft remain unassessed. It supplies no model observation
or permission to attach an assessment or dispatch a writer. Six historical v33
reviews retain their existing assessment eligibility.

Thirteen new adapter regressions exercise the operator interface using independently
created portable workspaces. The focused adapter, qualification and completion suites
passed 113 tests. All **2,593** collected Python tests also passed across six isolated
pytest groups. The per-test reports account for every test once, with zero skips.
Ruff, formatting and strict mypy passed across 323 repository Python files.
The preservation check also verified 3,620 members of 30 earlier seals and 1,788
source files against their saved hashes and modification times.

## Reproduction

Use the [operator commands](../../README.md) with the private qualification archive
present. The code-owned registration has no command-line override for the source
path or trust digest. Each mode takes its own output directory. `--journal` selects
an explicit fixture scenario. A damaged complete journal fails integrity checks.
An incomplete output directory remains available for inspection and a fresh export
can be written to a new destination.

The verified replay is under
`data/diagnostics/assessment-saved-review-adapter-2026-11-19/verified/`.
`verification.json` in its parent records manifest hashes and outcomes. Inspect
`published-review/source-receipt.json`, `audit.json` and `view.md` for the positive
case, and `no-delivery/audit.json` and `intent-only/audit.json` for the controls.
The earlier trial exports sit outside `verified/`.
The tracked regression suite builds its own fixtures on a fresh checkout. Run it
from the repository root with
`uv run --extra api pytest tests/api/test_saved_review_completion.py`.
Replaying the specific registered capture also requires the private archive.
[Adapter](../../apps/api/open_hollywood_api/services/saved_review_completion.py) ·
[CLI](../../scripts/saved_review_completion.py) ·
[Regression suite](../../tests/api/test_saved_review_completion.py) ·
[Decision](../adr/0065-read-only-saved-review-completion-adapter.md)

## Recommended next step

Qualify the saved-review source receipt through a compact OpenAI request and terminal
journal **locally**, using the same one-work fixture and injected responses. Verify
that the model-visible input retains the story, full review context, active claim and
evidence references, while archive paths and operator receipts stay in the application.
Bind both the count and generation inputs to the same selected version. Exercise one
complete response, one missing terminal and one wrong-version request. The acceptance
test is exact source-to-response traceability with publication allowed only for the
complete matching fixture.

For a later live test of reviewer accuracy, first admit a supported saved review with
a substantive claim, sufficient source evidence and a defensible expected judgment.
Q010 is an authored structural placeholder. Step 19 remains in progress, production
prompts are unchanged, live calls are paused and the full workflow canary is on hold.
