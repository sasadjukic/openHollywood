# Creative engine

Provider-neutral Python domain and workflow engine. The
`open_hollywood_engine` package contains:

- `agents/`: registered specialist capabilities
- `artifacts/`: typed creative artifacts and version lineage
- `context/`: bounded context-packet construction
- `evaluations/`: rubrics and evaluation records
- `models/`: provider-neutral model gateway contracts
- `rendering/`: deterministic Markdown/Fountain renderers and PDF/DOCX exporters
- `secrets/`: runtime-only credential resolution and leak guards
- `workflows/`: explicit durable graphs and subgraphs

This package must not depend on FastAPI, React, Tauri, or provider-specific
request/response types at its domain boundaries.

The current `ProseManuscript` contract accepts only three to eight complete
scenes with unique IDs and contiguous numbering. Markdown, PDF, and DOCX share
that exact source model. Fountain uses an independent typed screenplay element
model so the engine never infers script structure from prose. PDF and DOCX
exporters normalize document metadata and archive identifiers to produce
repeatable bytes for identical inputs.
