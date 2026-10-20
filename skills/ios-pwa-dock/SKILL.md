---
name: ios-pwa-dock
description: >-
  Sets up the iPhone PWA shell (dock, safe areas, status bar) and diagnoses a misplaced dock from device readings. Use when scaffolding an installable app, moving a bottom nav, or on "the dock is too high", "the dock floats", "there's a gap under the dock", "the dock goes back to the bottom when I scroll", "everything is on the top side", "the header is under the notch / status bar", "the dock is stuck in the middle after typing", "do I need to reinstall the PWA?", "the dock again", "same dock issue as the other apps". NOT for a keyboard-shoved sheet (use frontend-interaction-patterns) or manifest, service worker, push (use pwa-patterns).
---

# ios-pwa-dock - the phone shell, and how to diagnose it without guessing

This skill sets up the iPhone PWA shell (dock, safe areas, status bar) correctly at scaffold time, and
diagnoses a misplaced dock from numbers measured on the device. The failure it prevents is the guess loop:
the dock was wrong in eight apps in a row, each re-diagnosed by guessing CSS, redeploying, and asking for
another screenshot. Measure on the device first, then pick the fix from the table, and never ship a second
guess.

## Rules

- **Do not trust headless for any of this.** Headless Chromium and Playwright WebKit have no standalone
  mode, `env(safe-area-inset-*)` is 0, and fixed bars repaint every frame, so a green check is not evidence.
- **Do not ask the user for screenshots.** The launch probe sends the numbers to the server log, which is
  faster and exact.
- **Decide whether a change needs a PWA reinstall BEFORE deploying, and say so in the same reply.** iOS
  copies some settings into the home-screen app only at Add to Home Screen, so a redeploy or reopen does
  nothing for them.
- **Never say "fixed" for a reinstall change until a probe reading from the REINSTALLED app proves it.**
  The old install keeps the old settings.

| Change | Reinstall? |
|---|---|
| `apple-mobile-web-app-status-bar-style`, `apple-mobile-web-app-capable` / `mobile-web-app-capable`, `apple-mobile-web-app-title` | **YES** |
| manifest: `display`, `name` / `short_name`, `start_url`, `scope`, icons, `apple-touch-icon` | **YES** |
| `viewport` meta, `theme-color`, CSS, JS, components, server code | no (fully close the app from the app switcher and reopen) |
| service worker | no, but see `pwa-patterns` stale caches |

When the answer is YES, the deploy reply MUST include these numbered steps:
1. Delete the app from the Home Screen.
2. In Safari open the app URL, then Share -> Add to Home Screen.
3. Open the new icon (log in again).
4. Push notifications: re-enable them in the app's settings (a reinstall mints a new push subscription).

## Steps

1. **New app: apply the shell checklist** in `references/shell-checklist.md`, all of it, at scaffold time.
   The core: `viewport-fit=cover`; status bar style `default`, never `black-translucent`; `theme-color` =
   the background; `min-height: 100dvh`; `--top-space` and `--dock-bottom` variables; an opaque fixed dock
   with `translateZ(0)` and no `backdrop-filter`; `ResumeReseat` mounted once.
   Done when: every box in `references/shell-checklist.md` is ticked in the first UI commit.
2. **A dock or spacing report: measure first.** Paste the probe from `references/launch-probe.md` (about 40
   lines of client code plus a log-only endpoint) and deploy; one headless hit must show a `DIAG` line in
   the server log. Tell the user ONE thing: "open the app from the home screen, wait 3 s, scroll once" (and
   "reinstall first" if a meta tag changed since install). Read the readings yourself
   (`journalctl -u <unit> | grep DIAG` or `docker logs <c> | grep -a DIAG`), keep only `standalone: true`,
   and quote the decisive numbers in the reply.
   Done when: the log shows a `DIAG` line with `standalone: true` and the reply quotes its numbers.
3. **Map the reading to a cause and fix** with the table below.
   Done when: the reply names the matching table row, or states that no row matches.
4. **Verify, then close.** Headless checks only what it can see (served meta tags, CSS variables resolving
   to px rather than 0, layout at 393x793, the area below the status bar); say plainly that it cannot see
   the bug. The next device reading must show the fixed numbers (for example the dock gap equal to
   `--dock-bottom` from the real screen bottom). Remove the probe and its endpoint in the same commit, and
   add a row to the table if it was a new cause.
   Done when: a new device reading shows the fixed numbers and `grep -rn DIAG` finds no probe code in the repo.

| Reading (standalone) | Cause | Fix |
|---|---|---|
| `inner` height = `screen` height - `safe` top, `safe` top > 0, gap shrinks after a scroll | black-translucent iOS 26 viewport regression | status bar `default`, then **reinstall** |
| `vv` height far below `inner` (>100) with no input focused | phantom keyboard inset after typing | `ResumeReseat` |
| dock wrong only on short pages, `bodyH` < `inner` | `height: 100%` / `min-h-full` chain | `min-height: 100dvh` |
| dock moves with scroll, `dockTop` changes with `scrollY` | `backdrop-filter` or no own layer | drop the filter, `translateZ(0)` |
| `safe` bottom far above 34 at launch | inflated bottom inset (public report) | cap: `min(34px, env(safe-area-inset-bottom))` |
| everything matches the CSS, the user still sees it wrong | stale build or old install | check the served HTML, then reinstall |

Add a row only after the fix is proven on the device, with the reading.

## Gotchas

- **The dock floats by exactly the top inset until the first scroll.** The status bar style is
  `black-translucent`; switch to `default` and have the user reinstall, because swapping the capable tag
  or switching to `dvh` alone changes nothing.
- **A JS offset computed from `screen.height - innerHeight` moves the nav.** It jumps on resize and focus
  and pushed the nav off-screen; do not use it.
- **Adding the top inset to shell heights (`100vh + 47px`) seems to fit.** The painted area still ends at
  the short line; fix the status bar style instead.
- **No `first-scroll` reading arrives.** The page did not scroll; ask the user to scroll a long page.
- **A reading looks wrong but comes from Safari, not the installed app.** Filter on `standalone: true`,
  because browser-tab readings include the toolbars.

## References

- `references/shell-checklist.md`: the full scaffold-time checklist, one failure per line. Read it for
  every new installable app.
- `references/launch-probe.md`: the client probe, the server endpoint, and how to read the log. Read it for
  every dock or spacing report.
- `references/history.md`: the agent-factory measurements, the fixes that failed, public sources, and the
  open question about Shelf and Aro.
- Related: `frontend-interaction-patterns` `references/ios-layout-traps.md` holds the per-cause detail for
  fixed-bar traps; `pwa-patterns` owns manifest, service worker, push, and stale caches.
