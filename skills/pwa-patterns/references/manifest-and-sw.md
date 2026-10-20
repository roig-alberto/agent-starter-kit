# Manifest, icons, service-worker tiers, share_target, and install

The detail behind the manifest, service-worker, and install rules in `SKILL.md`. All the fleet apps are
installed PWAs behind Cloudflare tunnels; these are the patterns that survived contact with real phones.

## Manifest (hand-written, per app)

`public/manifest.webmanifest`: `display: standalone`, `scope: /`, **`start_url` = the app's daily screen**
(`/today`), `orientation: portrait`, and theme/background = the app's base color. Icons: SVG (`any`) + PNG
192/512 (`any`) + **512 `maskable`**; the maskable variant is what makes Android icons not look cropped.
Every app has a `gen:icons` script (sharp) generating the set from one source SVG, so regenerate rather
than hand-export. **On Next 16 you do NOT need to add `sharp`**: Next's image optimizer ships it, so
`require('sharp')` already resolves inside the app container (confirmed 0.34.5 in recall). Adding the
devDep costs a `--renew-anon-volumes` rebuild for nothing.

## Changing an icon: VERSION the URL in the manifest

Use `/icons/icon-512.png?v=2`. Cloudflare stamps static assets `max-age=14400` even when the origin sends
`max-age=0` (CF's Browser Cache TTL overrides the origin), so phones hold the OLD PNG for 4h, and the OS
home-screen icon is sticky on top of that. The manifest itself is uncached (`DYNAMIC`), so the OS re-reads
it, and the `?v=2` URLs were never cached, which gives a fresh icon. Then remove and re-add the PWA. The
systemic alternative is setting CF "Browser Cache TTL = Respect Existing Headers".

## Service worker: three proven tiers; pick by need, never exceed it

1. **Push-only, no fetch handler** (Aro `public/sw.js`, 37 lines): install calls `skipWaiting`, activate
   calls `clients.claim`, plus `push` and `notificationclick`. It suits an online-only app; zero cache
   means zero stale-cache bugs. **This is the default for new apps.**
2. **Tier 1 + share_target + an immutable-gated static cache** (Caudal `public/sw.js`): adds cache-first
   for `GET /_next/static/*` ONLY when the response carries `Cache-Control: immutable`. Prod hashed chunks
   cache and `next dev` chunks never do, so tunnel hot-reload stays fresh with ONE sw file for both
   containers. Use it when a rarely-opened PWA feels slow to load. The full rationale and verification are
   in `verify-ui-live/references/gotchas-and-perf.md`.
3. **Precached app-shell** (closet: Workbox `injectManifest`, `precacheAndRoute`, custom `src/sw.ts`): a
   true offline shell. Only for apps that must open offline; it costs cache-invalidation care.

**Never** add a cache-first fetch handler without the immutable gate. That is the "changes aren't
deploying" bug (installed PWAs kept a stale shell until manually re-added).

## share_target (Caudal)

Manifest `share_target`: `POST /share-target`, multipart, accepting CSV/XLS/XLSX/XML; the SW forwards the
POST. It lets the phone "share" a bank export straight into the import wizard. Copy this shape for any
file-intake app.

## Install details

- **Status bar style: `default`, never `black-translucent`.** The iOS 26 standalone viewport comes up short
  by the top inset and every fixed bottom bar floats. The shell checklist and diagnosis are in
  `ios-pwa-dock`.
- **Auth middleware must allowlist** `/manifest.webmanifest`, `/sw.js`, and `/icons/*`, because an
  auth-gated manifest breaks install silently. **The trap is an icon at the public ROOT, outside the
  `/icons/` prefix**: recall's `/icon-source.svg` (referenced by both the manifest AND layout `icons.icon`
  = favicon) stayed auth-gated, redirected to `/login`, and silently 404'd for the installed PWA while the
  `/icons/` PNGs worked. Enumerate every path the manifest and layout reference, not just the prefix. The
  same applies to the Cloudflare Access bypass.
- **Cloudflare Access blocks WebAPK minting** (the Android icon opens Chrome instead of standalone). Add a
  scoped Access Bypass for the manifest and icon paths; the runbook is in `fleet-ops`
  `references/cloudflare-tunnel.md`.
- **After changing the SW, installed clients self-heal only on next launch** (about a daily check); a
  one-time remove and re-add of the PWA forces it. Verify what the container actually serves first:
  `curl -s http://localhost:<hostport>/sw.js` (host ports are in `~/.claude/FLEET.md`).
- **Verify install-affecting changes at phone width against the live tunnel** (`verify-ui-live`).
