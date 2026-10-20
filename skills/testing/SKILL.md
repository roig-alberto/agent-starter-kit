---
name: testing
description: >-
  Testing for this fleet's own apps: Vitest logic tests in the dev container, what deserves a test, test-first bug fixes, and proving a DB write, commit, migration or destructive path against a throwaway database. Use WHENEVER writing or running tests, adding domain logic, fixing a bug, or mutating a database: "add tests", "run the tests", "is this tested", "write a test for this", "test the commit", "does the import actually save", "verify this write path", "test the migration", "without touching prod / real data", "use a test database". First stop when a test WON'T LOAD or a suite lies: "Cannot find package '@/lib/db'", "Failed to load url @/…", `PASS (0)` or 0 collected tests. NOT for browser driving (use verify-ui-live) or Java interview drills (java-testing-drill).
---

# testing - how this fleet tests, and how to prove a write path safely

Every app here tests the same way: Vitest, `environment: node`, pure logic only, run inside the dev
container, and any write is proven against a database you are willing to `DROP`. This skill prevents the
classic failures: a suite that silently did not run reported as green, a test that agrees with the code
because it was copied from the code, and a "test" that wrote to the shared database the user sees.

## Steps: a change that needs tests

1. **Agree the test points.** List where the tests will go: the public functions or boundaries a test calls,
   each with one line on what it catches and what it misses. In an interactive session, confirm the list
   with the user before writing a test. In an unattended Agent Factory run, the plan step records the list
   in the plan and the agent follows it without stopping to ask.
   Done when: the list is in the plan, or the user has confirmed it.
2. **Bug fix: prove it first.** Write a test that reproduces the bug, run it, and watch it fail for the
   reason the bug describes. Only then fix the code.
   Done when: the new test fails on the unfixed code with the bug's symptom.
3. **Write the code one test at a time.** One failing test, then just enough code to pass it, then the next.
   Done when: every test point from step 1 has a test with a value from the spec.
4. **Run the full suite and the full typecheck in the container** (`references/running-tests.md`).
   Done when: the run prints `Test Files N passed (N)` with both numbers equal and above 0, and tsc is clean.
5. **If the change writes to a database, prove the write path** with the four steps under "Isolated write
   path" below. Done when: the scratch database shows the write and the real one does not.

## Rules: architecture

- **Domain logic lives in `lib/<area>/` (or `src/lib/`) as pure functions; routes, actions, and UI stay
  thin.** If you cannot test it without HTTP or a DB, the logic is in the wrong layer.
- **Keep testable logic in a DB-free sibling module with RELATIVE imports, and test that.** No repo here
  configures `resolve.alias` in `vitest.config.ts` (vitest ignores tsconfig `paths`), and `lib/db` throws at
  import when `DATABASE_URL` is unset. Do not add `resolve.alias {'@': './src'}`; it drags the DB pool into
  every run. The caller keeps the SQL.
- **Import only pure modules from tests, never an entrypoint.** Importing `worker/index.ts` executes it: it
  registers the cron schedules and can write to the shared DB.
- **Never `vi.resetModules()` a file that imports the ORM graph.** It reloads the drizzle graph and OOMs the
  worker; import once and use `vi.stubEnv(...)`, and move a value captured at module scope into a tiny
  DB-free file.
- **IndexedDB logic is unit-testable, although `environment: "node"` has no `indexedDB`.** Put
  `import "fake-indexeddb/auto";` as the FIRST line of the test and drain the fake DB in `beforeEach`.
  Importing `idb` is fine; importing an `@/lib/db` chain is not.

## Rules: what deserves a test

- **Yes: every domain engine, parser or importer, date, streak, or pace math, and any edge case you had to
  think about.** A new engine's tests land WITH it, not later.
- **Yes: a regression test for every bug fixed.** RULES.md says "write a test that reproduces it, then make
  it pass".
- **No (deliberate): React components, API routes, E2E.** UI is verified live with `verify-ui-live`; do not
  add a component-testing stack without the user asking.

## Rules: running

- **Always run inside the container.** The deps are Linux-built and host node_modules differ; each repo's
  AGENTS.md (the same file as `CLAUDE.md`) Commands block wins over `references/running-tests.md`.
- **Always run the FULL suite and the full typecheck, never a filtered subset.** Partial runs let type drift
  sit unnoticed; a pre-existing failure is a finding to fix if small or flag if not.
- **A test count of 0 is never a pass.** rtk renders a collection failure as `PASS (0) FAIL (0)`, so assert
  the count, not the absence of failures.
- **Check that the number IN PARENTHESES matches the number that passed.** `N passed (M)` with `N < M`
  means M-N files were collected and never reported.
- **If a test assumes "nobody else is writing", isolate it or serialise the files with
  `fileParallelism: false`.** Vitest runs files in parallel; a session-level advisory lock is rejected (see
  `backend-patterns` `references/concurrency.md`).

## Rules: keeping tests honest

- **Assert values and side effects that matter, not existence or call counts** (`expect(total).toBe(42.5)`,
  never just `toBeDefined`). A test is only useful if it fails when the logic breaks.
- **A test changes only when the spec changed.** Never skip, delete or loosen one to reach green (floor guard).
- **Never compute the expected value the way the code does.** Such a test passes by construction; take the
  value from the spec, a worked example, or a known-good literal.
