# Reviewer recall eval

Does `review-diff` catch a real bug when it sees only the commit that introduced it? Built 2026-10-20 from
Anthropic's "Solving code review" and "Automating eval design" posts: past bugs become the eval, and every change to
the reviewer's prompt, model or effort is scored against it before it ships.

## Files

| File | What |
|---|---|
| `cases.json` | 12 real cases from our repos (5 more stay private; their bug classes are listed below): the introducing commit, the fix, the file and line, the bug in code terms, keywords. Mined from `git log` fix commits and confirmed with `git blame`; confidence 3 to 5. No personal data: bugs are described in code terms only. |
| `mine.py` | Proposes cases from any repo: fix commits, and by `git blame` the commit that introduced each bug. `--check` compares it with the hand-made cases (15 of 17 the same, 2026-10-20). |
| `split.json`, `labels.json` | The tuning and held-out split, and hand labels that check the judge (both for the cases above). |
| `prompts/` | The reviewer prompt add-ons tried while tuning (`REVIEW_EXTRA`). |
| `run.py` | Reviews each case in a throwaway shared clone checked out at the introducing commit (`--base` = its parent), so the user's repos are only read. Resumable. One arm at a time. |
| `judge.py` | Haiku asks one checkable question per review ("does it report this bug, same place, same problem?"), twice. Caught = YES twice; a split is "unstable". |
| `out/` | Run outputs. Gitignored: reviews quote private code. |

## Run

```sh
python3 run.py <arm> <model> <effort> [repeats=2] [case-id ...]   # e.g. run.py sonnet-high sonnet high
python3 judge.py [arm ...]
```

A review costs about 15k tokens and 40 to 90 seconds. Several `claude -p` processes at once exhaust this box's memory,
so chain arms one after another.

## Scoring

1. `run.py` reviews each case twice per arm. An arm is a model plus an effort, for example `sonnet-medium`.
2. `judge.py` asks Haiku, twice per review, whether a finding names the same code path and the same mechanism as
   the known bug. It reasons first and puts the verdict on the last line.
3. Caught means YES twice. A split is "unstable" and counts as missed.
4. Recall is caught runs over all runs, per arm, printed for the whole set and for the tuning and held-out halves.
5. Every run also prints the judge's agreement with `labels.json`. Below full agreement, read the differing reviews
   before trusting any score: a judge error looks exactly like a reviewer miss.

## Build your own cases (a new machine)

The cases point at commits in the repos of the box that built them, so on another machine they only show the
format. Build a set from your own history:

1. `python3 mine.py ~/projects/<app> > candidates.json` for each app with some history. It keeps fix commits whose
   introducing commit has at most 60k characters of diff.
2. For each candidate, read the fix (`git show <fix>`) and the introducing commit. Keep it only if a reviewer
   could have seen the bug in that diff. Drop config values, vendor changes and taste.
3. Write `bug` in code terms (the function, what goes wrong, why), never with personal data. Add 3 to 5
   `keywords`. Set `confidence`: 5 when a test or the exact line proves it, 3 when probable. Remove `fix_subject`
   and `blame_share`.
4. Aim for 15 or more cases from at least 3 repos. Replace `cases.json` with them.
5. Make a new split: shuffle the ids with a fixed seed, put about a third in `test`, and write `split.json`.
6. Run one arm (`run.py sonnet-medium sonnet medium`), then label 10 or more of its reviews by hand in
   `labels.json` (`"<arm>/<case>-<n>": "caught"` or `"missed"`). Then run `judge.py` and check its agreement.
7. Add a case each time a review misses a bug that later ships.

Bug classes that held real cases here but stay out of the public kit (they describe one app's permission layer
and its money app). Look for them in your own history:

- A path checked with `startsWith` on the raw string, never normalized, so `../` escapes the allowed folder.
- A shell redirect target checked only by its text, so a symlink or a `$VAR` writes outside the sandbox.
- Two permission checks in the wrong order: an "ask the user" check runs before the deny rules, so a denied
  command reaches the user as a question.
- The server trusts a verdict the client sends ("the balance reconciles"), so a forged request skips the check.
- A security timer kept only in memory, so a page the OS discards and reloads never locks.

## Rules (from the eval post)

- **The judge never reviews.** Haiku judges; reviews run on Sonnet or Opus.
- **Measure the noise first.** Two runs per case per arm; a difference between arms smaller than the run-to-run swing
  is not a result.
- **Tuning the reviewer prompt:** split the cases at random into a tuning set and a held-out set, change one thing per
  round, and keep a change only if both sets improve. Never paste a missed bug's text into the prompt.
- **Rescore** whenever the `review-diff` prompt, its model or the `sonnet` alias changes, and record the result in
  `../plugin-verdicts.md`.
- **Add a case** each time a review missed a bug that later shipped: the introducing commit, the fix, the bug in code
  terms.
