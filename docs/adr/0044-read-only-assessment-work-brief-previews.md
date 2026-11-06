# ADR 0044: Read-only assessment work-brief previews

- Status: Accepted
- Date: 2026-11-06
- Extends: ADRs 0041–0043, with their diagnostic provenance and authority limits.

## Context

The Sol-high U/B comparison produced one obligation-scope failure in U and its
matched recovery in B. The failing response described the story facts correctly
but answered whether further repair was needed. Its identical U repeat passed.
The user authorized regression preservation and a bounded read-only integration
check. This supports a local authored brief preview, not production promotion.

## Decision

Add the pure `evaluations.assessment_work_brief` module alongside the existing
work, result and scope components. It has no provider, filesystem, database,
workflow, prompt construction or dispatch operation. Existing contracts and
callers remain unchanged.

`assessment-work-briefs-1` binds an authored collection to the exact work
fingerprint and canonical fingerprint of the complete scope declarations. Each
entry identifies an existing selected unit and supplies a question, temporal
scope, source authority and evidence obligation. These are bounded nonblank
strings supplied by the author. Expected labels and extra fields are rejected;
free text is not automatically checked for answer leakage or semantic neutrality.

`preview_work_briefs` revalidates work, request-bound active scope, declarations
and briefs. Duplicate or foreign units, changed work/declarations and unchecked
authority overrides are rejected, including supplied inactive entries. It
recomputes the existing scope audit rather than accepting cached findings.
Every active unit receives a finding. Missing briefs and existing scope issues
remain `needs_scope_review`; they are not filled in, filtered or reinterpreted.

The preview retains the complete declaration audit, including the original
selection, whole report field, pointer, offsets and versioned source locations.
The renderer displays that preview with the complete work and full context as
literal JSON inside dynamically sized fences. Optional native results must pass
the unchanged result-binding boundary. Historical quote-witness responses and
receipts are not converted into that native contract.

`declared_consistent` is a mechanical result, not semantic admission. A brief can
still misinterpret its claim or disagree in meaning with a declaration while
passing identity checks. Temporal scope and authority remain authored assertions;
the application does not invent them from the claim or document names. The full
evidence requirement and the shorter brief remain separate visible records.
Declaration references are not a whitelist of valid answer citations.

The new contracts explicitly keep `model_input` false. Factual support, evidence
adequacy, obligation existence, observed fulfillment, edit necessity, editorial
effect and craft remain unassessed. Whole-relation credit and writer permission
remain false. Successful delivery, citation binding or a model's supported label
cannot create a repair requirement. Existing completion behavior is unchanged.

## Qualification

Tracked authored tests exercise missing and unresolved scope, stale bindings,
inactive entries, full-context literal rendering, unsupported fields, unchecked
caller mutation, native-result validation and completion without semantic credit.
A deliberately wrong free-text question passes structural checks while remaining
explicitly unverified. Private regressions retain all 24 captured reports and 144
original judgments without rescore or synthetic native receipts.

No persistence, migration, dependency, API/client schema, exporter eligibility,
production prompt/profile/graph, acceptance gate, writer route or human checkpoint
changes. Any model-input adapter or autonomous brief authoring requires separate
qualification. See the [integration record](../handoffs/reviewer-work-brief-integration-audit-2026-11-06.md).
