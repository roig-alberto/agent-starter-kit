# Drizzle, SQL, money and dates

The detail behind the data rules in `SKILL.md`.

## Drizzle discipline

- One schema file (`db/schema.ts` / `lib/db/schema.ts`). Client: postgres.js pool
  (`max: 10`), `drizzle(client, { schema })`, throw if `DATABASE_URL` unset, cache on
  `globalThis` in non-prod so hot-reload doesn't leak connections (`db/index.ts` /
  `lib/db/index.ts`).
- **Three migration traps, each of which blocked or broke a deploy:** `db:push` hangs on its
  confirmation prompt and ignores piped stdin (it reads `/dev/tty`); the shared dev/prod database
  makes every schema change a two-part change - **redeploy prod in the SAME turn or prod runs new
  DB + old code**; and the prod `runner` image cannot run `db:migrate` at all (it has no
  `db/migrations/`). Recipes: `references/migrations.md`.
- **Migrations: commit them.** The correct pattern is Aro's - `npm run db:generate` →
  migration files committed under `db/migrations/` (0000-0020 + journal) → `db:migrate`
  applied in-container. Caudal's `db:push`-only workflow (no `drizzle/` folder on disk)
  is tracked drift: schema reproducibility rides on a live DB. Do not copy it into new
  apps; for schema changes on real data, follow additive order (add → backfill → switch
  reads → drop) with each step its own migration.
- **Apply migrations IN-CONTAINER; a host `npm run db:migrate` LIES** - `DATABASE_URL`
  points at the compose service (`…@db:5432/…`), unresolvable from the host, so the run
  prints `applying migrations…` and **exits 0 having applied nothing**. An inline
  `DATABASE_URL=…@127.0.0.1:5434…` does NOT help: **drizzle-kit auto-loads `.env` and
  overrides the inline var.** Winner: `docker compose -f docker-compose.dev.yml run --rm
  --no-deps web npm run db:migrate` (recall 2026-07-12; a table that "migrated" and never
  appeared).
- Postgres **major pinned to the dumps** (16 - `postgres:16.14-alpine` everywhere).

## postgres.js + drizzle bind traps - typecheck green, explode at QUERY time

Three separate sessions across recall (2026-07-11) and superhuman (2026-07-17, hit
3× in ONE session). `tsc` catches neither; unit tests don't either - an integration
fixture found them. **Rule: `sql\`\`` is for STRUCTURE; values go through drizzle operators.**

| Trap | Runtime error | Fix |
|---|---|---|
| a JS `Date` interpolated in a raw ``sql`…` `` | `ERR_INVALID_ARG_TYPE: The "string" argument … Received an instance of Date` | `gte(col, d)` / `lte(col, d)` / `and(...)` |
| `= ANY(${jsArray})` (binds the whole array as ONE param) | `malformed array literal` | `inArray(col, arr)` - or `inArray(sql\`lower(col)\`, arr)` |
| you genuinely need the array inside a raw correlated subquery | same | `sql.join(arr.map(x => sql\`${x}\`), sql\`, \`)` → one bind per element |

## Money, numbers, dates

- Money: `const money = (name) => numeric(name, { precision: 12, scale: 2 })`
  (Caudal `lib/db/schema.ts:30`). EUR-only, signed. Never floats.
- Measurements: plain `numeric` (Aro). Timestamps `withTimezone: true`; calendar
  concepts (schedule dates) use `date` columns.
- **Day-key rule:** local day = `toLocaleDateString("en-CA", { timeZone: "Europe/Madrid" })`
  → `YYYY-MM-DD`. Timezone is hardcoded `Europe/Madrid` in lib code AND `TZ` is set on
  every container. Never use UTC day boundaries for user-facing "today".
- **A day BOUNDARY built with `date.setHours(23,59,...)` resolves against the HOST tz, not the
  product tz** - so a 23:30Z deadline counts as "arrived today" on a UTC box and not on a Madrid
  one, a bug that only appears when host tz ≠ product tz (invisible on a Madrid-`TZ` container,
  live in CI/another host). Build the boundary from the product day: `madridInstant(dayKey(now), 24)`,
  never a bare `setHours`. Found by a mutation test, not tsc. (loop, 2026-09-05)
