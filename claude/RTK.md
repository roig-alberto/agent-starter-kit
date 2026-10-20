# RTK - the command proxy on this box

`rtk` rewrites dev commands through a Claude Code hook (`git status` runs as `rtk git status`) and
filters their output to save tokens. Filtering is also the trap: a filtered result can look exactly
like an empty one. Measurements behind these rules are in `~/.claude/HISTORY.md` (re-measured against
rtk v0.43.0 on 2026-09-05).

## Commands

```bash
rtk proxy <cmd>       # run raw, without filtering
rtk gain              # token savings so far (also proves this is the right rtk)
rtk gain --history    # per-command history
rtk discover          # missed opportunities in Claude Code history
```

If `rtk gain` fails, a different tool called rtk (reachingforthejack/rtk, Rust Type Kit) may be installed instead.

## Rules

- Before stating "there are none", "nothing matches", or "it never happened", re-run the command through `rtk proxy`. Filtered output cannot prove absence.
- Get the total yourself. `rtk grep` announces `+N more` but never the total, prints 0 bytes on zero matches (only the exit code says so), and defaults to `--max 200` and `--max-len 80`. Count with `rtk proxy <cmd> | wc -l` or `grep -c`, or raise `-m`.
- Do not assume one subcommand behaves like another. `rtk docker ps` prints an honest total; `rtk grep` does not.
- For logs, use `rtk proxy docker logs <c> 2>&1 | grep -a <pattern>`. `docker logs` through rtk has returned a summary-only view of a Next.js container, and plain `grep` treats cloudflared logs as binary and prints nothing.
- Never write `sudo <cmd>`. The hook turns it into `sudo rtk <cmd>`, which fails with `sudo: rtk: command not found` on stdout, so a check reads it as an empty file. Write `sudo /bin/sh -c '<cmd>'`; the hook only rewrites the outer word. `scripts/agent-guard.py` blocks a bare `sudo` before it runs.
- A check passes only on exit code 0, never on rtk's summary line. `rtk tsc` reports "TypeScript: No errors found" whenever it sees no `error TS` lines, including when tsc never ran (no local TypeScript, so `npx tsc` printed a refusal and exited 1). Read `${PIPESTATUS[0]}` after a pipe, or run the check through `rtk proxy`. Since 2026-10-19 `tsc` and `npx tsc` are in `exclude_commands` (`~/.config/rtk/config.toml`, INSTALL.md step 6) and run raw; the rule still holds for every other rtk filter.
- The hook rewrites `grep` inside pipes too, so `grep ... | while read` gets rtk's summary line instead of the lines. Feed loops with awk or `rtk proxy grep`, and give `claude -p` inside a loop `< /dev/null`.
