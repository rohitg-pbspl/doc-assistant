# doc-assistant

Q&A over financial documents (annual reports, policy wordings, regulatory circulars) with page-level citations.

## Setup

Requires Python 3.12, [uv](https://docs.astral.sh/uv/) and Docker.

```bash
cp .env.example .env        # adjust if needed
uv sync                     # create .venv and install dependencies
docker compose up -d        # start PostgreSQL (with pgvector)
```

## Common commands

```bash
uv run ruff check .         # lint
uv run ruff format .        # format
docker compose ps           # database status
docker compose exec db psql -U app -d doc_assistant   # psql shell
docker compose down         # stop (data kept in the pgdata volume)
```

## Docs

- [Database](docs/database.md): starting, stopping and inspecting PostgreSQL
