# Technical documentation

This directory contains implementation-facing documentation for the rewrite.

- `adr/` contains accepted Architecture Decision Records.
- Product and experience requirements live in `open_hollywood_bible/` at the
  repository root.
- The original product vision lives in `open_hollywood_future.md`.

Architecture records are append-only decisions. If a decision changes, add a
new ADR that supersedes the old one rather than rewriting history.

## Current model evaluation references

- [New-chat handoff: 31B Cloud production, three four-story batches](handoffs/31b-cloud-production-new-chat-2026-09-11.md)
- [September 11 testing direction and E4B retrospective](benchmark_reports/model-testing-direction-2026-09-11.md)
- [31B creative-writing evaluation register](benchmark_reports/gemma4-31b-evaluation-register-2026-09-11.md)
- [Deferred critic/repair issue draft](issue_drafts/gemma4-31b-critic-repair-follow-up.md)

These records change evaluation priorities, not the durable graph architecture.
Historical canary reports and diagnostic judgments remain preserved.
