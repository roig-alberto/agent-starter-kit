# Ripple check - full incidents

The three 2026-07 incidents behind the checklist in `SKILL.md`.

Three incidents, same shape: a change is correct in isolation and silently kills a
consumer somewhere else. **No error is thrown - the feature just stops working.**

- **Migrating/renaming a table: the READ path is the obvious half; the WRITERS and every
  duplicated inline copy of the logic drift silently.** superhuman 2026-07-17 generalised
  `mutes` → a `rules` table and repointed the inbox read. A pre-ship grep found two live
  landmines: the swipe-mute UI still POSTed `/api/mutes` (muting would have become a no-op
  *with a cheerful toast*), and `lib/push/notify.ts` held its OWN inline copy of the mute
  filter (the worker would have kept pushing for muted senders). The domain logic lived in
  THREE places. **Recipe:** `grep -rn '<old-table>\|/api/<old-endpoint>'` across
  `components/ app/ worker/ lib/`, enumerate **WRITERS and READERS** before touching the
  read, then collapse the duplicated logic into one pure `lib/` module (here
  `lib/classify/rules.ts`). **Delete orphaned endpoints in the same commit** - a dead route
  that still accepts writes is indistinguishable from a working one (the same session found
  `/api/auth/logout` returning `{ok:true}` while logging out nobody since Phase 0).
- **Breaking a load-bearing INVARIANT: hunt what it was quietly buying.** Same session,
  a rule action that WRITES to the mailbox broke "rules only filter at read time" - an
  invariant that had silently underwritten three unrelated promises, none of them in the
  diff: audit events stamped `by:"you"` (crediting the user with a 500-item sweep), a
  "handled N this week" count reading a table the flush DELETEs from (sweep 500 → report
  0), and "undo everything this rule did" implemented as a plain DELETE (correct only
  while nothing had been touched). **Name the invariant you are breaking, grep every
  consumer that assumed it, re-earn each promise in the same commit.**
- **A new enum value usually touches 4 spots, and only 1 is typechecked.** Aro 2026-07-09
  shipped a dead settings toggle to prod (`ZodError: Invalid enum value` at runtime, tsc
  green because the server action signature is `key: string`). A new `NudgeKey` needs:
  `db/schema.ts` column + `NotificationPrefs` type/defaults (`lib/settings/prefs.ts`) + the
  settings **Zod enum** (`app/(app)/settings/actions.ts`) + the `NudgeRow`. grep the enum.


## Making a GLOBAL resource per-request (Caudal, 2026-07-21)

- **Making a GLOBAL resource per-request** (db connection, API client, tenant) → **DELETE the
  singleton export; never keep it "for compatibility".** Caudal 2026-07-21 moved 51 `import { db }`
  sites to `await getDb()` (`~/projects/finance-proj/lib/db/index.ts:5,103` - there is deliberately
  no `db` export, only `getDb()`/`realDatabase()`). Removing the export made `tsc --noEmit`
  enumerate exactly the 51 call sites, turning the job mechanical and exhaustive. Keeping it would
  have let any forgotten site keep compiling while silently pointing at the wrong resource - which
  was precisely the catastrophic failure being prevented (showing REAL data believing it is demo).
  Corollary: once the typechecker is the checklist, the conversion can be split across subagents by
  DISJOINT file groups under a short written contract and verified centrally with `tsc` (5 agents /
  51 sites / 0 type errors on merge).

## The original checklist wording

- **Migrating/renaming a table or endpoint** → `grep -rn '<old-table>\|/api/<old-endpoint>'`
  across `components/ app/ worker/ lib/` and enumerate **WRITERS and READERS**, not just the
  read path you're moving. superhuman's `mutes`→`rules` migration left a UI still POSTing
  the dead endpoint (muting = a no-op *with a cheerful toast*) and a second inline copy of
  the filter in `lib/push/notify.ts`. Collapse duplicated domain logic into ONE pure `lib/`
  module, and **delete orphaned endpoints in the same commit** - a dead route that still
  accepts writes is indistinguishable from a working one.
- **Breaking a load-bearing INVARIANT** → name it, then grep every consumer that assumed
  it and re-earn each promise in the same commit. superhuman's "rules only filter at read
  time" had silently underwritten three unrelated promises (audit attribution, a weekly
  count, an undo) - none of them in the diff.
- **Adding an enum value** (a pref, a kind, a status) → it typically touches 4 spots and
  only 1 is typechecked. Aro shipped a dead prod toggle (`ZodError` at runtime, tsc green
  because the action signature is `key: string`): schema column + type/defaults + the **Zod
  enum** + the row component. grep the enum.
