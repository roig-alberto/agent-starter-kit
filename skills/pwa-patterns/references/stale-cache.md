# Stale-cache failures in an installed PWA (two different root causes)

Both present as "the installed app shows something old". They are NOT the same bug - check which
symptom you have before touching the service worker.

| Symptom | Cause | Section |
|---|---|---|
| Old DATA after a mutation; a fresh tab is fine; only reinstalling helps | cache-FIRST navigation in the SW | 1 |
| Old or blank PAGE for hours after a DEPLOY; localhost fine; clearing the cache fixes it per-device | Cloudflare pinning `/sw.js` | 2 |

## Installed PWA shows STALE DATA - `staleTimes` is a DEAD END; the fix is a network-first SW (recall, RESOLVED 2026-07-16)

Symptom: installed PWA shows old counts/data after a mutation; a fresh browser tab is fine; **only
REINSTALLING the PWA refreshed it**. `staleTimes` was correctly a DEAD END - don't retry it: (1) a Tier-1 SW
(no fetch handler) caches nothing; (2) `experimental.staleTimes: { dynamic: 0 }` (App Router client Router
Cache) was tried and reverted, did NOT fix it.

**What actually fixed it (recall, `src/sw/index.js`, commits `c6797fc` + `c3c8e9c`):** a proper Workbox SW
that (a) **precaches only the immutable hashed shell** (`precacheAndRoute(self.__WB_MANIFEST)` - hashed
`/_next/static/*` chunks never go stale), (b) serves **navigation NETWORK-FIRST** - always fetch the fresh
document/RSC online, fall back to the precached shell only when offline (so data is never stale online), and
(c) ships a **clean SW-update flow that auto-refreshes clients on a new SW** (skipWaiting + clients.claim +
reload on `controllerchange`). The stale-data class of bug comes from cache-FIRST navigation (or a cached
`start_url` document surviving relaunch); network-first navigation is the cure. This moves an app to the
Tier-3 (precached app-shell) column below - recall now joins closet there, but with network-first nav so
live data stays fresh. **Do NOT** add cache-first navigation to a data-live PWA; that's the bug, not the fix.

## Cloudflare pins a STALE `/sw.js` for 4h - every deploy ships broken until it expires (recall, 2026-07-23)

Symptom: after a prod deploy the app serves an old or blank page for hours; localhost is fine, and
"clear the cache" fixes it per-device. Same *symptom* as the stale-data section above, different
cause - do not go re-reading the SW logic.

**Measure before theorising** - compare origin vs edge headers on the SW itself:
`curl -sI http://<origin>:3000/sw.js` vs `curl -sI https://<host>/sw.js | grep -i "cache-control\|cf-cache-status"`.
Origin said `public, max-age=0`; the edge returned **`max-age=14400`, `cf-cache-status: REVALIDATED`** - 
Cloudflare's default 4h **Browser Cache TTL** overrides the origin for static extensions (`.js`), so
browsers keep the OLD service worker, whose precache manifest points at chunk hashes the new build no
longer serves.

**Fix (both halves, or it comes back):**
1. Origin must send `no-store` for the SW + manifest - CF then leaves them alone (`cf-cache-status: BYPASS`).
   Next.js: a `headers()` entry in `next.config.ts` for `/sw.js` and `/manifest.webmanifest`.
2. **Version the SW's own page cache per build** and delete older ones in `activate`. recall's was a
   constant `recall-pages-v1` that survived every deploy, so one failed fetch served HTML referencing
   dead chunks (`src/sw/index.js`; build id injected by `scripts/build-sw.mjs` via esbuild `define`).
   Watch the TDZ: read the cache name AFTER its `const`, or `activate` throws on every activation.

Same family as the icon `max-age=14400` override below and the edge-cached `/api` config in
`fleet-ops`. A hashed-chunk precache does NOT protect you - the stale thing is the SW.

## `immutable` on a URL whose bytes can change = a year-long stale trap

`Cache-Control: max-age=31536000, immutable` on an API resource that CAN be replaced at the SAME
URL is a silent stale-content bug, and `immutable` **never revalidates** - so changing the header
later cannot dislodge an already-cached entry. Only a URL change reaches clients that cached it.

glow served preset LUTs at `/api/presets/<id>/lut` as immutable, assuming a preset's LUT is
forever; re-fitting a look overwrote the bytes at the same id, so phones rendered a YEAR-old LUT
(the pre-fix grey-faced one with the new contrast on top - worse than either).

**Rule: mark a URL `immutable` only if the URL is content- or version-addressed.** If the same URL
can ever change bytes, put a version token in it - glow versioned by the row's `updatedAt`
(`?v=<ms>`), kept `immutable` (now honest per-version), and threaded the version through every
consumer plus any in-memory cache keyed `id:ver`. Note this is the HTTP cache layer, distinct from
the service-worker cache above: glow's SW is Tier-1 with no fetch handler and was NOT the culprit.
**Identify which cache layer is stale before blaming the SW.** (glow, 2026-08-12)
