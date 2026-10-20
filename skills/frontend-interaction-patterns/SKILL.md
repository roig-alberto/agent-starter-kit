---
name: frontend-interaction-patterns
description: >-
  Picks the library and pattern for interaction primitives and fixes phone traps: drag-and-drop, swipes,
  sheets, chart scrubbing, long-press, bottom navs, optimistic lists, date pickers, shadcn/Radix, Sonner
  toasts. Use when adding one, on "shadcn", "radix", "add a UI component", "replace the native date input",
  "what should I use for X", or symptoms: list stale until reload, can't tap inside a sheet/menu/calendar,
  modal behind the nav, keyboard covers the sheet input, a select or picker that feels finicky or slow to
  scroll, edit form opens blank, commas rejected in a decimal input, Radix dialog dead inside a vaul drawer,
  "the toast never shows/appears", "toast behind the modal", "toasts are doubled". NOT for desktop ports (use
  responsive-desktop-port) or motion feel (use animate).
---

# Frontend interaction patterns (cross-project)

This skill picks the LIBRARY and the pattern for interaction primitives in React/Next + Tailwind apps
(drag-and-drop, sheets, gestures, date pickers, dialogs, menus, toasts) and holds the phone and iOS traps
that come with them. It prevents hand-rolled primitives that lose accessibility, gestures that fight
scrolling, toasts that never show, and phone-only layout bugs that a headless check calls fine. How the
motion should FEEL once the library is chosen belongs to `animate`.

## Picking a library

- **Check `package.json` first, then look the task up in `references/library-list.md`.** Recommend one
  library from the list, because a menu of generic alternatives wastes the curated answer.
- **Keep what the project already uses.** Flag a listed alternative, but never swap a dependency unasked,
  because a swap is its own decision (`research-decision`).
- **On this box the primitive layer is shadcn + Radix, not the list's base-ui.** Aro, recall and Agent
  Factory ship it, and the traps below are written for it.
- **Toasts are Sonner, through the shadcn `sonner` component where shadcn is present.** A hand-rolled or
  modal-library toast loses stacking, swipe, and timing.

## Rules

- **Use @dnd-kit for drag-and-drop and sortable lists; never hand-roll pointer-event reordering.** It
  handles touch, mouse, and keyboard accessibly, while a hand-rolled version drowns in scroll, selection,
  and stale-state edge cases.
- **Use shadcn + Radix for anything that traps focus, floats over content, or needs keyboard nav**
  (dialog, dropdown, select, tooltip, popover, toast, tabs, switch). A hand-rolled one loses focus-trap,
  ARIA, Esc, and outside-click. Build custom only for bespoke visuals, and keep native controls where they
  suffice.
- **Use `vaul` for bottom sheets and drawers, not Radix Dialog.** vaul owns drag-to-close and snap momentum
  and still uses Radix Dialog internally.
- **Give a sheet with inputs a FIXED-height flex frame, a pinned header, and one inner scroll region, with
  `repositionInputs={false}` and no `autoFocus`.** Otherwise iOS shoves the whole sheet off the top when
  the keyboard opens.
- **Use react-day-picker (shadcn Calendar) in a bottom sheet for dates**, and parse "YYYY-MM-DD" at local
  noon, because the native date input is unstylable and `toISOString()` rolls the day back.
- **Prefer pointer events** (`onPointerDown/Move/Up` + `setPointerCapture`) over separate mouse and touch
  handlers, because one code path serves both and capture keeps events flowing outside the element.
- **Scope `touch-action: none` to the gesture handle**, so the rest of the page still scrolls.
- **Hold a gesture's live values in refs, not state.** State updates are batched, so a fast flick reads
  stale values and does nothing.
- **Make optimistic UI the norm**: update locally, persist in the background, and reconcile on the server
  round-trip.
- **Parse every `inputMode="decimal"` value with a shared `parseDecimal`** that accepts a comma, because
  EU keyboards emit "," and `Number("68,5")` is `NaN`.
- **Mount exactly one `<Toaster />` at the root and call `toast()` only from client code.** A second
  Toaster doubles every toast, and `toast()` does nothing on the server.
- **Set the Toaster theme explicitly** (`theme="system"` or the resolved theme), because it defaults to
  `'light'` and ignores the OS.
- **Kill the tap-highlight box globally** in every app's `globals.css` with
  `-webkit-tap-highlight-color: transparent` and `:focus:not(:focus-visible) { outline: none; }`.
- **Send iPhone dock and shell work to `ios-pwa-dock` FIRST.** It has the shell checklist, the launch
  probe, and the readings table; the traps below are the per-cause detail it points into.
- **Let the SHELL own bottom clearance.** A screen adds its own `pb-*` only if it has its own fixed
  element, because extra length strands fixed bars on iOS.
- **Verify on a real phone-width DOM (about 375-390px)** with `verify-ui-live`, because headless resolves
  `env(safe-area-inset-*)` to 0 and repaints `fixed` elements every frame.

## Red flags

- **Calling a tap fixed because a synthetic `.click()` passed.** It skips hit-testing; check with
  `document.elementFromPoint` (shipped "can't tap the calendar" twice, `references/history.md`).
- **Letting a green headless check overrule a phone report.** The fixed-bar strand was green headless
  before and after its fix; trust the phone screenshot (`references/history.md`).

## Gotchas

- **List stale until reload after a create or delete.** A list seeded with `useState(props.items)` under a
  React Server Component needs `useEffect(() => setItems(props.items), [props.items])`
  (`references/dnd-kit.md`).
