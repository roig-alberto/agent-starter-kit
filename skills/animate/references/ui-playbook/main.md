# UI playbook: motion (moved from Agent Factory)

Moved word for word from `~/projects/agent-factory/docs/UI-PLAYBOOK.md` on 2026-10-16 (user: this skill is the
source for motion; the playbook keeps the look, the iPhone and Android fixes and the porting checklist). Paths such
as `web/src/...`, `docs/MOTION.md` and "UI-PLAYBOOK section 4" are in `~/projects/agent-factory`. The section numbers
are the playbook's; its section 2 here holds only the motion tokens.

---

## 1. How to decide, before building anything

Run every animation through this gate (the `animate` skill). It stops most bad motion before it is written.

1. **How often does it happen?** 100+ times a day (keyboard shortcuts, the command palette) = **no animation, ever**.
   Tens a day (tabs, buttons, rows) = fast and subtle. Occasional (sheets, menus, toasts) = normal. Rare (approving a
   plan, first run) = the only place for delight.
2. **Name its purpose** in one word: *feedback* (the app heard you), *spatial* (where something came from or went),
   *state* (something changed), *preventing a jarring change*, *direct manipulation* (it follows the finger),
   *delight* (rare only). No purpose = do not animate.
3. **Cheapest tool**: CSS transition > CSS keyframes (off the main thread) > the `motion` library (springs, layout
   moves, exits) > a component library for the whole thing (vaul sheets, sonner toasts, @dnd-kit drag).
4. **Only `transform` and `opacity`** (plus `filter`, `clip-path`). Never width/height/top/left, except one tolerated
   case: collapsing the gap after a list row leaves.
5. **Interruptible**: anything that can fire twice in a second uses a transition (retargets), never keyframes.
6. **Reduced motion ships in the same commit**: fewer and gentler, not zero. Fades stay, movement goes.
7. **Data the user reads does not move for style** (charts, budget bars, numbers).

Never: `ease-in` on UI, `transition: all`, `scale(0)` (start at 0.95), keyframes on toggles or toasts, hover motion
on touch (gate hover under `@media (hover: hover) and (pointer: fine)`).

---

## 2. Foundations: tokens

### Motion tokens (define once; components never hard-code a timing)

```css
@theme {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);      /* entrances, exits, feedback */
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);  /* things moving on screen */
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);   /* iOS-like sheets and screen pushes */
}
:root {
  --dur-press: 120ms; --dur-fast: 150ms; --dur-base: 200ms; --dur-move: 250ms; --dur-sheet: 400ms;
}
```

Purpose: one place to tune the feel of the whole app; every value comes from the `animate` skill's tables.

---

## 3. Motion catalogue

### Feedback

**Press on everything tappable** (tens/day, feedback). Every button, link, tab, menu item, switch, checkbox scales to
0.97 while pressed: 120 ms down, 160 ms back, `--ease-out`. One global CSS rule, no per-component work. Uses the
individual `scale` property so it composes with any transform the element already has. It also carries the colour
transitions, so hover and selected colours ease instead of snapping. `data-no-press` opts out (canvas items).
Reduced motion: opacity 0.85 instead of scale. iOS needs a `touchstart` listener on `document` for `:active` to fire.

```css
:is(button, a[href], [role="button"], [role="tab"], [role="menuitem"], [role="option"], [role="switch"], [role="checkbox"], summary):not([data-no-press]) {
  transition-property: scale, opacity, color, background-color, border-color, box-shadow;
  transition-duration: 160ms; transition-timing-function: var(--ease-out);
}
:is(button, a[href], [role="button"], [role="tab"], [role="menuitem"], [role="option"], [role="switch"], [role="checkbox"], summary):not([data-no-press], :disabled, [aria-disabled="true"]):active {
  scale: 0.97; transition-duration: var(--dur-press);
}
```

**Round check circles** (occasional, feedback): fill `scale(0.9)` to 1 plus a drawn tick, `--ease-out` 150 ms
(`components/CheckCircle.tsx`). **Drawn tick** (rare, delight): put `pathLength="1"` on the path, animate
`stroke-dashoffset` 1 to 0 in 300 ms `--ease-out` (class `af-draw`); used once per task on "Approve plan", where the
button label crossfades to "Approved". **Switches**: knob translateX + track colour, 200 ms (shadcn switch).
**Selectable cards**: border colour only, `ease` 150 ms (no scale: they are compared side by side).

### Navigation

**Sliding pill** (tens/day, spatial): one highlight that slides to the selected tab / dock item instead of each item
having its own background. 200 ms `--ease-in-out`, retargets mid-slide, first placement does not animate, reduced =
instant. One component (`components/SlidingPill.tsx`): it measures the selected sibling (`aria-selected`,
`aria-checked`, `aria-current="page"`) with a ResizeObserver + MutationObserver and moves an absolutely positioned
span with `translate`. Put it first inside a `relative isolate` container.

**Push / pop a screen** (tens/day, spatial): going one level deeper slides the new screen in from the right while the
old one moves 20% left and dims; back is the exact reverse. 250 ms `--ease-drawer`. Same-document **View
Transitions** with types, decided by path depth (`lib/motion.ts` `pushType`): deeper = push, shallower = pop, same
level (dock, tabs) = no transition. The dock and floating buttons get their own `view-transition-name` so they fade
instead of sliding with the page. Reduced: 150 ms crossfade. Limitation: no swipe-back (a view transition cannot
follow a finger).

```css
html:active-view-transition-type(push, pop)::view-transition-old(root),
html:active-view-transition-type(push, pop)::view-transition-new(root) {
  mix-blend-mode: normal; animation-duration: var(--dur-move); animation-timing-function: var(--ease-drawer); animation-fill-mode: both;
}
html:active-view-transition-type(push)::view-transition-old(root) { animation-name: af-under; }
html:active-view-transition-type(push)::view-transition-new(root) { animation-name: af-from-right; }
html:active-view-transition-type(pop)::view-transition-old(root) { animation-name: af-to-right; z-index: 1; }
html:active-view-transition-type(pop)::view-transition-new(root) { animation-name: af-from-under; }
@keyframes af-under { to { transform: translateX(-20%); filter: brightness(0.6); } }
@keyframes af-from-under { from { transform: translateX(-20%); filter: brightness(0.6); } }
@keyframes af-from-right { from { transform: translateX(100%); } }
@keyframes af-to-right { to { transform: translateX(100%); } }
```

**Shared-element zoom** (occasional, spatial): an item grows from its spot to full screen and shrinks back
(`view-transition-name` on both, `--ease-drawer` 400 ms; reduced = crossfade). Used for a design artboard opening.

**Badge count** (tens/day, state): the number fades in when it changes (`key={count}` + a 150 ms fade).

### Sheets, menus, toasts

