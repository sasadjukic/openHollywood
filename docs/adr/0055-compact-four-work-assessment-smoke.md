# ADR 0055: Compact version-two four-work assessment smoke

- Status: Accepted for local qualification and freeze; live execution awaits approval
- Date: 2026-11-14
- Extends: ADRs 0052–0054; does not reopen the version-one smoke

## Decision

Add a separate `assessment_openai_compact_smoke` application service and CLI.
Preserve the version-one runner and every previously sealed presentation, mapping,
manifest and journal. The compact request preparation stays explicitly distinct
from permission to run it.

1. Freeze N06/N07/N10/N11, their original six active claims and one original batch
   per work. Bind registered intake, verified compact presentation/export manifest,
   local provenance, exact new request set and implementation, including the CLI.
   Preserve all eight qualified version-two endpoint bodies byte for byte.
2. Use new version-two plan, event, header, audit and publication discriminators.
   The new loader authenticates the compact export as well as the native intake.
   Mixed version-one plans or changed provenance cannot enter this path. Publication
   and journal locations must stay outside source, preparation and presentation trees.
3. Count all four works in fixed order before any generation. Freeze four count
   slots and four generation slots, no retries/resume/replacements, Sol/high,
   272,000 input and 32,000 output tokens per generation, $1 conservative generation
   estimate per work, 120/600-second network deadlines and a 3,600-second run window.
   Review model metadata against official documentation without calling the provider.
4. Use the already qualified serializer and response mapper through one async HTTP
   client. Disable redirects, environment proxies and connect retries; verify TLS.
   Check actual outgoing bytes, write/fsync intent before transport, reauthenticate
   sources and bound exports before each dispatch, and enforce cancellable deadlines.
   Check the remaining deadline again after durable intent: if it expired, retain
   the consumed slot as cancelled and do not send it.
5. Stop on failed/unknown/over-budget counts; failed or unsafe terminal delivery;
   native binding failure; unknown usage or a reservation violation; cancellation;
   deadline; or source/presentation/request/code/journal drift. Never trim context,
   increase a budget, repair a response or substitute another work/model. Uncertain
   interrupted intents consume their slots and remain auditable without resumption.
6. Preserve every fixed slot, including undispatched slots, native whole-work
   coverage and nullable usage. Report generations with unknown usage separately
   from generations with accounting holds: known excessive usage is not unknown.
   Keep actual billed cost null and semantic judgments unassessed. Origin describes
   the application transport path; a local journal is not provider-signed attestation.
7. Qualify the real client configuration with injected transport and a separate
   journal. Only explicit `run`, exact approved plan hash, fixed empty live journal
   and confirmation of the full prose/context at both OpenAI endpoints may resolve
   the approved application key and construct real transport. `verify` and `audit`
   never resolve that key or dispatch requests. Fixture qualification cannot occupy
   the fixed live journal. Existing process secret-refusal guards remain active.

The separate orchestration preserves the earlier frozen implementation hashes.
Any later common-core refactor needs its own qualification. This change adds no
production prompt/profile/gate, database schema, UI route, writer permission or
human workflow checkpoint. The canary remains on hold.

## What the smoke can establish

Whether the smaller exact presentation fits the reservation and delivers native
assessments for these four works. Inspect every delivered claim for whole-claim
support and material evidence coverage using its unchanged declarations and brief.
No new semantic gold is invented, and authored local responses remain fixtures.
Delivery and factual assessment do not qualify editorial judgment or story quality.

See the [frozen plan](../handoffs/assessment-openai-compact-smoke-plan-2026-11-14.md).
