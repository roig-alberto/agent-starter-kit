# Date field / calendar picker (react-day-picker)

## Date field / calendar picker → react-day-picker (shadcn Calendar), themed, in a bottom sheet
Native `<input type="date">` is unstylable + renders inconsistently on iOS (locale format, an
intrinsic width that overflows a flex row - see min-w-0 trap below). **Winner:** shadcn's Calendar =
`react-day-picker` (v10 on Aro) fully Tailwind-classed to the app's tokens, wrapped in a `DateField`
(field-styled trigger → calendar in a bottom sheet). Theme via `classNames` (start from
`getDefaultClassNames()`) + custom `DayButton`/`Chevron` components; props `weekStartsOn`, `disabled`
(min/max matchers), `startMonth`/`endMonth`. v10 classNames keys differ from v8/v9 - read them from
`getDefaultClassNames()`, never guess.
**TZ off-by-one trap:** parse "YYYY-MM-DD" as `new Date(`${s}T12:00:00`)` (local NOON anchor) and
format back with date-fns `format(d,"yyyy-MM-dd")` (local). NOT `toISOString().slice(0,10)` - that is
UTC and rolls the day back one in `+0x` zones. Reference: personal-dash `components/ui/{calendar,date-field}.tsx`. 2026-07-19.

### A flex-row `<input type="date">` needs `min-w-0` or it overflows on iOS (whole panel shifts left)
iOS date inputs have a large intrinsic content width; a flex item defaults to `min-width:auto` (won't
shrink below its content), so a date input in a `flex-1` track blows the row wider than its frame - the
scroll container then focus-scrolls the WHOLE column left, clipping every label ("TARGET"→"ET"). Desktop
Chromium's narrower date input hides it entirely (looks fine headless, breaks on the phone). **Fix:**
`min-w-0` on BOTH the flex track AND the input (`w-full min-w-0`). An overflow guard does NOT fix it:
`overflow-x:clip` beside `overflow-y:auto` computes to `hidden`, and `hidden` still allows
focus/programmatic horizontal scroll (proved: scrollLeft moved to 90 under `hidden`). Kill the overflow
at the source, don't clip it. Reference: personal-dash `goal-sheet.tsx` / `phase-editor.tsx`. 2026-07-19.

### A portal sheet rendered INSIDE a vaul/Radix modal is dead to finger taps → `pointer-events-auto`
A bottom sheet (calendar picker, phase config, …) that `createPortal`s to `document.body` while a vaul
`Drawer` / Radix Dialog modal is open inherits the modal's `body { pointer-events: none }` - real finger
taps are swallowed. Synthetic `.click()` bypasses hit-testing, so it PASSES in Playwright and looks fine.
**Fix:** `pointer-events-auto` on the portal root (re-enables the whole subtree). **Verify with
`document.elementFromPoint(x,y)`** (a real hit-test that resolves to the button), never `.click()`.
Reference: personal-dash `components/ui/bottom-sheet.tsx`. Cost: shipped "can't tap the calendar" to the
phone twice because the synthetic-click test passed green. 2026-07-19.
