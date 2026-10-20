# testing - incident history

The incidents and measurements behind the rules in `SKILL.md`, kept nearly verbatim. This skill merged
`app-testing` and `isolated-test-db` on 2026-10-15; each part below keeps its source's entries. The old
`isolated-test-db` file `references/recipes.md` is now `isolated-db-recipes.md`.

## From app-testing (fleet test conventions)

### Where the conventions came from (2026-07-06)

Distilled from the real test suites (2026-07-06): Aro 5 files, Caudal 24 files, closet 8 files / 74
cases. All Vitest, all `environment: node`, all pure logic. Real engines: recommendation + color harmony
(closet), FIRE/drawdown/dedup/importers (Caudal), streaks/nudges/one-rep-max/decode (Aro).

Partial runs are why the 2026-07-06 TS drift (6 strict errors) sat unnoticed.

### The `@/` alias trap (hit in 4 apps)

**No repo here configures `resolve.alias` in `vitest.config.ts`** (verified 2026-07-20: recall +
personal-dash set only `environment`/`include`; superhuman-mvp has no vitest config at all - vitest
ignores tsconfig `paths` either way). So a test importing any module that TRANSITIVELY reaches
`@/lib/db` fails to LOAD: `Error: Cannot find package '@/lib/db'`. Worse, `lib/db` throws at IMPORT
when `DATABASE_URL` is unset, so even a wired alias would drag the postgres pool (and `web-push`) into
the test env.

- **Proven winner:** keep the logic in a DB-free sibling module with RELATIVE imports and test THAT; the
  caller keeps the SQL. Real extractions: recall `ai-budget.ts` out of `ai.ts`, personal-dash
  `lib/workouts/progression-scope.ts`, superhuman `lib/classify/rules.ts`.
- **Losing approach:** adding `resolve.alias {'@': './src'}` - "works" but imports the DB pool into
  every test run. Rejected in recall.
- **Cost:** recall 2026-07-12, personal-dash 2026-07-10 (~5 min), superhuman 2026-07-16 (~10 min) and
  again 2026-07-17 (a whole file written the wrong way).

### `vi.resetModules()` OOM (Caudal, 2026-07-21)

`lib/db/__tests__/dataset.test.ts:47-52`, commit a4a98b5: re-importing `lib/db` after a reset reloads
the whole drizzle graph and blew the worker heap at 2 GB. The winner was importing the module ONCE and
stubbing only the environment with `vi.stubEnv(...)`, which works because the code under test reads
`process.env` at call time (here `demoConfigured()`/`getDb()`).

### A suite that failed to load read as green (superhuman, 2026-07-17)

rtk's vitest summary renders a collection failure as `PASS (0) FAIL (0)`; the superhuman session
nearly committed on it. The raw JSON had `numFailedTestSuites: 1`.

### `37 passed (38)` (Caudal, 2026-07-21)

`Test Files 37 passed (38)` + `Error: Worker exited unexpectedly` (the OOM above) scans as green at a
glance, and a whole file had silently not run.

### IndexedDB logic is unit-testable (recall, 2026-07-14, first try)

`import "fake-indexeddb/auto";` as the FIRST line of the test made an outbox/queue module's
enqueue, flush, retry, and poison-drop reducer testable with zero browser or container (recall
`src/lib/offline/queue-store.test.ts`, `rating-queue.test.ts`).

### A test import ran the worker (loop, 2026-09-05)

`import`ing `worker/index.ts` from a test EXECUTED it - it registered the cron schedules and fired
`void ensureTodayObjectives(...)`, so the test booted the worker and could write to the shared DB. It
cost ~5 min, but it could have created a page in prod.

### Stale node_modules in a worktree (Aro, 2026-09-15)

Running a copy through `docker compose run -v <tree>:/app web-dev` produced **4 phantom `FAIL` test
files (papaparse, date-fns missing) and 20 TS2307 errors, identical on a pristine `master` export**. It
cost one wasted verification round and a wrong recipe handed to an agent.

### Test name and assertion disagreed (superhuman, 2026-07-17)

Building a phishing detector, I wrote
`it("does not mistake a brand word inside an unrelated name", … .flagged).toBe(true)` - the name says
one thing, the assertion the opposite, suite green, bug ships. The tell: I reached for `toBe(true)`
because that's what the code DID.

### A fixture inside a short-circuit branch (closet, 2026-07-20)

`pairScore` returns a flat `0.9` whenever either colour `isNeutral` (`src/lib/color.ts:181`), so a
black/white fixture scored every candidate identically and the deterministic id tie-break silently
decided the assertion - the test "proved" colour ranking while actually proving alphabetical order.
Fix: build the fixture from saturated hues (`#1f3a93` vs analogous `#2f6fd0` vs clashing `#2fd08a`)
AND name the loser so it would win on id order.

