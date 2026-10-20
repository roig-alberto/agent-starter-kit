---
name: new-app
description: >-
  The one entry point for any brand-new project or app, from a one-line idea to a running build; for a
  new self-hosted app that runs as a container on this box's Docker CE and WSL2 home base, it also covers
  the bootstrap (--guided or --auto). Use when the user wants to start a new project or app from scratch,
  invokes /new-project or '/bootstrap', or says 'start a new app', 'scaffold a project', 'spin up a new
  service', 'bootstrap my-app'. NOT for a feature on an existing app (use one-shot); NOT for migrating an
  existing app onto Docker CE (use portability); NOT for a PACKAGED third-party image such as Uptime Kuma,
  Beszel, or Grafana (use fleet-ops). It scaffolds OUR OWN apps from source.
---

# new-app

Take a new project from a one-line idea to a building implementation, and, for a containerized app on this
box, to booted, tunnelled, and backed up off-site. Run the steps **in order**; each one has a gate, so do
not advance until its artifact exists and (in `--guided`) the user has confirmed it. The failure this
prevents is a build that starts before the stack, the docs, and the design are settled, and an app that
ships without a port record, a tunnel, or a backup. Treat the user as the decision-maker: recommend, never
dictate.

For the container steps this skill is thin glue: it sequences `fleet-ops`, `backups-and-alerts` (not in this kit),
`portability`, and `verify-ui-live` and does not re-implement them. The source of truth for those steps is
the dev-system repo: `~/projects/dev-system/bootstrap/`, which holds
`NEW_APP_CHECKLIST.md` (the gated step list plus the Dockerized-Next dev-loop gotchas) and `templates/`
(compose dev and prod, Dockerfile, `.env.example`). Read the checklist; this file is the map.

## Steps

0. **Pick the mode.** **`--guided` (default)** puts an approval gate at each step; use AskUserQuestion for
   genuine forks. **`--auto`** is a walk-away one-shot with the blessed defaults that stops only for a hard
   blocker (a port or hostname collision that cannot be auto-resolved, or a missing secret).
   Done when: the mode is stated.
1. **Ask the first prompt, always: "default stack or interview?"** **Default stack** is one keystroke: the
   blessed stack, asking only the name, the public hostname, and the front/back-split question (only for
   an ML backend or a multi-client app). **Interview** runs step 2 in full for the exceptions. Also settle
   whether the app runs as a container on this box; if not, skip steps 6 to 12.
   Done when: the answer and the container yes or no are recorded.
2. **Requirements and stack, with `grill-me`.** Walk the design tree one question at a time: audience and
   scope, platform, persistence and hosting, **the full stack**, the data model, domain rules, edge cases,
   and what is out of scope. Lock early the UI toolkit, 1-3 reference apps, the #1 usability priority, the
   tempting-but-out-of-scope wants, and the load-bearing external dependency. Offer the default stack first
   and deep-dive only the layers the user changes; in default-stack mode, pre-fill all of this.
   Done when: the stack and the core domain decisions are explicit and agreed.
3. **Write the canonical spec docs** in `~/projects/<app>` (WSL-native): **CLAUDE.md** with a Facts block
   and a Commands block, **AGENTS.md as a symlink** (`ln -s CLAUDE.md AGENTS.md`),
   **IMPLEMENTATION_PLAN.md**, **DESIGN_BRIEF.md**, and **FEATURES.md**; once the scaffold builds, the
   `architecture` skill adds ARCHITECTURE.md, GLOSSARY.md, CODEMAP.md and REVIEW.md.
   Done when: the docs exist, agree with each other, and the user has reviewed them.
4. **Design.** Ask with AskUserQuestion, both paths **equally, with no default**: **A, the Claude Design
   Agent** (external, with the token-export prompt and the `ui/inbox/<feature-slug>/` file exchange), or
   **B, in-house** (load `frontend-design` first). In `--auto`, use in-house with no pause. Either way the
   palette comes first, and the result is **DESIGN_TOKENS.md**, which `DESIGN_BRIEF.md` points to.
   Done when: the user confirmed the **color palette**, DESIGN_TOKENS.md exists, and the direction is agreed.
5. **Plan the build, with the `plan` skill.** The first phase is always the **scaffold** (config, the theme
   wired from DESIGN_TOKENS.md, the schema and first migration, run and build). For a container app the
   scaffold phase is steps 6 to 12; a builder that cannot run Docker (an Agent Factory agent) scaffolds the
   dev stack only and leaves the tunnel, backup and rebuild-file steps to a later go-live phase. Then **prove the load-bearing external dependency end to end** before
   any feature sits on it. Then build feature by feature, ticking each off in `FEATURES.md`.
   Done when: the plan exists and the scaffold builds and runs; later phases follow the plan's approvals.
6. **Host port, with `fleet-ops`.** Read its port registry AND run a live `docker ps -a` before picking.
   Keep the **container** side conventional (app=3000, db=5432) and shift only the **host** side. Record
   the new row in the registry.
   Done when: `__PORT__` is chosen and recorded with no collision.
7. **Scaffold from the templates.** Copy `bootstrap/templates/` (with its `scripts/`) into the project and substitute
   `__APP__`, `__APP_NS__`, `__PORT__`, `__HOSTNAME__`. Put `restart: unless-stopped` on every service so
   it self-heals after `wsl --shutdown`.
   Done when: `docker compose config` parses and the dev stack builds.
