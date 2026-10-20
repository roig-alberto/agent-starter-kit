---
name: one-shot
description: >-
  End-to-end loop for implementing a feature or fixing a bug on an EXISTING app (Aro, Caudal,
  closet, any repo here) in one session, from clarifying the ask to verified close-out. This is the
  default entry point: use when the user asks to add, build, change, implement, or fix something in
  an existing project, such as "add X", "implement Y", "build Z into the app", "change how...",
  "fix the bug where...", "/one-shot", even without naming this skill. NOT for brand-new apps (use
  new-app), for planning alone (use plan), or for pure questions and analysis.
---

# one-shot

Take a feature or a bug fix on an existing app from the ask to a verified finish in one session. It owns
the order of the work and calls the specialist skills for each part, so nothing (a migration, a new
secret, a backup implication, a missing test) gets skipped.

Run the steps IN ORDER. Never skip a step because the task "looks small"; write "step N: nothing applies"
instead, so skipping is a decision, not an accident. Each step names its exit artifact; produce it before
moving on.

## Steps

0. **Load the ground truth before any opinion.** Read the project's `AGENTS.md` (the same file as
   `CLAUDE.md`; the Facts and Commands blocks), `FEATURES.md`, and `CODEMAP.md` and `ARCHITECTURE.md` when they exist. If the repo lacks them, flag it (the doc contract is in RULES.md) and
   reconstruct them minimally. For an area you have not mapped, spawn a read-only subagent (Explore or
   `cavecrew-investigator`) per area, all in ONE message, returning file:line refs, not prose. When the
   feature touches an existing DOMAIN CONCEPT (pairing, dedup, categorization, reconciliation, matching,
   scoring), the recon brief MUST ask "is there already a function that does this?" and grep the concept,
   not just where the data lives.
   **Exit:** you can state the stack, the container names (see `~/.claude/FLEET.md`), and the exact test
   command.
1. **Clarify with `grill-me`**, scoped to this feature, with NO cap on questions. Seed it from the
   checklist in `plan` (`references/interrogation.md`) plus anything in the ask that has two readings.
   When the change calls anything outside the app (an API, a model, a CLI, a push, an alert), always ask its
   "Limits, failure and success" questions: rate limit or budget hit, failure and retry, what success moves.
   Skip it ONLY for genuinely mechanical asks (a typo, a copy change, an unambiguous one-liner), and even
   then open your reply with an **"Assumptions:"** line so a wrong guess costs one correction.
   **Exit:** a confirmed scope, explicit non-goals, and done-criteria.
2. **Run the implication sweep.** Walk EVERY line of the table in `references/implication-sweep.md` and
   answer each with "yes, load the skill" or "no".
   **Exit:** a short implications list in your reply ("schema: yes - new table + migration; secrets: no;
   design path: match-existing; ...") BEFORE writing code. The table is the step.
3. **Plan, sized to the change.** For 3 files or fewer, no migration, and no fork that survived step 1,
   write an inline mini-plan of steps with the check per step and proceed. Run `plan` instead when the
   work is bigger, has a migration, needs phases, or another agent will build it; a migration is always
   its own phase. A change that keeps behaviour (a refactor, a rename, moving code) follows
   `references/refactoring.md`: pin the behaviour first.
   **Exit:** written steps, each with its check.
4. **Implement.** Follow `backend-patterns` and the frontend skills the sweep named. For a bug fix, run
   `debugging` FIRST (reproduce before fixing), then add a regression test with `testing`. Keep the scope
   surgical: every changed line traces to the scope from step 1.
   **Exit:** the change is in the tree and the narrowest check for each edit passed.
5. **Verify with evidence, never "should work".**
   - Run the project AGENTS.md **Commands** block: tests and typecheck, and **the FULL suite, not just the
     area you touched**, because full runs catch drift that landed between sessions.
   - Tests and any write path: `testing` (prove a DB write or migration on a throwaway database).
   - UI: the repo's `.claude/skills/verify-<app>/` project skill when it exists, `verify-ui-live`
     otherwise (measure the DOM at phone width).
   - Independent review: load `review`; it hands the diff to `review-diff` rather than a reviewer that
     explores the repo.
   Paste the decisive output lines. Label each check Pass, Fail or Unverified with its evidence, failures
   first, and name each plan `AC-n` it proves. A failing check means step 4 is not done, so loop instead of
   reporting.
   **Exit:** every check labeled with its decisive output line, all Pass or flagged.
6. **Close out** with the checklist in `references/close-out.md`: update `FEATURES.md` and the project
   AGENTS.md, run the harvest check, record feature-level decisions, report, offer to stop the dev
   environment, and offer (never auto) a commit and a prod redeploy.
   **Exit:** every checklist line done or answered "nothing applies".

## Rules

- **Never silently invent a new visual direction on an app that has one.** Match the existing screens, or
  take the design-path fork in `references/implication-sweep.md`.
- **Always request hi-fi STATIC wireframes, one frame per screen state, never an interactive or clickable
  prototype,** when you hand UI to a design agent. It is a standing user rule, and the exact wording lives
  in `frontend-design`.
- **Use the narrowest honest check per edit while iterating:** one test file (`vitest run <file>`), hot
  reload plus one DOM measurement, or a single curl. Do NOT run the full suite per tweak, and never rebuild
  prod per edit; batch and redeploy once at the end if asked. The FULL suite runs exactly once, in step 5.
- **Never step around a pre-existing red check silently.** Fix it if it is small (the quality bar),
  otherwise flag it as a finding in your report. "Unrelated, so I ignored it" is how drift sits unnoticed.

## Red flags

- **You are about to hand-roll a domain concept.** The codebase very likely already solves it; grep the
  concept name and its synonyms before writing a new function (the Caudal incident in
  `references/history.md`).
- **A check was red before your change and you are moving on.** That is how the typecheck drift in
  `references/history.md` sat unnoticed.

## Gotchas

- **A dev container is still running after the task.** Idle hot-reload dev containers leak GBs of RAM on
  this box (see `fleet-ops`), so remind the user and offer `docker compose stop <dev services>`. Never
  auto-stop it, because the user may still be looking.

## References

- `references/implication-sweep.md`: the step 2 table and the design-path fork for UI changes.
- `references/close-out.md`: the full step 6 checklist, including the harvest check.
- `references/refactoring.md`: the steps for a change that keeps behaviour (pin, delete first, no shims, prove
  unchanged). Read it in step 3 when the change is a refactor.
- `references/history.md`: the incidents behind the domain-concept recon rule and the pre-existing-red
  rule, the old skill names, and why the review goes through `review-diff`.
