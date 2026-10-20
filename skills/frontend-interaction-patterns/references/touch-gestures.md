# Touch gestures

## Touch chart scrubbing (drag across a chart to read a point)
Pointer-capture + `clientX → fraction → nearest index`. Same idiom in
`finance-proj/components/NavChart.tsx` and `DashboardTrendCard.tsx`.
```tsx
const onDown = (e) => { scrub.current = true; locate(e.clientX); e.currentTarget.setPointerCapture?.(e.pointerId); };
const onMove = (e) => { if (scrub.current) locate(e.clientX); };
function locate(x) { const r = ref.current!.getBoundingClientRect();
  const frac = Math.min(1, Math.max(0, (x - r.left) / r.width)); setIdx(Math.round(frac * (n - 1))); }
// onPointerUp / onPointerCancel → scrub.current = false
```

## Tap vs drag/swipe (don't fire onClick on a scroll)
Record `{x,y}` on pointerdown; flip a `moved` flag once past a small threshold (~8px); on pointerup
treat as a tap only if `!moved`. Reference: `finance-proj/components/TransactionList.tsx`.

**Long-press + the click that follows it:** a real long-press is followed by a browser `click` that
must be swallowed (`longPressed` ref set in the timer, checked+reset in `onClick`). A **synthetic**
pointerdown+pointerup in a test does NOT fire that click, so the guard stays `true` and the next REAL
click is swallowed - a test artifact, not a bug. In tests, fire a `click` on the long-pressed element
too, or expect the first tap after a synthetic long-press to no-op. superhuman-mvp 2026-07-18.

## Swipe-to-delete a list row (right-to-left)
No library - same pointer-event idiom as the sheet/scrub above. The failure it prevents: **a fast
flick does nothing** because the release handler read stale React state.
Reference: `personal-dash/components/nutrition/meal-plans-screen.tsx` (`PlanRow`).

Load-bearing rule: **hold the gesture's live values in refs, not state.** State updates are
async/batched, so within one gesture the handlers see stale values:
- **Gate on a ref** (`active.current`), set in `onPointerDown`. Gate on a `dragging` *state* and the
  first `pointermove` can fire before the re-render commits → `onMove` early-returns → gesture no-ops.
- **Track the live offset in a ref** (`dxRef.current`) beside the state you render from; read the
  **ref** in `onPointerUp` to decide delete-vs-spring-back. Reading `dx` *state* there misses a fast
  flick (moves batch, no re-render, `dx` still 0).

```tsx
const active = useRef(false), dxRef = useRef(0), axis = useRef<null|"x"|"y">(null);
const [dx, setDx] = useState(0);                                    // render only
const onDown = (e) => { active.current = true; startX.current = e.clientX; startY.current = e.clientY; axis.current = null;
  try { e.currentTarget.setPointerCapture?.(e.pointerId); } catch {} };  // synthetic/edge pointers throw
const onMove = (e) => { if (!active.current) return;
  const ddx = e.clientX-startX.current, ddy = e.clientY-startY.current;
  if (!axis.current && (Math.abs(ddx)>6||Math.abs(ddy)>6)) axis.current = Math.abs(ddx)>Math.abs(ddy) ? "x":"y";
  if (axis.current==="y") return;                                  // vertical → let the page scroll
  dxRef.current = Math.min(0, ddx); setDx(dxRef.current); };        // leftward only
const onUp = () => { active.current=false;
  if (axis.current==="x" && dxRef.current < -threshold) onDelete(); else { dxRef.current=0; setDx(0); } axis.current=null; };
// row: style touchAction:'pan-y'; onClick preventDefault when a horizontal swipe happened (don't navigate)
```
**axis-lock** (decide x vs y once past ~6px) + `touch-action: pan-y` keep vertical scroll working.
For a destructive full-swipe, remove the row optimistically then call the server action; block rows
the action would reject (Aro: the *active* plan stays a plain link, non-swipeable). Verify headlessly
with the synthetic-swipe recipe in `verify-ui-live`.

## Slider with debounced save
Native `<input type="range">` (or daisyUI `range`) + a live value label + **debounce the persist**
(≈400ms) so you don't PATCH on every tick. Reference: `finance-proj/components/FundThreshold.tsx`,
`AportacionesView.tsx`; reusable `<Slider>` in `FireCalculator.tsx`. Style the native track/thumb via
`accent-color` or a UI lib's `range` classes rather than rebuilding the control.
