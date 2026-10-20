---
name: retro
description: >-
  Looks back at a session or a week and proposes fixes to the agent setup, not to the app: checks, skills,
  rules, always-loaded docs and tools; also processes the HARVEST inbox and trims memory. Use when the user
  says "retro", "retrospective", "what did we learn", "why did that take so long", "process the harvest",
  "clean up the memory", "the harvest is overflowing", at the end of a long task, or in the weekly skills
  review. NOT for writing the change itself (use knowledge-authoring) or for checking facts against the live
  system (use skills-audit).
---

# Retro

Look back at real work and make the next run cheaper. It prevents three slow failures: the same mistake made
in a third session because nothing turned it into a check, an inbox of lessons that grows faster than anyone
reads it, and always-loaded files (`AGENTS.md`, RULES.md, memory) that fill with history every agent pays for.

## Steps

1. **Pick the scope and read the primary sources.** Default: this session. A named session or "the week" means
   the transcripts, never memory: Claude Code in `~/.claude/projects/<slug>/*.jsonl`, Codex in
   `~/.codex/sessions/`, OpenCode in `~/.local/share/opencode/`. Extract with a script, not by reading every
   line.
   Done when: you can name the sessions read and the moments that cost the most (time, tokens, user corrections).
2. **Find candidates, each tied to one moment.** Look in these places, in this order:
   - **Checks:** a mistake a lint rule, type, test or hook could have caught. Read the repo's own check command
     first; a check that exists but is unwired is the finding.
   - **Routing:** a skill that should have loaded and did not, or the wrong one did (prove it with
     `agent-tool-bench/references/router-eval/run-skill.sh <skill>`).
   - **Navigation:** the agent searched long for a file or fact; a pointer in `CODEMAP.md` or a skill fixes it.
   - **Tool economy:** an expensive call (a huge output, a re-read file, a filtered command re-run raw).
   - **Information access:** a fact the agent could not reach (a log, a read-only view of a service).
   - **Steering:** an instruction the agent ignored (make it a check) or one that changes nothing (delete it).
   Done when: every candidate names its moment (a session, a quote or a tool call), never a generic tip.
3. **Process the HARVEST inbox.** Every `## Pending` entry in `~/.claude/HARVEST.md` older than 7 days gets one
   verdict with the filter in `references/harvest.md`: a check, a skill edit, a RULES line, the repo's docs, or
   dropped with the failed criterion. Group by repo, and report inflow against outflow.
   Done when: each processed entry is ticked under `## Processed` with its destination or its failed criterion.
4. **Trim memory and the always-loaded files.** For each memory under `~/.claude/projects/*/memory/`: a general
   preference moves to RULES.md (memory loads only in its own folder); a project fact still true moves to that
   repo's docs or a skill; anything stale or already in the repo is deleted. Flag an `AGENTS.md` far larger than
   the others (history and solved gotchas move to `docs/` or the decision log), and RULES.md growth.
   Done when: every memory has a verdict and oversized files are listed with what would move.
5. **Propose, then apply only what the user approves.** Rank by cost saved, most first; at most 5 to act on and
   the rest in one line each. In the weekly review each proposal becomes a Triage item instead. Apply approved
   ones with `knowledge-authoring` (placement, style, ripple check).
   Done when: the user has a ranked list, and every approved item is applied and lint-clean.

## Rules

- **A check before a rule.** A mechanical mistake (a pattern, a banned call, a file location) gets a lint rule,
  test or hook; prose only for judgment calls. Agents re-break a rule that is only written down.
- **Always-loaded files should shrink over time.** A retro that only adds lines to `AGENTS.md` or RULES.md has
  failed; move detail to a skill or a doc and leave a pointer.
- **Capture is cheap, so the filter is strict.** Most lessons are one-offs; dropping one with its reason is a
  good outcome, not a loss.
- **Redact.** A proposal or Triage item quotes counts, skill names and short paraphrases, never personal data
  or a secret from a transcript.

## References

- `references/harvest.md`: the five-question filter, where an accepted lesson goes, the entry format, and the
  monthly inbox hygiene. Read in step 3.
- `references/history.md`: where this skill came from and why HARVEST processing moved here.
