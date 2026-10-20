# Isolated test database recipes

## Postgres in a docker-compose project (a sibling database in the same server)

```bash
DB=db; U=<user>; APP=<dbname>            # compose service, db user, real db name
docker compose exec -T $DB psql -U $U -d postgres -c "CREATE DATABASE ${APP}_test;"
URL=$(docker compose exec -T web printenv DATABASE_URL | tr -d '\r'); TEST_URL="${URL%/$APP}/${APP}_test"
# Schema: clone it from the real DB (default - no app tooling, no node_modules, no prompts):
docker compose exec -T $DB sh -c "pg_dump -U $U --schema-only --no-owner $APP | psql -U $U -d ${APP}_test -q"
# Fallback ONLY if you need the migration tool itself: `docker compose run --rm --no-deps -e
# DATABASE_URL="$TEST_URL" web <schema-cmd>`. It HANGS silently in any compose that mounts
# `- /app/node_modules` as an anonymous volume (every app here): `run` gets a fresh EMPTY volume,
# so the binary is missing and it looks like a drizzle prompt.
docker compose run --rm --no-deps --name testapp -e DATABASE_URL="$TEST_URL" -p 3099:3000 web <run-cmd> &
# 3099 is the reserved scratch port in the port registry (fleet-ops).
# ... drive the flow against :3099, then assert:
docker compose exec -T $DB psql -U $U -d ${APP}_test -c "select …"
docker stop testapp
docker compose exec -T $DB psql -U $U -d postgres -c "DROP DATABASE ${APP}_test WITH (FORCE);"
```

## Realistic-data variant (migration or data-shape testing)

Restore the latest dump into the scratch database instead of creating it empty, apply the change, and
verify counts. On this box a weekly `restore-test.sh` (dev-system) already does this into a throwaway
Postgres, so reuse it.

## Other stacks (same four steps, different primitives)

- **MySQL/MariaDB:** `CREATE DATABASE app_test;`, override `DATABASE_URL`/`MYSQL_DATABASE`, assert with
  `mysql -e`, then `DROP DATABASE app_test;`.
- **SQLite:** point the app at a temp file (`DATABASE_URL=file:/tmp/app_test.db`), run migrations, drive,
  and `rm` the file. It is trivially isolated, with no server needed.
- **Managed or cloud DB (RDS, Neon, Supabase, Turso):** create a **branch** or a throwaway database or
  schema, never a shared instance, and delete the branch afterwards. Prefer a local container for tests
  if the managed branch is slow or costs money.
- **No compose, bare app:** run the app process with the connection env var overridden inline
  (`DATABASE_URL=… npm start`), on a spare port.

## Next server actions under vitest

Alias `next/cache` to a no-op stub in the integration config (`resolve.alias`), so you test the DATABASE
EFFECT without booting Next. Pair it with a disposable-Postgres harness (`scripts/test-db.sh`, its own
container on a dedicated port, and a guard that aborts unless `DATABASE_URL` contains the `_test`
database name).

## Related skills and the per-project shape

- `verify-ui-live` step 0b covers driving the write path through a browser (`chrome-devtools-axi` or a
  committed `e2e/*.e2e.py`) against the `:3099` scratch instance.
- `debugging` step 1 is the why: never fire a destructive path at real rows.
- Caudal (`~/projects/finance-proj/PLAN-demo.md`) keeps a parallel demo dataset (`caudal_demo`) built for
  exactly this: writes are real, the data is fake. It is the per-project shape of step 1 (isolate).
- The stack-agnostic technique works for Postgres, MySQL, SQLite and managed DBs, in docker or local; the
  fleet's own testing conventions live in the same `SKILL.md`.

## Teardown and login gotchas

- **Login seems to need data.** It usually does not: single-user apps often keep the password hash in an
  env var, so login works against the scratch DB with the same credentials.
- **`DROP DATABASE` blocks.** A still-open app connection holds it; stop the throwaway instance first, or
  drop `WITH (FORCE)` (Postgres), or kill the connections.
- **A stray row survives a failed teardown unnoticed.** Use fake, obvious ids that cannot collide with
  real ones and are greppable (`ZZTEST…`, `IE00TEST…`).
