---
name: responsive-desktop-port
description: >-
  Ports a phone-first app to a wide desktop screen incrementally, without breaking the phone. Use when asked 'make it work on desktop / big screen / my laptop', 'add a sidebar or rail', 'looks like a stretched phone app', 'port this screen to desktop', 'two-column layout', 'the page scrolls twice', 'the sheet is a full-width bar on desktop', 'two nav icons open the same screen', 'everything is too small / make it bigger / text is tiny on the laptop', 'it splits into two skinny columns inside the panel', 'this component only breaks in the sidebar/rail', or a layout fine at 390px and wrong at 1440px. NOT for phone gestures, bottom navs or iOS safe areas (use frontend-interaction-patterns), NOT for visual direction (use frontend-design).
---

# responsive-desktop-port

This skill ports a phone-first app to a wide desktop screen one piece at a time without costing the phone
anything. The failure it prevents is a port that *looks* done: every trap below is invisible in the code
and in a phone-width check, and shows up only at a wide viewport or on a screen nobody re-opened.

## Rules

- **Render `{children}` exactly once, inside shells toggled by CSS.** Two breakpoint branches mount every
  screen twice, which doubles fetches, timers, and store subscriptions without any visible symptom.
- **Make width a route-table property with three tiers: `own`, `wide`, and `measure`.** The shell then owns
  every screen's width, so dozens of screens get a decent desktop layout without bespoke work.
- **Left-align `measure` (about 820px) and default every unlisted route to it.** A lone centred column
  beside a left rail reads as a mistake, and a later route cannot silently ship stretched to 1400px.
- **Resolve width by EXACT match and the rail highlight by longest prefix.** Reusing the prefix lookup for
  width stretches every `/workouts/*` sub-screen to its parent's tier.
- **Keep thumb-driven flows narrow on purpose.** A set logger or numeric entry screen stays `measure`,
  because wider is not a synonym for improved.
- **Use a container query for a component that lives at two widths.** A media query asks about the window,
  but the component's problem is its own box; measure the real container width before picking the
  threshold.
- **Centre desktop bottom sheets with margin, never `translate`.** Vaul writes an inline `transform` that
  clobbers any `left-1/2 + -translate-x-1/2` centring the moment the sheet is dragged.
- **Give every nav item a distinct route and assert it in a test.** Two icons opening the identical screen
  is a dead affordance that a user will spot before any check does.
- **Fix "everything is too small" with ONE `zoom` band, after asking for the browser zoom level.** Re-tuning
  hundreds of px literals drifts from `DESIGN_TOKENS.md`, and the cause is often just a zoomed-out browser.
- **Start the zoom band above `lg` and divide every viewport unit by the zoom.** Media queries, `vw`, and
  `dvh` all measure the unzoomed window, so they overflow or leave dead scroll without the correction.
- **Make the grid COLUMN sticky, not the panel inside it.** A sticky inner element has no room to stick
  against inside a column only as tall as itself.

## Steps (exit checklist)

Answer each step in the close-out, or write "nothing applies" when it does not. The artifact is this list answered.

1. Render `{children}` exactly once in the shell.
   Done when: grepping the shell for `{children}` finds one match.
2. Resolve every route's width tier by EXACT match, with unlisted routes defaulting to `measure` (left-aligned).
   Done when: a test shows an unlisted route and a sub-route each resolve to their own tier.
3. Wrap any component used in two places in a container-query scope.
   Done when: the component's layout is measured correct at both container widths.
4. Measure `main` scrollHeight AND the document scrollHeight at desktop width.
   Done when: both numbers are quoted and only one scroller is taller than the viewport.
5. Check that no `position: fixed` layer still inherits `--max-width`.
   Done when: each fixed layer's measured width matches the width you intended.
6. Centre every bottom sheet by MARGIN (not `translate`) and cap it at desktop width.
   Done when: after dragging a sheet at 1440px, its left and right margins measure equal.
7. Point every nav item at a DISTINCT route.
   Done when: a test asserts that the nav hrefs are unique.
8. Re-check the PHONE viewport after the desktop pass, because the port must not cost the phone.
   Done when: a 390px check shows no horizontal overflow and the same layout as before the port.

Measurement mechanics (computed styles, scroll heights, overflow hunting) live with `verify-ui-live`; do
not restate them here.

## Gotchas

- **"The page scrolls twice."** A phone-era `main { overflow-y: auto }` coexists with document scrolling;
  compare both scroll heights and remove one scroller.
- **A class cannot turn a strip into a grid.** An inline `display:flex; overflow-x:auto` beats any class;
  extract the inline styles verbatim to a class (verify 0px difference), then restyle.
- **An overlay stops short on desktop and the form shows down both sides.** The `position:fixed` layer is
  capped at `--max-width`; remove the cap and centre its content instead.
- **"It splits into two skinny columns inside the panel."** The component uses a media query; wrap it in
  `container-type: inline-size` and switch to `@container`.
- **A float button lands inside the content column under zoom.** A `calc(50vw - …)` expression measures the
  unzoomed window; divide it by a `--zoom` token.
- **Every screen has a little dead scroll under zoom.** `min-h-dvh` resolves before zoom; divide it back
  out with your own class, because `body { min-height }` loses to the Tailwind utility.
- **The drag preview starts far from the cursor under zoom.** `DragOverlay` portals into the zoom and is
  re-scaled; move the real node instead, as `frontend-interaction-patterns` describes for @dnd-kit.
- **A tall sheet's header goes off-screen under zoom.** Cap `.sheet-surface` per band with
  `max-height: calc(100dvh / <zoom> - 3rem)`.
- **"I tap Add while scrolled down and can't see the menu."** The sticky rule sits on the inner overlay;
  move `position: sticky; align-self: start` to the grid column.

## References

- `references/layout-recipes.md`: the shell, width tiers, container queries, the three mobile-era rules,
  sheet centring, distinct nav routes, and sticky side panels, with code. Read it while porting a screen.
- `references/zoom.md`: the zoom band, its CSS, every unit correction, and how to measure it. Read it for
  any "too small / too big on my screen" report.
- `references/history.md`: the closet, personal-dash, and recall incidents and costs behind these rules.
