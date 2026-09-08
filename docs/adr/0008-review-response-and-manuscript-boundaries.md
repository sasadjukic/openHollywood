# ADR 0008: Separate review-response repair from manuscript revision

- Status: Accepted
- Date: 2026-09-08

## Context

The v26 canary completed 3/9 runnable cases versus v25's 6/9. All five Local
first drafts were byte-identical to v25, but the new exact-quotation viewpoint
audit failed across every runnable case. Local 002 classified its own reviewer
metadata error as a blocking manuscript defect. Local 003 retained an unsupported
continuity allegation and a likely false critic blocker; the latter correctly
prevented terminal adjudication, but the final error concealed that interaction.

## Decision

Retain v26's immutable Bible-history fix, registered terminal adjudication,
recurrence guard, diagnostics, and pinned baseline tooling. Keep the writer,
mandatory approval, profile routing, revision allowance, and call budgets intact.

An aligned viewpoint review needs only a status, not evidence proving an absence
of violations. Actual violations select exact application-provided draft handles
and a typed narrative breach involving a different character. The approved style
remains authoritative; a focal-character assignment does not forbid that
character's interiority or imply external-camera narration. Applicability is
application-owned, including the existing single-character fallback.

There is one validated viewpoint route. Reviewer-format diagnostics and rejected
values are not replayed as story evidence; the bounded repair receives structural
locations and instructions to repair the review only. It never receives authority
to turn a schema error into a manuscript violation. Model judgments can still be
wrong: typed fields do not prove semantic correctness.

Continuity rechecks and adjudication receive a first-allegation ledger binding
the original report, assertion, evidence, and selected canonical scope. The
original requested repair is explicitly not canon. This does not add redundant
model-authored certificates or pretend to deterministically infer semantic
incompatibility. The independent terminal adjudicator remains limited by ADR 0007.

Terminal errors expose both review gates, immutable critic references and issue
indexes, and the adjudication eligibility reason. Checkpoints remain reference-
and-counter-only. A completed adjudication is explicitly remembered within a
scene and reset when the next scene begins.

New runs use graph v7 / prompt v27, although the repairs are developed on the
existing v26 development branch. No old run or checkpoint is retagged. No SQL
migration is needed.

## Verification and promotion

Offline tests cover response-versus-story separation, aligned and genuine
viewpoint cases, exact evidence handles, fixed original allegations, combined
terminal blockers, and protected Bible history. Simulated decisions are not live
model-conformance or semantic-quality evidence.

Opt-in isolated critic/Bible probes reconstruct exact historical artifact inputs,
verify their hashes, and use the current production validators and Bible reducer.
They allow at most two calls, retain original model/seed/per-call budgets, require
explicit Cloud opt-in, and write only new diagnostic directories. Source canaries
are read-only, and probe results cannot count as canary completions or human reviews.

Run the predeclared probes before a separately authorized fresh 6-Local/4-Cloud
canary. Keep v23/v25 as baselines until matched completion, scene coverage, repeat
evidence, and blind quality review justify replacement.
