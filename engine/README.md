# Creative engine

Provider-neutral Python domain and workflow engine. Its future source package
will be named `open_hollywood_engine` and will contain:

- `agents/`: registered specialist capabilities
- `artifacts/`: typed creative artifacts and version lineage
- `context/`: bounded context-packet construction
- `evaluations/`: rubrics and evaluation records
- `models/`: provider-neutral model gateway contracts
- `secrets/`: runtime-only credential resolution and leak guards
- `workflows/`: explicit durable graphs and subgraphs

This package must not depend on FastAPI, React, Tauri, or provider-specific
request/response types at its domain boundaries.
