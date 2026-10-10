# Severity-bound restatements and precise critic retries: v44

Date: 2026-10-10. Production contract v44 / graph v9.

**Implementation, local checks and all five approved live probes are complete.
Four probes produced valid reviews; the unchanged draft failed both attempts.**
Precise retry guidance reached the model and both missing boundary links were
corrected, but reviewer reliability and semantic deduplication remain unresolved.
See [ADR 0029](../adr/0029-severity-bound-restatements-and-precise-retries.md).

## Changes and scope

The [v43 report](eligible-repair-links-v43-2026-10-10.md) isolated three structural
problems in its unchanged-draft control: a nonblocking craft issue with an invalid
assignment reference, an omitted boundary link and category spelling drift.

v44 makes restatement choices conditional on severity. Note, minor and major
issues allow only null. Blocking issues retain null for independent craft and
exact applicable references for declared assignment repetitions. Validation
continues to require a reported blocking target. It never changes the model's
severity, category or links to make a response pass.

The existing structural retry now receives precise application facts for these
link failures. Its directives identify allowed references, exact original repair
category/severity, complete consolidated routes, missing routes and competing
owners. When several independently observable faults exist, they can reach the
same retry instead of being masked by the first rejection.

The implementation preserves the boundary between review errors and story
defects. Rejected descriptions, advice and assessments do not enter the retry.
Original categories and severities are retrieved from exact input repair tests.
Hints are bound to the candidate version, typed, bounded and checked again before
use. The application reuses its actual hard-route validators for the diagnostic
projection; this projection never becomes a canonical critique. A failed review
remains failed until a new model response satisfies the normal validator.

Valid responses bypass this diagnostic pass. No writer instructions, critic
system instructions, story context, canonical fields, database migrations,
provider SDKs, model-call allowances or retry limits change. Critic retry policy
is 11; other specialist retry policies remain 10.

## Local verification

The 22 new regression cases cover severity alternatives in local/cloud schemas,
nonblocking null requirements, exact reported target choices, category drift,
partial links, duplicate references, met-link errors, competing owners, malformed
and stale hints, bounded diagnostics and secret redaction.

A persisted workflow test injects both a bad restatement and a missing boundary
link. Both corrections reach the existing review retry. The candidate and input
artifacts are identical across attempts, the failed invocation has no canonical
output, and writer count remains unchanged from the underlying revision fixture.
Its durable replay makes no additional model calls.

All **806 Python tests** pass, including the 92 focused cases. Ruff lint/format,
strict mypy over 180 files, frontend format/lint/type checks, 11 frontend tests
and the production build pass.

The first frontend test invocation timed out starting the Vitest forks worker
and ran no tests. The same `pnpm test` command then passed all 11 tests when run
alone, without source/configuration changes or a timeout increase. The startup
failure's cause is not established; the passing rerun is not claimed as a fix.
Node v24.18.0 and pnpm 11.12.0 match the repository requirements.

## Unmodified v43 response replay

All six saved raw responses are replayed locally without annotating or rewriting
them:

| Response | v44 offline outcome |
|---|---|
| Unchanged draft, attempt 1 | Still rejected; retry receives null-only restatement choice and missing boundary route |
| Unchanged draft, attempt 2 | Still rejected; retry also receives exact `dramatic_tension` / `major` original identity |
| Saved repair 19102 | Identical canonical PASS |
| Saved repair 19103 | Identical canonical PASS |
| Saved repair 19104 | Identical canonical PASS; interpretation remains disputed |
| Missing-turn control | Identical canonical REVISE with one turn finding |

The two reconstructed retry requests are offline evidence only and have not
been sent. They include two and three precise directives respectively. This
confirms that the actual v43 failures reach the new mechanism, not that a model
will obey it. No saved failure is reclassified as a valid review.

## Frozen five-case comparison

| Case | Predeclared observation |
|---|---|
| Unchanged draft, 19102 | Valid REVISE, retaining two original repairs once each with compatible complete links |
| Saved repair 19102 | Valid PASS; original checks met with empty links |
| Saved repair 19103 | Valid PASS; original outcome met with empty links |
| Saved repair 19104 | Inspect match/authorship interpretation without forcing a verdict |
| Missing-turn control, 19103 | Original outcome met; one independent turn finding and one new repair target |

The exact private OH-V01-002 inputs, saved revisions, synthetic explicit endpoint,
seeds, settings and per-call budgets are identical to v43. Initial system messages
are identical. Removing only the new issue severity branches reproduces every
old initial user payload exactly; each grows by **162 characters**. Conditional
retry requests use the new precise guidance only following structural failure.

The prepared allowance is five critic probes, at most ten calls: one initial
call and at most one structural retry per case. No writer calls, semantic rerolls,
second revisions or full-story generation are included. Recorded October 8 rates
of USD 0.14/M input and USD 0.40/M output, with 24,000 input / 8,000 output tokens
per call, give a maximum estimate of **USD 0.06560**. Actual charges remain
unknown. Destination: the existing Ollama Cloud Gemma4 deployment through the
local Ollama daemon. The user explicitly authorized this revised private payload
set: "Yes, run the five v44 probes". The campaign is finished; no additional
requests were made beyond those five probes and their permitted retries.

## Live results

| Case | Calls | Final result | Interpretation |
|---|---:|---|---|
| Unchanged draft, 19102 | 2 | Failed validation | Retry added the missing boundary link, then introduced an invalid major-issue restatement reference |
| Saved repair 19102 | 2 | PASS; zero issues | Retry corrected malformed evidence handles; both original repairs met |
| Saved repair 19103 | 1 | PASS; zero issues | Original outcome repair met |
| Saved repair 19104 | 2 | REVISE; two issues, one new repair target | Link errors corrected, but a generic pacing issue repeats the endpoint finding |
| Missing-turn control, 19103 | 1 | REVISE; one issue, one new repair target | Original outcome met; missing turning point remains independently reported |

