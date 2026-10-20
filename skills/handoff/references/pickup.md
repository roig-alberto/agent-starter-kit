# Picking up a handoff

When a session starts from someone else's work: "read HANDOFF.md and continue", "resume where it stopped", "take over
this". The handoff is trusted input: the job is to continue it, not to redo it. Adapted from pstack's session-pickup
playbook (2026-10-16).

1. **Read the trail.** The root `HANDOFF.md`, then the newest dated handoff it names, then the files that one points at
   (the plan, the decision log). When a decision the handoff needs lives only in the last session's replies, extract
   the assistant text from its transcript (`~/.claude/projects/<slug>/*.jsonl`) with a script; never read a whole
   transcript, and never search other projects' transcripts.
   Done when: you can state the goal, the decisions, and the next step the handoff names.
2. **Rebuild the state from git, not from the text.** For every repo in the handoff's tree table: branch, `git status`,
   `git log` since its HEAD, unpushed commits. A tree that differs from the table is the first finding.
   Done when: each repo matches the table or its difference is named.
3. **Name the resume point.** What is done (do not redo it or rerun a repro that already passed), what is pending, and
   the exact next step.
   Done when: the next step is one concrete action.
4. **Recheck only what the next step stands on.** Rerun the one check the handoff quotes for that part (a test, lint, a
   health call). A "passed" in a handoff is a lead, not proof; if it fails now, fixing it comes first.
   Done when: that check's output is in your reply.
5. **Hand the rest to the matching skill** (the router in RULES.md), and open your first reply with where the last
   agent stopped, what you rechecked and its result, and the resume point.
   Done when: the matching skill is loaded and the reply opens with those three facts.
