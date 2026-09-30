# Formal Cloud-versus-baseline evaluation: setup

Prepared September 29, 2026. **Setup-time status: ready for execution, before
model generation.** At that checkpoint, item 4 and product Step 19 were **IN PROGRESS**.
Subsequent Blueprint execution is recorded in the
[generation report](step-19-formal-cloud-v33-blueprints-2026-09-29.md).

The user has completed reviews of all 22 manually tested stories. Those reviews
will inform the later quality discussion. They are a separate evidence set from
the new campaign's randomized comparisons and will not be imported as scores for
this campaign's stories.

**September 30 update:** all eleven eligible formal comparisons have completed
human review, and the reviewed campaign archive is sealed and verified. Item 4
is complete; Step 19 remains open for unmet acceptance criteria, unknown cost
and independent repeatability. The
[execution and review report](step-19-formal-cloud-v33-execution-2026-09-29.md#human-review-completed--2026-09-30)
records the results. The setup measurements and runbook below preserve the
original preparation state and procedure.

## Frozen campaign

| Field | Value |
| --- | --- |
| Campaign | `042918c2-8a50-49fd-831b-c1a93553d4f6` |
| Scope | `cloud-first`, plan schema 2 |
| Cases | 12 agentic Cloud + 12 direct-model baseline |
| Corpus | All OH-V01-001 through OH-V01-012; original versions and seeds |
| Model for both arms | `gemma4:31b-cloud`, remote identifier `gemma4:31b` |
| Route | Existing Ollama service at `http://127.0.0.1:11434` |
| Runtime source commit | `a60f7037367c16b1cdab0bdc55c360caaa22ecde` |
| Production | Prompt v33 / graph v9 |
| Blueprint | Prompt v9 / graph v4 |
| Baseline | Prompt v1 / workflow v2 |
| Dialogue subgraph | v2 |
| Ollama | 0.34.4 |
| HTTP request timeout | Existing formal-harness default: 900 seconds |
| Database | Fresh, isolated SQLite database at migration 0008 |
| Execution policy | Sequential cases; three four-case production batches |

Evidence directory:
`data/benchmarks/v0.1/formal-cloud-v33-2026-09-29/`.

Canonical digests:

- Plan: `a297c944acc5288dedc95c370afc8504e1d32cf5c3aa32d6c170c95ac28a6614`
- Corpus: `56057c30aa13384f7f09e9dd08d64e5dbaafb2a7498f477538483cbaa81f0f5a`
- Cloud profile: `5feda6671bdb89f311cc171cf0917e7f6227596a2a42a9c4916778211a783c70`
- Model alias metadata: `c382fbfbc73b6fdd08c8549c23caedc6e62eb09933c65a1fb82dbf3398320a4e`

All twelve registered roles use the same Cloud model. The baseline receives the
same corpus premise, mandatory requirements, forbidden shortcuts, advisory word
target and run seed through the existing direct-story prompt. It receives no
agentic Blueprint, draft or review output. The comparison uses the same intended
final story length; it does not equalize total computation across the two systems.
Record their full token usage and actual lengths separately.

This campaign starts from premises. It imports no old Blueprints, approvals,
manuscripts, model invocations or production checkpoints. This is the substantive
difference from the production-only v29/v33 canaries. The source application
database was opened read-only to inspect its Cloud profile; its bytes were
unchanged during setup. Only the new campaign database was migrated.

Ollama changed from 0.34.0 in the September canaries to 0.34.4. The metadata digest
identifies the local Cloud alias, not independently pinned remote weights. Fixed
seeds do not guarantee identical provider output. No claim of unchanged provider
internals is made. Metadata endpoints responded; inference authorization and
remaining provider quota have not been tested by a generation request.

## Prepared artifacts

The git-ignored evidence directory contains:

- `campaign.db`: initialized schema and Cloud profile, with no story state.
- `campaign-plan.json`, `corpus.json`, `profile-snapshot.json`, `batches.json`:
  frozen campaign inputs.
- `campaign-report.json`: valid report bound to the plan, with zero results.
- `preflight.json`: source/environment hashes, budgets, isolation checks and
  setup-time status. It is an immutable setup receipt, not live progress.
- `setup-file-hashes.json`: byte hashes of the immutable input/receipt files.
- `setup_campaign.py`: retained offline staging procedure.
- `verify_campaign.py`: read-only runtime/input/schema/integrity verification.
- `run-campaign.ps1`: phased operator commands with verification and timestamped
  logs. Its default phase is offline `Verify`.
- `logs/`, `blueprints/`, `public/`, `private/`: designated output locations.

No Blueprint approval packet or blind story packet exists yet: both must be built
from actual generated artifacts. No approval, review score or answer key was
invented during setup.

## Execution sequence

Run from the repository root in PowerShell:

```powershell
$campaignRunner = '.\data\benchmarks\v0.1\formal-cloud-v33-2026-09-29\run-campaign.ps1'
& $campaignRunner -Phase Verify
```

The next live phase generates the twelve new Blueprints and stops before drafting:

```powershell
& $campaignRunner -Phase PrepareBlueprints
& $campaignRunner -Phase PackageBlueprints
```

The exact versions are packaged in `blueprints/packet.json`, with a readable
dossier in `blueprints/guide.md` and a matching `blueprints/approvals.csv`. The user
has chosen to approve without editorial review to observe autonomous output. A
technical manifest can identify the exact set without exposing story contents;
the dossier remains available if requested. Record that choice separately from
any later story-quality assessment. The assistant must not fill in approval
without the user's decision on the generated set. This is the existing mandatory checkpoint in
`AGENTS.md` and the [product contract](../../open_hollywood_bible/product_contract_and_benchmarks.md#3-required-approval-checkpoints).
Failed Blueprint cases remain in the campaign denominator. If a Blueprint needs
changes, pause to record the intervention and establish valid replacement lineage;
do not silently regenerate it to improve a first-pass result.

The twelve baseline cases can run sequentially while Blueprint review is pending.
Keep their prose out of the reviewer-facing conversation before blind comparison:

```powershell
& $campaignRunner -Phase RunBaseline
```

After the completed approval form is available, apply it offline, then execute
production in the declared order:

```powershell
& $campaignRunner -Phase ApproveBlueprints
& $campaignRunner -Phase RunProduction -Batch 1
& $campaignRunner -Phase RunProduction -Batch 2
& $campaignRunner -Phase RunProduction -Batch 3
& $campaignRunner -Phase Summarize
```

| Production batch | Frozen prompts |
| --- | --- |
| 1 | OH-V01-001 through OH-V01-004 |
| 2 | OH-V01-005 through OH-V01-008 |
| 3 | OH-V01-009 through OH-V01-012 |

Use this one database, plan and report for all phases. Before live phases, the
runner checks runtime hashes, corpus, plan, database integrity, Ollama version
and model-alias digest. Drift stops execution for investigation. Do not rewrite
the frozen receipt to conceal drift, alter prompts/limits during the campaign or
launch multiple runners concurrently.

The runner never enables `--retry-failed`. Interrupted execution can resume from
durable state with the same phase command; cached successful work is recovery,
not an independent repeat. Preserve all failed attempts, logs and intervention
details. Provider/rate-limit or environmental interruptions must remain visible
in raw accounting; a separate recovery analysis may explain them.

## Budgets and accounting

Existing limits are preserved:

| Stage | Per-case call bound | Per-call input / output tokens | Configured amount |
| --- | --- | --- | --- |
| Blueprint | At most 12 | 12,000 / 8,000 | $0.50 per Blueprint |
| Direct baseline | 1 | 8,192 / 7,000 | $2.00 per baseline |
| Production | 12 per scene; 3–8 scenes | 24,000 / 8,000 | $5.00 per production run |

Blueprint aggregate caps remain 120,000 input / 36,000 output tokens and 3,600
seconds active runtime. Production retains two revision cycles per scene and
7,200 seconds active runtime. Actual production envelopes will be recorded after
the new approved scene plans exist.

The outer first-pass call envelope is 144 Blueprint + 12 baseline + at most 1,152
production calls = **1,308 calls**. This is a configured ceiling, not an expected
request count. The configured dollar amounts sum to **$90** across the campaign;
they are neither a price estimate nor a verified aggregate provider-spend cap.
Current Ollama Cloud reports no per-call dollar charge, so formal cost acceptance
remains **unknown**. The existing $2 median Cloud acceptance criterion is unchanged.

## Formal review and item 5

After all 24 cases have a terminal result, package eligible completed pairs:

```powershell
& $campaignRunner -Phase PackageBlindReview
```

With 24 successes this yields twelve randomized A/B comparisons. Keep
`private/review.key`, `private/answer-key.json`, the database, diagnostics and
sealed archive separate from `public/`. The canonical rubric includes originality,
AI-pattern concerns, prose, character, dialogue, pacing, coherence and hard gates.
The existing 22 manual reviews remain valuable contextual evidence, but cannot
replace actual reviews of these newly generated comparisons.

Reading Blueprint content exposes the approver to planned plots and characters.
If the same person scores the story pairs, record any actual exposure; approval
without reading does not itself establish plot exposure. Hidden A/B labels alone
do not establish complete reviewer blinding. A reviewer who has not seen the
Blueprints or provenance provides a stronger independent comparison. The default
reviewer ID is `primary-reviewer`; record the actual reviewer identity and exposure
in the review notes without claiming independence that did not exist.

After genuine human scores are submitted:

```powershell
& $campaignRunner -Phase ImportReviews
& $campaignRunner -Phase SummarizeReviewed
& $campaignRunner -Phase Seal
```

Evaluate the unchanged criteria: at least 95% Cloud technical completion
(12/12 is required in this twelve-case sample), at least 80% severe-continuity-free,
mean weighted score at least 3.5, no dimension mean below 2.5, and at least 60%
agentic preference under the current harness. Report failures, ties and missing
review coverage alongside the headline metrics. Cost qualification remains pending
without supported cost evidence even if all other criteria pass.

One formal campaign does not establish repeatability. Before item 5's live repeats,
predeclare fresh campaign identities, case coverage, unchanged configurations and
how Blueprint approval/intervention will be handled. Use independent executions,
not cached outputs or a renamed database. The existing canary protocol calls for
at least three independent fresh repeats; item 5 must define its Cloud-first
design rather than silently reuse the older Local/Cloud canary matrix. No repeat
has been staged or launched here. Evidence sealing proves archive integrity,
not statistical certainty or a passing quality/cost result.

Item 4 proceeded before the detailed discussion of the 22 completed manual
reviews. Formal human review and this campaign's evidence seal are now complete.
Item 5 still requires independent repeatability evidence; it cannot be closed
solely from one reviewed campaign or the prior manual-review count.

## Setup verification

Plan/corpus/profile validation passed for the exact 24-case matrix. The runner's
offline Verify phase passed against **123 frozen runtime/configuration files**.
SQLite integrity and foreign-key checks passed at migration 0008. Projects,
workflow runs, invocations, artifacts, artifact versions, approvals, checkpoints
and pending checkpoint writes all counted zero. The initial report has zero
terminal results. PowerShell parsing, campaign-script Ruff lint/format, and the
standard CLI corpus validation passed. The final metadata check also confirmed
the frozen Ollama version and model-alias digest. No application source was changed;
validation concerned the setup artifacts and operator scripts, not a new runtime
implementation. No inference request or user-database migration was performed.
