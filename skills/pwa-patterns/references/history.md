# pwa-patterns - incident history

The stories behind the rules in `SKILL.md`, kept nearly verbatim.

## Patterns proven on real phones (2026-07-06)

All three apps are installed PWAs behind Cloudflare tunnels. The manifest and service-worker patterns are
the ones that survived contact with real phones (2026-07-06).

## sharp already ships with Next 16 (recall, 2026-07-11)

`require('sharp')` resolved inside the app container (confirmed 0.34.5 in recall, 2026-07-11).

## The sticky icon (recall)

Recall shipped a new icon and the phone kept the old one through a reinstall, because Cloudflare's 4h
Browser Cache TTL held the PNG and the OS home-screen icon is sticky on top of that. Versioning the icon
URLs in the manifest fixed it.

## Cache-first without the immutable gate (finance-proj)

That is the "changes aren't deploying" bug that burned finance-proj: installed PWAs kept a stale shell
until manually re-added.

## Auth-gated root icon (recall, 2026-07-12)

recall's `/icon-source.svg` stayed auth-gated and silently 404'd for the installed PWA while the `/icons/`
PNGs worked, so it was easy to miss. The same applied to the Cloudflare Access bypass (2026-07-12).

## Stale data and stale pages (recall, 2026-07-16 and 2026-07-23)

Old DATA after a mutation was RESOLVED 2026-07-16 in recall with network-first navigation; `staleTimes`
was a dead end. Old or blank PAGES for hours after a deploy were fixed 2026-07-23 in recall with
`no-store` on `/sw.js` and a per-build page-cache name. Details are in `references/stale-cache.md`.

## Offline (recall, 2026-07-14 to 2026-07-16)

recall is the only app here that has done offline writes and cold open; the playbook is
`references/offline-playbook.md`.

## iOS duplicate notifications (Aro, 2026-07-16)

Symptom: one event (for example a rest-timer end) delivered **N identical banners to the SAME phone**. Aro
had 3 rows, all one iPhone (identical `device_label` UA, weeks apart), which gave 3x banners. The proven
winner was deduping by device on subscribe; the losing approach was the 404/410 prune alone.

## Launch splash (personal-dash, 2026-07-13)

closet's Vite `<div id="splash">` trick did not port to Next; the `SplashScreen` client component won.
Details are in `references/launch-splash.md`.

## Why stale-after-deploy symptoms load this skill

The old description said: "notifications don't arrive". ALSO first stop when STALE AFTER A DEPLOY: "I don't see the
new version". The stale-after-deploy symptoms are listed as trigger phrases in the current description.
