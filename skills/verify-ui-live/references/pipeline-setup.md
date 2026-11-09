# Setting up the live-verify pipeline

The detail behind the pipeline steps in `SKILL.md`: the dev container, the tailnet hostname, the browser, and when a change needs action before it is live.

## The core trick

**Two containers, two audiences.** The dev server (hot reload, source bind-mounted) is
published to the host only (e.g. Aro: `localhost:3007`); measuring the DOM there shows the
change seconds after the edit. The phone reaches the app through its Tailscale sidecar,
whose `tailscale serve` targets the prod container (`web-prod:3000`). So a dev pass shows
what the phone will see after the next prod rebuild, and a check of what the phone sees
today goes to the tailnet hostname (`https://<app>.<tailnet>.ts.net`, listed in
`~/.claude/FLEET.md`). The box itself is on the tailnet, so `curl` and the headless
browser reach that hostname. Confirm the serve target with
`docker exec <app>-tailscale-prod-1 tailscale serve status` (see `fleet-ops`).

Three pieces: a hot-reload dev container, the tailnet hostname for prod, and a headless
browser.

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
- Repos live in `~/projects/*` on the native Linux filesystem, where inotify works, so
  **no polling is needed**. `WATCHPACK_POLLING: "true"` is webpack-only; Turbopack has no
  polling fallback (see `references/gotchas-and-perf.md`).

Bring up with `docker compose up -d web-dev`, then run the hot-reload end-to-end check
(gotchas list below).

## B. One tailnet hostname, for prod

Each app has one tailnet hostname, served by its Tailscale sidecar to `web-prod:3000`
(the compose service and container port, never a host port). There is no dev hostname;
dev is localhost only. To let the user see a change on the phone, rebuild prod
(ask first), then verify on the tailnet hostname. Sidecar setup: `new-app` step 8 and
`fleet-ops`.

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
runtime speed). Before telling the user a change is on the phone, measure the prod
container through the tailnet hostname, because the dev pass measured a different process.

A growing app makes the dev server feel slow - that's on-demand route compilation, not
a code perf bug. Diagnose from container logs before optimizing anything:
`references/gotchas-and-perf.md`.

## Applies beyond Aro

Any self-hosted app on this box with a Tailscale sidecar. Per-project specifics
(hostname, host port, container names) live in each project's compose and in
`~/.claude/FLEET.md`.
