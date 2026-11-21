# Opening the saved archive in the read-only viewer

## Open the actual Q008 archive

From the repository root, run `pnpm build` once with the web dependencies installed. Rebuild after changing the web client. Then start the viewer and open the loopback URL it prints.

```powershell
uv run --extra api python -m scripts.open_archive
```

In **Benchmark OH-V01-001 — cloud**, open **Critique — scene_1** v2 or **The Pristine Lure** (Scene Draft) v1, then select **View saved assessment**. Chrome opened both exact versions from the registered sealed archive. The actual draft has one saved version. Both selections displayed the same assessment and one generation receipt for 58,894 input and 345 output tokens. The original request remains bound to the critique even when opened from the draft.

| Selection | Exact version |
| --- | --- |
| Q008 critique v2 | `2268e6e8-b82b-4cca-932f-55cc418a58b5` |
| Q008 draft v1 | `b74efc96-dbe6-4147-8dd3-a1c24f295321` |

The launcher checks the sealed file's registered identity and contents before copying it into a private, immutable SQLite navigation snapshot. The ordinary workspace uses SQLite's backup API to include committed rows still in its write-ahead log. Navigation reflects launch time. Each assessment or provenance lookup checks the original source registration for its exact selection. The viewer serves the built client and its GET-only API on one loopback origin. [Launcher](../../scripts/open_archive.py) · [Read-only API](../../apps/api/open_hollywood_api/readonly_workspace.py)

## Return to verified provenance in an ordinary workspace

```powershell
uv run --extra api python -m scripts.open_archive --workspace ordinary
```

In **The Bone Labyrinth**, select **Critique — s1** v1. Chrome showed **Version relationship verified**. Choosing **View saved assessment** returned `unregistered_workspace` and displayed **Assessment unavailable in this workspace.** The response contained zero assessments, zero accounting records and no usage total.

Choosing **Return to provenance** issued a fresh GET for that same selection. The API returned `identity_verified` with reason `exact_registered_identity`. Chrome again displayed **Version relationship verified**, critique version `326c231a-72e8-4576-833b-d3ecece1b500` and draft version `d4b89be6-7b91-46de-9177-efe73a019c32`. The source registration and invocation matched the saved relationship. The assessment and usage cleared. This verifies the review-to-draft relationship. Assessment eligibility is a separate check. [Browser assertions](../../apps/web/e2e/archive-launcher.mjs)

## Clean shutdown

Press **Enter** or **Ctrl+C** in the launcher terminal. In the browser replay, each launcher exited with code 0 on Enter, released its listener and removed its private snapshot directory. The ordinary launcher reused the archive launcher's port. A separate foreground Windows Ctrl+C check also observed the launcher exit with code 0. The sealed archive acquired no SQLite sidecars. Hashes and modification times matched before and after for all 18 checked files, including the Q008 archive, its 15 publication files and the ordinary database and write-ahead log.

## Repeat the verification

With both registered workspaces, the Q008 publication, Google Chrome and the built web client available locally, run the following command from the repository root.

```powershell
uv run --extra api python -m scripts.qualify_archive_launcher
```

The replay starts the supported operator process for each workspace, checks that the API refuses project creation, and exercises artifact navigation in Chrome. The recorded browser traffic used only local GETs. Private results are saved to `data/diagnostics/archive-launcher-2026-11-21/verification.json`. Two portable regressions also cover a byte-identical replacement of the sealed database and a committed ordinary-workspace row still in the write-ahead log. [Replay](../../scripts/qualify_archive_launcher.py) · [Snapshot regressions](../../tests/api/test_archive_launcher.py)

Chrome 157.0.8103.79 passed both launcher scenarios. The earlier browser replay also passed the adjacent-version, copied-workspace and damaged-publication controls, and all 11 HTTP inspector checks passed with the shared server code. The full suites passed 2,644 Python tests and 44 web tests. Lint, formatting, strict type checks and the production build passed. This qualification used zero provider calls.

## Next step

Check newly saved ordinary v61 reviews from a second scene family for one substantive factual claim with complete evidence. Freeze the whole-claim judgment and exact source versions before viewing an assessor delivery. A second eligible review would let us test that each review opens its own assessment and usage receipt. If no new review qualifies, record the gap and propose one isolated critic capture for approval. The verified ordinary relationship above remains an identity control. The full story workflow canary remains on hold.
