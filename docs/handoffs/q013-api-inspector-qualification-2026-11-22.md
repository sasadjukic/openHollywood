# Q013 through the read-only API and artifact inspector

The Impossible Card’s critique v3 and reviewed draft v1 open the same saved Q013 assessment. The original critique owns the Sol-high request. Opening either version displays one generation record with 62,835 input and 427 output tokens, including 255 reasoning tokens. The preflight count was 62,835. The billed cost is unknown. The saved model judgment was `supported`, with citation `E0920`. The operator scored claim correctness and evidence coverage separately, and both passed. These are scores on this factual claim. Story craft and edit necessity remain unassessed. [Original publication](q013-observed-publication-2026-11-22.md)

## Exact versions and workspace identity

| Selection in the registered database | Version ID | API result |
| --- | --- | --- |
| Critique v3 | `ca5915a5-5b82-4bad-82ce-e5c31a519dc0` | One Q013 delivery |
| Reviewed draft v1 | `c3689bce-e108-4761-bafe-390f6e7ea1b3` | Same delivery and usage |
| Critique v2 | `3128c91a-1b2f-4b57-9c50-f89ddee061c4` | `exact_selection_unavailable` |
| Draft v2 | `7cbed44f-b4c3-4736-a912-3ea2fad713f3` | `exact_selection_unavailable` |

The GET checks the configured database path and physical file identity, rejects SQLite sidecars and verifies the sealed bytes. It reads the authenticated image in a private immutable SQLite snapshot. It checks the project, artifact, role, version and content digest before reading the publication, then checks the workspace stamp again before returning. A separate database with identical bytes and IDs returned `unregistered_workspace` for both exact selections. Unavailable responses contained an empty assessment list, an empty accounting list and null totals. [Workspace verifier](../../apps/api/open_hollywood_api/services/assessment_inspector_workspace.py) · [Q013 adapter](../../apps/api/open_hollywood_api/services/q013_inspector.py)

The endpoint returns `Cache-Control: no-store`. Its response exposes just the two operator score labels. The detailed gold, operator witnesses, frozen request hash and provider envelopes stay in the local archive. A portable fixture with a passing claim and failing evidence score verifies that the two labels can differ. The standard application returned the assessment only with its reader explicitly configured and released that reader’s inspector service on shutdown. The isolated qualification server exposed one assessment GET. [API regressions](../../tests/api/test_q013_inspector_api.py)

## Stale assessment and usage

- **Version switch.** With draft v1 displayed, the inspector started a refresh and cleared the previous claim, citations, scores, delivery ID and usage. The test held a successful HTTP response for v1, selected the genuine draft v2 and waited for its unavailable result. Releasing the older success left v2 unavailable.
- **Damaged refresh.** The test changed the recorded input-token count in a disposable copy of a previously verified publication. The inspector hid the prior results as soon as refresh began. The API returned `publication_member_changed`, and the panel kept the claim and usage clear. Restoring the exact bytes and refreshing recovered the original record.
- **Copied workspace.** The inspector displayed “Assessment unavailable in this workspace” for each exact selection through a second HTTP server bound to the copy. Neither selection displayed the registered workspace’s usage.

The qualification uses the generated TypeScript client and the mounted React artifact inspector in a DOM test environment. The loopback adapters read the registered database and a separate physical copy. The saved publication supplies the reference response. The mounted damage test uses its own publication copy. [Inspector regressions](../../apps/web/src/components/Q013Assessment.test.tsx) · [Archive replay](../../scripts/qualify_q013_inspector.py)

## Reproduce locally

With the captured archives and web dependencies present, run these from the repository root.

```powershell
uv run --extra api python -m scripts.qualify_q013_inspector
uv run --extra api python -m scripts.qualify_q008_inspector_api
```

The Q013 report and mounted-test results are under `data/diagnostics/q013-inspector-api-2026-11-22/` in `verification.json` and `inspector.xml`. The Q008 replay uses its existing report directory. Both commands use local data and loopback HTTP.

All four Q013 mounted checks and all eleven Q008 compatibility checks passed. Q008 retained its original score display, delivery and usage of 58,894 input and 345 output tokens. All 26 Q013 source and publication files and all 16 Q008 files checked retained their digests and modification times. All nine focused API tests passed. Comparison of the generated OpenAPI contract with the preceding revision found all existing paths and schemas identical. The sole new path is the Q013 assessment GET. Verification used zero provider calls.

The full local run passed all 2,673 distinct Python tests and all 48 web tests. Ruff, strict mypy across 358 files, web lint, formatting, TypeScript checks and the web and contracts production builds passed. The local evidence directory includes `suite/result.json`, `api-tests.xml` and `web-tests.xml`.

## Next step

Qualify the operator’s **View saved assessment** action in a real browser for Q013. Start from artifact navigation, open both exact versions, select an adjacent version, refresh after damage to a disposable publication, and return to verified provenance. Include the identical-ID workspace and a Q008 navigation replay. Passing that check would justify extending the supported archive launcher to Q013. This work requires zero inference calls.
