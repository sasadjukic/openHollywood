# Q008 read-only consumer lookup

The exact critique and the draft it reviewed open one saved Sol assessment of Q008. Either selection can be opened alone, first, or repeatedly. The original critique remains the selection used for generation. [Operator command](../../README.md#q008-lookup) · [Publication decision](../adr/0067-observed-saved-review-publication.md)

## What a consumer receives

The command returns a JSON object with contract `q008-consumer-lookup-1`. Its `lookups` list follows the requested order. Each available row references the shared delivery and claim. The `assessments` list contains the whole claim, attributed model judgment, citations, separate operator score and application status. The `accounting_records` list holds the original request selection and the generation usage once per delivery. [Lookup implementation](../../scripts/lookup_q008_completion.py)

| Selection or publication state | Lookup result | Assessments | Usage records |
| --- | --- | ---: | ---: |
| Exact critique, exact draft, or both in either order, including repeats | Available for every exact selection | 1 | 1 |
| Exact pair and a same-text adjacent draft | Exact pair available, adjacent draft unavailable | 1 | 1 |
| Adjacent draft alone | `exact_selection_unavailable` | 0 | 0 |
| Previously valid publication with altered usage | `publication_member_changed` for both selections | 0 | 0 |
| Missing directory, incomplete publication, changed manifest or extra member | Unavailable for both selections, with a reason | 0 | 0 |

The saved model judgment was `supported`, with citations `E0233` and `E0883`. The operator scored the label, plan evidence and ending evidence **3/3**. Application semantic support, evidence adequacy, edit necessity and craft remain unassessed. Generation used **58,894 input and 345 output tokens**, including 165 reasoning tokens in output and zero cached input. The preliminary count of 58,894 is reported separately. Actual billed cost is unknown. When all selections are unavailable, both lists are empty and `generation_totals` is null. [Original score and usage](q008-sol-high-smoke-results-2026-11-20.md)

## Local verification

Each lookup reads the fixed `critique-first` publication, pins its manifest by SHA-256, authenticates the observed journal and operator score through the publisher, and compares all 15 published files with the canonical bytes. The reader projects the native bound result. Its only input is the selection list. It reads existing files and prints to standard output. [Publisher](../../scripts/publish_q008_completion.py)

The saved draft has a single version. The adjacent-version control uses a disposable SQLite copy containing a child with identical prose and digest. The child's distinct version ID makes it unavailable even in an inventory containing both eligible selections. The damage control first opens a valid copy, changes its generation usage and opens it again in the same process. That second read returns no claim, score, citations or usage. Additional controls cover a locally recomputed manifest, missing closure or manifest, extra file, withdrawn publication and changed upstream score. [Portable regression tests](../../tests/api/test_q008_consumer_lookup.py)

The tracked lookup reproduced all eight saved-capture inventories, the adjacent-only result and seven absence or damage controls from the rehearsal. All 58 original files retained their hashes and modification times. Local verification details are in `data/diagnostics/q008-consumer-lookup-2026-11-21/verification.json`. The lookup used zero provider calls. [Rehearsal and fixture lineage](q008-consumer-rehearsal-2026-11-21.md)

All **2,635 distinct Python tests** passed, including the 11 new lookup tests and the 11 existing publisher regressions. All **34 web tests** passed. Python and frontend lint, formatting, type checks and the web production build passed.

## Next step

Qualify a read-only display in an isolated artifact inspector. First verify that its workspace can resolve the exact critique and draft through the normal version lookup. Switch to the same-text successor while the earlier lookup is in flight, then refresh an exact selection after publication damage. Check that each transition clears the previous judgment and usage and shows the current selection's status. Keep the single shared accounting record and the distinction between model judgment, operator score and application status visible. This qualification can use local captures throughout.
