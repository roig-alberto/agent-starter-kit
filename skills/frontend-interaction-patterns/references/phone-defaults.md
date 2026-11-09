# Phone defaults: six small rules for every screen

Six cheap habits that a phone-first app misses by default. Each one is a class or an attribute, so add it while
building the screen, not in a later polish pass. Source: a "20 UI tips" list the user shared on 2026-10-26; the
other 14 tips were already covered elsewhere (optimistic lists and Undo toasts here, motion in `animate`, safe
areas in `ios-pwa-dock`, idempotency keys in `backend-patterns`).

| Rule | Where it applies | How |
|---|---|---|
| Skeletons, not spinners | a first load that can take over about 300 ms | a block shaped like the content (same heights, rows, avatar circles), `animate-pulse` dropped under `motion-reduce:` |
| Cached first, then refresh | reopening a screen already seen | show the last data at once, refresh in the background, never blank the screen to refetch |
| Hit slop | any tap target under 44 pt (icon buttons, chips, checkboxes, a row's X) | an invisible larger tap area around the small visible one |
| One-time code autofill | every code input (2FA, email or SMS code) | `autocomplete="one-time-code"` plus `inputMode="numeric"` |
| Tabular numbers | numbers that change or line up (money, counts, timers, columns) | Tailwind `tabular-nums` |
| Balanced headings | headings and short multi-line labels | Tailwind `text-balance` on headings, `text-pretty` on paragraphs |

## Skeletons

- Show a skeleton only on the FIRST load of a screen. A refresh of data already on screen keeps the old data and shows
  a small busy sign (a thin top bar or a spinning refresh icon), because a skeleton flashing over known data reads as
  data loss.
- Match the real layout: same row height, same gaps, same number of rows the screen usually shows (3 to 5). A layout
  shift when the data lands is the bug this prevents.
- Delay it about 150 ms so a fast load shows nothing at all instead of a flash.
- Next.js app router: `loading.tsx` per route renders the skeleton. TanStack Query: render it when `isLoading`
  (pending and fetching), never on `isFetching`; `isPending` alone stays true forever on a query with `enabled: false`
  and no data, so a button guarded by it locks for good (agent-factory, 2026-10-19).

## Cached first, then refresh

- TanStack Query (Agent Factory): this is the default as long as `gcTime` is not set to 0 and screens read `data`
  while `isFetching`. Do not gate the whole screen on `isFetching`.
- Next.js server components: navigating back re-renders from the router cache; after a write, call
  `router.refresh()` and keep the old list on screen until it returns (the optimistic list rule in the SKILL).
- A hand-rolled fetch in `useEffect`: keep the previous value in state while the new request runs; do not reset it to
  `null` or `[]` first.

## Hit slop

Grow the tap area, not the drawing, so the layout stays dense:

```tsx
<button className="relative size-6 before:absolute before:-inset-2.5 before:content-['']" aria-label="Remove">
  <X className="size-4" />
</button>
```

`size-6` plus `-inset-2.5` on each side gives a 44 px tap area. Two neighbouring targets must not overlap their
areas; leave at least 8 px of gap or shrink the inset. Check with `document.elementFromPoint` at the edge of the
grown area, not with a `.click()` (red flag in the SKILL).

## One-time code autofill

```tsx
<input autoComplete="one-time-code" inputMode="numeric" pattern="[0-9]*" maxLength={6} />
```

iOS offers the code from Messages or Mail above the keyboard only with this attribute. Use one input, not six
boxes: split boxes break autofill and paste. The same habit for other fields: `autoComplete="email"`,
`"current-password"`, `"new-password"` (so the password manager offers to save), and `inputMode="decimal"` for
amounts (with `parseDecimal`, SKILL rules).

## Tabular numbers

Proportional digits make a ticking timer or a changing total jiggle sideways, and columns of amounts stop lining
up. Put `tabular-nums` on the element that shows the number (a timer, a counter badge, a money cell, a table
column), not on whole paragraphs of prose. Right-align amount columns as well.

## Balanced headings

`text-balance` spreads a 2 to 4 line heading evenly instead of leaving one word alone on the last line;
`text-pretty` only avoids that lone last word in a paragraph. Both are Tailwind 3.4+ classes (every app here is 3.4 or
4). Browsers balance only short blocks (Chromium stops at 6 lines), so use it on headings, card titles and toast
titles, not on long text.
