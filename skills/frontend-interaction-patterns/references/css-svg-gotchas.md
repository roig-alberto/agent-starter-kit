# Cross-platform CSS / SVG gotchas

## Cross-platform CSS / SVG gotchas (Aro, 2026-07-17)

- **daisyUI v5 exposes colour tokens in OKLCH components, not hex/HSL.** `--p` computes to
  `67.45% 0.166 153.7`, so raw CSS must wrap it: `oklch(var(--p))`. A bare `var(--p)` is an invalid
  colour and the browser ignores it **silently**.
- **Overriding a third-party library's own CSS variables must happen ON the library's root
  element, not a parent.** react-day-picker declares `.rdp-root { --rdp-accent-color: blue }`; an
  element's own declaration beats an inherited one, so setting the var on a wrapping div does
  nothing. Pass it through the library's `style` prop. Combined symptom: the date picker stayed
  blue despite the var being set on the wrapper - fixed with `oklch(var(--p))` in `DayPicker`'s own
  `style`. Date-picker winner: **react-day-picker v9** (no extra deps, i18n via `Intl`, no
  date-fns). (caudal, 2026-09-01)

### The "box on tap" - kill it globally, once
Tapping a link/button on mobile draws a rectangular box around it (users report it as "the
rings have a box"). TWO causes, both fixed with a global base-layer rule (do this in every
app's `globals.css` up front - it recurred across Aro screens):
```css
@layer base {
  * { -webkit-tap-highlight-color: transparent; }        /* the grey flash box on tap */
  :focus:not(:focus-visible) { outline: none; }          /* the focus-outline box on pointer/touch */
}
```
`:focus-visible` keeps the keyboard outline (a11y intact). Verify with a real pointer press
(Playwright `mouse.down()`, not `.focus()` which falsely reports focus-visible=true): the
element should compute `outline-style: none` and match `:focus:not(:focus-visible)`.

### iOS Safari does NOT render CSS `filter: drop-shadow()` on SVG elements - use `feDropShadow`
A glow/shadow set as CSS `style={{ filter: 'drop-shadow(0 0 7px ...)' }}` on an SVG `<circle>`/
`<path>` shows on **Android Chrome but is invisible on iOS Safari/WebKit** (the classic "the
glow only shows on Android" bug). It also clips at the SVG viewBox edge. Fix = a real SVG
`<filter>` referenced via the `filter` ATTRIBUTE, plus `overflow:visible` so the halo isn't
clipped:
```jsx
<svg viewBox="0 0 120 120" style={{ overflow: "visible" }}>
  <defs><filter id={fid} x="-50%" y="-50%" width="200%" height="200%">
    <feDropShadow dx="0" dy="0" stdDeviation="3.4" floodColor={color} floodOpacity="0.9" />
  </filter></defs>
  <circle ... filter={active ? `url(#${fid})` : undefined} />
</svg>
```
`feDropShadow` is supported on iOS 12+. Headless Chromium == Android here; the iOS render can
only be confirmed on a real device - say so. Reference: Aro `components/today/hero-trio.tsx`.

### Percentage-height bars inside a flex column collapse to ~0 - use pixel heights
A bar chart column `<div style={{height: `${v/max*100}%`}}>` inside a `flex items-end` track
renders as a thin sliver: a percentage height needs a parent with a *definite* resolved height,
which a flex item often isn't. Compute an explicit px height instead:
`height: (v/max) * CHART_PX` in a fixed `h-[96px]` row. Symptom: "the weekly bars are flat".
Reference: Aro `components/trends/recovery-detail.tsx` weekly-pattern bars.

### Decimal `<input inputMode="decimal">` must accept a COMMA separator (es-ES/EU keyboards)
An `inputMode="decimal"` field on a Spanish/most-EU iOS keyboard emits "," as the decimal key, but
`Number("68,5")` is `NaN` and `parseFloat("68,5")` TRUNCATES to 68 - so the value silently logs 0 /
the Save button stays disabled ("the keyboard has commas but it won't accept them"). **Fix:** a shared
`parseDecimal(v) = Number(String(v).replace(",", "."))` (NaN for blank/garbage so callers keep their
`|| 0` / `Number.isFinite` guards); use it at EVERY parse site (save handler AND the `disabled` check).
It's a strictly-safe widening - identical for dot/integer input, only adds comma tolerance - so replace
`Number(x)`/`parseFloat(x)` on any input string with it. `inputMode="numeric"` fields are exempt (that
keyboard has no separator). Reference: Aro `lib/utils.ts` `parseDecimal` (and the pre-existing
`lib/nutrition/parse.ts` `parseNum` - same idea, already done for nutrition). Cost: reported once per
module (measurements → weight → workouts) before sweeping all decimal inputs. 2026-07-19.

**Sweep gotcha (Aro, second pass):** a sweep that only replaces `parseFloat(` MISSES the sibling
`+state` and `Number(state)` forms (the barcode manual-add used `+mKcal`, `+mP || 0`) - same bug, other
syntax. Grep ALL THREE (`parseFloat(x)`, unary `+x`, `Number(x)`) against every `inputMode="decimal"`
state before calling the sweep done. Two-occurrence pattern: Caudal already guarded each `parseFloat`
with `.replace(",",".")` but never wrote it up, so Aro re-hit a bug the fleet already knew.

- **A scrolling grid** (fixed height, `overflow: auto`) whose items are `overflow: hidden` with an aspect ratio
  collapses its auto rows to about 0 and stacks every item on one spot. Set `grid-auto-rows: max-content` (Shelf).
- **An unlayered global rule beats Tailwind 4 utilities**, which live in `@layer`: `h1, h2, h3 { font-family: serif }`
  makes `font-sans` on an h2 do nothing. Put global base rules inside `@layer base` (Shelf).
- **Tailwind v3 emits no rule for `bg-primary/10`** when the colour is a bare `var(--primary)`. Define a space-separated
  `--primary-rgb` and set the colour to `rgb(var(--primary-rgb) / <alpha-value>)`; find it by grepping the compiled CSS
  for the rule (personal-dash).
