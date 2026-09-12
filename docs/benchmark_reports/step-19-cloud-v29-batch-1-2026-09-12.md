# v29 Cloud canary — batch 1, 2026-09-12

## Result

**4/4 stories completed, 21/21 planned scenes accepted, 99/99 production
invocations succeeded.** There were **zero failed invocations, zero terminal
failures and zero manual retries**. Five scenes received one continuity-driven
prose revision each. This first v29 canary batch ran to completion in
**492.722 seconds (8 minutes 13 seconds rounded)**.

Scope: Cloud OH-V01-001 through OH-V01-004, the first of three planned
four-story batches. Batch 2 and batch 3 have not been staged or launched by this
task. Step 19 remains **IN PROGRESS**; this is production evidence, not a human
quality verdict or completion of the entire Cloud-first evaluation.

| Cloud case | Status | Accepted scenes | Calls (failed) | Prose revisions | Input / output tokens | Words |
| --- | --- | --- | --- | --- | --- | --- |
| OH-V01-001 | SUCCEEDED | 5/5 | 23 (0) | 1 | 231,040 / 18,463 | 3,165 |
| OH-V01-002 | SUCCEEDED | 5/5 | 20 (0) | 0 | 192,478 / 15,768 | 3,765 |
| OH-V01-003 | SUCCEEDED | 6/6 | 30 (0) | 2 | 306,740 / 23,483 | 3,893 |
| OH-V01-004 | SUCCEEDED | 5/5 | 26 (0) | 2 | 296,045 / 23,897 | 4,454 |

All manuscripts are within their frozen advisory word-count ranges. Literary
hard gates, quality and blind preference still require human review.

## Setup, approval and isolation

Production was explicitly authorized after the
[ten-story manual run](manual-v29-cloud-production-2026-09-12.md) was documented.
The batch uses prompt **v29 / graph v7** on
`ad48a75891c380ea7ced720a72df187509d0a87e`. Only previously documented Markdown edits were
present at preparation. The preflight records those edits and content hashes of
the tracked runtime files; the runner and post-run audit verified those source
hashes unchanged. No production prompt or application behavior was edited.

The clean human-approved seed was
`data\benchmarks\v0.1\formal-2026-08-01\pre-production-approved.db`,
SHA-256 `400379c746487cecc0f26dca055c4f51ded5674407b16a0a7d42b7cc9071ab3f`.
It was inspected with read-only SQLite access and the existing secret-export
guard, copied to a new isolated campaign directory, and migrated from schema
0006 to 0007 there. The source seed and historical databases/reports were preserved.
Preflight verified zero prior production runs and zero production artifacts;
no old production checkpoint was resumed under v29.

All four selected Blueprint runs were already succeeded, with applied human
approve decisions and approval events naming the exact immutable versions.
Blueprint content hashes match both pinned v23/v25 sources. The seed retains
historical pre-production and direct-baseline state, but the explicit four-case
selection prevents execution or counting of other cases.

The existing validated 48-case plan envelope and original campaign ID are kept
for exact seed/approval lineage. The **new scope ID**
`v29-cloud-cycle-2026-09-12`, batch ID and four selected case IDs in
`preflight.json` define this execution. This does not relabel the old
48-case campaign as Cloud-only or claim it completed. Whole-canary comparison
and sealing invariants were not changed.

| Case / seed | Production run ID | Approved Blueprint ID | Approved Blueprint SHA-256 |
| --- | --- | --- | --- |
| OH-V01-001 / 19001 | `7643e3e9-2899-5c27-8b38-c64559f24cde` | `6c3e8a05-6c3f-4c44-95cf-09a10fe36f38` | `49bba4def7783dcb9e9c313c3ff21625dc3760147b0fbbecb4f8b08018ff66e1` |
| OH-V01-002 / 19002 | `b192bed7-e068-54bb-9c52-4749bf1caa50` | `0dcdcc34-65ee-4e82-8706-22a689e76f5e` | `bf7bc76b7f5dae5d533997569e4314c2f98c708cb25306c7433f6888f9e060ef` |
| OH-V01-003 / 19003 | `8de6b17d-9601-5d4f-82d1-0b7eebd8cfb5` | `07969472-3b29-4003-b705-7120095c4d9e` | `3e8cd4907cdee392ae671ed076e612c62020d549b409cdeeb215f26bb83665b1` |
| OH-V01-004 / 19004 | `801723ef-2659-51ed-9d45-a7dabcfa2ecd` | `6523e881-6b59-48a3-954e-021398e9f445` | `a118e18fb30afcf1ad8fb55db08cca77024063b2475e71839fa6f2ac6574dfd1` |

