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

## Rounds instead of one question at a time (user, 2026-10-26)

The user asked to adopt Matt Pocock's current `grilling` (mattpocock/skills, MIT): rounds that ask the whole
frontier of the design tree at once, lookups that do not block the other questions, and an end when the
frontier is empty. It replaced the one-question-at-a-time rule of 2026-10-15. The plain-word shape per
question stayed, because what failed in October was jargon without examples, not the number of questions.
Skipped from the same repo: `grill-with-docs` (the `architecture` skill covers ADRs and the glossary) and
`to-questionnaire`.

## 2026-10-27: runs with no user

Agent Factory runs steps and loops with nobody watching, and the skill had no rule for that case (a grep for
"loop", "unattended" and "no user" found nothing). The gotcha "No user is there to answer" splits decisions by
whether they are cheap to undo. Adapted from georgewangyu/GeorgeCodingSkills `grill-me` "Non-interactive runs"
(MIT), rewritten. Its required "Out of scope" line was skipped: step 6 already restates what we do not build.
