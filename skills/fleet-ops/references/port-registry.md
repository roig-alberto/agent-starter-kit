# Port registry (template)

Fill this in for your box. Live port claims are generated into `~/.claude/FLEET.md`; this file keeps only what a
generator cannot see: conventions, and ports reserved by containers that are often removed rather than stopped.

## Conventions

- Container ports stay conventional (3000 for a web app, 5432 for Postgres); only the host side shifts.
- Dev ports bind to `127.0.0.1`. Example: "dev web apps take 3000-3099, dev databases 5400-5499."
- Prod maps no host port when a tunnel or proxy reaches it over the compose network.

## Reserved ports

| Port | App | Why it is reserved |
|---|---|---|
| `<port>` | `<app>` | `<for example: a dev profile that is usually down>` |

## Hostnames

| App | Hostname | Notes |
|---|---|---|
| `<app>` | `<app>.<your-domain>` | `<one hostname with a dev/prod flip, or a dev- twin during a v1 build>` |
