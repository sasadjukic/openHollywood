# Open The Impossible Card in the read-only archive viewer

From the repository root, build the web client with `pnpm build` after installing dependencies or updating the client. Start the viewer with the following command, then open the loopback URL it prints.

```powershell
uv run --extra api python -m scripts.open_archive --workspace q013
```

## Critique v3 and draft v1

Open **Benchmark OH-V01-002 — cloud**, choose either selection below and click **View saved assessment**. The browser replay used these same controls on the built client served by the operator command.

| Artifact | Selected version | Version ID |
| --- | --- | --- |
| **Critique — scene_1** | v3 | `ca5915a5-5b82-4bad-82ce-e5c31a519dc0` |
| **The Impossible Card** (Scene Draft) | v1 | `c3689bce-e108-4761-bafe-390f6e7ea1b3` |

Chrome showed one saved Sol assessment of the critic’s explanation of the date on the card. Both selections returned `supported`, cited the original draft at `E0920` and displayed separate passing scores for claim correctness and evidence coverage. The critique owns the single receipt for **62,835 input tokens and 427 output tokens**, including 255 reasoning tokens. Opening the draft reproduced the complete assessment and accounting record. [Original claim and independent evidence scores](q013-sol-high-smoke-results-2026-11-21.md)

## Clean shutdown

Press **Enter** in the terminal to close the viewer. After the browser checks, all three launcher processes printed `Archive viewer closed.` and exited with code 0 on Enter. [Subprocess qualification](../../scripts/qualify_archive_launcher.py)

A separate foreground Windows check sent **Ctrl+C** to Q013. PowerShell reported the interruption as status 1. An observer waiting on the launcher process itself recorded exit code **0**, an empty snapshot directory and successful rebinding to the same port. The child receipt is `foreground-shutdown.json` in the evidence directory.

## Snapshot cleanup

For Q013 and Q008 the launcher verifies the original database’s registered physical identity and digest, then writes a separate navigation snapshot. SQLite opens that snapshot in immutable, read-only mode. The registered original remains the authority for assessment lookup. The two archive snapshots matched their pinned SHA-256 digests. The ordinary workspace uses SQLite backup so navigation includes committed write-ahead-log rows. All three private temporary directories were empty after shutdown. All 44 checked source and publication files retained their hashes and modification times. [Launcher](../../scripts/open_archive.py) · [Snapshot regressions](../../tests/api/test_archive_launcher.py)

## Port reuse

The operating system assigned port **63599** to Q013. Q008 and then the ordinary launcher each served Chrome on **127.0.0.1:63599**. A new listener also bound successfully to the port immediately after each of the three exits.

## Q008 and ordinary compatibility

The default command opens Q008. In Chrome **157.0.8103.79**, its critique v2 and *The Pristine Lure* draft v1 shared one original receipt for **58,894 input and 345 output tokens**. In ordinary mode, *The Bone Labyrinth*, **Critique — s1** v1, returned `unregistered_workspace` for assessment with empty accounting. **Return to provenance** then restored `exact_registered_identity` for the original critique and draft. All three modes exposed only GET operations in their API schemas and rejected a project creation request with HTTP 405. The replay made zero provider calls. [Browser assertions](../../apps/web/e2e/archive-launcher.mjs)

## Reproduce the verification

Run the following command with the three registered local workspaces, built web client and Chrome available. It writes the per-mode evidence to `data/diagnostics/q013-archive-launcher-2026-11-22/verification.json`.

```powershell
uv run --extra api python -m scripts.qualify_archive_launcher
```

All **2,674 distinct Python tests** passed. The three portable launcher tests cover rejection of a physically replaced database with identical bytes for each sealed archive and preservation of committed rows in the ordinary workspace’s write-ahead log. The evidence directory contains the full test count in `suite/result.json` and the focused results in `launcher-tests.xml`.

All **49 web tests** passed on a single-worker run with their standard timeouts. An earlier parallel run timed out in the empty-library creation test. Both JUnit reports are retained. Ruff lint and formatting, strict mypy across 359 files, client lint and formatting, web and contracts type checks, and both production builds passed.

## Proposed next step

Both published assessments cover supported factual claims. Audit two as-yet-unscored statements from the same saved critiques locally. In *The Pristine Lure*, check the critic’s claim about Elias entering the threshold against the draft’s final action. In *The Impossible Card*, check the critic’s inference about Elara’s continuing resolve to disprove the card against the ending and the plan. Preserve each complete review field and its exact sources. Freeze an independent judgment and evidence requirements for any factual claim that qualifies before opening any assessor output. If a statement is editorial or the evidence cannot settle it, record that limit. This would identify which observations a future revision decision could rely on. Whether changing either ending improves the story remains a reader judgment. [Q008 ending observations](ordinary-v61-single-capture-results-2026-11-20.md) · [Q013 ending observations](second-family-ordinary-v61-capture-results-2026-11-21.md)