**Bottom sheets** (occasional, spatial): rise from the bottom with a backdrop fade, drag down to dismiss by velocity,
exit the same way. Library: **vaul**. 250 ms open / 200 ms close since 2026-10-14 (was 400; vaul's default 500 feels slow): `[data-vaul-drawer], [data-vaul-overlay]
{ animation-duration: var(--dur-sheet) !important }`. Reduced: 150 ms fade. Sheets with inputs: see section 5.

**Popovers and menus** (occasional, spatial): scale 0.95 + fade **from the trigger corner** (Radix gives the origin),
180 ms in, 150 ms out, `--ease-out`. One shared class string for every popover (`lib/motion.ts` `POP`):
`origin-(--radix-popover-content-transform-origin) duration-[180ms] ease-(--ease-out) data-[state=open]:animate-in
data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0
data-[state=closed]:zoom-out-95 data-[state=closed]:duration-(--dur-fast)`. Centred picker cards (modals) scale from
the centre instead. Submenus replace the menu (8 px slide + fade) or expand in place while the parent items dim.

**Long press** (occasional, spatial): hold 350 ms, the row lifts (`scale(1.02)` + shadow), the menu grows from the row.

**Toasts** (occasional, feedback): **sonner** (transitions, swipe to dismiss, stacking). Never hand-roll.

### Linear's iOS 26 motion, copied frame by frame (2026-10-14)

Status (2026-10-14, end of day): **approved by the user on the iPhone**: the menus (over the pill, inside out, the slower
spring), the slingshot icon, and the Android / Chrome dock fix (section 5b). The press circle that section 1 first
copied was iOS Show Touches from the recording; removed everywhere. Everything else in
the index is matched to Linear's frames and measured headless; its feel on the phone is still owed (checklist:
"Still to check on the phone" below). Every code block
below is copied from the live code (regenerated at the end of the day).

Index (status 2026-10-14):

| # | animation | where it came from | status |
|---|---|---|---|
| 1 | Header press: the glass brightens, no shrink (the grey circle was iOS Show Touches, removed) | Linear recording | brightening: headless only |
| 2 | Menus open over the buttons, inflate from the button's centre, spring | Linear recording | **approved** ("perfect", played 25% slower) |
| 3 | Menu icon returns like a slingshot | Linear recording | **approved** |
| 4 | Sheets 250 / 200 ms; dock steps aside under a sheet | Linear recording | headless only |
| 5 | Dock morphs into a task's bottom bar | Linear recording | headless only |
| 6 | New header buttons slide in like a slingshot | the user's ask (no recording) | the Android bug it caused is fixed and **approved**; the slide itself: phone feel owed |
| 7 | Dock morphs into Search's bar and back | the user's ask | headless only |
| 8 | The dock becomes its menu (squeeze, shoot up, 5% overshoot, settle) | Linear recording | headless only |
| 9 | Picker modals: centred, blurred page, 140 ms in / 150 ms out | Linear recording | headless only |
| 10 | Copy unrolls a panel over its menu; search pickers ready to type; Linear's picker sizes | Linear recording | headless only |
| 11 | Rows light up (no shrink), dock places cross-fade (the tab / dock circle was Show Touches, removed) | Linear recording | headless only |
| 12 | The @ card's scroll indicator (always there while the list is longer than the card) | Linear recording | headless only |
| 13 | Agent chat: ready to type, history sheet, attach menu, thinking shimmer, message pill | Linear recording | headless only |
| 14 | The same look on every other screen (headers, Triage rows, flat chips, sharper lists; 2026-10-14 the task sub-pages and Needs you screens too) | the user's ask | headless only |

#### Still to check on the phone (2026-10-14)

These are matched to Linear's frames and measured in a headless browser, but nobody has felt them on the iPhone
yet. Tick one when it is tried on the phone; if it feels wrong, record a screen video of OURS and compare it frame by
frame with the Linear recording (the method below).

- [ ] **4. Sheets + the dock stepping aside.** Open New task from the Board, then close it. Expect: the sheet up in a
      quarter second, down a bit faster; the dock fades away while the sheet is open and pops back as it leaves.
- [ ] **5. Dock into the task's bottom bar.** Open a task from the Board, then go back. Expect: the dock shrinks into
      the round Needs you button, Comment grows out of it, the chat button turns into the task's agent button; back
      reverses it. No abrupt switch.
- [ ] **6. Header buttons slide in.** Switch Board -> Needs you -> Repos from the dock. Expect: the new buttons come
      in from the right edge, go a few points past their place and settle; same buttons = no motion. (The Android
      dock bug this caused is fixed and approved.)
- [ ] **7. Into Search and back.** Open Search from the menu, then tap the back arrow. Expect: the dock shrinks into
      Search's back button and the search field grows out of it; back turns them into the dock again; the page fades.
- [ ] **8. The dock becomes its menu.** Tap the dock's last button, then tap outside. Expect: the dock's icons blur,
      it squeezes a little, then shoots up into the menu (a touch too tall, then settles); the menu's text arrives
      blurred and sharpens; closing sinks it back into the dock.
- [ ] **11. Rows + dock switch.** Press a Board row: it lights up, no shrink; switch dock places: the page
      cross-fades quickly. Press a header button: its glass brightens (no circle anywhere).
- [ ] **9 + 10. Pickers and the Copy menu.** On a task tap Priority, then Labels, then "..." > Copy. Expect:
      Priority centred over a dark, blurred page, fast in, blurring out; Labels pinned near the top with the cursor in
      its search field **and the keyboard up** (the one thing headless cannot show: whether iOS raises the keyboard);
      closing Labels while typing drops the keyboard first; Copy expands inside the menu (arrow turns, the rest
      a panel unrolls down from the Copy row over the items below, the rest of the menu dims).

- [ ] **New task opens ready to type** (2026-10-14, the user's ask): tap + on the Board (or Needs you, Favorites, a
      repo's +, Create sub-task, a draft): the sheet slides up with the keyboard already up and the cursor in the
      title. Same trick as the agent chat: `primeKeyboard()` in the tap, then the sheet's title takes the focus on mount
      (`preventScroll`, so Safari does not scroll the page while the sheet slides in). Watch: the sheet must not jump
      off the top (why it had no autofocus before).
      **Chips + toolbar on the keyboard** (2026-10-15, the user's Linear screenshot): while the keyboard is up the sheet
      fits the visible area (`useKeyboardFit(8)` + `KEYBOARD_MOTION` on the vaul content, as the agent chat), the title
      and description scroll in the area above, and the chips + formatting toolbar are a pinned footer that sits right
      on the keyboard. "Create more after this" and the footnote hide while typing (Linear shows only the chips and the
      toolbar there); closing goes through `closeAboveKeyboard`. Headless with a faked 500 px visual viewport: sheet
      bottom 500, toolbar bottom 492. Phone check owed.
      **Pickers over the typing sheet** (2026-10-15, Linear recording): (1) while a picker is open the sheet drops its
      keyboard fit AT ONCE (no top/height transition), so the card centred in it appears where it stays instead of
      sliding down as the keyboard leaves; (2) the field that had the keyboard is recorded when the chip is tapped and
      focused again INSIDE the closing tap (`closeTo` in `pickers.tsx`): `flushSync(onClose)` first, else the still-open
      Radix dialog's focus trap pulls the focus back, and `onCloseAutoFocus` is prevented when a text field already has
      the focus (else Radix hands it to the chip after the exit animation and the keyboard drops). A picked option closes
      at once in that case (the 120 ms tick delay would put the focus outside the tap, and iOS raises the keyboard only
      inside one). (3) Search pickers (Template, Repo, Labels) call `primeKeyboard()` in the chip tap and focus their
      search on open, so the keyboard never drops. Headless: card top fixed at 225 px, focus back in the title / editor.
      **Sharper, measured at 3x against Linear**: chips 36 pt flat `bg-surface-3` + 1 px top highlight, 15 px
      semibold (unset ones `text-text-4`); toolbar 48 pt, icons at stroke 2.2, quote and list dots filled. Medium weight,
      thin 1.8 strokes and the gradient glass read soft next to it.
      **Rich description**: Tiptap's own CodeBlock (React node view: line-number gutter, native `<select>` for the
      language at 16 px so iOS does not zoom), BulletList / TaskList / ListItem / TaskItem (nested) / ListKeymap,
      Blockquote, in a `rich` mode of the shared MentionInput; the value stays plain markdown (`lib/richtext.ts`
      richDoc / richText, round-trip tested). In a list the toolbar grows Outdent / Indent and scrolls to them.
      **The @ card inside the scrolling text area** (2026-10-15, the user: "the @ window is not implemented"): pinning
      the chips under a scrolling text area hid the absolute @ card whole (measured 398-518 px under an area ending at
      390; the card existed, 7 rows, invisible). Fix, as Linear: the area carries `data-mention-bounds`; the card is
      `position: fixed` under the caret (`view.coordsAtPos(selection.from).bottom + 8`) and fills to the area's bottom,
      re-measured on the area's scroll, the query and the keyboard. A transformed ancestor (vaul's sheet) is a fixed
      element's frame, so subtract its rect only when `getComputedStyle(host).transform !== "none"`. A bare @ shows
      "Type to search tasks and repos"; the list comes with the first letter. Headless: 174-388 px over chips at 444,
      the tap reaches it, a pick makes the chip.
- [ ] **Linear's date card** (2026-10-15, D132): a floating `PickerCard` (top), tabs Day / Month / Quarter / Half-year /
      Year as 32 pt pills (the chosen one `bg-surface-4`), a 350 pt body that scrolls by itself, "Remove <title>" under a
      hairline. Day = react-day-picker with `hideNavigation` and our own header: "October 2026 ›" (the › and the ‹ › arrows
      in `text-brand-text`), MON..SUN in 11 pt semibold grey, 40 pt round days, today in blue, the picked day a blue disc,
      outside days invisible. The title holds a transparent `<input type="month">` (16 px, so no zoom): the iPhone opens
      its own month + year wheel there, a computer gets `showPicker()`. Time cards (Remind, Snooze, Due date, Start
      later) are the same card: quick times with the time on the right, "Pick a date" = the calendar + a native time
      field and one blue button "Remind me · 22 Oct at 18:30". Inside a vaul sheet: `portal={false}`.
- [ ] **New project sheet** (2026-10-15, D133, Linear's New project): New task's shell (keyboard fit, pinned chips,
      `picking` freezes the fit), a 36 pt icon tile left of a 24 pt bold name, a summary, chips Stack / Architecture /
      Design / hostname / Start / Target date (unset ones grey), the explanation line only with the keyboard down.
      Repos "+" is a Popover menu that grows out of the button it covers (`sideOffset={-44}`, origin at the button),
      like the repo page's.
- [ ] **Plan Steps on the task page** (2026-10-15, D135): same look as Sub-tasks (13 pt grey heading with "2 of 4" on the
      right), 18 pt icons: done = `CircleCheck` in `text-verifying` with the text dimmed, the step being worked on =
      `LoaderCircle` spinning in `text-brand-text` (still under reduced motion), to do = `Circle` in `text-text-5`.
      Refetched every 4 s only while the task is Implementing (`refetchInterval` from the query's own data).
- [ ] **The plan on the task page** (2026-10-15, D136): a section like Sub-tasks (13 pt grey heading "Plan · Architect ·
      Claude Opus 5.5 · 5m ago", a History button with the version number), the architect's open question in a
      `bg-brand-soft` card with `border-brand/40` and an Answer button, the plan in a `glass-card` clipped at 360 pt with
      a mask fade and "Show the whole plan", then a full-width "Approve & implement" and four equal glass pills (Ask, Grill
      me, Edit, Reject in `text-danger`). Edit is a full-height sheet with a monospace textarea; the others a short sheet.
      Landing on `#plan` scrolls there once the plan has loaded (the page renders before the data).
- [ ] **Plain words under every setting** (2026-10-15, D134): a two-line row (17 pt name, 13 pt `text-text-4` sub-line,
      `py-2.5`), the value on the right `shrink-0 whitespace-nowrap` (without it "2 connected" broke onto two lines once
      the sub-line took the width). Menus use the same pattern as "Remove from board": `items-start py-2.5`, icon `mt-0.5`.
- [ ] **12 + 13. The agent chat.** Tap the dock's chat button: the keyboard should come up by itself (the phone
      check: iOS may refuse); type @: a thin scroll bar inside the list's right edge; tap the paperclip: Browse files /
      Photos; tap history: a sheet with Today and ages, pick a chat: it opens ready to type; send something: "Thinking..."
      shimmers, then "Worked for Ns" above the reply.

