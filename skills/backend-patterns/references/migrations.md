# Migration gotchas (fleet-wide, each cost a blocked or broken deploy)

## `db:push` hangs forever on its confirmation prompt (drizzle-kit 0.24)

`db:push` asks for interactive confirmation on a destructive/ambiguous change and reads the
answer from `/dev/tty`, **not stdin** - so `printf 'y\n' | docker compose run -T ... db:push`
hangs exactly the same way. It blocked two schema changes in one Caudal session (a unique
constraint, and `int` → `int[]`).

**What worked:** apply the DDL by hand through `psql`, using EXACTLY the name and definition
`schema.ts` declares. A later `db:push` then introspects, sees no difference, and never asks.
Reuse the name drizzle would generate (`<table>_<cols>_uq`, or whatever you passed to
`unique("...")`) or the next push will try to create it again. (caudal, 2026-09-01)

`drizzle-kit generate` hangs the SAME way, not just `db:push`. Dropping one column while adding
another to the same table makes it ask "is `rir` created or renamed from `rpe`?" on `/dev/tty`, so
`docker compose exec -T ... db:generate` hangs with the question unanswerable. **Fix needs no TTY:
split into two unambiguous migrations** - generate once with the old column still present (pure
additions), then remove it and generate again (pure drop). Each is unambiguous, so neither prompts.
(personal-dash, 2026-09-07)

## The shared dev/prod database makes every migration a two-part change

On this fleet dev and prod containers share ONE Postgres per app. Applying a migration while
prod still runs the OLD code leaves prod incoherent until the redeploy - a silent landmine, not
an error. Two occurrences in one Caudal session:

- added the `auto_rules` unique constraint → old code still did a blind INSERT → 500 whenever a
  merchant was re-ruled
- converted `reminder_lead_days` to `int[]` → old code compared `number !== array` → payment
  reminders silently stopped firing, no error anywhere

**Rule: if you touch the schema of the shared DB, redeploy prod (web AND worker) in the SAME
turn.** Never end a turn with new DB + old code. Applies to every app whose dev and prod share a
Postgres - `loop` shares `loop-db-1` the same way. (caudal, 2026-09-01)

The subtlest direction of this is a column DROP, because a bare `db.select().from(table)` (no
column list) enumerates the columns in the TABLE DEFINITION OF THE BUILD THAT RUNS IT - so after
dev's migration drops `workout_sets.rpe`, prod's OLD code keeps issuing `SELECT ... rpe ...` and
500s on the missing column, silently, with dev fully green (tsc and tests can't see it - the SQL is
generated at runtime from the old schema object). **Guard before dropping any column on a shared DB:
`grep -rn "select()" | grep <table>`; if a bare select touches it, redeploy prod in the same turn or
defer the drop to the redeploy.** (personal-dash, 2026-09-07)

## The prod `runner` image cannot run `db:migrate`

The runner stage copies `node_modules` but NOT `db/migrations/` or `drizzle.config.ts` (only
`.next`, `public`, `package.json`), so drizzle-kit has nothing to apply - and migrations are not
auto-applied on boot (CMD is just `npm run start`).

**To migrate prod**, run the postgres-js migrator in a throwaway container on the compose network
with the repo mounted (host `node_modules` works if the image is glibc - `node:22.23.1-bookworm-slim`, not
alpine):

```bash
DBURL=$(docker exec glow-web-prod-1 sh -c 'echo $DATABASE_URL')
docker run --rm --network glow_default -e DATABASE_URL="$DBURL" \
  -v "$PWD":/app -w /app node:22.23.1-bookworm-slim node -e "<postgres-js migrate>"
```

It applies only pending migrations (drizzle skips what is already in
`drizzle.__drizzle_migrations`) and keeps the journal consistent. **A raw `psql` ALTER is the
wrong move here** - it does not record the journal, so the next `migrate` re-runs it and errors.
Always migrate BEFORE deploying code that reads the new column, or the new build 500s on a
missing column. Verify after: journal row count == number of migration files, and the column
exists. Fleet-wide shape (recall/triage/glow/loop share this runner). (glow, 2026-08-12)

## drizzle-kit traps (personal-dash, 2026-09-12/14)

- **A column a VIEW depends on: drop the view FIRST, by hand.** A `pgView(...).existing()` is
  unmanaged, so `db:generate` emits `DROP COLUMN` but no view drop and the migration rolls back with
  `cannot drop column ... because view <v> depends on it`. Put `DROP VIEW IF EXISTS "<v>";` as the
  migration's FIRST statement (recreate it after if still needed).
- **`generate` hangs under `exec -T` (no TTY)** on the create-vs-rename prompt. Split the change into
  two generates (drop-only, then add-only) so no prompt is asked. Migration files come out
  root-owned: edit them through the container, not host `sed`.
- **drizzle-orm 0.38 pg-core `unique()` has no `.nullsNotDistinct()`** (only mysql/singlestore
  builds ship it). Write `UNIQUE NULLS NOT DISTINCT` as raw SQL in the migration, or accept
  nulls-distinct and guard the null case in app logic.
- **Big re-architecture on a shared dev+prod DB, near-zero downtime, in this order:** (1) new code
  uses column-specific `db.select({...})`, never bare `select()`; (2) additive migration + backfill;
  (3) `--profile prod up -d --build` so prod runs the new code while old columns still exist;
  (4) only THEN drop/tighten. Back up (NAS + scratchpad) before every data step. The auto-mode Bash
  classifier blocks live-DB writes (`psql -f`), so the user runs that step via `!`.

## Hand-check a generated migration before anything boots (Agent Factory, 2026-10)

- **A drizzle-kit sqlite table-recreate** (a column made nullable plus a new column) can SELECT the new column from the
  old table in its INSERT copy, which fails at boot. Remove the new column from both lists of that INSERT by hand, then
  dry-run on a `.backup()` copy of the real database.
- **Never append SQL to a migration the dev server already applied:** dev never runs the addition while prod gets the
  whole file. Write the full migration (seeds included) before anything boots, or add a separate data migration with
  `drizzle-kit generate --custom`.
