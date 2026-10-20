# iOS / fixed-bar / flex layout traps (full diagnoses)

Every entry here was earned on a real phone after a headless check said "fine". The gotchas in
`SKILL.md` have the one-liners; this file has the cause + fix + reference impl.

**Standing rule for this whole file:** headless/desktop Chromium resolves `env(safe-area-inset-*)`
to 0 and repaints `position:fixed` on every frame, so most of these are **not reproducible
headlessly**. A green `ui-check` is NOT evidence against a phone-reported bug.

---

## 1. Fixed bottom nav: icons crammed at the TOP of the bar (phone only)

**Cause:** the app sets `viewport-fit=cover` (needed for `pt-[env(safe-area-inset-top)]`), so
`env(safe-area-inset-bottom)` ≈ 34px on the phone. A `pb-[env(safe-area-inset-bottom)]` on the
FIXED `h-16` row eats 34px off the 64px row (border-box) → `items-center` centers in the leftover
~30px. Identical classes look fine in an app WITHOUT `viewport-fit=cover` (there `env()` = 0) - 
that's why Aro's tab-bar looked right and recall's didn't with byte-identical markup.

**Fix - pick by the look you want:**
- **Bar ignores the home indicator** (Aro's look, plain 64px bar): put **no** safe-area padding on
  the nav. Row `flex h-16 items-center justify-around` = centered.
- **Bar reserves space for the indicator**: move `pb-[env(safe-area-inset-bottom)]` **off the fixed
  row and onto the `<nav>`**. Row stays a clean centered 64px; the inset becomes bar background
  below it. NEVER leave `pb-[env(...)]` on the fixed-height row.

Shared metrics (both apps): `fixed inset-x-0 bottom-0 z-50 border-t`, `h-16` row,
`items-center justify-around`, item `flex-col items-center gap-1 text-[10px]`, center FAB
`-mt-8 h-14 w-14`. Reference: recall `src/components/bottom-nav.tsx`, Aro
`personal-dash/components/nav/tab-bar.tsx`. Cost: chased "identical classes, different result"
before spotting `viewport-fit=cover` as the variable. 2026-07-11.

**Flush-vs-reserve is a TASTE call**, not a correctness fix - default to matching the reference app
the user names ("like Aro" = flush). A **nav** may sit flush; a **primary action button** (Import /
Start review) should NOT hide under the indicator → give ITS bar
`pb-[calc(18px_+_env(safe-area-inset-bottom))]`. Picking wrong cost a full lift→flush→re-pad round-trip.

## 2. `min-h-full` shell → bottom bars FLOAT on SHORT pages. Use `dvh`. (2026-07-12)

**Symptom:** the fixed tab bar (or an `absolute bottom-0` action bar) is flush on some screens but
**floats up with a gap below it on OTHERS - always the SHORT-content pages**. Phone-only.
**Cause:** `html h-full` + `body min-h-full` + page-root `min-h-full` (percentage height). With
`body pt-[env(safe-area-inset-top)]` on a notched phone the percentage chain **collapses to CONTENT
height**, so a short page is shorter than the screen; mobile browsers then anchor
`position:fixed;bottom:0` to the **document** bottom. **The tell is "only the short pages are wrong."**
Not reproducible headless - cost 3 wrong iterations.
**Fix:** `min-h-full` → `min-h-[calc(100dvh_-_env(safe-area-inset-top))]` (Tailwind arbitrary needs
`_` for spaces), or adopt Aro's model: `min-h-dvh` shell + `fixed` nav + content `pb-*`.
Reference: recall page roots, Aro `components/nav/app-chrome.tsx`.

## 3. A sticky CTA stacked ABOVE the fixed nav must be `fixed`, not `absolute` (2026-07-12)

An `absolute inset-x-0 bottom-16` CTA anchored to a `min-h-*` page root **drifts to the TOP of the
page on iPhone** (same root-height fragility as §2). Make it `fixed inset-x-0 bottom-16 z-40 mx-auto
max-w-[Npx]` and keep `<BottomNav>` a **sibling**, not a child. Use `bottom-16` (nav height), never
`bottom-0` (the CTA's lower part hides behind the bar). Reference: recall `src/app/page.tsx`.

## 4. A `fixed` bar with its OWN `backdrop-filter` scrolls with the page on iOS (2026-07-18)

**Symptom:** the fixed nav (and a second fixed bar, e.g. a workout dock) **rides UP mid-screen as you
scroll**, both offset by exactly the scroll amount. WebKit only; not reproducible headless
(Chromium kept navTop constant at every scrollY).
**Cause:** a `position:fixed` element that ALSO carries `backdrop-filter` / `-webkit-backdrop-filter`
(Tailwind `backdrop-blur`) can be promoted on WebKit so it scrolls with the page.
**Fix:** don't put `backdrop-filter` on the fixed element. The nav/dock bg were already 95-97% opaque →
dropped `backdrop-blur` for a fully-opaque bg, visually identical, pinning restored. If the blur is
essential, move it to a NON-fixed inner layer. Reference: Aro `components/nav/tab-bar.tsx`,
`components/workouts/workout-dock.tsx`.

## 5. A `fixed` bar strands MID-DOCUMENT on iOS once the page gets LONG (2026-07-20)

**Distinct from §4 - this nav has NO blur; the trigger is page LENGTH.** Expanding an inbox bundle
took a page from ~840px to 3213px; on the phone the fixed nav then painted **mid-document** (list rows
above AND below it) and its visible icons did nothing, because hit-testing still used the bar's REAL
position. **The tell: "only when a collapse/expander is open."**
**Cause:** WebKit repaints `position:fixed` only when momentum scrolling SETTLES, so a fling strands
the bar at its last painted document position.
**Fix:** `transform: translateZ(0)` on the fixed bar (own compositing layer → the compositor keeps it
pinned mid-fling). Applied to the nav AND the fixed selection bar.
**The agent trap:** Chromium measured `navTop` constant at every scroll offset BEFORE and AFTER the
fix - the headless check is green in BOTH states. Do not let it talk you out of the phone screenshot.
**Diagnosis path that worked:** confirm ONE nav, `fixed`, no transformed/filtered/contained ancestor,
no duplicate → structure is fine → therefore it's a WebKit *paint* issue, not a CSS bug.
Confirmed on-device. Source: superhuman-mvp.

**Check page LENGTH before reaching for `translateZ(0)` (personal-dash 2026-07-24).** First check the page
is not just too TALL: a screen's OWN `pb-*` stacked on the shell's bottom clearance (the `<main>` already
reserves `pb-[max(6rem,calc(5rem+var(--dock-h)+12px))]`) adds a dead gap AND lengthens the page enough to
trip this same WebKit strand. One line (deleting the redundant `pb-28`) fixed BOTH "there's a gap below"
and "the navbar scrolls", with no `translateZ(0)` needed. Rule: the SHELL owns bottom clearance; a screen
adds its own `pb-*` only if it has its OWN fixed element (a `bottom-[88px]` CTA yes; a plain scroll page
no). Measure with the viewport FORCED to overflow (390x500), because at 390x844 the page does not scroll
and `scrollHeight==innerHeight` hides it.

## 6. `position: sticky` that never sticks - two different causes

**(a) Sticky as the LAST child (2026-07-13).** A bottom tray coded as the last child with
`position:sticky; bottom:<nav-height>` **cannot pin** - sticky only holds while there's content BELOW
it to scroll against; as the last element it rests at its flow spot, leaving a gap (user: "blank space
at the bottom of the drag-and-drop"). Symptom math from closet `DiasPage`: gap = 168px = `main`
padding-bottom (76+16) + the 76px sticky offset. Negative margins do NOT help a sticky element.
**Fix:** make it in-flow `position:static` and cancel the container's nav-clearance padding with a
negative bottom margin, OR make it truly `fixed` above the nav with matching bottom padding on the
list. closet fix: `.dias-page{padding-bottom:0}` + `.dia-tray{position:static;margin-bottom:-16px}`.
Verify by scrolling to `document.body.scrollHeight` and reading
`innerHeight - tray.getBoundingClientRect().bottom`.

**(b) The intended scroller has no BOUNDED height (2026-07-15, closet).** `position:sticky; top:0`
does not anchor when the `overflow:auto` ancestor (`<main>`) isn't height-bounded: with
`#root{min-height:100dvh}` (instead of `height`) `main` grows to content, never scrolls internally,
and the DOCUMENT scrolls - carrying the sticky away. **Fix:** bound the shell (`#root{height:100dvh}`)
so `main{overflow-y:auto}` is genuinely the scroll container (a fixed nav +
`sheet-open main{overflow:hidden}` already betrayed that intent).
**Diagnosis:** measure `main.scrollHeight > main.clientHeight` live and walk the ancestor chain
(overflow / transform / height) - `getComputedStyle().position` reports `sticky` even when it does
nothing. Generic React/Tailwind app-shell pattern.

## 7. A full-screen overlay COVERED by the fixed nav on mobile → portal to `document.body` (2026-07-15)

closet's eyedropper overlay (`PhotoColorSampler`) rendered inside `AddItemPage` with `z-index:300`
**lost to the bottom nav at `z-index:100`**: an ancestor created a stacking context, so `fixed` was
scoped to it and the app-root nav painted over the overlay's footer - desktop fine, iOS hid the close
button. **z-index measurement alone LIES here** ("300 > 100, should be fine"); the tell is
`elementFromPoint` at the nav location returning the **nav**, not the overlay.
**Fix:** `createPortal(node, document.body)` so `fixed` is viewport-relative and z-index is global - 
**not** a higher z-index. Then also: opaque bg, `env(safe-area-inset-*)` padding, an explicit ✕,
`user-select:none` + `-webkit-touch-callout:none`.
**Verify:** `browser_resize` 390x844 + screenshot AND `elementFromPoint` over the nav returns the
overlay. Bonus from the same component: tap-to-sample on a `<canvas>` must use `onPointerDown`, not
`onClick` (click on a non-interactive canvas is flaky in mobile Safari); `getImageData` on a
`data:` URL canvas is untainted.

## 8. Flex sizing traps that only appear on LONG content

**(a) `flex flex-col overflow-y-auto` SHRINKS its children instead of scrolling (2026-07-16).**
`flex-shrink` defaults to 1, so once content overflows every row is squeezed into a thin bar rather
than the list scrolling. Only shows on long lists (a short lane looked fine). **Fix: the `shrink-0`
Tailwind UTILITY on each row.** A `.container > * { flex-shrink: 0 }` custom CSS rule did **not** win
(computed stayed 1); the utility did. Source: superhuman-mvp, ~15 min.

**(b) A container whose ONLY children are `absolute inset-0` has NO in-flow content → height
collapses (2026-07-10, recall).** A CSS 3D flip card measured 50px tall; `h-full` doesn't reliably
resolve inside a flex column. The front face looked fine only because its overflow wasn't clipped;
the back face (`overflow-y-auto`) clipped to 50px. **Fix:** flip area `flex flex-col`, flip container
`flex-1 min-h-0` (NOT `h-full`); faces stay `absolute inset-0`.

## 9. Verifying `env()`-based arbitrary classes when you can't see the phone

`env(safe-area-inset-*)` resolves to 0 headless, so the phone effect is invisible - but you can still
prove the CSS is VALID: inject a throwaway `<div className="<the-arbitrary-class>">` and read
`getComputedStyle(el).paddingBottom` / `minHeight`. A valid `calc()` yields the exact px
(`7rem`→112px); an INVALID one (`calc(7rem+env(...))` without the `_+_` spaces - CSS `calc` requires
whitespace around `+`) silently drops to `0px`. Works on any page (Tailwind's stylesheet is global).
The real safe-area behaviour still needs a notched device - say so, don't claim it verified.

## 10. iOS standalone LOSES `viewport-fit=cover` on a `next/link` soft nav (2026-07-16, recall)

**Symptom:** in the installed PWA the fixed bottom bar sits correctly on first load, then **lifts off
the home indicator after navigating** - the safe-area inset silently goes to 0 mid-session, so this
looks like a §1/§2 layout bug but the CSS never changed. Only the installed (standalone) app; only
after a client-side route change.
**Cause:** upstream Next bug `vercel/next.js#81264` - the App Router rewrites the viewport meta on
soft navigation and drops `viewport-fit=cover`, and iOS then stops resolving
`env(safe-area-inset-bottom)`.
**Fix (the LIGHT one - use this):** on route change, toggle the existing meta's `content`
attribute (`viewport-fit=auto` → back to `cover`) inside a `requestAnimationFrame`. Cheap, restores
the inset on every online nav.
**The heavier fix that LOST:** removing and re-inserting the whole `<meta name="viewport">` node also
fixed the offline fresh-load case, but it forces a full viewport reflow on EVERY navigation, which
made online route switches visibly slow - reverted. Don't reach for it.
**Accepted limitation:** an offline HARD load still comes up with the bar lifted. Known, not worth
the reflow cost.
**Not reproducible headless** (see the standing rule at the top of this file) - verified on device.
