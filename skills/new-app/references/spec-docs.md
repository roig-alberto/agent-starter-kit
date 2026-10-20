# Phase 2: the canonical spec docs

Write these at the project root. Adapt the names to the project's convention, and keep them the single
source of truth.

- **CLAUDE.md**: concise operating context for agents, which **wins on conflict**. It covers the stack,
  hosting, data model, conventions, domain rules, out-of-scope items, and backlog; it is what future
  agents read. It must include a **Facts** block (host port, public hostname, container names) and a
  **Commands** block (exact copy-paste lines: dev up, test, typecheck, db:generate and migrate, redeploy
  prod, backup verify), because lower-tier models guess these wrong unless they are written down. Also
  create **AGENTS.md as a symlink to CLAUDE.md** (`ln -s CLAUDE.md AGENTS.md`) so other agent tools
  read the same contract.
- **IMPLEMENTATION_PLAN.md**: a **decisions table** (every branch and the why), the full data schema, the
  container architecture, a roadmap (v1, v1.5, v2), and a **"Rejected / parked - do not re-litigate"**
  section with rejected approaches in the record format below.
- **DESIGN_BRIEF.md**: product principles, navigation, every screen (zones, components, states), reusable
  components, and an explicit "expected deliverable" list. It must be self-contained enough to hand to a
  design agent. Open it with the **usability principle** from Phase 1 (the one flow that must be
  effortless, and why, especially for an infrequently used app), and include a **"References &
  inspiration"** section: the reference apps, *what to borrow* from each, and any screenshots (saved under
  `ui/refs/`).
- **FEATURES.md**: the **living feature tracker**, derived from the IMPLEMENTATION_PLAN roadmap. List every
  feature and implementation under a version heading (**v1, v1.5, v2-backlog**), each as a checklist row
  with a status marker (`[ ]` todo, `[~]` in progress, `[x]` done) plus a short note and date when it is
  completed. Cover backend engines and worker jobs, not just screens, and keep the rows granular enough to
  act on. This document is **updated every time a feature lands**. It is the single at-a-glance answer to
  "what's built vs left", separate from the IMPLEMENTATION_PLAN roadmap: `FEATURES.md` tracks *progress*,
  the plan captures *decisions*.

**Gate:** the four docs exist, are internally consistent, and the user has reviewed them.

## Decision record format (the two parking lanes)

Record every decision with its rationale and an upgrade path, so a settled question never gets re-argued.

- **Deferred feature** (do later): a Backlog or v2 entry with the *why*, *how to add it later without a
  destructive migration*, and a `FEATURES.md` v2-backlog row.
- **Rejected approach** (will not do, do not revisit): record it deeply enough to close the question. Put
  it in **IMPLEMENTATION_PLAN.md under a "Rejected / parked - do not re-litigate" section** (or inline in
  **AGENTS.md** for a domain rule). Each entry has a **Decision**, a **status** (parked or rejected), a
  **Why not** (concrete enough to close it), a **What would change the answer** (the specific condition
  that reopens it), and an **Upgrade path** (if it can be deferred). Flag settled ones "do not
  re-investigate."

**"What would change the answer" is the load-bearing field.** It turns a future "should we do X?" from
re-arguing the whole thing into a one-line check ("has that condition flipped?"). A note with only "why
not" makes you redo the analysis every time, so always name the trigger condition.
