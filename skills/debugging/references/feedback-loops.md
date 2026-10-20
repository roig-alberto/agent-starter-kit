# Building the red command

Adapted from mattpocock/skills `diagnosing-bugs` (MIT, commit 49dd158). The red command is the skill: with a
tight pass/fail signal that goes red on this bug, bisection, guesses and instrumentation just consume it.
Without one, reading more code does not help. Spend disproportionate effort here.

## Ways to build one, roughly in this order

1. A failing test at whatever seam reaches the bug: unit, integration, end to end (`testing` has the runners).
2. A curl or HTTP script against the running dev stack.
3. A CLI call with a fixture input, diffing stdout against a known-good snapshot.
4. A headless browser script that drives the UI and asserts on the DOM, the console or the network
   (`verify-ui-live`: `ui-check`, `chrome-devtools-axi`, a committed `e2e/*.e2e.py`).
5. Replay a captured trace: save a real request, payload or event log to disk and replay it through the code
   path alone.
6. A throwaway harness: one service, mocked dependencies, the bug path reached by a single function call.
7. A property or fuzz loop: for "sometimes wrong output", run 1000 random inputs and look for the failure.
8. A bisection harness: when the bug appeared between two known states (commit, dataset, version), automate
   "boot at state X, check" and run `git bisect run` on it.
9. A differential loop: run the same input through the old and the new version, or two configs, and diff.
10. The user as the loop, last resort: when only the user's phone shows the bug, ask for one exact action and a
    screenshot or screen recording per run, and keep a numbered log of each run's input and result.

## Tighten it

Treat the loop as a product. Make it faster (cache setup, skip unrelated init, narrow the test), make the signal
sharper (assert the specific symptom, not "did not crash"), and make it deterministic (pin time, seed random
numbers, isolate the filesystem, freeze the network). A 30-second flaky loop is barely better than none; a
2-second deterministic one is tight.

The finished command is:

- **red-capable:** it drives the real bug path and asserts the user's exact symptom;
- **deterministic:** the same verdict every run, or a pinned, high reproduction rate for flaky bugs;
- **fast:** seconds, not minutes;
- **unattended:** any agent can run it without a person, except loop 10.

## Flaky bugs

The goal is a higher reproduction rate, not a clean repro. Loop the trigger 100 times, run in parallel, add
stress, narrow timing windows, inject sleeps. A 50% flake is debuggable; 1% is not, so keep raising the rate.

## When no loop is possible

Stop and say so. List what you tried. Ask the user for one of: access to the environment that reproduces it, a
redacted captured artifact (a HAR file, a log dump, a screen recording with timestamps), or permission to add
temporary instrumentation in production. Do not move on to guesses without a loop.

## Wrong bug

Before minimizing, check the red output is the failure the user described, not a different failure nearby. A
loop that goes red on the wrong bug leads to the wrong fix.
