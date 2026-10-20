# DOM measurement snippets

Paste into `mcp__claude-in-chrome__javascript_tool` (REPL semantics: the last expression
is returned - no `return` needed). Each is self-contained. Adjust selectors to the page.

## Horizontal overflow at phone width

The most common Aro bug: content that fits on desktop but runs off a phone screen. Force a
narrow width on the app root, then compare `scrollWidth` vs `clientWidth` (any positive
`overflowPx` = it spills). Restores the width afterward so you don't disturb the user's view.

```js
(() => {
  const root = document.querySelector('main') || document.body;
  const prev = root.style.width;
  root.style.width = '360px';                       // simulate a phone
  const el = document.querySelector('SELECTOR');    // e.g. a chart row
  const m = e => e ? { scrollWidth: e.scrollWidth, clientWidth: e.clientWidth, overflowPx: e.scrollWidth - e.clientWidth } : null;
  const res = {
    forcedWidth: root.getBoundingClientRect().width,
    target: m(el),
    docOverflowPx: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  };
  root.style.width = prev;
  return res;
})()
```

`docOverflowPx: 0` and `target.overflowPx: 0` = no overflow.

### Which element CAUSES the overflow - filter out clipping ancestors, or the noise buries you

`docOverflowPx > 0` says the page spills, not WHO. Listing every element with
`right > clientWidth` returned **119** candidates on Caudal's home at 390px and **none** was the
culprit: almost all live inside carousels with `overflow-x:auto/scroll/hidden`, which overflow ON
PURPOSE and never widen the document. The filter that leaves ONE candidate: walk the ancestors up
to `documentElement` and drop the node if any has `overflowX !== 'visible'`.

```js
(() => {
  const w = document.documentElement.clientWidth;
  const clipped = el => { for (let p = el.parentElement; p; p = p.parentElement)
    if (getComputedStyle(p).overflowX !== 'visible') return true; return false; };
  return [...document.querySelectorAll('*')]
    .filter(el => el.getBoundingClientRect().right > w + 0.5 && !clipped(el))
    .slice(0, 5)
    .map(el => ({ tag: el.tagName, cls: String(el.className).slice(0, 60),
                  right: Math.round(el.getBoundingClientRect().right) }));
})()
```

Companion habits:
- **Measure the BASELINE before assuming your change caused it**: `git stash -u`, re-measure,
  `git stash pop`. In Caudal the same 10px was preexisting.
- Typical root cause: `shrink-0` on a flex item whose content grows with the data (a badge holding
  a 4-digit amount). Forbidding it to shrink doesn't make it fit - it converts it into page overflow.
- Lock it in with a guard proven on the NEGATIVE too (exit 1 with the bug, 0 without):
  `finance-proj/e2e/no-overflow.e2e.py`.

Losing approach: the unfiltered `right > clientWidth` listing - ~10 min and 3 wasted measurements
before the ancestor filter (Caudal, 2026-07-21).

## Exact computed styles (colors, spacing, fonts)

Screenshots can't confirm a hex or a padding value; this can. Great for wireframe-exactness.

```js
(() => {
  const el = document.querySelector('SELECTOR');
  if (!el) return { found: false };
  const cs = getComputedStyle(el);
  return {
    found: true,
    color: cs.color, background: cs.backgroundColor,
    fontSize: cs.fontSize, fontWeight: cs.fontWeight, fontFamily: cs.fontFamily,
    padding: cs.padding, margin: cs.margin, gap: cs.gap, borderRadius: cs.borderRadius,
    box: el.getBoundingClientRect(),
  };
})()
```

## Element / text presence + count

```js
(() => {
  const els = [...document.querySelectorAll('SELECTOR')];
  return { count: els.length, texts: els.slice(0, 12).map(e => e.textContent.trim()) };
})()
```

## Drag rows: text-selection guard

Confirms rows won't select underlying text on long-press (the `select-none` fix).

```js
(() => {
  const rows = [...document.querySelectorAll('div.select-none')]
    .filter(d => d.querySelector('button[aria-label="Reorder"]'));
  const cs = rows[0] && getComputedStyle(rows[0]);
  return { rowCount: rows.length, userSelect: cs && (cs.userSelect || cs.webkitUserSelect) };
})()
```

