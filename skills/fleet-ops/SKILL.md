---
name: fleet-ops
description: >-
  TEMPLATE to adapt: host ports, tunnels or reverse proxies, RAM and disk pressure, and packaged third-party images
  on your own self-hosted box. Use when mapping a host port, 'port already allocated', 'expose this', 'set up a
  tunnel', 'redeploy prod', "the hostname doesn't resolve", the box is slow, 'memory/RAM is full', 'disk is full',
  'docker prune', stacks `Exited` after a Docker crash, 'add a health check', 'self-host X'. NOT for your own apps'
  code (use one-shot or new-app) or for app tests (use testing).
---

# Fleet ops: ports, tunnels, resources, packaged images (template)

This is a template. It keeps the shape and the general rules of a working fleet-ops skill from a self-hosted Docker
box; every `<placeholder>` is a fact of YOUR machine to fill in, and every "Example:" shows what the original box
wrote there. Delete what you do not run. Once filled, it prevents three silent failures: a host port collision that
stops a project from starting, a tunnel or proxy that serves the wrong app, and a blind prune that deletes a stopped
app's data. Live facts (ports, containers, hostnames) belong in a generated file (`~/.claude/FLEET.md` from
`~/.claude/scripts/fleet-facts.py`), never restated here.

## Part 1: host ports and the public path

Pick a host port:

1. Run `python3 ~/.claude/scripts/fleet-facts.py` and read "Claimed host ports" in `~/.claude/FLEET.md`. Stopped
   containers count: they re-claim their port when they start.
2. Read the reserved table in `references/port-registry.md` (ports of containers that are often removed).
3. Pick a port in neither list. Keep the container port conventional (3000, 5432); shift only the host side, bound to
   `127.0.0.1`.
4. A new long-term reservation goes into the reserved table in the same commit.

Done when: `port is already allocated` does not appear on `docker compose up`.

The public path (fill in: `<Cloudflare tunnel plus Access | Tailscale serve | a reverse proxy>`). Full runbook in
`references/cloudflare-tunnel.md`. General rules that held on the original box:

- Point the public hostname at the container port over the compose network (`web-prod:3000`), never at a host port.
- Read the tunnel or proxy token from the app's `.env` (`env_file:`), never from a shell variable: compose gives the
  shell precedence, so an inherited variable silently joins the wrong tunnel.
- Build and smoke-test the prod container before you point the hostname at it; flipping first serves a 502.
- Example: "a public 302 to the login page proves nothing, because the edge answers it even with a dead connector;
  check the connector's own log for this hostname."

Done when: `<your check that the hostname reaches THIS app, for example getent hosts plus a curl that ends at your
login page>` passes, and FLEET.md is regenerated.

Compose traps that fail silently (true on any Docker host):

- Renaming a service breaks every hardcoded network target; keep the old name as a network alias.
- `docker compose restart` does not reload `env_file`; use `up -d --force-recreate`.
- `env_file` interpolates `$`: store hashes base64-encoded or escape `$` as `$$`.
- An inline comment on an `.env` line becomes part of the value.

## Part 2: RAM and disk pressure

1. Diagnose first; RAM and disk are different problems:
   ```sh
   free -h            # RAM: "available" and swap used
   df -h /            # disk
   docker system df   # images, containers, volumes, build cache
   docker stats --no-stream --format '{{.MemUsage}}\t{{.Name}}' | sort -h -r | head -30
   ```
2. RAM: stop idle dev containers first. Example: "`-dev` containers are safe to stop; `-prod` and `-db` stay up."
   Your naming rule: `<fill in>`.
3. Disk, safest first: `docker builder prune -f`, then `docker image prune -f`, then volumes one by one after
   `docker volume inspect` proves each is a throwaway (node_modules, build cache).

Done when: swap drains and every live app is still up (`<your list of must-stay-up containers>`).

Rules:

- Never `docker volume prune`: it deletes every volume whose container is merely stopped, databases included.
- Never stop `<your live app, database, tunnel and monitoring containers>`.
- A long-running dev server leaks with uptime; restart it periodically.

## Part 3: packaged third-party images

A prebuilt image (a monitoring panel, a password manager, any self-hosted app) gets one lean compose file, not the
`new-app` flow.

- Pin the image as `tag@sha256:...` right after the first pull.
- Bind the local port to `127.0.0.1:` only; the public path is your tunnel or proxy with its own login.
- SQLite apps: back up the whole data dir (the db and its WAL together), never the db file alone.
- Set any app-generated encryption key explicitly in `.env`, or a restore yields undecryptable data.
- Never mount the raw Docker socket into an internet-facing container; use a socket proxy.
- Register the app everywhere in the same change: `<your backup list, rebuild runbook, port registry, monitoring>`.

## Gotchas

- Example: "edits invisible through the tunnel but fine on localhost: the CDN cached an API response with no
  Cache-Control; add a bypass rule and purge once."
- Example: "every hostname is down but the containers are fine: suspect the ISP before restarting anything."
- Example: "a new Docker bridge network took the home LAN's address range: pin `default-address-pools` in Docker's
  daemon.json."
- `<add a gotcha each time something cost you real time on this box>`

## References

- `references/port-registry.md`: your port conventions and reserved ports (template).
- `references/cloudflare-tunnel.md`: your public-path runbook (template).
