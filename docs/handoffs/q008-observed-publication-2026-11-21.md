# Q008 read-only publication

An operator can now open the saved Sol-high assessment from either the exact critique or the exact draft. Both lookup orders published the same 15 files and reused them without changing a byte or a modification time. The critique owns the observed request. The draft opens that assessment through its recorded association. [Publisher](../../scripts/publish_q008_completion.py) · [Operator commands](../../README.md) · [Decision](../adr/0067-observed-saved-review-publication.md)

## Qualification on the registered delivery

| First selection | Second selection at the same destination | Outcome |
| --- | --- | --- |
| Critique `2268e6e8-b82b-4cca-932f-55cc418a58b5` | Draft `b74efc96-dbe6-4147-8dd3-a1c24f295321` | Created, then reused |
| Draft `b74efc96-dbe6-4147-8dd3-a1c24f295321` | Critique `2268e6e8-b82b-4cca-932f-55cc418a58b5` | Created, then reused |

Both independently created manifests had SHA-256 `efef8fc3348b3a5cfc3c9529e6e645d390685e5030c01d56b257eaa27631619d`. They identify one delivery, `q008-c8aa452c352b8879f4d6abc1c17c56e1f6c5476613cfeb7c89792ab949988e92`, bound to the critique-selected request manifest `0aa8d63ce59895017f07750146b267997c85e2f54777f5d0e916e18954549b93`. The five-part identity check covers role, project, artifact, version and content digest.

`delivery.json` records a preliminary count of **58,894** and one generation usage record with **58,894 input**, **345 output**, **165 reasoning** and **0 cached input** tokens. The input count is a preflight measurement. Reasoning tokens are included in the output total. Actual billed cost remains unknown. The bundle retains the original HTTP envelopes, both request bodies and the source receipt for inspection.

`evidence.md` reproduced the native regression render byte-for-byte. The separate `operator-score.json` reproduced the original **3/3** adjudication for whole-claim support, plan evidence and draft-ending evidence. Application support, evidence adequacy, edit necessity and craft stay unassessed. This publication adds zero model calls and measures one previously scored claim. [Original scoring](q008-sol-high-smoke-results-2026-11-20.md) · [Preserved regression](q008-observed-completion-audit-2026-11-20.md)

## Refusals and replay

The registered replay checked both exact selections against a stale version with the original content digest and against their matching injected fixture journals. All four attempts were refused before output creation. The 28 original files checked across the sealed workspace, smoke, selectors, gold and operator score retained their hashes and modification times.

The portable tests exercise the same publisher with disposable sources. They cover changes to all five selector fields, a draft-selected request substituted into the critique journal, injected journal formats, missing closure or generation outcome, missing usage in a correctly reclosed journal, changed terminal bytes, and altered scoring evidence. An existing altered bundle is preserved and refused. Source drift during writing leaves a partial directory without the final manifest. [Publisher regression tests](../../tests/api/test_q008_publisher.py)

All 2,624 distinct Python tests passed, including the 11 publisher regressions, with zero skips. Ruff lint, formatting and strict mypy passed across 333 Python files. The workspace passed frontend formatting, lint, type checking, all 34 web tests and the production build.

The private qualification lives under `data/diagnostics/q008-publication-2026-11-21/`. Open `critique-first/manifest.json` or `draft-first/manifest.json` to inspect the member hashes. `qualification.json` records both orders and the four refusals. The operator command requires the private registration, original closed journal and registered score in this checkout. The publication provides local inspection only. Step 19 remains in progress and the canary is on hold.

## Recommended next step

Rehearse the **read-only consumer** against this one pinned publication. Open it from both exact selections in one consumer inventory and verify one displayed assessment, one usage total and correct attribution of the operator score. Include an adjacent draft version and a changed or incomplete publication as unavailable controls. This can be done locally before exposing a result in the artifact inspector. Broader accuracy and story-quality decisions still need evidence from other reviews.
