---
name: portability
description: >-
  Keeps the self-hosted fleet movable to a fresh host (WSL2 to bare-metal Proxmox). Use WHENEVER editing a
  docker-compose.yml or Dockerfile, adding or removing a service, volume, port, image or secret, wiring a
  backup, touching host pieces (systemd, tg-alert, NAS creds), relocating anything stateful, or updating
  any pin or framework. Trigger on 'add a service', 'map a volume', 'change the backup', 'edit
  the compose', 'bump the image', "migrate", "move the app", "host move", "onto Docker CE", "into WSL",
  "Proxmox migration", "update X", "upgrade Next/node/postgres", "npm audit", "are my deps outdated", or a
  CVE ask. NOT for ports or tunnels (use fleet-ops), the backup pipeline (use backups-and-alerts), or
  scaffolding a new app (use new-app).
---

# portability: keep the fleet movable

Every app must rebuild on a fresh host (the future Proxmox box) from git repo + NAS secrets bundle + NAS
data dump + `docker compose up`, as dev-system `REBUILD.md` describes. This skill keeps that true in three
situations: any infra change (part 1), a migration (part 2), and a dependency or image bump (part 3). It
prevents the drift that turns a host move into heroics: host-only paths and secrets, moving tags,
half-applied bumps, and a `REBUILD.md` that lies.

## Part 1: the invariants, on every infra change

1. **No host-absolute paths in compose.** Secrets and config a container needs live in the app's in-repo
   `./secrets/` (gitignored), referenced relatively, never `/mnt/c/...`, `/home/<user>/...`,
   `<alert-token-file>`, or an absolute `~/.config/...`. Named volumes and `./` paths move with the
   repo; host paths do not.
2. **Pin every image to an exact patch**, for example `postgres:16.14-alpine`. No `:latest` and no moving
   `:NN-alpine` tag, because a moving tag rebuilds into something different on the new host.
3. **The Postgres major must match the dumps (16).** A restore into another major is not guaranteed; the
   major procedure is in `references/pin-sync.md`.
4. **Every stateful volume is recoverable**, either dumped or synced to `nas:/backups/...` or trivially
   rebuildable. A new volume holding real state MUST join the backup pipeline, or it is lost on a move.
5. **No secret lives only on the box.** An app's `.env`/`./secrets/` is auto-covered by
   `scripts/secrets-backup.sh`; a NEW secret anywhere else on the host (`~/.config/*`, a new dir, a
   systemd EnvironmentFile) is added to `secrets-backup.sh` in the SAME change. Full rule in `security` (not in this kit).
6. **Tunnels are named and token-based** (`TUNNEL_TOKEN`), never a host-bound quick tunnel. A token
   tunnel reconnects from any host.
7. **Pin the compose project name** (`name: <app>`). A folder rename or relocation then cannot fork a
   second stack.
8. **Split dev and prod by profiles** (`profiles: [dev]` / `[prod]`). Profile-less services are always on
   and leak into `--profile prod`.
9. **Dev and prod NEVER share a stateful data volume**; dev gets its own scratch volume. Two services that
   cache the same store each serialize writes to the same file, so a dev write silently overwrites prod.
   To read or write PROD data, go THROUGH prod (login plus an authed request), never via the dev service.

Steps:

1. **FLAG** each violation to the user with its fix; never silently accept it. Example wording is in
   `references/sync-checklist.md`. Done when: every violation in the change is fixed or named to the user.
2. **SYNC** the dev-system rebuild files with `references/sync-checklist.md`. Done when: each checklist
   row that the change triggers is updated, and `python3 ~/.claude/scripts/fleet-facts.py` has rerun.

## Part 2: migrations (an app onto Docker CE, a repo into WSL, the fleet onto Proxmox)

Migrations run 40 steps, days apart, across sessions, so drift bites hardest here. State lives on disk,
not in the conversation, and every phase ends re-verified, not just "moved".

1. **Write `MIGRATION.md` first**, in the app's repo (or in dev-system for fleet moves), through the `plan`
   skill. Add three parts to the standard plan: an **inventory** of every stateful thing that must
   survive (volumes, secrets, env files, tunnel tokens, cron and systemd units, DNS and hostnames, backup
   wiring, AND off-repo host secrets such as `~/.config/ui-check/*.pw` and the backup keys in
   `<key folder>`), checked against the nine invariants with anything host-absolute or unpinned fixed
   BEFORE the move; a **rollback line** per phase (usually the old host is still intact, because you
   never destroy the source until the destination is verified); and a **status** per phase, updated the
   moment it changes. Done when: the file exists with all three parts.
2. **Back up before touching anything.** Take a fresh dump and confirm it landed on the NAS with the verify
   section of `backups-and-alerts` (not in this kit). Done when: the fresh dump is listed on the NAS.
