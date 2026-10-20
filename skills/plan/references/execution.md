# Phase execution (mode 3)

Implement the approved plan one phase at a time, with an approval gate between every phase.

## The loop, per phase

1. **Announce.** State which phase you are starting and its scope, pulled from the plan file.
2. **Implement.** Make only the changes in that phase's scope. Do not pull work forward from later phases,
   even when it is tempting and small, because that is how phases stop being independently reviewable.
3. **Verify.** Run that phase's "How to check" commands. If it fails, fix it before proceeding; never reach
   the gate with a red build or failing tests.
4. **Update the plan file.** Set the phase's status to done and check off the acceptance criteria it
   satisfies. The plan file is the running source of truth.
5. **Gate.** Summarize what changed in this phase (the files touched and what the verification showed),
   then **stop and ask for approval before starting the next phase.** Use AskUserQuestion with the
   options continue, adjust the plan, or stop here.

## Rules during execution

- **One phase per gate, with no silent continuation.** Even if a phase is trivial, stop at the gate. The
  user controls the pace.
- **If reality diverges from the plan, stop and re-plan.** If the plan turns out wrong (a missing
  dependency, an assumption that does not hold, a phase bigger than it looked), do not improvise around
  it. Surface it, update the plan file, and get the user's sign-off on the revised phasing before
  continuing. A plan changing mid-execution is normal and expected; silently deviating from it is not.
- **Keep verification honest.** "It compiles" is not "it works." Run the actual tests or checks named in
  the plan. If a phase has no meaningful verification, that is a smell; say so.
- **Respect project conventions.** Follow the patterns in `AGENTS.md` (the same file as
  `CLAUDE.md`) and the surrounding code (naming, layering, error handling, test style). Do not introduce a
  new way of doing something that already has an established way in the repo.
- **Leave it green.** Reach every gate with the build passing and the tests green. If you cannot, the gate
  message must clearly flag what is broken and why.
- **Reserve expensive actions for milestones.** Iterate on the cheapest honest loop: hot reload and tests.
  Do not rebuild or redeploy the production build after every small change; batch the tweaks and redeploy
  once at a phase boundary or when the user asks to see it. Default to asking *"redeploy now, or after a
  few more tweaks?"* rather than auto-deploying each edit. Commits stay one per coherent unit, on explicit
  request, never one per tweak. Per-edit rebuilds and redeploys are the single biggest avoidable token
  sink.
- **Verify on the cheapest surface that is honest.** Prefer tests and the dev hot reload. If confirming
  the UI genuinely needs a real browser you cannot drive (or the user prefers it), **ask the user for a
  screenshot** instead of burning turns on browser automation. A mocked-up widget is also fine to preview
  a redesign.

## When all phases are done

Confirm every acceptance criterion in the plan file is checked off. Give a final summary: what was built,
which checks pass, and anything deliberately left out of scope (pointing back to the non-goals). Then ask
whether the user wants follow-up work; if so, that is a new plan, not an extension of this one.

## When the session ends mid-plan

Before a `/clear` or a hand-off to another agent, update the plan file's statuses and write a handoff
(the `handoff` skill, which points the root `HANDOFF.md` at it): where things stand, the next phase, and anything the plan file does not say yet.
The next session starts from `HANDOFF.md` and the plan, not from memory.
