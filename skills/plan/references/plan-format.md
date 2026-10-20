# Plan format (mode 2)

Write the plan to a file, not just to chat, so it survives context compaction and serves as the source of
truth across the whole execution. Use `PLAN.md` at the repo root, or `.agents/plans/<feature-name>.md` if
the project keeps plans there. A repo with its own convention (for example a long-lived `PLAN.md` with a
section per slice, plus a `HANDOFF.md` for "where things stand right now") keeps it.

## Template

```markdown
# Plan: <feature name>

## Goal
One or two plain sentences. What this delivers and why.

## Non-goals
Explicit list of what this does NOT do, each with a one-line reason. Prevents scope creep.

## Acceptance
- [ ] AC-1: Concrete, checkable statements of "done", each with a stable ID
(Use the acceptance table below instead when the feature has consequential decisions.)

## Affected areas
Files, modules, tables, endpoints this will touch, and the `ARCHITECTURE.md` rules (RULE-n) it must keep or
proposes to change.

## Open decisions
None. (A plan with an open decision is not ready for approval.)

## Phases

### Phase 1: <plain action and result>
**Status:** not started

**What are we building?**
One to three short sentences: what is missing or wrong today, and what works after this phase.

**Why?**
One or two sentences: the practical value to the user.

**Done when**
- Three to seven observable results.

**How to check**
- Exact commands (e.g. `mvn -pl module test`, a specific test class, a manual curl) and any manual
  check automation cannot cover.

**Out of scope**
- Related work this phase is likely to absorb by mistake.

**Agent notes** (only when another agent builds it without this conversation)
- Depends on: <phase titles, or None>
- Files and paths, the wireframe frames it must match, the decisions and constraints specific to this
  phase, and the failure behavior. Not the whole plan again.

### Phase 2: <plain action and result>
...
```

## The phase ticket

The user is a PM who reads plans on a phone. Each phase must be understood in under a minute from its
title, "What are we building?", and "Why?".

- The title names an action and its result: "Retry a failed nightly check once", not "Retry logic".
- "What are we building?" and "Why?" use no requirement IDs, file names, function names, or jargon. Say
  what a person would notice: "sending the same message twice creates one card", not "make it
  idempotent".
- "Done when" lists results someone can observe, plus any internal rule that must hold.
- "How to check" names exact commands. Never invent a command for code that does not exist yet; describe
  the scenario and the expected result instead.
- Keep the first five sections short, about 250 words or less. Do not repeat a fact in two sections. No
  filler words such as "robust", "seamless", or "comprehensive".
- Add "Agent notes" only when another agent builds the phase blind. When you build it yourself, the
  Affected areas list is enough.

## The acceptance table (for consequential decisions)

When a feature carries decisions that change data, security, money, or what the user sees, write the
acceptance as a table so each result has its own proof:

```markdown
| ID | Done when | How to check |
|---|---|---|
| AC-1 | A failed run retries once and then shows "failed" on the card | `npm test -- retry.test.ts`, then stop the network and watch the card |
```

Every acceptance line gets an `AC-n` ID, in the checklist or the table. Verify and review report each ID with its
proof (Pass, Fail or Unverified), so a check that went missing shows. Never renumber or reuse an ID, and never reword a
check to match the code: a changed check is a changed spec, which the user approves.

## The two-reader check

Read each phase twice before showing the plan.

1. **Human pass.** From the title and the first two sections alone, could the user explain what will
   change and why? If not, rewrite them in plainer words.
2. **Agent pass.** Could a fresh agent find what it needs, see what it depends on, build it, and prove it
   without asking a product or design question? If not, a decision is missing: take it back to the user.

## Hand-off plans ("so another agent can build this")

When another agent will build the plan without this conversation:

- Every phase gets Agent notes.
- The plan header lists the wireframe paths and which frame each phase matches, the design docs
  (`DESIGN_BRIEF.md`, `DESIGN_TOKENS.md`), the project's Commands block or where it lives, and the
  conventions the agent must follow.
- The handoff that `HANDOFF.md` points at says where things stand and names the plan and the next phase to build.
- Each phase is small enough for one agent run and one focused review.

## How to phase the work

- **Each phase must be independently verifiable and leave the codebase in a working state.** No phase may
  depend on a later phase to compile or pass tests.
- **Order by risk and dependency.** Tackle the riskiest, most uncertain piece first, usually the data
  model or the core integration, so you fail fast while change is cheap. Scaffolding and polish come last.
- **Additive, never throwaway.** Order the build by dependency into additive phases where **nothing is
  thrown away, and each phase is reused by the next.** Ship at coherent points, but **never build a
  throwaway or temporary version of something just to make a release smaller.** If shrinking a phase
  would force building the real thing twice, do not shrink it: build it once and let later phases
  *extend* it. Splitting is correct only when the earlier piece is a permanent foundation the later one
  builds on (for example a manual-entry path now and a later import that writes into the *same* table, or
  a core engine now and a new type plugged into it later). Prefer this over artificially small releases
  that create rework.
- **Cut vertically, not horizontally.** Prefer a thin end-to-end slice (one feature through UI, API, and
  schema, working) over layer phases (all schema, then all API, then all UI). Vertical slices verify
  honestly at every gate, ship value earlier, and stay independently grabbable, which is what makes
  parallel subagent or worktree execution possible. Horizontal cuts are right only for true foundations
  (the scaffold, a migration). Never name a phase "database", "backend", or "frontend".
- **One shared contract, one phase.** A shape that several phases use (an API, a table, an event) is
  settled in one phase; the others list it under "Depends on".
- **Keep refactoring apart from behavior changes** when mixing them would hide what changed.
- **Keep phases small.** A phase should be reviewable in one sitting. If it has more than a handful of
  meaningfully distinct changes, split it.
- **Make migrations their own phase** when a data model change is involved, and state the migration order
  explicitly: add the column, backfill, switch the reads, then drop the old one.
- **Call out the verification per phase**, not just at the end. Each phase carries the command that
  proves it.
- **No scaffolding or cleanup phase without a checked result.**

After writing the plan file, show the user the phase breakdown and **get explicit approval before writing
any code.** Ask whether the phasing, ordering, and scope are right, and revise the file until they approve.
