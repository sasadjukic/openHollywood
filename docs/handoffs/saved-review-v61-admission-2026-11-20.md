# Saved v61 factual-claim admission audit — 2026-11-20

**Source gap.** The 54 inventoried workspace and benchmark databases contained zero
ordinary production critic invocations with prompt v61. The highest recorded prompt
version was 33. None carried native audit schema 7. The six-review allowance was
therefore unused. No candidate review was opened for claim inspection, no assessor
output was viewed, no gold was frozen and no claim replay ran.

## Evidence

| Inventory measure | Result |
| --- | ---: |
| Databases read for metadata | 54 (configured workspace plus 53 benchmark and campaign databases) |
| Ordinary-critic rows across all snapshots | 1,712 |
| Distinct critic invocation IDs | 1,254 (1,197 succeeded, 56 failed, 1 running in the saved snapshot) |
| Configured workspace alone | 147 rows (144 succeeded, 3 failed), prompt versions 29–33 |
| Rows with prompt v61 / rows with native audit schema 7 | 0 / 0 |
| Eligible reviews / detailed reviews opened / claims admitted | 0 / 0 / 0 |

Before querying review metadata, the audit recorded the source scope, eligibility
filter, six-review cap, whole-claim evidence requirements and gold-before-replay order.
Discovery covered the configured database and SQLite files under the project’s
`data/` tree. Of 3,607 database paths, 3,553 had test-directory markers and were
excluded. Repeated campaign snapshots count separately in the row total. The distinct
count uses invocation UUIDs. This result covers the inventoried local sources.

The saved-review contract requires a successful, schema-validated ordinary critique,
matching prompt v61 and graph 9 on the invocation and frozen run, and native audit
schema 7. The metadata screen alone ruled out all 1,712 rows. Opening source prose or
assessor results could not change those stored versions. The registered Q010 source
was already admitted as an authored fixture. The October ordinary-v61 probe archives
also have documented diagnostic provenance. Neither supplied a fresh saved production
review for this audit. [Saved-review contract](../adr/0038-read-only-review-evidence-export.md) ·
[Q010 qualification](assessment-saved-review-openai-2026-11-19.md) ·
[October probe provenance](ordinary-review-admission-2026-11-12.md)

## Verification

The existing read-only inventory ran on disposable copies of each database and its
WAL where present. An independent SQL count in a separate read transaction checked
the ordinary-critic total and the two version counts for each database, including
numeric and text version tags. All 54 database path and metadata row sets matched
the October inventory. Size, SHA-256 and modification time matched before and after
for every inventoried database and its existing sidecars. Four focused regressions
passed for read-only inventory, snapshot consistency, write refusal and path handling.
[Earlier workspace inventory](reviewer-copy-export-results-2026-10-30.md)

The private evidence is under `data/diagnostics/saved-review-v61-admission-2026-11-20/`.
`protocol.json` records the admission rules. `inventory.json` contains per-database
metadata and source pins. `summary.json` records the deduplicated counts and
prior-inventory comparison. `disposition.json` records the empty selection and the
SHA-256 digests of the inventory and protocol. This audit contributes zero accuracy or
story-quality observations. Live calls totaled zero and the workflow canary stays on hold.

## Recommended next step

Look first for a **different, existing workspace backup** containing a genuine ordinary
v61 production critique. Inventory that backup on a consistent SQLite copy. If a
review qualifies, verify its immutable critique, draft, plan and source inputs. Select
one substantive whole factual claim, freeze the expected judgment, evidence locations
and rationale before opening assessor output, then replay locally. Revisit the current
54 databases when their source data changes.

If another backup is unavailable, the next local task is to design an isolated capture
of **one** ordinary v61 critic review against an exact saved scene and plan. First verify
that the ordinary persistence path can produce the required invocation, artifact links,
messages and schema-7 audit without starting downstream writer work. Any proposed
provider call would have its own bounded plan for approval. A fresh database row would
still require claim-level admission before it could be used to evaluate reviewer accuracy.