## Interact, then re-measure

`javascript_tool` can click/open before measuring - e.g. open a Vaul sheet whose content
isn't in the initial HTML, then assert on it:

```js
(() => {
  document.querySelector('BUTTON_SELECTOR')?.click();
  return { opened: !!document.querySelector('[role="dialog"]') };
})()
```

Wait a beat, then run a presence/style check in a second call.

## Drive a swipe/drag gesture headlessly (synthetic pointer events)

`ui-check` has no finger - dispatch `PointerEvent`s to exercise a swipe/drag handler. Must sit inside
the async IIFE (see `gotchas-and-perf.md`). Leftward swipe-to-delete a row:
```js
(async () => {
  const row = document.querySelector('ROW_SELECTOR');
  const r = row.getBoundingClientRect(), y = r.top + r.height/2, x0 = r.left + r.width - 20;
  const pe = (t,x) => new PointerEvent(t,{clientX:x, clientY:y, pointerId:1, bubbles:true, cancelable:true});
  row.dispatchEvent(pe('pointerdown', x0));
  for (let i=1;i<=10;i++) row.dispatchEvent(pe('pointermove', x0 - i*28));  // drag left
  row.dispatchEvent(pe('pointerup', x0 - 280));                            // release past threshold
  await new Promise(r => setTimeout(r, 700));
  return { gone: !document.querySelector('ROW_SELECTOR') };
})()
```
The dispatch is **synchronous** - all events in one tick, no re-render between them - so it only
passes if the gesture handlers are **ref-gated** (not React-state-gated). That's a feature: it fails
in the exact way a real fast flick fails, so it also proves the fast-input path. Ref-gating detail:
`frontend-interaction-patterns` "Swipe-to-delete a list row". For a **destructive** gesture, drive it
on a throwaway row you created, never a real one.

## Notes

- The user's browser holds an Aro session, so `navigate` reaches gated pages directly.
- Prefer these over `preview_screenshot` for anything numeric; use a screenshot only for a
  quick layout gut-check.
- After measuring, restore any inline style you changed (the width snippet already does).

## Driving gestures with synthetic PointerEvents (the dispatch-target rule)

`browser_click` / Playwright `dragTo` / HTML5 DnD **silently no-op** on pointer-gesture UI. Dispatch
raw `PointerEvent`s instead - and **match the dispatch target to WHERE the library listens**:

| Gesture kind | Dispatch `pointerdown` on | Dispatch `pointermove`/`pointerup` on |
|---|---|---|
| React `onPointerDown/Move` props (a `useSwipeRow`-style hook) | the ROW element | **the same ROW element** - events on `document` bubble UP only and never reach a descendant |
| @dnd-kit (adds document-level listeners after pointerdown) | the drag HANDLE | **`document`** |

Every event needs `{pointerId:1, isPrimary:true, bubbles:true, pointerType:'touch'}`, `button:0` on
down, `buttons:1` during move. Put ~25ms between events (`setTimeout`), and drive the whole sequence
inside ONE `browser_evaluate` async function.

**Swipe row** (personal-dash `lib/hooks/use-swipe-row.ts`): find the sliding element
(`el.closest('div[style*="translate"]')`), `pointerdown`, ~8 `pointermove`s with increasing `clientX`,
`pointerup`. Threshold is `max(minPx=96, rowWidth*0.4)` - a 356px row needs >142px. Right-swipe =
`onSwipeRight` (edit), left = `onSwipeLeft` (delete). Proved 2026-07-13/14; the first attempt failed
purely because move/up went to `document`.

**@dnd-kit**: `pointerdown` on the grip, ~12 stepped `pointermove`s (the FIRST must exceed the 6px
activation distance), `pointerup` on `document`. `browser_resize` TALL first (900x1500) so every drop
target is on-screen and you don't fight auto-scroll. Proved end-to-end on Aro objectives 2026-07-13
(DOM order changed AND the DB pref updated) - **via the Playwright MCP**. It does **not** work in
`ui-check`/plain headless Chromium (2026-07-07: needs coarse-pointer detection + rAF + real droppable
layout measurement; `buttons:1`/`isPrimary`/window-dispatch all tried, no reorder fires). There, verify
dnd-kit by (a) render + handle presence, (b) the persist action in isolation, (c) mirroring a proven impl.

