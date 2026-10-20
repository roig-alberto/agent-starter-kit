---
name: plan
description: >-
  Turn a feature or a decided brief into a written plan of short, vertical phases, then build it phase by
  phase with an approval gate after each, or hand the plan to another agent. Use whenever the user asks
  to plan, design, or architect a feature, or says 'plan this', 'let's plan', 'make a plan', 'how should
  we implement', 'break this down', 'phased approach', "write the plan", "so another agent can build
  this", "hand this off", or any variation of wanting to think through implementation before coding,
  or invokes /plan or /phased-plan. NOT for the question round alone (use grill-me) or for a small
  feature or bug on an existing app (use one-shot, which calls this skill when the work needs phases).
---

# plan

Act as a skeptical, detail-obsessed architect who makes sure every decision is made before code is
written, then cut the work into short phases the user can read on a phone and approve one at a time. It
prevents wasted work, a hidden decision that an implementing agent guesses, and a plan nobody can follow.

## Context

- Current branch: !`git branch --show-current`
- Current git status: !`git status --short`
- Project `AGENTS.md` (the same file as `CLAUDE.md`): !`cat CLAUDE.md 2>/dev/null | head -50`

## Steps

1. **Interrogate.** Run `grill-me` for the questions: one plain-word question at a time, a recommended
   answer with each, facts looked up by you, decisions asked of the user. Seed it from the checklist in
   `references/interrogation.md` and scan the whole list every time, because the dangerous gaps are the
   ones nobody is thinking about.
   Done when: you can write, without guessing, what is built, what is **out of scope**, what "done" looks
   like as concrete checks, which parts of the codebase it touches, and the riskiest part and how the
   first phase removes that risk.
2. **Get the scope confirmed.** Restate the scope, the non-goals, and the acceptance checks in plain words
   and ask the user to confirm or correct them. A misunderstanding caught here costs one message; caught
   in execution it costs a rewrite.
   Done when: the user said yes to the restated scope.
3. **Clear every open decision.** Read each planned phase and ask: would two capable builders build
   different things here? If yes, it is a decision, so take it back to the user. Never hide an unresolved
   decision inside a phase.
   Done when: the plan's "Open decisions" section says None.
4. **Write the plan to a file**, never only to chat: `PLAN.md` at the repo root, or the repo's own
   convention (for example `.agents/plans/<feature-name>.md`). The file survives context compaction and is
   the source of truth for the whole build. Use the template, the phase ticket shape, and the cutting rules
   in `references/plan-format.md`. Read `CODEMAP.md` and `ARCHITECTURE.md` first when the repo has them, and
   add a phase task to update them when the plan moves ownership, data, a boundary or a main folder.
   For a hand-off plan or one with three or more phases, then run `review` on the plan file and settle
   each Act on item (fix it, or take it to the user as a decision) before step 5.
   Done when: the file exists, every phase passes the two-reader check in `references/plan-format.md`,
   and a required plan review ended in `Approve`.
5. **Get explicit approval before any code.** Show the phase titles with their "What are we building?"
   lines, ask whether the phasing, order, and scope are right, and revise the file until the user approves.
   Done when: the user approved the plan file.
6. **Build one phase per gate, or hand off.** If you build it, follow the loop in `references/execution.md`:
   implement only that phase, run its "How to check", tick it in the plan file, summarize, and **stop and
   ask for approval**. If another agent builds it, finish the hand-off section in
   `references/plan-format.md` and write a handoff (`handoff` skill) whose next step names the plan.
   Done when: each built phase is ticked with its check output, or the hand-off plan exists and
   `HANDOFF.md` points at a handoff that names it.
7. **Finish.** Confirm every acceptance check in the plan file is ticked. Summarize what was built, which
   checks pass, and what was left out (pointing back to the non-goals). Follow-up work is a new plan, not
   an extension of this one.
   Done when: the summary is in the reply and the plan file shows every phase done.

## Rules

- **Cut vertical slices, each a working result.** A phase delivers something a person can see or run,
  through every layer it needs; never "database", "backend", "frontend" phases. A thin end-to-end slice
  verifies honestly at every gate and can be built by a separate agent or worktree.
- **Write each phase as a short ticket a PM can read on a phone in under a minute.** "What are we
  building?" and "Why?" use no IDs, file names, or jargon; the user reads plans on a phone.
- **Settle each shared contract in one phase.** A shared contract (an API shape, a table, an event name)
  is decided in exactly one phase, and later phases depend on it, so two phases never answer the same
  question differently.
- **Be adversarial and push back on bad ideas.** If the user says "add a settings page", ask what
  settings, who can access them, what happens to existing users, what the validation rules are, and what
  the error states look like. If a design has a flaw, say so directly, explain why, and propose an
  alternative; the user explicitly wants disagreement when it is warranted.
- **Calibrate the depth to the size of the work.** A one-line copy change needs no concurrency analysis;
  a new payments flow needs all of it. If the request is genuinely trivial, say so and offer to skip
  straight to implementation instead of performing ceremony.
- **Park tempting adjacent features in the Non-goals or backlog with a one-line reason.** That keeps the
  current work focused while preserving the idea.
- **Make each phase independently verifiable and leave the codebase working.** No phase depends on a
  later phase to compile or pass tests.
- **Build additively and never throw work away.** Each phase is reused by the next; never build a
  throwaway version just to make a release smaller.
- **Stop at every gate, with no silent continuation.** Even a trivial phase stops, because the user
  controls the pace.
- **Stop and re-plan when reality diverges from the plan.** Surface the divergence, update the plan file,
  and get sign-off on the revised phasing. A plan changing mid-execution is normal; silently deviating
  from it is not.
- **Always write the plan file.** The user hands work between sessions and agents through `PLAN.md` and
  `HANDOFF.md`, so a plan that lives only in chat is lost at the next `/clear`.

## Gotchas

- **A phase has no meaningful verification.** That is a smell; say so and find a real check, because "it
  compiles" is not "it works."
- **A phase reads like a work order ("add column X, wire endpoint Y").** Rewrite "What are we building?"
  as the result the user will see, and move the mechanics to Agent notes.
- **You are rebuilding prod after every small change.** Per-edit rebuilds and redeploys are the single
  biggest avoidable token sink; batch the tweaks and ask "redeploy now, or after a few more tweaks?"
- **Confirming the UI needs a browser you cannot drive.** Ask the user for a screenshot instead of
  burning turns on browser automation.

## References

- `references/interrogation.md`: the full interrogation checklist (edge cases, data model, authz,
  concurrency, limits, failure and success of outside calls, and more) to scan in step 1.
- `references/plan-format.md`: the plan file template, the phase ticket shape, the acceptance table, the
  hand-off section, and the rules for cutting phases.
- `references/execution.md`: the per-phase loop and the rules that hold during execution.
- `references/history.md`: where the ticket shape came from and which outside ideas were rejected.
