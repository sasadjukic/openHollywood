# ADR 0065 — Read-only saved-review completion adapter

Accepted on 2026-11-19 for local authored fixtures.

## Decision

Give saved ordinary-review completions their own source, receipt, audit and export
contracts. A review can be inventoried from a normalized critique and its native audit
even when the raw critic response is unavailable. A later assessment requires its own
request, attempt and terminal evidence. The first registration is the closed, authored
v61 workspace and assessment journal from the [local qualification](../handoffs/assessment-production-intake-qualification-2026-11-19.md).

The service owns the archive location and acceptance-seal digest. It reads the sealed
SQLite bytes into a disposable copy and uses existing saved-review intake to rebuild the
original work. The source receipt binds the invocation, both immutable artifact identities,
intake, work, scope declarations, briefs and exact offline request. The historical source
path in the intake manifest is used only to reproduce its recorded digest.

An authored terminal becomes a native receipt only after its intent and closure agree
with the registered bytes. Publication additionally requires exact whole-work coverage
through the existing result binder. The output records the raw authored final and its
resolved citations. Missing delivery and an unclosed intent each have an explicit audit
state. A failed or malformed final cannot publish a successful subset.

The CLI publishes immutable operator files using the existing manifest-last writer.
Identical exports can be reused. Source and output are rechecked before finalization.
The fixture reports zero live calls, null token observations and unassessed editorial
effect. Production attachment and writer dispatch require separate decisions.

## Scope

The registration covers one closed image, one batch and one authored delivery. This
decision introduces no live-workspace enrollment, provider mapping or persisted schema.
Existing probe and authored-packet registrations retain their own contracts. See the
[implementation and verification report](../handoffs/assessment-saved-review-adapter-2026-11-19.md).