- **State the expected value from the SPEC before you run the test.** If the test name and the assertion
  disagree, the CODE is wrong; a green suite proves consistency with itself, never correctness.
- **Cover the boundary that made the function interesting:** exactly-full, empty input, the timezone edge
  (23:59 Madrid), negative amounts, duplicate rows. Ask: "if someone flipped `>=` to `>`, does a test go red?"
- **Any test over a scorer with a saturating or short-circuit branch needs a fixture OUTSIDE that branch.**
  Inside it, a tie-break such as id order decides the assertion; name the loser so it would win on id order.
- **After touching a component, reload THAT page.** tsc is blind to a hook added after an early return,
  which blanks the page.

## Rules: data and fixtures

- **Any test that writes runs against a database you are willing to `DROP`.** These apps share one Postgres
  between dev and prod, so a `docker compose run … commit` writes the rows the user sees.
- **Prefer read-only assertions where they prove the same thing.** Most UI verification needs no write.
- **A backup existing is not an undo existing.** A snapshot restores a different state and the app's undo
  window has closed by then; if you cannot isolate, create a throwaway record or snapshot the exact entity
  first (`curl /api/<coll> > scratch/pre.json`).
- **If your plan includes "and then I undo it", set up a scratch dataset instead.** A loop that mutates (a
  review, a grade, a streak) cannot be checked "carefully" on real data.
- **Guard a seed or one-off script exactly like a test.** It inherits the app's `DATABASE_URL`, which can be
  the shared prod `db-1`; abort unless `DATABASE_URL` names a `_test` DB.
- **Need an empty or destructive state? Scope the view to a synthetic fixture.** Use a token-less fixture
  account with identifiers on the reserved `.invalid` TLD; dev is not isolated on this fleet.
- **Freeze the clock, not a date literal.** Use `vi.setSystemTime(...)` in `beforeEach`; a frozen
  `new Date("2026-01-15")` next to a live `dayKey()` fails on some future date.
- **Fixtures are anonymized only.** Never commit real personal data as a fixture.

## Isolated write path (any stack)

1. **Isolate.** Stand up a scratch database no one else uses: empty and schema-pushed, or a restored dump
   when the path needs realistic data. Never the dev or prod database.
2. **Point the app at it.** Run a throwaway app instance whose connection string targets the scratch
   database. Done when: a health route answers and the override is confirmed (first gotcha below).
3. **Drive and assert.** Exercise the path (curl, a browser, a script, or the migration tool), then read the
   scratch database directly (`psql`/`mysql`/`sqlite3`). Done when: the expected rows are there.
4. **Drop.** Stop the throwaway instance and force-drop the scratch database. Done when: nothing is left and
   the real database is untouched.

The Postgres-in-compose recipe (sibling `${APP}_test` database, schema cloned with `pg_dump --schema-only`,
app on the scratch port 3099) and the MySQL, SQLite, managed, and bare-process variants are in
`references/isolated-db-recipes.md`.

## Red flags

- Saying "tests pass" on `PASS (0)` or on `37 passed (38)`. Both happened; read both numbers.
- Driving a mutating flow on real data "just to check the UI". It deleted a real record and graded real cards.
- Running a seed or test import in the app container without a `_test` guard. It wrote phantom rows to prod.
- Picking the assertion because that is what the code did. A wrong test went green and the bug shipped.

## Gotchas

- **`Error: Cannot find package '@/lib/db'` or "Failed to load url @/…".** The test transitively imports the
  DB module; extract the logic into a DB-free sibling with relative imports.
- **`Error: Worker exited unexpectedly` next to `Test Files 37 passed (38)`.** A `vi.resetModules()` over the
  ORM graph blew the heap; stub the env instead.
- **A worktree or agent copy shows phantom `FAIL` files and TS2307 errors.** The image's node_modules is
  stale; mount the live container's volume read-only and compare against a pristine export of the base.
- **A bare `curl -X POST` returns `403 Cross-site POST form submissions are forbidden`.** It is Astro's CSRF
  guard; send `-H "Origin: http://127.0.0.1:<port>"` and never disable the guard.
- **Caudal's `compose run` says tsc or vitest is not found.** Its dev deps live in a named volume that only
  the dev profile populates; run `npm install` first.
- **You are not sure the run hit the scratch DB.** A `.env` file can shadow an env var or the reverse; in
  Next.js an OS or `-e` env var WINS over `.env`. Check the scratch DB got the write and the real one did not.
- **Every write returns 500 against the scratch DB.** It has no tables; run migrate or push against
  `TEST_URL`, or clone the schema, before driving.
- **`docker compose run … web <schema-cmd>` hangs silently and looks like a drizzle prompt.** The anonymous
  `- /app/node_modules` volume is empty under `run`; clone the schema with `pg_dump` instead.
- **Calling a Next server action from vitest throws
  `Invariant: static generation store missing in revalidatePath`.** Alias `next/cache` to a no-op stub.

## References

- `references/running-tests.md`: where tests live, per-app run commands, the worktree recipe, the CSRF header.
- `references/fixtures-and-write-paths.md`: fixture scoping, the frozen-date trap, migrations on real data.
- `references/isolated-db-recipes.md`: read before isolating a database; copy-paste recipes for every stack,
  the vitest server-action harness, and related skills.
- `references/history.md`: every incident and measurement behind these rules; read it when a rule seems
  excessive.
