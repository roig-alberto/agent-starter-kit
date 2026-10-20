# In-app launch splash for a Next SSR app (personal-dash, 2026-07-13)

Full recipe behind the pointer in `SKILL.md`.

closet's trick doesn't port: it's a Vite SPA, so `<div id="splash">` sits in `index.html`
and paints before React, hidden on a `mycloset:ready` event after the client fetch. **Next
has no index.html AND server-renders the data**, so there is no client "loading" gap - a
pure ready-trigger just flashes by. Working pattern:

1. A `"use client"` `SplashScreen` rendered in `app/layout.tsx`'s body - its markup ships in
   the SSR HTML and paints pre-hydration. React owns the node, so hide via **state +
   unmount, NEVER a manual `.remove()`** (that fights React).
2. Dismiss after `max(MIN_MS, time-to-interactive)`: `Math.max(0, MIN_MS - performance.now())`
   in a `useEffect` (the effect only runs post-hydration = interactive; `performance.now()`
   ≈ ms since navigation, so it tops the visible time up to the minimum). This is what makes
   it read as intentional instead of a sub-second flash.
3. Match the overlay background to the manifest `background_color`/`theme_color` so the
   OS-rendered cold-start splash blends into the in-app one. 450ms opacity fade + a hard
   safety timeout + a `prefers-reduced-motion` guard.
4. **Verify by asserting the splash is in the SSR HTML *without* its hidden attribute**
   (`fetch('/route').then(r => r.text())` + grep) - a warm dev container hydrates faster
   than Playwright's navigate resolves, so you usually cannot screenshot the live splash;
   re-inject the markup via `browser_evaluate` to screenshot the real CSS/icon.

