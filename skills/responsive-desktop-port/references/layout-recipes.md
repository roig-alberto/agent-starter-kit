# Desktop port recipes: shell, width tiers, container queries, sheets, nav, sticky panels

The detail and code behind the rules in `SKILL.md`. The zoom band has its own file,
`references/zoom.md`, and the incidents behind each recipe are in `references/history.md`.

## 1. The shell: render `{children}` ONCE, toggled by CSS

Two breakpoint BRANCHES (`isDesktop ? <DesktopShell>{children}</DesktopShell> : <MobileShell>…`) mount
**every screen twice**: double fetches, double timers, double store subscriptions. It is not a rendering
bug you will see; it is a load and correctness bug you will not.

Render one `{children}`, inside shells toggled with CSS. A route table drives the rest: the rail or
sidebar active state, the page title, and the per-route width tier below. This is reusable fleet-wide.

## 2. Width is a route-table PROPERTY, resolved EXACT-match; the nav key is not

Do not model this as a boolean "ported". Three tiers, looked up per route, let the SHELL own every
screen's width, which is how about 25 screens got a decent desktop treatment without 25 bespoke layouts:

| tier | meaning |
|---|---|
| `own` | the screen has a real desktop layout (grid/rail); shell imposes no cap |
| `wide` | no bespoke layout, but reads better wide - charts, tables, calendars |
| `measure` | capped (~820px) and **LEFT-aligned**; lists, forms, and the DEFAULT for anything unlisted |

Two things are easy to get backwards:

- **`measure` is left-aligned, not centred.** A lone centred column beside a left-anchored rail reads as a
  mistake. Centred is right only when there is no rail.
- **Default unlisted routes to `measure`, never to full width**, so a route added later cannot silently
  ship stretched to 1400px.

The nav-highlight key uses **longest-prefix** matching (`/workouts/123` highlights `/workouts`), and
reusing that lookup for width marked every `/workouts/*` sub-screen as its parent, stretching all of them.
**The rail key cascades to children by design; "how wide is this screen" must NOT.** Use exact-match for
width (a detail view may inherit a listed parent's width but never its `own`) and prefix-match for the
rail. Pin the sub-route cases with regression tests.

**Not everything wants the width.** One-handed, thumb-driven flows (a set logger, a numeric entry screen)
stay `measure` on purpose, because a 1300px set row is worse, not better. "Wider" is not a synonym for
"improved".

## 3. A component reused at TWO widths needs a CONTAINER query, not a media query

`DaySuggestions` is full-width in Suggestions and lives in a narrow rail in Calendar. With
`@media (min-width:1024px)` it split into two unusably skinny columns *inside the rail*, because a media
query asks about the WINDOW, and the component's problem is its own box.

```css
.ds-scope { container-type: inline-size; }        /* wrap the component */
@container (min-width: 700px) { /* the split */ } /* each site decides with ITS width */
```

**Measure the real width before assuming it fits.** The panel measured 654px, so the month column had to
narrow (420 to 360) to clear the 700px threshold.

## 4. Three mobile-era rules that sabotage a desktop viewport (all invisible in the code)

1. **`main { overflow-y: auto }` plus the document scroll means you must scroll TWICE.** It is a phone-era
   rule that coexists with document scrolling. The tell is measurable, not visual: `main` at 1101/1047 AND
   the document at 1047/900. Check both scroll heights, not just the page's.
2. **An INLINE style beats any class.** A strip carrying `display:flex; overflow-x:auto` inline cannot be
   turned into a grid by a class, no matter the specificity. Extract those inline styles to a class first,
   copying them **verbatim** and verifying a **0px difference**, then restyle.
3. **A `position:fixed` layer capped at `--max-width` leaks on desktop.** On the phone the cap is invisible
   (480px IS the screen); on desktop the overlay stops short and the form shows down both sides. Remove the
   cap from the fixed layer and centre its CONTENT instead.

## 4b. Bottom sheets: centre with MARGIN, never `translate`

A phone bottom sheet (`fixed inset-x-0 bottom-0`) becomes a 1400px-wide bar on desktop. The fix is a
centred floating card, but **Vaul writes an inline `transform` to drive its open and drag animation**, so
any `left-1/2 + -translate-x-1/2` centring is clobbered the moment the sheet is dragged. Margins are
untouched by that:

```css
@media (min-width: 1024px) {          /* one class, applied to every sheet */
  .sheet-surface { margin: 0 auto 1.5rem; max-width: 560px; border-radius: 24px; border-width: 1px; }
}
```

Declare it once and append the class per sheet rather than repeating a utility string; place it AFTER the
Tailwind layers so it beats the mobile `rounded-t-*` / `border-t` on the same elements. Keep the drag
pill, because Vaul's drag works with a mouse.

## 4c. Two nav items must never open the same screen

A rail item pointing at `/objectives?section=goals` while nothing read that param gave two icons that
highlighted differently and opened the **identical** screen, a decorative second button. Give the second
item a real route (reuse the same reader or component, so there is no second implementation) and assert it
mechanically:

```ts
const hrefs = RAIL_ITEMS.map(i => i.href);
expect(new Set(hrefs).size).toBe(hrefs.length);   // distinct destinations
```

This is the same family as the dead-affordance rule: a control that looks like it does something must.

## 4e. A sticky side panel sticks on the grid COLUMN, not the inner element

A desktop side panel that scrolls out of view when you go down usually has `position:sticky` on the wrong
node. Sticky on the inner overlay (`.cls-sheets .sheet-overlay { position:sticky; top:18px }`) does NOT
engage, because its container (the grid column) is only as tall as the panel, leaving no room to stick
against (measured: `top -222` with the page at the bottom). `align-self:stretch` on the column is not
enough either. What works is making the COLUMN itself sticky and leaving the overlay static inside:

```css
.cls-sheets { position: sticky; top: 18px; align-self: start; }  /* the standard grid-sidebar pattern */
```

The user symptom was: "I tap Add while scrolled down and can't see the menu, I have to scroll up."
