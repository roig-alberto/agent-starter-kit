# Offline playbook - making a Next App Router PWA work without signal

Everything here was proven on `~/projects/recall` (2026-07-14 → 2026-07-16). Pointer lives
in `SKILL.md`. Two independent halves: **writes that survive offline** (the outbox) and
**opening the app offline** (the static shell). Ship the outbox first - it is smaller and
independently useful.

## 1. Offline mutation OUTBOX (recall Phase-1, first-try clean)

Problem class: the app mutates via a server-action network POST, so it **silently loses the
write offline** (metro tunnel). The pattern:

1. **Persist first, network second.** Write each mutation to an **IndexedDB outbox** the
   instant it is triggered (`idb`, keyPath = a client-generated uuid) BEFORE the POST - this
   survives an app KILL, not just signal loss. Real code: `src/lib/offline/{db,queue-store,
   rating-queue}.ts`.
2. **Advance the UI optimistically - never `await` the POST inside the transition.** The
   old code did, so a rejected await skipped the advance = stuck card with no feedback.
   Guard double-fire with a per-item ref.
3. **Flush through ONE shared adapter**, triggered on the `online` event + on app load (a
   root-layout `"use client"` flusher catches a PRIOR session's buffered writes) + after
   each online action.
4. **Idempotency WITHOUT a migration.** Reuse the table's existing settable uuid PK as the
   client key and guard `SELECT WHERE id=?` → skip. The server action returns a
   discriminated `ok | skip | gone` (`gone` = row deleted → drop, don't retry); a THROW is
   transient (keep, retry, drop as poison after N attempts).
   *Rejected:* adding a `clientId` unique column - the PK was already settable, so the
   migration was avoidable.
5. **Thread the CLIENT timestamp, CLAMPED server-side to `[now-24h, now]`** so time-sensitive
   logic (FSRS intervals, day-keyed streak) uses tap-time not flush-time, bounded against a
   bad device clock. *Rejected:* flush-time timestamps - they drift scheduling and put the
   streak on the wrong day across midnight.

Test it with `fake-indexeddb` in the node vitest env - recipe in `testing`.

## 2. Opening the app offline (the harder half)

- **In-app `next/link` taps are SOFT navs = RSC fetches that FAIL offline and never reach
  the SW.** Fixes: (a) an offline-critical route → a plain `<a>` HARD nav so the SW serves
  the precached static shell; (b) the tab bar → soft nav online, hard nav when
  `!navigator.onLine`; plus a SW `warm-pages` message that caches the top-level nav HTML
  while online, giving last-known-data offline. Cost: multiple blind device round-trips
  before a headless repro existed.
- **Offline-functional page pattern:** convert an SSR-data page into a STATIC client shell
  that loads its data from IndexedDB (offline) / the API (online). Then it precaches and
  cold-opens offline. Live data (the review due-queue) = IndexedDB prefetch +
  replace-snapshot store; writes were already covered by the outbox above.
- **Serwist LOST on Next 16 - hand-rolled precache won.** Next 16 builds Turbopack by
  default; `@serwist/next`'s webpack path forces `next build --webpack`, and
  `@serwist/turbopack` serves the SW from a route handler (which conflicts with a static
  `/sw.js`). Winner: `workbox-build.getManifest` + an esbuild bundle that define-injects the
  manifest - bundler-agnostic. (2026-07-16)
- **iOS standalone drops `viewport-fit=cover` on `next/link` nav**
  (vercel/next.js#81264) → fixed bottom bars lift. A LIGHT attribute toggle (auto→cover in a
  rAF) on route change fixes it online. A heavier remove+reinsert of the meta node also fixed
  the offline fresh-load BUT reflowed the viewport on every nav = slow online switches
  (reverted). Offline hard-load lift is an accepted iOS limitation.

## 3. Verifying offline WITHOUT device round-trips

Headless Playwright against a temp prod container on public routes **can** verify the
functional half - SW install, precache contents, shell render offline. It **cannot** verify
iOS safe-area / viewport cosmetics (headless reports 0 insets). **Always verify functional
headless BEFORE any device round-trip**; reserve the phone for cosmetics.
