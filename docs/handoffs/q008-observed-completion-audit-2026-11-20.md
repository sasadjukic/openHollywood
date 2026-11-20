# Q008 observed delivery through the critique and draft selections

The local replay recovered **one complete factual assessment** from either exact artifact selection. The original critique owns the observed OpenAI request. The reviewed draft can lead an operator to the same delivery through its recorded association with that critique. Both selections rendered identical evidence. The existing saved-review exporters have no publication contract for this observed journal. [Original smoke and scoring](q008-sol-high-smoke-results-2026-11-20.md)

## Which request was observed

| Selected artifact | Exact version | Request manifest SHA-256 for that selection | Audit outcome |
| --- | --- | --- | --- |
| Original critique | `2268e6e8-b82b-4cca-932f-55cc418a58b5` | `0aa8d63ce59895017f07750146b267997c85e2f54777f5d0e916e18954549b93` | The closed journal binds Q008 to this request. |
| Reviewed draft | `b74efc96-dbe6-4147-8dd3-a1c24f295321` | `ab5816798cbe453ca1a4c4508e8950d6a9d159bfe61e4039495cc979961cf564` | This request was prepared locally. Rebinding or completing it with the observed receipt raises `wrong_request_receipt`. |

Each lookup verified the project, role, artifact ID, version and content digest. Both reconstructed the same source pair and entire assessment work. Replaying the **original** receipt against that work completed one batch and one claim. The engine rendered the full work, original model response and verified citation locations from either selection. Both renders had SHA-256 `512879e518d405e71a28b854c159ea89c3b26f157cc07262f637299855b51a7b`. The single generation accounts for 58,894 input and 345 output tokens, including 165 reasoning tokens. [Qualification of both selections](assessment-saved-review-q008-qualification-2026-11-20.md)

The model returned `supported`. The separate operator score remains **3/3** for the whole Q008 explanation, plan evidence (`E0233`), and draft-ending evidence (`E0883`, with the ending located). The application establishes where the evidence came from and that the delivery is complete. Its semantic support, evidence adequacy, edit necessity and craft fields remain `unassessed`. Opening the draft adds neither a score nor a second assessment.

## Publication boundaries exercised

| Local path or control | Result |
| --- | --- |
| Matching saved-review **injected** journal, both selections | The fixture exporter created and reused a bundle per selection. Each described an injected `uncertain` result, with model-evidence, production-attachment and writer permissions false. |
| **Observed** smoke journal supplied to the fixture exporter | Both selections stopped before publication. The fixture reader looks for `journal.json` and raises `KeyError`. The observed journal uses `header.json` and a separate single-use ledger. Its origin and closure are checked by the smoke auditor. |
| Saved-review completion publisher, observed probe and authored publishers, consumer exporter | Each rejected the Q008 source registration. The artifact inspector returned `unavailable / unregistered_workspace` for both exact selections on the captured diagnostic database. |
| Wrong version with original content digest, opposite-selection fixture journal, interrupted fixture journal | Both selections rejected all three substitutions. The rejected publication attempts produced no output directory. |
| Missing receipt, delivery receipt before binding, duplicate receipt, altered raw final | The first gave 0/1 delivered. The second gave 1/1 delivered with binding unresolved. A duplicate receipt and a changed final both failed validation. |
| Copied observed journal and injected smoke controls | A byte-exact copy outside the registered smoke location failed outcome binding. An interrupted generation, missing usage and invalid claim produced no bound result. A successful injected smoke bound structurally and remained ineligible for observed scoring. |

## Preserved regression and local replay

The private archive is `data/diagnostics/q008-observed-completion-audit-2026-11-20/`. Its 29 byte-identical members include the sealed review source and database snapshot, frozen requests, spent ledger, both endpoint intents and outcomes, closure, both selectors, original audit, independent gold and operator score. The archive inventory SHA-256 is `d8b133364673b9f455463ebc4636be1313d8638b60663cca838d11dd9a58fe48`. Full prose and provider envelopes stay in the ignored diagnostic directory. Observed-origin replay also requires the registered original journal and the implementation pinned by its approval plan.

From the project root, with the private evidence present, run the following local checks. The first reauthenticates the registered original, checks the pinned archive, and compares both native completions and evidence renders. The second also exercises the publisher refusals and injected controls with outbound connections disabled.

```powershell
.venv/Scripts/python.exe -m scripts.verify_q008_observed_completion
.venv/Scripts/python.exe data/diagnostics/q008-observed-completion-audit-2026-11-20/audit_boundaries.py
```

`completion-audit.json` contains one attempt and two selection records. `native-evidence.md` is its private evidence render. `boundary-checks.json` records the publication and failure controls. The separately pinned `capture/operator/score.json` preserves the adjudication. [Versioned regression verifier](../../scripts/verify_q008_observed_completion.py)

Both runs of the 27 boundary checks produced identical results. The original scoring replay independently rechecked both endpoint chains and both cited witnesses. All 29 source files retained their original digests and modification times. The focused suites passed **304 tests** across the smoke, saved-review and publisher paths, inspector, consumer, and native assessment work and results. Ruff lint, formatting and strict mypy passed across 331 Python files. This audit made zero provider calls.

## Recommended next step

Implement a **read-only publisher for this one registered observed saved review**. Have it rebuild the source and original request, authenticate both terminal slots and closure, check accounting and bind the complete work. Its bundle should name the critique selected for the request and the two exact artifact versions permitted to look up that delivery. Give both lookups one stable delivery identity and one usage record. Keep the operator score separately attributed.

Qualify first publication and byte-identical reuse through each lookup, including creating from the critique and reopening from the draft and the reverse order. Return an explicit unsupported-journal result for a fixture submitted to the observed publisher. Require refusal on stale versions, the unsent draft manifest, missing usage or closure, and an altered existing bundle. This step needs zero inference. Production attachment, reviewer routing and story-quality evaluation remain separate decisions. Step 19 remains in progress and the workflow canary is on hold.