8. **Tunnel and Access, with `fleet-ops`.** Stand up the per-app `cloudflared` **container** (profile
   `prod`, a named tunnel and `TUNNEL_TOKEN`) on `example.com`, with the Cloudflare Access policy. **One
   hostname:** `<app>` to `web-prod:3000`. There is no dev hostname; dev is localhost only. Add it to the
   registry's tunnel table.
   Done when: the tunnel is healthy and the hostname is in the registry.
9. **Backup by construction, with `backups-and-alerts` (not in this kit) and `backup-template/`.** Every app with a database
   gets a **`db-backup` sidecar**: a local-first `pg_dump`, then an additive `rclone copy` to
   `nas:/backups/<app>` with the NAS host key pinned. A NAS failure fires a Telegram dead-man's-switch and
   never fails the local dump. The templates already carry it (`db-backup-prod`, `scripts/backup.sh`). Once
   the first real dump lands, flip the app's line in the NAS-side `nas-deadman-check.sh` to `enabled=1`.
   Done when: one manual run of the sidecar's `backup.sh` then `rclone lsl nas:/backups/<app>` shows the dump and both
   alert layers are armed.
10. **Make it portable, with `portability`.** The templates already use the in-repo `./secrets/` and
    pinned images. Register the app in the rebuild files: `REBUILD.md`, `scripts/secrets-backup.sh`,
    `scripts/restore-test.sh`, `nas-deadman-check.sh`, and the port registry (step 5b of the checklist).
    Done when: the app appears in every rebuild file.
11. **Check skill fit.** Scan the app against `~/.agents/skills` and note the skills that apply
    (`frontend-interaction-patterns`, `verify-ui-live`, `ios-pwa-dock`, and others) in its `AGENTS.md`
    (the same file as `CLAUDE.md`).
    Done when: the skill-fit note is in the app's AGENTS.md.
12. **Verify live, with `verify-ui-live`.** The app is reachable through its tunnel hostname, the backup is
    on the NAS, and the containers return after `systemctl restart docker` (or a coordinated
    `wsl --shutdown`). The live names and ports then show in `~/.claude/FLEET.md`.
    Done when: live, backed up, and self-healing, each shown by a command.
13. **Wrap up.** When pausing or finishing, offer the **handoff** skill, and confirm `FEATURES.md` is current.
    Done when: everything shipped this session is ticked and new scope is added.

## Rules

- **Make one decision at a time, always with a recommended option.** Never dump a survey on the user.
- **Record every decision with its why and a "What would change the answer".** That field turns a future
  "should we do X?" into a one-line check instead of a re-argument.
- **Keep `FEATURES.md` as the living tracker of progress.** IMPLEMENTATION_PLAN.md holds the decisions.
- **Use the blessed default stack unless the user overrides it.** It is locked in SYSTEM_SPEC §2, so every
  app shares one backup and restore pipeline.
- **Keep project code in `~/projects/<app>` inside WSL2, never under `/mnt/c`.** `/mnt/c` is a
  performance trap.
- **Run Docker CE (systemd-managed), not Docker Desktop, with `restart: unless-stopped` everywhere.** The
  fleet must come back on its own after a restart.
- **Make the backup a `db-backup` sidecar, not a host systemd timer.** The sidecar migrates *with* the app.
- **Verify, never assume.** Typecheck, test, build, and launch before calling anything done; when the UI
  cannot be driven headlessly, ask the user for a screenshot.
- **Treat rebuilds, redeploys, and commits as milestone actions.** Ask *"redeploy now, or after a few more
  tweaks?"*, because a prod redeploy per one-line tweak is the most common token sink.
- **Never commit secrets or real user data, and never commit or push unasked.** Use anonymized fixtures.
- **Lock the UI language and the identifier language early.** Mixed languages drift and are costly to fix.
- **If wireframes were provided, match them 1:1.** A divergence is a defect, not a judgment call.

## Gotchas

- **The build nails layout and logic but feels flat and "almost right".** Visual detail was dropped; study
  each wireframe for the items in `references/implementation.md` before coding the screen.
- **An installable phone app ships with a misplaced bottom dock.** Apply the `ios-pwa-dock` §1 shell
  checklist before the first screen is built.
- **A worker's scheduled jobs silently never run.** Every `cron.schedule` needs an explicit
  `missedExecutionTolerance` (see `references/stack.md` and `backend-patterns`).
- **The backup sidecar fails on its first start.** Stage `./secrets/{nas_known_hosts,nas_backup_key}`
  (0600, gitignored) **before** the first container start.
- **The NAS dead-man's-switch alerts for a healthy app.** The glob in `nas-deadman-check.sh` does not match
  the dump names; fix the glob when you flip the line to `enabled=1`.
- **The dev container misbehaves (docs clobbered, missing deps, stale CSS, HMR dead on the phone).** Read
  the Dockerized-Next dev-loop gotchas at the end of `NEW_APP_CHECKLIST.md`.

## References

- `references/stack.md`: the early locks, the default (blessed) stack, the non-negotiables, and the stack questions.
- `references/spec-docs.md`: what each canonical doc contains, and the decision record format.
- `references/design-step.md`: both design paths, the token-export prompt, the file exchange, and the
  palette-first iteration protocol.
- `references/implementation.md`: the build phase in full, including wireframe fidelity and wrap-up.
- `references/teardown.md`: how to tear down a scratch or verification app completely.
- `references/history.md`: the merged sources and their old names, and why the dock checklist is mandatory.
