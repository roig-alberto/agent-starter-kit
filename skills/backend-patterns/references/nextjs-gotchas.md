# Next.js server-side gotchas

Each of these cost a debug pass or a broken deploy. The one-line versions are in `SKILL.md`.

- **A `"use server"` file may ONLY export async functions.** Adding
  `export const MAX_ELEVATIONS = 3` beside the actions breaks the whole route with a 500
  (`Only async functions are allowed to be exported in a "use server" file`), and neither `tsc`
  nor `eslint` catches it - it appears only when you request the page. Constants shared between an
  action and its page belong in a `lib/` module. (loop, 2026-09-01)
- **`allowedDevOrigins` in `next.config.ts` REPLACES the default dev allowlist, it does not extend
  it.** Adding only the tunnel hostname (`['dev-loop.example.com']`) silently dropped
  `127.0.0.1`/`localhost`, so every page still rendered server-side and returned **HTTP 200 while
  React never hydrated** on localhost - no gestures, no buttons, no client navigation. Always
  include the localhost origins alongside the tunnel host. (loop, 2026-08-30)
- **A per-item Server Action that reshapes the list it is rendered from = runaway cascade**, because
  invoking a Server Action auto-refreshes the current route. loop's resurface flow read
  `cards[index]` straight from the server prop and called `markResurfaceShown` in a per-card
  `useEffect`; the insert triggered the implicit route refresh, which re-ran the page query, which
  re-rendered the list, which fired the effect again. Snapshot the item into client state, or move
  the write out of render. (loop, 2026-08-31)
- **Second confirmation of the `revalidatePath` rule below:** triage's swipe advanced the card but
  the UNDO banner never appeared - `revalidatePath('/bandeja')` re-rendered the parent RSC and
  reconciled away the client component holding the undo state. Generalises past recall.
  (loop, 2026-08-30)

- **A server-action `redirect()` from a segment's INDEX page to a route NESTED under that same
  segment never completes** (Next 15.5.20) - the transition stays pending forever and takes the
  whole router with it. `/workouts` → `/workouts/session/[id]` triggers it;
  `/workouts/routines/[id]` → `/workouts/session/[id]` (same depth) does not. It does NOT look
  like a hang: the main thread is alive, no overlay, no JS error, the POST returns 303 with
  `x-action-redirect` and the destination RSC returns 200 - the user just reports "the app
  freezes, I have to close and reopen it". Navigate from a sibling depth, or redirect
  client-side. (personal-dash, 2026-07-27)

- **A prod Dockerfile MUST set a build-only placeholder `DATABASE_URL`.** `lib/db` throws
  at IMPORT when it's unset, and `next build`'s "collect page data" evaluates every route
  module (even `force-dynamic` ones) with NO runtime env - `env_file` is runtime-only. This
  is why recall's prod build had never worked. Fix, before `RUN npm run build`:
  `ENV DATABASE_URL="postgres://build:build@127.0.0.1:5432/build"` (compose overrides it at
  runtime). Verified present in `~/projects/recall/Dockerfile:32` and Caudal's.
- **Don't `revalidatePath` the CURRENT route from a server action whose caller renders the
  result IN PLACE.** recall: grade-a-session showed results without navigating; the
  revalidation refreshed the parent server component mid-`useTransition`, that component
  now took an emptier branch ("0 due"), React reconciled to it and UNMOUNTED the client
  holding the result state - results vanish, though the DB write clearly succeeded.
  `force-dynamic` pages re-fetch on the next navigation anyway, so it was redundant.
- **NOTHING exported from a `"use client"` module is usable by a server component - and
  `tsc` says nothing.** Values too, not just functions: personal-dash 2026-07-23 exported
  `ADD_FOOD_TABS` (a plain `as const` array) from `add-food-screen.tsx` and used it in the page
  to validate `?tab=`; the page got a client REFERENCE and threw
  `ADD_FOOD_TABS.find is not a function` on the first real GET. Second occurrence in that repo - 
  the first was a function (`AchievementState.def`, "Functions cannot be passed directly to Client
  Components"), so treat it as a rule, not a one-off: **arrays, maps, constants and functions all
  cross as opaque references.** Fix: the shared thing goes in a neutral db-free module both sides
  import (`lib/nutrition/add-food-tabs.ts`), never in the `"use client"` file. Detection: only a
  real request to the route catches it - not the typecheck, not vitest. Same invisible-to-tsc
  family as the enum-value trap above.
- **A `lib/` module imported by BOTH an RSC/page and the node `worker/` must NOT
  `import "server-only"`** - the worker (tsx) crashes at import ("cannot be imported from a
  Client Component"). personal-dash convention: `server-only` is fine only if no worker
  imports it; shared derive/read logic (`computeGoal`, `lib/objectives/metrics.ts`) stays
  plain. Client components type-import safely (erased).
