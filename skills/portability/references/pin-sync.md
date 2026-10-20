# The pin-sync map (a bump is not done until all match)

Locations verified 2026-10-15 with a grep of dev-system and the app compose files.

| Pin | Lives in |
|---|---|
| `postgres:16.x-alpine` | each app's compose (db + db-backup, dev and prod files) · dev-system `bootstrap/templates/docker-compose.{dev,prod}.yml` · `scripts/restore-test.sh` `PG_IMAGE` · `REBUILD.md` wherever it names the image |
| `node:*-alpine` / `node:*-bookworm-slim` | compose (web/worker) · Dockerfiles (all stages). Apps differ on purpose (Shelf uses `bookworm-slim` for glibc); read the current tags in FLEET.md |
| `cloudflare/cloudflared` | each app's compose · bootstrap templates |
| `rclone/rclone` | every rclone backup sidecar's compose (closet and the ops bundle) · backup-template |
| `tailscale/tailscale` | each compose that runs a tailscale sidecar |
| npm deps | the app's `package.json` + lock, per app, never "while I'm here" across apps |

After any image bump, grep the fleet so no copy is missed:
`grep -rn "<old-tag>" ~/projects/*/docker-compose.yml ~/projects/*/*Dockerfile* ~/projects/dev-system ~/.agents/skills`
Projects with split compose files (`docker-compose.dev.yml`, `docker-compose.prod.yml`) need
`~/projects/*/docker-compose*.yml` in that grep.

## Postgres major procedure

NAS dumps are pg16. Bumping to 17 requires:
1. restore-test still green against a 17 container FIRST;
2. then bump the app's db and db-backup images, restore-test `PG_IMAGE`, and `REBUILD.md` together;
3. then a fresh dump lands and restore-test passes again.

## Order of operations (per app), full form

1. Fresh backup verified on the NAS (`backup once` + `rclone lsl`) before majors.
2. Bump in compose/Dockerfile/package.json. `npm install` runs IN the container (deps are Linux-built):
   `docker compose run --rm web npm install <pkg>@<ver>`.
3. Rebuild and verify DEV first: `docker compose build web && docker compose up -d web`, then the
   AGENTS.md Commands block (tests + typecheck) and, for UI-touching bumps, `verify-ui-live`.
4. Then prod: `docker compose --profile prod up -d --build` (batch with other pending changes, no
   per-bump redeploys).
5. Sync the pin-sync map (grep above) and tick REBUILD.md.
6. Security patches (npm audit / CVE): the same flow, but land the minimal fix version, not an
   opportunistic major.
