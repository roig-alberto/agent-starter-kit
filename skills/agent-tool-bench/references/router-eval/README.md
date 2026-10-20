# Router eval - does a prompt load the right skill?

## Baseline (2026-10-16, phase 2 of the skills redo)

39 fixtures in `fixtures.tsv`: 27 real messages from past chats (typos kept), 9 from the 2026-09 runs, 3
synthetic, 3 of them negatives ("none": no skill should load). Numbers are in `baseline.json`.

- **Free check** (`python3 word_rank.py`, 0 tokens, under a second): top-1 23/36 (64%), top-3 30/36 (83%), no
  description pair over 0.5 cosine. Port of Addy Osmani's run-evals.js Tier 2 (MIT); the routing surface is the
  skill name (twice), its description and its RULES.md router rows. It measures shared words only: "a screen to
  edit the foods" ranks `one-shot` 27th, yet a real model picks it through the router row.
- **Real runs** (`run.sh`, Sonnet, 2-turn cap, write-proofed): 32/39 (82%) at $4.66 API-equivalent, about
  $0.12 and 7 seconds a run. Every failure loaded no skill; none loaded a wrong one.
  - Real misses: `orca` (a tool-adoption question went straight to WebFetch, never `agent-tool-bench`);
    `select_finicky` (a finicky select loaded nothing, in the scratch repo and in Aro's repo).
  - Harness, not routing: `anim_slow_menu` failed in the empty scratch repo but loaded `animate` inside Aro's
    repo. `plain_1`, `plain_2`, `scaffold` and `design_canvas` are mid-conversation replies; alone, the model
    rightly asks what "this" means. Rewrite them with the earlier message in the prompt.

## Phase 5 router rewrite (2026-10-16)

The RULES.md router went from 33 rows to 9 grouped rows ("Area | Skill, and when", each skill with its own
segment). Four full sweeps the same day, on the original 39 fixtures: the old router 32/39 (morning); the 9 rows
29/39; the 33 rows restored 28/39; the 9 rows plus a precedence note 33/39 (37/43 on all fixtures, $5.09). Two
lessons:

- **One sweep at n=1 swings by about 3 fixtures** (`anim_page_load` loaded three different skills in three runs).
  Compare two routers on the same day with the same skills, never against an older baseline; prefer n=2 when
  the gap is under 4.
- **`one-shot` steals specialist requests** (swipe, animation, desktop) once its description reads "use when the
  user asks to add, change, fix". The fix was one precedence line in the router notes, not description edits:
  the router is always loaded, a description is not (the same lesson as 2026-09-08).

## Coverage rule (2026-10-16)

Every skill has at least one fixture where it is the ONLY accepted answer; a skill that appears only as an
alternative would pass even if it never loaded. 20 fixtures were added that day for the 9 skills with no test
(`testing`, `architecture`, `backups-and-alerts` (not in this kit), `capacitor-apk-wrap` (deleted the same day at the user's request), `create-verification-skill`,
`gh-git-ops`, `grill-me`, `home-assistant-fleet` (not in this kit), `skills-audit`) and the 8 covered only as alternatives;
19 of 20 loaded the expected skill on the first run (the miss was a mixed request that `one-shot` rightly took).
A new skill gets its sole-answer fixture in the same change.

## Fixture fixes (2026-10-16)

- A mid-conversation reply is tested with its earlier message in the prompt ("Earlier you wrote: ... My reply:
  ..."), source `real+context`. Alone, the agent rightly asks what "this" means. With context, `plain_1`,
  `plain_2`, `scaffold` and `design_canvas` all loaded the expected skill.
- A fixture that fails once is run 3 times before anything changes; 2 of 3 is a pass. `resume_coach` (1/3) and
  `select_finicky` (0/3) were real gaps: one quoted trigger phrase each in the skill description took both to
  3/3. A description fix needs only `run-skill.sh`; a router fix needs the full sweep.

## When to run what

1. Every turn, automatically: `knowledge-lint.py` runs the free check and warns when top-1 falls below
   `baseline.json`.
2. After changing a skill's description or its router row: `./run-skill.sh <skill>` runs only the fixtures that
   expect it (about $0.12 each), then `python3 score.py 1`.
3. Full sweep (about $5, 6 minutes): after ANY change to the RULES.md router (a row can steal another skill's
   prompts, so a per-skill run is not enough), and weekly in the skills review. `knowledge-lint.py` warns until
   it is done: it compares a fingerprint of the router with `router_sha` in `baseline.json`; record the new
   one after a sweep that passes. Feed
   the loop with awk, never `grep` (the rtk hook rewrites grep and the loop runs on its summary line):
   `awk -F'\t' '!/^#/ && NF==4' fixtures.tsv | while IFS=$'\t' read -r id prompt expected source; do ./run.sh "$id" "$prompt" 1; done`
4. Raise `baseline.json` when a full sweep beats it. Lower the free check's number only when a real run proves
   the fixture it lost still routes correctly, and record that run in `word_rank_changes` (first case: the
   `debugging` rewrite cost `box_slow` its word-overlap win, while the real run still loaded `fleet-ops`).

Run transcripts (`*.jsonl`, `*.gitcheck`) are gitignored. `fired.py` prints what one run loaded.

## History (2026-09)

Unfinished then. 5 of 10 fixtures ran (all passed); the other 5 were cut off by a monthly spend limit
on 2026-09-07, NOT by a routing failure - their transcripts contain
`You've hit your monthly spend limit` and zero tool calls.

## Why this exists

Nothing else checks that the ~55 installed skills actually FIRE. `skills-audit` checks whether
skill CONTENT is stale; a skill whose trigger never matches passes every audit and is never used.
Adding 12 Emil skills on 2026-09-06 raised the odds of a trigger collision.

## Run it (2026-09 form, superseded by "When to run what" above)

```bash
while IFS=$'\t' read -r id prompt expected; do ./run.sh "$id" "$prompt" 1; done < fixtures.tsv
```

`run.sh` writes `<id>-<n>.jsonl` (stream-json) plus `<id>-<n>.gitcheck` next to itself.
Detect the fired skill by scanning for `tool_use` entries named `Skill`.

**Write-proofing is mandatory and load-bearing.** An earlier version ran with
`--permission-mode bypassPermissions` and no tool restrictions inside `~/projects/loop`; the agent
treated a fixture prompt as a real request and edited `components/swipe-deck.tsx` (reverted).
`run.sh` now disallows Edit/Write/NotebookEdit/Bash and asserts `git status --porcelain` is empty
after every run. Do not remove either guard.

## Grading

Regression eval, so the bar is `pass^3` (see the grading section of `../method.md`) - a router line matching
two prompts in three is a defect, not 67%. Sweep at n=1 for breadth, then n=3 on what fires.

## Result so far (n=1, 2026-09-07)

| fixture | expected | fired |
|---|---|---|
| swipe_janky | frontend-interaction-patterns | PASS |
| app_down | debugging | PASS |
| schema | backend-patterns | PASS |
| expose | security-posture | PASS |
| box_slow | docker-fleet-maintenance | PASS |
| sheet_motion, desktop, bump, toast_modal, tool_worth | - | NOT RUN (spend limit) |

The two most valuable are unrun: `toast_modal` tests the `ask-sonner` vs
`frontend-interaction-patterns` boundary, and `tool_worth` tests whether `agent-tool-bench` fires
at all - if it does not, everything in it is dead weight.

Caveat: restricting tools could shift behaviour slightly. Skill selection happens on the first
turn from the prompt alone, so the effect should be small, but it is not zero.


## Run 2 (2026-09-08) - PARTIAL, and it exposed a COST BUG in the harness

Stopped early: it drained the 5-hour quota. **Root cause (now fixed): `run.sh` had no turn cap, so
each run did not stop after the skill fired on turn 1 - it went on to DO the task for 48-75
assistant turns** (read files, plan), 15 runs of that. Skill selection is turn-1; the rest was pure
waste. Fixed: `run.sh` now passes `--max-turns 2`. Re-run cost should drop by ~30-40x. Do NOT run
the sweep again without that cap. Also: run FEW at a time (3-6), not 15 in one unattended batch.

Completed before the kill (n as far as it got), all write-proofed (loop worktree clean):

| fixture | expected | fired | verdict |
|---|---|---|---|
| sheet_motion | `animate` | **`frontend-interaction-patterns` (3/3)** | **FAIL** - trigger collision |
| desktop | `responsive-desktop-port` | `responsive-desktop-port` (2/2) | pass so far |

**Finding (real, the point of the eval): `animate` does NOT fire for "the bottom sheet opens too
abruptly, make it feel nicer" - `frontend-interaction-patterns` eats it 3/3.** fip's "bottom sheet"
trigger wins over animate's motion-craft triggers. The fip->animate boundary note (added 2026-09-06)
does not help, because it lives INSIDE fip and only a model that already loaded fip would see it. So
the motion-polish prompt never reaches `animate`. This directly answers part of the "do the new UI
skills fire" question: **at least `animate` is shadowed by fip for sheet-motion prompts.** Options to
weigh (not yet done): sharpen `animate`'s description to claim motion-polish verbs, or add a
router precedence line. UNRUN: bump, toast_modal, tool_worth (the two most valuable still pending).


## Run 3 (2026-09-08, quota reset, `--max-turns 2` cap = cheap)

8 capped runs (1-2 turns each vs 48-75 uncapped). All write-proofed (worktree clean).

| fixture | expected | fired | verdict |
|---|---|---|---|
| bump | `dependency-updates` | `dependency-updates` (3/3) | **PASS (pass^3)** |
| toast_modal | `ask-sonner` \| `frontend-interaction-patterns` | fip (2/3), direct-Grep (1/3) - **ask-sonner never** | mixed: fip is accepted, but ask-sonner is shadowed |
| tool_worth | `agent-tool-bench` | answered from context, no Skill | **CONTAMINATED** - the fixture asks the axi-vs-playwright question whose answer this session wrote into ENVIRONMENT.md; the agent read it and answered directly. Rewrite the fixture to a tool the docs do NOT mention. |

**Headline finding - fip shadows the new specialist UI skills.** `animate` (Run 2: sheet_motion→fip
3/3) and `ask-sonner` (toast_modal→fip 2/3, never ask-sonner) both lose to
`frontend-interaction-patterns`, whose broad triggers ("bottom sheet", "toast", "modal") match the
signature prompts of the new Emil skills first. The reciprocal boundary NOTE added inside fip on
2026-09-06 cannot help - it is only read AFTER fip has already won. Fix options (a routing decision,
not yet made): (a) sharpen `animate`/`ask-sonner` descriptions to claim the motion/toast verbs and
add a router precedence line fip↔them; (b) narrow fip's toast/sheet triggers to defer to the
specialist. Either is free.

**Two harness fixes still owed (free):** `run.sh` should add `--setting-sources ''` for isolation
(Run 3 showed the agent answering from this session's own doc edits - the same contamination class
the arm-isolation section of `../harness.md` already documents for the axi harness); and `tool_worth` needs rewriting to an
undocumented tool.

## Status
- PASS (pass^3 or accepted): swipe_janky, app_down, schema, expose, box_slow (n=1, Run 1); bump (3/3).
- desktop: responsive-desktop-port (2/2, Run 2).
- FAIL/shadowed: sheet_motion→fip (animate shadowed); toast_modal→fip (ask-sonner shadowed).
- Contaminated/invalid: tool_worth (rewrite).


## Shadowing fix applied + VERIFIED 2026-09-08 (n=2 post-fix, both flipped)

User keeps the UI skills, so the fix is to make them WIN, not disable them. Root cause: the
fip→animate/ask-sonner boundary lived in fip's BODY, which routing never reads. Moved it to the
DESCRIPTIONS (the routing surface), symmetric:
- `frontend-interaction-patterns` description now DISCLAIMS motion-feel ("opens too abruptly / make
  it feel nicer / feels off" → `animate`) and toast behavior (never shows / doubled / behind a modal
  → `ask-sonner`), stating it only picks the LIBRARY.
- `animate` description now claims those feel-verbs and asserts it wins over fip when the element is a
  sheet/drawer/dialog/toast/nav.
- `ask-sonner` asserts precedence over fip for any toast symptom.

NOT yet re-run (quota). To verify (cheap now, `--max-turns 2`): re-run sheet_motion + toast_modal at
n=3 and confirm animate / ask-sonner fire pass^3. Budget note: this GREW 3 descriptions (~600 bytes)
 - a shadowed skill that never fires is worse waste, so it's the right trade, but the budget still
needs the separate free recovery (trim answer-fat descriptions).

**VERIFIED:** after the fix, sheet_motion -> `animate` (2/2) and toast_modal -> `ask-sonner` (2/2).
The load-bearing lever was NOT the skill descriptions (fip's defer clause truncates - fip is the
fattest description and gets cut before its NOT-section) but the **RULES.md router precedence**
(always-loaded, never truncated): sharpened to "an EXISTING component that opens too abruptly / feels
janky / needs to feel nicer is a motion-FEEL fix -> animate, even when it's a sheet/nav/toast; fip
only for CHOOSING the primitive." Plus ask-sonner asserting precedence + removing fip's
"toast never appears" trigger from its (visible, early) symptom list. Lesson: **for a routing
precedence fix, edit RULES.md (always loaded), not a fat skill description that truncates.**
