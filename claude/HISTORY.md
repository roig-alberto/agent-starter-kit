# HISTORY.md - the evidence behind RULES.md and ENVIRONMENT.md

RULES.md and ENVIRONMENT.md keep each rule or fact plus one sentence of why. This file keeps the
incidents and measurements, so a rule can be re-judged later. Not loaded every session.

## Measure the real data first

Dumping the actual headers of the false positives beat two confident guesses in one slice:
`List-Unsubscribe` covered only 7/25 messages and its ABSENCE proved nothing, so the "obvious" fix
would not have fixed the motivating case (superhuman-mvp, 2026-07-17). Confirmed three more times:
a session where four confidently reasoned conclusions all died on contact with the data (loop,
2026-08-29); measuring task activity by `createdTime` instead of `modifiedTime` declared 20 of 23 live
TickTick lists dead and reached a finished brief as an architecture decision (personal-dash,
2026-08-29); a rate computed over elapsed weeks with no window floor rated a one-day-old project
"comfortably on pace", hiding exactly the case the feature existed for (loop, 2026-09-01).

## Personal data never enters a repo

Caught on caudal 2026-08-27 with nothing yet pushed (`git reset --mixed` plus a clean recommit). One
push earlier and it would have been irreversible.

## Proven solution first

One session shipped drag and drop in 2 minutes with @dnd-kit; another hand-rolled it for 25 minutes and
never got it working.

## Filtered views (rtk)

Re-measured against rtk v0.43.0 on 2026-09-05: `rtk grep` on zero matches prints 0 bytes; `rtk grep`
announces "+N more" but never the total (measured 203 of 331 shown), which is how a ripple check reported
clean while the contradicting line sat among the hidden ones (2026-09-02); plain `grep` on a container
json log answered "binary file matches" and printed nothing, which a count pipeline read as zero
(2026-08-28); `sudo rtk <cmd>` fails to stdout so a state check reads it as an empty file. The
2026-08-16 entry "rtk dropped every Registered tunnel connection line from `docker logs`" was retired
2026-09-05 (does not reproduce at 5000 lines), but on 2026-10-11 `docker logs` returned a summary-only
view of a Next.js container that hid 16 app lines.

`pip show graphify` and `python3 -c "import graphify"` both answered "not found" against `/usr` while
the tool was installed and runnable (`graphify 0.9.7`, `~/.local/bin/graphify`), and "not installed"
nearly shipped as a finding (2026-09-07).

## Subagents

The 2026-07-06 sweep (4 agents, ~180k tokens read, ~8k returned) is the model for delegation. On
2026-07-20 parallel agents writing the knowledge repos left a 145-line reference file at 0 bytes and 4
more orphaned, because the Stop auto-push committed a half-done restructure. Opus-plan then Sonnet-exec
for one small edit measured about 5x the cost of doing it inline.

## git add -A in app repos

One sweep bundled 20 unrelated files in recall, 6 in personal-dash, 3 in mycloset (2026-07-12); another
swept 297 `.playwright-mcp/` screenshots into a feature commit (2026-07-15). The Playwright MCP was
removed 2026-09-08; agents now use `chrome-devtools-axi`.

## Router notes

- Animation skills installed 2026-09-06 from emilkowalski/skills (author of Sonner and Vaul, both used in
  4 of our apps). Only Shelf and Aro ship `motion` (verified 2026-10-11).
- `graft ask --source` reached a body-level fact at about 2.6k tokens where graphify could not
  (2026-09-08).
- `review-diff` measured 23k tokens against 1.41M for an agent exploring the repo.
- `banana` and `interior-redesign` removed 2026-10-15; vendor `paseo*` skills removed 2026-10-15, at the
  user's request.
- Answer shape adapted from the an answer-style skill skill, de-conflicted 2026-09-09.
- RULES.md absorbed and replaced the `karpathy-guidelines` and `agent-guidelines` skills (2026-07-06).

## Timer drift (ENVIRONMENT.md "Scheduled jobs")

