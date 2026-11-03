# Database (PostgreSQL via Docker Compose)

PostgreSQL 17 with pgvector runs as the `db` service in `docker-compose.yml`.
Credentials come from `.env` (copy from `.env.example`).

Run all commands from the project root.

## Start and stop

```bash
docker compose up -d        # start in the background
docker compose up -d --wait # start and wait until healthy
docker compose ps           # check status
docker compose stop         # pause the container (keeps it)
docker compose start        # resume a stopped container
docker compose down         # remove the container (data is kept)
docker compose down -v      # remove the container AND delete all data
```

## Inspect

```bash
docker compose logs -f db                              # follow logs
docker compose exec db psql -U app -d doc_assistant    # psql shell
```

## Try it out

Open a psql shell (see above), then run these in order.

### psql meta-commands

```sql
\l              -- list databases
\dt             -- list tables
\d notes        -- describe a table
\dx             -- list installed extensions
\x              -- toggle expanded output (one column per line)
\q              -- quit
```

### Create, read, update, delete

```sql
CREATE TABLE notes (
    id         SERIAL PRIMARY KEY,
    title      TEXT NOT NULL,
    body       TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO notes (title, body) VALUES
    ('Annual report', 'Revenue grew 12% year over year'),
    ('Policy wording', 'Claims must be filed within 30 days'),
    ('Circular', 'New KYC norms effective April');

SELECT * FROM notes;
SELECT id, title FROM notes WHERE body ILIKE '%claims%';
SELECT count(*) FROM notes;

UPDATE notes SET body = 'Revenue grew 14% year over year' WHERE id = 1;

DELETE FROM notes WHERE id = 3;
```

### pgvector (similarity search)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE items (
    id        SERIAL PRIMARY KEY,
    label     TEXT,
    embedding VECTOR(3)
);

INSERT INTO items (label, embedding) VALUES
    ('revenue', '[1, 0, 0]'),
    ('profit',  '[0.9, 0.1, 0]'),
    ('claims',  '[0, 1, 0]');

-- Nearest neighbours to [1, 0, 0] by cosine distance (<=>); smaller = more similar
SELECT label, embedding <=> '[1, 0, 0]' AS distance
FROM items
ORDER BY distance
LIMIT 2;
```

### Clean up

```sql
DROP TABLE notes;
DROP TABLE items;
```

## Notes

- Data lives in the `pgdata` volume, so `down` keeps it. Use `down -v` for a clean database.
- `restart: unless-stopped` brings the container back after a reboot, unless it was stopped or brought down.
