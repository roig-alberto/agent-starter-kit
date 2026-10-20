# Shared Agent Instructions

Before starting any task, check the scenario router at the end of
`$HOME/.claude/RULES.md` and load the matching skill first. Machine facts such as
paths, apps, and accounts live in `$HOME/.claude/ENVIRONMENT.md`; never guess them.

The imports below preserve Claude Code's automatic loading behavior:

@RTK.md
@RULES.md
@ENVIRONMENT.md

## Dispatching a crew (Paseo)

When the user asks you to **coordinate** rather than implement - the message starts with
`dispatch:`, or they ask you to handle something end to end / run the crew - read
`$HOME/.paseo/DISPATCH.md` and follow it: brief and supervise crew agents in their own
worktrees, run the deterministic gates, and escalate on its ladder instead of editing code
yourself.

Otherwise you are the crew: do the work in front of you and ignore this section. Never spawn
agents for a task you were given directly.
