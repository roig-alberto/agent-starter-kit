# Phase 1: requirements and stack

Invoke the **grill-me** skill with the project idea. Walk the whole design tree one question at a time,
resolving dependencies: audience and scope, platform, persistence and hosting, **the full stack**
(frontend, backend, DB and ORM, auth, validation, deploy), the data model, domain rules, edge cases, and
what is explicitly out of scope. Each answer is a locked decision with a recorded reason. Do not stop until
the user agrees the design tree is walked.

## Lock these early

They are cheap to ask now and expensive to discover later.

- **The UI toolkit explicitly** (not just "Tailwind": daisyUI vs shadcn vs headless), so it is never
  re-asked mid-build.
- **Reference apps: 1-3 existing apps the user admires, and *what specifically* about each.** These
  anchor the design and surface features the user actually wants (for a finance app: YNAB's "give every
  euro a job", Monarch's net-worth trend, Copilot's auto-categorization). Save the names and the borrowed
  ideas for the DESIGN_BRIEF and the design step, and ask for screenshots if the user has them.
- **The #1 usability priority**, and, for apps used infrequently, **what makes the core flow effortless
  enough to come back to.** Capture it as a top-level product principle; ease of use is a requirement,
  not polish.
- **Adjacent "tempting but out-of-scope" wants** (for example a net-worth or wealth view on a budgeting
  app). Park each one in the backlog with a reason, so good ideas are not lost and v1 does not bloat.
- **The load-bearing external dependency.** Ask "What single external thing, if it doesn't work, makes
  this project pointless?" (for example iOS Web Push for an engagement-driven PWA, a third-party API with
  no alternative, or a platform capability the OS may not support). Name it now; it must be **proven end
  to end in Phase 4 before any feature is built on top of it.**

## Offer the proven default stack first

Do not silently impose it. Ask with AskUserQuestion whether to use the **default stack below** wholesale
or choose a different one, and allow diverging per layer. Deep-dive only the layers the user wants to
change.

> **Default stack (Recommended) = the blessed stack of `new-app`**
> (single source of truth: dev-system SYSTEM_SPEC §2; if this list and that spec ever
> disagree, the spec wins):
> - **Frontend**: Next.js (App Router) + TypeScript + Tailwind CSS + **shadcn/ui**; installable PWA.
> - **Architecture**: **Next monolith**: server components and actions, direct DB via Drizzle; one
>   container, one port, and one tunnel per app, no API boilerplate. Add a separate **worker**
>   container (`node-cron`) only if the app has scheduled jobs.
> - **DB**: PostgreSQL + **Drizzle ORM** (`postgres.js` driver) + Drizzle Kit migrations.
> - **Validation**: Zod (schemas shared between routes and forms).
> - **Auth**: a single password (`@node-rs/argon2`, the hash stored **base64** in env to survive `$`
>   interpolation) + a signed HTTP-only **HMAC cookie session** (edge-safe, sliding expiry).
> - **Hosting**: `docker-compose` (hot-reload dev container) on the home base, a **Cloudflare
>   Tunnel** (outbound, no open ports) behind **Cloudflare Access** (Zero Trust), NAS backup
>   baked in. No Node on the host. Code lives WSL-native in `~/projects/<app>`.
> - **Tests**: vitest for pure logic. All URLs are relative; absolutes come from env (`BASE_URL`).
>
> This default fits a single-user, low-frequency, privacy-conservative app. Steer away from it
> when the project differs materially (multi-user or SaaS, native mobile, heavy realtime, serverless,
> static content and SEO, a different language ecosystem), and then grill the stack from scratch.

## Stack questions to resolve

Each answer is a locked decision with a recorded reason. Lead with the *deciding criterion*, not just the
option list.

- **Platform and scope:** web or PWA vs native vs desktop; single-user vs multi-user; online-only vs
  offline.
- **Framework:** Next.js (unified front and back, SSR and SEO) vs a Vite SPA with a small API (lighter).
  Criterion: if you need SSR, SEO, or one TS codebase, use Next; for a pure app shell hitting an API, use
  Vite with Hono or Express.
- **UI toolkit (pin it explicitly):** **shadcn/ui (the blessed default)** vs daisyUI (velocity,
  CRUD-shaped screens) vs plain Tailwind or headless. Criterion: if the visual bar is premium,
  Monarch-level *from day one*, shadcn or headless avoids override fatigue later.
- **DB and ORM: SQLite vs PostgreSQL.** Default to **SQLite** for solo, self-hosted, low-write apps
  *unless* you need native `DECIMAL` (money apps), multiple processes writing (for example a separate
  worker), or real concurrency; then use Postgres. Drizzle ORM either way. The blessed stack picks
  Postgres so every app shares one backup and restore pipeline; divergence to SQLite is allowed but must
  be argued.
- **Background jobs:** is there any scheduled or recurring work? If yes, add a separate `worker`
  container (`node-cron`); if none, do not add the container. If you DO add one, every `cron.schedule`
  needs an explicit `missedExecutionTolerance`, because the 1000 ms default silently drops every tick on
  this box (`backend-patterns`, section Background jobs).
- **Auth:** a single password with a signed cookie (only behind an edge gate like Cloudflare Access) vs
  passkey or WebAuthn with rate limiting (open internet) vs real multi-user auth.
- **Validation:** Zod, with schemas shared between client and server (the default).
- **Hosting and deploy:** self-hosted docker-compose with a Cloudflare Tunnel and Access vs cloud or
  serverless vs static. All URLs are relative; absolutes come from env (`BASE_URL`).

**Gate:** the stack and the core domain decisions are explicit and agreed.

## Blessed default stack and non-negotiables (from the old blessed-stack reference)

The blessed default stack (opinionated, overridable) is locked in SYSTEM_SPEC §2: Next.js App Router,
TypeScript, Tailwind, **shadcn/ui**, Postgres, **Drizzle**, Docker Compose (hot reload), a Cloudflare tunnel,
and NAS backup.

**The architecture is a Next monolith**: server components and actions, with direct DB access via Drizzle.
That means one container, one port, and one tunnel per app, with no API boilerplate. **Ask about a front/back
split only** for an ML-backend or multi-client app. This is the one architecture question asked at creation
time.

Non-negotiables (from SYSTEM_SPEC):

- Project code lives in `~/projects` **inside WSL2**, never under `/mnt/c`.
- Docker **CE** (systemd-managed), **not** Docker Desktop. `restart: unless-stopped` everywhere.
- The backup is a **`db-backup` sidecar** (it still migrates *with* the app), not a host systemd timer.
- The shared NAS target, set up once: `<NAS_IP>`, SFTP, user `<backup user>`, folder `<share>`, path
  `nas:/backups/<app>`. The Telegram chat_id is `<TELEGRAM_CHAT_ID>`. `~/.claude/ENVIRONMENT.md` is the canonical
  card for these facts.
