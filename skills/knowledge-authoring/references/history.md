# History behind knowledge-authoring

The rules in SKILL.md each carry one sentence of why. This file keeps the incidents and the full
previous version of the skill. It has one heading per source skill: knowledge-authoring (below) and
skill-creator (at the end), merged into one skill on 2026-10-15.

## knowledge-authoring: snapshot of SKILL.md before the 2026-10-15 rewrite


### knowledge-authoring - write it so a weak model follows it and the audit keeps it true

#### 0. First decision: WHERE does this knowledge live?

| It is... | It goes in... |
|---|---|
| A behavior that must hold in EVERY session (verify, scope, calibration) | RULES.md - always loaded; skills load only sometimes |
| A stable machine fact (path, port, account) | ENVIRONMENT.md (global) or the project CLAUDE.md Facts block - never both (drift) |
| Task-shaped knowledge loaded on demand (a runbook, a recipe, gotchas) | a skill |
| Project-specific context, commands, domain rules | that project's CLAUDE.md (AGENTS.md symlinks to it) |
| A dated event, user preference, or cross-project state | a memory file (+ MEMORY.md line) |
| Dispatch only ("when X load Y") | the RULES.md router - NEVER a dispatch-only skill (it's a failure point) |
| A lesson flagged but NOT yet encoded | `~/.claude/HARVEST.md` "## Pending" - the durable inbox; digest it through this table at close-out, then tick |

One artifact per fact. If you're copying a paragraph between two files, one of them
should be a pointer.

#### 1. Writing a skill (use `skill-creator` for mechanics; these are the house rules)

- **Description = the trigger surface.** Write it for the dumbest router: name the
  concrete user phrases ("trigger even if the user only says ..."), name what it is
  NOT for, and name the sibling skill for the adjacent case. This line is the only
  part loaded in every session - spend effort here.
- **Descriptions carry TRIGGERS and BOUNDARIES. Bodies carry ANSWERS, mechanisms and
  provenance.** The description is the only text loaded in EVERY session, for all ~41
  skills at once - measured 2026-09-02 at **~9,000 tokens** before a single skill fires.
  It inflates by a specific mechanism: a gotcha gets solved, and the fix is pasted into
  the description "so it triggers" - so `frontend-interaction-patterns` reached 3,137
  chars carrying its own answers (`npx shadcn add`, `min-w-0`, `parseDecimal`). Those
  belong in the body; the router never needed them. A trimming pass over the 6 fattest
  cut 4,555 chars (~1,139 tokens) while preserving every quoted trigger phrase.
  **When trimming, verify mechanically** - extract the quoted phrases from the old and
  new description, normalise whitespace (the old text wraps mid-phrase), and refuse the
  edit if any is lost. That check blocked two drafts that would have dropped real
  triggers.
- **Body ≤ ~150 lines**; templates, catalogues, long gotcha narratives → `references/*.md`
  with a one-line pointer. (The audit flags violations.)
- **Imperative steps with exit artifacts.** "Step N produces X" - a weak model treats
  judgment as optional and instructions as mandatory; convert judgment to instruction.
  Make skipping explicit: "say 'step N: nothing applies'", never silent.
- **Distill from reality, not general knowledge.** Every fact carries a source
  (file:line, command output) and a verified date. Generic advice the model already
  knows is trigger-noise - encode only what's EARNED (gotchas, decisions, this box).
- **Name the failure the skill prevents** in the first lines - future readers (and
  models) follow rules whose cost they understand.
- **Cross-reference, don't duplicate**: point at `nas-offsite-backup` etc. instead of
  restating; the audit checks referenced names resolve.
- New skill → add its router line to RULES.md in the same change, or it won't fire
  for weak models.

#### 2. Writing/editing RULES.md

- Only universal, always-true imperatives. If it's conditional on a task type, it's
  a router line + skill instead.
- Top-5 non-negotiables box stays ≤5 items - it's the weak-model glance surface;
  adding a 6th dilutes all of them.
- Every rule earns its tokens: loaded in EVERY session. Prefer editing an existing
  rule over appending near-duplicates.

#### 3. Writing a project CLAUDE.md (+ AGENTS.md)

Contract (RULES.md "Canonical project docs"): Facts block (verified ports, hostnames,
containers, pins - with date), Commands block (copy-paste, in-container, tested by
actually running each once), conventions, domain rules, out-of-scope. Then
`ln -s CLAUDE.md AGENTS.md`. Never write a command you didn't run - the Caudal
test-command incident (documented but never executed, broken for weeks) is the
cautionary tale.

**Group invariants by SUBJECT, never by version.** A section stamped with a version number
(`## v2`, `## v3 invariants`) only ever GROWS and eventually contradicts itself: an old version's
rule is silently superseded by a later one, but both sit in the doc asserting opposite things, and
the next session trusts the stale one. Loop's CLAUDE.md carried a v2 rule (`if (!state.behind)
return []`) that v3 had deleted - found only by reading the code. Regroup by subject (Projects,
Plan, Undo, …) so each fact lives once and a change edits it in place instead of appending a
contradiction. (loop 2026-09-05, regrouped 2026-09-07.)

#### 3b. Tracker honesty - FEATURES.md/PLAN.md describe the CODE, never the plan

Two projects hit this in one month; both cost a session that began with the USER noticing a
symptom the doc denied.

- **Write a tracker line from the code you just read, not the plan you just wrote.** closet's
  FEATURES.md claimed activity garments were "inventory-pick"; only the EXCLUSION gate was ever
  built (`capsule.ts:160`, `recommend.ts:94`), so a bañador was unreachable for any trip - for 2
  days, while the doc asserted otherwise (2026-07-20). When you write "X is handled by Y", grep
  that Y exists AND does it. A design-doc phrase copied into a status doc becomes a lie the next
  session inherits and trusts.
- **A spec item can be superseded by a LATER architecture decision.** Build it, prove it's
  unreachable, then DELETE it - never silently skip it, never silently ship dead code. triage's
  `G9` loading skeleton was in the design pack; a later slice (SSR seeding) made `messages`
  never-null, so the branch could not render and a boot splash already covered that moment. It was
  built, proven dead, removed, and recorded as **superseded, with the reason** (2026-07-17). Ask
  "did a later decision EAT this?" before forcing a spec item to work - a shimmer that cannot
  appear is decoration pretending to be a state.
- Spec frames already served by an existing surface → mark them **covered-by-existing** honestly
  rather than building a redundant screen.
- Corollary: "shipped" needs the commit; "verified" needs the command output.

#### 3c. A house rule that subagents keep breaking needs MECHANICAL enforcement

In a 9-phase orchestrated rewrite, subagents kept re-introducing the em-dash character in UI copy
and comments despite the standing rule - every phase cost a grep+sed sweep. A rule re-violated by
every fresh context is not a knowledge problem: a lint rule or pre-commit hook beats re-policing it
by hand (closet, 2026-07-15). Same for any invariant a fresh agent cannot see.

#### 4. Writing memories

One fact per file, frontmatter + type (user/feedback/project/reference); feedback
memories include **Why** and **How to apply**; relative dates → absolute; link
related memories `[[name]]`; add the MEMORY.md index line. Update or delete stale
memories - the audit checks them against reality.

#### 4b. Harvest protocol - turning session pain into skills

The triggers (from RULES.md, restated): >5-min struggle a recipe would erase ·
a FAILED approach (hand-roll lost to a library - capture even though admitting
failure feels optional; it isn't) · same problem in a second project · a settled
library-vs-alternative trial.

- **Placement**: an existing skill's gotchas section beats a new skill (check the
  router first); a new skill only when no home exists AND the lesson generalizes;
  a memory when it's dated/one-off.
- **Entry format**: problem → the proven winner (library/pattern + minimal recipe)
  → the losing approach AND its cost ("hand-rolled 25 min, never worked") → date.
  Naming the loser is the point - it's what stops the next model from retrying it.
- The model that just failed is the least likely to volunteer the harvest - do it
  anyway; the failure IS the value. `frontend-interaction-patterns` (born from the
  @dnd-kit-vs-hand-rolled incident) is the reference shape.

#### 4c. Ripple check - every knowledge change has a blast radius; walk it NOW

The audit catches dangling references in a month; this check catches them in the
same commit. Run the branch that matches your change:

- **Renamed or deleted something** (skill, file, section, command, container name):
  `grep -rn "<old-name>" ~/.claude/RULES.md ~/.claude/*.md ~/.agents/skills --include="*.md"`
  plus the project docs if project-scoped. Fix EVERY hit in the same commit - 
  a rename isn't done while one reference points at the old name.
- **Created a NEW artifact** (skill, file, convention) - registration checklist,
  answer each line yes/no:
  1. Router line in RULES.md? (a skill nobody routes to never fires)
  2. Row in this skill's placement table? (if it's a new *kind* of artifact)
  3. Consumers wired? - which existing skills should READ or WRITE it
     (one-shot close-out, handoff, skills-audit, bootstrap...); add the hook there
  4. `~/.claude/.gitignore` whitelist? (anything new in ~/.claude root)
  5. An audit check? (if it can rot - stale entries, drift)
  6. REBUILD.md / MODEL-MIGRATION.md? (if it affects rebuild or portability)
  7. ENVIRONMENT.md? (if it's a machine fact)
  8. Overlap: does an EXISTING skill already claim this territory or these trigger
     phrases? Prefer extending it; if a new skill is truly warranted, disambiguate
     BOTH descriptions and add a precedence line to the router (the
     bootstrap-vs-new-project ambiguity is the cautionary case)
- **Changed a skill's behavior/contract**: grep for skills that reference it by
  name; verify each described interaction still holds.

**Exit artifact:** a "Ripple: <N refs checked, M files updated>" line in the reply
(and commit message). Precedents that motivated this: the grill-me rename needed
3 reference fixes; HARVEST.md shipped unregistered in 2 consumers until the user
caught it (2026-07-06).

#### 4d. Concurrency: ONE writer per skill DIRECTORY, and never across a turn boundary

Learned the hard way processing the 114-entry harvest (2026-07-20), where four agents wrote to
`~/.agents/skills` at once and a restructure was silently half-committed three times: a 145-line
reference file went to 0 bytes, `SKILL.md` was left pointing at a file that no longer existed, and
four reference files ended up orphaned with their content duplicated inline (-419 lines to clean up).

- **Ownership is the DIRECTORY, not the file.** Per-file ownership is fine for editing prose, but
  "move this section out of `SKILL.md` into `references/<name>.md`" is a TRANSACTION across three files
  (delete here, create there, repoint). No instant mid-sequence is coherent. Never put two agents in
  `skills/<name>/`, even on different files. One restructurer at a time.
- **Do not leave background agents writing to a knowledge repo across a turn boundary.** The `Stop`
  hook (below) commits whatever exists at turn end, so a half-done transaction gets committed as if
  it were finished - and the NEXT agent reads that half-state as deliberate structure and "fixes" it
  in a different direction. Wait for the agents, run the integrity check, THEN let the hook commit.
- **The failure is silent, which is why it needs a mechanical check.** Nothing errors: the skill
  still loads, `SKILL.md` still looks complete, and the lesson that went missing is simply invisible
  to the next reader. Same class as the tracker-honesty rule (3b) - a doc that looks right beats one
  that is obviously broken, at being dangerous.

**Integrity check - run after ANY skill edit, before you report done** (cheap, catches all three
signatures: dangling pointer, orphaned file, truncated file):

```bash
cd ~/.agents/skills
for s in */SKILL.md; do d=$(dirname "$s"); grep -o '`references/[a-z0-9-]*\.md`' "$s" | tr -d '`' \
  | sort -u | while read -r r; do [ -f "$d/$r" ] || echo "DANGLING: $s -> $r"; done; done
for f in */references/*.md; do d=$(dirname $(dirname "$f")); \
  grep -qr "$(basename "$f")" "$d" || echo "ORPHAN: $f"; done
find . -name "*.md" -empty
```
Cross-skill pointers (the owning skill named alongside, e.g. docker-ports-and-tunnels + its port-registry ref) show as DANGLING - 
read the line before "fixing" it, and write those qualified with the owning skill's name.
Recovery when it already happened: the content is in git (`git log -S"<marker>"`, then
`git show <sha>:<path>`) - the auto-push hook is what makes this survivable.

#### 5. Before finishing ANY knowledge artifact

1. Read it as a hostile weak model: is any step skippable silently? Any fact
   unverified? Any trigger phrase missing from the description?
2. Run `skill-creator`'s validator/eval when it's a skill and triggering matters.
3. Stamp the verify date. Commit (the repos are the durability layer).

**Auto-push safety net.** A `Stop` hook (`~/.claude/scripts/autopush-knowledge.sh`,
registered in `settings.json`) commits+pushes any pending changes at each turn end for
every repo listed in `~/.claude/scripts/autopush-repos.conf` (currently `claude-skills`,
`claude-config`, `dev-system` - knowledge/config repos ONLY, never app code). So a created
skill and its RULES.md router line reach their repos automatically (the
`proxmox-portability` requirement that no artifact live only on this box). It never
`git add -f`s and refuses to commit secret-like paths. It is a backstop, NOT an excuse
to skip a deliberate commit with a real message - it exists so a forgotten push can't
strand a skill on the box. Log: `~/.claude/skills-autopush.log`. Disable via `/hooks`.

## skill-creator

`skill-creator` was Anthropic's generic skill-building skill (Apache 2.0, `LICENSE.txt` at the root of this
directory covers the files that came from it: `agents/`, `scripts/`, `eval-viewer/`, `assets/`, and the
references `skill-building.md`, `writing-skills.md`, `eval-loop.md`, `description-optimization.md`,
`eval-schemas.md`, `packaging-and-environments.md`). knowledge-authoring used to "wrap" it: the house rules lived
here, the mechanics there, and every skill session had to load two skills and reconcile them. On 2026-10-15 the
redo merged it into knowledge-authoring.

- Its SKILL.md body moved nearly verbatim to `references/skill-building.md`; only the paths changed.
- Two references were renamed so the name says the topic: `references/schemas.md` became
  `references/eval-schemas.md`, and `references/environments.md` became `references/packaging-and-environments.md`.
- Conflicts settled: skill-creator said a SKILL.md may run to 500 lines and the description should be "a
  little bit pushy" and carry all "when to use" info. The house style wins on this box: 150 lines at most, a
  description of 800 characters at most that names triggers and boundaries and never the steps.
- The scripts still run as `python -m scripts.<name>` from the skill directory; they import each other as a
  package, so the move needed no code change beyond two docstrings.
- Codex has its own native skill-creator, and `~/.claude/INSTALL.md` disabled the shared copy for Codex.

The description skill-creator had before the merge:

> Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy. NOT for this machine's house style, ripple check, or rule-vs-skill placement (use knowledge-authoring, which wraps this skill).

## 2026-10-16: HARVEST processing moved to retro

Section 4 used to hold the five-question filter, the routing of an accepted lesson and the record format. They
moved unchanged to `retro/references/harvest.md`, so one skill owns the inbox; this skill still writes what
`retro` accepts. The old text began "Process the oldest first. Accept a lesson only if every answer is yes".
