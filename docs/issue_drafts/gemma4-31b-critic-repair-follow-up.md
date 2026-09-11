# Deferred evaluation follow-up: 31B critic coverage and minimal word repairs

Status: **deferred as of 2026-09-11**. This is an issue draft, not a submitted
GitHub issue. Revisit after the Cloud-first production evaluation establishes
that `gemma4:31b-cloud` is a viable end-to-end testing model.

## Summary

Open Hollywood's frozen creative-writing diagnostics found useful POV,
assignment and prose-review capabilities in 31B, but inconsistent mechanical
review and minimal word-repair advice. A correct `revise` verdict and valid
evidence reference do not necessarily yield an unambiguous, minimally scoped
correction.

These are observed behaviors under the tested prompts and input presentations,
not a claim that the model universally cannot proofread or write.

## Reproduced weaknesses

- **Missed word-level defect:** the full v29 critic with continuous prose plus
  its evidence catalog passed “She checked the the delivery number again.”
  without a finding in **3/3** trials, replicated **3/3** in a fresh reference
  batch. A general proofreading instruction recovered detection and the
  one-word recommendation in **3/3** paired trials.
- **False required revision:** in the latest excerpt comparison, both
  instructions rejected the valid “He passed her her mittens.” in **3/3** trials
  each. Recipient and possession are different grammatical roles. The previous
  instruction made two grammar accusations and one mandatory style rephrase;
  the minimal-repair candidate made three grammar accusations.
- **Contradictory repair:** for “He passed her her her mittens.” the candidate
  said to remove **two** occurrences while printing “He passed her her mittens.”
  in **3/3** trials. That result requires **one** deletion.
- **Overediting:** the candidate failed all **3/3** minimal-repair checks for
  “Leah knew that that that key opened the greenhouse.” Two recommendations
  contradicted their counts; one consistently removed two words when one
  deletion would preserve the valid construction.
- **Calibration:** local duplication sometimes received a prose score of 2/5
  despite otherwise positive assessment. Exact numeric scores have not been
  human-adjudicated; mandatory repair, repair size and broader craft quality
  must remain separate.

The latest 84-response comparison had **84/84 structurally valid responses**.
Minimal recommendations were **17/21** for the previous instruction and **15/21**
for the candidate. No word repairs were executed in that comparison.

Counterevidence matters: c05's sentence repetition was detected **3/3** with
continuous prose; an actual bounded writer/re-critic test removed only the two
duplicate sentences **3/3**, preserved all other prose byte-for-byte, and passed
fresh review **3/3**. The problem is not a universal inability to repair repetition.

## Reproduction scope and eventual acceptance checks

The September 11 excerpt comparison used `gemma4:31b-cloud`, requested seeds
19105/29105/39105, temperature 0.2, top-p 0.95 and thinking disabled. Matched arms
shared passages, evidence, schema and settings; only the frozen instruction
addition differed. These are not bare-chat prompts or full production runs.

When resumed, require valid grammatical/expressive repetition to remain intact,
each definite error to receive the smallest sufficient correction, and stated
counts to agree with exact before/after spans. Test actual patches and fresh
re-review without unrelated text changes, plus new human-reviewed controls and
full-critic regressions. Do not use unconditional repeated-word deletion.

Detailed scores, label history and source receipts:
[31B evaluation register](../benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md).
No implementation or additional diagnostic run is requested by this issue draft.

