# Step 19 autonomous-production round report

Date: 2026-08-09  
Campaign: `f0190000-0000-4000-8000-000020260801`  
Branch: `codex/step-19-autonomous-production`

## Status

This production round exercised all 35 human-approved Story Blueprints: 11 Local,
12 Cloud, and 12 Hybrid. It is an engineering and completion report, not the
final Step 19 benchmark summary. Blinded review packets, human scoring,
preference analysis, final cost analysis, and evidence sealing have not happened.

The round produced 26 complete stories. Three workflows failed and six Cloud
workflows remain durably paused. Step 19 must remain in progress.

## Aggregate results

| Profile | Approved | Succeeded | Failed | Paused | Completion | Completed scenes | Prose words | Calls succeeded / failed | Input tokens | Output tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Local | 11 | 10 | 1 | 0 | 90.9% | 49 | 37,817 | 227 / 3 | 1,860,558 | 183,842 |
| Cloud | 12 | 5 | 1 | 6 | 41.7% | 28 | 22,384 | 198 / 12 | 1,659,293 | 189,639 |
| Hybrid | 12 | 11 | 1 | 0 | 91.7% | 52 | 47,009 | 250 / 5 | 2,200,520 | 225,427 |
| **Total** | **35** | **26** | **3** | **6** | **74.3%** | **129** | **107,210** | **675 / 20** | **5,720,371** | **598,908** |

Among workflows that reached a non-paused terminal outcome, 26 of 29 succeeded
(89.7%). Local and Hybrid, which were not left paused by the earlier Cloud
interruption, completed 21 of 23 stories (91.3%).

Provider-reported aggregate invocation latency was 12,226,298 ms (about 203.8
minutes): 95.9 minutes Local, 20.2 minutes Cloud, and 87.6 minutes Hybrid. This
is summed invocation latency, not end-to-end campaign elapsed time.

All profiles recorded estimated cost as `$0.00`. The signed-in Ollama route did
not provide usable monetary estimates, so this round cannot support the Step 19
cost criterion.

## Non-completed cases

| Profile | Prompt | Case | Outcome | Accepted / planned scenes | Last node | Reason |
| --- | --- | --- | --- | ---: | --- | --- |
| Local | `OH-V01-001` | `a3fe7bda-7677-5400-a4b7-57610a505c81` | Failed | 1 / 5 | continuity | Blocking continuity findings remained at the revision limit. |
| Cloud | `OH-V01-002` | `50ba5887-ac09-5d1c-86b3-56c54b6eacb2` | Paused | 2 / 5 | continuity | Wall-clock budget; 9,448 seconds elapsed. |
| Cloud | `OH-V01-004` | `2c7f9eb3-248a-521f-9913-df0b6162ce3a` | Paused | 0 / 5 | continuity | Wall-clock budget; 9,222 seconds elapsed. |
| Cloud | `OH-V01-005` | `6b930f42-7747-5bd3-bab0-e2ebcba1015a` | Paused | 0 / 4 | continuity | Wall-clock budget; 9,163 seconds elapsed. |
| Cloud | `OH-V01-006` | `4c2eb13b-a996-54b4-8ee8-6d0045b3a343` | Paused | 0 / 5 | continuity | Wall-clock budget; 9,105 seconds elapsed. |
| Cloud | `OH-V01-008` | `557e3b3f-5b1e-5a37-9150-ce9c656e6f28` | Paused | 0 / 6 | continuity | Wall-clock budget; 8,686 seconds elapsed. |
| Cloud | `OH-V01-010` | `875e6395-be88-55fc-bb9d-658b5686f828` | Paused | 4 / 5 | critique | Wall-clock budget; 8,474 seconds elapsed. |
| Cloud | `OH-V01-012` | `039a7438-bbb0-5757-a581-317a3d95770c` | Failed | 2 / 6 | continuity | Blocking continuity findings remained at the revision limit. |
| Hybrid | `OH-V01-009` | `1ca51cb1-a42d-547e-ae9c-d0ab905a24fc` | Failed | 5 / 6 | continuity | Local continuity supervisor exhausted structured-output attempts. |

