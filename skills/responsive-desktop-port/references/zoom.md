# "Everything is too small on my big screen": ONE `zoom`, not a re-tune

A phone-first app is written in literal px (`text-[13px]`, `h-[130px]`, ring SVG sizes). On a 1920 screen
it reads small, and the instinct, re-tuning hundreds of literals or adding `lg:text-*` everywhere, is a
huge diff that drifts from `DESIGN_TOKENS.md` and will never be consistent.

## First, prove it is a VIEWPORT question, not a CSS one

Ask for the browser zoom level and a screenshot before touching sizes. "Everything looks huge/tiny" is
usually the user's browser zoomed out or in, which inflates or shrinks the effective CSS width and
stretches every screen; the CSS was never wrong. **A 1440 canvas is not a 1440 viewport**: cap content to
canvas-minus-rail (for example 1368 = 1440 - 72). Retune size with ONE variable, never by re-walking
components. The recall story behind this rule is in `references/history.md`.

## The band

```css
@media (min-width: 1280px) { :root { zoom: 1.15; } .app-min-h { min-height: calc(100dvh / 1.15); } }
@media (min-width: 1680px) { :root { zoom: 1.25; } .app-min-h { min-height: calc(100dvh / 1.25); } }
```

## Things that are NOT optional, each of which bites silently

- **Do not start the zoom at your `lg` breakpoint.** Media queries (yours and Tailwind's) evaluate against
  the **unzoomed** viewport, so at 1024 physical with `zoom: 1.15` the layout still believes it has 1024px
  while only about 890 are painted, which overflows at exactly the width you tested least. Start a band or
  two above `lg`.
- **Correct every viewport UNIT, `vw` too, not just `dvh`.** `zoom` scales the layout but `vw`/`vh` and
  `@media` keep measuring the UNZOOMED window, so at 1920 with `zoom:1.2` `50vw` = 960 while the layout
  only spans 800. A float button placed with `calc(50vw - …)` landed INSIDE the content column over a
  stepper. Fix it with a `--zoom` token mirroring each band, and divide every `vw` expression by it.
- **Correct every viewport-unit height.** `zoom` scales `100dvh` too, so a `min-h-dvh` body gives EVERY
  screen exactly `zoom - 1` of dead scroll: measured 1080px of document in a 1000px viewport, a scrollbar
  with nothing behind it. Divide it back out per step. (`dvh` resolves BEFORE zoom.)
- **Portals re-scale under zoom too.** `@dnd-kit`'s `DragOverlay` mounts on `document.body` (inside the
  zoom) and its measured rect and pointer-delta transform both get re-scaled, so the drag preview starts
  far from the cursor ("appears at the bottom"). Do not use `DragOverlay` under a zoom band; move the real
  node (`useDraggable` transform, already inside the zoom) with the delta divided by zoom. The full recipe
  is in `frontend-interaction-patterns` (@dnd-kit).
- **Cap tall sheets too.** A phone sheet's `h-[Nvh]` resolves against the UNZOOMED viewport, so in a zoom
  band a tall sheet overflows the top and its header and handle go off-screen. Cap `.sheet-surface` per
  band: `max-height: calc(100dvh / <zoom> - 3rem)`.
- **Correct it with a CLASS, not the element.** `body { min-height: … }` (0,0,1) loses to Tailwind's
  `min-h-dvh` class (0,1,0) and silently does nothing. Swap the utility for your own class.

## Measure, do not eyeball

At each band check `scrollWidth === clientWidth` (no horizontal overflow) and
`scrollHeight === clientHeight` on a short page (no dead scroll), plus the phone still reporting
`zoom: 1`. Fixed overlays (a cmdk palette, Vaul sheets) scale and stay centred correctly (verified in
personal-dash), but check yours.
