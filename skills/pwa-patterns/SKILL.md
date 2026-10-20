---
name: pwa-patterns
description: >-
  PWA mechanics: manifest, icons, service-worker tiers, Web Push and VAPID, share_target, offline writes, launch splash, and stale-after-deploy fixes. Use when making an app installable, changing a service worker or manifest, or on "make it installable", "add push notifications", "PWA icon", "add to home screen", "notifications don't arrive", "I don't see the new version", "blank page after deploying", "it's showing the old UI", "something is cached", "only reinstalling the PWA fixes it", "it loses my changes with no signal", "queue the writes", "make it work offline / on the metro", "offline outbox", "Serwist", "precache the shell", "launch splash". NOT for the iPhone dock or safe areas (use ios-pwa-dock).
---

# pwa-patterns - installable apps on this fleet

This skill covers the mechanics of the fleet's installed PWAs: manifest and icons, the service-worker tier,
Web Push, share_target, offline support, and the launch splash. It prevents the expensive PWA failures:
an install that breaks silently, an installed app stuck on an old version after a deploy, and duplicate
or missing notifications on iOS.

## Rules

- **Hand-write the manifest per app** with `display: standalone`, `scope: /`, `start_url` set to the app's
  daily screen, and a 512 `maskable` icon, because the maskable variant is what keeps Android icons from
  looking cropped.
- **Regenerate icons with the app's `gen:icons` script**, never by hand-export, and do not add `sharp` on
  Next 16, because Next already ships it.
- **Version icon URLs in the manifest when an icon changes** (`/icons/icon-512.png?v=2`), because
  Cloudflare pins static assets for 4h regardless of the origin's headers.
- **Pick the lowest service-worker tier that meets the need:** push-only with no fetch handler (the
  default), then an immutable-gated static cache, then a precached app-shell. Every cache you add is a
  stale-cache bug you can ship.
- **Never add a cache-first fetch handler without the `Cache-Control: immutable` gate**, because that
  keeps installed PWAs on a stale shell until they are re-added.
- **Serve navigation network-first** in any SW that caches, because cache-first navigation is what shows
  old data after a mutation.
- **Send `no-store` for `/sw.js` and `/manifest.webmanifest`, and name the SW page cache per build**, so
  Cloudflare cannot pin an old service worker that points at chunks the new build no longer serves.
- **Mark a URL `immutable` only if it is content- or version-addressed**, because `immutable` never
  revalidates and only a URL change reaches clients that cached it.
- **Set `VAPID_SUBJECT` to a real `mailto:`**, because Apple rejects placeholders.
- **Dedupe push subscriptions by device on subscribe, and prune rows on 404/410**, because iOS mints a new
  live endpoint on every reinstall and the prune never catches those.
- **Allowlist every path the manifest and layout reference** in auth middleware and in the Cloudflare
  Access bypass, not just the `/icons/` prefix, because an auth-gated manifest or icon breaks install
  silently.
- **Use status bar style `default`, never `black-translucent`**; the shell checklist and diagnosis live in
  `ios-pwa-dock`.
- **Never promise haptics or push outside the installed app.** iOS Web Push works only for the installed
  PWA over real HTTPS, and `navigator.vibrate` is unsupported.

## Steps for offline support and the launch splash

1. **Offline writes first:** an IndexedDB mutation outbox that persists BEFORE the network, advances the UI
   optimistically, and flushes through one adapter. The playbook is `references/offline-playbook.md`.
   Done when: a write made with the network off sits in the IndexedDB outbox and is flushed after reconnect.
2. **Cold open second:** hard navigations for offline-critical routes and static client shells that read
   IndexedDB. Use a hand-rolled `workbox-build.getManifest` + esbuild precache on Next 16, because Serwist
   lost there.
   Done when: a cold open with the network off renders the offline-critical route from the precache.
3. **Verify the functional half headless** before any device round-trip, and reserve the phone for iOS
   safe-area cosmetics.
   Done when: the headless offline run passes before the first device round-trip.
4. **Launch splash on Next:** a `"use client"` `SplashScreen` in `app/layout.tsx`, hidden via state and
   unmount after `max(MIN_MS, time-to-interactive)`. The recipe and how to verify it are in
   `references/launch-splash.md`.
   Done when: the served SSR HTML (`curl -s`) contains the splash markup.

## Gotchas

- **"I don't see the new version" / "blank page after deploying", localhost fine.** Compare origin and edge
  headers first: `curl -sI https://<host>/sw.js | grep -i "cache-control\|cf-cache-status"`. A
  `REVALIDATED` with a `max-age` you did not set means the edge is pinning the old SW; follow
  `references/stale-cache.md` section 2.
- **Old data after a mutation, and "only reinstalling the PWA fixes it".** The SW navigation is
  cache-first; `staleTimes` is a dead end. Switch to network-first navigation (`references/stale-cache.md`).
- **The phone keeps rendering year-old content from an API URL.** The URL is `immutable` but its bytes
  changed; put a version token in it and identify which cache layer is stale before blaming the SW.
- **A new icon never shows up, even after reinstalling.** Version the icon URLs in the manifest, then
  remove and re-add the PWA, or set CF "Browser Cache TTL = Respect Existing Headers".
- **One event delivers several identical banners to the same iPhone.** Stale same-device subscriptions are
  still live; dedupe by `device_label` on subscribe (`references/web-push.md`).
- **Install breaks silently, or one icon 404s only in the installed app.** A manifest or icon path outside
  the allowlisted prefix is auth-gated; enumerate every referenced path.
- **The Android icon opens Chrome instead of standalone.** Cloudflare Access blocks WebAPK minting; add the
  scoped bypass from `fleet-ops` `references/cloudflare-tunnel.md`.
- **A SW change does not reach installed clients.** They self-heal only on the next launch; check what the
  container serves with `curl -s http://localhost:<hostport>/sw.js` (ports in `~/.claude/FLEET.md`), then
  have the user remove and re-add the PWA if it cannot wait.
- **The launch splash cannot be screenshotted.** A warm dev container hydrates before Playwright's
  navigate resolves; assert the splash is in the SSR HTML instead (`references/launch-splash.md`).
- **An iOS PWA's EventSource (SSE) dies while the phone is locked or backgrounded** and may not come back. Close and reopen it on `visibilitychange` to visible, and have the server send a hello event that makes screens refetch.

## References

- `references/manifest-and-sw.md`: the manifest, icon versioning, the three SW tiers, share_target, and
  install details. Read it before making an app installable or changing its SW.
- `references/web-push.md`: the VAPID, routes, send, dedupe, and SW-side recipe. Read it before wiring push.
- `references/stale-cache.md`: the two stale-cache failures and the `immutable` trap, with fixes.
- `references/offline-playbook.md`: the offline outbox and cold-open recipe from recall.
- `references/launch-splash.md`: the Next SSR launch splash and how to verify it.
- `references/history.md`: the incidents behind these rules.
