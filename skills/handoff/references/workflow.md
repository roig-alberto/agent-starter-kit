# Handoff workflow

A handoff lets a fresh agent (any agent, in a new session or an Agent Factory run) continue the work after `/clear`
without the transcript. It prevents three failures: the next session re-argues a decision that was already
made, trusts a "done" that was never checked, or cannot find the newest handoff among old ones. This file is
the single source for every agent; each agent's handoff skill points here.

## Steps

1. **Find the home and the focus.** The home is the root of the git repo the work happened in
   (`git rev-parse --show-toplevel`), not the directory the session started in. When the work spanned
   repos, use the repo where most changed and list the others in the tree-state section. If the user named
   what the next session is for, shape the whole handoff around that goal.
   Done when: you can say the home path and the next session's goal in one sentence.
2. **Collect the five restart facts with read-only commands, never from memory.**
   1. Decisions made this session, each with its why and where it is recorded (a decision-log ID, an ADR,
      a plan file). A decision recorded nowhere else goes into the handoff in full.
   2. Task status: each task is done and verified (with the evidence), done but unverified, in progress, or
      only proposed. Never let a proposal read like finished work.
   3. Changed files and tree state, per repo touched: branch, `HEAD`, `git status --short`, ahead or behind
      its upstream, and whether the change is deployed.
   4. Check commands and their results: the exact command lines that ran, the decisive output line, and
      when. A check that has not run since the last change is marked "not re-run".
   5. Open questions and blockers, each with your recommended answer.

   Then write the exact next step as one command or one action.
   Done when: each of the five has entries or says "none", and the next step is written.
3. **Point at files instead of copying them.** Reference plans, `PLAN.md`, the decision log, ADRs, issues,
   commits, diffs and earlier handoffs by path, URL or commit hash. Copy only what lives nowhere else.
   Done when: no paragraph repeats the content of a file that exists.
4. **Check HARVEST.** First add any lesson from this session to `## Pending` in `~/.claude/HARVEST.md`, the one
   inbox for every agent. Then list the pending entries that touch this work in the Harvest section.
   Process them only when that is already in scope; otherwise leave them for the next agent's close-out.
   Done when: the Harvest section lists the entries or says "none".
5. **Name only skills that exist.** In a Suggested skills section, list skills the next agent has
   (`ls ~/.agents/skills`), each with one line on when to use it.
   Done when: every skill you named has a `SKILL.md` on disk.
6. **Save a new dated file, then point the root `HANDOFF.md` at it.**
   - Save to `handoff/HANDOFF-YYYY-MM-DD-HHMM.md` at the home, using the real local time (`date +%F-%H%M`).
     Never overwrite an older handoff.
   - If the root `HANDOFF.md` holds a full handoff rather than a pointer, move it first to
     `handoff/HANDOFF-<its date>-root.md` (the date from
     `git log -1 --format=%cd --date=format:%F-%H%M -- HANDOFF.md`, or the file's mtime when untracked).
   - Rewrite the root `HANDOFF.md` as the pointer below, and nothing else:

     ```markdown
     # Handoff

     Newest: `handoff/HANDOFF-2026-10-16-1530.md` (read it first). Older files in `handoff/` are history.
     ```

   - If the repo's `AGENTS.md` (the same file as `CLAUDE.md`) names one dated handoff as the latest, change
     that line to point at `HANDOFF.md`, because a dated name goes stale with the next handoff.
   Done when: `head -3 HANDOFF.md` names the new file, and that file exists.
7. **Prune old handoffs: keep the newest 3.** An old handoff describes a state that is no longer true, and an
   agent that opens it trusts stale facts. Only the dated session handoffs count; leave every other file in
   `handoff/` alone.

   ```bash
   ls handoff/HANDOFF-*.md | sort | head -n -3                       # the ones to prune
   git ls-files --error-unmatch handoff/HANDOFF-<date>.md            # exit 0 means tracked
   ```

   - First skim each one for a decision or an open question recorded nowhere else, and move it to the repo's
     decision log, its plan, or `~/.claude/HARVEST.md`.
   - Delete a tracked one with `git rm`, because git history keeps it. Never delete an untracked or ignored
     one: list it in the report instead, since deleting it loses it for good.
   Done when: at most 3 dated handoffs remain, or the report lists the untracked ones kept.
8. **Redact.** No secrets, tokens, credentials, authentication material, personal identifiers, or real user
   data (amounts, names, account numbers, private task titles). Use counts or effects instead.
   Done when: `grep -niE 'token|secret|password|bearer|api[_-]?key' <file>` shows only safe mentions.
9. **Re-read the saved file.** Check that every path it names exists, that no placeholder is left, and say
   whether `handoff/` is tracked or ignored in this repo. Do not commit unless the user asked.
   Done when: every named path passes `test -e`, and no `<...>` or `TODO` remains.
10. **Report** the saved path and the next step. The user's habit is `/handoff` then `/clear`, so end with
   a line saying the session is safe to clear, or what still blocks that. Name what step 7 pruned and kept.
   Done when: the reply holds the path and that line.

## The document's shape

```markdown
# Handoff YYYY-MM-DD HH:MM: <topic>

Next session: <goal>. Start with: <the exact next step>.

## Status          (task | done and verified, done unverified, in progress, proposed | evidence)
## Decisions       (decision, why, where it is recorded)
## Tree state      (per repo: branch, HEAD, uncommitted files, pushed, deployed)
## Checks          (command | decisive output | when)
## Open questions  (question, recommended answer)
## Harvest
## Suggested skills
```

Drop a section that would only say "none", except Open questions.

## Rules

- Keep it proportional to the unfinished work. Finished, verified work gets one status line; the space goes
  to what the next agent must do or decide.
- Write the current state, not a story of the session. The next agent needs where things are, not how
  they got there.
- Call something verified only when this session ran the check and the output is in the Checks section.
  Older evidence is "last verified <date>", so stale proof never reads as current.
- Follow the reply style in `~/.claude/RULES.md`: plain words, full sentences, no long dashes.

## Gotchas

- The work happened in one repo but the session started in another. Save the handoff in the repo where the
  work is, and say so in the report.
- A root `HANDOFF.md` from before this convention holds a whole handoff, sometimes with a hand-written
  "newer handoff, read it first" line on top. Move it into `handoff/` as step 6 says, then write the pointer.
- An `AGENTS.md` says "`handoff/HANDOFF-<date>.md` (latest, read it first)". It is stale after the next
  handoff; point it at `HANDOFF.md`.
- `handoff/` also holds plans and other notes in some repos. The pointer names the handoff, so those files
  do not hide it, and step 7 never prunes them. Design bundles with screenshots belong in the repo's design
  folder (`ui/inbox/<slug>/`), not here: one repo had 26 MB of PNGs tracked under `handoff/`.

## References

- `history.md`: why the convention changed on 2026-10-16 and where this workflow used to live.
