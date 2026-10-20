# Reviewer recall eval

Does `review-diff` catch a real bug when it sees only the commit that introduced it? Built 2026-10-20 from
Anthropic's "Solving code review" and "Automating eval design" posts: past bugs become the eval, and every change to
the reviewer's prompt, model or effort is scored against it before it ships.

## Files

| File | What |
|---|---|
| `cases.json` | 12 real cases from our repos (5 more that describe security bypasses stay private): the introducing commit, the fix, the file and line, the bug in code terms, keywords. Mined from `git log` fix commits and confirmed with `git blame`; confidence 3 to 5. No personal data: bugs are described in code terms only. |
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
