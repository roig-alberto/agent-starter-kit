# Interactive primitives (shadcn + Radix)

## Interactive primitives (dialog, dropdown, select, tooltip, popover, toast, tabs, switch) → shadcn + Radix, NEVER hand-roll

**Failure this prevents:** a modal/dropdown/select hand-rolled from `useState` + a `fixed`/`absolute`
div loses focus-trap, ARIA roles, keyboard nav (arrows/Home/End/Esc/Tab), outside-click, scroll-lock,
and focus-return. A keyboard or screen-reader user can often OPEN it but can't drive or dismiss it.
Radix ships all of that, tested; you will get the edge cases wrong. Aro's audit (2026-07-13) found 8
such primitives - a `MealMenu` dropdown with no keyboard/Esc, a `Picker` select with no outside-close,
a `Toggle` switch with no `role="switch"`/`aria-checked` (on/off never announced) - three of them
defined **twice** because there was no shared primitive to reuse.

**shadcn/ui is "own the components", NOT a runtime library.** `npx shadcn add dialog` COPIES the
component source (Radix primitive + Tailwind) into `components/ui/` - you own and restyle it, no
black-box dep. So "we use shadcn" and "our components are bespoke" are the SAME thing; a
custom-looking app still uses shadcn (Aro `IMPLEMENTATION_PLAN.md:15`: "shadcn/ui (own the
components)"). This is why "why hand-roll when shadcn's in the stack?" is a false premise for VISUALS
 - but a real bug when a PRIMITIVE gets hand-rolled instead of `shadcn add`ed.

**The line - hand-roll vs `npx shadcn add`:**

| Build custom (no library equivalent) | `shadcn add` (Radix-backed) |
|---|---|
| Bespoke VISUAL surfaces: rings, gauges, cards, sparklines/charts, streak strips, progress bars, hero layouts | dialog · alert-dialog · dropdown-menu · context-menu · select · combobox(+cmdk) · popover · tooltip · sonner(toast) · tabs · accordion · collapsible · switch · checkbox · radio-group |

Rule of thumb: if it **traps focus**, **floats over** content, or needs **keyboard nav** → Radix
primitive, don't hand-roll. If it's a static/animated visual with no a11y contract → custom is right.
A control duplicated across 2+ files is the promote-to-`components/ui/*` signal.

**Concrete proof a hand-rolled primitive drifts:** recall's hand-rolled toggle rendered its knob
off-centre because an absolutely-positioned knob (`top-[3px] left-[21px]`) is measured from the
track's PADDING box - a 1px `border` (`box-sizing:border-box`) shifted it ~1-2px low and hard against
one edge; the tell was a *no-border* sibling toggle with symmetric `left/right-[3px]` looking fine.
Bit 3 duplicated copies. Minimal fix `top-1/2 -translate-y-1/2` + symmetric insets (border-agnostic);
proper fix the Radix `Switch` (flex `items-center` + thumb `translate-x`, a11y free). Verify by
measuring `gapTop == gapBottom` and equal resting edge-gap in BOTH states - a screenshot won't catch
2px. 2026-07-13.

**Settled exceptions on this box:**
- **Bottom sheets / drawers → `vaul`, not Radix Dialog** - vaul owns the drag-to-close + snap
  momentum Radix lacks (see `references/sheets.md`) and uses Radix Dialog internally, so
  focus-trap/ARIA still hold. Established fleet pattern (Aro nutrition sheets, `focus-sheet`).
- **A Radix popup INSIDE a vaul drawer breaks in two ways - check both, they hide each other.**
  (a) **Unclickable by mouse/finger** (2026-07-18, superhuman-mvp): shadcn's dialog layers default to
  `z-50` while the vaul Drawer overlay is higher (z-90/91), so the drawer overlay intercepts pointer
  events on the nested AlertDialog/Dialog/DropdownMenu. Playwright's tell: click times out with
  `<div data-vaul-overlay> intercepts pointer events`. Fix: raise the nested dialog's overlay+content
  above the drawer (`components/ui/alert-dialog.tsx` `z-50` → `z-[100]`).
  (b) **Keyboard-dead** (2026-07-13, Aro): a portaled Radix `Select`/`DropdownMenu`/`Popover` opens on
  Enter and closes on Esc and taps select fine, but `document.activeElement` stays on the trigger and
  ArrowDown never enters the list (`aria-activedescendant` null) - vaul's FocusScope re-captures focus.
  Radix `Switch` in the same drawer is fully keyboard-operable (in-place button, no portal).
  Fix if keyboard matters: `SelectPrimitive.Portal container={drawerContentRef}` so the content lives
  inside vaul's focus scope (flagged, unverified).
  **Both are invisible to the "obvious" check** - (a) passes focus-trap/a11y assertions, (b) passes
  roles/Esc/tap assertions. When migrating a hand-rolled control to Radix inside a sheet, verify an
  actual CLICK *and* arrow-key focus entry; don't claim "full a11y" from roles alone.
