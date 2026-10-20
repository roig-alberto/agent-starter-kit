# ios-pwa-dock - incident history and sources

The stories, measurements, and failed fixes behind `SKILL.md`, kept nearly verbatim.

## Why the skill exists (agent-factory, 2026-10-13)

The dock was wrong on the iPhone in EIGHT apps in a row, each time re-diagnosed from scratch by guessing
CSS (`dvh`, `translateZ`, meta tags), redeploying, and asking the user for another screenshot. On
2026-10-13 (agent-factory) four guessed fixes in a row failed before one measurement from the phone named
the cause in a single reading.

## Reinstall rounds

The user had to reinstall for the status bar fix on 2026-10-13; the earlier capable-tag change also needed
one.

## The black-translucent measurements

Measured `innerHeight` 793 of a 852 screen, inset 59 (agent-factory 2026-10-13); 797 of 844 with inset 47
and 812 of 874 with inset 62 in two public reports.

The decisive line (iPhone, iOS 26.5, standalone, black-translucent):
`inner [393,793] screen [393,852] vv [393,793,0] safe ["59px","34px"] dockBottomGap 44`, meaning the
viewport was short by exactly the 59px top inset and the dock sat 44 + 59 = 103px above the real bottom. On
that page nothing scrolled, so no `first-scroll` reading arrived; scroll a long page.

Proven 2026-10-13: after the reinstall with status bar `default`, `safe` top 0, `inner` 793 = 852 - 59 (the
page starts below the status bar), and `dockBottomGap` 44 from the real bottom (was 103).

## What did NOT work (each cost a deploy round on 2026-10-13 or in public reports)

- Swapping `apple-mobile-web-app-capable` for `mobile-web-app-capable`: no change (793 again).
- `height: 100%` -> `min-height: 100dvh` plus `translateZ(0)` alone: no change when the cause is the
  status bar style (dvh itself reads 793 there).
- A JS offset from `screen.height - innerHeight` translating the nav: jumps on resize and focus, pushed the
  nav off-screen (public PR, removed).
- Adding the top inset to shell heights (`100vh + 47px`): the painted area still ends at the short line
  (public PR, reverted).

## Sources

agent-factory probe 2026-10-13, before and after the reinstall (`web/src/lib/diag.ts`, readings in the
service journal); github.com/dylanlegouellec-jpg/grimoire-morgane/pull/1 (status bar `default` fix,
812/874); github.com/tpdbf5509/busssss/pull/23 (797/844 measurements, WebKit bug 301108 cited,
unverified); github.com/alidd11/rider-comms/pull/128 (inflated bottom inset cap). Verified 2026-10-13.

## Open question

Why Shelf and Aro (also black-translucent) do not show it was not measured; probe them before assuming they
are immune.
