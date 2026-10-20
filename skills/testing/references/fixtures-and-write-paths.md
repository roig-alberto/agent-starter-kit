# Fixtures & exercising write paths without wrecking real data

Full incidents behind the fixture rules in `SKILL.md`. The generic isolate-drive-drop recipe for a real DB
is in `isolated-db-recipes.md`.

- **Need a state that requires "no data" (empty lane, destructive path, celebration)?
  SCOPE THE VIEW to a synthetic fixture - never delete/mutate real data.** Proven recipe
  (superhuman 2026-07-17, 16 assertions, zero risk): seed a fixture account whose
  `homeAccountId` is bogus (**token-less ⇒ the flusher can never reach the real API**) with
  identifiers on the reserved **`.invalid`** TLD (can never collide with real data), then
  use the app's own per-mailbox filter to scope the view to it - the lanes are empty *for
  that mailbox*, so both states render against real code paths. Add a cleanup that asserts
  it removed itself. It paid for itself immediately: the fixture caught two drizzle bind
  bugs that tsc and the unit suite both missed (see `backend-patterns`).
  **Losing approach:** the session before archived the user's REAL mail to see a
  destructive path. closet did the same class of damage (2026-07-17): its `api-dev` and
  `prod` containers mount the SAME `armario_data` volume / `db.json`, so a shell `PUT`
  meant to be a test mutated production data - recovered from the 07:02 `backups_local`
  snapshot. **Dev is not isolated on this fleet.** For a real write/commit path use
  the isolated write path in `SKILL.md`; for a *view* state, the fixture-scoping trick above is cheaper.

- **A FROZEN date literal next to live `dayKey()`/`new Date()` is a time-bomb fixture.** A test that
  hard-codes `new Date("2026-01-15")` but compares against a helper reading the real clock passes
  today and FAILS on a specific future calendar date (a month/DST/year boundary the frozen value
  crosses) - a "flaky on Tuesday" failure with no code change. Freeze the CLOCK for the whole test
  (`vi.setSystemTime(...)` in `beforeEach`, restore after) so fixture and code share one `now`, or
  derive the expected value from that same clock. Never mix a frozen literal with a live date call.
  (loop 2026-09-05; ~10 min forensics on unrelated stashed work.)

- **Migrations against real data:** the weekly `restore-test.sh` (dev-system) already restores the
  newest NAS dump into a throwaway Postgres and checks sentinel tables. For a risky migration, run the
  same trick manually: restore the latest dump into a scratch container, apply the migration, and verify
  counts BEFORE touching prod.

- **Exercising a WRITE / commit path (endpoint, wizard, server action) end-to-end needs an isolated test
  DB, NEVER the dev/prod DB.** These apps share ONE Postgres container between dev and prod (single
  `db-1`), so a commit from a `compose run` writes the SAME rows the user sees. The generic
  isolate-drive-drop recipe (create `${app}_test` in the same container, push schema, throwaway app on
  `:3099`, assert with `psql`, `DROP … WITH (FORCE)`) lives in `isolated-db-recipes.md`;
  browser-driving it is in `verify-ui-live` step 0b. Fleet specifics to plug in: db user/name = the app's (`caudal`, etc.),
  login reuses `~/.config/ui-check/<host:port>.pw`, and Next makes an env `DATABASE_URL` win over `.env`.

- **Fixtures are anonymized only.** Real bank exports are gitignored by pattern in Caudal (`*.real.csv`
  etc.); never commit real personal data as a fixture.
