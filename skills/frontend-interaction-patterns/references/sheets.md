# Bottom sheets / drawers

## Drag-to-close bottom sheet
Pointer drag on the **grabber/header only** (not the body - else it steals content scroll/inputs);
sheet `translateY` follows the finger; past a threshold → close, else spring back. No library.
Reference: `finance-proj/lib/sheet-drag.ts` (`useSheetDrag(onClose, threshold=110)`).
```tsx
const start = useRef<number|null>(null);
const onPointerDown = (e) => { start.current = e.clientY; setDrag(true); e.currentTarget.setPointerCapture?.(e.pointerId); };
const onPointerMove = (e) => { if (start.current!=null) setDy(Math.max(0, e.clientY - start.current)); }; // down only
const end = (e) => { const past = (e.clientY - (start.current??e.clientY)) > threshold; start.current=null; past ? onClose() : setDy(0); };
// handle zone: style={{ touchAction: "none" }}; sheet: transform translateY(dy), transition none while dragging
```
Pair with a `useScrollLock(open)` hook to freeze the page behind the sheet.

> Making these sheets look right on a WIDE screen (centred card, not a 1400px bar) belongs to
> `responsive-desktop-port` `references/layout-recipes.md` section 4b - and the centring must be margin-based, because Vaul writes an
> inline `transform` that clobbers `translate`.

## Vaul sheet with inputs → fixed-height frame + inner scroll (iOS keyboard)
A `Drawer.Content` that is content-height or `max-h-[Nvh] overflow-y-auto` (the WHOLE sheet is
the scroll container) gets shoved off the top on iOS the moment the user focuses an `<input>`
that sits low in the sheet - Safari's scroll-into-view drags the `fixed inset-x-0 bottom-0`
frame up out of view ("the menu shoots up when I type"). Same shove if any sheet input has
`autoFocus` (pops the keyboard on mount).
**Winner:** a FIXED-height flex frame + pinned header + one inner scroll region - the keyboard
scrolls the BODY, the frame stays put; and a short list can't collapse the sheet to the bottom.
```tsx
<Drawer.Root repositionInputs={false}>                                              {/* never autoFocus a sheet input */}
<Drawer.Content className="fixed inset-x-0 bottom-0 flex h-[85vh] flex-col …">      {/* FIXED h, NOT max-h */}
  <div className="… flex-none">…grabber + Cancel / Title / Save…</div>              {/* pinned → Save always reachable */}
  <div className="flex min-h-0 flex-1 flex-col overflow-y-auto">…fields / list…</div> {/* ONLY this scrolls */}
</Drawer.Content>
```
Applies to **any tall sheet with inputs - forms AND search pickers**, not just pickers. A short
sheet with a single input at the very top is fine (input stays above the keyboard). Losing
approach = `max-h + overflow-y-auto` on the whole sheet (looks fine on desktop, breaks on a real
iPhone). Reference: personal-dash `routine-detail.tsx` / `session-screen.tsx` / `goal-sheet.tsx`.
Cost: re-diagnosed 3×+ from scratch (workout picker → session picker → goal create form) before
generalising. 2026-07-07.

### Hand-rolled fixed overlay sheet → bind it to `visualViewport` (height AND offsetTop)
Same symptom, different container: a `position:fixed; inset:0; align-items:flex-end` sheet (no vaul)
stays anchored to the **layout** viewport, which does NOT shrink when the keyboard opens - an input
near the sheet top ends up behind the keyboard and Safari's scroll-into-view makes "everything shoot
up". **Fix (applies to every sheet at once):** a `ScrollLock`-style effect writes
`window.visualViewport.height` into `--sheet-vh` on its `resize`/`scroll`; overlay
`height:var(--sheet-vh,100dvh)` + `top:0` (drop `inset:0`), sheet `max-height:min(88vh,100%)`.
**Track `visualViewport.offsetTop` too, not just height** - a height-only half-fix shipped and still
broke (iOS pushes the visual viewport DOWN, so the `top:0` overlay renders above the fold).
Verify in Playwright: `browser_resize` to a short height, assert the input's
`getBoundingClientRect()` stays within `innerHeight`. closet, 2026-07-15 (two rounds).

## Pickers and dialogs inside a sheet (Agent Factory, 2026-10)

- **A Radix Dialog opened in the same render as the vaul Drawer that holds it** gets `pointer-events: none`, so every
  option tap is lost. Open the inner dialog one tick after the drawer mounts (`setTimeout(0)`), and diagnose with an
  `elementFromPoint` hit test, not a click.
- **Give the iOS keyboard back to a typing sheet after a picker closes over it:** focus the field inside the closing
  tap, right after `flushSync(onClose)`, and `preventDefault` `onCloseAutoFocus` when a text field already has focus.
  A close timer runs outside the gesture, and iOS then refuses the focus.
