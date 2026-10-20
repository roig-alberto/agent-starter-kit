# React structure traps (only live-driving catches these)

## React structure traps that ONLY driving the real UI catches

- **"The app freezes when I press X" is usually a DEAD BUTTON under a `fixed` element, not a hang.**
  personal-dash's workout dock (`fixed bottom-[80px] z-30`) overlapped the routine CTA
  (`fixed bottom-[88px] z-20`): boxes 720-764 vs 704-756, so the button's CENTRE fell inside the
  dock and `elementFromPoint` resolved to the dock's link. Diagnose by calling
  `document.elementFromPoint(x, y)` at the button's centre and checking what comes back - if it
  isn't your button, it is occlusion, not a freeze. The main thread being alive (console evaluates,
  no overlay, no JS error) is the tell. (personal-dash, 2026-07-27)

- **A `useEffect` placed AFTER a page's early-return passes typecheck and the first render, then
  throws only once data arrives over the network** (`Rendered more hooks than during the previous
  render`). The repo already carried this warning in a comment on another page and it recurred
  anyway - so the lesson is not "remember the rules of hooks", it is **drive the real screen in a
  browser whenever you add an effect**. Playwright caught it on the first click; `tsc` and 517
  tests did not. (closet, 2026-08-08)

### A screen rendered by an early `return` misses the parent's portal providers
`if (showSearch) return <SearchScreen/>` inside a screen whose `<Toaster/>` (or modal root) lives in
the main return **below** the branch point → every toast from that child fires into nothing. Real
cost (superhuman-mvp 2026-07-17): a bulk-archive of up to 2000 emails showed NO feedback and its
**Undo was unreachable** - the undo existed and was tested server-side, and no user could ever have
tapped it. `tsc`, unit tests and a route-level check all passed. **Rule:** any provider a child needs
must sit ABOVE every early return (or be mounted by the child); when a component early-returns a
full-screen child, audit which providers live below the branch point.

### Seeding a child's `useState` from an async parent hook seeds EMPTY
A per-call data hook (`useState([])` + async load, e.g. `useTrips`) feeding a child that does
`useState(list.find(id))` seeds from an empty array: the child's own hook instance starts empty and
`useState` only runs once (no re-seed). Symptom: **"the edit form opens blank as if nothing was
filled."** A load-gate on the PARENT alone is NOT enough (the child re-fetches). **Fix:** gate on the
parent AND pass the resolved entity DOWN AS A PROP, plus `key={id}` to remount on id change. closet
2026-07-15; verify LIVE (Playwright) - `tsc` says nothing about this.

### Wizard/draft state: `sessionStorage` snapshot, and version the key
A multi-step wizard that navigates AWAY to a sub-page loses all local `useState` (back at step 1,
empty). **Fix:** snapshot every field + step + done-set to `sessionStorage` (keyed by id / `'new'`)
on change, lazy-init each `useState` from it, clear on final submit; gate forward nav
(`goStep` only if `n <= step || [0..n-1].every(done.has)`) and `disabled` the unreachable chips.
**Trap:** a draft holding empty/default values SHADOWS real data - `??` spares `null`, but `""` and
defaults win outright. **Bump the draft-key version** to discard poisoned drafts fleet-wide. closet
2026-07-15.

### A listener inside a component the AUTH GATE doesn't mount is a PROD-ONLY bug
closet's boot splash was removed by a `useEffect` inside `App` - but with `APP_PASSWORD` set, `App`
does not mount until after login. `AuthGate` dispatched the "ready" event and **nobody was
listening**, so the splash covered the password form and swallowed its clicks. Dev has no password,
so it was invisible there; it had been shipped for months. **Rule:** anything that must happen
BEFORE or BESIDE the auth gate belongs outside React (in `main.tsx`), not in a gated component. And
verify any BOOT/startup change against the **prod container**, never dev alone - the gate is the
whole difference. closet 2026-07-22.

### Next App Router: a NEW parallel-route slot isn't served until the dev server RESTARTS
Adding `app/(x)/@slot/<route>/page.tsx` while the dev server runs falls through to `default.tsx` and
renders nothing - **identical on screen to a slot you wired wrong**, so you debug the wiring instead
of restarting. Restart first, then debug. Sibling trap in the same phase: a headless test of a
keyboard shortcut must **wait for hydration**; a synthetic `keydown` fired at load hits no listener
yet and reads as a broken binding. personal-dash 2026-07-22 (~10 min each).

### A server component importing ANYTHING from a `"use client"` file → `backend-patterns`
Arrays and constants cross the boundary as opaque client references exactly like functions do, so
`X.find is not a function` at runtime with `tsc` green. Put the shared value in a neutral module.
Full incident + the rule in `backend-patterns` ("Next.js server-side gotchas").

### Two SSR hydration traps, both invisible in the server logs
Surfaced only via the Next dev-overlay issue badge - nothing in the terminal:
- A **pre-paint inline script writing a `data-*` attribute on `<html>`** (the theme-script pattern)
  needs `suppressHydrationWarning` on `<html>`, or React flags an attribute the server never
  rendered.
- **`new Date().getHours()` in a component runs on the server (container TZ) AND the client
  (browser TZ)** and they disagree. Pin it with `Intl.DateTimeFormat` + an explicit `timeZone`.
- **A live clock/elapsed counter is the same trap** - an elapsed timer renders server-side (request
  time) and client-side (mount time), ~1s apart (`1:20` vs `1:21`), mismatch on EVERY load. Render the
  live value CLIENT-ONLY (`useEffect`/`suppressHydrationWarning` on that node), or send `startedAtMs`
  and compute the elapsed only after mount. Rule: any ticking clock/counter is client-only. (personal-dash `ResumeWorkoutCard`, 2026-07-24)

personal-dash 2026-07-22 (~15 min).

- **React Compiler memoizes a render-time call with no reactive inputs**, such as one that reads `localStorage`, so the
  value never updates after a write. Keep it in state (`useState(lastPlace)`) and set it on write (Agent Factory).
