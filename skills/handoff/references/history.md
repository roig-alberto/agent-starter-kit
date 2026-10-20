# Handoff history

## 2026-10-16: dated file plus a root pointer

Measured across the repos on 2026-10-16: ten repos kept dated files in `handoff/` (loop had 20), three
kept a root `HANDOFF.md`, and Agent Factory had both. Its root file had grown a hand-written first line,
"Newer handoff ... read it first", pointing at `handoff/HANDOFF-2026-10-16-0924.md`. shelf's `CLAUDE.md`
hard-coded "`handoff/HANDOFF-2026-10-11.md` (latest, read it first)", which goes stale with the next
handoff. The same day, a handoff about skills work was saved into agent-factory because the session started
there.

The user chose (2026-10-16): each handoff is a new dated file in `handoff/`, never overwritten, and the root
`HANDOFF.md` is a short pointer to the newest one. Rejected: one root file rewritten each time (an
uncommitted older handoff would be lost), and dated files only (every `CLAUDE.md` would need "read the
newest file" wording, and the plan skill already points at `HANDOFF.md`).

The five restart facts (decisions, task status, changed files with tree state, check commands with results,
open questions) came from the skills redo plan, decided 2026-10-15.

## 2026-10-16: the workflow moved into the skills repo

Until 2026-10-16 the workflow lived in `~/.agent-skills-shared/handoff/workflow.md`, linked from both
`~/.agents/skills/handoff/references` and `~/.codex/skills/handoff/references`. That folder was in no git
repo and in no install or rebuild step, so a fresh machine would have had two handoff skills pointing at
nothing. It now lives in this directory, and Codex's `references` link points here.

The `disable-model-invocation: true` flag was removed the same day: the user never types skill names
(measured over every transcript on 2026-10-15), so a skill only the user can start never runs.

The first version was adapted from mattpocock/skills `handoff` (save outside the workspace, suggested
skills, point at artifacts, redact). Two choices differ on purpose: handoffs are saved in the repo, not in
`$TMPDIR`, because the user resumes from the phone in a later session and `/tmp` can be wiped; and the
pending HARVEST entries are listed for the next agent.

The frontmatter line `argument-hint: "What will the next session be used for?"` was removed the same day. It
is Claude-only, shows only when someone types `/handoff`, and fails the skill validator; the workflow still
shapes the handoff around a focus whenever the user gives one.

## 2026-10-16: agent-agnostic wording

The user asked for skills that name no agent where any agent is meant. The skill and workflow now say "any
agent" instead of listing Claude, Codex and OpenCode, and name `AGENTS.md` (the cross-agent name; in every repo
here it is a link to `CLAUDE.md`). The workflow used to say "`~/.claude/HARVEST.md` (or `~/.codex/HARVEST.md`)";
the Codex file never existed (checked 2026-10-16), so there is one inbox for every agent.

## 2026-10-16: prune to the newest 3

Measured the same day: 88 dated handoffs across 11 repos, the oldest from July; Aro and closet held 18 each.
superhuman-mvp tracked 26 MB under `handoff/` (197 PNGs from design hand-off packages) and glow 3 MB of JPGs.
The user chose to keep the newest 3 (a pick, not measured) and to check the rest weekly in the architecture
review. Tracked ones are deleted with `git rm` (history keeps them); untracked or ignored ones (loop,
finance-proj) are never deleted, only listed.