Measured 2026-09-05 in `loop-worker-prod-1`, six 20-second timers, process otherwise idle:
`overshoot ms = [1740, 20, 1618, 1674, 19, 1684]`. The 15-minute cron in the same container ran 12 s
late at first and drifted to 44 s over 29 hours. Loop's worker did 56 syncs, then 110 consecutive
misses with zero executions across 29 hours (2026-09-03 20:15Z onward), and its 21:30 night plan was
reported missed at 22:12, so a morning opened with no page. `recall-worker-prod-1` had the same failure
for 8 days. node-cron logs `missed execution … Possible blocking IO or high CPU` while the process is idle.

## App table drift

The ENVIRONMENT.md app table drifted for about six weeks carrying a "verified" stamp while four stacks
ran undocumented; `wrap-mvp` and `fisio` were prototypes deleted 2026-09-02 (containers, volume
`wrap-mvp_mvp_pgdata`, and both repos, which had no remote). The 2026-10-15 audit found 32 doc-versus-reality
mismatches, nearly all duplicated facts. That is why live facts now come only from the generated FLEET.md.

## Context costs

`ha-mcp` cost 1,115 context tokens in every session until it moved off the always-on scope (2026-09-15);
the four claude.ai connectors cost 128 per turn together, so they stay. A Claude agent exploring a repo to
review a diff measured 1.41M context tokens over 24 turns; `review-diff` (the diff inline, one turn, no
tools) measured about 18k. Bare-session floor: 6.4k lean versus 36.9k normal. `chrome-devtools-axi`
replaced the Playwright MCP on 2026-09-08: about half the input tokens, cost a wash. Paseo's Claude route
was measured 2026-09-14 to draw from the plan (usage credits are off, so a disallowed route errors
instead of billing). `graft` was adopted 2026-09-08 for "how does the code work" questions.

## claude-config auto-push

A crashed git process left an empty `.git/index.lock` in `~/.claude`; every `git add` failed and
claude-config sat uncommitted for two days (found 2026-10-15). The auto-push script now clears a stale
lock when no git process runs.

## rtk details (RTK.md)

- `rtk grep` measured 203 of 331 matches shown, announced only as "+24 more files"; a ripple check was
  declared clean on 2026-09-02 while the contradicting line sat among the hidden ones.
- Plain `grep` on a container json log answered "binary file matches" with no output (2026-08-28), and a
  count pipeline read it as zero ("never registered").
- `sudo rtk <cmd>` printing `sudo: rtk: command not found` to stdout made a state file read as empty,
  "unset" (verified 2026-07-17).
- On 2026-10-11 `docker logs <c> 2>&1 | tail` on a Next.js prod container returned only a `Log Summary`
  block (`0 errors... 0 info messages`) while 16 app lines existed. Separately, `docker logs` measured full
  passthrough at 80, 400, 1000 and 5000 lines (5000 in, 5000 out), which retired the 2026-08-16 claim that
  rtk dropped every "Registered tunnel connection" line.
- `rtk docker ps` printed an honest header (`55 containers`, 20 rows, `+35 more`).
- On 2026-10-19 `npx tsc --noEmit 2>&1 | head` in a checkout whose `npm ci` had failed printed "TypeScript: No errors found" (rtk 0.43.0) while it exited 1: rtk's own tee copy held npx's "This is not the tsc command you are looking for". An agent briefly read it as a green typecheck. Adding `tsc` to `exclude_commands` in `~/.config/rtk/config.toml` did not stop the rewrite of `npx tsc`.

## Reply style replaced caveman (2026-10-15)

Mining 58 past sessions found about 24 round trips where the user had to ask again after a dense options
list or jargon ("i do not understand 1, 2, 4", "what do you mean", "what are the epics thing ?"), even at
caveman's lite level. The user chose to turn caveman's reply style off (`CAVEMAN_DEFAULT_MODE=off` in
settings.json) and use the RULES.md "Reply style" section, built from pstack's technical-writing (STE) and
poteto-mode reply rules. The caveman plugin stays installed only for its `cavecrew-*` helper agents, whose
terse output is read by the main agent, not the user. caveman's own benchmark here (agent-tool-bench
plugin-verdicts.md, 2026-09-06) had already shown higher cost per run with it on.

Update 2026-10-16: the user uninstalled the caveman plugin. The three `cavecrew-*` agents were copied into
`~/.claude/agents/` (tracked in this repo), so nothing that used them changed. The plugin's builder model
override had never applied (agent-tool-bench plugin-verdicts.md); the copy sets `model: sonnet` itself.
