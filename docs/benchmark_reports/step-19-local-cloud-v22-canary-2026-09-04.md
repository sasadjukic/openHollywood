# Step 19 Local/Cloud prompt-v22 canary diagnostics — 2026-09-04

## Provenance and scope

This diagnostic compares the prompt-v22 canary report at
`data/benchmarks/v0.1/v22-canary-2026-09-04/report.json` with the original
prompt-v21 canary at
`data/benchmarks/v0.1/v21-canary-2026-09-03/report.json`. The v22 plan digest
is `e732b3f5e368938daafcfffee0de1927f6e37c9965b704689cc1de3f56c46976`.
One known Local Blueprint failure remained outside production, leaving five
Local and four Cloud production-runnable cases. Human review gates are still
unset, so these results measure execution behavior rather than blind story
quality.

The comparison is directional, not a clean prompt-only experiment. Runtime
hardening added after the original v21 canary included evidence-handle
normalization, exact-node retry, a 24,000-token Cloud input allowance, prompt
compaction, and a ten-calls-per-scene aggregate budget.

## What worked

| Profile | v21 completed | v22 completed | v21 accepted scenes | v22 accepted scenes | v21 successful production calls | v22 successful production calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Local | 2/5 | 0/5 | 14 | 2 | 119/122 | 18/28 |
| Cloud | 1/4 | 3/4 | 8 | 18 | 44/50 | 83/85 |
| Combined | 3/9 | 3/9 | 22 | 20 | 163/172 | 101/113 |

Cloud completion improved materially, and its continuity calls succeeded in
21 of 23 attempts. The compact v22 context reduced first-continuity input by
6–27% on Local and 20–35% on Cloud; its Local schemas were 16–33% smaller and
Cloud schemas 25–41% smaller. The largest Cloud input was 16,227 tokens, below
the corrected 24,000-token allowance.

The narrowed contract retained meaningful World Rule enforcement. Cloud
OH-V01-002 repaired a future card that incorrectly survived an erasure, and
Cloud OH-V01-004 repaired an encrypted device that violated safehouse
isolation. Local OH-V01-004 accepted two scenes while keeping qualitative
continuity observations advisory.

## What failed

All six production-terminal failures occurred in an initial continuity check,
after a normal provider stop, while validating v22's model-authored non-world
direct-conflict certificate. Across twelve failed attempts, five mismatched
`conflict_kind`, four failed a lexical phrase check on
`logical_conflict_assessment`, and three failed exact-copy validation on
`draft_assertion`. There were no timeout, truncation, or provider-outage
failures. The one bounded retry did not recover any of these cases: Local often
fixed one redundant field while breaking another, and Cloud did not receive
the focused repair packet that Local received.

The critic also repeated a separate scope error from v21. In Cloud OH-V01-004,
it treated the story-wide 2,500-word advisory minimum as a hard per-scene
minimum, expanding the first scene from roughly 995 to 2,056 words. The final
story reached 6,636 words, 33% over the 5,000-word advisory maximum. This is a
contract defect even though word-count adherence is not a hard benchmark gate.

## Prompt-v23 corrective contract

Prompt v23 retains production graph v3 and the bounded one-repair policy, with
these changes:

- A non-world contradiction asks the model only for one canonical claim ID,
  one or more draft evidence handles, the `directly_incompatible` disposition,
  a corrective action, and an optional explanation. The application derives
  category, conflict kind, provenance, lineage, and the exact draft assertion.
- Human-readable conflict explanations are not lexically gated. Invalid claim,
  evidence, disposition, and corrective-action selections still fail closed;
  qualitative or additive craft feedback remains advisory rather than being
  silently accepted as a contradiction.
- The focused repair packet is provider-neutral and carries bounded, redacted
  `expected_value` and `received_value` diagnostics when application-owned
  validation can supply them.
- Writers and critics receive accepted words so far, the remaining story-wide
  advisory range, remaining scenes, and a derived soft scene allocation. A
  word-count-only critic issue is deterministically reduced to a note and
  cannot cause a revision unless the request contains an explicit hard
  scene-length constraint.
- Regression coverage preserves genuine World Rule blockers and structural
  critique blockers while covering the exact v22 certificate and v21/v22
  word-count failure shapes.

Prompt v23 needs a fresh canary before it can be treated as benchmark evidence.
The acceptance target is zero failures from removed certificate fields, no
word-count-only revision loops, restored Local continuity throughput, and no
regression in the genuine World Rule paths above.
