# Concurrency gotchas (Postgres + a connection pool)

## Advisory locks must be TRANSACTION-scoped (`pg_try_advisory_xact_lock`)

Caudal 2026-07-21, seeding the demo dataset on demand: two simultaneous requests must not both
seed. **The reflex - `pg_try_advisory_lock` + unlock in a `finally` - is broken behind any pool**
(postgres.js, pgbouncer): the `pg_advisory_unlock` can run on a DIFFERENT pooled connection, so
the lock stays held forever and the guarded function never runs again. It throws nothing; the
feature just silently stops working, which is why it survives review.

Winner: `pg_try_advisory_xact_lock` INSIDE `db.transaction()` - released on commit/rollback,
always on the same connection. Sequence is **check, open tx, try lock, RE-CHECK under the lock**
(someone may have won between the first look and the lock), then work.
Full shape: `~/projects/finance-proj/lib/db/demo-seed.ts:36-57`.

```ts
if (await hasData(db)) return "present";
return db.transaction(async (tx) => {
  const [got] = await tx.execute<{ ok: boolean }>(sql`SELECT pg_try_advisory_xact_lock(${LOCK}) AS ok`);
  if (!got?.ok) return "busy";             // another request is doing it; let it win
  if (await hasData(tx)) return "present"; // re-check under the lock
  await seed(tx); return "seeded";
});
```

Verified: 4 concurrent requests on an empty DB gave 1 `seeded` + 3 `busy`, zero duplicates.

**Corollary that bit during the same change:** work whose input must be visible to a NEW connection
runs AFTER the commit, never inside the transaction. Persisting net-worth snapshots calls a function
that resolves its own connection, so inside the tx it would have read the pre-seed state and stored
an empty series. Whenever a helper opens its own connection, it cannot see your open transaction.

## Two writers of one temp file (Shelf, 2026-10)

Two requests writing the same `x.tmp` and renaming it give the loser an ENOENT and a 503. Dedupe in-flight work per key,
and give every temp file a unique name.
