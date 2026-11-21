# Q008 saved assessment from artifact navigation

Google Chrome 157.0.8103.79 opened the same saved Q008 assessment from critique v2 and its reviewed draft v1 through the regular story library, artifact list and version selector. The operator chooses **View saved assessment** in the inspector toolbar. The default view is ordinary provenance. The artifact list now shows type alongside title so the scene plan and draft both named *The Pristine Lure* are distinguishable. [Artifact navigation](../../apps/web/src/App.tsx) · [Inspector](../../apps/web/src/components/ArtifactInspector.tsx)

## Both exact versions

In the registered workspace, the browser opened the saved critique `2268e6e8-b82b-4cca-932f-55cc418a58b5` and draft `b74efc96-dbe6-4147-8dd3-a1c24f295321`. Both selections displayed the same claim and one generation receipt. The original request was attributed to critique v2 on both screens. The receipt records **58,894 input and 345 output tokens**, with 165 reasoning tokens included in output and zero cached input. Opening or refreshing the view only reads this historical delivery. [Saved assessment and accounting](q008-read-only-api-qualification-2026-11-21.md)

## Switching to the adjacent version

With the assessment open on draft v1, the browser selected draft v2, `c176b3ef-6868-5f0f-822c-2b2da9390ff2`, in the version selector. This test-only successor has the same prose and digest as v1. The checking state cleared the previous claim, judgment and receipt. The API returned `exact_selection_unavailable`, and the inspector displayed “Assessment unavailable for this version.” Switching back to v1 recovered the original receipt.

## Unregistered workspace

A second local server used a byte-for-byte copy of the registered database with a different physical file identity. Both exact version selections returned `unregistered_workspace`. Chrome displayed “Assessment unavailable in this workspace.” The API returned empty assessment and accounting lists and null totals for both.

## Refresh after damage

While the successful draft v1 view was open, the replay changed the stored input usage from 58,894 to 58,895 in a disposable publication. **Refresh assessment** cleared the old claim and usage while checking. The real API then returned `publication_member_changed`. The inspector showed that the publication could not be verified. For this check and the adjacent-version switch, Playwright held the outgoing GET long enough to inspect the pending screen, then released it to the application server.

## Return to provenance

The operator returned to provenance four times, covering both exact selections in both workspaces. Each return issued a fresh GET for the current selection, removed the assessment and receipt, and displayed ordinary review provenance. The Q008 archive has a saved-assessment registration only. Its ordinary provenance response correctly says that the workspace has no registered provenance source. A portable regression also exercises the positive ordinary-provenance case and confirms that a late assessment response cannot replace it after the operator returns. [Provenance regression](../../apps/web/src/components/ArtifactProvenance.test.tsx)

## Replay and scope

Run this command from the project root with the private Q008 archive, installed web dependencies and Google Chrome available.

```powershell
uv run --extra api python -m scripts.qualify_q008_browser
```

The replay builds the ordinary web application and serves it on two temporary loopback origins. Project, artifact and version navigation read an immutable snapshot containing the synthetic successor. Each server independently binds its assessment and ordinary provenance readers to the configured workspace. The rehearsal exposes GET routes only. The browser uses a fresh context per workspace, clicks the visible controls and checks the response selection, cache policy, rendered states and delivery identity. The seven assessment GETs made zero provider calls. All 15 original publication files and the sealed database retained their hashes and modification times, and the sealed database directory remained free of SQLite sidecars. The result file is `data/diagnostics/q008-browser-2026-11-21/verification.json`. [Local server and source checks](../../scripts/qualify_q008_browser.py) · [Playwright replay](../../apps/web/e2e/q008-navigation.mjs)

The full Python suite passed all 2,642 tests, and the standard web suite passed all 44 tests at its normal timeouts. An initial concurrent run timed out in the existing story-creation test. The full web rerun passed after the other frontend jobs finished. All 11 checks in the previous HTTP inspector replay also passed. Lint, formatting, strict type checks and the production build passed.

## Next step

Provide a supported read-only operator launch command for the registered archive. It should open the actual saved workspace through artifact navigation, use the existing assessment reader, and shut down cleanly. Reserve the synthetic successor and damaged publication for the regression replay. Include an ordinary workspace with a verified provenance relationship as a browser control, so operators can see the correct relationship restored after an unavailable assessment lookup.
