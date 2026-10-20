# new-app history

## Merged sources

`new-app` merges two skills (2026-10-15): `new-project` (the interview, the canonical docs, the design step,
and the build plan) and `bootstrap-orchestrator` (the container bootstrap on this box). Names the sources
used that now live elsewhere:

- `phased-plan` is now `plan`; `ui-design-references` is now part of `frontend-design`.
- `docker-ports-and-tunnels` and `selfhosted-panels` are now `fleet-ops`. The port registry was
  `references/port-registry.md` in `docker-ports-and-tunnels`.
- `nas-offsite-backup` is now `backups-and-alerts` (not in this kit).
- `proxmox-portability` and `app-migration` are now `portability`.
- `references/blessed-stack.md` (bootstrap-orchestrator) is now the last section of `references/stack.md`.

## new-project: the bottom dock bug recurred across apps

For an installable phone app, apply the `ios-pwa-dock` §1 shell checklist before the first screen: the
dock bug recurred in 8 apps without it.

## 2026-10-16: one hostname, and the backup sidecar inside the templates

A plan review of Agent Factory's go-live steps (PLAN.md 9.8 and 9.9) found the bootstrap templates could not
do what this skill asked: dev and prod shared the service names `web` and `db` and the `db_data` volume, so
the prod profile replaced the dev containers and shared their database; the only `cloudflared` was in the
prod profile, so the `dev-<app>` hostname had no tunnel before prod; and the template had no backup sidecar,
only the older in-app wiring. The user decided (2026-10-16): fix the templates in dev-system, and drop the
dev hostname as loop did (dev is localhost only). The templates now follow shelf's split (`web` + `db-dev`
in dev; `web-prod`, `db`, `cloudflared-prod`, `db-backup-prod` in prod) and carry `scripts/backup.sh`.
The old step said "create BOTH hostnames on day one" and checked `dev-<app>` past Access; the backup check
was `backup:once`, a script name the templates never had.
The replaced wording, kept for reference: step 7 said copy `bootstrap/templates/*`; step 8 mapped `dev-<app>`
to `web:3000`; step 9 said merge `backup-template/.env.snippet` and `docker-compose.snippet.yml`. Those
snippets still exist in dev-system for migrating an older app, but a new app gets the sidecar from the
templates.

## 2026-10-16: frontmatter fixed for the validator

Removed what failed `quick_validate`: in new-app the Claude-only `argument-hint: "One-line description of the project to build"`; in skills-audit `disable-model-invocation: true` (the user never types skill names, so a hidden skill never runs); in create-verification-skill the angle brackets in the description (`.claude/skills/verify-<app>/` is still in the body); in new-app the trigger "bootstrap <name>" became "bootstrap my-app" for the same reason.