- **shadcn `sonner` in an always-dark app with no `next-themes`** (Aro, 2026-07-13): `npx shadcn add
  sonner` installs `next-themes` and the generated `components/ui/sonner.tsx` calls `useTheme()`. An
  app that hardcodes `<html className="dark">` has no provider → `theme=undefined` → **light toasts on
  a dark app**. Fix: rewrite `sonner.tsx` to drop the next-themes import, hardcode `theme="dark"` +
  app-token classNames, then `npm uninstall next-themes` (now orphaned). Verifying the toast itself:
  `verify-ui-live` (transient UI - a screenshot lies).
- **Native is fine** where it suffices: `<select>`, `<input type=checkbox/radio>`, `<button>`,
  `title=` tooltips - don't Radix-ify a plain native control that already has a11y.
- **A Radix primitive with an unfixable upstream bug → hand-roll that ONE primitive (weighed, not a
  blanket licence).** Recall (2026-07-14): Radix `Select` wraps content in `react-remove-scroll`, which
  locks body scroll on open (`body{overflow:hidden;position:relative}`, NO disable prop in react-select
  2.3.3); on the installed **iOS PWA** that re-resolved `100dvh`/`viewport-fit=cover` and left a gap
  under the fixed bottom nav (headless can't repro it - needs the real device's dynamic viewport). Fix
  = hand-rolled `Dropdown` (`recall/src/components/ui/dropdown.tsx`): button + menu **portalled to
  `<body>` with `position:fixed`** (so no `overflow` ancestor clips it, no portal-less clipping), flips
  up at the viewport bottom, closes on outside-tap/Esc/scroll, and **never touches `body`**. Cost: you
  RE-OWN focus-trap / ARIA / keyboard-nav - so hand-roll only when the bug resists config **and** CSS
  override (try `body[data-scroll-locked]{…}` first) AND escaping it beats re-owning a11y. That
  build-vs-buy call is `research-decision`'s territory: a known unfixable upstream bug is a legitimate
  deciding criterion.

- **A fixed-width Radix popup overflows the phone - clamp with the var Radix already exposes, not a
  media query.** `w-[380px]` on a 390px viewport overflowed; `w-[min(380px,var(--radix-popover-content-available-width))]`
  + `collisionPadding={12}` solves it in one class and leaves desktop intact (measured: 366px at 390,
  380px logical at 1440). Generic to every Radix Popper (popover/dropdown/tooltip/hover-card): it
  exposes `--radix-popper-available-width`/`-height` besides the popover's `-content-` vars. Exactly
  the kind of value you can't guess. (personal-dash 2026-07-23)

**Adding one** (shadcn is already configured in Aro - `components.json` present, but ZERO
`@radix-ui/*` installed; the first add pulls them in):
```
npx shadcn@latest add dropdown-menu select switch tabs sonner
```
Lands in `components/ui/`; restyle with the app's `DESIGN_TOKENS.md`. Replacing a duplicated
hand-rolled control (`Picker`, `Segmented`, `Toggle`) with one Radix wrapper deletes the copies too.

**Migrating a WHOLE tuned app to shadcn (not one component) → `references/shadcn-migration.md`.**
Proven on recall (~30 files, 2026-07-13). The two things that bite first: **never run `shadcn init`
on an app with tuned tokens** (it can clobber `globals.css`) - hand-write `components.json` instead;
and **run `npx shadcn add` IN the dev container** (it has network + `node_modules`; the bind mount
persists the files). The rest - restyle the primitive BASE to the app tokens, one
`cavecrew-builder` per file with a LEAVE-UNTOUCHED list, per-phase `tsc` + pixel-parity pilot, and
which primitives to SKIP - is in the reference.
