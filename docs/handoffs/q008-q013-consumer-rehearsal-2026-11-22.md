# Q008 and Q013 read-only consumer rehearsal

Eight interleaved selections of the two critiques and their drafts produced eight lookup rows, **two assessments and two generation usage records**. Reversing the lookups or starting with Q013 preserved the records and totals. Each row retained the requested version and position. Both drafts referred back to the critique that owned their generation request. [Q008 publication](q008-observed-publication-2026-11-21.md) Â· [Q013 publication](q013-observed-publication-2026-11-22.md)

| Active selections on refresh | Assessments | Generation usage records | Input tokens | Output tokens |
| --- | --- | ---: | ---: | ---: |
| Exact Q008 critique or draft, including repeats | Q008 | 1 | 58,894 | 345 |
| Exact Q013 critique v3 or draft v1, including repeats | Q013 | 1 | 62,835 | 427 |
| Both cases' exact selections, mixed and repeated | Q008 and Q013 | 2 | 121,729 | 772 |
| Exact Q008 plus an adjacent Q013 version | Q008 | 1 | 58,894 | 345 |
| Exact Q008 plus both Q013 selections after damage to Q013 | Q008 | 1 | 58,894 | 345 |
| Only adjacent Q013 selections, or only Q013 selections against the damaged bundle | None | 0 | Unknown | Unknown |

The combined output includes 420 reasoning tokens. Both generations reported zero cached input tokens. Each input-count measurement stayed with its original request and contributed nothing to the generation total. Actual billed cost is unknown. Q008's model judgment, operator score and usage matched the supported Q008 consumer. Q008 retained its three operator judgments. Q013 retained separate passes for claim correctness and evidence coverage, with Sol's citation to `E0920`. Application judgments about semantic support, evidence adequacy, edit necessity and craft stayed `unassessed`. [Q008 lookup](q008-consumer-lookup-2026-11-21.md) Â· [Q013 scoring](q013-sol-high-smoke-results-2026-11-21.md)

## Exact versions and refresh

The rehearsal resolved the genuine adjacent Q013 critique v2 (`3128c91a-1b2f-4b57-9c50-f89ddee061c4`) and draft v2 (`7cbed44f-b4c3-4736-a912-3ea2fad713f3`) from a read-only copy of the sealed workspace. Replacing the last exact Q013 selection with either neighbor removed Q013's assessment and usage. The adjacent lookup returned `exact_selection_unavailable` with empty claim and delivery references. When another exact Q013 selection was still present, the inventory kept one Q013 record and the adjacent row stayed unavailable. Returning to an exact version recovered the original record.

Each refresh built a fresh inventory. For each requested exact match, the rehearsal checked the registered publication manifest, reauthenticated the original delivery through the publisher and compared all 15 publication members. The rehearsal keyed assessments by delivery ID and claim ID, and accounting by delivery ID. Keeping failures local to each publication allowed the surviving Q008 assessment, score and usage to be compared in full with the healthy baseline. [Publisher](../../scripts/publish_saved_review_completion.py) Â· [Publication contract](../adr/0067-observed-saved-review-publication.md)

## Damaged Q013 publication

Each control first opened an intact disposable Q013 publication alongside Q008. The very next refresh used the same path and the same eight selections. Every Q013 row became unavailable, with no Q013 model judgment, score, delivery reference or usage record. The Q008 rows kept their positions, and their shared assessment and accounting record matched the healthy baseline in full.

| Change to the Q013 copy | Q013 lookup reason |
| --- | --- |
| Increase the generation input count by one token in `delivery.json` | `publication_member_changed` |
| Change the operator's claim-correctness score | `publication_member_changed` |
| Change the usage and recompute its member hash in the manifest | `publication_manifest_changed` |
| Remove the generation terminal | `publication_incomplete` |
| Withdraw the publication directory | `publication_missing` |

A Q013-only refresh against the damaged usage record yielded empty assessment and accounting lists and null totals. The lookup left each damaged copy as it found it. After the rehearsal restored the copy, both original records reappeared with the original combined totals.

## Local verification

The rehearsal verified **29 inventories**, including the healthy reads before each damage control and the final recovery. A second run reproduced the saved inventories and verification record byte for byte. All **86 original files checked** retained their hashes and modification times. The existing publisher and Q008 consumer suites passed all **33 tests**. Ruff lint, formatting and strict mypy passed across the 351 repository Python files and the rehearsal. Zero provider calls were made.

Private evidence is under `data/diagnostics/q008-q013-consumer-rehearsal-2026-11-22/`. Compare `mixed-inventory.json` with `adjacent-refresh.json` and `damaged-refresh.json` to inspect the full records before and after each change. The `verification.json` file records each scenario, per-row outcomes, surviving delivery IDs, generation totals, both manifest pins and the two adjacent selectors. With the private archives present, run the replay from the repository root.

```powershell
.venv/Scripts/python.exe data/diagnostics/q008-q013-consumer-rehearsal-2026-11-22/rehearse.py
```

The two-publication lookup was exercised in the private rehearsal. The supported consumer and artifact inspector continue to serve Q008. Production prompts are unchanged and the workflow canary stays on hold.

## Recommended next step

Implement the tracked read-only lookup for these two registered publications, keeping the existing Q008 command compatible. Promote the mixed-order, last-exact-selection, still-selected, valid-then-damaged and restored cases into portable regression tests. Once that lookup passes, qualify Q013's exact workspace and version binding through the API and artifact inspector before exposing it there. The next step needs only saved data.