### A blank page shipped to prod (closet, 2026-07-14)

A `useState` added AFTER an early return ("Rendered more hooks than during the previous render"); tsc
is blind to it, and the session verified other screens. One screenshot of the edited screen would have
caught it.

### The isolated write-path test that worked (Caudal, 2026-07-10)

Verified Caudal 2026-07-10: the import wizard persisted a shared `traspaso_pair_id`; real DB untouched.

### A global-invariant test on a shared database (caudal, 2026-08-27)

Two integration tests that hit the same real database - one asserting a GLOBAL invariant (total spend ==
budgeted + outside), the other seeding and deleting rows - interleaved: the second's writes landed
between the first's queries. It passed in isolation and failed in the full suite, and it took two green
runs to show itself. `fileParallelism: false` fixed it (Caudal: 3.6s to 12s, three consecutive green
runs).

### The CSRF guard (2026-07-27)

A bare `curl -X POST` to an Astro API route returned
`403 Cross-site POST form submissions are forbidden`; it looked like a broken endpoint and was not.

## From isolated-test-db (isolated write paths)

### The incident that earned this skill (closet, 2026-07-20)

Verifying a stateful UI flow by driving it against the user's REAL data: exercising swap + quitar on
the live Madeira trip deleted a real `Bañador` essential from `db.json`. By the time it was noticed the
in-app undo toast had expired (5 s), so there was no undo left. Recovery only worked because a local
backup volume held an 08:17 snapshot
(`docker run --rm -v closet_backups_local:/b alpine cat /b/db-<ts>.json`) - and that snapshot ALREADY
DIFFERED from live, so the restore was a **reconstruction, not a rollback** (~10 min, unclean).

Note the shape of the failure: a backup existing is NOT the same as an undo existing. A nightly or
opportunistic snapshot restores a *different* state, and the mutation is discovered after the app-level
undo window has closed.

### Second occurrence (recall, 2026-07-23) - a review LOOP that mutates

Exercising the spaced-repetition review twice in Playwright "just to check the UI" graded 15-16 REAL
cards and advanced the streak each time; both runs had to be hand-reverted from `reviews.prev_fsrs`
(worked only because the exact rollback column existed). A visual check of any loop that MUTATES must
run against a throwaway/seeded dataset, not the real study "carefully".

### The destructive repro (Aro, 2026-07-07)

See `debugging` step 1: a destructive repro on real rows once deleted a live record.

### The migration tool that hung (Aro, 2026-09-09)

`docker compose run --rm --no-deps -e DATABASE_URL="$TEST_URL" web <schema-cmd>` HANGS silently in any
compose that mounts `- /app/node_modules` as an anonymous volume (every app here): `run` gets a fresh
EMPTY volume, so the binary is missing and it looks like a drizzle prompt. It cost a 120 s timeout.

### The scratch port collision (2026-07-21 audit)

The scratch app port is 3099, the reserved scratch port in the port registry. It was :3009 until the
2026-07-21 audit - that is triage's DEV port, so this recipe collided with a running dev container.

### The server-action harness (loop, 2026-09-01)

Original gotcha, verbatim: **Calling a Next server action from vitest throws `Invariant: static
generation store missing in revalidatePath`.** Clean fix: alias `next/cache` to a no-op stub in the
integration config (`resolve.alias`), so you test the DATABASE EFFECT without booting Next. Pairs with
the disposable-Postgres harness (`scripts/test-db.sh`).

### The seed that poisoned prod (loop, 2026-09-02)

A `npm run seed` run in the app container inherited the app's `DATABASE_URL` = the SHARED prod DB
(dev+prod share one `db-1`), so it wrote fake rows straight into what the user sees - loop's seed left
17 phantom items feeding the planner for 3 days before anyone noticed.

## Test-first additions (2026-10-15)

### Where the test-first rules came from

During the 2026-10-15 skills redo the user asked to fold two outside ideas into this skill, rewritten in
the house style: agree where the tests go (the test points) before writing any test, and never write an
assertion that recomputes the expected value the way the code does (from Matt Pocock's `tdd` skill); and
start every bug fix with a failing test that reproduces it, the "prove it" pattern (from Addy Osmani's
test-driven-development skill). RULES.md already said "a test that reproduces it now passes".

### The user's decision on asking about test points

The outside skill stops and asks the user to confirm the test points before any test exists. The user
decided that this only holds in interactive sessions. In an unattended Agent Factory run nobody is there
to answer, so the plan step writes the test points into the plan and the implementing agent follows that
list without stopping to ask.
