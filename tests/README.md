# Tests

Cross-package tests, integration tests, evaluation fixtures, failure-injection
tests, and end-to-end scenarios live here. Package-local unit tests may remain
next to their implementation when that improves ownership.

`fixtures/legacy/` preserves the useful behavior contract from the final legacy
prototype without restoring its application code. The dialogue-subgraph
regression suite consumes `director_flow.json` to verify the preserved call
order, round cardinality, and termination invariants.

`workflows/test_scene_production.py` verifies ordered scene production,
embedded dialogue passes, exact-version critique targets, bounded revision,
hard-limit dispositions, isolated retries, incomplete-output rejection, and
content-free checkpoint state.

The [Step 19 failure-path matrix](../docs/verification/step-19-failure-paths-2026-09-19.md)
maps injected provider faults, process/cancellation boundaries and report-write
failures to their regression tests. It also identifies the existing budget,
adjudication and isolation checks and the limits of synthetic verification.
