# ADR 0062: Read-only historical production review associations

- Status: Accepted; bounded local implementation
- Date: 2026-11-19
- Extends: ADRs 0038 and 0061

## Decision

Implement a separate application record, structural validator and operator exporter
for the six saved identity snapshots from the November 19 production-association
audit. Do not expand v61 assessment admission to accept historical v33 reviews.
Keep identity, source authentication and assessment eligibility separate.

The only export source is `production-association-2026-11-19`. Pin its acceptance
seal by exact byte digest in tracked code. Authenticate the complete sealed archive,
including inventory, paths and member bytes; exclude the original unsealed Python
cache directories without executing them. Accept only a registration and output
directory. No arbitrary database, snapshot, expected hash, trust override or subset
can be supplied through the operator CLI.

The structural validator independently reconstructs each association from the saved
snapshot and frozen selection. Check database snapshot identity, project/run/review
invocation, critique logical/version identity, creator/output/input links, canonical
content hashes, target UUID and matching Scene Plan. Recover one exact system/user
message pair from the saved message hash, validate the visible input inventory, and
bind ordered evidence-catalog occurrences to canonical target prose. Preserve separate
canonical and visible-target hashes and whitespace/occurrence distinctions.

Verify critique and target lineage, including parent identity and ordering. A newer
captured version never substitutes for the reviewed version. Explicit selection
matching requires role, project, logical artifact, version and canonical content
hash. It is an identity comparison over a previously authenticated record, not an
authentication API or assessment-admission decision.

## Records and eligibility

`production-review-association-1` records are strict, frozen typed values with a
published JSON schema. Parsing a record or passing structural validation does not
authenticate its source; the fixed exporter supplies that boundary. It recomputes
proofs rather than trusting the earlier private audit's derived association files.

Identity status is `verified_in_registered_snapshot`. Record lineage heads as
`latest_version_id_at_capture` and `selected_is_latest_at_capture`. Current database
revalidation and provider attestation are explicitly false. The database hash is
historical capture evidence, not permanent workspace identity. The archive retains
a digest of the SQL content serialization, but not those raw SQL bytes; only the
canonical content digest is independently recomputed.

For this registration, assessment source status remains `unsupported_contract`
(prompt 33, not 61; required boundary/run markers absent). Native assessment delivery
is `missing` within this captured evidence, and assessment attachment eligibility is
false. No check is synthesized from an old response hash or schema-success flag.
Semantic support, evidence adequacy, editorial effect, edit necessity and craft remain
unassessed; writer permission is false. Whole-review verdict and actual billing stay
null. `live_calls=0` describes this export, not the original historical review calls.

## Publication

Authenticate all 51 source files: 50 sealed members and their seal. Copy nine required
evidence members byte-exact: six snapshots, selection, database pins and original seal.
Add six association records, six literal Markdown views, an index and final manifest,
for 23 output files. The manifest identifies both the complete authenticated archive
and the copied subset. It does not claim the exported subset contains every member
listed by the original seal or can replace the registered source archive.

Reuse existing bounded reads, secret screening, symlink/junction rejection,
bidirectional destination protection, exclusive writes and manifest-last completion.
Protect the source archive and configured database/WAL/SHM paths without opening the
database. Recheck source bytes/inventory and implementation before publication and
finalization, and on exact reuse. Retain partial/conflicting output without repair.
There is no additional fsync/durability guarantee beyond the existing storage helper.

All navigation is generated from fixed case names. Source values appear as literal
JSON inside a sufficiently long fence. Complete unpublished context stays in the
local snapshots. No raw SQL database, provider settings or credential export is added.

## Limits and next boundary

This is a historical operator export, not a current database adapter, API route,
production inspector attachment, semantic qualification or new human checkpoint.
The existing seven diagnostic consumer works retain null production associations.
No engine evaluation module, native intake, publisher, production prompt, workflow,
provider implementation, persisted schema or UI is changed.

Next qualify a narrow read-only workspace lookup for explicit immutable selections.
It must authenticate workspace/source identity and revalidate the relevant rows,
without treating the historical database digest or a matching UUID as sufficient.
Keep missing, mismatched and ambiguous associations unavailable; retain old versions
when newer heads exist. Assessment attachment additionally requires a supported
production source and separately authenticated completion. Neither is supplied here.

See the [implementation report](../handoffs/assessment-association-export-2026-11-19.md).
Story quality still requires separate evaluation of feel, flow, character and
story-breaking effects. Live calls remain paused and the canary remains on hold.
