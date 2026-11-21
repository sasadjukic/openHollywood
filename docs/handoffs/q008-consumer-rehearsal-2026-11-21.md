# Q008 read-only consumer rehearsal

The exact critique and reviewed draft opened **one Q008 assessment and one generation usage record** in the same local inventory. Reversing the order or opening the two selections repeatedly produced the same assessment, score and token totals. The original critique remains the selection used for inference. [Registered publication](q008-observed-publication-2026-11-21.md)

| Lookups in one inventory | Assessment rows | Generation usage records | Display |
| --- | ---: | ---: | --- |
| Exact critique alone or exact draft alone | 1 | 1 | Sol’s assessment of Q008 |
| Both exact selections, either order, including repeated opens | 1 | 1 | Two exact versions can refer to the same assessment |
| Exact pair plus adjacent draft, adjacent first or last | 1 | 1 | Both exact versions available, adjacent version unavailable |
| Adjacent draft alone | 0 | 0 | Unavailable, usage unknown |
| Both exact selections with a damaged, incomplete or absent publication | 0 | 0 | Both unavailable, usage unknown |

The displayed claim was the complete 307-character outcome explanation. Sol returned `supported` with citations `E0233` and `E0883`. The **3/3** belongs to the operator who checked the whole-claim label, plan and draft ending against the frozen gold. The application continues to report semantic support, evidence adequacy, edit necessity and craft as unassessed. [Original adjudication](q008-sol-high-smoke-results-2026-11-20.md)

Generation used **58,894 input and 345 output tokens**, or **59,239 total**. The 165 reasoning tokens are included in output, and cached input was zero. The preliminary endpoint also counted 58,894 input tokens. The consumer kept that measurement separate from generation usage. Actual billed cost remains unknown.

## Identity and failure controls

The rehearsal used the 15-member `critique-first` publication pinned by SHA-256 `efef8fc3348b3a5cfc3c9529e6e645d390685e5030c01d56b257eaa27631619d`. It rebuilt the canonical bytes through the publisher’s read-only collection path and checked all members on each lookup batch. The independently published `draft-first` bundle yielded the same inventory. A missing directory stayed absent. [Publisher contract](../adr/0067-observed-saved-review-publication.md)

Each allowed lookup matched the project, role, artifact ID, version ID and content digest. The critique version was `2268e6e8-b82b-4cca-932f-55cc418a58b5` and the draft version was `b74efc96-dbe6-4147-8dd3-a1c24f295321`. The inventory keyed assessments by **delivery ID and claim ID**, and generation accounting by **delivery ID**. Each displayed lookup refers to these records.

The sealed workspace contained only version 1 of this draft. A disposable SQLite copy supplied a **fixture version 2**, `c176b3ef-6868-5f0f-822c-2b2da9390ff2`, with version 1 as its parent and identical prose and content digest. The source-row check confirmed a valid draft identity. The consumer returned `exact_selection_unavailable` because this assessment belongs to the registered version 1 pair.

Seven publication controls covered an absent directory, missing manifest, missing closure, changed usage, changed operator score, changed usage with a recomputed member digest in the manifest, and an unexpected file. The six damage cases first opened successfully as intact copies. On reread, both selections showed unavailable and exposed no model judgment, operator score, evidence or usage. The missing and damaged controls were left exactly as found.

## Local evidence and replay

Open `data/diagnostics/q008-consumer-rehearsal-2026-11-21/inventory.md` for the shared view. `inventory.json` holds its lookup rows, assessment and accounting record. `adjacent-unavailable.md` and `damaged-unavailable.md` show the two failure displays. `verification.json` records the scenarios and fixture lineage.

With the private Q008 registration and published bundles present, run the replay from the project root.

```powershell
.venv/Scripts/python.exe data/diagnostics/q008-consumer-rehearsal-2026-11-21/rehearse.py
```

The rehearsal verified eight inventory cases, one adjacent-only lookup and seven damaged or absent publication cases. All **58 original files** checked retained their hashes and modification times. All **63 focused publisher and consumer tests** passed. Ruff lint, formatting and strict mypy passed, including the rehearsal. Zero provider calls were made.

## Recommended next step

Implement a tracked read-only Q008 consumer lookup for this fixed publication. Require complete, pinned source bytes on every read, return stable delivery and claim references for the two exact selections, and return an explicit unavailable result when a version or publication fails verification. Promote the same-text successor and valid-then-damaged reread into portable regressions. Once that lookup passes, qualify its display in the artifact inspector. This step requires no inference. Step 19 remains in progress and the canary is on hold.
