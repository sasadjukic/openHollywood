# Q013 read-only publication for The Impossible Card

Critique v3 and draft v1 each open the same saved Q013 assessment. The first selection creates a 15-file bundle. Opening it from the other selection returns `reused` and preserves every byte and modification time. Starting from the draft produces the same bundle as starting from the critique. [Operator commands](../../README.md#q013-publication) · [Publisher](../../scripts/publish_saved_review_completion.py)

## Publication and accounting

| First selection | Second selection | Result | Manifest SHA-256 |
| --- | --- | --- | --- |
| Critique v3 | Draft v1 | Created, then reused | `aa4d3d4563c03592748eae990449888697681b4611715cc70e0bcde589df24fc` |
| Draft v1 | Critique v3 | Created, then reused | `aa4d3d4563c03592748eae990449888697681b4611715cc70e0bcde589df24fc` |

Both bundles bind the exact critique version `ca5915a5-5b82-4bad-82ce-e5c31a519dc0` and draft version `c3689bce-e108-4761-bafe-390f6e7ea1b3`. The critique owns request manifest `59ad7cd95b4d22e3541e3d7f190d30c37ea8132b02e4e6c76a7d5dec5fce170f`. Both lookups retain delivery ID `q013-ee5fe8bc94d4a374ff9594204b425182449edac3698feee431f5ca0809a29cb5`.

The input-count slot measured 62,835 tokens. One generation usage record accounts for **62,835 input and 427 output tokens**, including 255 reasoning tokens and zero cached input tokens. Actual billing is unknown. The retained score and rendered evidence match the earlier audit byte for byte. The operator separately scored whole-claim correctness and draft-evidence coverage as passes. The application records its own semantic and craft judgments as `unassessed`. [Original scores](q013-sol-high-smoke-results-2026-11-21.md) · [Source and delivery audit](q013-observed-completion-audit-2026-11-21.md)

## Rejection controls

The local archive replay recorded 16 rejection outcomes. For rejected destinations it checked that a fresh path stayed absent or that every existing member retained its bytes and modification time.

| Control | Observed result |
| --- | --- |
| Select the genuine adjacent critique v2 or draft v2, or pass either exact selection to the other registration | Refused with the selected registration's `wrong_selection` reason. |
| Supply an injected journal, the other registration's journal, or a byte-identical journal copy at a new path | Refused with `q013_unsupported_journal`. The original closed journal is the authority. |
| Bind Q008's genuine receipt or account for it under either Q013 selection | Both native operations rejected the receipt with `mixed_work_scope`. |
| Publish inside the other registration's protected source root | Refused with `completion_protected_path`. |
| Publish either case over the other's bundle, or reuse an altered Q013 bundle | Refused with `completion_output_conflict`. |

All 57 original files checked across the two captures retained their hashes and modification times. An independent native replay also verified Q013's pinned 29-member regression and its evidence render. [Receipt and exact-version verifier](../../scripts/verify_q013_selection_binding.py) · [Native completion verifier](../../scripts/verify_q013_observed_completion.py)

## Q008 compatibility

The original Q008 command and the shared command both reopened the historical publication without changing any member or modification time. A fresh draft-first Q008 export matched all 15 historical files, including manifest SHA-256 `efef8fc3348b3a5cfc3c9529e6e645d390685e5030c01d56b257eaa27631619d`. The existing consumer returned one Q008 assessment and one usage record when asked for both Q008 and both Q013 selections. Both Q013 lookups returned unavailable in that consumer. [Historical Q008 publication](q008-observed-publication-2026-11-21.md)

## Replay

The shared command accepts two fixed registrations, `q008` and `q013`. Each supplies its own sealed source, smoke auditor, registered journal and score digests. The publisher reconstructs the original critique request, verifies delivery and known usage, and rechecks its sources before committing the manifest or accepting an existing destination. The original Q008 command remains available. [Publication decision](../adr/0067-observed-saved-review-publication.md) · [Portable regression tests](../../tests/api/test_q008_publisher.py)

The private replay and its two bundles are under `data/diagnostics/q013-publication-2026-11-22/`. Its `qualification.json` records both creation orders, the 16 controls, the historical Q008 manifest and the source-integrity check. From the repository root, the following command exercises the operator entry points using saved data and blocks outbound connections.

```powershell
.venv/Scripts/python.exe data/diagnostics/q013-publication-2026-11-22/qualify.py
```

A second replay reused both existing Q013 bundles from both selectors and reproduced all 16 refusals. All 33 focused tests passed, including 22 publisher cases across the two registrations and 11 Q008 consumer cases. On disposable journals the tests also rejected missing closure, an interrupted generation, missing usage, changed terminal bytes, the draft-selected request and an altered operator score. A source change during writing left the partial output without a publication manifest.

All 2,662 distinct Python tests passed with zero skips. Ruff lint, formatting and strict mypy passed across 351 Python files. Frontend formatting, lint, type checks, all 44 web tests and the production builds passed. The replay made zero provider calls. Step 19 remains in progress and the full workflow canary remains on hold.

## Recommended next step

Rehearse read-only consumer lookup on the two pinned publications. Request Q013 through each exact selection, then mix and repeat the four Q008/Q013 selectors in both orders. Expect two assessments, each with its original score labels, and two usage records totaling 121,729 input and 772 output tokens. Switch to an adjacent version and refresh after damaging a disposable Q013 bundle. Q013 should become unavailable, its previous usage should clear, and a simultaneous exact Q008 lookup should still report 58,894 input and 345 output tokens. This local rehearsal can establish the consumer behavior before an inspector change or further inference.
