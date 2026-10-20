---
name: create-verification-skill
description: >-
  Generates or maintains a project-local verification skill (a `verify-` skill in the repo's `.claude/skills/`) that drives one app the way the user does: launch, doctor, drive, evidence, cleanup, plus a feature map with one file per user-facing feature, proven by running it once. Use when an app has no scripted way to prove its behavior, on "make a verify skill for this app", "create a verification skill", "audit the verify skill", or when a verify skill's feature map has drifted from the app. NOT for a one-off UI measurement (use verify-ui-live) or app unit tests (use testing).
---

# Create or maintain a verification skill

Agents prove a change works only when they can drive the real app and capture evidence. A generic recipe makes
every session rediscover how to start the app, log in, and reach a feature. A project-local `verify-<app>` skill
writes that down once, per app, and is proven by running it. Adapted from pstack's `create-verification-skill`
and `maintain-verification-skill` (cursor/plugins).

## Create

1. **Interview the repo, not the user.** From the code and its AGENTS.md (the same file as `CLAUDE.md`), answer:
   the surface the user touches (web UI, PWA, CLI, API), how dev starts (the Commands block), the ready signal,
   how to log in headlessly (`~/.config/ui-check/<host:port>.pw`), what can drive it (`chrome-devtools-axi`,
   `ui-check`, committed `e2e/*.e2e.py`, curl), what evidence exists (screenshots, DOM values, DB rows, logs),
   and whether two instances can run side by side. Ask the user only what the code cannot answer.
   Done when: every question above has an answer written down, each cited to a file or command.
2. **Fix the base first.** If the dev stack does not start as documented, fix that or report it before writing
   steps against a broken base.
   Done when: the documented start command reaches the ready signal, or the failure is reported to the user.
3. **Write `SKILL.md`** in the repo at `.claude/skills/verify-<app>/` with frontmatter (`name: verify-<app>`, a
   description naming the app and when to use it) and these sections, each from real findings:
   - **Launch**: the exact command, the ready signal (usable, not just a port answering), teardown.
   - **Doctor**: one read-only check that the instance is worth driving (health endpoint, right build, port
     owned by the dev stack, login works). Run it first and after any surprise.
   - **Drive**: the harness recipe with this repo's real selectors (roles, accessible names, data attributes),
     never coordinates.
   - **Evidence**: what proves a claim and where artifacts go (outside the repo, kept after cleanup). Drive the
     real user path, capture action and resulting state, check side effects (rows written, files stored).
   - **Cleanup**: stop only what this run started; remove scratch data the run created; keep the evidence.
   - **What headless cannot see**: the device-only traps the user reports from the phone, so a green run is
     never presented as disproof.

   Done when: `.claude/skills/verify-<app>/SKILL.md` exists and holds all six sections.
4. **Seed the feature map** at `features/README.md` plus one file per top feature (start with three to five).
   Each file has exactly four H2 sections: `Sub-features`, `How to get to it (user POV)`,
   `Driving it with <harness>`, `Gotchas`. Driving bullets pair a user action with an exact command and the
   observable result. If seed data lacks a precondition, the journey reports a failure; never weaken it to pass.
   Done when: `features/README.md` lists every feature file and each file has the four H2 sections.
5. **Prove it before handing over.** Run launch, doctor, one mapped feature, evidence capture, and cleanup end to
   end; confirm the evidence survives cleanup. A skill that was never executed is a draft.
   Done when: the run's evidence files exist after cleanup and the reply quotes the doctor output.
6. **Register it** in the project's AGENTS.md (one line pointing at the skill) and commit it in the app repo by
   explicit path.
   Done when: `git log -1 --stat` lists the skill files and the AGENTS.md line.

## Maintain

Run when the app changed or the user asks to audit the verify skill. Outcomes are `clean`, `changed` (one commit
of proven corrections inside the skill directory only), or `blocked` (say what blocked it).

1. Fix the feature-map index: missing, extra, or dead entries.
   Done when: every file under `features/` is listed in `features/README.md` and every entry has a file.
2. Read the source behind each feature file (a read-only subagent per feature when there are many) and flag
   drift with citations.
   Done when: each feature file has a verdict with a file and line citation, or is marked clean.
3. Drive every feature live at least once, running doctor before the first drive and after any failure. A
   feature that cannot be reached is reported with the missing prerequisite and the route tried.
   Done when: each feature has a pass, a fail with evidence, or a blocked report naming the prerequisite.
4. Classify each finding: doc drift (fix the map), harness gap (fix the harness and re-drive it), or product
   regression (report it; never paper over it in the map).
   Done when: every finding carries one of the three labels, and the outcome is `clean`, `changed` or `blocked`.

## Gotchas

- A dry-run or test mode may still touch the network or data; verify what it skips by observing it.
- Never drive an instance this run did not health-check, and never kill processes by name; stop what you started.
- Shared dev and prod databases (see ENVIRONMENT.md) make every dev write a prod write; drive writes against a
  throwaway database (`testing`).

## References

- `references/feature-map-example.md`: a worked feature file in the required four-section shape. Read before
  writing the first one.
