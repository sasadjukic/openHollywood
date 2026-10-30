# Proposed diagnostic-probe export adapter

Date: **2026-10-30**. **PROPOSAL ONLY — not implemented or live-authorized.**
Model/daemon budget **zero**. Prompts unchanged, inference **PAUSED**, canary
**ON HOLD**.

The [twelve-capture provenance audit](reviewer-probe-provenance-audit-2026-10-30.md)
justifies a narrowly supported adapter for the sealed October 16 ordinary-v61
probe archive. It can supply operators with verifiable mechanical evidence from
existing captures. It cannot certify semantic judgments, recover missing
production lineage or establish story quality.

Recommended bounded local implementation:

1. **Define a separate typed `diagnostic_probe` contract.** Bind experiment,
   trial, stage, arm, seed, successful attempt, synthetic-context flag, historical
   contract versions, source namespace and source-closure identity. Retain exact
   request, response, receipt, input-source and rendered-view hashes. Leave
   production invocation and canonical critique identities absent; do not insert
   rows, rename diagnostic keys or weaken the SQLite export's source checks.
2. **Read saved evidence only.** Accept an explicit supported archive and up to
   twelve distinct trial IDs. Require complete preparation/live seals, reservation
   binding, successful receipt, exact response and all required source records.
   Retain failed predecessor links without promoting them. Emit a specific
   unsupported/incomplete/inconsistent result or refuse the export; never
   regenerate a missing prompt, receipt or judgment. Support this archive's
   contract explicitly rather than assuming all later probes have the same form.
3. **Preserve all three review views.** Keep full raw model content, normalized
   critique and saved native audit. Label application-rendered repair advice and
   verdict normalization. Bind native-selected handles to the full catalog and
   exact source offsets. Distinguish shown current catalog, visible historical
   repair quotations and recovered old prose. Keep source and view hashes separate.
4. **Reuse the deterministic algorithms without inventing production identity.**
   The existing catalog replayer, exact string/hash rules and literal-source
   rendering are suitable for reuse. The current production `SourceSpan` and
   `ReviewSnapshot` require project/creator identities that these probes do not
   have. Use explicit probe records, or extract a narrow common text-comparison
   helper with parity tests; do not manufacture UUIDs to fit those types. Preserve
   separate excerpt results and unresolved semantic alignment.
5. **Qualify and export the same pinned twelve captures.** Add tracked positive
   and corruption fixtures for retry identity, synthetic-source labels, advice
   origin, source visibility, missing hashes and repeat export. Preserve the
   original-review display, secret guard, literal Markdown, bounded size and
   refusal to overwrite changed/partial destinations. Verify deterministic repeat
   exports and source immutability locally. Update ADR/documentation/tracker with
   actual deliverables and coverage; retain all historical scores.

Success means twelve transparently labeled, reproducible operator review bundles
from the existing supported archive, with no database mutation or model calls.
It does not mean twelve newly qualified production reviews or repaired critic
failures. Do not add a writer route, semantic repair permission, new human
checkpoint, acceptance gate or literary score.

No additional live experiment follows automatically. The audit recovered the
already known event-versus-endpoint and ending-preservation examples. A future
experiment still needs a materially different hypothesis grounded in observed
evidence, followed by frozen cases, scoring, stops, budget and explicit approval.
