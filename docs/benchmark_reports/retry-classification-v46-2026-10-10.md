# Critic classification preservation v46: 2026-10-10

Implementation, all required local verification and the approved three-call
campaign are complete. Classification was preserved in all three responses, but
all three reviews failed on a newly introduced historical repair link.
Step 19 remains IN PROGRESS and Step 20 remains NOT STARTED.

## Problem and change

The v45 unchanged control called its generic tension complaint a repetition of
`assignment:outcome`, then changed it to independent craft during structural
retry. The original reference was structurally valid; its comparison object and
one historical repair's consolidated links were malformed.

Production contract v46 / graph v9 retains valid classification choices in
bounded failure metadata. Critic retry policy 13 supplies exact category,
severity, current evidence handles and classification counts, bound to the
candidate and task fingerprint. Runtime validation rejects silent changes,
dropped complaints and duplicate counts. Issue ordering is immaterial. Rejected
review prose stays out of the retry packet. All ordinary finding and comparison
validation remains in force.

This is classification preservation, not semantic endorsement. Metadata-identical
complaints retain their counts without being merged; different wording or
defective reasoning may still require human inspection. Capture remains bounded
and skips invalid or oversized groups. See [ADR 0031](../adr/0031-preserve-critic-classification-during-structural-repair.md).

## Local evidence

- 33 new regressions cover repeated and independent choices, both provider
  delivery modes, drift and omission, reorderings, shared metadata, invalid and
  stale hints, bounded capture, disappearing hard findings and immutable original
  repair identities.
- A persisted workflow rejects an empty summary after domain validation, retains
  the valid classification for its retry and completes with the same candidate,
  original tests and writer count. No extra manuscript revision is introduced.
- All five initial diagnostic requests are identical to their v45 messages and
  settings. Only a failed review's structural retry gains the new information.
- All six saved v45 responses are replayed unmodified. Four valid reviews
  materialize identically; the two rejected responses remain rejected.
- Under the new retry contract, the labeled v45 first-response counterfactual
  (comparison wrapper and missing boundary link corrected manually) produces the
  same two original repair targets, with no new target.
- The labeled v45 retry counterfactual (comparison coverage corrected but null
  reclassification retained) now fails with `critic_classification_drift`.

Those edited copies are offline simulations, not new model successes. The real
v45 campaign remains four valid cases and one failed unchanged case.

Final checks passed: 862 Python tests (173.72 seconds), Ruff lint/format, strict
mypy across 184 files, frontend formatting/lint/types, 11 frontend tests (6.61
seconds), production build and `git diff --check`. No test or validation rule was
weakened.

## Approved live experiment

Three probes reused the exact saved first failed v45 response against the private
OH-V01-002 unchanged draft and its existing synthetic explicit endpoint. Each
uses one remaining structural retry, at seeds 19102, 19103 and 19104. The first
response is not regenerated; these are controlled replays, not three independent
natural review sequences.

The predeclared expectation was that the critic retains `assignment:outcome`, repairs
comparison shape and the missing boundary link, and preserves original repair
IDs without introducing another target for the same allegation. Both structural
results and the underlying claim and remedy were inspected. A format-valid
response alone would not establish semantic success.

- Destination: existing Ollama deployment, `gemma4:31b-cloud`.
- Maximum: three calls total; 24,000 input and 8,000 output tokens per call.
- Recorded October 8 rates: USD 0.14/M input and USD 0.40/M output.
- Maximum recorded-rate estimate: **USD 0.01968**. Actual charges remain unknown.
- One call per probe. No additional retry, writer call, canonical change or
  full-story run. Sealed benchmark evidence remains unchanged.
- Limitation: one saved failure and one model; no live independent-craft control.

Private requests, source hashes, local replay evidence and the runnable harness
are under `data/diagnostics/retry-classification-v46-2026-10-10/` (ignored by Git).
The source database is read-only and its SHA-256 remains
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.

## Results

The user explicitly approved the three retries. Exactly three calls ran, with no
additional retries or writer calls. Receipts and raw model responses are retained.

| Observation | Result |
| --- | --- |
| Retained original classification and metadata | 3/3 |
| Corrected comparison object and selected-target coverage | 3/3 |
| Corrected original outcome repair's boundary/outcome links | 3/3 |
| Fully validated reviews | **0/3** |
| New invalid link from original tension repair to `issue:0` | 3/3 |

All three generic complaints still describe the immediate handwriting confirmation
as prematurely removing skepticism. Their comparisons explicitly call this a
repetition of the outcome breach. They do not claim independent craft as the v45
retry did. Manual inspection supports retention of the same underlying allegation
in these responses, not merely the same reference value. This narrow observation
does not demonstrate general semantic accuracy or prove a causal effect across
other stories and models.

Each response also links the original tension repair to `issue:0`. But the generic
issue declares itself a repetition and is consolidated into the hard assignment
finding before historical links are resolved. It therefore has no separate
`issue:0` identity to link. The original tension obligation may remain unmet with
`current_finding_refs=[]`; it does not disappear when the current repetition is
folded into the assignment finding. The first saved v45 response already used an
empty link for this original repair, so the invalid link is new in these retries.

Three labeled offline copies change only that link from `["issue:0"]` to `[]`.
Each then materializes as REVISE with the same two original repair tests and zero
new targets. Nothing else is edited. This isolates the remaining structural
failure; it does **not** convert the actual failed responses into successes.

Usage: **41,832 input / 4,225 output tokens**, estimated **USD 0.00754648** at the
recorded October 8 rates, below the approved USD 0.01968 maximum. Provider usage
reports a zero numeric cost with an **unknown** cost basis; that is not evidence
of zero charges. Actual charges remain unknown.

Frozen code, requests, source responses and source database hashes were verified
after execution and offline diagnosis. Full benchmark and canonical artifacts
remain unchanged. All final local quality checks listed above still apply; no
production code changed during or after the live campaign.

## Remaining work

The next focused change is to make the distinction between a retained raw
complaint and a separately linkable current finding explicit before emission.
In particular, a generic assignment repetition must not be offered or selected as
`issue:N` for an original craft repair. Preserve the original obligation as unmet
with empty links when no eligible independent current finding repeats it. Do not
restore the discarded duplicate, change categories to force a link, merge original
repair IDs or clear links silently in application code.

The additional decision-to-verify complaint from the missing-turn control is a
separate unresolved issue. Neither that question nor full-story recovery, human
preference and cost acceptance is closed by this change.
