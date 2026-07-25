# Open Hollywood benchmarks

Benchmark inputs are product artifacts, not ad-hoc development prompts.

`v0.1/corpus.json` contains the accepted 12 short-prose prompts with immutable
IDs and versions, target length, required elements, forbidden shortcuts, likely
failure modes, stressed rubric dimensions, research policy, and stable seeds.

Validate it and print its canonical digest:

```powershell
uv run --extra api python scripts/evaluation_harness.py validate-corpus
```

After all three model presets are completely configured in the local database,
create a campaign plan:

```powershell
uv run --extra api python scripts/evaluation_harness.py plan `
  --database data/open_hollywood.db `
  --output data/evaluations/campaign-plan.json
```

The plan expands the corpus into 48 cases: one direct single-model baseline and
Local, Cloud, and Hybrid agentic runs for every prompt. It pins the corpus hash,
workflow versions, exact secret-free profile configurations, model identifiers,
and per-prompt seeds. Existing plan files are not overwritten unless
`--overwrite` is explicit.

Run or resume the 12 direct single-model baseline cases:

```powershell
uv run --extra api python scripts/evaluation_harness.py run-baseline `
  --database data/open_hollywood.db `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json
```

This command uses the local Ollama service endpoint. A model identifier ending
in `cloud` can still consume Ollama Cloud capacity through that service. The
report is replaced atomically after every newly executed case and again at
clean completion. Existing successful report results and succeeded SQLite
workflow lineage are reused; pass `--retry-failed` only when failed cases
should be attempted again.

The baseline runtime persists each frozen prompt input, bounded model
invocation, and complete story version in SQLite. It assigns only syntactic
hard gates automatically. Gates requiring literary judgment remain `null`
until a blind reviewer submits the canonical rubric.

Create a private blinding key, then build separate public and private review
artifacts:

```powershell
uv run --extra api python scripts/evaluation_harness.py create-review-key `
  --output data/evaluations/private-review.key

uv run --extra api python scripts/evaluation_harness.py package-review `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json `
  --blinding-key data/evaluations/private-review.key `
  --public-output data/evaluations/review-packet.json `
  --answer-key-output data/evaluations/private-answer-key.json
```

Aggregate technical evidence without human reviews:

```powershell
uv run --extra api python scripts/evaluation_harness.py summarize `
  --plan data/evaluations/campaign-plan.json `
  --report data/evaluations/campaign-report.json `
  --output data/evaluations/summary.json
```

Supplying `--reviews` also requires the separate `--answer-key`. Review files
use the strict `HumanReviewBundle` contract, including campaign identity and
unique reviewer/comparison pairs.

The private blinding key and generated answer key must not be distributed with
the public A/B review packet. None of these files may contain API keys.