#### The method (use it for any "make it move like app X")

1. Ask for a **screen recording from the phone** (iPhone = 3x: 1179 px wide = 393 pt). A still screenshot cannot show
   motion; a recording of OUR app is the way to compare when something "feels" off.
2. ffmpeg without installing it: `uvx --with imageio-ffmpeg python -c "import imageio_ffmpeg as f; print(f.get_ffmpeg_exe())"`.
3. Extract the **native frames**, never resampled: `-vf showinfo -fps_mode passthrough` (keep each frame's `pts_time`).
   **Bit us:** a first pass at `fps=60` duplicated frames and smeared a one-frame snap into what looked like a 70 ms
   fade; the copy was wrong and the user caught it. Scale to 393 px wide (1 px = 1 pt) for positions, full resolution
   for colours.
4. Find the moments: mean absolute difference per screen region between consecutive frames (header / menu / bottom).
5. Measure per frame: bounding box of what changed against a rest frame (size -> scale, position -> origin), the
   brightest pixel in a box (text / rim colour), a fill sampled mid-body (not near rounded ends). Contrast-boost a few
   frames to see subtle things (the page did NOT dim; a "slingshot" did happen).
6. Origin of a scale: `left(s) = xo + (left_final - xo) * s` on two frames gives xo. Spring: fit damping / frequency /
   start scale to the measured points (a small grid search), sample it into CSS `linear()` (33-37 points).
7. Check the copy the same way: sample computed styles every animation frame in a headless browser (`requestAnimationFrame`
   loop reading `getComputedStyle`), compare the numbers row by row, then let the user feel it on the phone.

#### 1. Header button press: the glass brightens (feedback)

While a header button is held, its glass pill (or the round glass button) brightens #282828 -> #3C3C3C; no shrink.
That is all. **Not copied, on purpose:** the 44 pt grey circle with a light rim over the pressed button in Linear's
recordings is **iOS "Show Touches"** (the screen recorder marking the finger), not Linear's UI. I copied it for a
whole evening (header buttons, the X on pickers, then tabs and the dock) before the user pointed it out ("it is an
animation of the recording to show what I am clicking"); it was removed everywhere. Lesson for any copy-from-a-video
job: a circle that follows the finger, appears in one frame and vanishes on release is the recorder, not the app;
ask whether Show Touches was on before measuring presses.

```css
/* Row 1b: header buttons: while held the glass pill (or the round glass button) brightens #282828 -> #3C3C3C, no shrink
   (Linear, recorded 2026-10-14). NOT copied: the grey circle with a light rim in those recordings is iOS "Show
   Touches" marking the finger, not part of Linear's UI (the user, 2026-10-14). */
header :is(button, a[href]).glass:not(:disabled):active,
header .glass > :is(button, a[href], [role="button"]):not([role="tab"], :disabled):active {
  scale: none !important; /* beats row 1's shrink, which matches the same elements */
}
header .glass:has(> :is(button, a[href], [role="button"]):not([role="tab"], :disabled):active),
header :is(button, a[href]).glass:not(:disabled):active {
  --glass-top: #3c3c3c;
  --glass-mid: #3c3c3c;
  --glass-bottom: #3c3c3c;
}
```

#### 2. The menu: opens over the buttons, inflates from the button (spatial)

Header menus open **over** their pill: top-right corner on the pill's top-right (Linear: menu top 59 = pill top, right
373 = pill right). They grow from the **centre of the button** that opened them ("inside out", the user's words), scale
0.4 -> 1 on a spring fitted to Linear's frames (damping 0.72, 24 rad/s: 0.66 at 89 ms, 0.94 at 145, peak 1.024 at 235,
settled ~420), **played 25% slower** at the user's ask (560 ms; fade 190 ms), content scaled along with it. Close:
150 ms to 0.5 + fade. On open the button's icon shrinks to 0.9 and drops 8 pt toward the menu while it fades.

```css
--spring-pop: linear(0, 0.039, 0.134, 0.258, 0.393, 0.524, 0.644, 0.748, 0.833, 0.901, 0.952, 0.989, 1.013, 1.028, 1.036, 1.038, 1.037, 1.034, 1.029, 1.024, 1.019, 1.014, 1.010, 1.007, 1.004, 1.002, 1.001, 1.000, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 1);
```

```css
/* Row 8: every popover menu (lib/motion.ts POP) inflates out of its trigger like Linear's: scale 0.4 -> 1 on
   --spring-pop (560 ms: Linear's 450 stretched 25% at the user's ask, ~2% overshoot), fading in over 190 ms with its content scaled along (no blur: a filter on a big
   shadowed card drops frames on the iPhone); out in 150 ms back into the trigger. Header menus (POP_OVER) open over their
   pill and grow from the CENTRE of the button that opened them, inside out. */
.af-pop {
  transform-origin: var(--radix-popover-content-transform-origin);
}
.af-pop.af-pop-over {
  transform-origin: calc(100% - var(--radix-popover-trigger-width) / 2) calc(var(--radix-popover-trigger-height) / 2);
}
.af-pop[data-state="open"] {
  animation: af-pop-scale 560ms var(--spring-pop) both, af-pop-fade 190ms var(--ease-out) both;
}
.af-pop[data-state="closed"] {
  animation: af-pop-out var(--dur-fast) var(--ease-out) both;
}
@keyframes af-pop-scale { from { scale: 0.4; } }
@keyframes af-pop-fade { from { opacity: 0; } }
@keyframes af-pop-out { to { opacity: 0; scale: 0.5; } }
```

```tsx
// Radix: every header menu
<Popover.Content align="end" sideOffset={-44} className={`... ${POP_OVER}`}>   // POP_OVER = "af-pop af-pop-over"
// a trigger that is not the last one in its pill (the + next to the ...): cover the whole pill, grow from its own centre
<Popover.Content align="end" sideOffset={-44} alignOffset={-44} style={{ transformOrigin: "calc(100% - 66px) 22px" }} ...>
```

Wrong turns (each cost a round with the user): menu 8 pt BELOW the button (Linear covers it); grown from the menu's
corner (Linear: from the button's centre); an 8 px blur fading in (felt slow on the iPhone: a filter on a big shadowed
card is expensive there); first spring overshot only 1% (Linear ~2.4%).

#### 3. The slingshot: the icon coming back when the menu closes (delight, but tied to a real state change)

Spotted by the user, then measured on two closes: 130 ms after the menu starts closing the icon comes back from where
the menu shrank into (8 pt left, 3 pt down, 0.7, invisible), flies up-right **past** the centre (6.7 pt above at
83 ms) and sinks back to rest by 450 ms. Keyframes are the measured points, `linear` between them; one
`MutationObserver` on `data-state` plays them on open -> closed only (never on page load); `fill: backwards` keeps the
icon hidden during the delay so it never flashes in place first. Reduced motion: a 150 ms fade.

```ts
// MOTION.md row 8b: a header menu's icon comes back like a slingshot when its menu closes (Linear, native frames
// 2026-10-14): from where the menu shrank into (8 pt left, 3 pt down, 0.7, invisible) it flies up and right past the
// centre (6.7 pt above at 83 ms) and sinks back to rest by 450 ms. Keyframes sampled from the recording, linear
// between them. Starts 130 ms after the close, once the menu is gone.
const SLINGSHOT: Keyframe[] = [
  { offset: 0, translate: "-8px 3px", scale: "0.7", opacity: 0 },
  { offset: 0.044, translate: "-6px -2.6px", scale: "0.83", opacity: 0.75 },
  { offset: 0.111, translate: "-3.5px -5.9px", scale: "0.94", opacity: 1 },
  { offset: 0.184, translate: "-1.9px -6.7px", scale: "0.98", opacity: 1 },
  { offset: 0.26, translate: "-0.9px -6.1px", scale: "1", opacity: 1 },
  { offset: 0.333, translate: "0px -4.6px", scale: "1", opacity: 1 },
  { offset: 0.444, translate: "0px -3px", scale: "1", opacity: 1 },
  { offset: 0.556, translate: "0px -2px", scale: "1", opacity: 1 },
  { offset: 0.667, translate: "0px -0.9px", scale: "1", opacity: 1 },
  { offset: 0.833, translate: "0px -0.4px", scale: "1", opacity: 1 },
  { offset: 1, translate: "0px 0px", scale: "1", opacity: 1 },
];

// One observer for every header menu trigger (Radix flips data-state on the trigger): open -> closed plays the
// slingshot. The backwards fill keeps the icon hidden during the delay, so it never flashes back in place first.
export function watchMenuIcons() {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  new MutationObserver((records) => {
    for (const r of records) {
      const el = r.target as HTMLElement;
      if (r.oldValue !== "open" || el.dataset.state !== "closed" || !el.closest("header")) continue;
      const icon = el.querySelector(":scope > svg");
      if (!icon) continue;
      icon.animate(reduce.matches ? [{ opacity: 0 }, { opacity: 1 }] : SLINGSHOT, { duration: reduce.matches ? 150 : 450, delay: 130, easing: "linear", fill: "backwards" });
    }
  }).observe(document.body, { subtree: true, attributes: true, attributeFilter: ["data-state"], attributeOldValue: true });
}
```
(Call `watchMenuIcons()` once in `main.tsx`.)

#### 4. Sheets: faster (spatial)

Linear's New issue sheet: up in 250 ms (64% of the way at 100 ms, 97% at 200 ms: exactly `--ease-drawer`), down in
200 ms. Ours was 400 / 400. The dock and bottom bars step aside while a sheet is open and pop back as it leaves.

```css
/* Row 6: vaul sheets, timed on Linear's New issue sheet (2026-10-14): up in 250 ms, down in 200 ms, --ease-drawer
   (its measured path: 64% of the way at 100 ms, 97% at 200 ms). */
[data-vaul-drawer][data-state="open"],
[data-vaul-overlay][data-state="open"] {
  animation-duration: 250ms !important;
  animation-timing-function: var(--ease-drawer) !important;
}
[data-vaul-drawer][data-state="closed"],
[data-vaul-overlay][data-state="closed"] {
  animation-duration: 200ms !important;
  animation-timing-function: var(--ease-drawer) !important;
}

/* Row 6b: the dock and the bottom bars step out of the way while a sheet is open (150 ms fade + 0.92), and pop back
   once it has nearly left (200 ms, 120 ms late). */
nav[aria-label="Dock"],
button[aria-label="Ask your board"].fixed,
[data-bottom-bar] {
  transition-property: opacity, scale;
  transition-duration: 200ms;
  transition-timing-function: var(--ease-out);
  transition-delay: 120ms;
}
html:has([data-vaul-drawer][data-state="open"]) :is(nav[aria-label="Dock"], button[aria-label="Ask your board"].fixed, [data-bottom-bar]) {
  opacity: 0;
  scale: 0.92;
  transition-duration: var(--dur-fast);
  transition-delay: 0ms;
}
```

#### 5. The dock morphs into a page's bottom bar (spatial)

Opening a task: the dock does not vanish; its capsule shrinks into the task bar's first round button, the Ask button
becomes the task's Ask button, the Comment capsule grows out of it, all through a 6 px blur cross-fade, 280 ms. Done
with shared `view-transition-name`s (`dock`, `ask-button`, `dock-grow`) on the page bar's buttons.

```css
/* Row 4b: the dock morphs into a task's bottom bar (Linear, 2026-10-14): the task bar's first round button and its
   agent button carry the same names, so the capsule shrinks into the button while the two cross-fade through a 6 px
   blur, and the Comment capsule grows out of it. 280 ms, --ease-in-out (an on-screen morph). Back = the reverse. */
::view-transition-group(dock),
::view-transition-group(ask-button),
::view-transition-group(dock-grow) {
  animation-duration: 280ms;
  animation-timing-function: var(--ease-in-out);
}
::view-transition-image-pair(dock) {
  overflow: clip;
  border-radius: 9999px;
}
::view-transition-old(dock),
::view-transition-new(dock) {
  height: 100%;
  width: auto;
  object-fit: none;
  object-position: left center;
}
::view-transition-old(dock),
::view-transition-old(ask-button),
::view-transition-old(dock-grow) {
  animation: af-blur-out 280ms var(--ease-in-out) both;
}
::view-transition-new(dock),
::view-transition-new(ask-button) {
  animation: af-blur-in 280ms var(--ease-in-out) both;
}
::view-transition-new(dock-grow) {
  transform-origin: left center;
  animation: af-grow-in 280ms var(--ease-out) both;
}
@keyframes af-blur-out { to { opacity: 0; filter: blur(6px); } }
@keyframes af-blur-in { from { opacity: 0; filter: blur(6px); } }
@keyframes af-grow-in { from { opacity: 0; scale: 0.6 1; filter: blur(6px); } }
```

**Trap:** a page that renders nothing until its data arrives gives the view transition a blank snapshot: no bar to
morph into, and an empty screen slides in. Fetch in the route loader so the push commits with data:
`loader: ({ params }) => queryClient.ensureQueryData(taskQuery(Number(params.taskId))).catch(() => undefined),`

#### 6. New header buttons slide in like a slingshot (spatial)

Asked by the user (2026-10-14), no Linear recording of it: when a screen's header buttons are not the same as the last
screen's (another number, or other buttons), the new right-hand group comes in from just beyond the window's right
edge on a spring that overshoots ~6% past its place (6-9 px on a Board / Needs you trip) and settles by ~450 ms; it
fades in over 150 ms. Same buttons (Board -> Board) or the first screen: nothing. Works on every screen with no
per-screen code: one `MutationObserver` watches for a new `<header>`, takes its last child when it sits on the right
half, compares the buttons' `aria-label`s with the previous header's (a header with no buttons on the right counts as
"none", so coming back from Settings animates). Reduced motion: a 150 ms fade. Headless-measured; phone feel owed.
**Bit us (same day):** started inside the view transition's DOM update (the observer fires there), the off-screen
start made Chrome abort EVERY screen push / pop ("Transition was aborted because of invalid state"): screens switched
abruptly and the dock seemed to vanish (user, Android + Chrome). Fix: start it one `requestAnimationFrame` later,
hidden until then. Found by bisecting commits on the dev server with a page-error listener. Also: a Playwright
sampler run with `evaluate_handle` + a later `tap()` queues the tap behind the sampling promise; start sampling from
an in-page `pointerdown` listener instead.
**Bit us twice (same evening; fix confirmed by the user on the phone: "perfect"):** the off-screen start also made the PAGE wider than the screen for the length of the
slide; mobile browsers then grow the layout viewport to fit (Pixel 7: 412 -> 544 pt wide, 839 -> 1108 tall) and every
fixed bar drops with it: the dock vanished below the screen for ~0.5 s after Search -> back and on other screen
changes (user, Android + Chrome). DOM checks said the dock was there and opaque; only per-frame paint (a CDP
screencast) and the dock's `getBoundingClientRect().top` (763 -> 1032) showed it. Fix: `header { overflow-x: clip }`
(vertical stays visible for the press lens). Rule: anything that animates in from off-screen must sit inside an
`overflow-x: clip` box, or a phone will zoom the whole layout out.

```ts
// MOTION.md row 4c: when a screen's header buttons differ from the last screen's (another number or other buttons),
// the new right-hand group comes in from beyond the window's right edge like a slingshot: past its place (~6%, 8 px
// on a typical trip) on a spring, settled at 520 ms (user, 2026-10-14: "como un tirachinas"). Same buttons, or the
// first screen: no motion.
// One observer for every screen's <header>; the group = the header's last child when it sits on the right half.
// Spring sampled into linear(): damping 0.66, 21 rad/s, 520 ms, peak 1.063 at ~200 ms.
const HEADER_SPRING =
  "linear(0, 0.040, 0.139, 0.270, 0.413, 0.553, 0.680, 0.790, 0.879, 0.948, 0.998, 1.031, 1.052, 1.061, 1.063, 1.060, 1.053, 1.044, 1.035, 1.026, 1.019, 1.012, 1.007, 1.003, 1.000, 0.998, 0.997, 0.996, 0.996, 0.996, 0.997, 0.997, 0.998, 0.998, 0.999, 0.999, 1)";
let lastActions: string | null = null;
export function watchHeaderActions() {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const check = (header: Element) => {
    const group = header.lastElementChild as HTMLElement | null;
    const r = group?.getBoundingClientRect();
    // No buttons on the right (a title, only Back) is a state too: the next screen with buttons differs from it.
    if (!group || !r || header.childElementCount < 2 || r.left < innerWidth / 2 || !(group.matches("button, a") || group.querySelector("button, a"))) {
      lastActions = "";
      return;
    }
    const sig = Array.from(group.matches("button, a") ? [group] : group.querySelectorAll("button, a"))
      .map((b) => b.getAttribute("aria-label") ?? b.textContent?.trim())
      .join("|");
    const changed = lastActions !== null && sig !== lastActions;
    lastActions = sig;
    if (!changed) return;
    if (reduce.matches) return void group.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 150, easing: "ease" });
    // The full width to the window's edge, on a spring that overshoots ~6% (8 px on a 130 px trip) and settles.
    // Started a frame later: begun inside a view transition's DOM update, the off-screen start aborted every screen
    // push / pop in Chrome ("Transition was aborted because of invalid state"). Hidden until then.
    group.style.opacity = "0";
    requestAnimationFrame(() => {
      group.style.opacity = "";
      group.animate([{ translate: `${innerWidth - r.left}px 0` }, { translate: "0px 0" }], { duration: 520, easing: HEADER_SPRING });
      group.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 150, easing: "cubic-bezier(0.23, 1, 0.32, 1)" });
    });
  };
  new MutationObserver((records) => {
    for (const r of records)
      for (const n of Array.from(r.addedNodes)) {
        if (!(n instanceof Element)) continue;
        const h = n.matches("header") ? n : n.querySelector("header");
        if (h) check(h);
      }
  }).observe(document.body, { subtree: true, childList: true });
}
```
(Call `watchHeaderActions()` once in `main.tsx`.)

The guard that keeps the slide from widening the page (section 5b):

```css
/* Row 4c guard: a header never widens the page. Its buttons slide in from off-screen (lib/motion.ts watchHeaderActions);
   without the clip that overflow makes mobile browsers grow the layout viewport (412 -> 544 pt wide, 839 -> 1108 tall
   on a Pixel 7) and every fixed bar, the dock first, drops off the bottom of the screen until the slide ends (user,
   Android + Chrome, 2026-10-14). Vertical overflow stays visible: the press lens sticks out below the pill. */
header {
  overflow-x: clip;
}
```

#### 7. Into Search and back: the dock morphs into Search's bar (spatial)

Asked by the user (2026-10-14): Search had no transition at all (same level as the Board). Now it moves like iOS 26's
search tab: the dock shrinks into Search's Back button (it takes the dock's place, bottom-left), the search field grows
out of it, the chat button blurs away, and the page behind cross-fades in 200 ms. Back = the reverse. Same named groups
as section 5 (`dock` on Back, `dock-grow` on the field): 280 ms `--ease-in-out`, 6 px blur cross-fade. A router type
gives these same-level moves a transition at all:

```ts
// lib/motion.ts pushType: into Search and back out at the same level
if (a === b && (from === "/search" || to === "/search")) return ["search"];
```

```css
html:active-view-transition-type(search)::view-transition-group(root),
html:active-view-transition-type(search)::view-transition-old(root),
html:active-view-transition-type(search)::view-transition-new(root) {
  animation-duration: var(--dur-base);
  animation-timing-function: var(--ease-out);
}
```

Headless-checked (no aborts, the dock back in place after); phone feel owed.

#### 8. The dock BECOMES its menu (spatial; copied from a Linear recording)

The user asked for "only 1 menu, not 2", then sent a recording of Linear's iOS app; measured on native frames
(1 px = 1 pt): the dock (56 pt tall) turns into the menu (428 pt tall), same width, its bottom fixed on the dock's
bottom, and the dock's own buttons are gone while it is open.

| phase | Linear (from release) | ours (from tap, headless) |
|---|---|---|
| pull back | 0-70 ms: the dock squeezes (305 -> 270 wide, a bit lower), its icons blur | 0-65 ms: icons blur and fade (0.4), the dock squeezes to 90% x 94% |
| shoot up | 63% of the height at 100 ms, 84% at 134, 101% at 200 | 81% at 149 ms, 102% at 216 |
| overshoot | peak 105% (450 of 428) at 284 ms | peak 105% at 287 ms |
| settle | at rest by ~550 ms | at rest by 540 ms |
| content | arrives blurred, sharpens | blur 6 px -> 0 and fades in, 70-270 ms |
| close | back into the dock in ~230 ms, sagging up to 28 pt below the dock's line | 240 ms, sags 16 pt, content blurs out first, the panel fades off over the dock in the last quarter |