Seeds are 19001–19004. Every substantive role uses the frozen Cloud profile:
`5feda6671bdb89f311cc171cf0917e7f6227596a2a42a9c4916778211a783c70`.
Requested model: `gemma4:31b-cloud`; provider-reported model:
`gemma4:31b`. Inference ran through the existing signed-in local Ollama
Cloud route at `http://127.0.0.1:11434`. Ollama was **0.34.0**, versus
0.33.3 in the reference preflight; the model alias digest was unchanged.
Remote weights and seed enforcement remain unpinned.

The four cases ran sequentially through the existing harness with explicit case
IDs and target Cloud. The budget was $5 per story, $20 aggregate application
ceiling, at most 252 production calls, 24,000 input / 8,000 output tokens per
call, two prose revision cycles per scene, 7,200 seconds per story and a
600-second HTTP timeout. The exact manifest and persisted run budgets are local.
No new Blueprint generation or approval was needed.

## Completion, calls and recovery

All 99 new calls were production calls. Inherited Blueprint invocations remain
in seed lineage and may appear in the harness output's whole-workflow accounting;
they are excluded from the fresh production totals here.

- Production usage: **1,026,303 input + 81,611 output = 1,107,914 tokens**.
- Validation: **99 succeeded, 0 failed**; no automatic structured repair or
  transport recovery was needed.
- Prose: **26 writer drafts for 21 accepted scenes**, with five revisions
  across three stories. Only Cloud 002 had no prose revision.
- Reviews: **26/26 persisted scene critiques passed**. Continuity raised five
  blocking findings, all typed as contradictions; all final accepted versions
  have passing critiques and zero blocking continuity findings.
- There were no terminal adjudicator or dialogue-subgraph calls, no accepted
  revision-limit exhaustion and no manual run-control command.
- This is four clean production executions when “clean” means no failed
  invocation; it is one story without either failed invocations or prose revision.

| Role | Succeeded | Failed |
| --- | --- | --- |
| scene_writer | 26 | 0 |
| scene_critic | 26 | 0 |
| continuity_supervisor | 26 | 0 |
| story_bible_maintainer | 21 | 0 |

All production calls retain v29/graph v7 and the expected model. Schema-valid
output and a successful production status do not establish correct literary
judgment or absence of semantic defects.

## Revision diagnostics

| Case / scene | Recorded continuity allegation | Observed change | Character similarity |
| --- | --- | --- | --- |
| 001 / 5 | Stroller reappears despite already being present | Remanifestation passage replaced with repositioning | 80.67% |
| 003 / 2 | Sarah's stated third floor versus fourteenth-floor corridor | One dialogue passage revised | 99.37% |
| 003 / 4 | Archive entered after confession | Archive-entry sentence preserved; advisory escape attempt added | 94.27% |
| 004 / 2 | Unlatched window versus bolted door | Window closure and advisory night cue added | 97.95% |
| 004 / 4 | Satellite phone versus isolation rule | Phone replaced with prearranged extraction note | 97.65% |

The complete before/after version IDs, content hashes, prior criticism and
unified diffs are in `diagnostics/analysis.json` and
`diagnostics/revision-review.md`. Similarity is character-level Python
SequenceMatcher with autojunk disabled, not a literary-preservation score.
Four edits are narrow changes or additions; Cloud 001 rewrites a larger
manifestation passage while preserving the surrounding scene.

All five rechecks produced clean reports with empty persisted finding audits.
This confirms that the graph proceeded, not that all five allegations were
correct or all requested repairs actually occurred. Two observations merit
focused human review:

1. **Cloud 003, scene 4:** the allegation cites the Blueprint constraint
   “Inaccessible to those who have confessed.” The requested repair was to
   reorder entry/confession or establish an authorized exception. The writer
   retained the cited Archive-entry sentence and added an escape attempt from
   an advisory goal-coverage note. Continuity then cleared the scene. The
   visible diff does not substantiate the requested blocking repair; this may
   be an initial false allegation or an inconsistent recheck. It remains
   unadjudicated, not recorded as a proven semantic repair.
2. **Cloud 004, scene 2:** the selected prior-state assertion says the back
   window is unlatched; the draft describes a bolted heavy door. Those are
   distinct objects and can coexist, so the alleged contradiction appears
   questionable. The writer added an off-page window closure and a night cue.
   This is a localized edit, but not evidence the original prose needed it.

The floor-position and isolation-rule findings also retain their exact sources
for contextual review. Advisory suggestions were incorporated alongside
blocking feedback in 003/4 and 004/2. Do not silently promote those suggestions
into approved canon, or interpret automatic acceptance as human endorsement.
No tuning or v30 change was introduced during the batch.

## Matched historical Cloud comparison

