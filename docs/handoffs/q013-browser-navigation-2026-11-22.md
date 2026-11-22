# Q013 saved assessment from artifact navigation

Google Chrome 157.0.8103.79 opened The Impossible Card’s saved Q013 assessment from both exact versions in **Benchmark OH-V01-002 — cloud**. The replay used the built React client, the visible project and artifact buttons, the version selector and **View saved assessment**. All assessment and provenance responses came from real read-only loopback servers. It made zero provider calls. [Browser replay](../../scripts/qualify_q013_browser.py)

## Exact versions

| Artifact in the project | Selected version | Result in Chrome |
| --- | --- | --- |
| **Critique — scene_1** v3 | `ca5915a5-5b82-4bad-82ce-e5c31a519dc0` | Q013 with the original critique receipt |
| **The Impossible Card** (Scene Draft) v1 | `c3689bce-e108-4761-bafe-390f6e7ea1b3` | Same assessment, receipt and original request selection |

Each exact selection displayed one generation record with **62,835 input and 427 output tokens**, including 255 reasoning tokens. Both showed the citation `E0920`, a passing claim-correctness score and a passing evidence-coverage score. The browser compared the assessment and accounting lists across the two versions. These were reads of the original publication. [Saved delivery and independent scoring](q013-api-inspector-qualification-2026-11-22.md)

## Adjacent versions

From critique v3, the browser selected critique v2 (`3128c91a-1b2f-4b57-9c50-f89ddee061c4`). From draft v1, it selected draft v2 (`7cbed44f-b4c3-4736-a912-3ea2fad713f3`). Both are saved versions from the archive. In each case the browser held the outgoing GET long enough to verify that the inspector cleared the previous claim, scores, citations and usage. Both responses returned `exact_selection_unavailable`, empty assessment and accounting lists, and null totals. Switching back recovered the complete original response for that selection.

## Copied workspace

A second read-only server displayed the same project, artifact IDs, versions and content from a byte-identical copy of the database. Clicking **View saved assessment** returned `unregistered_workspace` for both exact versions. Chrome displayed “Assessment unavailable in this workspace.” The screen showed neither the claim nor the generation receipt. The workspace’s display setting selects which reader to call. Each lookup independently verifies the physical database, exact version and publication. [Workspace response](../../apps/api/open_hollywood_api/routes/workspace.py) · [Inspector](../../apps/web/src/components/ArtifactInspector.tsx)

The workspace response supplies the optional `saved_assessment_view` field. If it is absent, the client uses the existing Q008 view. A Q013-only server advertises Q013 even for the copied workspace, so this control exercises the Q013 reader’s own identity check. With both readers installed, the configured Q013 archive path selects the Q013 view. Loading the workspace and opening ordinary provenance leave the saved delivery unopened. [API regression](../../tests/api/test_q013_inspector_api.py) · [Navigation regression](../../apps/web/src/components/ArtifactProvenance.test.tsx)

## Damaged refresh and recovery

In a separate run, the browser opened draft v1 successfully against a disposable copy of the publication. The replay changed the copy’s recorded input-token count from 62,835 to 62,836. **Refresh assessment** cleared the claim and usage while checking, then displayed the verification failure. The API returned `publication_member_changed`. Returning to provenance and reopening the assessment still showed the failure. After restoring the original bytes, refreshing returned a response identical to the initial healthy response, including the original usage. [Browser assertions](../../apps/web/e2e/saved-assessment-navigation.mjs)

## Return to provenance

In the Q013 archive and its copy, **Return to provenance** requested the exact current selection again, removed the assessment and showed the archive’s actual ordinary provenance state, `unregistered_workspace`. This also worked while the publication was damaged.

For a positive control, Chrome opened the registered ordinary workspace and selected **The Bone Labyrinth**, **Critique — s1** v1. The Q013 assessment was unavailable there. **Return to provenance** issued a fresh GET and restored **Version relationship verified**. Its critique version `326c231a-72e8-4576-833b-d3ecece1b500`, draft version `d4b89be6-7b91-46de-9177-efe73a019c32`, source registration and invocation matched the saved relationship. [Ordinary workspace control](../../apps/web/e2e/archive-launcher.mjs)

## Q008 compatibility

The existing Q008 command passed in the same Chrome version. Both exact selections retained their original shared receipt of **58,894 input and 345 output tokens**. The same-text adjacent draft, copied workspace, damaged refresh and return to provenance controls all passed. [Q008 browser qualification](q008-browser-navigation-2026-11-21.md)

The supported Q008 and ordinary operator launcher modes also passed a separate replay. Both exited cleanly, released the listener and removed their temporary snapshots. The ordinary launcher reused the Q008 port. [Launcher replay](../../scripts/qualify_archive_launcher.py)

## Reproduce and inspect

With the private archives, registered ordinary workspace, web dependencies and Google Chrome present, run these commands from the repository root.

```powershell
uv run --extra api python -m scripts.qualify_q013_browser
uv run --extra api python -m scripts.qualify_q008_browser
```

The Q013 report is `data/diagnostics/q013-browser-2026-11-22/verification.json`. Its `archive`, `damaged_refresh` and `ordinary_provenance` sections record the separate runs. The Q008 report is `data/diagnostics/q008-browser-2026-11-21/verification.json`. All 28 files checked for the Q013 and ordinary runs retained their hashes and modification times. All 16 Q008 files checked did likewise.

A portable fixture initially opened its sealed test database through the writable studio connection. SQLite created write-ahead-log sidecars and the assessment reader refused the file. The corrected fixture reads navigation through a separate immutable snapshot, matching the browser. All 18 focused API checks passed, including configurations with both readers installed. The original archive also retained its sidecar-free directory during the browser replay.

The full local suite passed all 2,673 distinct Python tests and all 49 web tests. Ruff, strict mypy across 359 files, frontend lint and formatting, TypeScript checks, and both production builds passed. The Q013 evidence directory contains `suite/result.json`, `snapshot-api-tests.xml` and `web-tests.xml`.

## Next step

Extend the supported read-only launcher with an explicit `--workspace q013` option. Verify that it opens the sealed Q013 archive without the qualification harness, serves both exact selections, releases the loopback port and deletes its temporary snapshot on shutdown. Replay the existing Q008 and ordinary launcher modes. This step needs only local reads of saved deliveries.
