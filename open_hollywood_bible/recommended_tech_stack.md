# Recommended technology stack

## Architecture recommendation

Build a local-first modular monolith with three deployable parts from one repository:

1. React desktop/web client
2. FastAPI API service
3. Python workflow worker

Package it as a desktop application once the browser-based vertical slice is reliable.

This keeps the product simple to develop while allowing long-running work to survive UI refreshes, application restarts, and human approval delays.

## Stack

| Layer | Choice | Reason |
|---|---|---|
| UI | React + TypeScript + Vite | Excellent interactive UI ecosystem and straightforward Tauri integration |
| Components | Tailwind CSS + Radix primitives/shadcn-style components | Accessible, customizable UI without fighting a rigid visual system |
| Client data | TanStack Query | Server-state caching, retries, invalidation, optimistic interactions |
| Small UI state | Zustand | Appropriate for workspace panels and transient UI state |
| Desktop shell | Tauri 2 | Cross-platform shell, filesystem integration, small footprint, secure secret options |
| API | FastAPI + Pydantic v2 | Preserves the strongest part of the current Python stack |
| Agent runtime | LangGraph `StateGraph` | Durable graphs, subgraphs, checkpoints, interrupts, replay |
| Model gateway | LiteLLM Python SDK behind an internal adapter | Unified provider calls, routing, fallback, usage and cost handling |
| Local inference | Ollama | Existing integration and local model discovery |
| ORM/migrations | SQLAlchemy 2 + Alembic | Explicit domain persistence and migration support |
| Desktop database | SQLite | Zero-configuration local persistence |
| Hosted database | PostgreSQL | Production concurrency, JSONB, full-text search, durable checkpoints |
| Streaming | Server-Sent Events plus REST commands | Simple resumable one-way run/event streaming |
| File storage | Local project directory; S3-compatible storage when hosted | Keeps manuscripts and attachments separate from workflow state |
| Validation | JSON Schema generated from Pydantic models | Provider-independent structured artifacts |
| Testing | pytest, Vitest, React Testing Library, Playwright | Unit, integration, UI, and end-to-end coverage |
| Observability | OpenTelemetry plus an optional self-hosted LLM trace viewer | Traces without forcing story content into a third-party service |
| Packaging | Tauri sidecar for the Python service/worker | Desktop distribution without requiring users to configure Python |

Tauri supports bundling external binaries as sidecars, which makes a packaged Python service feasible. Its Stronghold plugin is available for secret storage. [Tauri sidecar documentation](https://v2.tauri.app/develop/sidecar/), [Stronghold reference](https://tauri.app/reference/javascript/stronghold/).

### Why not rewrite everything in TypeScript?

A full TypeScript stack would simplify language boundaries, but the Python ecosystem remains a better fit for agent orchestration, model evaluation, document processing, structured validation, and the current working code.

UI/UX quality comes primarily from React architecture and product design; it does not require the orchestration engine to be JavaScript.

### Why not keep the existing HTML/CSS/JavaScript frontend?

The future workspace requires:

- Multiple persistent projects
- Nested story artifacts
- Streaming agent activity
- Approval states
- Version history and diffs
- Run controls
- Model matrices
- Search
- Responsive panels
- Long-lived client state

Implementing this reliably in one imperative JavaScript file would become expensive and brittle.

### Why LangGraph rather than a fully autonomous agent framework?

Open Hollywood needs explicit creative stages, recoverability, approval points, and inspectable state. LangGraph supports persisted checkpoints, subgraphs, parallel nodes, fault recovery, and state history. Its documentation specifically recommends per-invocation subgraphs for independent specialist-agent tasks. [LangGraph subgraphs](https://docs.langchain.com/oss/python/langgraph/use-subgraphs).

Use LangGraph as the workflow runtime, but keep Open Hollywood’s domain objects independent of LangGraph so the framework could be replaced later.

### Why LiteLLM?

The application needs local/cloud/hybrid model experiments and role-specific configuration. LiteLLM provides a normalized interface for many providers, retry/fallback routing, cost tracking, and budgets. [LiteLLM documentation](https://docs.litellm.ai/).

Wrap it in your own `ModelGateway` interface rather than allowing provider-specific types to leak throughout the application.