Only Cloud 001–004 are compared below. The original report files remain intact.
The read-only analysis verifies case/profile/seed equality, corpus identity,
non-production versions and exact approved Blueprint hashes for the subset.
Different full attempted sets mean this is not a successful whole-canary
comparison or a sealed all-profile benchmark.

| Contract | Cloud completions | Accepted scenes | Production calls | Failed calls | Prose revisions | Input tokens | Output tokens |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v23 | 4/4 | 21/21 | 92 | 2 | 2 | 856,556 | 77,571 |
| v25 | 4/4 | 21/21 | 90 | 3 | 1 | 779,662 | 73,334 |
| v26 | 3/4 | 16/21 | 84 | 10 | 3 | 757,120 | 68,068 |
| v29 | 4/4 | 21/21 | 99 | 0 | 5 | 1,026,303 | 81,611 |

v29 retains all four v23/v25 Cloud successes and completes Cloud 002, which failed
v26. Compared with v25, failed production attempts fall from 3 to 0, while calls
increase from 90 to 99 (**10%**) and input tokens rise from 779,662 to 1,026,303
(**31.6%**). Five v29 prose revisions versus one in v25 account for additional
review work. The result supports completion and validation improvement in this
sample; it does not establish a cheaper workflow or better stories.

v26's lower aggregate usage includes an early failed case, so it is not evidence
of superior efficiency. The changing Ollama gateway, unpinned remote model and
differing generated prose limit causal interpretation. v23/v25 remain reference
canaries; this single batch is not a repeatability demonstration.

## Time, environment and cost

Runner interval: **16:34:08–16:42:20 UTC**, or approximately
**18:34:08–18:42:20 Europe/Belgrade**. The exact interval is 492.722 seconds.
Production invocation latency sums to **466.596 seconds**; per-run elapsed and
persisted active timers differ because of orchestration and timer semantics.

| Case | Production start UTC | Production elapsed | Recorded active time |
| --- | --- | --- | --- |
| OH-V01-001 | 16:34:09 | 117.434 s | 104 s |
| OH-V01-002 | 16:36:07 | 100.767 s | 93 s |
| OH-V01-003 | 16:37:47 | 113.095 s | 98 s |
| OH-V01-004 | 16:39:41 | 159.498 s | 148 s |

No provider errors, clock/budget pauses or manual control events were observed.
Estimated production cost is $0.00 in app records. That does not establish free
Cloud inference or allocate an Ollama subscription bill. Monetary budget
acceptance for Step 19 remains unverified by those zeros.

## Artifacts and verification

Local evidence directory:
`data/benchmarks/v0.1/v29-cloud-batch-1-2026-09-12/`.

The completed report is schema-validated and matches its plan digest. All four
result IDs equal the predeclared selection. Every accepted manuscript's content
and hash match the exact canonical scene references and the report output.
The final database snapshot passed the existing secret-export guard.
`diagnostics/evidence-manifest.json` records byte lengths and hashes of
the final snapshot, frozen plan/preflight, runner logs, scripts, report,
diagnostic analysis and four Markdown manuscripts.

| Evidence file | SHA-256 |
| --- | --- |
| plan.json | `ca4098fc9c8f36ffeda0b95ac5bfa11f1af9839696c6d2515a7b7ec3a07efac4` |
| preflight.json | `04cefbaca43f623409734fddf984b96bc8d520d6bf1dc66909b995f245f2b2da` |
| report.json | `e9c23a186af8111d028b9a9fe0ca6374c6b6589dddfc0701c3e35249808efa61` |
| runner-status.json | `992c3aff429f997f8ae986affc4ac9fec332c2584bb8541ded02d08760d1fad7` |
| completed-snapshot.db | `8b55dcb0d5f6467e17e5b6d66dddf44a55fd33a9134413694154d8be246f064f` |
| diagnostics/analysis.json | `012ad71106c1a0c55274f8e8bcf6c10bad3489d9ab99b75289ca99555f13a489` |
| diagnostics/evidence-manifest.json | `18e3bb697ca57ad9665271bfafe0311ca27d8241259ba94a215e034ed8b1c03f` |

Raw databases, prompts, artifacts and manuscripts are git-ignored local evidence,
not part of a public checkout. This public report preserves conclusions and
receipts; hashes identify evidence rather than supplying independent replication.
Human scores and blind preference were not manufactured.

## Remaining evaluation

Batch 1 is complete. Cloud cases 005–008 and 009–012 remain for batches 2 and 3.
This four-case canary and the separate ten-story manual sample do not replace
the complete frozen corpus, direct-model baseline, blind human rubric/hard
gates, preference, budget and repeatability requirements. Step 19 remains
**IN PROGRESS**; no later phase or Hybrid run has started.
