# ADR 0023: Bind material advancement to the current scene endpoint

- Status: Accepted
- Date: 2026-10-08
- Amends: ADR 0021's shared boundary policy and ADR 0022's overrun applicability.

## Context

The v38 critic acknowledges that the frozen OH-V01-002 scene completes handwriting
verification beyond its assigned decision to verify. It still passes the scene
because scene 2 retains a more specific flourish and full acceptance of the
warning. The user requested work on whether retaining that later detail should
justify advancing beyond the current endpoint.

## Decision

New runs use prompt v39 / graph v9. The existing writer and critic share a policy
that makes the current outcome/exit state bind substantive plot and knowledge
changes independently of later work. A more specific later detail or stronger
proof does not authorize an earlier result. A decision, attempt and established
result are distinct states.

Setup, foreshadowing, guesses, inconclusive tests and incidental follow-through
remain permitted when they do not establish a result beyond that endpoint.
Explicit current-plan instructions can authorize overlap; a broad goal or summary
cannot override a specific endpoint. The critic must identify any authorizing
plan field and instruction in its existing current-endpoint comparison.

Keep the existing five-field `scene_boundary_check`. Change `overrun` applicability
to require only a populated current outcome or turning point. No next reservation
is necessary; final scenes can also overrun. The schema and validator agree on
this rule. Without either current anchor, the bound status allows only
`no_overrun`; other assignment checks remain available.

A valid model-reported overrun still becomes a blocking assignment issue and
forces revision independently of craft scores. Repair guidance asks the writer
to remove unassigned material advancement, not merely defer one detail of an
already established result. It includes next-scene reservations only when supplied.

This is a semantic instruction plus application validation of the reported
decision. The application does not infer an overrun from words such as
"identical" or "exceeds," and does not treat valid evidence handles as proof of
correct interpretation. A `no_overrun` response cannot clear independent blockers.

## Scope and verification

No additional role, call, response field, dependency, migration or canonical
artifact schema is introduced. Graph v9, repair guidance v10, provider settings,
budgets and retry/revision limits remain unchanged. Existing audit provenance and
malformed-response handling remain intact. The seven measured critic requests
grow by 251 characters; their corresponding writer requests grow by 254.

Eleven new cases cover Local/Cloud applicability with present, absent and final
reservations, blocking despite perfect scores, optional reservation guidance,
permitted simulated judgments, shared policy through revision, explicit overlap,
and persisted final-scene revision/replay. Existing v38 applicability tests now
use the absence of a current anchor. Full checks passed: 697 Python tests, Ruff,
strict mypy, frontend checks, 11 frontend tests and production build. Simulated
judgments verify plumbing, not semantic discrimination.

## Live result and limit

All seven approved isolated Gemma4 probes validated on their first calls.
The original overrun still passes. The critic calls the comparison preliminary
while explicitly acknowledging that it concludes the handwriting is identical.
Its current-endpoint comparison states that the required outcome is achieved;
its next-scene comparison still relies on the reserved flourish and full acceptance.
It cites no current-plan instruction authorizing the extra result.

Five legitimate-progress controls pass without boundary issues, and the missing
turn still blocks through the independent assignment gate. Every response says
`no_overrun`, so the controls do not demonstrate successful discrimination.
No fresh writer, full-story, repeatability or multi-provider result is established.

See the [implementation and probe report](../benchmark_reports/binding-endpoint-v39-2026-10-08.md).
The policy and routing change is implemented; improved detection remains
unqualified. Step 19 is IN PROGRESS; Step 20 is NOT STARTED.
