# plan history

## Renamed from phased-plan (2026-10-15)

The skill was called `phased-plan` until the 2026-10-15 skills redo. Old docs and chats that say
`/phased-plan` mean this skill.

## Where the phase ticket came from (2026-10-15)

The user asked for plans a PM can read on a phone. The ticket shape (What are we building, Why, Done
when, How to check, Out of scope, optional Agent notes), the vertical-slice rule with no "database /
backend / frontend" tasks, one shared contract per task, no unresolved decision inside a task, and the
two-reader check came from blueprint's `plan` skill. The acceptance table where each "done when" has its
own check came from blueprint's `spec` skill. The material-question test came from blueprint's
`architecture-review` skill.

## Rejected: "never write a plan document"

blueprint's `plan` skill returns the plan in chat and never writes a file. Rejected: the user hands work
between sessions and agents through `PLAN.md` and `HANDOFF.md` (Agent Factory runs on exactly that pair),
and a plan in chat is lost at the next `/clear` or compaction.

## Rejected: several questions per round

Matt Pocock's `grilling` asks every question whose prerequisites are settled in one numbered round, and
the old phased-plan allowed up to 4 per AskUserQuestion call. Rejected: the user's standing rule in
`~/.claude/RULES.md` is one question at a time with a recommended answer, and the user lost track of dense
numbered option lists (see the `grill-me` history).
