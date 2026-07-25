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

The initial 12-prompt corpus is stored at
`benchmarks/v0.1/corpus.json`. The corpus must never be edited silently; change
a prompt version or create a new corpus version.

The current Step 19 implementation is still in progress: the full-story
application executor and formal paid benchmark campaign have not run yet.