- **Can't tap inside a sheet, menu, or calendar on the phone, but the test passes.** A portal inside a
  vaul or Radix modal inherits `pointer-events: none`; add `pointer-events-auto` to the portal root.
- **A Radix dialog is dead inside a vaul drawer.** Raise the nested dialog above the drawer overlay
  (`z-50` to `z-[100]`) and check arrow-key focus entry too (`references/interactive-primitives.md`).
- **Modal behind the nav, or a full-screen overlay covered by the fixed nav.** Use
  `createPortal(node, document.body)`, NOT a higher z-index; `elementFromPoint` over the nav is the tell.
- **Keyboard covers the sheet input.** Use the fixed-height frame for vaul, or bind a hand-rolled sheet to
  `visualViewport` height AND `offsetTop` (`references/sheets.md`).
- **Edit form opens blank.** A child `useState` seeded from an async parent hook seeds empty; pass the
  resolved entity down as a prop with `key={id}` (`references/react-structure-traps.md`).
- **Commas rejected in a decimal input.** Replace `parseFloat(x)`, unary `+x`, and `Number(x)` with
  `parseDecimal` at every parse site, including the `disabled` check.
- **The toast never shows.** No `<Toaster />` is mounted, it sits below an early `return`, or `toast()`
  ran on the server; mount one at the root and toast the action's result on the client.
- **Toasts are doubled.** Two Toasters (layout and page) or an effect under StrictMode; keep one Toaster
  and fire from the event handler or pass a stable `id`.
- **Toast behind the modal, unstyled, or light on a dark app.** Move `<Toaster />` to the document root,
  import `sonner/dist/styles.css` if styles were lost, and set `theme` (`references/sonner-troubleshooting.md`).
- **Icons crammed at the TOP of the bar, phone only.** `pb-[env(safe-area-inset-bottom)]` sits on the
  fixed `h-16` row; move it onto the `<nav>` or drop it (only apps with `viewport-fit=cover`).
- **Bar floats up with a gap below it, only on SHORT pages.** The `min-h-full` chain collapses; use
  `min-h-[calc(100dvh_-_env(safe-area-inset-top))]` or `min-h-dvh`.
- **A CTA above the nav drifts to the TOP of the page on iPhone.** Make it `fixed bottom-16` (not
  `absolute`) and a sibling of the nav.
- **Fixed bar RIDES UP as you scroll.** It carries its own `backdrop-filter`; drop `backdrop-blur` for an
  opaque background.
- **Fixed bar STRANDS mid-document once the page gets LONG** ("only when an expander is open"). First
  delete any redundant screen `pb-*` such as `pb-28`; otherwise add `transform: translateZ(0)` to the bar.
- **`position:sticky` never sticks.** It is the last child, or the `overflow:auto` ancestor has no bounded
  height (`#root{min-height}` must become `height`).
- **Rows squashed into thin bars instead of scrolling.** A `flex flex-col overflow-y-auto` list gives rows
  `flex-shrink:1`; add the `shrink-0` utility per row (a custom `> * {flex-shrink:0}` rule loses). For a
  container whose only children are `absolute inset-0`, use `flex-1 min-h-0`, not `h-full`.
- **Bottom bar lifts after navigating, installed PWA only.** iOS drops `viewport-fit=cover` on a
  `next/link` soft nav (`vercel/next.js#81264`); toggle the viewport meta's `content` in a `rAF` on route
  change.
- **An `env()` arbitrary class silently computes `0px`.** An invalid `calc()` is missing the `_+_` spaces;
  inject a throwaway div and read the computed px.
- **Drag preview far from the cursor on desktop.** Under a `zoom` band, drop `DragOverlay` and move the
  real node (`references/dnd-kit.md`).

## References

- `references/library-list.md`: the curated task-to-library table and how to use it. Read it whenever
  you pick a library.
- `references/dnd-kit.md`: the sortable-list skeleton, sensors, nested lists, persistence, zoom, and the
  iPhone whole-row drag. Read it before adding drag-and-drop.
- `references/sheets.md`: drag-to-close, vaul with inputs, and binding a hand-rolled sheet to the visual
  viewport.
- `references/date-picker.md`: the react-day-picker recipe, the `min-w-0` overflow, and the portal
  `pointer-events` trap.
- `references/ios-layout-traps.md`: full cause, fix, and reference implementation for every fixed-bar,
  sticky, and flex trap above.
- `references/touch-gestures.md`: chart scrubbing, tap vs drag, long-press, swipe-to-delete, debounced
  slider.
- `references/react-structure-traps.md`: structure and hydration bugs only live driving catches (portal
  providers, async seeding, drafts, auth-gate listeners, parallel routes, SSR hydration).
- `references/interactive-primitives.md`: hand-roll vs `shadcn add`, the vaul exceptions, and the
  per-primitive notes.
- `references/shadcn-migration.md`: migrating a whole tuned app to shadcn.
- `references/sonner-usage.md`: wiring the Toaster, picking the `toast()` call, recipes, and the styling
  ladder with icons and theme. Read it before writing any toast code.
- `references/sonner-troubleshooting.md`: every Sonner symptom with its cause and fix.
- `references/sonner-api.md`: every `<Toaster />` prop, `toast()` option and function, with types and
  defaults.
- `references/css-svg-gotchas.md`: daisyUI OKLCH tokens, library CSS variables, the tap box, iOS
  `feDropShadow`, percentage-height bars, and decimal commas.
- `references/history.md`: provenance, the dates behind each trap, and the 2026-10-15 merge.
