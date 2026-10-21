# Requiring models to reproduce exact binding metadata makes diagnostic reports unusable

Local ID: **CW-007**. Status: **PARTIALLY MITIGATED** by application-owned binding; not production-qualified.

## Problem

Diagnostic interfaces have asked models to copy exact parent hashes, fingerprinted evidence handles, versions and quotations. A substantively useful answer can fail because those identities are miscopied or combined incorrectly. Exact provenance remains necessary, but generating it as prose has been unreliable.

## Recorded evidence and attempts

- The October 19 F2/F3 comparison produced twelve incorrect parent hashes. None qualified, including F3's four descriptively correct explanations.
- V3 delivered only 1/18 valid reports; seventeen used bare catalog references instead of the required fingerprinted handles.
- In the October 20 V2 comparison, three Gemma reports and one DeepSeek report first failed citation binding. Some paired a real quotation with the wrong entry.
- C1 moved version/quote expansion into the application. Gemma delivered 12/12 valid reports, up from 5/12 under V2. DeepSeek still had separate evidence-count failures. This is promising interface evidence, not proof of supported judgments or production readiness.

## Expected behavior and local investigation

Let the application bind the exact request, parent artifact and expanded quotation from a validated short selection. Keep source choice inspectable. Selecting a real but irrelevant passage remains a semantic failure; deterministic binding cannot resolve it.

## Closure criteria

- [ ] Bind every accepted reference to the exact input versions without model-authored identity copying.
- [ ] Reject unknown, stale or cross-request references and apply corrections only to their exact parent.
- [ ] Replay saved binding failures under a separately versioned candidate contract, clearly separating offline recovery from fresh live evidence.
- [ ] Qualify delivery and semantic support separately before adopting any interface in production.

Do not repair raw hashes after the fact or rescore historical invalid reports as original successes. Evidence count, response shape and factual support have separate issues.

## Sources

- [F2/F3 and V3 binding failures](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/fulfillment-output-contract-v61-retry-results-2026-10-19.md)
- [V2/C1 crossover](https://github.com/sasadjukic/openHollywood/blob/08cd9bca404f614b4be527e3d986813bb47abc15/docs/benchmark_reports/reviewer-gemma-deepseek-v61-results-2026-10-20.md)
