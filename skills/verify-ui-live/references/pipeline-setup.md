# Setting up the live-verify pipeline

The detail behind the pipeline steps in `SKILL.md`: the dev container, the tunnel, the browser, and when a change needs action before it is live.

## The core trick

**One container serves two audiences** - but only while the Cloudflare
tunnel origin points at the dev container. The dev server (hot reload, source
bind-mounted) is published to the host (e.g. Aro: `localhost:3007`) AND is the tunnel's
origin (`web:3000`), so measuring the DOM on localhost inspects exactly what the user
sees at the public hostname. No build/upload/deploy. **In steady-state prod the tunnel
serves `web-prod:3000` instead** - then localhost dev is a *separate* process from
what's public; verify against whichever container the tunnel origin currently targets
(check the dashboard origin URL; see `fleet-ops`).

Three pieces: a hot-reload dev container, a tunnel pointed at *that* container, and an
attached browser.

## A. The hot-reload dev container

Run the framework's **dev server** (not a production build) in the container, source
bind-mounted. Reference shape (Aro's `web` service):

```yaml
services:
  web:
    build: { context: ., dockerfile: web.Dockerfile }
    ports:
      - "3007:3000"            # host:container - pick a free HOST port (fleet-ops)
    environment:
      NODE_ENV: development
      TZ: Europe/Madrid
    env_file: [.env]
    volumes:
      - ./:/app                # bind-mount source → host edits reach the running process
      - /app/node_modules      # anonymous volumes: keep the container's Linux-built deps…
      - /app/.next             # …and build cache, so the host dir can't shadow them
    command: npm run dev       # dev server (HMR), NOT next build/start
    restart: unless-stopped
```

- **`./:/app`** makes hot reload possible; the anonymous `node_modules`/`.next` volumes
  are the classic "works on host, not in container" fix.
- Repos live WSL-native (`~/projects/*`) where inotify works - **no polling needed**.
  Only a legacy `/mnt/c` mount needs `WATCHPACK_POLLING: "true"`, and then webpack dev
  only - Turbopack has no polling fallback and silently stops reloading (see
  `references/gotchas-and-perf.md`).

Bring up with `docker compose up -d web-dev`, then run the hot-reload end-to-end check
(gotchas list below).

## B. Give the tunnel a DEV hostname (dual-hostname pattern)

Preferred shape (2026-07-06): the app's one tunnel carries TWO permanent hostnames - 
`dev-<app>.example.com → web:3000` (this hot-reload container) and
`<app>.example.com → web-prod:3000`. Both behind Access; configured once in the Zero
Trust dashboard (compose service + container port as origin - never the host port).
During early development the user opens the DEV hostname on their phone: edits are
live there in ~1s, no deploys, while prod (if any) stays untouched on the real URL.
Full runbook in `fleet-ops`. The "localhost == what the user sees"
identity holds on the dev hostname whenever the dev profile is up.

## C. Agent-drivable browser = `ui-check` (headless, on the box)

No desktop browser exists in this workflow (the box is driven over SSH / Remote
Control). `ui-check` (workflow step 0) is the browser: headless Chromium renders the
app, `--login` handles the auth cookie, `--js`/`--selector` measure, `--shot` for
screenshots. Multi-step flows (uploads, wizard click-throughs, commit) → the
`chrome-devtools-axi` CLI or a committed `e2e/*.e2e.py` script - see workflow step 0b.

## When a change is live vs when you must act first

- **`.tsx`/`.ts`/CSS edit** → live the instant you save. Just verify.
- **Schema change** → generate + apply the migration or the app errors:
  `docker exec <web-container> npm run db:generate && docker exec <web-container> npm run db:migrate`
- **New dependency** → baked image lacks it: `docker compose build web-dev && docker compose up -d web-dev`.
- **Pure logic** → unit tests instead of the browser: `docker exec <web-container> npx vitest run`.

## Dev server vs production build

Measurement is build-agnostic; what changes is iteration speed. Dev server: edit →
live in ~1s (keep while building features). Prod build: every change costs
`next build` (~30-90s) + restart (switch once the feature set stabilizes and you want
runtime speed). **Avoid the hybrid** (prod on the tunnel + separate dev on localhost) - 
then what you measure isn't what the user sees, which breaks the whole point.

A growing app makes the dev server feel slow - that's on-demand route compilation, not
a code perf bug. Diagnose from container logs before optimizing anything:
`references/gotchas-and-perf.md`.

## Applies beyond Aro

Any tunneled self-hosted dev app on this box (finance-proj/Caudal at
`budget.example.com → web-prod:3000` in steady state, etc.). Per-project specifics (hostname, host port,
container names) live in each project's compose + the `fleet-ops`
registry.
