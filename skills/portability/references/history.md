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
