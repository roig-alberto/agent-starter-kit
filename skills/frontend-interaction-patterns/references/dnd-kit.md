# Drag-and-drop / sortable list (@dnd-kit)

## Drag-and-drop / sortable list → use @dnd-kit

**Default choice. Do NOT hand-roll pointer-event reordering** - it's a swamp of edge cases (touch
scroll vs drag, text selection, infinite `setState`-in-effect loops, stale-props commits). @dnd-kit
is touch + mouse + keyboard, accessible, and small.

```
npm i @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

Canonical impl (copy this):
- `personal-dash/components/objectives/objectives-screen.tsx` - single-level sortable, server-action persist.
- `finance-proj/components/BudgetsManager.tsx` (reorder mode) - **nested** lists (groups outer,
  items inner), drag from a handle, ▲▼ kept as an accessible alternative.

Skeleton:
```tsx
const sensors = useSensors(
  useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),   // mouse: 6px before drag
  useSensor(TouchSensor,   { activationConstraint: { delay: 180, tolerance: 8 } }), // touch: hold 180ms
);
<DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onEnd}>
  <SortableContext items={rows.map(r => r.id)} strategy={verticalListSortingStrategy}>
    {rows.map(r => <SortableRow key={r.id} row={r} />)}
  </SortableContext>
</DndContext>

function SortableRow({ row }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: row.id });
  return (
    <div ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition, WebkitUserSelect: "none", WebkitTouchCallout: "none" }}
      className={cn("select-none ...", isDragging && "z-10 opacity-90 shadow-lg")}>
      {/* drag ONLY from a handle so the row stays tappable/scrollable */}
      <button {...attributes} {...listeners} className="cursor-grab touch-none" onClick={e => e.stopPropagation()}>⣿</button>
      ...
    </div>
  );
}

function onEnd(e: DragEndEvent) {
  const { active, over } = e;
  if (!over || active.id === over.id) return;
  const next = arrayMove(rows, rows.findIndex(r => r.id === active.id), rows.findIndex(r => r.id === over.id));
  setRows(next);                    // optimistic
  persist(next.map(r => r.id));     // server action or PATCH
}
```

**The gotchas (each cost real debugging time):**
1. **Touch `delay`** on `TouchSensor` (≈150-200ms) - without it, a drag hijacks the scroll and the
   list won't scroll on a phone. With it, a quick swipe scrolls, a hold-then-move drags.
2. **Text-selection fix** ("the text underneath gets selected while dragging"): on each row set
   `select-none` + `WebkitUserSelect:"none"` + `WebkitTouchCallout:"none"`, and drag from a handle
   with `touch-none`. iOS Safari/PWA has no `navigator.vibrate`, so haptics won't help - the
   select-none IS the fix.
3. **Resync-from-props is a two-edged trap - know which edge you're on:**
   - **Loop edge:** `useEffect(() => setRows(items), [items])` where `items`'s identity changes on
     renders driven by THIS tree's own `setState` (a *client* parent recreating the array) →
     `setState` → re-render → new `items` → loop → "Maximum update depth exceeded". Avoid.
   - **Required edge:** when the list is seeded `useState(props.items)` for optimistic drag BUT the
     parent is a **React Server Component**, `props.items` identity changes *only* on route
     revalidation (`revalidatePath`), never on this client component's own `setState`. There you
     MUST `useEffect(() => setItems(props.items), [props.items])` - otherwise a server action that
     creates/deletes a row (revalidates the route, pushes fresh props) shows **nothing until the
     screen remounts** (user symptom: "I add X and don't see it till I leave and come back").
     No loop, because the RSC parent doesn't re-render from a child `setState`.
   - Rule of thumb: depend on the **specific array from an RSC parent** (`[view.metrics]`), never the
     whole prop object, and never an array a client parent rebuilds each render. Aro precedent:
     `objectives-screen.tsx` (2026-07-08) - drag-reorder lists were fine WITHOUT resync until
     create-in-place needed it; fix was the two `useEffect` resyncs.
4. **Persist correctly**: if `sortOrder` is **local to the list**, write `index`. If it's **global**
   (shared across sibling lists/groups), don't write index - permute the list's existing sortOrder
   "pool" into the new order, or you'll collide with other groups. And assign the new order
   **unconditionally**; don't skip PATCHes by diffing against props that a prior refresh may not
   have propagated yet.
5. **Drive the drag from a handle**, not the whole row, when the row is also a link/tappable - put
   `{...listeners}` on the handle and `onClick={e=>e.stopPropagation()}` on it.
6. **Nested sortables** (reorder SECTIONS that each reorder their ITEMS): separate `DndContext` per
   level, each with its **own `useSensors` instance** (never share sensor instances across nested
   contexts); scope BOTH drags to explicit handles so a pointerdown activates only the context whose
   handle it hit. An **opaque/Suspense-streamed child** doesn't need refactoring - wrap it in a
   `<SortableSection>` whose grip lives in the wrapper, body untouched. Give an empty section an
   invisible placeholder so it keeps its slot in the stored order. Aro objectives page, 2026-07-13
   (worked first try with these four rules). Driving the drag in a test: `verify-ui-live`.
7. **Under a desktop `zoom` band, do NOT use `DragOverlay` - move the real node.** `DragOverlay`
   portals to `document.body` (inside the `:root{zoom}`) and positions with the measured rect as
   top/left plus a pointer-delta transform; BOTH get re-scaled by the zoom, so the preview starts far
   from the cursor ("the card appears at the bottom"). A `Modifier` dividing the transform fixes only
   the DELTA (tracking) but not the ORIGIN. Fix that works: drop `DragOverlay`, apply `useDraggable`'s
   transform to the REAL element (already inside the zoom) with the delta divided by the zoom token - 
   no origin jump, no double scale. Verified at 1440/zoom 1.12: initial offset (10,10), tracking 1:1.
   Same family as `vw`-under-zoom (`responsive-desktop-port` `references/zoom.md`). closet 2026-07-24 (2 rounds - the
   first only fixed the delta).
8. **iPhone: drag the whole row, not a thin grip; cross-list moves must happen LIVE.** (agent-factory Settings >
   Dock, 2026-10-13, confirmed on the phone after two rounds.) A 28 px grip handle passed every headless test and
   never started a drag under a real finger. Winner: put `{...listeners}` on the whole row, use **`MouseSensor`
   (distance 6) + `TouchSensor` (delay 250, tolerance 8)** instead of `PointerSensor` (on a phone the pointer sensor
   reads a scroll swipe as a drag), and make the whole screen `select-none` + `-webkit-touch-callout:none` +
   `-webkit-user-select:none` (the 250 ms hold otherwise selects nearby text and iOS shows Copy / Translate). A quick
   tap still reaches the row's own button. For two lists in one `DndContext`, do the move/swap in **`onDragOver`
   into local draft state** (render from it, save on `onDragEnd`, reset on cancel): swapping only in `onDragEnd`
   leaves the other list's rows frozen while you drag ("the options do not move around"). Headless finger repro:
   CDP `Input.dispatchTouchEvent` (touchStart, wait > delay, touchMove steps, touchEnd) from the ui-check Playwright
   venv (`~/.local/share/uv/tools/playwright/bin/python`), context `has_touch=True, is_mobile=True`.
