# Q013 observed completion and publication audit

**Both exact selections recover one complete Q013 assessment in the local replay.** Critique v3 owns the observed Sol-high request. Draft v1 reaches the same response through the review’s saved association. Both produced identical evidence and one generation usage record. The operator publisher and artifact inspector currently serve Q008 only. Q013 is ready for a read-only publisher registration. [Observed smoke and scores](q013-sol-high-smoke-results-2026-11-21.md) · [Existing publisher contract](../adr/0067-observed-saved-review-publication.md)

## Completion from each selection

| Selection in *The Impossible Card* | Exact version | Manifest prepared for that selection | Observed delivery |
| --- | --- | --- | --- |
| Critique v3 | `ca5915a5-5b82-4bad-82ce-e5c31a519dc0` | `59ad7cd95b4d22e3541e3d7f190d30c37ea8132b02e4e6c76a7d5dec5fce170f` | Owns the request, response and usage. |
| Draft v1 | `c3689bce-e108-4761-bafe-390f6e7ea1b3` | `47f1bc0e1778e7663c2a6cfcde86e69bc36b28109373a171747ec63067054169` | Reopens the critique’s delivery. Trying to assign it to the draft-selected request fails both binding and accounting with `wrong_request_receipt`. |

For each lookup the verifier checked the role, project, artifact, version and content digest, reconstructed the same work, then bound the authenticated final to the original critique request. Both completed **one batch and one claim** with delivery ID `q013-ee5fe8bc94d4a374ff9594204b425182449edac3698feee431f5ca0809a29cb5`. The full evidence render had SHA-256 `177fc22bb38ca93665e53d9fd375f2b3a7f22f8d981c43dc26b0a401dc46d5ad` from either selection.

The input-count slot measured 62,835 tokens. The generation reported **62,835 input and 427 output tokens**, including **255 reasoning tokens**, with zero cached input tokens. The completion accounts for the generation once. Reopening the draft adds no tokens. Actual billing is unknown.

Sol returned `supported` and cited the complete draft at `E0920`. The separate operator record retains two passes, one for whole-claim correctness and one for the four draft-evidence obligations. Replaying the original scorer rechecked the cited passage against the frozen offsets. The application records delivery and evidence provenance. Its semantic support, evidence adequacy, edit necessity and craft judgments remain `unassessed`.

## Publication and failure controls

| Path exercised locally | Outcome |
| --- | --- |
| Current observed saved-review publisher | The Q008 publisher refused each exact Q013 selection and refused the Q013 journal when supplied explicitly. Rejected exports created no bundle. |
| Saved-review fixture exporter, observed probe/authored publishers and consumer exporter | The public entry points refused the unregistered Q013 source. The fixture reader also requires its own journal format. Both earlier Q013 fixture publications contain an injected `uncertain` response with a different receipt. |
| Current lookup and inspector | The consumer returned unavailable for both Q013 versions with no usage. A mixed lookup returned the registered Q008 assessment once. The inspector returned `unregistered_workspace` for each Q013 selection on its sealed database. |
| Wrong versions and foreign receipts | Genuine adjacent critique v2 and draft v2 failed exact selection. Q008’s genuine receipt failed Q013 result binding and usage accounting. A duplicate Q013 receipt and an altered final were rejected. |
| Missing or damaged delivery | An absent receipt completed zero units. A delivery receipt alone left binding unresolved. Removing closure in a disposable journal read withheld the result. Removing its generation terminal left usage unknown. Changing its response bytes failed the terminal digest check. |
| Copied or injected journal | A byte-identical smoke copy outside the registered location could not establish observed origin. Injected interrupted, missing-usage and invalid-claim controls produced no bound result. A successful injected delivery remained ineligible for observed scoring. |

## Preserved regression

The private archive at `data/diagnostics/q013-observed-completion-audit-2026-11-21/` preserves **29 byte-identical files**. They include the sealed review source and SQLite image, both exact selectors, frozen requests, spent ledger, both intent/outcome pairs, closure, gold, reconstructed audit and separate operator score. The pinned inventory SHA-256 is `20a66691b10bd8462b8cd611782ef5cabe265a8ee079be2c782ffa88ee9d6ff3`. The verifier checks the archive against that pin and the original files before replaying the registered journal. Private prose and provider envelopes remain in the local archive. [Regression verifier](../../scripts/verify_q013_observed_completion.py)

With the private registration present, the following commands reproduce the native completions and exercise the publication controls without provider calls.

```powershell
.venv/Scripts/python.exe -m scripts.verify_q013_observed_completion
.venv/Scripts/python.exe data/diagnostics/q013-observed-completion-audit-2026-11-21/audit_boundaries.py
```

The private outputs are `completion-audit.json` (one delivery and two lookups), `native-evidence.md` (the exact render), `boundary-checks.json` (41 completion and publication checks) and `archive-integrity-checks.json` (two archive damage controls). A second replay reproduced the same 41 outcomes. Altering a disposable copy of the archived score failed the member check. Updating its inventory to match the alteration then failed the pinned manifest check. All 29 original source files retained their hashes and modification times. Both runs were offline.

All **340 focused tests passed** across native assessment work and results, saved-review smoke and completion, observed publishers, consumer lookup, inspector and provenance. Ruff lint, formatting and strict mypy passed across 350 Python files. This audit made zero provider calls. Production prompts are unchanged and the full workflow canary remains on hold.

## Recommended next step

**Add Q013 as a second fixed registration for read-only observed publication.** Use the original critique request and delivery ID as the accounting identity, allow both exact selections as lookups, and carry Q013’s two operator scores with their original labels. Reuse the existing manifest-last bundle writer. Verify critique-first and draft-first creation and byte-identical reuse, one generation usage record, and refusal of adjacent versions, Q008 receipts, injected or damaged journals and altered destinations. Replay Q008’s existing publication as a compatibility control. This step can be completed locally before extending the consumer or inspector.
