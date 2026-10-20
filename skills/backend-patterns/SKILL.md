---
name: backend-patterns
description: >-
  Proven backend patterns for this box's self-hosted Next.js apps. Use WHENEVER writing/reviewing backend code here: an endpoint or server
  action, the Drizzle schema or migrations, validation, auth/sessions, money or dates, or a new
  app's backend. Trigger on 'add an endpoint', 'new table', 'add a field', 'validate this',
  'change the schema', 'add a job'. ALSO first stop for a query that typechecks and explodes at
  RUNTIME (`malformed array literal`, `ERR_INVALID_ARG_TYPE ... instance of Date`), a migration
  that 'applied' but changed nothing, a `next build` failing on `DATABASE_URL is not set`, or
  'what else does this table/rename/enum touch?'. NOT for tests (use `testing`).
---

# backend-patterns - how backends are built here

This skill encodes how the fleet's Next.js backends are actually built, distilled from the code of
`~/projects/personal-dash` (Aro) and `~/projects/finance-proj` (Caudal). It prevents the failures that
typecheck green and break at runtime: a bind that explodes at query time, a migration that applied
nothing, a rename that silently kills a consumer, and a deploy that runs new DB with old code.

## Rules: mutations and validation

- **Pick one mutation shape per app and stay consistent.** Aro uses server actions (`"use server"` files
  at `app/(app)/<area>/actions.ts`); Caudal uses route handlers (`app/api/**/route.ts` with
  `export const runtime = "nodejs"`). Follow whichever the app already uses, because mixed shapes hide
  mutations.
