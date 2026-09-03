# Step 19 mixed Local/Cloud v21 canary — 2026-09-03

## Scope

- Campaign: `f0190000-0000-4000-8000-000020260801`
- Plan digest: `0a85c406fe24a19683f30b644826b5bfe5df7fd4670ede5d6bd366bc62cfe5e3`
- Story Blueprint graph/prompt: v4/v9
- Scene production graph/prompt: v3/v21
- Local model: `gemma4:e4b`
- Cloud model: `gemma4:31b-cloud`
- Executed batches: Local batch one (six planned cases, five production-runnable)
  and Cloud batch one (four cases)

This is diagnostic canary evidence, not a formal benchmark conclusion about
either model.

## Result

| Profile | Completed | Other production state | Terminal production failure | Blueprint failure |
| --- | ---: | ---: | ---: | ---: |
| Local | 2/5 runnable | 1 budget pause | 2 | 1 |
| Cloud | 1/4 | 0 | 3 | 0 |

Local OH-V01-004 and OH-V01-005 completed. OH-V01-003 successfully made all 40
reserved calls, accepted four scenes, and paused before the next Story Bible
update because the production budget reserved eight calls per planned scene
while graph v3 can require ten. OH-V01-001 and OH-V01-002 stopped with blocking
continuity findings at the revision limit, but their underlying judgments were
different: the first was semantic overreach, while the second found real Scene
Plan drift and then recommended weakening or removing an immutable requirement.
OH-V01-006 retained its pre-production Blueprint failure.

Cloud OH-V01-001 completed. OH-V01-002 and OH-V01-003 both failed continuity
after bounded repair because requirement coverage supplied values outside the
candidate draft's exact evidence-reference catalog. The prior diagnostic did
not retain those rejected values, so it could identify the field and rule but
not the model's attempted reference. OH-V01-004 reached a continuity re-check
whose provider-reported input was 21,161 tokens, exceeding the frozen 20,000
per-call allowance; application composition telemetry estimated 17,610.

Compared with the recent Local canaries, v21 recovered from v20's zero of five
and two accepted scenes, but remained below v18's three of five and 18 accepted
scenes. Its Local production-call success was 119 of 122 and continuity success
was 35 of 38, versus 48 of 53 and 14 of 19 for v20 and 76 of 83 and 18 of 25 for
v18. The high call reliability shows that v21 removed much of v20's structural
schema burden; completion remained limited by semantic continuity decisions and
the incorrect aggregate call envelope. The Cloud sample is the first comparable
v21 Cloud batch and should not be treated as proof that model size is or is not
the primary constraint.

## Manual Cloud diagnostics

`The Seamstress` first reached a failed continuity specialist after two invalid
exact-evidence attempts. The UI exposed Stop and Blueprint retry choices but no
retry at the failed production node. Retrying from the Brief produced another
approved Blueprint that reused `scene_1` while changing its Scene Plan from
`Stitches of Silence` to `Silk and Secrets`. Production handoff then collided
with the already persisted project-level artifact
`scene_plan_scene_1` version one:

`deterministic handoff artifact 'scene_plan_scene_1' has conflicting content`

That exception occurred before a production child was persisted. The worker
therefore continued to see the approved Blueprint as eligible, selected it
again immediately, and repeated the same failure. `Unreleased` had an approved
Blueprint but no production child and was starved behind that loop. The UI's
`Succeeded at Approval` label described only the selected Blueprint workflow;
it did not mean autonomous production had completed.

## Retained v21 response

Prompt contract v21 and graph v3 stay unchanged so the next run does not mix a
new semantic prompt experiment into the operational diagnosis.

1. Derive the production call envelope from the graph contract: with two
   revision cycles, each scene reserves three specialist calls for each of
   three candidates plus one Story Bible call, or ten total.
2. Give Cloud-capable profiles a bounded 24,000-token input allowance and reduce
   inline schema duplication by defining the evidence enum once and referencing
   it throughout continuity output.
3. Normalize a model value only when it is either an exact evidence handle or
   the unique exact excerpt represented by one handle. Preserve bounded,
   secret-redacted rejected values in validation diagnostics.
4. Append immutable Scene Plan and initial Story Bible versions keyed by the
   approved Blueprint lineage when regenerated content differs. Replays of the
   same content remain idempotent.
5. Persist a terminal `production_handoff_failed` child before returning any
   pre-graph handoff error. That child removes the approved Blueprint from the
   worker's eligible set and prevents retry starvation.
6. Expose the exact failed Production node as retryable when a durable
   checkpoint exists. Retrying requeues the same checkpoint and preserves all
   completed artifacts, events, and model invocation history. Label workflow
   attempts explicitly as Story Blueprint or Production and do not offer Stop
   for already terminal failures.

The next canary should remain v21/v3 and rerun the same Local and Cloud batch
shape. It can then distinguish runtime recovery from model-semantic variance
without adding another prompt-contract variable.
