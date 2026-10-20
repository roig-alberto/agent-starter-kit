---
name: skills-audit
description: >-
  Repeatable maintenance audit of the whole agent-knowledge system (skills, RULES.md, ENVIRONMENT.md,
  memories, HARVEST, and per-project CLAUDE/AGENTS/FEATURES docs) against reality: runs the knowledge
  linter and the fleet-facts generator, then the judgment checks a script cannot (contradictions,
  trigger overlap, stale plans, wrong facts in project docs). Use when the user says "audit the
  skills", "/skills-audit", "spring cleaning", "are the skills still accurate", roughly monthly, or
  after a big environment change (machine move, app retired or added, stack change). NOT for writing or
  renaming a skill (use `knowledge-authoring`) or processing the HARVEST inbox alone (use `retro`).
---

# Skills audit

Facts rot silently, and a doc that looks right is more dangerous than one that is obviously broken. The mechanical
checks now run on every turn through `knowledge-lint.py`; this audit adds the checks that need judgment and a look
at the live system. Agent Factory runs it read-only as loops: "Box checks" weekly (the script checks, no model) and
"Knowledge audit" quarterly (Jan, Apr, Jul, Oct; Run now forces it), one turn over a masked snapshot, findings to
Triage; fixing is interactive.

## Steps

1. **Mechanical baseline.** Run `python3 ~/.claude/scripts/fleet-facts.py` and then
   `python3 ~/.claude/scripts/knowledge-lint.py`. Fix every ERROR. Re-verify every WARN stamp against the
   live system and update its date, or mark it "unverified since <date>".

   Done when: `python3 ~/.claude/scripts/knowledge-lint.py | grep ERROR` prints nothing.
2. **Always-on cost.** Run `python3 ~/projects/dev-system/harvest/context-budget.py`
   and compare with the last audit. Growth means a description or RULES.md picked up answers; move them to
   skill bodies.

   Done when: the new total is quoted next to the last audit's total in your findings.
3. **Project docs against reality.** For each app repo (FLEET.md lists them): `AGENTS.md` (the same file as
   `CLAUDE.md`) has a Commands block and points at FLEET.md instead of restating ports or containers;
   `AGENTS.md` is a symlink (`ls -la AGENTS.md`); `FEATURES.md` exists and its recent rows match the code; no
   PLAN.md or MIGRATION.md is marked active while untouched for weeks (`git log -1 --format=%cs -- PLAN.md`). Which
   canonical docs and `verify-<app>` skills are missing is already a script check
   (`python3 ~/.claude/scripts/box-checks.py project-docs`): copy its problems into the findings, never recount them
   by hand. `box-checks.py skill-usage` names skills unused two recorded months in a row: list them for `retro`, which
   decides whether each is merged, sharpened or deleted.

   Done when: every app repo has a row in the findings table, even if the row says "clean".
4. **Contradictions.** Grep load-bearing terms (stack versions, image pins, "default", backup times, tool
   names) across skills and project docs. Reconcile to the canonical source: FLEET.md for live facts, then
   the owning skill, then the app doc.

   Done when: each term you grepped has either one agreed value or a flagged row naming the files that
   disagree.
5. **Trigger overlap.** Compare skill descriptions for shared trigger phrases. Resolve with a precedence note
   in the RULES.md router, not by making both descriptions vaguer.

   Done when: each shared phrase you found has a router precedence note or a flagged row.
6. **Memories.** Read each memory under `~/.claude/projects/*/memory/` and delete or update any the audit
   proved wrong. Watch for memories stranded under an old project slug that no session loads.

   Done when: every memory directory was read, and each wrong memory is fixed or listed in the findings.
7. **HARVEST.** Process entries older than 30 days with `retro` (its filter is in
   `retro/references/harvest.md`).

   Done when: `~/.claude/HARVEST.md` has no `## Pending` entry older than 30 days.
8. **Untracked knowledge.** `git -C ~/.claude status --short`, `git -C ~/.agents/skills status --short`, and
   `tail ~/.claude/skills-autopush.log`. Commits that stopped appearing mean the push gate is holding or git
   is blocked.

   Done when: both status outputs and the log tail are quoted in the findings, with any held push explained.

## Output

A findings table (`file | finding | fixed or flagged`), fixes applied for anything provably wrong, and flags for
anything that needs the user. Then a ripple line and a clean lint run.

## Gotchas

- A filtered view is not proof of absence: re-run any "none found" through `rtk proxy` or count with `grep -c`.
- Python tools live in `uv tool` venvs; `which <bin>` and `uv tool list` before calling one missing.
- **A deployed copy drifts from its repo source.** Compare every script in `/usr/local/bin` and the systemd units with their dev-system sources (`cmp`), and redeploy with `sudo /bin/sh -c 'install ...'` in the same change as the edit. Drift once left the backup and restore-test jobs blind to five apps.

## References

- `references/history.md`: the incidents that shaped this audit and its previous version.
