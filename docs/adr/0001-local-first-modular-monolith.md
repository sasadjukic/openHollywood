# ADR 0001: Local-first modular monolith

- Status: Accepted
- Date: 2026-07-13

## Context

Open Hollywood must work with local Ollama models, keep early development
simple, and support a future desktop distribution without prematurely building
hosted multi-user infrastructure.

## Decision

Build a local-first modular monolith with four logical parts in one repository:

1. React/TypeScript web client
2. FastAPI API
3. Python workflow worker
4. Provider-neutral creative engine

The browser-based vertical slice comes first. Tauri packages the stable system
later. Cloud inference is optional and does not make project storage hosted.

## Consequences

- Local development and Ollama access remain straightforward.
- Module boundaries must be enforced in code rather than through services.
- Authentication, multi-tenancy, billing, and cloud synchronization are out of
  scope for v0.1.
- API and worker processes may later be packaged as desktop sidecars.