The six Cloud pauses were caused only by `max_wall_clock_seconds`. Interrupted
downtime was measured from the original `started_at` timestamp and counted as
active run time when Cloud was resumed. They must not be interpreted as six
model-quality failures.

## Reliability observations

The production adapter originally trusted models to reproduce application-owned
scene and artifact lineage. Local models returned plausible but invented IDs,
and Story Bible maintenance also copied canonical event IDs, sequence numbers,
and existing prohibitions. The branch now materializes those deterministic
fields from exact input artifacts while retaining model-authored prose,
criticism, continuity judgments, state descriptions, and resolution text.

Cloud continuity output exposed another redundant routing mismatch: findings
could declare blocking severity while returning `blocks_approval=false`. The
application now derives that routing flag from canonical severity. Focused
production, workflow, and worker tests passed with fixtures that deliberately
invent lineage, reuse event IDs and sequences, duplicate prohibitions, and
return an inconsistent blocking flag.

Remaining production-call failures in the retained database were:

- Local: two Story Bible schema/invariant attempts and one deliberately
  reconciled interrupted critic invocation.
- Cloud: ten structured-output attempts and two deliberately reconciled
  interrupted invocations.
- Hybrid: four local continuity structured-output attempts and one transient
  cloud writer `provider_unavailable` attempt.

Continuity is the dominant risk: it caused both quality-limit failures, the
Hybrid structured-output terminal failure, and most recoverable validation
attempts.

## Evidence audit

- SQLite integrity: `ok`.
- Running invocations after Hybrid: `0`.
- Duplicate successful task fingerprints: `0`.
- Current database SHA-256:
  `5a450d333f4db7a9120a52e3c1db1b7129ca48f56c2e1dff54ebb5940881ed15`.
- Frozen plan SHA-256:
  `97eb18775807739b2ad9b5dbde3b3bca0f717920e3db9e087655cd0173ce57ba`.
- Current JSON report SHA-256:
  `24363fd30e2c96831f5c9312a1f5c77b9e386069a9134321cf5e4a783fc55925`.

The current `report.json` is not a complete round index. It contains 22 results:
one baseline, five Cloud successes, all 12 Hybrid results, and only four Local
successes. SQLite contains all 35 production runs. The report checkpoint/merge
path must be repaired before blinded packets or a sealed archive are generated.

The earlier concurrently started Local attempt is excluded from these metrics
and remains preserved separately as `aborted-concurrent-production.db`. The
current campaign database was restored from the verified pre-production approval
snapshot before the retained Local run.

## Recommended path

1. Fix wall-clock accounting so only active execution intervals consume the
   run budget. Persist active intervals or accumulated active duration across
   interruption and resume; do not infer it as `now - started_at`.
2. Fix atomic report merging so running one target cannot discard prior target
   results. Add a regression covering sequential Local, Cloud, and Hybrid target
   runs plus retries and paused cases.
3. Add a bounded structured-output repair path for continuity responses and
   persist safe validation locations. Preserve fail-closed semantic validation;
   do not auto-rewrite continuity findings or recommendations.
4. Record retry attempt ordinals accurately. Separate invocations currently
   remain auditable, but `retry_count` does not communicate the graph attempt.
5. Add a cost estimator for the signed-in Ollama Cloud route, or run through a
   provider route that returns billable usage. A zero-cost record is not
   sufficient for the benchmark cost criterion.
6. After these fixes, create a new formal campaign from the approved Blueprint
   snapshot and rerun all profiles without manual budget mutation. Do not use
   the six paused Cloud cases as final completion evidence.
7. Only after a clean 35-case production pass should the project create blinded
   comparison packets, collect/import human reviews, generate the completion,
   continuity, quality, preference, and cost summary, and seal the final archive.

Hybrid is the strongest operational signal in this round: 11 of 12 stories
completed despite mixed routing, versus 10 of 11 Local. That does not establish
creative-quality preference. No profile should be selected as the benchmark
winner until blinded human scoring is complete, and Cloud cannot be compared
fairly until its interruption-related pauses are rerun cleanly.
