# History behind skills-audit

The previous version of this skill, kept for its incident notes and baselines.

## Snapshot of SKILL.md before the 2026-10-15 rewrite


### skills-audit - keep the knowledge system true

This audit exists because facts rot silently: the 2026-07-06 audit found months-old
Mac paths in two skills, a hand-copied AGENTS.md drifted from CLAUDE.md, docs claiming
Next 14 over a Next 15 package.json, and a plan describing an nginx setup that no
longer existed. Run the checks; fix what's provably wrong; flag what needs the user.

#### Checks (in order - each names its evidence command)

1. **Stale paths.** Every absolute path mentioned in skills/RULES/ENVIRONMENT must
   exist: `grep -rhoE '(/home/[a-z]+|/mnt/c|/Users)[^ )"`]*' ~/.agents/skills ~/.claude/*.md | sort -u`
   then test each with `ls`. `/Users/...` = Mac fossil, always wrong here.
2. **Dead cross-references.** Every `skill-name` referenced by another skill or the
   RULES.md router must exist in `~/.agents/skills/`. (Today's equivalent: references
   to deleted `karpathy-guidelines` would have dangled.)
3. **Fact spot-check against reality.** For each fact-bearing doc, verify a sample
   against the live system: ports/containers vs `docker ps -a`; image pins vs compose
   files; package versions claimed in docs vs `package.json`; ENVIRONMENT.md table vs
   the port registry; deadman `enabled` flags vs the NAS script. Fix + re-stamp dates.
4. **Contradictions between docs.** The known shape: two files both claiming a default
   (stack, port, convention). Grep the load-bearing terms (stack names, "default",
   port numbers) across skills + CLAUDE.mds and reconcile to the canonical source
   (SYSTEM_SPEC > registry > skill > app doc).
5. **Verification stamps.** Anything stamped >90 days ago is due a re-verify or an
   honest "unverified since X" note. Scope explicitly includes PROMPT-GUIDE.md and
   MODEL-MIGRATION.md, not just skills/RULES/ENVIRONMENT.
6. **Trigger overlap.** Skill descriptions claiming the same trigger phrases degrade
   selection. List descriptions, look for collisions, resolve via the RULES.md router
   (precedence line) rather than rewording both into vagueness.
7. **Bloat.** SKILL.md over ~150 lines → move narrative/gotcha-history to
   `references/` (the verify-ui-live treatment). Descriptions stay trigger-rich; bodies
   stay lean. **Measure the always-on cost with `python3 dev-system/harvest/context-budget.py`**
   (sums the imported MD + every skill DESCRIPTION - the standing tax paid every turn; bodies
   load on-demand and don't count). It flags descriptions over 800 chars: trim answer-fat and
   duplicate trigger phrasings while KEEPING every distinct trigger (a dropped trigger silently
   degrades routing; a fat one truncates the budget). Baseline 2026-09-09: ~19.1k standing tok,
   20 descriptions over cap. For a skill the model must NEVER auto-trigger (user runs it by
   `/name` only), set `disable-model-invocation: true` in its frontmatter - CC then drops its
   description from the routing budget entirely (verified native, CC 2.1.265).
8. **Project doc contract.** Each app repo: CLAUDE.md has Facts+Commands, AGENTS.md is
   a *symlink* (not a copy - `ls -la AGENTS.md`), FEATURES.md exists and its recent
   rows match reality, no stale PLAN/MIGRATION marked in-progress.
9. **Untracked knowledge.** `git -C ~/.claude status --short` and
   `git -C ~/.agents/skills status --short` - weeks of uncommitted knowledge is one
   `rm -rf` from gone; prompt the user to commit (never auto-commit).
10. **Memory hygiene.** Memories are PER-PROJECT, not global: `~/.claude/projects/<slug>/memory/`
    with a `MEMORY.md` index inside each (the slug is the cwd path with `/`→`-`). Enumerate with
    `for d in ~/.claude/projects/*/memory; do ls "$d"/*.md 2>/dev/null | wc -l | xargs echo "$d"; done`.
    Read the entries; delete/update ones the audit proved wrong (memories rot like docs) and check
    each `MEMORY.md` index line still points at a file that exists. **Watch for LEGACY SLUGS**: a
    project that moved directory leaves its memories stranded under the old slug where no session
    will ever load them - e.g. 15 files under `-mnt-c-Users-<user>` predating the WSL-native move
    (found 2026-07-21). Stranded ≠ wrong: judge each, then migrate or delete deliberately.
    (This check said "read `~/.claude/MEMORY.md`" until 2026-07-21; no such file has ever existed,
    so the check silently passed on nothing for months.)
11. **Harvest inbox rot.** `~/.claude/HARVEST.md` "## Pending" entries older than 30
    days = a finding: a session flagged a lesson and nobody encoded it. Process or
    consciously drop each; prune ticked lines older than a month. ALSO check the file's
    SHAPE: exactly one `## Pending` and one `## Processed`, and no unticked entry filed
    under Processed. It had drifted to three Pending headings, which is how 114 entries
    accumulated in a month without the >30-day rule ever firing (2026-07-20).
12. **Skill-directory integrity.** Run `knowledge-authoring` §4d's check: every
    `` `references/<name>.md` `` a SKILL.md points at exists · no reference file is orphaned
    (nothing points at it - its knowledge is invisible) · no `.md` is empty. These are the
    silent signatures of a half-committed restructure; nothing errors, the skill still
    loads, and the missing lesson is simply unreadable. Cross-skill pointers written
    `<owning-skill>` + its reference filename are fine - read the line before "fixing" it.

#### Output

A findings table (`file · finding · fixed/flagged`), fixes applied for anything
provably wrong, flags for anything needing a user decision. Re-stamp every doc the
audit verified. Offer commits at the end.

## 2026-10-16: frontmatter fixed for the validator

Removed what failed `quick_validate`: in new-app the Claude-only `argument-hint: "One-line description of the project to build"`; in skills-audit `disable-model-invocation: true` (the user never types skill names, so a hidden skill never runs); in create-verification-skill the angle brackets in the description (`.claude/skills/verify-<app>/` is still in the body).
