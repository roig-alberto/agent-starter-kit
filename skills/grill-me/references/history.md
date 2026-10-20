# grill-me history

## Dense option lists the user could not follow (measured 2026-10-15)

A search of the session transcripts under `~/.claude/projects` found 23 transcript files where the user
wrote "i do not understand" or a close variant. Several came right after an agent listed numbered options
in technical words: "i do not understand 1, 2, 4", "i do not understand 4", and "yes it sounds good but i
do not understand the 2 option". Another asked "what are the changes ... is it going to take more space
more ram?", which the options had not said. The lesson: each question is in plain words, each option says
what changes for the user, and an abstract option comes with a concrete example.

## Sources of the 2026-10-15 rewrite

- The "yes takes the recommendation" wording and "facts are the agent's job, decisions are the user's"
  came from Matt Pocock's `grilling` skill.
- The material-question test (two capable builders would build different things) came from blueprint's
  `architecture-review` skill.
- The hypothesis first, the "if you did not have to justify it" probe, and the list of answers that are not
  a yes came from addy's `interview-me` skill.
