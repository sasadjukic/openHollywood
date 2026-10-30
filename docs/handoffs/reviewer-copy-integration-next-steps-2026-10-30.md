# Proposed next step: a read-only application-evidence export

Date: **2026-10-30**. **PROPOSAL ONLY.** No live experiment or call budget is
proposed. Production prompts remain unchanged, inference **PAUSED**, canary
**ON HOLD**.

The [local integration design](reviewer-copy-integration-design-2026-10-30.md)
supports a small tracked implementation of a **read-only operator export for
saved ordinary-critic reviews**. The literal-comparison question no longer needs
model inference. Another PO/EX repeat would not resolve the remaining question
of selecting semantically appropriate passages.

Recommended bounded scope:

1. **Record the integration contract in an ADR and port the tested core.** Keep
   the deterministic domain contract separate from the SQLite adapter. Use typed,
   versioned source/selection/export records with boundary validation. Preserve
   current prompt, graph, native-audit, fulfillment and acceptance behavior.
2. **Add an explicit offline operator command.** Accept exact invocation IDs and
   a new export destination. Open a consistent read-only SQLite view, never
   initialize a model gateway or a worker, and keep existing records immutable.
   Begin with the supported v61/schema-7 ordinary critic. Recover saved messages
   only when their stored hash matches exactly; unsupported/missing records get
   bounded diagnostic outcomes. Preserve credential guards and exact-source
   integrity checks.
3. **Export assignment-to-selected-evidence comparisons automatically from saved
   native handles.** Emit every selected excerpt separately with application
   labels, exact field/version/handle/offsets and visibility provenance. Preserve
   the complete original review and its independent status. Leave original-to-
   revision correspondence unresolved unless a separately bound reviewed mapping
   exists; do not add a text-similarity selector or an LLM selection step.
4. **Qualify the exporter locally.** Port the twelve cases and SQLite retry/replay
   checks into tracked tests. Include missing canonical lineage and unsupported
   historical messages as explicit non-results. Verify repeat export, source
   drift rejection, a fresh database session and no database mutation or network
   activity. Run the applicable repository lint, typing and test suites.
5. **Inspect at most twelve saved ordinary production reviews.** Inventory
   compatibility first and select exact existing invocation IDs before export,
   then examine source completeness and passage selection. Availability of twelve
   eligible v61 records has not been established by this pass. If records are
   absent or unsupported, report that coverage gap; do not generate replacements,
   silently retag earlier versions, or substitute authored diagnostics. Supporting
   an older contract needs its own local compatibility checks. Report export
   coverage and unresolved mappings separately, without claiming model gains.

The export should help people review machine-prepared mechanics without making
literal wording a story-quality score. It needs no manuscript editor, new human
checkpoint, model call or production prompt change. An external derived export
requires no SQL migration; persisted/API/UI evidence would be a separate design
with appropriate migration and generated-contract work.

After this pass, consider a new live diagnostic only if the saved-review audit
identifies a concrete materially different failure, such as an otherwise valid
review selecting another character's passage or omitting an essential clause.
First preserve that failure with source ground truth. Then propose and separately
freeze a comparison of **selection**, with explicit controls, fresh families,
both presentation orders, scoring, stop rules and an approved ceiling. Do not
bundle writer revisions or a full workflow canary into that experiment.

No live budget, request set, model-setting change or production admission is
authorized by this proposal. PO remains limited diagnostic evidence, EX remains
unadopted, all unresolved issues stay open, and story-quality qualification
continues to require human judgment.
