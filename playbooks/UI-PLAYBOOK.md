# UI playbook: motion, look and iPhone fixes (reusable)

Written 2026-10-14 from Agent Factory (React 19 + Tailwind 4 + Vite, iPhone PWA). Everything here is built and in
use in this repo; each entry says **what it is, why it exists (its purpose), the exact values, and how to build it**,
with the file to copy from. Statuses: **proven** = measured on the iPhone or covered by tests; **headless only** =
checked in a phone-sized browser, not yet on the device.

Sources: `docs/MOTION.md` (the 42-row motion spec), `docs/MOTION-AUDIT.md` (what was built where), `DESIGN_TOKENS.md`,
`web/src/styles.css`, the skills `animate`, `ios-pwa-dock`, `frontend-interaction-patterns`.

---

## 1. How to decide, before building anything

Moved on 2026-10-16 to the `animate` skill, word for word: this gate (section 1), the motion tokens and the motion catalogue (section 3) now live in
`~/.agents/skills/animate/references/ui-playbook/main.md`. Motion fixes update that file; this playbook keeps the
look, the iPhone and Android fixes and the porting checklist.

---

## 2. Foundations: tokens

### Motion tokens

In the `animate` skill (`references/ui-playbook/main.md`, section 2).

### Colour: neutral greys (the "sharper" look)

Purpose: greys with a blue tint (`#1C1C1F`, `#A1A1A8`) read soft next to native iOS apps. Pure greys, sampled from
Linear's iOS app, read sharper at the same lightness, so contrast does not drop.

| token | value | use |
|---|---|---|
| bg | `#0D0D0D` | page (also `theme-color`, the iOS status bar colour) |
| surface-1 / 2 / 3 / 4 | `#151515` / `#1F1F1F` / `#282828` / `#343434` | cards / popovers / chips / selected |
| divider / border | `#202020` / `#2B2B2B` | rows / 1px borders |
| text / 2 / 3 / 4 / 5 | `#F5F5F5` / `#CACACA` / `#A0A0A0` / `#8C8C8C` / `#6E6E6E` | primary ... muted headings |

Also: icon stroke **2** (not 1.8), Linear's icons read bolder. Keep the system font
(`-apple-system, "SF Pro Text", system-ui`): on the iPhone it IS Apple's font, nothing to load.

### Glass (the Linear look for controls)

Purpose: one recognisable material for everything you press (dock, header buttons, tab pills, chips), so the app
reads as one product. Sampled from a 3x Linear screenshot: a neutral grey body a little lighter at both ends, lit 1px
rims top and bottom, a dark outer ring.

```css
:root {
  --glass-top: #2d2d2d; --glass-mid: #282828; --glass-bottom: #2e2e2e; --glass-rim: rgb(255 255 255 / 0.13);
  --glass-on-top: #3e3e3e; --glass-on-mid: #3a3a3a; --glass-on-bottom: #3d3d3d;   /* the selected item */
  --glass-card-top: #1a1a1b; --glass-card-bottom: #151516;                         /* cards: darker */
  --glass-deep-top: #2b2b2b; --glass-deep-bottom: #111113;                         /* avatars */
}
.glass { background: linear-gradient(to bottom, var(--glass-top), var(--glass-mid) 50%, var(--glass-bottom));
  box-shadow: inset 0 1px 0 var(--glass-rim), inset 0 -1px 0 var(--glass-rim), 0 0 0 1px rgb(0 0 0 / .55), 0 2px 8px rgb(0 0 0 / .3); }
.glass-float { box-shadow: inset 0 1px 0 var(--glass-rim), inset 0 -1px 0 var(--glass-rim), 0 0 0 1px rgb(0 0 0 / .55), 0 8px 24px rgb(0 0 0 / .45); }
.glass-on { background: linear-gradient(to bottom, var(--glass-on-top), var(--glass-on-mid) 50%, var(--glass-on-bottom));
  box-shadow: inset 0 1px 0 rgb(255 255 255 / .07), inset 0 -1px 0 rgb(255 255 255 / .05); }
.glass-card { background: linear-gradient(to bottom, var(--glass-card-top), var(--glass-card-bottom));
  box-shadow: inset 0 1px 0 rgb(255 255 255 / .07), inset 0 -1px 0 rgb(255 255 255 / .03), 0 0 0 1px rgb(0 0 0 / .5); }
.glass-deep { background: linear-gradient(to bottom, var(--glass-deep-top), var(--glass-deep-bottom));
  box-shadow: inset 0 1px 0 rgb(255 255 255 / .06), 0 0 0 1px rgb(0 0 0 / .5); }
/* a segmented control made of glass, selection without a sliding pill: */
.glass > [role="radio"][aria-checked="true"] { background: linear-gradient(to bottom, var(--glass-on-top), var(--glass-on-mid) 50%, var(--glass-on-bottom)); }
```

