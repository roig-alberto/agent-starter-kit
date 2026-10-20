# Doc shapes

Use only the sections that say something about this repo. Every path is written in backticks and relative to
the repo root, so `scripts/check-doc-paths.py` can check it.

## Part 1: ARCHITECTURE.md

```markdown
# <App> architecture

> Read with GLOSSARY.md (words) and CODEMAP.md (where things live). Live facts: ~/.claude/FLEET.md.

## Summary
Two to five sentences: what the system is, its main parts, the source of truth for data.

## Diagram
A Mermaid flowchart: users, outside systems, components, data stores. Label every arrow with what moves.
Group trust boundaries with subgraphs. Add one caption sentence explaining the main flow.

## Parts and responsibilities
One bullet per part: what it owns, what it does not own, which way dependencies may point.

## Data model
Core entities, relationships, identifiers, lifecycle, and the rules the database enforces. Point at the
schema file instead of copying it.

## Main flows
Two to four flows in execution order, including what happens on failure, retry and restart, and when a rate
limit, usage window or budget runs out before or during the flow (the questions are in `plan`,
`references/interrogation.md`, "Limits, failure and success").

## System rules
- RULE-1: <the rule>. Enforced by <code, constraint or test>; checked by <command or test name>.

A rule ID is permanent: plans, reviews and `AGENTS.md` cite it. Never renumber or reuse one; a dropped rule
keeps its line as `RULE-n: removed <date>, <why>`.

## Status
What is decided but not built, and what is built differently from the plan.

## Decisions (ADRs)
### ADR-1: <short decision>
- Context: the problem and the constraint that forced a choice.
- Decision: what we do.
- Alternatives considered: each option and the reason it lost.
- Cost: what this choice makes harder.
- Would change if: the condition that reopens it.
- Source: decision-log IDs (for example D14, D31), with dates when known.

Keep each ADR to four to eight lines; the decision log holds the long story.
```

## Part 2: GLOSSARY.md

```markdown
# <App> glossary

## Terms
- **Task**: one piece of work on the board, owned by one repo. A task runs through a pipeline.
  _Avoid_: ticket, issue (except when quoting Linear).
- **Step**: one stage of a pipeline, run by one agent session or by plain code.
  _Avoid_: stage (that is the task's column on the board).

## Relationships
- A **Pipeline** has many **Steps**; a **Task** has at most one active **Pipeline**.

## Ambiguities resolved
- "plan" meant both the step and its output. Resolved: the **Plan step** writes a **Plan**.
```

Use a bullet per term, because consecutive bold lines merge into one paragraph when rendered. Terms are in
user words, without implementation detail. Sort terms alphabetically or by flow, whichever
reads better for this project.

## Part 3: CODEMAP.md

```markdown
# <App> code map

Read this before searching. Paths are relative to the repo root.

## Areas
### <Area name> (`path/to/folder/`)
- Owns: ...
- Entry: `path/to/entry.ts` (`mainFunction`)
- Key pieces: `file.ts` (`functionA`, `functionB`) - what each does in one line.
- To change <common thing>: start at `file.ts` `functionA`.

## Flows across files
### <Flow name>
1. `a.ts` `start()` creates ...
2. `b.ts` `run()` ...

## Tests and checks
Where tests live, the command, and which test file covers which area.
```

## Part 4: REVIEW.md

The format follows Claude Code's Code Review docs (code.claude.com/docs/en/code-review-customize), adapted to our
levels (Must fix, Should fix, Could fix). Reviewers here read it through `review-diff` and Agent Factory's Review
step, always from the committed copy, so a change cannot soften its own review.

```markdown
# Review instructions

## What Must fix means here
<The failures that matter in this repo, in user terms: it loses data, it leaks a secret or personal data, it runs
code without approval, it shows a wrong amount. Style, naming and refactoring are Could fix at most.>

## Always check
- <one line per system rule a diff can break, with its ID: "RULE-4: each task runs in its own worktree">
- <one line per bug class this repo has shipped before, from the decision log or fix commits>

## Do not report
- Anything CI already enforces: <the repo's lint, typecheck, test commands>
- Generated files: <paths, for example drizzle/meta/*.json, dist/>

## Findings
- At most 3 Could fix items per review.
- A behavior claim needs a file:line citation, never an inference from a name.
- Mark a bug in lines the change did not touch as Pre-existing.
- Start the summary with the count, or say plainly that there is nothing to fix.
```

A sub-folder REVIEW.md (for example `services/billing/REVIEW.md`) adds checks for changes under that folder only.
A finding the user dismissed twice for the same reason becomes a "Do not report" or evidence line (skill `review`).
