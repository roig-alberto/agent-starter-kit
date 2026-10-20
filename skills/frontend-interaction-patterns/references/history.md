# frontend-interaction-patterns - history

Dated notes and provenance that used to sit in `SKILL.md`, kept nearly verbatim. The full incident for
each trap lives in its topic file; this file records when and where things were learned.

## Provenance

- The topic files under `references/` were moved out of `frontend-interaction-patterns/SKILL.md`
  2026-09-08 (body-size restructure).
- Motion craft was split out when `animate` / `review-animations` / `apple-design` were installed
  2026-09-06. Sonner depth was `ask-sonner`. In the 2026-10-15 skills redo all the motion skills merged
  into `animate`, and `ask-sonner` and `pick-ui-library` merged into this skill (see below). The split
  stays: this skill picks the LIBRARY, `animate` owns how the motion feels.
- Working reference implementations live on this machine: `~/projects/personal-dash` (Aro) and
  `~/projects/finance-proj` (Caudal), WSL-native.
- The cross-platform CSS and SVG gotchas came from Aro, 2026-07-17.

## Trap index dates (the old SKILL.md one-liners)

- Icons crammed at the TOP of the bar, phone only: 2026-07-11. Flush-vs-reserve is a TASTE call; match
  the app the user names.
- Bar floats up with a gap below it, only on SHORT pages: 2026-07-12.
- A CTA above the nav drifts to the TOP of the page on iPhone: 2026-07-12.
- Fixed bar RIDES UP as you scroll (offset == scrollY): 2026-07-18.
- Fixed bar STRANDS mid-document once the page gets LONG: 2026-07-20. Headless is green BEFORE and AFTER;
  trust the phone. The redundant-`pb-28` variant: personal-dash 2026-07-24.
- `position:sticky` that never sticks: 2026-07-13 / 2026-07-15. `getComputedStyle` reports `sticky` in
  both broken cases.
- Full-screen overlay COVERED by the fixed nav on mobile: 2026-07-15.
- Rows squashed into thin bars: 2026-07-16; container with only `absolute inset-0` children collapsing:
  2026-07-10.
- A portal sheet inside a vaul or Radix modal dead to finger taps: 2026-07-19. "Can't tap the calendar"
  shipped to the phone twice because a synthetic `.click()` test passed green (`date-picker.md`).
- Bottom bar lifts after navigating (installed PWA only): 2026-07-16. Re-inserting the whole meta node also
  fixes offline cold loads but reflows the viewport every nav (slow), so it was rejected.

## The 2026-10-15 merge (skills redo)

### From `frontend-interaction-patterns` (this skill)

Everything above this heading. The body kept its rules and gotchas; the topic files kept their names.

### From `ask-sonner`

- `ask-sonner` was a standalone Sonner guide (wire the Toaster, pick the `toast()` call, style, theme,
  troubleshoot). Its description said to prefer it over this skill for any toast symptom, because this
  skill then only picked the toast library. After the merge one skill owns both, so the toast symptoms
  ("the toast never shows/appears", "toast behind the modal", "toasts are doubled", unstyled, dark mode
  ignored) sit in this description and the three most common are body gotchas.
- Its `references/api.md`, `references/usage.md` and `references/troubleshooting.md` became `sonner-api.md`,
  `sonner-usage.md` and `sonner-troubleshooting.md`. Its SKILL.md rules moved into the "Wiring" section
  of `sonner-usage.md`, nearly verbatim; its gotchas were already the rows of the troubleshooting table.

### From `pick-ui-library`

- `pick-ui-library` had `disable-model-invocation: true`, so it ran only when typed by name. `animate`
  pointed at it, but a model could never load it, and the user never types skill names. After the merge
  the curated list is `references/library-list.md`, which the model can read whenever it picks a library.
- Its steps, rules and smells moved into `library-list.md` nearly verbatim.
- Conflict settled in the merge: the list names base-ui for unstyled accessible primitives, while this
  skill had already standardised on shadcn + Radix (Aro audit 2026-07-13, recall migration 2026-07-13,
  Agent Factory). The box wins: shadcn + Radix stays the default, base-ui only on request. The list's
  `motion` pick is also qualified by the RULES.md note that only Shelf and Aro ship it.
