# Q008 artifact inspector qualification

The isolated React artifact inspector opened the saved Q008 assessment from both the exact critique and the exact reviewed draft. Each selection showed the same generation receipt and attributed the original request to the critique. The existing application inspector continues to use its registered review-provenance panel. The Q008 panel was mounted through the inspector’s review-panel prop during local qualification. [Inspector](../../apps/web/src/components/ArtifactInspector.tsx) · [Q008 panel](../../apps/web/src/components/Q008Assessment.tsx)

## Shared usage

The normal workspace project and version readers resolved all three selections in a disposable copy of the sealed workspace. The qualification checked project membership, artifact and version IDs, role, lineage and a content digest recomputed from the returned detail. The fixture successor has the original draft as its parent and the same prose and digest.

| Selected artifact | Exact version | Inspector result |
| --- | --- | --- |
| Captured critique v2 | `2268e6e8-b82b-4cca-932f-55cc418a58b5` | Q008 and its original generation receipt |
| Reviewed draft v1 | `b74efc96-dbe6-4147-8dd3-a1c24f295321` | The same Q008 assessment and receipt |
| Fixture draft v2 | `c176b3ef-6868-5f0f-822c-2b2da9390ff2` | Assessment unavailable for this version |

Opening the two exact versions in either order and reopening the first displayed **58,894 input and 345 output tokens** once. The 165 reasoning tokens are included in output, and cached input was zero. The panel shows the preliminary count of 58,894 separately and reports billed cost as unknown. The saved Sol judgment was `supported`, with citations `E0233` and `E0883`. The **3/3** was the operator’s score against frozen gold. Application-level support, evidence adequacy, edit necessity and craft are unassessed. [Consumer contract](q008-consumer-lookup-2026-11-21.md)

## Switching versions mid-lookup

With the draft assessment visible, the test started a refresh, held the response and used the inspector’s version selector to switch to the same-text successor. The claim, model judgment, citations, operator score, receipt and usage disappeared during refresh. The old request received an abort signal. After the successor showed unavailable, the test released the old success anyway. The successor stayed unavailable. A separate control supplied detail for the previous version while the successor was selected. The inspector hid the assessment panel until detail matched the selection.

## Refreshing after damage

On a disposable publication, the inspector opened the critique, then the draft, through the Python lookup. While the successful draft view was open, the test changed the stored input usage by one token and clicked **Refresh assessment**. During that read the panel showed its checking state and cleared the old data. The fresh lookup returned `publication_member_changed`, empty assessment and accounting lists, and null totals. The panel showed unavailable. The transport-error control also cleared a previous success. [Display regressions and on-demand lookup test](../../apps/web/src/components/Q008Assessment.test.tsx)

## Local replay

Run these commands from the project root with the private Q008 registration and publication present. The first command prepares the workspace version details and lookup outcomes in the ignored diagnostics directory. The second exercises those records in the React inspector under Vitest/jsdom, including a fresh Python lookup on each open and refresh in the damage test. Portable display fixtures also run under the normal web test command.

```powershell
uv run --extra api python -m scripts.qualify_q008_inspector
$env:OH_Q008_INSPECTOR_REPLAY = '1'
try {
  pnpm --filter @open-hollywood/web exec vitest run src/components/Q008Assessment.test.tsx
} finally {
  Remove-Item Env:OH_Q008_INSPECTOR_REPLAY
}
```

The initial workspace probe used SQLite read-only mode against the sealed database and created an empty WAL and its shared-memory file. The registered lookup refused the extra files. Both were moved to the private qualification directory after checking their origin, size and the database digest against its seal. The reproducible harness authenticates and copies the sealed bytes before opening SQLite. The original database digest is `2724fd7db1cbe2a0d400acebf5536f42f65b9f1eeabfa0dd86fd7f668f894b61`. [Replay preparation](../../scripts/qualify_q008_inspector.py)

All **ten saved-capture inspector checks** passed. The ordinary web suite passed **43 tests**, including nine portable Q008 cases. The suites include controls for mismatched selections, a different delivery ID, duplicate accounting records and changed totals. The private replay, `web.xml` and `saved.xml` are under `data/diagnostics/q008-inspector-2026-11-21/`. Zero provider calls were made.

All **2,635 Python tests**, lint, formatting, type checks and the web production build passed. One existing story-creation UI test timed out when verification jobs overlapped. The full web suite passed at its original five-second per-test timeout on the subsequent standalone run. Rebuilding the private inspector replay reproduced the same bytes.

## Next step

Qualify one application-owned, read-only API adapter for Q008. Resolve the selection from the configured workspace and its exact artifact version, then call the existing consumer. Generate the client types from that response contract and use the existing provenance endpoint’s `Cache-Control: no-store` convention. Exercise registered, unregistered and same-ID copied workspaces, plus a damaged reread, through the API and inspector together. Keep the ordinary provenance panel as the default. These checks can run on local fixtures with zero inference.