How: the menu is a Radix popover anchored to the dock with `sideOffset={-56}` (its bottom on the dock's bottom) and
`w-(--radix-popover-trigger-width)`; it is revealed upward from the dock's 56 pt band with `clip-path`, scaled from its
bottom centre for the squeeze and the overshoot; the real dock hides under it (`visibility`, switched at once both ways:
an opacity fade inherited the sheet rule's 120 ms delay and left a moment with neither the menu nor the dock). Closed by
tapping outside it, like Linear. Wrong turns: a separate card above the dock (the user: one menu, not two), then the
dock's buttons kept at the bottom of the menu (the recording: they go away). Phone feel owed.

```css
/* Row 8c: the dock BECOMES its menu (Linear's iOS app, recorded and measured frame by frame 2026-10-14). One surface:
   the menu sits on the dock (same width, same bottom) and the dock hides under it.
   Open, 540 ms: the dock is pulled back like a slingshot (~65 ms: 90% wide, 94% tall), shoots up into the menu
   (revealed from the dock's 56 pt band, clip-path) and overshoots ~5% taller at ~280 ms, then settles; the menu's
   content arrives blurred and sharpens. Close, 240 ms: it sinks back into the dock, sagging up to 16 pt below the
   dock's line, content blurring out first, fading in the last quarter so the dock shows through. */
/* visibility, not opacity: it switches at once both ways (opacity would inherit row 6b's delayed fade and leave a gap
   with neither the menu nor the dock on screen); the closing menu fades off over the dock. */
nav[aria-label="Dock"][data-menu] {
  visibility: hidden;
  transition: visibility 0s linear 70ms; /* the dock's own icons are seen blurring for the first beat */
}
nav[aria-label="Dock"][data-menu] > * {
  filter: blur(4px);
  opacity: 0.4;
  transition: filter 70ms ease-out, opacity 70ms ease-out;
}
.af-dock-grow {
  transform-origin: 50% 100%;
}
.af-dock-grow[data-state="open"] {
  animation: af-dock-grow-in 540ms both;
}
.af-dock-grow[data-state="closed"] {
  animation: af-dock-grow-out 240ms both;
}
.af-dock-grow[data-state="open"] .af-dock-grow-content {
  animation: af-blur-in 200ms cubic-bezier(0.33, 1, 0.68, 1) 70ms both;
}
.af-dock-grow[data-state="closed"] .af-dock-grow-content {
  animation: af-blur-out 120ms cubic-bezier(0.33, 1, 0.68, 1) both;
}
@keyframes af-dock-grow-in {
  0% { clip-path: inset(calc(100% - 56px) 0 0 0 round 28px); scale: 1 1; opacity: 0; animation-timing-function: cubic-bezier(0.33, 1, 0.68, 1); }
  12% { clip-path: inset(calc(100% - 56px) 0 0 0 round 28px); scale: 0.9 0.94; opacity: 1; animation-timing-function: cubic-bezier(0.33, 1, 0.68, 1); }
  52% { clip-path: inset(0 0 0 0 round 28px); scale: 1 1.05; animation-timing-function: cubic-bezier(0.65, 0, 0.35, 1); }
  76% { scale: 1 0.99; animation-timing-function: cubic-bezier(0.33, 1, 0.68, 1); }
  100% { clip-path: inset(0 0 0 0 round 28px); scale: 1 1; }
}
@keyframes af-dock-grow-out {
  0% { clip-path: inset(0 0 0 0 round 28px); translate: 0 0; opacity: 1; animation-timing-function: cubic-bezier(0.33, 1, 0.68, 1); }
  35% { translate: 0 16px; }
  75% { opacity: 1; }
  100% { clip-path: inset(calc(100% - 56px) 0 0 0 round 28px); translate: 0 0; opacity: 0; }
}
```

#### 9. Picker modals: centred, a blurred page behind, fast in, blur out (spatial)

From a second Linear recording (54 s, the user, 2026-10-14), measured on native frames: every property picker
(Priority, Assignee, Labels, Project, Project icon) is ONE card style. No search field: centred on the screen. With a
search field: pinned near the top so it clears the keyboard; the keyboard rises FIRST (~100 ms) and the card comes after;
on close the keyboard drops first. The page behind goes dark AND blurred (not just a scrim). The card is there ~20 ms
after the tap, semi-transparent, blurred and ~3% small, and sharp, opaque and full size by ~90 ms; it leaves in ~150 ms,
fading while it blurs. (The circle on the X in the recording is iOS Show Touches, not Linear's UI: not copied.)

Ours (`components/pickers.tsx` `PickerCard`, all 39 pickers): centred (`top-1/2 translate-y-[-50%]`) unless it is a
search list (pinned top, as before), scrim `bg-scrim/70 backdrop-blur-xl` fading in 120 ms, card in 140 ms / out
150 ms. Measured headless: opacity 0.90 and blur
0.6 px at 80 ms, settled by ~150 ms; closes over ~150 ms. Animate only individual properties (`scale`, `filter`,
`opacity`): a `transform` keyframe would override the centring translate.

**Bit us:** the portal picker passed its scrim and card to `Dialog.Portal` as ONE fragment; Radix's Presence watches
each child for its exit animation and a fragment gave it nothing to watch, so portal pickers vanished at once on close
(their exit animation had never played). Fix: pass them as separate keyed children (an array), not a fragment.

```css
/* Row 6c: picker modals (components/pickers.tsx PickerCard), timed on Linear's (recorded 2026-10-14): the card arrives
   in 140 ms (fade, a 6 px blur clearing, 0.96 -> 1) over a dark, blurred page (the scrim fades in 120 ms) and leaves in
   150 ms (fade + blur out). Individual properties only (scale, filter), so the centring translate is never overridden. */
.af-modal[data-state="open"] { animation: af-modal-in 140ms cubic-bezier(0.23, 1, 0.32, 1) both; }
.af-modal[data-state="closed"] { animation: af-modal-out 150ms cubic-bezier(0.23, 1, 0.32, 1) both; }
.af-modal-scrim[data-state="open"] { animation: af-fade-in 120ms ease-out both; }
.af-modal-scrim[data-state="closed"] { animation: af-fade-out 150ms ease-out both; }
@keyframes af-modal-in { from { opacity: 0; scale: 0.96; filter: blur(6px); } }
@keyframes af-modal-out { to { opacity: 0; scale: 0.98; filter: blur(6px); } }
```

#### 10. Copy unrolls a panel inside its menu; search pickers open ready to type; Linear's picker sizes

From the same recording (2026-10-14). All headless-measured; phone feel owed.

- **Copy: a panel unrolls from the Copy row** (spatial). First try was wrong (the user: "it should be like in the
  video"): I cross-faded the items under Copy into the copy items. Linear, on native frames: the menu itself does not
  change. Copy's arrow turns (› to ⌄, ~120-180 ms); then a slightly lighter rounded panel (its own border and shadow)
  appears ON the Copy row and unrolls DOWN over the items below (~130-250 ms), its first row the Copy header (bold, ⌄),
  then Link / Issue ID / Branch name / Prompt; the old rows show through for a frame or two as it passes. Once it is
  open the rest of the menu dims to ~50% (~280-400 ms). Closing the menu shrinks everything back into the "..." button.
  Ours: the same order (arrow 0-85 ms, panel from ~100 ms, unrolled by ~170 ms, rest dims from ~150 ms over 200 ms);
  tapping the panel's Copy header folds it back up. Built with motion: `height: 52 -> "auto"` (52 = one row), opacity
  in after the arrow starts turning, `AnimatePresence` for the fold back; the panel is placed at the Copy row's
  `offsetTop`, read when Copy is tapped (not during render: the React Compiler).
- **Search pickers open ready to type**: a picker over the page (`portal`) with a search field focuses it on open
  (Radix `onOpenAutoFocus`), like Linear's Assignee / Labels / Project. Not inside a sheet (focusing on open makes a
  sheet jump on iOS) and not the icon picker (`calm`: Linear drops the keyboard for it). Closing with the keyboard up:
  the field lets go first and the card closes 130 ms later (Linear: keyboard down first). On Android the tap focuses
  the button before the close runs, so "was I typing" is read at `pointerdown`. Whether iOS raises the keyboard from
  this focus is the phone check.
- **Sizes measured on Linear's picker**: card 12 pt from the screen edges, title 16 semibold, rows 16 regular on a
  48 pt pitch, text 49-51 pt from the card's edge, X glyph 14 pt. Ours now: same card box (306 vs 305 pt for the
  priority list), same row pitch and first-row position (both 83 pt from the top).

Pickers (`components/pickers.tsx` `PickerCard`): ready to type on open, the keyboard first on close:

```tsx
      // Linear: a picker with a search field opens ready to type (the keyboard comes up with it). Only for pickers over
      // the page (portal): inside a sheet, focusing on open makes the sheet jump (UI-PLAYBOOK, iPhone fixes).
      onPointerDownCapture={() => (typing.current = document.activeElement instanceof HTMLInputElement && !!document.activeElement.closest(".af-modal"))}
      onOpenAutoFocus={(e) => {
        const input = top && portal && !calm ? (e.currentTarget as HTMLElement).querySelector("input") : null;
        if (input) (e.preventDefault(), input.focus({ preventScroll: true }));
      }}
    // Linear: with the keyboard up, it drops FIRST and the card closes ~130 ms later (recorded 2026-10-14).
    <Dialog.Root
      open={open}
      onOpenChange={(o) => {
        if (o) return;
        const field = document.activeElement instanceof HTMLInputElement && document.activeElement.closest(".af-modal") ? document.activeElement : null;
        if (!field && !typing.current) return onClose();
        typing.current = false;
        field?.blur();
        (document.activeElement as HTMLElement | null)?.blur();
        setTimeout(onClose, 130);
      }}
```

The Copy panel (`screens/task/Task.tsx` `Actions`):

```tsx
          {/* Linear (recorded 2026-10-14): the menu stays; Copy's arrow turns, then a panel unrolls DOWN from the Copy row,
              over the items below it, its first row the Copy header (tap it to fold the panel back). Once it is open,
              the rest of the menu dims. */}
          <div className={`transition-opacity duration-200 ${copyMenu ? "opacity-50 delay-150" : ""}`} inert={copyMenu || undefined}>
            <MenuItem
              icon={<Star size={20} strokeWidth={2} className={task.favorite ? "fill-current" : ""} />}
              close
              onClick={() => void onPatch({ favorite: !task.favorite })}
            >
              {task.favorite ? "Unfavorite" : "Favorite"}
            </MenuItem>
            <Sep />
            <MenuItem icon={icon(Share)} close onClick={() => void share()}>
              Share
            </MenuItem>
            <div ref={copyRow}>
              <MenuItem
                icon={icon(Clipboard)}
                right={<ChevronRight size={18} strokeWidth={2} className={`text-text-3 transition-transform duration-[120ms] ease-(--ease-out) ${copyMenu ? "rotate-90" : ""}`} />}
                onClick={() => (setCopyTop(copyRow.current?.offsetTop ?? 0), setCopyMenu(true))}
              >
                Copy
              </MenuItem>
            </div>
              <Sep />
            <MenuItem
              icon={icon(Clock)}
              right={task.reminderAt && <span className="text-[13px] text-text-4">{when(new Date(task.reminderAt))}</span>}
              close
              onClick={onRemind}
            >
              Remind me
            </MenuItem>
            <MenuItem icon={icon(Pencil)} close onClick={onEdit}>
              Edit task
            </MenuItem>
            <MenuItem icon={icon(CalendarDays)} right={task.dueAt && <span className="text-[13px] text-text-4">{dueText(new Date(task.dueAt))}</span>} close onClick={onDue}>
              Due date
            </MenuItem>
            <MenuItem icon={icon(Copy)} close onClick={() => void makeCopy()}>
              Make a copy
            </MenuItem>
            <MenuItem icon={icon(History)} close onClick={onHistory}>
              Description history
            </MenuItem>
            <MenuItem icon={icon(Link2)} close onClick={onRelation}>
              Add link or relation...
            </MenuItem>
            <Sep />
            {task.stage !== "canceled" && (
              <MenuItem icon={icon(CircleX)} close onClick={() => void cancelTask()}>
                Cancel task
              </MenuItem>
            )}
            <MenuItem icon={icon(Trash2)} danger close onClick={() => void remove()}>
              Delete task
            </MenuItem>
          </div>
          <AnimatePresence>
            {copyMenu && (
              <motion.div
                key="copy"
                className="absolute inset-x-2 z-10 overflow-hidden rounded-[18px] border border-surface-4 bg-surface-3 shadow-[0_16px_40px_rgba(0,0,0,0.55)]"
                style={{ top: copyTop }}
                initial={{ height: 52, opacity: 0 }}
                animate={{
                  height: "auto",
                  opacity: 1,
                  transition: { height: { duration: 0.16, delay: 0.08, ease: [0.23, 1, 0.32, 1] }, opacity: { duration: 0.08, delay: 0.06 } },
                }}
                exit={{ height: 52, opacity: 0, transition: { duration: 0.14, ease: [0.23, 1, 0.32, 1] } }}
              >
                <button type="button" onClick={() => setCopyMenu(false)} className="flex h-[52px] w-full items-center gap-3.5 rounded-[14px] px-3.5 text-left text-[17px] font-semibold">
                  <span className="flex size-5 items-center justify-center">{icon(Clipboard)}</span>
                  <span className="grow">Copy</span>
                  <ChevronDown size={18} strokeWidth={2} className="text-text-3" />
                </button>
            <MenuItem icon={icon(Link2)} close onClick={() => void copy(link, "Link")}>
              Link
            </MenuItem>
            <MenuItem icon={icon(FileText)} close onClick={() => void copy(task.key, "Task ID")}>
              Task ID
            </MenuItem>
            {task.branch && (
              <MenuItem icon={icon(GitBranch)} close onClick={() => void copy(task.branch!, "Branch name")}>
                Branch name
              </MenuItem>
            )}
            <MenuItem icon={icon(MessageSquare)} close onClick={() => void copy(asPrompt(task), "Prompt")}>
              Prompt
            </MenuItem>
            {d.lastSession && (
              <MenuItem icon={icon(SquareTerminal)} close onClick={() => void copy(resumeCommand(d.lastSession!), "Resume command")}>
                Resume command
              </MenuItem>
            )}
              </motion.div>
            )}
          </AnimatePresence>
```

#### 11. Rows light up instead of shrinking, the dock's places cross-fade (feedback, spatial)

Second pass over the 54 s recording (the user: "review the video again"), native frames:

- **Removed: a press circle on tabs and dock buttons.** I first read the grey circle on "Priority" / "Other" and on the
  dock as Linear's press feedback and copied it; it is iOS Show Touches (section 1). Tabs and dock places keep the
  app's normal press (0.97).
- **List rows light up instead of shrinking**: the pressed row's background goes #0F0F0F -> #1C1C1C over the whole row
  (52 pt), no scale. This settles the D120 question ("is a 0.97 shrink on every row too much?"): yes, Linear lights
  rows. Ours: `data-row` on the Board, Needs you, Triage, Repos and Search rows -> `surface-2`, no scale.
- **Switching between the dock's places cross-fades** (~100 ms; both titles overlap for a frame or two). Ours: a new
  view-transition type `switch` for any move between two top-level places (`pushType`), the page cross-fades in
  120 ms and the dock stands still (its pill slides in the live page).
- Already matching, measured: opening an item (~300 ms slide, long settle) and going back (~200 ms; ours 250 ms), the
  tab pill sliding, Edit project and New issue sheets (~250 ms).
- Not copied on purpose: Linear keeps the dock on an opened Inbox item with an action bar above it; ours gives pushed
  pages their own bottom bar (D79). Say if you want the dock there.

```css
/* Row 1c: list rows light up on press instead of shrinking (Linear, recorded 2026-10-14: the pressed row's background
   goes #0F0F0F -> #1C1C1C, full row, no scale). Mark a row with data-row. */
[data-row] {
  border-radius: 14px;
}
[data-row]:active {
  scale: none !important; /* no shrink: Linear lights the row instead (row 1 would otherwise win) */
  background-color: var(--color-surface-2);
  transition-duration: 60ms;
}
```

```css
/* Row 4e: switching between the dock's places: the page cross-fades in 120 ms (Linear: ~100 ms, both titles overlap
   briefly); the dock and its button stand still (their pill slides in the live page). */
html:active-view-transition-type(switch)::view-transition-group(root),
html:active-view-transition-type(switch)::view-transition-old(root),
html:active-view-transition-type(switch)::view-transition-new(root) {
  animation-duration: 120ms;
  animation-timing-function: var(--ease-out);
}
html:active-view-transition-type(switch)::view-transition-group(dock),
html:active-view-transition-type(switch)::view-transition-group(ask-button),
html:active-view-transition-type(switch)::view-transition-new(dock),
html:active-view-transition-type(switch)::view-transition-new(ask-button) {
  animation: none;
}
html:active-view-transition-type(switch)::view-transition-old(dock),
html:active-view-transition-type(switch)::view-transition-old(ask-button) {
  animation: none;
  opacity: 0;
}
```

#### 12. The @ card's scroll indicator (state indication)

From a third Linear recording (the agent chat, 2026-10-14; the user: "look at the scrollbar, the sizing of the
scrollbar when doing the @"). Linear's @ card (about 170 pt tall with the keyboard up) shows a thin indicator the whole
time the list is longer than the card: 3 pt wide, 6 pt in from the card's right edge, its thumb as long as the visible
share of the list (measured 62 pt), moving as the list scrolls. On the web the iPhone only shows its own bar WHILE
scrolling, hugging the very edge, so ours drew nothing at rest. Ours now: the native bar hidden
(`[scrollbar-width:none] [&::-webkit-scrollbar]:hidden`) and our own 3 pt bar (`bg-text-4/70`), 6 pt from the right,
10 pt from the top and bottom, length = track x visible / total (min 24 pt), position from `scrollTop`, recomputed in
the same handler that drives the bottom fade (`components/MentionInput.tsx` `checkMore`). Headless: 215 of 280 pt with
the card 300 pt tall, moving from 10 to 75 pt as the list scrolls to its end. Phone look owed.

#### 13. The agent chat (from the third recording)

Linear's agent chat, measured on native frames (2026-10-14), and what ours does now (`screens/agent/BoardAgent.tsx`):

- **Opens ready to type.** Linear's chat sheet slides up (~300 ms), then the keyboard rises by itself with the box
  focused. The iPhone only raises the keyboard for a focus made inside a tap, so the dock's chat button primes it:
  `primeKeyboard()` focuses a hidden field during the tap, and the chat's box takes the focus over when it mounts (the
  keyboard stays). Headless: the box is focused on open; whether the keyboard comes up is the phone check.
- **History is a sheet**, not a menu: it slides up over the dimmed chat (the keyboard drops first), chats grouped
  Today / Yesterday / Earlier with their age ("3m", "6h"); picking one slides it away and the picked chat opens ready
  to type. Once a chat exists the header has history and a "+" (new chat) together in one glass pill. The history sheet
  starts 10 pt below the chat sheet's top, so it COVERS the header and the button that opened it (the user: "the
  history should cover the button that presses it"), and the chat stays behind as a slightly smaller card (iOS stacked
  sheets: vaul `Drawer.NestedRoot`, the chat at 0.96). "Today" carries a hairline to the right, like Linear's.
  **Bit us:** closing the nested sheet from React state never told the chat sheet, which then stayed shrunk at 0.96 for
  good; the rows are vaul `Drawer.Close` buttons (vaul's own close restores the parent) and the chat swaps 260 ms later,
  after the slide. On the full /ask page there is no sheet to nest in, so it is a plain `Drawer.Root` there.
- **Attach menu**: the paperclip opens a small menu that grows out of it (Browse files / Photos), instead of the file
  picker straight away (Linear: Browse files / Photos & Videos; our uploads take images, not videos).
- **Thinking**: "Thinking..." with a bright band sweeping across the grey letters, about once a second (Linear's
  shimmer; ours a background-clip gradient, reduced motion = plain grey), then "Worked for Ns" above the reply.
- **Sent message**: a full-width pill at the top of its turn (Linear), not a bubble on the right.
- **Fourth recording (2026-10-14, the user's 68 s video of Linear's agent): what was still different, now built.**
  A named chat's title sits on the LEFT next to the X ("New chat" stays centred). While it answers, the empty box's
  button is a **Stop** square (`Square` filled, surface-4); typed text **queues** instead (a dimmed pill with "Queued ·
  Edit · Delete" under the reply in progress, answered as soon as it lands: Claude Code's behaviour, the closest a
  one-call agent can get to steering). The live line names the REAL phases (measured: `opencode run --format json`
  sends one `step_start` ~3-6 s after launch and then the whole reply as ONE text event, so nothing streams word by
  word): "Starting the agent..." then "Reading the board...". After it, "Worked for Ns ›" opens what the answer was
  made from (the board's counts, the tasks it looked at, repo, skill, files, tokens and model) in a thin left-ruled
  list, like Linear's expandable steps. Not copied: Linear's starters send at once and the agent asks back (a model
  call just to ask a question; ours fill the box).

```css
/* Row 16b: "Thinking..." while the agent works (Linear, recorded 2026-10-14): a bright band sweeps across the grey
   letters, left to right, about once a second. Reduced motion: plain grey text. */
.af-shimmer {
  background: linear-gradient(90deg, var(--color-text-4) 0%, var(--color-text-4) 40%, var(--color-text) 50%, var(--color-text-4) 60%, var(--color-text-4) 100%);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: af-shimmer 1.1s linear infinite;
}
@keyframes af-shimmer {
  from { background-position: 100% 0; }
  to { background-position: 0% 0; }
}
@media (prefers-reduced-motion: reduce) {
  .af-shimmer { animation: none; background: none; color: var(--color-text-4); }
}
```

```ts
// The iPhone raises the keyboard only for a focus made INSIDE a tap. A screen that opens with its field ready to type
// (Linear's agent chat, 2026-10-14) calls this in the tap's handler: a hidden field takes the focus at once (keyboard up),
// and the real field takes it over when it appears (the keyboard stays). If nothing takes it over, it lets go after 1.2 s.
export function primeKeyboard() {
  if (!matchMedia("(pointer: coarse)").matches) return;
  let el = document.getElementById("af-kb-proxy") as HTMLInputElement | null;
  if (!el) {
    el = document.createElement("input");
    el.id = "af-kb-proxy";
    el.setAttribute("aria-hidden", "true");
    el.tabIndex = -1;
    Object.assign(el.style, { position: "fixed", top: "0", left: "0", width: "1px", height: "1px", opacity: "0", fontSize: "16px", pointerEvents: "none" });
    document.body.appendChild(el);
  }
  el.focus({ preventScroll: true });
  setTimeout(() => document.activeElement === el && el.blur(), 1200);
}
```

#### 14. The same look on every other screen (the user, 2026-10-14)

"Having in mind the liquid glass, the sharper text, the animations: would you change other screens?" Yes: the rules
measured on Linear today, applied to Triage, Loops, Templates, the pipeline editor, Design, the Settings pages, the
repo sub-pages and Sessions (26 files, 4 agents in parallel on separate files, one shared kit first):

- **One header for every opened page**: `PageHeader` (44 pt glass back button left, actions right) and the title in the
  page with `PageTitle` (24 px bold, a small context line above, e.g. the repo key "SHELF", an optional grey line
  below). Before: some pages had a 17 px title in the bar, some a big one below, one a centred title. The design canvas
  keeps its floating header (a canvas has no scrolling page), with the shared back button and 17 px title.
- **Triage like Needs you**: Linear inbox rows (40 pt round icon, title 17 semibold, one grey "source · age" line), the
  count a plain grey number (no orange badge), the item page with a 24 px title and plain glass buttons.
- **Flat chips everywhere** (`CHIP` / `CHIP_READONLY`): white = tappable, grey = read-only (triage suggestions, the
  pipeline editor's agent and model chips, TickTick tags, prompt variables).
- **Sharper lists**: 20 pt icons without boxes, names 17 medium, one 15 px grey line, `data-row` (lights up on press);
  section labels 14 semibold text-5 everywhere (the shared `Section` too); step cards on `glass-card`.
- Not restyled: the top-level Settings and Usage pages (already 24 px titles and grouped cards). A `data-row` gets a
  14 px radius, so rows with a divider carry the divider on a wrapper.
- **Second round (2026-10-14): the task sub-pages and the Needs you decision screens** (PLAN.md, Shipped, Checkpoints,
  Review, Live preview, Step finished / stopped, Bar check, Compare attempts, the paused and ship screens, the Needs you
  item). Same `PageHeader` / `PageTitle`: the old 17 px title in the bar becomes the 24 px title, the "KEY · agent" line
  its context above, and an intro paragraph its grey `sub` line below. The page's own actions (PLAN.md's chat and
  history buttons, the Needs you item's "1 of N waiting") go in the header's `actions`. Section labels 14 semibold
  text-5. **The first card needs `pt-3` on the `main`** below a `PageTitle` (its `mb-1` alone left the card touching
  the title). Kept as they were: the UI check viewer and the design canvas (floating viewer headers), the Live
  preview's URL pill (only its back button is the shared one).
- **A settings screen used often becomes a place** (Templates, user, 2026-10-14): the page moves under the docked
  routes at a top-level path (`/templates`), gets a place's header (24 px title, a grey line, no back button) and the
  dock; Settings keeps a row that opens the same page. Kept out of the menu on purpose: set-up screens opened now and
  then (Prompts, Agents, Limits, Labels), two taps away through the menu's gear.
- **Edit a related setting from inside an unsaved editor = a sheet, not a page** (the Prompt row on a pipeline step,
  2026-10-14): the pipeline editor keeps its edits in component state until Save, so navigating to Settings > Prompt
  templates would unmount it and lose them. The prompt editor is one shared component (`PromptEditor`) used by the
  Settings page and the sheet. Chips in a sheet step up one grey (`bg-surface-3`): `CHIP` is surface-2, the sheet too.
- Two small fixes with it: Sessions rows keep the age visible (it has its own `shrink-0` span; the status line
  truncates before it), and the prompt-variable chips are `font-medium` (mono at 14 px semibold read heavy):
  `cn(CHIP, "font-mono font-medium")`, tailwind-merge drops CHIP's `font-semibold` (two font weights in one class
  string are decided by CSS order, not class order).

```tsx
import type { ReactNode } from "react";
import { ChevronLeft } from "lucide-react";

// One header and one title for every opened page (UI-PLAYBOOK "List page and detail page like Linear"; the task and
// repo pages were first): a 44 pt glass back button on the left, an optional actions pill on the right, and the page's
// title below in the content (24 px bold) with a small context line above it.
export function BackButton({ onClick, label = "Back" }: { onClick(): void; label?: string }) {
  return (
    <button type="button" aria-label={label} onClick={onClick} className="flex size-11 shrink-0 items-center justify-center rounded-full glass text-text">
      <ChevronLeft size={20} strokeWidth={2} />
    </button>
  );
}

export function PageHeader({ onBack, backLabel, actions }: { onBack(): void; backLabel?: string; actions?: ReactNode }) {
  return (
    <header className="flex items-center justify-between gap-2 px-4 pt-(--top-space)">
      <BackButton onClick={onBack} label={backLabel} />
      {actions}
    </header>
  );
}

export function PageTitle({ context, icon, sub, children }: { context?: ReactNode; icon?: ReactNode; sub?: ReactNode; children: ReactNode }) {
  return (
    <div className="mt-1.5 mb-1 flex flex-col gap-1 px-5">
      {context && <span className="truncate text-[13px] font-medium text-text-4">{context}</span>}
      <h1 className="flex items-center gap-2 text-[24px] leading-[1.2] font-bold tracking-[-0.01em]">
        {icon}
        <span className="min-w-0">{children}</span>
      </h1>
      {sub && <p className="text-[15px] leading-[1.4] text-text-3">{sub}</p>}
    </div>
  );
}
```

```ts
// Shared class strings for the Linear look (UI-PLAYBOOK section 4, measured 2026-10-14).
// Chips: flat surface-2, 29 pt tall, 14 px semibold, 14 pt icon, 8 pt gaps. White text = you can tap it; grey = read-only.
export const CHIP = "inline-flex h-[29px] shrink-0 items-center gap-1.5 rounded-full bg-surface-2 pr-3 pl-2.5 text-[14px] font-semibold text-text";
export const CHIP_READONLY = "inline-flex h-[29px] shrink-0 items-center gap-1.5 rounded-full bg-surface-2 pr-3 pl-2.5 text-[14px] font-semibold text-text-4";
// List rows: icon 20 pt (no box), name 17 medium, one 15 px grey line; `data-row` lights the row up on press (styles.css).
export const ROW_TITLE = "truncate text-[17px] font-medium";
export const ROW_SUB = "truncate text-[15px] text-text-3";
// Section label above a group: 14 px semibold, the muted grey.
export const SECTION = "px-5 pb-1.5 text-[14px] font-semibold text-text-5";
```

### Lists

**Row leaves** (tens/day, spatial): fades and slides 8% left in 150 ms, then the gap collapses (height, 250 ms
`--ease-in-out`, the one tolerated height animation). **Row arrives**: a highlight overlay fades out, linear 1.2 s.
**Row moves group** (e.g. a task changes stage): glides to its new place (layout / FLIP, `layoutId`). All three in one
wrapper, `components/ListRow.tsx`, inside `<AnimatePresence initial={false}>`:

```tsx
<motion.div layout={id ? "position" : true} layoutId={id}
  transition={{ layout: { duration: 0.25, ease: [0.77, 0, 0.175, 1] } }}
  exit={{ opacity: 0, x: "-8%", height: 0, transition: { opacity: { duration: 0.15 }, x: { duration: 0.15 },
    height: { delay: 0.15, duration: reduce ? 0 : 0.25, ease: [0.77, 0, 0.175, 1] } } }}>
  {children}
  <motion.span aria-hidden initial={{ opacity: 1 }} animate={{ opacity: 0 }} transition={{ duration: 1.2, ease: "linear" }}
    className="pointer-events-none absolute inset-0 bg-divider mix-blend-lighten" />
</motion.div>
```

Rows paint their own opaque backgrounds, so the arrival highlight is an overlay in `lighten` blend. Key the
`AnimatePresence` by the tab so switching tabs swaps the list without leave / arrive animations.

**Swipe a row** (tens/day, direct manipulation): follows the finger 1:1, the action colour shows behind, past 40% the
icon pops (`scale(1.1)`) to signal commit; release springs home (`duration 0.4, bounce 0.15`) or slides off then
collapses. Reduced: snap. **Drag to reorder**: **@dnd-kit**; the held card lifts (`scale(1.02)` + shadow), others slide
aside 200 ms, drop springs (`duration 0.35, bounce 0.1`).

**First load of a list**: at most a 40 ms stagger on the first 8 rows. **Routine navigation: no entrance animation.**

### Live work (an agent running)

- **Working dot**: opacity 1 > 0.4 > 1, linear 2 s, CSS keyframes (runs off the main thread, stays smooth while busy).
- **New message block**: fade + 4 px rise, 150 ms; **streamed text chunks append with no animation** (purpose:
  preventing a jarring change, not decoration).
- **Tool steps**: each fades in 120 ms; the running one has a spinner (0.8 s linear); a finished step swaps the
  spinner for a tick with no motion. A helper agent's steps nest under it, indented.
- **Auto-scroll**: smooth, and only when the reader is already at the bottom; their own scroll always wins.
- **Permission request card**: fade + 8 px once. **No looping pulse** (it nags and burns battery).

### Canvas (pan and zoom)

Pan / pinch follows the finger 1:1, momentum on release, rubber band at the limits (library inertia,
`react-zoom-pan-pinch`); zoom buttons and Fit animate 300 ms `--ease-in-out`; selection = outline opacity 100 ms; an
item being generated = dashed outline pulsing 1.5 s linear, then a 300 ms crossfade to the real thing.

### Deliberately NOT animated

Keyboard shortcuts and the palette (100+/day); charts, usage numbers, budget bars (data the user reads); toasts placed
by the design (kept where the frames put them); haptics (not possible from a web app on iOS).

### One reduced-motion switch for the whole app

```css
@media (prefers-reduced-motion: reduce) {
  /* press: opacity instead of scale */
  :is(button, a[href], [role="button"] /* ... */):active { scale: none; opacity: 0.85; }
  /* tw-animate entrances / exits keep their fade, lose scale and slide */
  *, ::before, ::after { --tw-enter-scale: 1 !important; --tw-enter-translate-x: 0 !important; --tw-enter-translate-y: 0 !important;
    --tw-exit-scale: 1 !important; --tw-exit-translate-x: 0 !important; --tw-exit-translate-y: 0 !important; scroll-behavior: auto !important; }
  /* sheets fade instead of rising */
  [data-vaul-drawer][data-state="open"], [data-vaul-overlay][data-state="open"] { animation-name: af-fade-in !important; animation-duration: var(--dur-fast) !important; }
  /* screen pushes become crossfades; loops stand still */
  .animate-pulse, .animate-spin, .animate-ping, .af-working, .af-draw { animation: none !important; }
}
```

Plus `<MotionConfig reducedMotion="user">` at the root for the `motion` library.
