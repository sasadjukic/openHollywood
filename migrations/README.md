# Database migrations

Alembic owns every persisted schema change. Never edit an applied migration;
add a new one and keep it aligned with the SQLAlchemy metadata in
`apps/api/open_hollywood_api/persistence/`.

The database path comes from `OPEN_HOLLYWOOD_DB_PATH` and defaults to
`./data/open_hollywood.db`. From the repository root:

```powershell
uv run alembic upgrade head
uv run alembic current
uv run alembic downgrade -1
```

Generate a candidate migration after changing persistence metadata, then review
the generated upgrade and downgrade operations before committing it:

```powershell
uv run alembic revision --autogenerate -m "describe schema change"
```

The migration integration tests apply the complete chain to an isolated SQLite
database, compare the result with current SQLAlchemy metadata, and exercise the
downgrade path.