- **External-facing endpoints are ALWAYS route handlers.** OAuth callbacks, push subscribe, webhooks, and
  file or binary serving need a stable URL (see Aro's `app/api/{withings,ticktick,push,auth}/**`).
- **An undo or revert restores the COMPLETE captured snapshot, not just the user-visible field.** Capture
  the full prior state on the mutation (a snapshot column) and restore exactly those keys, because a
  partial revert leaves derived state (a ranking timestamp) silently wrong.
- **Validate with Zod inline at every boundary.** Declare `const Body = z.object({...})` in the route or
  action file itself and parse before touching the DB; there is no central schema module, and docs
  claiming "shared schemas" are drift.

- **A state-changing call that can be retried honours an idempotency key** (imports, webhooks, money writes).
  The key comes from the intent (the client's `Idempotency-Key`, or `charge:v1:${orderId}`), never
  `crypto.randomUUID()` or a timestamp per attempt. Claim it with an insert under a unique constraint, never a
  check then an act (two retries both see "not seen"); the same key with a different body is a 422, and a
  duplicate still in flight gets a 409.

## Rules: data

- **Commit migrations and apply them in-container.** Use `npm run db:generate`, commit the files under
  `db/migrations/`, and run `db:migrate` inside the container, because a host `npm run db:migrate` prints
  `applying migrations…` and exits 0 having applied nothing. Caudal's `db:push`-only workflow is tracked
  drift; do not copy it.
- **Change schema on real data in additive order (expand, migrate, contract)**, each step its own migration,
  because the shared dev/prod database runs the old code against your new schema: add the new column nullable;
  write both old and new; backfill in batches, never one `UPDATE` over the table; switch reads; and drop the old
  column in a separate, later deploy once no code reads it. Build a large index with `CREATE INDEX
  CONCURRENTLY` so writes keep flowing.
- **If you touch the schema of the shared DB, redeploy prod (web AND worker) in the SAME turn.** Never end
  a turn with new DB plus old code; the recipes, including migrating prod from outside the `runner`
  image, are in `references/migrations.md`.
- **`sql\`\`` is for STRUCTURE; values go through drizzle operators.** A `Date` or an array bound inside a
  raw template typechecks and explodes at query time (`references/drizzle.md` has the table).
- **When a screen promises real numbers, reconcile the aggregate against `count(*)` of the source before
  shipping the query.** A `GROUP BY` that collides on its columns silently drops rows; prefer one row per
  record through a JS counter.
- **Advisory locks are TRANSACTION-scoped (`pg_try_advisory_xact_lock` inside `db.transaction()`).**
  Behind a pool a session lock can unlock on a different connection and stay held forever
  (`references/concurrency.md`).
- **Money is `numeric(name, { precision: 12, scale: 2 })`, never floats.** EUR-only, signed; measurements
  use plain `numeric`, timestamps `withTimezone: true`, calendar concepts `date` columns.
- **The local day is `toLocaleDateString("en-CA", { timeZone: "Europe/Madrid" })`.** Never use UTC day
  boundaries for a user-facing "today", and build a day boundary with `madridInstant(dayKey(now), 24)`,
  never a bare `setHours`, which resolves against the host tz.
- **Postgres major is pinned to the dumps.** See `references/drizzle.md` for the current pin.

## Rules: auth, outbound calls, jobs, LLMs

- **Single-user auth is argon2 plus an HMAC cookie, behind Cloudflare Access.** Never import the argon2
  native module in `middleware.ts` (it is edge code); gate with an explicit PUBLIC allowlist. The full
  recipe is in `references/auth.md`, and `security` (not in this kit) owns the first layer.
- **Every outbound call needs a per-ATTEMPT `AbortController` timeout, and the abort counts as transient.**
  Node's `fetch` waits forever, and a retry loop only fires on a response (`references/outbound-calls.md`).
- **A mutation queue classifies every response into ok, TRANSIENT, or permanent before writing status.**
  Marking every non-2xx `failed` loses work the moment the provider throttles you.
- **Scheduled work runs in a separate `worker` container** (`tsx worker/index.ts` plus node-cron), and
  every `cron.schedule` passes `missedExecutionTolerance` under its own interval plus `noOverlap: true`,
  because the 1000 ms default silently drops ticks on this box (`references/background-jobs.md`).
- **A plain-Node scheduler that needs the app's TS logic compiles the shared module with esbuild; it never
  re-types it,** because a hand copy drifts.
- **Before a "fill in the missing data" campaign, simulate it against every filter that reads the
  field.** An UNSET facet is a wildcard, so filling it can evict rows.
- **LLM structured output needs `max_tokens` AND a `maxLength` on every free-text field, plus a zod
  re-validate.** `strict: true` does NOT prevent truncation; make the model return a bounded integer
  INDEX, never an id (`references/llm-structured-output.md`).

## Rules: API shape and ripple check

- **Never inline blobs in a list JSON; match identifiers on a word or label BOUNDARY; give every default
  filter a "how much am I hiding?" count; no ambient `Math.random` in anything a user reloads.** Each is a
  correct implementation that lies to the user (`references/api-shape-traps.md`).
- **Migrating or renaming a table or endpoint: grep WRITERS and READERS.** Run
  `grep -rn '<old-table>\|/api/<old-endpoint>'` across `components/ app/ worker/ lib/`, collapse duplicated
  logic into one pure `lib/` module, and delete orphaned endpoints in the same commit.
- **Breaking a load-bearing INVARIANT: name it, grep every consumer that assumed it, and re-earn each
  promise in the same commit.** No error is thrown; the feature just stops working.
- **Making a GLOBAL resource per-request: DELETE the singleton export.** Then `tsc --noEmit` enumerates
  every call site and the conversion becomes mechanical (`references/ripple-check.md`).
- **Adding an enum value: grep the enum.** It touches about 4 spots and only 1 is typechecked.

## Gotchas

- **A `"use server"` file 500s with `Only async functions are allowed to be exported in a "use server" file`.**
  Move the exported constant into a `lib/` module.
- **`ADD_FOOD_TABS.find is not a function` or "Functions cannot be passed directly to Client Components".**
  Nothing exported from a `"use client"` module is usable by a server component; move it to a neutral
  module.
- **Results vanish after a server action although the DB write succeeded, or an undo banner never
  appears.** A `revalidatePath` of the current route remounted the client component; drop it.
- **The app "freezes" after a server-action `redirect()` from a segment's index page to a nested route.**
  Navigate from a sibling depth or redirect client-side.
- **Localhost renders HTTP 200 but React never hydrates.** `allowedDevOrigins` REPLACES the default
  allowlist; include `127.0.0.1` and `localhost` beside the tunnel host.
- **A per-item server action fires in a runaway cascade.** The action refreshes the route it reshapes;
  snapshot the item into client state.
- **`next build` fails on `DATABASE_URL is not set`.** Set
  `ENV DATABASE_URL="postgres://build:build@127.0.0.1:5432/build"` before `RUN npm run build`.
- **The worker crashes at import with "cannot be imported from a Client Component".** A `lib/` module
  shared with the worker must not `import "server-only"`.
- **A cookie set from an old localStorage key fails intermittently.** RFC 6265 forbids `:` in a cookie
  NAME; rename it.
- **`missed execution … Possible blocking IO or high CPU` in an idle worker.** The tick was dropped; pass
  `missedExecutionTolerance`.
- **`db:push` or `db:generate` hangs.** It reads `/dev/tty`; apply the DDL by hand or split the migration
  (`references/migrations.md`).
- **closet behaves differently.** It is frozen legacy (Vite plus Express, JSON-file persistence); a dev
  write there IS a production write (`references/legacy-closet.md`).

## References

- `references/migrations.md`: hanging prompts, the two-part shared-DB change, migrating prod, drizzle-kit traps.
- `references/drizzle.md`: the client setup, migration discipline, the bind-trap table, money and dates.
- `references/concurrency.md`: the transaction-scoped advisory lock recipe and the own-connection corollary.
- `references/auth.md`: the full single-user auth recipe and the cookie-name rule.
- `references/nextjs-gotchas.md`: every Next.js server-side gotcha with its incident and fix.
- `references/outbound-calls.md`: the timeout code and the queue classification rules.
- `references/background-jobs.md`: the worker container, node-cron tolerance, the esbuild engine, fill campaigns.
- `references/llm-structured-output.md`: truncation, the index pattern, and testing without a funded key.
- `references/api-shape-traps.md`: blobs, boundary matching, hidden-result counts, seeded shuffles.
- `references/ripple-check.md`: the full incidents behind the ripple-check rules.
- `references/legacy-closet.md`: closet's legacy stack and its shared-volume trap.
- `references/history.md`: incidents and measurements not told in a topic file.
