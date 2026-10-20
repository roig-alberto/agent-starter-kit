# Review history

## 2026-10-16: one skill for code and plans

Built in phase 1 of the skills redo (`~/.claude/SKILLS-REDO-PLAN.md`). Sources, all read on 2026-10-15 and
2026-10-16:

- owainlewis/blueprint (commit 74210b5) `review`: the default scope (branch commits plus staged, unstaged
  and untracked work), the review order, Must / Should / Could fix with confidence 0-5 (0-2 never
  reported), the verdict `Approve`, `Request changes` or `Blocked` plus what remains unverified, and
  "do not approve solely because checks pass".
- blueprint `architecture-review`: trace one real case from input to outcome, material questions as
  Blocking or Important with a recommended answer, and the same verdict set.
- mattpocock/skills `code-review`: two separate verdicts, Spec (the right thing) and Standards (built
  right), never blended, because a blended verdict lets the passing one hide the failing one. Also from
  its docs: a reviewer that can load the skill again fanned out to more than 50 agents in one report, and a
  judgment-based review finds new things on every run, so it never converges.
- addyosmani/agent-skills `code-review-and-quality`: answer "would the tests catch a regression" by
  inverting one condition and running the suite. Changed here to run in a scratch worktree, because the
  user's other uncommitted work shares the tree.

Why one skill and not two (user agreed, 2026-10-16): the shared rules (fresh read-only reviewer, priority,
confidence, verdict, Unverified) would otherwise live in two copies that drift. blueprint keeps them apart
because its skills only run when typed by name; here skills load from plain words, so one skill reads its
target instead.

Why `review-diff` is the default code reviewer: an exploring reviewer cost 1.41M context tokens over 24
turns on one change, and the same change inline in one tool-less turn cost 17.7k (2026-09-15, details in
`model-tiering`). The triage format (Act on at most 5, Dismissed with a reason) moved here from
`model-tiering` the same day; `review-diff` gained `--context` so the Spec and Standards lines have
something to judge against.

## The review log

The user asked (2026-10-16) for a way to tell whether reviews, plan reviews above all, are too much for
what they find. Each review appends one tab-separated line to `~/.claude/review-log.tsv`:

```text
date	repo	target	reviewer	tokens	verdict	confirmed	dismissed
2026-10-16	agent-factory	plan	subagent	41200	Request changes	2	3
```

`target` is `code`, `plan` or `architecture`; `reviewer` is `review-diff`, `subagent` or `self`;
`tokens` is what the reviewer reported, or `?`. The assessment (in the redo plan, phase 7) reads it: the
share of reviews with at least one confirmed finding, and the tokens per confirmed finding, by target. The user then
decides whether plan reviews stay per plan or only run in the weekly architecture review.

## 2026-10-16: agent-agnostic wording

The user asked for skills that name no agent where any agent is meant. The repo rules file is now named
`AGENTS.md` (in every repo here a link to `CLAUDE.md`); the old step read
`review-diff --context <what was asked> --context CLAUDE.md`. "Codex without subagents" became "an agent or
harness without subagents". `review-diff` stays: it is a shell command any agent can run, and its reviewer being
Claude is a fact, not a preference.
