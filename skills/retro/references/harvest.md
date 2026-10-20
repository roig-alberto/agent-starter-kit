# Processing the HARVEST inbox

`~/.claude/HARVEST.md` is the one inbox for lessons from every agent and every repo. Any agent appends a line
under `## Pending` the moment a lesson happens (the trigger list is in RULES.md, "Keeping knowledge true"). This
file is how `retro` empties it. It moved here from `knowledge-authoring` section 4 on 2026-10-16.

## The filter: accept only if every answer is yes

1. Will it still be true in six months, once paths, versions, and code shapes change?
2. Would a future agent do something different because of it?
3. Is it specific enough to recognize when it applies, but general enough to recur?
4. Is it missing from the target skill? Read the skill first; if the guidance exists but is buried, improve its
   placement instead of adding a duplicate.
5. Did the lesson come from a skill the session actually used, or from a missed trigger? A missed trigger means
   tuning that skill's description (then run `run-skill.sh <skill>`).

## Where an accepted lesson goes

1. A script, lint rule, type or test can enforce it: build that, not prose (`knowledge-lint.py` for knowledge
   files, the repo's own checks for app code).
2. It is about one repo: that repo's docs (`AGENTS.md` only if every session there needs it; otherwise `docs/`,
   the decision log or a gotchas section).
3. It recurs across repos: the existing skill's gotchas; a new skill only when no home exists and it recurs.
4. It must hold in every session for every agent: one line in RULES.md, kept short.

Write it with `knowledge-authoring` (placement table, style, ripple check).

## The record

Each processed entry: problem, proven fix, the losing approach and its cost, and the date. Tick the line and move
it to `## Processed` with where it went, or tick it as dropped with the failed criterion. `knowledge-lint.py`
rejects a malformed inbox and warns on entries older than 30 days.

## Monthly hygiene

- Processed entries older than 90 days leave the file; git keeps them. The file was 259 KB on 2026-10-16.
- If pending grew for a month (inflow above outflow), propose a stricter capture trigger in RULES.md instead of
  processing harder. Measured 2026-10-16: 64 pending, 54 from the last 7 days, none processed.