The eight calls used **100,171 input tokens and 8,463 output tokens**, for an
estimate of **USD 0.01740914** at the frozen October 8 rates. This is below the
ten-call / USD 0.06560 authorization. Actual charges remain unknown. No writer,
full-story or additional sampling calls occurred.

### What the retries actually did

The unchanged draft's first response correctly identified the endpoint overrun
but linked its original outcome repair only to `assignment:outcome`, omitting
the consolidated `boundary` route. Its generic issue list was empty; there was
no severity/restatement error on that attempt. The retry received the exact
missing route, original category and severity, and added the required link.
It also introduced a major `dramatic_tension` issue with
`assignment_finding_ref: "outcome"`. That violates the null-only rule for
nonblocking issues. The second response remains rejected and creates no
canonical review. This is a new error during regeneration, not evidence that
the supplied missing-link directive was ignored.

Two labeled offline counterfactuals isolate the failures: adding only `boundary`
to attempt 1, or changing only the major issue's reference to null in attempt 2,
produces REVISE with exactly the two original repairs and no new repair target.
These manually edited copies are diagnostic evidence only. They do not convert
the failed live probe into a success or authorize automatic response repair.

Repair 19102 initially shortened the zero-padded evidence handles (for example,
`draft_evidence_046_...` instead of the supplied `draft_evidence_0046_...`). The
existing evidence-location guidance was sufficient for a valid retry. This is
recovery through the existing evidence mechanism, not proof of the new link
guidance's effectiveness.

Repair 19104 initially had both a major issue with a non-null reference and an
omitted boundary link. Its retry received both precise directives, changed the
reference to null, and linked both assignment and boundary routes to the original
repair. That demonstrates one live structural recovery through the new guidance.
However, the generic major issue was relabeled `Plot Pacing` and retained: its
claim is that establishing a handwriting match consumes the next scene's turn,
and its remedy is to leave verification inconclusive. In manual assessment,
this repeats the same endpoint defect already represented by the original
blocking outcome repair. Null marks declared independence; it does not prove
semantic independence. The valid review therefore produces two canonical issues
and one additional repair target for that repeated allegation.

The 19104 verdict also changed from v43 PASS to v44 REVISE. Its cited prose says
the handwriting samples "seemed identical" and describes "ambiguous authenticity". The new
review interprets this as an established match, while the earlier review treated
the uncertainty as sufficient. Both v44 attempts use the overrun interpretation,
so this verdict change precedes the retry. Neither schema validity nor this
single changed judgment resolves the ambiguity. The comparison cannot attribute
the change to one instruction or establish improved narrative judgment.

### Recommended next slice

Address the distinction between a repeated assignment allegation and independent
craft criticism. A null reference plus a different category or severity must not
be treated as proof that the defect is different. Develop a compact explicit
same-defect/independent-claim comparison for the existing critic, preserving
independent tension criticism even when it cites the same passage. In particular,
the two historical repairs in the unchanged control must remain separate.

Exercise that distinction locally with the saved 19104 duplicate and independent
craft controls before another live campaign. Preserve the strict validation and
single retry limit; do not promote severity, discard all major issues, or silently
clear invalid references. The unchanged probe also shows that a full replacement
retry can introduce a new error elsewhere, which remains a reliability limit.

## Evidence and limits

Private evidence is retained under the ignored directory
`data/diagnostics/restatement-retry-v44-2026-10-10/`: `experiment.py`, `plan.json`,
the five `prepared/*.json` requests, `offline-replays.json`,
`offline-retry-requests.json`, `local-verification.json`, all eight request/raw
response/result records under `live/`, `assess.py`, `assessment.json`,
`diagnose.py`, `offline-diagnosis.json` and `postcheck.json`. The pre-live
verification file retains its historical pending-approval status; the postcheck
records the subsequent authorization and completed run. The plan freezes exact
code, prior evidence and request hashes. Source commit:
`261c54a082b222ebc4c21e1888304eb013c15727`.
Candidate file hashes identify this implementation.

The local assessment reconstructed every request, including the three conditional
retry packets, and reproduced valid and failed responses, failure evidence,
boundary audits and original repair lineage. All frozen hashes remain intact.

The completed v33 repeat-3 source snapshot retains SHA-256
`71618ce4d66ffd3b8ecc46fa4d034105b4e59aa5a80946b5364272b87caeafb2`.
Canonical stories, approved Blueprints, sealed benchmarks and prior evidence are
unchanged. The archived-source reconstruction retains v43's explicit null wire
metadata adapter; exact canonical inputs are asserted equal to the saved inputs.

This is a small one-model comparison of two coordinated protocol changes, with
one seed per case. It does not isolate causal effects. Three initial responses
failed; two recovered structurally, but one recovered review still contains a
semantic duplicate. The overall valid-review count remains four of five, as in
v43, with eight calls rather than six. This does not establish a reliability or
cost improvement. Diagnostics concern compatibility and ownership, not whether
two allegations mean the same thing. Large or invalid metadata can receive only
generic guidance under the fixed bounds. The model may still omit or misjudge
defects, and the handwriting-match/authorship ambiguity remains unresolved.

Full-story recovery, broader technical repeatability, human preference and cost
acceptance remain outstanding. **Step 19 remains IN PROGRESS; Step 20 is NOT
STARTED.**