3. **Move, verify, and only then cut over.** Bring each phase up at the destination and verify it end to
   end: the app is reachable, the data is present, the backup sidecar runs, and `restore-test` passes
   where it applies. Then repoint the tunnel or DNS, and only then retire the source. The verification
   commands live in `MIGRATION.md`, per phase. Done when: each phase's checks pass and its status says so.
4. **Sync the rebuild files as you go** (the SYNC step of part 1): REBUILD.md, secrets-backup,
   restore-test, nas-deadman-check, and the port registry. Done when: `REBUILD.md` describes the new home.

Rules:

- On resume, read `MIGRATION.md` FIRST and trust it over memory, then re-verify the last "done" phase
  cheaply. A phase can rot between sessions.
- Follow the existing recipe for the migration type; each one already paid for its mistakes. An existing
  app onto Docker CE follows the Phase-3/closet migration recipe in dev-system
  (`~/projects/dev-system`, PLAN.md and REBUILD.md). The fleet onto Proxmox
  (after Phase 7) is a mechanical replay of dev-system `REBUILD.md` plus PLAN.md, which is what part 1
  protects. A repo from /mnt/c to WSL-native is small but stateful-adjacent; see Gotchas.

## Part 3: dependency and image bumps

Everything is pinned on purpose, so a bump is manual and must land in EVERY place the pin is written.

Follow the order in `references/pin-sync.md` (backup before a major, `npm install` IN the container,
DEV first, then prod batched with other changes, then sync every pin location and tick `REBUILD.md`).
Confirm the running version with `docker exec <db> postgres --version` or `docker exec <web> node --version`.
Done when: dev tests and typecheck pass, prod runs the new version, and
`grep -rn "<old-tag>" ~/projects/*/docker-compose.yml ~/projects/*/*Dockerfile* ~/projects/dev-system ~/.agents/skills`
prints nothing.

Rules:

- **Postgres major equals dump major (16).** The db image is never bumped casually; follow the major
  procedure in `references/pin-sync.md`.
- **Pin to the exact new patch**, never `:latest` or a moving minor tag. A moving tag breaks invariant 2.
- **Framework majors get their own plan file** (the proven shape: finance-proj `PLAN-next15.md`) covering
  codemods, breaking changes and the doc sweep. Update README and AGENTS.md (the same file as `CLAUDE.md`)
  IN the same change.
- **One app per update session.** Cross-app "harmonizing" turns a 10-minute bump into a fleet incident.
- **Security patches land the minimal fix version**, not an opportunistic major.
- **No `npm audit fix --force`** and no Dependabot-style bulk bumps. It applies silent majors; this fleet
  updates deliberately, one thing at a time, verified.
- **Do not update `anki` or Docker-Desktop-era leftovers.** They are being retired, not maintained
  (dev-system PLAN.md Phase 7).

## Red flags

- A dev service mounts the prod data volume "just to read it". This lost real user data in closet.
- A bump is called done while README or AGENTS.md still names the old major (the Next 14 to 15 sweep).
- A bump is called done without the fleet grep. A missed pin location drifted before (`restore-test.sh`).

## Gotchas

- **A fresh-host prod `up` fails with `network monitoring declared as external, but could not be
  found`.** The external `monitoring` network must be created in `REBUILD.md` host bootstrap
  (`fleet-ops` owns the monitoring recipe).
- **A host-level piece exists only on the live host.** Capture every systemd unit, host script, or cron
  under `host/` or `systemd/` in dev-system with an install note.
- **Machine-local agent config (for example the `ha-mcp` MCP definition) is in no repo.** Record it in
  `REBUILD.md` and back its secret file up via `secrets-backup.sh`.
- **The Proxmox plan seems to require heroics.** An invariant was violated somewhere; fix it, and the move
  becomes a replay of REBUILD.md again.
- **A repo moved from /mnt/c into WSL misbehaves.** Remove `WATCHPACK_POLLING`, pin the compose project
  name (invariant 7), and replace Windows path references with WSL paths in scripts and skills.
- **A dev container returns a 500 or "Can't resolve `<pkg>`" for a package plainly in `package.json`.**
  The dev compose mounts an anonymous `- /app/node_modules` volume that shadows the host's, so `npm install`
  on the HOST never reaches it. Run `docker exec <app>-web-dev-1 npm install`, then restart that container
  (or recreate with `--renew-anon-volumes`). Prod bakes `node_modules` at build, so this only bites in dev.
- **`KEY=   # comment` in an `env_file` or `.env.example` sets the value to the comment text.** Put comments on their own line above the key, and check with `docker compose config | grep KEY`.

## References

- `references/sync-checklist.md`: what to update in dev-system for each kind of change, and where the
  rebuild files live. Read it on every infra change.
- `references/pin-sync.md`: every location each pin lives in, and the Postgres major procedure. Read it
  before any image bump.
- `references/history.md`: the incidents behind these rules, old pin tables, and the old skill names.

Current image tags per container are in `~/.claude/FLEET.md`.
