---
name: review
description: >-
  Reviews work with a fresh agent that did not write it: code (a diff, a branch, the uncommitted work) or a
  plan before code (a plan file, a spec, an ADR, a repo's ARCHITECTURE.md against its code). Use when the
  user says "review this", "review this diff", "review my changes", "second opinion", "is this plan sound", "review the
  architecture", "check before merge", or a workflow reaches its review step. NOT for finding the cause of
  a bug (use debugging), proving UI behavior in a browser (use verify-ui-live), or reviewing motion
  (use animate).
---

# Review

Get an independent verdict on code or on a plan, from an agent that did not write it. It prevents three
failures: the author reviewing its own assumptions, a long list of guesses that buries the one real bug,
and an approval that hides what nobody checked.

## Steps

1. **Pick the target.** A plan, a spec, an ADR or `ARCHITECTURE.md` is a **plan** review: read
   `references/plan.md`. Anything else is a **code** review: read `references/code.md`. With no target
   named, review the repo's whole local change: commits on this branch since it left the default branch,
   plus staged, unstaged and untracked work. If there is nothing to review, say so and stop; never swap in
   a whole-repo audit.
   Done when: you can name the target and its exact source (a ref range, or a file path).
2. **Collect what the reviewer needs.** What was asked (the ticket, the plan, `docs/plans/<KEY>.md`), the
   repo rules (`AGENTS.md`; `review-diff` adds the repo's committed `REVIEW.md` files by itself, a subagent reviewer
   gets them pasted from `git show HEAD:REVIEW.md`, never the working copy), and for code the test and typecheck results that already ran. Name the person
   the change affects.
   Done when: each item is a path or a pasted output line, or is listed as missing.
3. **Hand it to a fresh reviewer.** The reviewer never edits files and never delegates or loads this skill
   again. Which reviewer:
   - Code: `review-diff --context <what was asked> --context AGENTS.md` (one turn, no tools; a shell
     command any agent can run, with Claude as the reviewer). Use a fresh
     subagent that may read the repo only for a risky change, where the bug likely lives outside the diff:
     auth, money, a migration on real data, an invariant with many consumers.
   - Plan: a fresh read-only subagent with the brief in `references/plan.md`.
   - No fresh agent available (an agent or harness without subagents): stop and say independent review is
     blocked, unless the user accepts a self-review labeled as one.
   Done when: the reviewer's output is back.
4. **Verify every finding against the files.** A reviewer's finding is a lead, not a verdict. Open the
   cited line, confirm or disprove it, and run a focused check when that settles it (for code, the test
   check in `references/code.md`). Then fix every confirmed finding in the same change, Could fix included,
   with its narrowest check, and grep its bug class for other instances to fix too. Leave a confirmed
   finding unfixed only when it needs the user's decision (ask, with a recommendation), sits in lines the
   change did not touch (Pre-existing below), or its fix would grow the scope the user set (ask). A known,
   fixable gap in a report is unfinished work, not a finding.
   Done when: each finding is marked fixed (with its check's output), dismissed with a one-line reason, or
   left with one of those three reasons.
5. **Report.** In this order:
   1. **Fixed**: each confirmed finding fixed in step 4, by priority, with the place, what triggered it and
      what the person saw, and the check that now passes.
   2. **Left**: each confirmed finding not fixed, with which of the three reasons in step 4 holds; a
      decision for the user carries the options and a recommendation.
   3. **Pre-existing**: confirmed bugs in lines the change did not touch, one line each. They never block
      the verdict; file each to Triage (or HARVEST outside a board repo) instead of fixing it here.
   4. **Dismissed**: every disproved finding with its one-line reason, so the user can overrule it.
   5. For code, two separate lines: **Spec** (does it do what was asked) and **Standards** (does it follow
      the repo rules), each pass or fail with its worst issue. Never blend them.
   6. **Verdict**: `Approve`, `Request changes` or `Blocked`, then **Unverified**: what nobody checked.
   Done when: the reply has every part that applies.
6. **Log it.** Append one tab-separated line to `~/.claude/review-log.tsv`: date, repo, target (`code`,
   `plan` or `architecture`), reviewer (`review-diff`, `subagent` or `self`), reviewer tokens or `?`,
   verdict, confirmed count, Dismissed count. The user reads it to judge whether reviews are worth their cost.
   Done when: `tail -1 ~/.claude/review-log.tsv` shows this review.

## Rules

- **Priority:** **Must fix** (unsafe to ship: security, data loss, broken required behavior), **Should
  fix** (a real defect or reliability risk, or a missing test on a risky path), **Could fix** (a proven,
  limited problem or a simplification with the same result). Style preferences are never findings.
- **Confidence 0-5:** 5 is proven by a test, a run or the exact line; 3 is probable with some runtime
  evidence missing. Never report 0-2: check further or list the area under Unverified.
- **Verdict rule:** any confirmed Must fix or Should fix means `Request changes`; Could fix alone allows
  `Approve`. `Blocked` means the review lacked context, evidence or a reviewer able to judge a risk.
- **Passing checks never approve on their own.** Green tests prove only what the tests assert.
- **A finding dismissed twice for the same reason becomes a line in the repo's `REVIEW.md`** ("Do not report"
  or an evidence rule), committed before the next review, so the reviewer stops raising it.
- **One pass, then stop.** Each fix adds code, and a judgment-based review finds something new every run;
  re-review only the fix, never loop until clean.
- **Two Must fix in a row in one area means the design is wrong.** Stop patching that area: write the
  simplest design that removes the whole class (fail closed, move aside instead of delete, a clean start)
  and take it to the user before more code. Patches on patches took ten passes on one feature (2026-10-26).
- **Name the realistic threat in the reviewer's context** (a helpful formatter or agent, a crash, the user's
  own edits; not a hostile one unless the code faces one), so findings are weighed against it.

## Gotchas

- `review-diff` sees only the diff and the context files, so it reports confident bugs in code it cannot
  see. Step 4 exists for this; never forward its output unchecked.
- A reviewer told to "review the changes" without the diff inline explores the repo and costs about 60
  times more for the same findings (cost floors: `model-tiering`).
- A subagent that can load skills may load `review` again and spawn more reviewers. The brief must say
  "do not delegate, do not load the review skill".

## References

- `references/code.md`: scope commands, the review order and the test check. Read for every code review.
- `references/plan.md`: the plan reviewer's brief, material questions and the "too much" check. Read for
  every plan or architecture review.
- `references/history.md`: where each rule came from, why code and plan share one skill, and the log
  columns.
