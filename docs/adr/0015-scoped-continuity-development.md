# ADR 0015: Distinguish contradiction from ordinary story development

- Status: Accepted
- Date: 2026-09-13

## Context

The five production improvements must reduce unsupported failures without growing
prompts, retry allowances or revision limits. An earlier event's time, a character's
last known state and an open thread's administrative status can be misread as
permanent constraints. A request for a clearer transition is not itself evidence
that two story assertions are incompatible.

## Decision

Production-improvement step 5 is complete under prompt v33 / graph v9. The
continuity reviewer and its existing bounded adjudicator compare affirmative
assertions about the same subject and applicable time. Later movement, discovery,
changed trust, revealed secrets and new objects can develop without an explicit
transition sentence. Missing explanation alone belongs to craft advice, not a
hard contradiction. Initial and known-fact lists are non-exhaustive.

Real incompatible facts, impossible chronology, inaccessible knowledge and
explicit constraints still block when supported by evidence. Development cannot
rewrite an established event or resolution. Facts retain their stated temporal
scope and permanent restrictions. World Rules, requirements and forbidden
shortcuts retain their existing gates. Uncertainty at adjudication still blocks.

The application now supplies more precise canonical claims:

- Each timeline event binds its summary, time context and scene in one claim;
  a bare time such as Morning cannot be selected independently of that event.
- Character, relationship and location state claims identify the actual update
  scene, making their status as snapshots explicit.
- Initial knowledge, established facts and open/resolved threads have distinct
  scopes. Resolved history remains immutable; open setups can receive a payoff.
- Administrative Story Bible kind/status labels are excluded as contradiction
  evidence. Substantive statements, resolutions and prohibitions remain available.

Exact artifact versions, source paths, canonical IDs, related IDs and draft
excerpts remain observable. Existing dispositions determine advisory versus hard
findings; no word-matching heuristic automatically settles semantic truth.
Canonical Bible reducers and artifact schemas are unchanged. No SQL migration,
new graph node, extra model call, larger budget or additional human checkpoint.
Prior runtime labels and original canary evidence remain unchanged.

## Restart evidence and bookkeeping

The user's three latest manual stories completed under v32. Read-only diagnostics
verified the reported restart during The Root Ritual: the interrupted continuity
call began at 19:37:31 local on 2026-09-13; recovery was recorded at 19:51:02, and
the resumed call used the same task fingerprint and input lineage for scene 5,
revision 0. These times use Europe/Belgrade (UTC+2). App evidence confirms workflow
recovery; it does not establish the Windows crash's cause.

One pre-reboot invocation remained RUNNING in the completed run. Future recovery
now closes that run's stranded RUNNING calls as FAILED / interrupted_execution,
with a recovery-detection timestamp and an explicit unknown provider outcome.
The timestamp is not represented as the provider's actual completion time.
Recorded token/cost fields are preserved; default zero values do not establish
that the interrupted provider call consumed no resources.

Interrupted execution is excluded from malformed-response retry context, preserving
existing restart behavior. The invocation still counts toward the aggregate call
budget. Checkpoints and canonical artifacts are preserved. The completed v32
record remains unchanged; this fix applies when a run is subsequently recovered.

Across the three runs there were 73 invocation records: 71 succeeded, one failed
Bible transition and the interrupted record above. Perfect Silence recovered from
an unknown relationship-state ID within the existing structural allowance. Lyra
had no failed calls. None used adjudication, so these completions do not validate
step 4's disputed-finding path. Lyra's shared SammyAI premise is comparison context,
not a quality judgment. SQLite quick_check returned ok, foreign_key_check found
no violations, and all 146 artifact versions matched their stored hashes.

This is an engineering recovery check, not an individual literary review or a
new canary score. Continue the user's manual-test cadence and defer the aggregate
manual review until requested after at least ten stories.

## Verification and rollout

All 521 Python tests passed. Ruff lint/format, strict mypy on 159 files and the
production build passed. Nine new cases cover temporal claim binding, actual
snapshot scenes, metadata exclusion, preserved substantive constraints,
non-exhaustive knowledge, SQLite audit lineage, advisory/hard routing and restart
bookkeeping. Simulated model dispositions test contracts and control flow, not
semantic accuracy. Existing true-contradiction, revision and adjudication controls
remain in the full suite.

Three actual v32 continuity requests were reconstructed from exact recorded input
versions. Each baseline request hash matched its invocation's recorded prompt
hash. Matched v33 requests were shorter (message content characters):

| Recorded input | v32 | v33 | Claims, v32 to v33 |
| --- | ---: | ---: | ---: |
| The Root Ritual, scene 1 | 29,933 | 29,725 | 6 to 6 |
| The Root Ritual, recovered scene 5 | 48,492 | 45,913 | 42 to 36 |
| Lyra, scene 6 | 42,032 | 38,785 | 32 to 23 |

Continuity system instructions decreased from 7,328 to 7,184 characters. Writer
and critic instructions are unchanged. These are character measurements on three
matched inputs, not token counts or a universal request-size guarantee. Reproduction
script, request pairs and hashes are retained locally under
`data/diagnostics/v33-step5-offline-2026-09-13/`. No live model call or production
DB mutation was made for this comparison.

No live v33 probe or canary was run. Manual or controlled live testing is still
needed to assess semantic improvement; no new completion-rate claim follows from
these checks. All five production-improvement implementations are complete, while
product Step 19 remains IN PROGRESS pending its evaluation and human-review work.
