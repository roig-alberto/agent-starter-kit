---
name: architecture
description: >-
  Writes and maintains a repo's four agent-facing docs: ARCHITECTURE.md (parts, data model, flows, a
  diagram, and architecture decision records with the alternatives that lost), GLOSSARY.md (the project's
  words), CODEMAP.md (where each part lives, so an agent opens the right file first) and REVIEW.md (what a
  reviewer must flag or skip). Use when a repo has
  none of them, when a change moves ownership, stored data, trust boundaries, deployment or a main folder,
  or on "write the architecture", "add an ADR", "why did we choose X", "glossary",
  "code map", "help agents find their way in the code", "write the REVIEW.md". NOT for one feature's plan (use plan), a new app
  from scratch (use new-app, which calls this skill), or a dated log of every product choice (the repo's
  decision log).
---

# Architecture

Every agent that opens a repo cold spends its first turns rediscovering the same map: what the parts are,
why they are built this way, what the project's words mean, and which file to open. Those turns cost tokens
and produce wrong guesses, such as "improving" a choice that was made on purpose. This skill keeps four
short root files that answer those questions in one read and stay true because a script checks their paths.
The fourth, REVIEW.md, stops reviewers from missing this repo's real failures while flagging noise.

## The four files

| File | Answers | Shape |
|---|---|---|
| `ARCHITECTURE.md` | What the system is and why it is built this way | `references/doc-shapes.md` part 1 |
| `GLOSSARY.md` | What the project's words mean | `references/doc-shapes.md` part 2 |
| `CODEMAP.md` | Where each part lives and where to start a change | `references/doc-shapes.md` part 3 |
| `REVIEW.md` | What a reviewer must flag, at what level, and what to skip | `references/doc-shapes.md` part 4 |

`AGENTS.md` (the same file as `CLAUDE.md`) stays the entry point (stack, rules, commands) and links the
four. The repo's dated decision log (for example `docs/DECISION-LOG.md`) stays the full history; ADRs are
the curated few that shape code.

## Steps

1. **Read before writing.** Read `AGENTS.md`, `IMPLEMENTATION_PLAN.md`, the decision log, the schema and the
   entry files, and list the main folders. Claims about the code come from the code, never from memory.
   Done when: you can name every main folder's job and the source of truth for data.
2. **Write ARCHITECTURE.md.** Summary, a Mermaid diagram of parts, stores and what flows between them,
   responsibilities, data model, main runtime flows, numbered system rules, then the ADRs. Mark what is
   decided and what is built separately. If `IMPLEMENTATION_PLAN.md` has Architecture or Data model
   sections, move them here and keep each heading with a one-line pointer, so numbering survives and the
   facts live in one place. The data model also names stores outside the database (files, worktrees,
   credential stores) in one short paragraph.
   Done when: the diagram parses (a pinned `mermaid` in the scratchpad, or GitHub's preview) and every rule
   says how it is enforced or checked.
3. **Pick the ADRs.** Write one only when all three hold: the choice is hard to reverse, a newcomer would
   be surprised by it, and real alternatives were weighed. Aim for 10 to 20. Each ADR names the
   alternatives considered and why each lost, the cost of the choice, what would change the answer, and the
   decision-log IDs it came from, with the date when the log has one. Four to eight lines per ADR.
   Done when: a reader can explain why the code is not built the obvious other way.
4. **Write GLOSSARY.md.** One entry per project word a newcomer would misread: the term, a one or two
   sentence meaning in user terms, the words to avoid for it, and how it relates to other terms. No
   implementation detail.
   Done when: every capitalised or invented term used in ARCHITECTURE.md and CODEMAP.md is defined.
5. **Write CODEMAP.md.** Per main area: what it owns, its entry file, the key functions or components by
   name, and "to change X, start at Y". Then trace the two or three main flows across files. Names, not line
   numbers, because line numbers rot within days.
   Done when: an agent asked to change a common thing can open the right file without searching.
6. **Write REVIEW.md.** The four sections in `references/doc-shapes.md` part 4: what Must fix means here,
   what to always check (one line per system rule a diff can break, plus real bugs from the decision log or
   `git log --grep=fix`), what not to report (generated paths, what CI already enforces), and the nit cap
   and evidence rule. Add a REVIEW.md in a sub-folder only for a risky area (money, auth, migrations).
   Reviewers read the committed copy, so commit it before the review that should use it.
   Done when: every "always check" line names a rule or a past bug, and the file is under about 60 lines.
7. **Check the paths.** Run `python3 ~/.agents/skills/architecture/scripts/check-doc-paths.py <repo>`; it
   fails on any path in the four files that does not exist. Wire the same check into the repo's test
   command when the repo has one, so a moved file fails the build instead of misleading an agent.
   Done when: the script exits 0.
8. **Link and fix what you made stale.** Add the four files to `AGENTS.md`'s reading list, and fix every
   line elsewhere that your move made wrong (a reading list that still says "architecture is in
   IMPLEMENTATION_PLAN.md", a code comment pointing at a moved section). Agent Factory's plan prompt already
   tells agents to read `CODEMAP.md` first; check it, do not add it again.
   Done when: `AGENTS.md` names all four and a grep for the moved section names finds no stale pointer.

## Rules

- **Keep each file short: ARCHITECTURE.md under about 450 lines with its ADRs, GLOSSARY.md and CODEMAP.md under
  about 200, REVIEW.md under about 60.**
  They are read on every cold start, so length is a cost on every task.
- **Point at files, never copy code or schemas.** A copy drifts; a path fails the check when it moves.
- **Update in the same change that breaks them.** A change to ownership, stored data, a trust boundary,
  deployment, a main folder or a domain word updates the matching file in the same commit (a new system rule
  adds its REVIEW.md "always check" line); `plan` and
  `one-shot` close-out ask for it.
- **"Decided" is not "built".** Label proposed or missing parts, because an agent trusts what the doc says
  exists.
- **Live facts stay out.** Ports, containers and hostnames are in `~/.claude/FLEET.md`.

## Gotchas

- An ADR list that grows to every small choice reads as noise. Keep the three-test filter; the rest stays
  in the decision log.
- A diagram that only shows boxes connected says nothing. Label each arrow with what moves.
- The path check fails on a model id, a branch pattern or a bare `.test.ts`: it treats any backticked token
  with a slash or a file extension as a path. Put a placeholder in it (`<KEY-n>`) or drop the backticks.
- A code map written from memory names files that never existed. Write it from a directory listing and run
  the path check.

## References

- `references/doc-shapes.md`: the exact sections of each file, an ADR template and a glossary entry template.
- `references/history.md`: where these ideas came from and the user's decisions behind them.
- `scripts/check-doc-paths.py`: the path check used in step 6.
