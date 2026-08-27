# Step 19 Local v14 canary — 2026-08-26

## Frozen run

- Campaign directory: `data/benchmarks/v0.1/v14-canary-2026-08-26`
- Plan SHA-256: `61a3c33ae850c1bb9b7f030b896d362ceb8d2411770acc3354cde0357461b2ac`
- Production graph: `3`
- Production prompt contract: `14`
- Story Blueprint graph/prompt: `4` / `9`
- Model profile: Local, `gemma4:e4b`
- Selection: `--target local --batch-size 6 --batch-number 1`
- Run policy: normal bounded workflow repair; no operator `--retry-failed`

The database was copied byte-for-byte from the approved August 1
pre-production snapshot with SHA-256
`400379c746487cecc0f26dca055c4f51ded5674407b16a0a7d42b7cc9071ab3f`,
then migrated from schema revision 0006 to 0007. The frozen corpus digest was
`56057c30aa13384f7f09e9dd08d64e5dbaafb2a7498f477538483cbaa81f0f5a`.
All 61 benchmark-critical tests passed before execution, the Local model was
installed, and no workflow, invocation, or Ollama job was active.

## Outcome

OH-V01-001 through OH-V01-005 reached Production and failed at continuity.
OH-V01-006 retained its earlier terminal Blueprint artifact-contract failure.
The five production-runnable cases therefore completed 0 of 5.

| Prompt | Terminal result | Durable evidence |
|---|---|---|
| OH-V01-001 | Structured continuity failure | Two bounded re-check attempts repeated stale analysis for `world_rule_decay_as_narrative_1`. |
| OH-V01-002 | Revision limit | One re-check stagnation failure recovered, but a valid later continuity result still retained a blocker at the revision limit. |
| OH-V01-003 | Continuity input budget | Two scenes and Story Bible updates were approved before a later continuity request exceeded 20,000 input tokens. |
| OH-V01-004 | Continuity input budget | One scene and Story Bible update were approved before the next continuity request exceeded 20,000 input tokens. A writer Markdown-fencing failure recovered normally. |
| OH-V01-005 | Continuity input budget | One scene and Story Bible update were approved before a later continuity request exceeded 20,000 input tokens. |
| OH-V01-006 | Expected pre-production failure | The copied Blueprint still omits `beat5` and `beat6` from its Scene Plans. |

Across the five Production runs, 54 of 61 invocations succeeded:

- 18 of 19 writer calls succeeded;
- all 18 critic calls succeeded;
- 14 of 20 continuity calls succeeded; and
- all 4 Story Bible update calls succeeded.

The seven failed invocations comprised three continuity re-check stagnation
errors, three continuity input-budget errors, and one recoverable writer
Markdown-fencing error. The database passed `PRAGMA integrity_check`, and no
workflow or invocation remained running after the report was checkpointed.

## What v14 fixed

None of the failed calls reproduced v13's missing or invalid `world_rule_ids`,
missing `companion_rule_assessment`, invalid
`condition_explicitly_authorized`, or world-only-fields-on-a-non-world-finding
errors. The explicit category branches therefore closed the model-facing
schema gap they were designed to close.

The new `report.json` path also exposed detailed redacted causes for terminal
failed invocations instead of the old generic Production wrapper. This made the
stagnation finding IDs and input-budget failures visible directly in the
checkpointed report.

## New diagnosis

The explicit cross-product duplicates each full contradiction,
missing-requirement, and forbidden-shortcut branch into world-rule and
non-world variants. With the same representative catalogs and all three bases
available, compact serialized schema size increased as follows:

- initial check: 8,383 characters in v13 to 14,270 in v14, a 70.2% increase;
- re-check: 9,222 characters in v13 to 15,733 in v14, a 70.6% increase.

Prompt v14 sends the schema twice on Local calls: once inside the user message
and once through Ollama's enforced format channel. The reported input count
necessarily includes the inline copy. Successful v14 continuity calls reached
18,503 reported input tokens before three later calls crossed the 20,000-token
ceiling. This makes schema compaction, removal of the inline Local copy, and
exact prompt-component measurement the leading response; simply raising the
production budget would hide the contract's new overhead.

Re-check stagnation remains a distinct semantic Local-model problem. The model
can satisfy the structural world-rule branch while still copying a stale
assessment instead of evaluating the revised evidence.

Finally, OH-V01-002 exposed a report precedence defect. Its durable
`WorkflowRun.error_message` correctly records `blocking continuity findings
remain at the revision limit`, but `report.json` prefers the most recent failed
invocation even though that invocation recovered. Report assembly must prefer a
specific terminal workflow cause and use invocation detail only when the
workflow cause is the generic structured-output wrapper.

## Recommended next move

Before another canary:

1. preserve the six semantic basis/category combinations while composing shared
   object fields once, and verify Local Ollama support for the compact schema
   form;
2. measure prompt, schema, artifact, and retry-context token contributions on
   the three budget failures;
3. make re-check output distinguish unchanged offending evidence from changed
   evidence structurally, reducing the opportunity to copy stale analysis; and
4. fix report-cause precedence so a recovered invocation cannot mask the true
   terminal workflow cause.

The v14 campaign is immutable diagnostic evidence and must not be resumed under
a changed prompt contract.

## Implemented response: prompt v15, graph v3

Prompt v15 implements all four follow-ups while retaining production graph v3:

1. each blocking finding now has one shared object and independent nested
   `basis_details` and `category_details` unions, preserving the six semantic
   combinations without duplicating the full object;
2. representative initial and re-check schemas are 5,792 and 6,543 UTF-8 bytes,
   reductions of 59.4% and 58.4% from v14, and Local user messages no longer
   repeat the schema already supplied through Ollama's enforced format channel;
3. every invocation records content-free byte counts, hashes, and diagnostic
   token estimates for system, artifact, control, retry/repair, inline-schema,
   and gateway-schema contributions, while an over-budget response retains its
   exact provider-reported token usage;
4. contradiction and forbidden-shortcut re-check details declare evidence as
   `changed`, `unchanged`, or `newly_exposed`, which the application validates
   against prior exact evidence; and
5. a specific terminal workflow cause now outranks failed invocation detail,
   preventing a recovered structured-output attempt from masking the actual
   terminal failure in `report.json`.

A Local Ollama probe accepted and enforced the chosen nested `anyOf` object
shape. An alternative `allOf` composition was rejected because the Local model
accepted the schema syntactically but did not reliably honor its constant-field
constraints. A final production-shaped v15 probe returned the required nested
contradiction/non-world structure from `gemma4:e4b` with 93 reported input and
156 output tokens. The low input count on that deliberately tiny prompt also
shows why inline and gateway-schema contributions must be measured separately;
the enforced format schema is not reflected like an inline schema copy in the
provider's prompt-token count. No v15 canary was started as part of this
implementation change.
