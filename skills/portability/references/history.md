# History

This skill merged three older skills on 2026-10-15: `proxmox-portability` (the invariants and the sync
checklist), `app-migration` (the migration protocol) and `dependency-updates` (the bump recipe). Old
cross-reference names map to new skills: `phased-plan` is `plan`; `nas-offsite-backup` and
`syno-nas-sftp-ops` are `backups-and-alerts` (not in this kit); `docker-ports-and-tunnels` and `selfhosted-panels` are
`fleet-ops`; `security-posture` and `openbao-secrets` are `security` (not in this kit); `bootstrap-orchestrator` is `new-app`.

## From proxmox-portability

### Dev and prod sharing a volume lost real user data (closet, 2026-07-27)

Two services mounting the same store (worst with an in-memory-cached JSON file like closet's `db.json`)
each cache and serialize writes to the SAME file, so a dev write (or a test hit against the dev API)
silently overwrites prod. closet's `api-dev` + `prod` shared `armario_data` until a dev write took out a
user's real template that NO backup held (it never persisted stably). Fix: `api-dev` on its own
`armario_data_dev` (scratch, unbacked, seeded once from prod's `db.json`). Real user data was lost,
unrecoverable.

### Superseded pin examples (the old invariant 2 text)

"Pin to an exact patch (e.g. `postgres:16.14-alpine`, `node:22.23.1-alpine`, `rclone/rclone:1.74.3`,
`cloudflare/cloudflared:2026.6.1`)." The current tags are in `~/.claude/FLEET.md`; the pin locations are in
`references/pin-sync.md`.

## From app-migration

### The invariant number for the compose project name

The old app-migration gotcha for a repo moved from /mnt/c called "pin the compose project name"
invariant 6. In the invariant list it is number 7 (number 6 is token tunnels). The merged skill uses 7.

## From dependency-updates

### Old pin-sync table (snapshot; current tags live in FLEET.md)

| Pin | Lives in |
|---|---|
| `postgres:16.14-alpine` | each app's compose (db + db-backup) · dev-system REBUILD.md · restore-test.sh `PG_IMAGE` · proxmox-portability skill text |
| `node:*-alpine` / `node:*-bookworm-slim` | compose (web/worker) · Dockerfiles (all stages) - note apps differ (Aro 22.x, Caudal/closet 20.x; Shelf `bookworm-slim` for glibc) |
| `cloudflare/cloudflared` | each app's compose · bootstrap templates |
| `rclone/rclone` | closet compose · backup-template |
| npm deps | app package.json + lock - per app, never "while I'm here" across apps |

The proxmox-portability skill no longer lists tags (2026-10-15), so it is no longer a pin location.

### The restore test on a moving Postgres tag

A grep on 2026-10-15 found dev-system `restore-test.sh` with `PG_IMAGE=postgres:16-alpine`, a moving tag,
so the restore test could pass against a different Postgres patch than prod runs. A later check the same
day found it pinned to `postgres:16.14-alpine`. The lesson: a pin location that no one greps drifts, which
is why every bump ends with the fleet grep in `references/pin-sync.md`.

### The Next 14 to 15 doc sweep

After the finance-proj Next 15 bump, the audit caught README and CLAUDE.md still saying Next 14. Hence the
rule: update docs IN the same change.

### The shadowed `node_modules` (superhuman-mvp, 2026-07-18)

Adding shadcn + tw-animate-css: `npm install` on the host did not reach the dev container, because the
anonymous `- /app/node_modules` volume shadows the host's. Symptom: a 500 / "Can't resolve `<pkg>`" for a
package plainly in `package.json`. Fix: `docker exec <app>-web-dev-1 npm install`, then restart that
container.

## Before the native Ubuntu rebuild (retired text, 2026-10-27)

On 2026-10-27 the fleet moved from WSL2 on Windows to a native Ubuntu host, and every app moved from Cloudflare tunnels to Tailscale sidecars. The lines below were true on the WSL2 host and are kept verbatim.

### Former description

Keeps the self-hosted fleet movable to a fresh host (WSL2 to bare-metal Proxmox). Use WHENEVER editing a
docker-compose.yml or Dockerfile, adding or removing a service, volume, port, image or secret, wiring a
backup, touching host pieces (systemd, tg-alert, NAS creds), relocating anything stateful, or updating
any pin or framework. Trigger on 'add a service', 'map a volume', 'change the backup', 'edit
the compose', 'bump the image', "migrate", "move the app", "host move", "onto Docker CE", "into WSL",
"Proxmox migration", "update X", "upgrade Next/node/postgres", "npm audit", "are my deps outdated", or a
CVE ask. NOT for ports or tunnels (use fleet-ops), the backup pipeline (use backups-and-alerts), or
scaffolding a new app (use new-app).

### Former invariant 6, migration rule and gotcha

6. **Tunnels are named and token-based** (`TUNNEL_TOKEN`), never a host-bound quick tunnel. A token
   tunnel reconnects from any host.

- Follow the existing recipe for the migration type; each one already paid for its mistakes. An existing
  app onto Docker CE follows the Phase-3/closet migration recipe in dev-system
  (`~/projects/dev-system`, PLAN.md and REBUILD.md). The fleet onto Proxmox
  (after Phase 7) is a mechanical replay of dev-system `REBUILD.md` plus PLAN.md, which is what part 1
  protects. A repo from /mnt/c to WSL-native is small but stateful-adjacent; see Gotchas.

- **A repo moved from /mnt/c into WSL misbehaves.** Remove `WATCHPACK_POLLING`, pin the compose project
  name (invariant 7), and replace Windows path references with WSL paths in scripts and skills.

- **The Proxmox plan seems to require heroics.** An invariant was violated somewhere; fix it, and the move
  becomes a replay of REBUILD.md again.

Former dev-system path: `~/projects/dev-system`. Former Part 2 heading: "migrations (an app onto Docker CE, a repo into WSL, the fleet onto Proxmox)". The `cloudflare/cloudflared` pin row (each app's compose and the bootstrap templates) left `references/pin-sync.md` with the tunnels.
Former invariant 1 example: never `/mnt/c/...`. Former fleet grep after a bump: `grep -rn "<old-tag>" ~/projects/*/docker-compose.yml ~/projects/*/*Dockerfile* ~/projects/dev-system ~/.agents/skills`.
