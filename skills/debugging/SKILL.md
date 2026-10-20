---
name: debugging
description: >-
  Evidence-first loop for anything broken or slow whose cause is not proven: a command that goes red on
  this exact bug comes before any theory, then ranked guesses, then a fix proven on the same command.
  Use when an app, page, script or query errors, misbehaves, does nothing, is down, or got slower: "it's
  broken", "why doesn't this work", "fix this error", "I get this error", "the app is down", "not working",
  "this page is slow", "it takes forever", a pasted stack trace, a 500, a silent no-op, a flaky script. Use
  it even when the cause "looks obvious". NOT for the machine itself running out of memory or disk (use fleet-ops), a new feature (use
  one-shot) or motion that feels off (use animate).
---

# debugging - a red command first, a fix second

This skill prevents the most expensive debugging failure: guessing a cause from the symptom, "fixing" it,
declaring victory, and being wrong. Every step produces evidence before code changes. The center of it is a
**red** command: one command you have run that goes red on this exact bug and will go green once it is fixed.

## Steps

1. **Build the red command before any theory.** Reproduce the failure the way the user hits it (the real
   request, container, browser width), as one command you can rerun unattended: a failing test, a curl, a CLI
   call against a fixture, a headless browser script. Ways to build one, and how to make it **tight** (fast,
   deterministic, asserting the user's exact symptom): `references/feedback-loops.md`. A destructive trigger
   (delete, overwrite, cascade) runs on a throwaway record, never a real row (see `testing`). If you cannot
   build it, say so, list what you tried, and ask the user for an artifact or access; do not theorize.
   Done when: you have run the command once, it shows the user's symptom, and you can paste its invocation.
2. **Read the error verbatim, then minimize.** Quote the actual message, line and exit code from the terminal,
   never from memory; a silent no-op is itself a finding, so make it loud in step 4. Cut inputs, steps and
   config one at a time, rerunning the red command after each cut.
   Done when: every remaining element is load-bearing (removing any one turns the command green).
3. **Rank 3 to 5 guesses before testing any.** One guess anchors on the first plausible idea. Write each as a
   prediction: "If X is the cause, changing Y makes the bug disappear." A guess you cannot phrase that way is
   a vibe; drop it. Show the ranked list to the user, who may re-rank it at once; do not block if they are away.
   Done when: the list is in the reply, ranked, each with its prediction.
4. **Instrument one prediction at a time.** Probe the boundary that separates two guesses: a debugger, a
   targeted log, `docker logs`, `--verbose`, a curl, a DOM measurement. Tag every temporary log with one
   prefix such as `[DEBUG-a4f2]`, so cleanup is one grep. Never change two things in one run. When lost,
   bisect: `git bisect`, half the input, half the code, or last-known-good plus re-adding.
   Done when: one guess survives and the others are falsified by output you can quote.
5. **Fix the root cause, test-first where a correct seam exists.** Turn the minimized repro into a failing
   test at a seam that exercises the real bug pattern; watch it fail, fix, watch it pass. A seam too shallow
   for the bug gives false confidence: then record "no correct seam" as a finding. A fix that does not explain
   the evidence (why THAT error, why THERE) is a symptom patch; keep digging.
   Done when: the regression test passes, or the missing seam is written down.
6. **Prove it and clean up.** Rerun the step 1 red command on the original scenario and show it green. Remove
   every tagged log (`grep -rn "DEBUG-a4f2"` prints nothing) and throwaway harness. Close out with five parts:
   the root cause, the decisive evidence lines, the fix (files), the regression test or why none, and the green
   rerun. Name the guess that proved right in the commit message.
   Done when: all five parts are in the reply and the grep is empty.

**Too slow, not broken?** The same loop with a number: the red command is a timed measurement, each change is
kept only if the number improves, and every attempt goes in a log so a failed idea is not retried. Read
`references/performance.md` before changing code for speed.

## Rules: label every claim by evidence

- **Direct:** you observed it and cite it (the output line, the file and line, the query result). Only this
  label can carry "fixed" or "the cause is".
- **Supported:** several independent sources agree; name them, because two views of one source are one source.
- **Inferred:** reasoned from evidence; state the chain so a wrong link can be found.
- **Guess:** no evidence yet; name the check that would settle it.
- **Unknown:** you looked and did not find it; say what you searched and where.
- **Never present code as evidence of its author's intent.** Code shows what runs, not what was meant.
- **A guess embedded in the user's question is a candidate to test, not a conclusion.** "Is it the cache?"
  gets a falsifying check like any other guess.

## Rules: pick the layer with a read

- **"X only updates when I reload / after I leave and come back": read the store first.** Fetch the row and its
  `updated_at`/`synced_at` (`docker exec <db> psql -c "select …"`). A fresh row with a stale screen is a CLIENT
  bug; stop touching the pipeline, webhook or hardware.
- **Prove the client is not re-fetching.** Reload with the network filtered to the data path; no request on the
  user's stale path is the proof. The fix is a visibility-gated `router.refresh()`, never a re-sync call.
- **Only if the store IS stale, walk the writer, then the upstream source.** Read the cron or worker logs, then
  check the upstream is current before blaming your own sync.
- **"The delete/stop button does nothing": count the rows before touching the client.** N rows where there
  should be 1 means the creator lacks de-dup (fix with a single-session guard), never the deleter.

## Rules: redact

Before showing a command, output or captured artifact, replace every secret with `<REDACTED>`. Build loops on
environment variables, so a credential stays in the environment and never in what you show. Quote only the
lines that carry the signal; captured requests carry auth headers.

## Evidence sources on this box

- **Container apps:** `docker logs <container> --tail 120`, `docker ps -a` (running or restart-looping?) and
  `docker compose config`. Container names are in `~/.claude/FLEET.md`.
- **UI issues on tunneled apps:** measure the real DOM with `verify-ui-live` instead of eyeballing it.
- **"Can't access it":** DNS and the hostname first (`NXDOMAIN` looks identical to a down app), then the tunnel
  origin target, then the container. See the `verify-ui-live` gotchas.
- **Port collisions:** `fleet-ops`. **Backup or NAS pipeline:** `backups-and-alerts` (not in this kit).
- **Stale UI that "won't deploy":** usually the service-worker cache; see the `verify-ui-live` gotchas.

## Gotchas

- **You want to fix before reproducing ("it's probably the null check").** Stop and build the step 1 command.
- **You are reading code to build a theory and no red command exists yet.** That is the failure this skill
  prevents; go back to step 1.
- **You forced a test red by editing code or a fixture.** `diff` against a pristine copy to prove the edit
  landed before you trust the red.
- **You changed three things and reran once.** Revert to one change per run, or you learn nothing.
- **You are about to say "fixed" because the code should work now.** Rerun the red command first.
- **The urge to refactor mid-debug.** Park it; one problem at a time.
- **Two `node --watch` dev servers race for the port** and the log still says "listening", so probes hit stale code. Before starting one, check `ps -eo pid,etime,args | grep 'watch server'` and stop the old one by PID; compare `ps -o lstart -p <pid>` with the file's mtime before trusting a probe.

## References

- `references/feedback-loops.md`: ten ways to build the red command, how to tighten it, flaky bugs, and what to
  ask for when no loop is possible. Read in step 1.
- `references/performance.md`: the speed loop, the attempt log and the fair-measurement checklist. Read before
  any speed change.
- `references/history.md`: the incidents behind the destructive-repro, store-first and count-the-rows rules,
  and the sources of this version.
