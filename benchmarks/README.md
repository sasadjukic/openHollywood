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

The private blinding key and generated answer key must not be distributed with
the public A/B review packet. None of these files may contain API keys.
