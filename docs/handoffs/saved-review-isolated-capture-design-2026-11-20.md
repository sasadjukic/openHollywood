# Backup search and design for one ordinary v61 review

**November 20, 2026.** No additional qualifying workspace backup was found. A local
rehearsal established that the ordinary production critic can persist an exportable v61
review of an exact saved scene without running the writer or starting the workflow.
The response was injected. Genuine reviews admitted, gold records frozen, assessor
outputs viewed, claim replays and live calls all totaled **zero**.

## Backup search

The filename inventory covered the accessible local Desktop (including project checkouts,
the legacy rebuild, observations and test runs), Documents, Downloads, OneDrive and
public user folders. It also checked for named project, workspace, backup and File
History locations, Codex worktrees, database overrides and additional mounted drives.
It considered SQLite, dump and archive filenames with project or backup context.
The 54 database paths from the earlier inventory all matched. No additional candidate
appeared outside the checkout. Inside it, four formal v33 evidence ZIPs and one cost
test ZIP contained eight JSON members each. The remaining SQL file was a read-only
inventory query. ZIP inspection used member names only. Discovery excluded test
databases, dependency caches and unmounted or remote storage and did not follow
junctions. The result is bounded to these locations. [Prior inventory of 54 databases](saved-review-v61-admission-2026-11-20.md)

## Source for the proposed capture

I selected the earliest successful ordinary critic in the September 29 formal cloud
campaign, ordered by start time and invocation ID. Its input links identify scene 1’s
first writer draft and the standalone plan, approved Blueprint and Story Bible used
with it. Selection used lineage metadata before any judgment about the scene.
Historical v33 invocation `17d67eb2-766a-4caa-971f-2210bc675a03` supplies those links.
The proposed v61 critique would have its own run, invocation and output version.

| Saved input | Exact artifact version |
| --- | --- |
| Scene 1 draft | `b74efc96-dbe6-4147-8dd3-a1c24f295321` |
| Scene 1 plan | `b5179ac9-5585-5e5b-9555-20ca70b68f6a` |
| Approved Story Blueprint | `2cd751b5-57ce-4c81-8ecc-1fce54998fe3` |
| Story Bible | `28816b59-339c-57de-9a67-e6006c926bf9` |

## Local verification

On a disposable SQLite copy, the rehearsal verified all four content hashes, the
Blueprint approval and the draft creator. It prepared a separately identified
scene-production run and called `ProfileRoutedProductionExecutor.critique` directly
for revision zero. The production Ollama adapter serialized the full two messages to
an HTTPX mock transport. Socket connections were blocked during the rehearsal.
The saved prompt hash matched the messages seen by the mock. [Ordinary critic](../../apps/api/open_hollywood_api/services/production_model_executor.py) · [Ollama adapter](../../engine/open_hollywood_engine/models/ollama.py)

| Check | Observed in the final rehearsal |
| --- | --- |
| Dispatch and database delta | One mock POST, one successful schema-validated critic invocation and one new immutable critique version |
| Exact-version binding | The new critique linked to its creating invocation and the selected draft. The export recovered the selected plan, both original messages and native audit schema 7 under prompt 61 and graph 9. |
| Downstream use | Both read-only export and saved-review intake returned `compatible`. Writer, continuity and assessor dispatches totaled zero. |
| Repeat and source integrity | Repeating the task returned the same critique with zero further dispatches or versions. The source database, WAL and shared-memory file matched their prior hashes, sizes and modification times. |

Eight focused export regressions passed, covering normal read-only reuse and seven
refusal conditions including wrong target, missing source, missing prompt and
incompatible contract. The private discovery inventory, container inventory, rehearsal
script and receipt are under `data/diagnostics/saved-review-backup-capture-design-2026-11-20/`.
[Export regressions](../../tests/api/test_review_evidence_export.py) · [Saved-review contract](../adr/0038-read-only-review-evidence-export.md)

## Proposed capture and stops

1. **Prepare offline.** Recheck the source pins on a consistent copy of
   `data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/campaign.db`. Create a fresh
   dedicated diagnostic run in a private workspace outside worker discovery. Preserve
   the approved lineage and frozen profile. Leave the historical campaign rows intact.
   Bind the run ID, four version IDs and hashes, ordinary request bytes and destination
   in the approval manifest. Refuse drift, prior attempts or a cached result.
2. **Authorize one initial critic generation separately.** The archived profile selects
   `gemma4:31b-cloud` through the local Ollama daemon at
   `http://127.0.0.1:11434/api/chat`. The full system and user messages measured
   10,997 and 50,272 characters. The mock POST body SHA-256 was
   `35452ffd86fe44f4639f3fada86b7d00a97c1aaece16911dcba5e6195392bc51`.
   The ordinary settings were temperature 0.2, top-p 0.95, seed 19101 and thinking
   off. Proposed limits are **one POST, zero count calls, zero retries**, 24,000 input
   tokens, 8,000 output tokens and a 300-second outer deadline. The application reserves
   USD 0.20. Ollama Cloud billing is unknown in this adapter.
3. **Execute only the critic entry point after approval.** Require a durable single-use
   dispatch intent before transport. Reject a second send across restarts. Stop on
   cancellation, timeout, HTTP error, malformed or truncated output, mismatched
   identity or budget overrun. Preserve the terminal evidence and any reported usage.
   An open or ambiguous dispatch consumes the attempt. A request for revision also
   ends capture. No replacement scene, repair call, writer dispatch or graph resume.
4. **Verify and admit independently.** On success, seal the private database snapshot
   and receipt, verify exactly one new invocation and critique, then run the existing
   read-only exporter and intake. Label provenance as an isolated provider-generated
   ordinary critic review. Inspect the normalized critique and native audit for one
   substantive whole factual claim within the authority of the original request. If
   one qualifies, freeze its verbatim span, exact versions, expected label, adequate
   evidence locations and rationale in a hashed gold record **before opening assessor
   output**. Only then replay locally against that record. An absent defensible claim
   ends in a documented gap. Editorial preference and story quality remain for human
   review. The existing Q010 registration covers its authored fixture only.

**Next step.** Prepare the single-use capture harness and approval manifest locally.
Verify the real adapter against injected failure and interrupted-dispatch cases. Submit
the exact destination, payload digest, budget and stops before enabling any transport.
Production prompts remain unchanged, live calls are paused and the canary is on hold.
