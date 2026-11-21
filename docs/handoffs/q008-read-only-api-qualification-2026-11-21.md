# Q008 read-only API qualification

The local artifact inspector retrieved one saved Sol assessment through the generated API client. Opening the critique and its reviewed draft produced the same delivery ID and the same generation receipt. A byte-identical database copy returned no assessment. Altering a previously valid publication cleared the open inspector on refresh. This qualification used the saved Q008 observation and made zero provider calls.

## Exact-version binding

| Selection in the registered workspace | Version ID | Result |
| --- | --- | --- |
| Captured critique v2 | `2268e6e8-b82b-4cca-932f-55cc418a58b5` | One assessment and one generation receipt |
| Reviewed draft v1 | `b74efc96-dbe6-4147-8dd3-a1c24f295321` | The same assessment and receipt, attributed to critique v2 |
| Same-text successor from the adjacent-version fixture | `c176b3ef-6868-5f0f-822c-2b2da9390ff2` | Unavailable for that version |

`GET /api/v1/artifact-versions/{artifact_version_id}/q008-assessment` takes the project, artifact, role and content digest alongside the version ID. The server gets the database path from its application configuration. It verifies the registered file identity and SHA-256, checks the exact selection against the sealed registration and SQLite rows, and recomputes the digest from the application’s version detail. SQLite reads a private copy of the authenticated bytes. Each successful or unavailable lookup sends `Cache-Control: no-store`. The generated client passes the selected version and cancels a superseded request. [Route](../../apps/api/open_hollywood_api/routes/q008_inspector.py) · [Adapter](../../apps/api/open_hollywood_api/services/q008_inspector.py) · [Client](../../apps/web/src/api.ts)

Both exact versions showed **58,894 input and 345 output tokens**, including 165 reasoning tokens and zero cached input. Reopening through the draft adds no generation. The preflight count of 58,894 is separate and actual billed cost is unknown. The saved model judgment was `supported` with citations `E0233` and `E0883`. The operator score was 3/3. The API exposes that score and the attributed judgment. The operator’s detailed gold stays in the private publication. Application-level support, evidence adequacy, edit necessity and craft are unassessed. [Original smoke result](q008-sol-high-smoke-results-2026-11-20.md)

## Rejection of an identical-ID copy

The replay served two loopback API instances. One used the registered database. The other used a disposable copy verified to have identical bytes and a different physical file identity. Both clients requested the original five selection fields. The copy returned `unregistered_workspace` for the critique and draft, empty assessment and accounting lists, and null totals. The inspector showed “Assessment unavailable in this workspace.” Portable API tests also replaced the file at its registered path with a byte-identical copy, altered its contents, removed it and supplied a WAL sidecar. In each case the adapter refused the request before calling the publication reader. Replacing or restoring the sealed workspace therefore requires explicit requalification of its local registration. [API controls](../../tests/api/test_q008_inspector_api.py)

## Refresh after damage

With the saved assessment visible for draft v1, the replay changed the input usage in a disposable copy of `delivery.json` from 58,894 to 58,895. Clicking **Refresh assessment** cleared the claim, judgment, score, receipt and usage during the new read. The inspector then showed that the publication could not be verified. Independent HTTP reads for both versions returned `publication_member_changed`, empty assessment and accounting lists, and null totals. The original database and all 15 original publication files retained their digests and modification times. The sealed database directory remained free of SQLite sidecar files. [Inspector regression](../../apps/web/src/components/Q008Assessment.test.tsx)

## Local replay

Run from the repository root with its Python and web dependencies and the private Q008 registration and publication present.

```powershell
uv run --extra api python -m scripts.qualify_q008_inspector_api
```

The replay starts two temporary servers using the application's read-only factory. Its API schema contains one GET operation. The React inspector runs under Vitest/jsdom and uses the generated HTTP client. The local browser origin is checked on the HTTP responses. The standard app factory also accepts an operator-supplied reader when it owns the configured workspace. The ordinary inspector continues to open its provenance panel by default. Results are written under `data/diagnostics/q008-api-2026-11-21/` as `verification.json` and `inspector.xml`. [Application factories](../../apps/api/open_hollywood_api/app.py) · [Replay command](../../scripts/qualify_q008_inspector_api.py)

The saved HTTP inspector replay passed all 11 checks. The previous direct-reader replay passed all 10, and the standard web suite passed all 43. The full Python suite passed all 2,642 tests. A focused rerun covered the seven API adapter cases and the exported OpenAPI consistency check. Python and TypeScript lint, formatting, type checks and the web production build passed.

## Next step

Qualify an explicit **View saved assessment** action from ordinary artifact and version navigation in a real browser. Exercise both exact selections, the adjacent version and an unregistered workspace. Confirm that the operator can return to ordinary provenance and that version changes or a damaged refresh clear any visible assessment and receipt. Use a read-only workspace view for this rehearsal so normal project writes cannot reach the sealed database. This step needs no new model output.
