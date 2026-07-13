# Open Hollywood

Open Hollywood is a local-first agentic story studio that turns a user premise
into an approved story blueprint and then autonomously produces a versioned,
evaluated, properly formatted work through a durable specialist-agent workflow.

## Project status

The legacy scene-execution prototype is preserved on the
`openHollywood-legacy` branch and at the immutable `legacy-v2-final` tag. The
active branch is establishing the foundation for the complete rewrite; no new
application runtime exists yet.

The v0.1 target is deliberately narrow: short prose fiction, local-first
storage, optional local/cloud/hybrid inference, and one mandatory story
blueprint approval before autonomous drafting.

## Source of truth

- [`open_hollywood_future.md`](open_hollywood_future.md) describes the product
  vision and the distinction between Open Hollywood and SammyAI.
- [`open_hollywood_bible/`](open_hollywood_bible/) contains the accepted product,
  architecture, workflow, evaluation, and UI guidance.
- [`open_hollywood_bible/step_by_step_implementation.md`](open_hollywood_bible/step_by_step_implementation.md)
  is the authoritative implementation progress tracker.
- [`docs/adr/`](docs/adr/) records accepted architecture decisions.

## Toolchain

- Python 3.13
- uv 0.11.28+
- Node.js 24 LTS
- pnpm 11.12.0+

Versions are pinned in `.python-version`, `.node-version`, `pyproject.toml`,
and `package.json` where appropriate.

## Repository layout

```text
apps/          Deployable API, worker, web, and desktop applications
engine/        Provider-neutral creative workflow and domain engine
packages/      Shared TypeScript contracts and UI components
migrations/    Database migrations
tests/         Cross-package, integration, evaluation, and legacy fixtures
docs/          Architecture decisions and technical documentation
images/        Open Hollywood brand assets
```

## Development

The repository is not ready to run an application yet. Foundation validation:

```powershell
node --version
pnpm --version
uv --version
py -3.13 --version
```

Application setup and run commands will be added with implementation step 3.

## License

Open Hollywood is available under the [MIT License](LICENSE). Contributions,
forks, experimentation, and derivative projects are welcome under its terms.
