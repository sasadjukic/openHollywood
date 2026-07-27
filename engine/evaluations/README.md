# Evaluations

The provider-neutral evaluation package implements the reproducible core of the
Open Hollywood v0.1 benchmark:

- strict versioned corpus contracts and canonical SHA-256 pinning;
- exact campaign snapshots for graph versions, baseline model, and Local,
  Cloud, and Hybrid profile configurations;
- one direct-model baseline plus three agentic cases per prompt;
- sequential, failure-isolated execution with terminal-result resume;
- complete-output lineage through workflow-run, invocation, and artifact-version
  identifiers;
- the accepted eight-dimension weighted human rubric and seven hard gates;
- deterministic blind A/B packets whose public files contain no model or profile
  provenance;
- separately stored answer keys and aggregate v0.1 success criteria.

`BenchmarkCaseExecutor` is the application boundary for actual story
generation. The harness deliberately does not import provider SDKs, workflow
checkpoint types, or SQLAlchemy models.

The application layer now provides a persisted direct-baseline executor. It
uses the provider-neutral gateway, makes a single seeded and bounded story
call, and records the frozen prompt version, invocation, workflow run, and
complete story version in SQLite. Successful persisted cases replay without a
second model call. The harness can select only the baseline target while
retaining a partial campaign report for later agentic execution.

Agentic preparation now uses the actual SQLite-checkpointed Story Blueprint
graph. The benchmark snapshot—not the mutable current preset—selects every
specialist model. Calls persist the profile digest, prompt-template version,
seed, settings, exact input artifact versions, usage, latency, cost, and schema
status. Structured outputs are enforced for compatible local deployments and
validated at the application boundary for every deployment. The graph stops at
the required human Blueprint approval and replays that paused state without
duplicating calls.

After approval, the application layer deterministically materializes the
embedded Scene Plans and initial canonical Story Bible as immutable artifacts.
The real SQLite-checkpointed production graph then routes writer, critic,
continuity, and Story Bible maintenance through the frozen profile. Every call
is reserved against aggregate and per-call budgets, records exact inputs and
configuration, and replays successful task fingerprints without another
provider request. Story Bible deltas are reduced locally into canonical
successors. Accepted Scene Drafts are assembled without another model call into
one persisted `BenchmarkOutput` carrying the Blueprint, scene, final-bible,
manuscript, invocation, token, latency, cost, and hard-gate evidence.

Long campaigns accept a report-checkpoint boundary. The operator implementation
atomically replaces a validated JSON report after every new terminal case, so
process failure does not discard hours of completed inference. Failed results
remain resume evidence unless retry is explicitly requested.

The operator flow preserves the mandatory human checkpoint:

```powershell
uv run --extra api python -m scripts.evaluation_harness plan `
  --output data/benchmark-plan.json
uv run --extra api python -m scripts.evaluation_harness run-baseline `
  --plan data/benchmark-plan.json --report data/benchmark-report.json
uv run --extra api python -m scripts.evaluation_harness prepare-agentic `
  --plan data/benchmark-plan.json
uv run --extra api python -m scripts.evaluation_harness approve-blueprints `
  --plan data/benchmark-plan.json --case-id <reviewed-case-id>
uv run --extra api python -m scripts.evaluation_harness run-agentic `
  --plan data/benchmark-plan.json --report data/benchmark-report.json
```

`prepare-agentic` runs Local, Cloud, and Hybrid cases sequentially and stops
each one at its durable Story Blueprint interrupt. The operator must explicitly
approve reviewed case IDs before `run-agentic` will start production. Every
stage is idempotent and uses the same SQLite lineage and atomically checkpointed
report. Repeat `--target local`, `--target cloud`, or `--target hybrid` to stage
a subset. By default, cloud-tagged models are reached through the signed-in
local Ollama server. Pass `--direct-ollama-cloud` to route cloud deployments
directly with the runtime-only `OLLAMA_API_KEY`; Hybrid then uses separate local
and cloud gateways selected from the frozen campaign snapshot.

After every planned case has a successful terminal result, package and collect
the blind reviews without exposing the private answer key:

```powershell
uv run --extra api python -m scripts.evaluation_harness create-review-key `
  --output data/benchmark-review.key
uv run --extra api python -m scripts.evaluation_harness package-review `
  --plan data/benchmark-plan.json --report data/benchmark-report.json `
  --blinding-key data/benchmark-review.key `
  --public-output data/benchmark-public.json `
  --answer-key-output data/benchmark-answers.json
uv run --extra api python -m scripts.evaluation_harness create-review-form `
  --public-bundle data/benchmark-public.json --reviewer-id reviewer-1 `
  --output data/reviewer-1.csv --guide-output data/reviewer-1.md
uv run --extra api python -m scripts.evaluation_harness import-reviews `
  --public-bundle data/benchmark-public.json --input data/reviewer-1.csv `
  --output data/benchmark-reviews.json
uv run --extra api python -m scripts.evaluation_harness summarize `
  --plan data/benchmark-plan.json --report data/benchmark-report.json `
  --answer-key data/benchmark-answers.json `
  --reviews data/benchmark-reviews.json --output data/benchmark-summary.json
uv run --extra api python -m scripts.evaluation_harness seal-evidence `
  --plan data/benchmark-plan.json --report data/benchmark-report.json `
  --public-bundle data/benchmark-public.json `
  --answer-key data/benchmark-answers.json `
  --reviews data/benchmark-reviews.json `
  --summary data/benchmark-summary.json `
  --output data/benchmark-evidence.zip
uv run --extra api python -m scripts.evaluation_harness verify-evidence `
  --archive data/benchmark-evidence.zip
```

The Markdown guide carries the canonical rubric, weights, score anchors, and
hard-gate definitions without system provenance. CSV forms can be divided
among reviewers and merged by repeating `--input`. Import rejects incomplete
scores, invalid gates, duplicate reviewer/comparison pairs, unknown
comparisons, and files from another campaign or public packet. Review evidence
schema v2 pins the exact public-bundle SHA-256, and summary generation requires
that digest to match the separately stored private answer key.

`seal-evidence` is the formal completion boundary. It refuses partial reports,
unreviewed comparisons, mismatched corpora/plans/packets, foreign answer keys or
reviews, and summaries that cannot be reproduced from the supplied evidence and
declared cloud-run budget. The deterministic archive stores canonical JSON,
fixed metadata, a self-describing manifest, per-member SHA-256 digests, counts,
and explicit public/private classifications. `verify-evidence` checks all
digests and relationships and reproduces the exact archive bytes. Treat the
whole ZIP as private because it contains model/profile identities, story
outputs, reviewer identifiers, and the blind answer key; only members under
`public/` are reviewer-safe.

The initial 12-prompt corpus is stored at
`benchmarks/v0.1/corpus.json`. The corpus must never be edited silently; change
a prompt version or create a new corpus version.

The current Step 19 implementation is still in progress: blind human reviews
and the formal budget-authorized benchmark campaign have not run yet.
