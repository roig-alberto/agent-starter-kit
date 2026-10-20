---
name: handoff
description: >-
  Saves where the current work stands as a handoff document, so a fresh agent (any agent, in a new session
  or an Agent Factory run) can continue after /clear without the transcript, and picks one up again. Use when
  the user says "handoff", "/handoff", "write a handoff", "hand this to another agent", "save where we are",
  "continue in a new session", "I'm going to clear", or a session is ending with unfinished work; also "read
  HANDOFF.md and continue", "resume where it stopped", "take over this work". NOT for a status update in chat
  or a plan for new work (use plan).
---

# Handoff

Write a handoff so a fresh agent can continue the current work without the conversation transcript. The
behavior lives in one workflow file that every agent reads, so no two agents can drift.

## Steps

1. Read [the handoff workflow](references/workflow.md) completely, then follow it. It holds what the
   handoff contains, where it is saved, and how the root `HANDOFF.md` points at it.
   Done when: every step in the workflow reached its own "Done when".
2. Report the saved path to the user. The next session starts from `HANDOFF.md`.
   Done when: the reply names the new file.

To pick up a handoff instead (a session that starts from one), follow
[the pickup steps](references/pickup.md).

## Rules

- Keep behavioral instructions in `references/workflow.md`, not in this file. An agent with its own skills
  folder links to that same file (Codex: `~/.codex/skills/handoff/`), and a second copy of the steps would
  drift.

## References

- `references/workflow.md`: the full handoff workflow; read it every time this skill writes a handoff.
- `references/pickup.md`: how to continue from a handoff without redoing it; read it when a session starts from one.
- `references/history.md`: why the save convention changed and where the workflow used to live.
