# Background jobs

Scheduled work = separate `worker` container, same codebase, `tsx worker/index.ts` +
node-cron, own dev/prod profile pair. Skip the container entirely if no scheduled jobs.

## node-cron 4.x DROPS a late tick - always pass `missedExecutionTolerance`

Its default tolerance is **1000 ms**, and a tick later than that is not run at all: it logs
`missed execution … Possible blocking IO or high CPU` and advances to the next slot. Timers on this
box overshoot by ~1.7 s even on an idle container (ENVIRONMENT.md "Timers on this box drift"), so
the default means the job silently never runs. Loop: 56 syncs, then **110 consecutive misses, zero
executions, 29 hours**, no alert; recall had the same for 8 days. The warning text is misleading - 
it blames IO/CPU while the process is idle.

```ts
cron.schedule("*/15 * * * *", job, {
  timezone: TZ,
  missedExecutionTolerance: 14 * 60_000,  // UNDER the interval (see below)
  noOverlap: true,                        // a late tick now lands near the next one
});
```

**The trap inside the trap:** node-cron also requires `lateBy < gap`, where `gap` is the schedule's
OWN interval - so a tolerance at or above the interval is silently capped and buys nothing. A first
repro using a 1-second cron with a 60 s tolerance behaved *identically to the default* and nearly
proved the option useless. Test it on a schedule with room under the gap.
Reference impl + regression test: `~/projects/loop/worker/schedules.ts`, `schedules.test.ts`.
(loop + recall, 2026-09-05)

## A plain-Node scheduler that needs the app's TS business logic: COMPILE the shared module, never re-type it

closet had the bad pattern and it had already cost real correctness: `server/index.js` carried
hand-written copies of `codeToDescription`/`weatherEmoji` "replicating `src/lib/weather.ts"`, and a
case-by-case diff showed the copy had **drifted** - it knew nothing about storms or snow, so weather
code 95 rendered the sun-behind-cloud emoji. The recipe that worked (closet 2026-07-21, ~40 min, and
it killed 3 more would-be duplicates):

1. `src/lib/server-engine.ts` that ONLY re-exports pure logic (no DOM, no React).
2. Bundle it as part of the normal build:
   ```sh
   esbuild src/lib/server-engine.ts --bundle --format=esm --platform=node \
     --target=node20 --outfile=dist-engine/engine.mjs
   ```
   chained into `npm run build`. **esbuild already ships with Vite - zero new dependencies.**
3. Dockerfile copies `dist-engine` from the build stage; the dev compose builds it on start
   (`npm install && npm run build:engine && node server/index.js`).

**The real payoff is not DRY** - it is that the engine's unit tests now cover the code the 07:30 cron
actually runs, which is otherwise only debuggable by waiting until tomorrow.

**Corollary - testing a scheduler without touching real data:** an ephemeral container with its own
`DATA_DIR` and a FAKE push subscription. The send fails and the error is swallowed, while the
history row is written BEFORE the send - so 4 producers, retention pruning, and dedup were all
verified in minutes. (See `testing`.)

## Before a "fill in the missing data" campaign, SIMULATE it against the filters that read the field

**An UNSET facet is a wildcard, so an entity's NAME filters nothing.** A garment called "Chinos"
with an empty `tipo` passed the filter for EVERY style - the name is not data. The near-miss in the
same session is the sharper half: the fix (populate `tipo`) would have made things worse, because a
style's `allowedTipos` list is FLAT and applies to ALL roles, so tagging the t-shirts would have
evicted them from styles written for trousers (measured: Playa went 25 → 4 usable tops). Simulate
the fill against every consumer of that column before running it. closet 2026-07-22 - it would have
broken silently.