Where each goes: `.glass` on header buttons and button groups, tab pills, chips, secondary buttons; add `.glass-float`
to things floating over scrolling content (dock, round action button); `.glass-on` = the selected item inside glass;
`.glass-card` = cards and grouped lists (full glass on every card washes a screen out); `.glass-deep` = avatars.
Unselected tabs have **no** background (only the selected one is a pill). Keep **text fields** in the plain field style:
their border carries the blue focus colour, and the glass ring would hide it. Keep thin progress tracks flat.
Write the classes unlayered (outside `@layer`) so they beat utility backgrounds.

---

## 3. Motion catalogue

Moved on 2026-10-16 to the `animate` skill, word for word: the whole catalogue (feedback, navigation, sheets, Linear's iOS 26 motion, lists, live work, reduced motion) now live in
`~/.agents/skills/animate/references/ui-playbook/main.md`. Motion fixes update that file; this playbook keeps the
look, the iPhone and Android fixes and the porting checklist.

---

## 4. Look and layout fixes (today's batch, reusable)

**Dock and floating button** (proven sizes, sampled from Linear): dock 56 pt tall, items 58 x 50 pt (the selected one
a `.glass-on` pill inset 3 pt), the round action button 51 x 56 pt, 13 pt apart, centred with
`--dock-x: clamp(12px, calc((100vw - 328px) / 2), 33px)` (33 pt sides on a 393 pt iPhone, smaller on narrow phones
so nothing overlaps). All icons white; only the pill says which is selected. Sits 28 pt above the screen bottom:
`--dock-bottom: max(20px, calc(env(safe-area-inset-bottom) - 6px))`. Purpose: matches the native iOS tab bar weight.

**A dock switcher never points at a screen without a dock** (user, 2026-10-14): the dock's last slot shows the last
place opened from the menu and goes there on tap (it opens the menu only when you are already there). After Search
(which has its own bottom bar, no dock) it became a Search button with no way back to the menu. Places with no dock
are never remembered (`NO_DOCK` in `lib/dock.ts`), and a stored one is ignored, which heals phones that already saved it.

**One icon per thing, everywhere** (user, 2026-10-14: "the search page has different icons than the repo page"): a
repo is drawn with its own icon and colour (`RepoIcon`, set on the repo page) in every list, chip and picker: Repos,
Search, the @ mention sheet, the board agent's repo chip. Never a hard-coded folder: grep for one before shipping.

**Inbox rows like Linear**: two lines (what it needs; then "about what · key · age"), a 40 pt `.glass-deep` round
icon, title 17 px semibold, second line 15 px; **unread** = white + a blue dot, **read** = dimmed (`text-5`). Title of
the page 24 px bold (measured on Linear, see below; 34 and 28 were too loud). Purpose: scannable at a glance, read state without badges.

**List page and detail page like Linear's Projects** (measured from two 3x iPhone screenshots, 2026-10-14; headless
positions within 2 pt, phone look owed). Applied app-wide 2026-10-14: every page and detail title 24 px, every header / sheet-header button and header pill 44 pt (`size-11`, `h-11`, pill items `w-11`); stat numbers keep their size. List: title **24 px** bold on the same row as a **44 pt** glass button (Linear's
buttons are 44, not 48); section label 14 px semibold `text-5` (#6E6E6E, Linear #5F5F5F) ~22 pt under the header;
rows **48 pt**, 20 pt icon, 8 pt gap, name 17 px **medium, full white** (no dimming, no count text on the right), a
20 pt progress ring at the right edge (dashed `text-5` while nothing is done, even with no tasks). Detail: key 13 px
medium `text-4`, title 24 px bold with the **same 20 pt icon** (not a big one), tabs = one **35 pt `.glass` pill** under
the selected tab and nothing behind the others (no track; 15 px semibold, unselected `text-3`, px 14, gap 6);
property chips **flat `surface-2` (#1F1F1F), 29 pt tall, 14 px semibold, 14 pt icon**, 8 pt gaps; **white text = you can tap it, grey (`text-4`) = read-only** (user's rule; in Linear grey means "empty, tap to set") (glass chips read
heavier than Linear's); resource rows = icon + name 16 px medium + one 13 px grey line under it, never a long grey
string squeezed to the right. Purpose: what makes Linear read "sharp" is smaller type with heavier weight and fewer
lit surfaces, not more chrome. Files: `web/src/screens/repos/{Repos,RepoHome}.tsx`.

**@ mentions as chips** (headless + desktop tested): typing @ opens a card of **Tasks** (status icon, dim key, title)
and **Repos** (icon in its colour, name), recent ones before you type, filtered on the device; a pick becomes one
chip that Backspace deletes whole. The saved text stays plain (`@SHELF-7`, `@shelf`) so agents and old data keep
working; sent messages draw the same chips. Library: **Tiptap** (`@tiptap/react` + `extension-mention`), because
chips inside a text field are not reliable on iOS without a real editor. Settings that matter:
`deleteTriggerWithBackspace: true`, `renderText: ({node}) => '@' + node.attrs.id`, a React node view for the chip,
the suggestion `render()` lifting state into React, Enter = send in chat boxes (Shift+Enter = new line). File:
`web/src/components/MentionInput.tsx` (copy whole).

**Queued messages** (live tested): text typed while an agent works shows as a dashed "Queued · tap to edit" bubble;
tap to edit or delete before it is sent. Purpose: no lost thoughts, no wrong message sent mid-turn.

**Connection drops** (`docs/RESILIENCE.md`): a write tapped while offline is refused with a toast (no outbox: a held
tap would be lost); a write tapped in the seconds before the app notices the drop says "No answer from the box.
Check it went through once it reconnects." and starts reconnecting at once; buttons never stay stuck disabled.

**A tap outside a popup only closes it** (user, 2026-10-18: "I tap outside the options menu, it lands on a text field
and the keyboard opens"). A Radix `Popover` is non-modal by default: the outside tap closes it AND reaches whatever is
underneath (measured on a phone-size touch run: the board menu closed and the task under the tap opened). Every
`<Popover.Root modal>` blocks outside pointer events while it is open, so the tap only closes it (same run: the URL
stayed; a text field under the tap stayed unfocused, and a second tap focused it). Sheets and dialogs already have a
backdrop that takes the tap. Check: grep `<Popover.Root` and confirm each says `modal`.

**A chip sits on the text's centre line** (user, 2026-10-18: "the letters after @ sit on top of the chip"). An inline
26 pt chip (`inline-flex`) is aligned by its own text baseline; `vertical-align: -6px` left the typed text's centre 4 px
above the chip's in a 16 px field (measured with a text Range against the chip box). `-2px` centres it: 0 px gap at 16 px,
0.5 px at 17 px. Measure the centres, not the screenshot, when a font size changes.

**A picker with a search field is a card on a phone, never a menu above a button** (user, 2026-10-19, screenshots of
the board chat's Skills menu). With the iOS keyboard up, a popover placed above its trigger ran off the top of the
screen (search field hidden, nothing reachable), and a drag scrolled the page behind it. On a touch screen
(`(pointer: coarse)`) Skills opens the shared `PickerCard` with `SearchField`, whose search does not take the focus on
open; measured at phone size with touch: the card's list scrolled 649 px while the page stayed at 0, and a pick closed
it. The desktop keeps the menu.

**Information behind an icon opens a bottom sheet** (user, 2026-10-18, like the Claude app): the context ring is only a
ring; a tap opens a vaul sheet over the bottom of the screen with the numbers (big share, a bar, tokens of window, what
to do past 80%). Above the board chat panel: overlay `z-[75]`, sheet `z-[80]`.

---

## 5. iPhone (installed PWA) fixes: what bit, the measured cause, the fix

Rule from `ios-pwa-dock`: **measure on the device before changing CSS** (a ~40-line probe that posts
`visualViewport`, `innerHeight`, element rects to a log-only endpoint; recipe in the skill's `launch-probe.md`).
Headless browsers cannot see any of these bugs: no standalone mode, safe areas are 0, no keyboard.

| symptom | measured cause | fix | status |
|---|---|---|---|
| Dock floats ~100 px too high until the first scroll | iOS 26 + `apple-mobile-web-app-status-bar-style: black-translucent`: the layout viewport is short by the top inset (inner 793 of 852, inset 59) | status bar style `default` + `theme-color` = page background; **reinstall the PWA** (iOS reads it only at Add to Home Screen) | proven |
| Dock or a bar strands mid-screen after a fast scroll | WebKit repaints fixed layers late | `transform: translateZ(0)` on the fixed bar; no `backdrop-filter` on it | proven |
| Dock wrong only on short pages | `height: 100%` chains | `min-height: 100dvh` on body, never `height: 100%` | proven |
| Dock stuck mid-screen after the keyboard closes | phantom keyboard inset | a `ResumeReseat` component that re-seats the layout on resume / blur | proven |
| A sheet with an input shoots up when you type | Safari scroll-into-view moves a content-height sheet | vaul `repositionInputs={false}`, fixed-height sheet (`h-[85vh]`, not `max-h`), pinned header + one inner scroll, **never `autoFocus`** | proven |
| Chat sheet: header disappears and a gap sits over the keyboard | **measured 2026-10-14**: with the keyboard up, `innerHeight` AND the visual viewport are 390 while the layout viewport (`clientHeight`) stays 793, and iOS scrolls the page so the visible area starts at 403 | detect the keyboard as `clientHeight - visualViewport.height > 80` (NOT `innerHeight`); then the layer gets `top: vv.offsetTop + gap`, `height: vv.height - gap`, a 250 ms transition on top/height (keep the sheet library's own transform transition in the same inline value) | **proven** on the iPhone 2026-10-14 (probe readings, then the user's screenshot) |
| Welcome / empty-state content scrolls inside a chat sheet when the keyboard is up | a web app also gets the 44 pt form bar above the keyboard, so less room than a native app (measured 291 pt of content in 194) | compact empty state (17 pt title, 30 pt starter buttons) and, while the keyboard is open (`!!useKeyboardFit()`), only the title and the starters; icon, subtitle and hints return when it closes | fits exactly at the phone's numbers (headless); phone look owed |
| Closing the chat sheet with the keyboard up: the sheet looks "half open" mid-close | its slide-out, the keyboard going down, iOS scrolling the page back and the keyboard-fitted sheet regrowing all ran at once | `closeAboveKeyboard(fn)` (`lib/keyboard.ts`): with the keyboard up, blur the field and close at once with a **150 ms fade instead of the slide** (`html[data-kb-close] [data-vaul-drawer][data-state="closed"] { animation: af-fade-out var(--dur-fast) ease both !important }`); the page jump comes after the keyboard is down, with nothing on screen. No keyboard = the normal slide. First version waited for the keyboard + regrow and felt slow (user, 2026-10-14) | **proven** on the iPhone (user, 2026-10-14) |
| The @ card ran under the status bar: its top row half hidden, so it looked like the end of the list | a fixed 300 pt card with only ~190 pt free above the box (keyboard up) | the card's max height = the room between the sheet's header and the box (`useLayoutEffect` on open), `data-vaul-no-drag` so swipes scroll the list instead of dragging the sheet, `overscroll-contain`, and a bottom fade (`mask-image`) while rows remain below; arrow keys scroll the highlighted row into view. Re-measure on every space change (a `ResizeObserver` on the sheet + `visualViewport` resize): @ typed while the keyboard is still rising measured the full-height sheet and kept 300 pt. Every new card and every new search starts scrolled to the top | race + reset proven headless (300 pt before the keyboard, 181 pt under the header after; scrollTop 0 after typing); phone look owed |
| The ⌃ ⌄ ✓ bar above the keyboard | iOS adds it (the "form accessory bar") for every text field in Safari and home-screen web apps; no HTML / CSS / JS setting exists, also not in iOS 26 (checked 2026-10-14: Ionic keyboard docs, Apple Community) | a web app cannot remove it: plan the layout for its 44 pt (section 5, welcome row). Only a native wrapper can: Capacitor `Keyboard.setAccessoryBarVisible({ isVisible: false })` (iOS build needs a Mac + Xcode and an Apple developer account). One text field per screen may drop the arrows, never the ✓ (unverified) | known limit |
| Keyboard opens and the page zooms | inputs under 16 px | inputs at 16 px or more | proven |
| A device silently gets no push (opened in a Safari tab, permission blocked, or never subscribed) and nobody notices until an alert is missed | nothing on screen says this device is not subscribed; the server only knows some device is | a board pill from `pushState()` (no `PushManager` = unsupported, `Notification.permission` denied = blocked, no `getSubscription()` = off): "Turn on" calls the subscribe from the tap (iOS asks only from a user gesture), "How" toasts the fix for blocked or unsupported, an x hides it 7 days in `localStorage`. Agent Factory `web/src/lib/push.ts` + `PushBanner` in `Board.tsx` (D186) | headless proven; iPhone granted path owed |
| Tapping a toolbar button next to a text box (paste a screenshot) closes the keyboard | the tap moves focus from the box to the button, and iOS drops the keyboard on blur | `onPointerDown={(e) => e.preventDefault()}` on the button: the tap never takes focus, the click still runs (Agent Factory board chat paste) | unverified: headless keeps focus even without the fix, so only the iPhone can prove it |
| A link inside a sheet, picker or editor (More models, a task link in a chat) leaves the screen, and Back returns with the sheet closed and what was typed gone | the sheet or box unmounted; its text lived in component state | (1) a picker's "More models" opens one shared sheet over the screen instead of a page (`ModelsSheetHost` in the shell, `modelsSheet.open(h)`), so nothing unmounts; (2) every text box keeps its unsent text in memory per box until sent (`useUnsent(key, initial)`, `lib/unsent.ts`: comment, run and plan chat, Request changes notes, the board chat); (3) a chat link records a one-trip detour that reopens the chat on Back (`agentPanel.detour()`). Agent Factory | proven headless (models sheet over New task and its picker; a comment back after leaving the page; detour test) |

The keyboard fit, as code (`web/src/lib/keyboard.ts`):

```ts
export function useKeyboardFit(gap = 0) {
  const [fit, setFit] = useState<{ top: number; height: number } | null>(null);
  useEffect(() => {
    const vv = window.visualViewport;
    if (!vv) return;
    const update = () => {
      const open = document.documentElement.clientHeight - vv.height > 80; // NOT innerHeight: it shrinks too on iOS
      setFit(open ? { top: Math.round(vv.offsetTop + gap), height: Math.round(vv.height - gap) } : null);
    };
    vv.addEventListener("resize", update);
    vv.addEventListener("scroll", update);
    return () => { vv.removeEventListener("resize", update); vv.removeEventListener("scroll", update); };
  }, [gap]);
  return fit; // style={fit ? { top: fit.top, bottom: "auto", height: fit.height, paddingBottom: 0 } : undefined}
}
```

Which changes need a PWA reinstall: status bar style, `apple-mobile-web-app-capable`, title, everything in the
manifest (name, icons, start_url, display). Everything else (CSS, JS, `theme-color`, viewport meta): fully close the
app from the app switcher and reopen.

---

## 5b. Android + Chrome fixes (any mobile browser, not only the iPhone)

Found 2026-10-14 after the header-button slide (section 3, "6. New header buttons slide in like a slingshot") shipped.
Headless Chromium CAN see these (they are not iOS-only), but only with the right probe: see "How it hid" below.

| symptom | measured cause | fix | status |
|---|---|---|---|
| The dock disappears for ~0.5 s after Search -> back arrow, and on other screen changes (user, Android + Chrome) | The new header buttons start their slide just past the right edge of the window, so for the length of the slide the page is wider than the screen; mobile browsers then grow the layout viewport to fit (Pixel 7: 412 -> 544 pt wide, so 839 -> 1108 tall) and every fixed bar moves with it: the dock's top went 763 -> 1032, below the 839 pt screen, for ~470 ms. Proven by disabling only that animation: the dock stayed at 763 | `header { overflow-x: clip }` (vertical overflow stays visible: the press lens sticks out below the pill). General rule: **anything that animates in from off-screen sits inside an `overflow-x: clip` box**, or a phone zooms the whole layout out | **proven** (user on the phone: "perfect", 2026-10-14) |
| Every screen push / pop switched abruptly, no slide; the dock jumped instead of morphing (Chrome, Android) | The same slide was started from a `MutationObserver` that fires INSIDE the view transition's DOM update, with its element off-screen; Chrome aborts the transition: page error `Transition was aborted because of invalid state` (normally the duplicate-`view-transition-name` error, but no name was duplicated). Found by bisecting today's commits on the dev server with a page-error listener: clean before the slide, broken from it on | start the animation one `requestAnimationFrame` later, after the capture (the element is hidden until then) | headless-proven: no aborts on live |
| Opening New task crashed the whole app: "Something went wrong! destroy is not a function" (desktop Chrome, 2026-10-19; found by the first `verify-agent-factory` run) | Two one-line effects returned their call's value: `useEffect(() => el?.scrollTo({ ..., behavior: "smooth" }), [x])` and the same with `scrollIntoView`. Newer Chrome makes smooth scroll calls return a Promise, React takes it for a cleanup function and throws when the effect re-runs. Safari still returns undefined, so the phone never showed it | Never return a call's value from an effect: `useEffect(() => void el?.scrollTo(...), [x])` or a block body. Grep: `useEffect\(\(\) => [a-z]` and check each returns nothing | fixed (NewTask.tsx, MentionInput.tsx) |

How it hid (keep these, each cost a round):
- **A DOM check is not a paint check.** `getComputedStyle(dock).opacity` was 1 and the element existed the whole time;
  the dock was simply below the screen. What showed it: a CDP screencast (`Page.startScreencast`, every frame, time
  stamped against the tap) measuring bright pixels in the bottom strip (dock missing 580 ms), then
  `getBoundingClientRect().top` per frame (763 -> 1032).
- **Start a sampler from inside the page.** A Playwright `evaluate_handle(promise)` followed by `tap()` queues the tap
  behind the sampling: every frame showed the PREVIOUS screen and looked like a missing dock. Install a
  `pointerdown` listener (capture, once) that starts a `requestAnimationFrame` loop, then tap, then read the result.
- **`get_by_label(...).first` can be a hidden copy** (the desktop sidebar renders its own "New task"): a "never
  visible / stable" timeout was that, not a stuck animation.
- Emulate the phone, not just its width: `p.devices["Pixel 7"]` (touch, mobile viewport); the layout viewport only
  grows on a mobile viewport.

---

## 6. Copying a look from a screenshot (the method used here)

1. Ask for a screenshot **from the phone** (full resolution; an iPhone is 3x: divide pixels by 3 for points).
2. Sample exact colours and edges with a headless browser: draw the PNG on a canvas and read `getImageData` at points,
   or scan a row / column for colour changes to get edges and sizes. The brightest pixel in a box = the text colour.
   Without a browser: `uvx --with pillow python -I bands.py shot.png` scanning rows/columns against the page colour.
   Font size from a glyph: cap height / 0.705 (SF Pro), so a 17 pt tall capital = 24 px text. Measure fills mid-body,
   not near the rounded ends (the corner radius shortens the column).
3. Compare against your own screenshot at the same viewport (393 x 852, scale 3) at the same points.
4. Turn the numbers into tokens (never hard-code in components), then screenshot again.

---

## 7. Porting checklist for a new app

- [ ] Anything that animates in from off-screen sits inside an `overflow-x: clip` box (5b: else phones zoom the layout and fixed bars drop). Animations started from a DOM observer wait one `requestAnimationFrame` (else a running view transition aborts).
- [ ] Motion tokens + the press rule + the reduced-motion switch in the global CSS.
- [ ] `vaul` (sheets), `sonner` (toasts), `motion` (lists, springs), `@dnd-kit` (drag), Radix/shadcn (popovers) - never hand-rolled.
- [ ] `SlidingPill`, `ListRow`, the `POP` string, `pushType` + the view-transition CSS.
- [ ] Neutral grey tokens, glass classes, icon stroke 2, system font.
- [ ] iOS shell: status bar `default`, `theme-color` = background, `min-height: 100dvh`, dock `translateZ(0)` and no
      backdrop-filter, `--dock-bottom` / `--dock-x`, `ResumeReseat`, sheets with inputs per section 5, `useKeyboardFit`
      on any full-height layer with a text box.
- [ ] Mentions: copy `MentionInput.tsx` (Tiptap) if the app has @.
- [ ] Feel-check on the real iPhone: play suspicious motion at slow speed in Safari's Web Inspector, look again the
      next day.