**Long-press:** a real long-press is followed by a browser `click` that the component's guard swallows;
a synthetic down+up doesn't fire it, so the guard stays armed and eats the NEXT real click. Fire a
`click` yourself after the synthetic long-press.

## Transient UI (toast, optimistic Undo) - POLL the DOM, never screenshot

A screenshot lies about transient UI. Two proven failures: (1) a top-position Sonner toast spends its
first ~400ms mid-slide-in (measured `y:-28, opacity:0.02`) so two screenshots showed "no toast" while
the element was in the DOM; (2) a 5s auto-dismiss Undo elapsed during the round-trip between separate
`browser_evaluate` calls, so `find(btn => btn.text==='Undo')` returned nothing.

Rules: **poll inside ONE async `browser_evaluate`**, and assert settled geometry, not presence:

```js
() => (async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  document.querySelector('#move-btn').click();
  for (let i = 0; i < 25; i++) {                       // ~5s of polling
    await sleep(200);
    const t = document.querySelector('[data-sonner-toast]');
    if (t) {
      const r = t.getBoundingClientRect(), o = getComputedStyle(t).opacity;
      if (o === '1' && r.y >= 0) { /* settled → assert, or click Undo now */ }
    }
  }
})()
```

Also: React has NOT re-rendered a CTA (`Save changes` → `Move`) within the same synchronous evaluate
that flipped its state - `await sleep(200)` between selecting an option and clicking the now-enabled
button. Sources: personal-dash 2026-07-12 (Undo, wasted two cycles) and 2026-07-13 (Sonner).

**Stronger form: a click and the action it ENABLES cannot share one `browser_evaluate`.** Selecting a
swap target and then clicking its confirm CTA in the same `page.evaluate` silently no-ops - at click
time the CTA is still `disabled` (or bound to stale state). It fails SILENTLY and looks exactly like a
broken feature: closet 2026-07-20 read the DB, saw nothing written, and nearly went debugging a
persistence path that was correct (~5 min + one false bug conclusion). Rule: **one state-changing
click per `browser_evaluate`**, and re-measure (`{disabled}`) between steps rather than trusting a
sleep.

## Screenshot diffing: the two comparisons that produce a FALSE green

Surfaced by closet's dark-theme pass (2026-07-21) but not theme-specific: these bite any
before/after visual comparison. A check that reports "no change" when there IS one is worse than
running no check, because it ends the investigation.

- **Never compare screenshots by BYTES.** Two captures identical on screen differ by tens of bytes
  purely from the PNG encoder (4 of 27 files in that pass). A diff must count PIXELS. No PIL
  needed: draw both into a Chromium canvas via Playwright and compare `getImageData`. Reference
  implementation: closet `e2e/imgdiff.py`.
- **Never compare against a baseline captured "a while ago"** if anything on the screen is live
  (an hourly weather strip, a relative timestamp, a chart of today's data): it re-renders on its
  own and the diff blames your change. The honest baseline is captured WITH the change, then again
  IMMEDIATELY after `git stash` - back to back, same minute. Same discipline as the overflow
  baseline above.
- **A baseline is silently contaminated while a splash/boot overlay is still up.** A naive "is
  there text?" assertion passes anyway, because the content is already in the DOM underneath the
  overlay - so the capture looks valid and shows the wrong thing. Wait for the overlay to reach
  `state='detached'`, and disable animations and the text caret, before capturing.

The design-side audits these mechanics serve (AA contrast per token PAIR, and the
"invisible elements" check that compares an element's background against its CONTAINER's) live in
`frontend-design`. This file owns only the capture and diff mechanics.

## A data-driven screen whose live table is empty (personal-dash)

Never seed a shared dev/prod database to see it. Mount the real component at a temporary throwaway route with fixture
props, ui-check it at 390 and 1440, then delete the route and its stale `.next/types` entry. Zero database writes, and
the real responsive layout renders.
