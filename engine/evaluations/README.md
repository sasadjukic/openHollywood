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

The initial 12-prompt corpus is stored at
`benchmarks/v0.1/corpus.json`. The corpus must never be edited silently; change
a prompt version or create a new corpus version.

The current Step 19 implementation is still in progress: operator wiring for
all configured provider deployments, blind human reviews, and the formal
budget-authorized benchmark campaign have not run yet.
