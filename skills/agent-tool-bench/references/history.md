# agent-tool-bench history

## Why the skill exists (2026-09-05)

Adopting a token-saving tool on a vendor's benchmark, and rejecting one on a hand-rolled n=1, both
happened here on 2026-09-05 before this skill existed.

## context-mode rejected on call counts (2026-09-05)

On 2026-09-05 context-mode was rejected here because the agent called its tools **zero times** across
three runs with the tools loaded and named in the system prompt; it used Bash instead. The worked verdict
is in `context-mode-verdict.md`.

## The uncapped router sweep (2026-09-08)

Without a turn cap the agent kept going and completed the fixture's task for 48-75 turns per run. This was
measured 2026-09-08, when an uncapped 15-run sweep drained the 5-hour quota. Details are in
`router-eval/README.md`.

## Grading idea source (read 2026-09-06)

The capability vs regression grading idea was taken from `WorldFlowAI/everything-claude-code`'s `/eval`
(read 2026-09-06; nothing installed from it). The rest duplicates skills we already own, and one of its
hooks blocks writing any `.md` that is not README/CLAUDE/AGENTS, which would break our canonical project
docs.

## Measured verdicts (2026-09-07)

Results live in `plugin-verdicts.md` (caveman, ponytail, gh-axi; and the 2026-09-07 free SKIP verdicts on
graphify/tasks-axi/headroom, each settled by source review, no paid run).

## Map from the old section numbers

Older notes, including `plugin-verdicts.md` and `router-eval/README.md`, cite sections of the previous
single-file `SKILL.md` (for example `../../SKILL.md` section 9, or `agent-tool-bench §6`). They map to the
current files like this:

| old section | now in |
|---|---|
| §0 which question | `SKILL.md`, step 1 |
| §1 where it lives, §2 setup, §3 running | `harness.md` |
| §4 the design limit | `method.md`, chosen versus used |
| §5 adding a condition or task, §6 arm isolation | `harness.md` |
| §7 measured verdicts and method rules | `plugin-verdicts.md` and `method.md` |
| §8 wrong instrument, §9 grading | `method.md` |
