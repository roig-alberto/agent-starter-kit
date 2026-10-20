# debugging - incident history

The stories behind the rules in `SKILL.md`, kept nearly verbatim. Read them when a rule seems
excessive; each one cost real time or real data.

## Destructive repro on a real row (Aro, 2026-07-07)

Reproducing Aro's "delete meal plan errors" on the user's real plan wiped it (51 diary days referenced
it); it took a NAS-dump restore. A disposable record costs nothing. This is why step 1 says a
destructive trigger (delete, overwrite, cascade) is reproduced on a THROWAWAY record, never a real row.

## "Steps only update when I press reload" (Aro, 2026-07-13)

"The data is wrong" and "the client never re-rendered" produce the IDENTICAL symptom and live in
different layers. "Steps only update when I press reload" was theorized all the way up the stack
(a smartwatch cloud lag, then webhooks, then buy a Fitbit) before one query settled it:
`select date, steps, synced_at from daily_activity` showed today's row present and `synced_at` current
(worker cron logged `scheduled sync ok … activity:8`). The sync was fine; the `force-dynamic`
server-component page just never re-fetched, so an open tab kept its first render until the reload
button's `router.refresh()`.

Same incident's second half: a smartwatch' cloud lagged the watch until the iOS app was foregrounded
(now in personal-dash `IMPLEMENTATION_PLAN.md`, "Fresher steps than a smartwatch' cloud"), so even a reload that hit the vendor API returned old numbers.
"The DB is fresh" is only ever true relative to the layer above it.

## "Discard doesn't stop the workout" (personal-dash, 2026-07-24)

A destructive action that seems inert may work perfectly while the result stays INVISIBLE because
duplicate rows exist and the UI only shows the newest. A `startSession` with no single-session guard
inserted a row per tap, so 3 taps stacked 3 identical empty sessions; the dock/`getActiveSession` show
only the MOST RECENT, so Discard deleted the top one and the next identical one appeared - the button
always worked. Settled it by reading the store (3 "Espalda bis" sessions, 0 sets, 5s apart) and
watching the count go 3 to 2 on one tap, not by theorizing about the handler. Rule: N rows where there
should be 1 means the bug is the CREATOR without de-dup (fix = the single-session guard), never the
deleter.

## 2026-10-16: rewrite (skills redo, phase 3)

Adopted from mattpocock/skills `diagnosing-bugs` (MIT, commit 49dd158): the red-capable, tight feedback loop as
the gate before any theory (`references/feedback-loops.md`), minimizing until every element is load-bearing, 3 to
5 ranked falsifiable guesses shown to the user, one probe per prediction, tagged debug logs removed by one grep,
the test-first fix only at a correct seam, a `diff` against a pristine copy after forcing a red, and redaction.
Changed on purpose: Matt's human-in-the-loop bash template is replaced by asking the user for one action and a
screenshot per run, since the user works from a phone. The `performance` skill planned for phase 3 was folded in
as `references/performance.md` (user, 2026-10-16), with pstack's fair-measurement points (same input, several
runs, warm against cold). Kept from the earlier version: the evidence labels, the store-first layer reads, the
count-the-rows rule, the destructive-repro rule and the box's evidence sources. The old step 7 ("fix the root
cause, not the symptom") and step 8 ("prove the fix on the same path as the repro") became steps 5 and 6.
