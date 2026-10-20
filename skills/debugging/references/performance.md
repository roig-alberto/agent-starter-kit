# Too slow: the speed loop

Folded into `debugging` on 2026-10-16 instead of a separate `performance` skill: speed work came up about 3 or 4
times in two months (HARVEST), and it is the same loop with a number. Logs are usually the wrong tool here; a
measurement is the right one.

## Steps

1. **Measure a baseline number** the way the user feels it: "tab switch takes 900 ms on the phone", "the build
   takes 4 min", "this query takes 2.3 s". Use a timing harness, `performance.now()`, the browser profiler,
   `EXPLAIN ANALYZE` for a query, or `time` for a command. That number is the red command.
2. **Make the measurement fair** before trusting any comparison:
   - the same input and the same data size every run;
   - several runs, reporting the median and the spread, never one run;
   - warm and cold measured and labeled separately (first load against cached; dev against prod build);
   - the same machine state: no other heavy job running, the same container limits;
   - dev mode lies about speed (hot reload, unminified code): confirm a win on a production build.
3. **Rank 3 to 5 guesses** with predictions, as in the main loop ("if the waterfall of three fetches is the
   cause, parallelizing them cuts the time by about two thirds").
4. **Change one thing, measure again, keep or revert by the number.** A change that does not beat the spread is
   not a win; revert it, even if it "should" help.
5. **Log every attempt**, kept or reverted, in the task's notes or plan:

   | # | change | before | after | kept? | why |
   |---|---|---|---|---|---|
   | 1 | parallel fetches in `loadDay` | 910 ms | 340 ms | yes | the waterfall was the cost |
   | 2 | memoized `sumMacros` | 340 ms | 335 ms | no | inside the spread |

   The log stops the next session from retrying a failed idea.
6. **Prove it like a fix:** the baseline command on the original scenario, after numbers in the reply, and a
   guard (a test or a budget check) when there is a seam for one.

## A long improvement run (many tries toward a target)

When the job is to push one number toward a target over many tries ("get the bundle under 200 KB", "halve the tokens
per Implement step") rather than to fix one slowdown, the loop above runs many times, with four additions (adapted
from pstack's hillclimb playbook, 2026-10-16):

- **Set the stop rule before the first try:** a target plus a minimum number of tries, so a lucky early win does not
  end the run. Never loosen it to finish.
- **Prove the measuring script, then freeze it.** It must tell a known-slow case from a fast one, and print the median
  of N runs from one command. Changing it mid-run voids every comparison in the log.
- **Run the test suite on every try.** A win that turns a test red is reverted, however good the number.
- **A plateau is not the end.** After several reverts in a row, change the kind of idea (another layer, two near-misses
  combined, a fresh read of the code). Stop when the target is met or the ideas left cost more than they save, and say
  which.

## Where the known speed fixes live

Framework speed lessons found on this box (Next.js caching defaults, Turbopack recompiles) are in
`verify-ui-live/references/gotchas-and-perf.md`. Check there before measuring a Next.js app from scratch.
