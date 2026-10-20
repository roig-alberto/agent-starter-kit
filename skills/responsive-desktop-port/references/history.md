# responsive-desktop-port - incident history

The stories and measurements behind the rules in `SKILL.md`, kept nearly verbatim.

## Why the skill exists (closet, personal-dash, 2026-07-22)

An incremental desktop port that *looks* done. Every trap is invisible in the code and invisible in a
phone-width check: the screen renders, nothing errors, and the damage shows up only at a wide viewport or
on a screen nobody re-opened. Two projects hit four of these in one week (closet, personal-dash,
2026-07-22).

## Shell and width tiers (personal-dash, 2026-07-22)

The single-`{children}` shell came from personal-dash, 2026-07-22, and is reusable fleet-wide. The width
tiers gave ~25 screens a decent desktop treatment without 25 bespoke layouts. The longest-prefix width
trap cost a fix twice; it was caught by a sweep, and regression tests now pin the sub-route cases.

## Container query (closet, 2026-07-22)

`DaySuggestions` split into skinny columns inside the Calendar rail. About 30 minutes, with two failed
attempts using media queries first. The panel measured 654px, so the month column narrowed 420 to 360.

## Three mobile-era rules (closet, 2026-07-22)

Double scroll, inline style beating classes, and the `--max-width` fixed layer: about 1h across the three.

## Sheets centred by margin (personal-dash, 2026-07-22)

The `.sheet-surface` class was appended to 52 sheets across 29 files in personal-dash.

## Two nav items, one screen (personal-dash, 2026-07-23)

The USER spotted the duplicate `/objectives?section=goals` destination, not a check.

## The zoom band (recall, 2026-07-23; personal-dash, 2026-07-23; closet, 2026-07-24; personal-dash, 2026-09-14)

In recall a 67-frame port from a 1440 canvas got called "enormous" three times; two full density passes
over 26 components (copying the sibling app's numbers) were BOTH reverted (`3bc4938`) - the user was just
zoomed out. Cost: 2 reverted density passes + 3 rounds with the user.

The zoom band itself and its measurement rules came from personal-dash, 2026-07-23. The `vw` correction
came from closet, 2026-07-24 (about 15 minutes measuring boxes to see why the calc pointed elsewhere), as
did the `DragOverlay` portal finding. The tall-sheet cap came from personal-dash, 2026-09-14.

## Sticky side panel (closet, 2026-07-27)

Three attempts, with measured rects to rule out overflow and transform on ancestors, before making the grid
column sticky.
