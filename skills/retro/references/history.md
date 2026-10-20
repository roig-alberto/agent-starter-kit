# Retro history

## 2026-10-16: built (skills redo, phase 3)

Adapted from mattpocock/skills `retro` (MIT, commit 49dd158): suggest improvements to the agent's environment,
not the code; the categories navigation, automated checks, coding standards, global `AGENTS.md`, tool economy,
no-ops and information access; a mechanical violation gets a deterministic check, never a rule; every candidate
points back to a specific moment; `AGENTS.md` should get shorter over time. Changed on purpose: Matt's
`disable-model-invocation` flag is dropped (the user never types skill names), its `writing-for-agents` step is
`knowledge-authoring` here, and its "coding standards for the reviewer" category maps to the `review` skill's rules.

Added from this box, all user decisions of 2026-10-16:

- HARVEST processing moved here from `knowledge-authoring` section 4, so one skill owns the inbox. The five-question
  filter moved unchanged into `references/harvest.md`. Measured that day: 64 pending, 54 of them from the last 7
  days, 269 processed, the file 259 KB.
- The memory trim: a general preference moves to RULES.md, because memory loads only in the folder it was saved in
  (11 memories in 5 folders; the PM-and-architect preference lived only in agent-factory's).
- The always-loaded file check: per-repo `AGENTS.md` ran from 84 to 965 lines (mycloset 965, finance-proj 657).
- The routing check: phase 2 built `router-eval`, so a missed trigger can be proven with a real run.
