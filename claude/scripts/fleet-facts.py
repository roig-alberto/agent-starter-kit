#!/usr/bin/env python3
"""Generate FLEET.md + fleet.json: the single source of truth for live fleet facts.

Reads the running system (docker inspect, cloudflared ingress logs, tailscale serve,
host listeners) and writes ~/.claude/FLEET.md and ~/.claude/fleet.json. Docs link here
instead of restating ports, containers, images, volumes, or hostnames.

Files are rewritten only when the facts change, so the Stop hook can run this every
turn without commit churn.

Usage: fleet-facts.py [--check]   (--check: exit 1 if the files are stale, write nothing)
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
OUT_MD = os.path.join(HOME, ".claude", "FLEET.md")
OUT_JSON = os.path.join(HOME, ".claude", "fleet.json")
INGRESS_RE = re.compile(r'hostname\\?":\\?"([^"\\]+)\\?".*?service\\?":\\?"([^"\\]+)')


def sh(args, timeout=20):
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout + r.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, str(e)


def containers():
    code, ids = sh(["docker", "ps", "-aq"])
    if code != 0:
        sys.exit(f"fleet-facts: docker ps failed: {ids.strip()}")
    ids = ids.split()
    if not ids:
        return []
    code, out = sh(["docker", "inspect", *ids], timeout=60)
    if code != 0:
        sys.exit(f"fleet-facts: docker inspect failed: {out[:200]}")
    return json.loads(out)


def ingress(name):
    _, out = sh(["docker", "logs", "--tail", "5000", name], timeout=30)
    lines = [l for l in out.splitlines() if "Updated to new configuration" in l]
    if not lines:
        return []
    cfg = lines[-1]
    # one hostname/service pair per ingress rule (the catch-all 404 has no hostname)
    rules = []
    for chunk in cfg.split("hostname")[1:]:
        m = INGRESS_RE.search("hostname" + chunk)
        if m:
            rules.append({"hostname": m.group(1), "service": m.group(2)})
    return rules


def tailscale(name):
    code, out = sh(["docker", "exec", name, "tailscale", "status", "--json"])
    if code != 0:
        return None
    try:
        dns = json.loads(out).get("Self", {}).get("DNSName", "").rstrip(".")
    except json.JSONDecodeError:
        return None
    code, out = sh(["docker", "exec", name, "tailscale", "serve", "status", "--json"])
    routes = []
    if code == 0:
        try:
            web = json.loads(out).get("Web", {}) or {}
            for hostport, cfg in sorted(web.items()):
                for path, h in (cfg.get("Handlers") or {}).items():
                    routes.append({"listen": hostport, "path": path, "proxy": h.get("Proxy", "")})
        except json.JSONDecodeError:
            pass
    return {"node": dns, "serve": routes}


def git_remote(path):
    code, out = sh(["git", "-C", path, "remote", "get-url", "origin"])
    if code == 0:
        return out.strip()
    return "no git" if not os.path.isdir(os.path.join(path, ".git")) else "no remote"


def repo_root(path):
    code, out = sh(["git", "-C", path, "rev-parse", "--show-toplevel"])
    return out.strip() if code == 0 else path


def host_listeners(docker_ports):
    """TCP listeners on the host that docker does not own (systemd services etc.)."""
    code, out = sh(["ss", "-ltnH"])
    if code != 0:
        return []
    seen = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        addr = parts[3]
        host, _, port = addr.rpartition(":")
        if not port.isdigit():
            continue
        p = int(port)
        if p in docker_ports or p >= 32768:
            continue
        seen.add((host.strip("[]"), p))
    return sorted(seen, key=lambda x: (x[1], x[0]))


def database(env):
    """host/name of the container's DATABASE_URL, never its credentials; None without one."""
    for kv in env or []:
        if kv.startswith("DATABASE_URL="):
            m = re.match(r"[a-z+]+://(?:[^@/]*@)?([^:/?]+)(?::\d+)?/([^?\s]+)", kv.split("=", 1)[1])
            return f"{m.group(2)} on {m.group(1)}" if m else None
    return None


def shared_db(containers):
    """Whether the project's dev and prod containers use the same database (2026-10-19: three apps shared one and no
    doc said so). Only the app's own services count (web*, worker*): a `-prod` service is prod, any other is dev (Loop's dev
    service is plain `web`). The db, backup and tunnel containers use the database but are neither."""
    app = [c for c in containers if c.get("db") and c["service"].startswith(("web", "worker"))]
    dev = {c["db"] for c in app if "prod" not in c["service"]}
    prod = {c["db"] for c in app if "prod" in c["service"]}
    if not dev or not prod:
        return None
    both = sorted(dev & prod)
    return f"dev and prod SHARE one database ({', '.join(f'`{d}`' for d in both)}): a dev write is a prod write" if both else "dev and prod use separate databases"


def collect():
    projects = {}
    docker_ports = set()
    for c in containers():
        labels = c["Config"].get("Labels") or {}
        proj = labels.get("com.docker.compose.project", "(no compose)")
        wd = labels.get("com.docker.compose.project.working_dir", "")
        ports = []
        for cport, binds in sorted((c["HostConfig"].get("PortBindings") or {}).items()):
            for b in binds or []:
                hp = b.get("HostPort")
                if hp:
                    docker_ports.add(int(hp))
                    ports.append(f"{b.get('HostIp') or '0.0.0.0'}:{hp}->{cport.split('/')[0]}")
        volumes = sorted(m.get("Name") for m in c.get("Mounts", []) if m.get("Type") == "volume")
        image = c["Config"]["Image"].split("@")[0]
        entry = {
            "name": c["Name"].lstrip("/"),
            "service": labels.get("com.docker.compose.service", ""),
            "image": image,
            "state": c["State"]["Status"],
            "ports": ports,
            "volumes": volumes,
            "db": database(c["Config"].get("Env")),
        }
        if "cloudflared" in image and c["State"]["Status"] == "running":
            entry["ingress"] = ingress(entry["name"])
        if image.startswith("tailscale/") and c["State"]["Status"] == "running":
            entry["tailnet"] = tailscale(entry["name"])
        p = projects.setdefault(proj, {"project": proj, "dir": "", "remote": "", "containers": []})
        if wd and not p["dir"]:
            root = repo_root(wd)
            p["dir"] = root.replace(HOME, "~")
            p["remote"] = git_remote(root)
        p["containers"].append(entry)
    for p in projects.values():
        p["containers"].sort(key=lambda e: e["name"])
    host = [{"bind": h, "port": port} for h, port in host_listeners(docker_ports)]
    return {
        "projects": [projects[k] for k in sorted(projects)],
        "host_listeners": host,
        "claimed_ports": sorted(docker_ports | {h["port"] for h in host}),
    }


def render(facts, stamp):
    out = [
        "# FLEET.md - live fleet facts (GENERATED, do not edit)",
        "",
        f"Generated {stamp} by `~/.claude/scripts/fleet-facts.py` from `docker inspect`, cloudflared",
        "ingress logs, `tailscale serve status`, and `ss -ltn`. Regenerate: `python3 ~/.claude/scripts/fleet-facts.py`.",
        "Docs point here; they never restate a port, container, image, volume, or hostname.",
        "Policy (port ranges, reserved ports, why) lives in `fleet-ops` `references/port-registry.md`.",
        "",
    ]
    for p in facts["projects"]:
        out.append(f"## {p['project']}")
        out.append("")
        out.append(f"Dir `{p['dir'] or '?'}` · remote `{p['remote'] or '?'}`")
        out.append("")
        out.append("| Container | State | Host ports | Image | Volumes |")
        out.append("|---|---|---|---|---|")
        for c in p["containers"]:
            ports = ", ".join(c["ports"]) or "-"
            vols = ", ".join(c["volumes"]) or "-"
            out.append(f"| `{c['name']}` | {c['state']} | {ports} | `{c['image']}` | {vols} |")
        extras = []
        sd = shared_db(p["containers"])
        if sd:
            extras.append(f"- Database: {sd}")
        for c in p["containers"]:
            for r in c.get("ingress", []):
                extras.append(f"- Tunnel (`{c['name']}`): `{r['hostname']}` -> `{r['service']}`")
            t = c.get("tailnet")
            if t:
                extras.append(f"- Tailnet node (`{c['name']}`): `{t['node'] or '?'}`")
                for r in t["serve"]:
                    extras.append(f"  - serve `{r['listen']}{r['path']}` -> `{r['proxy']}`")
        if extras:
            out.append("")
            out.extend(extras)
        out.append("")
    out.append("## Host listeners (not docker)")
    out.append("")
    if facts["host_listeners"]:
        for h in facts["host_listeners"]:
            out.append(f"- `{h['bind']}:{h['port']}`")
    else:
        out.append("- none")
    out.append("")
    out.append("## Claimed host ports")
    out.append("")
    out.append(", ".join(str(p) for p in facts["claimed_ports"]) or "none")
    out.append("")
    return "\n".join(out)


def main():
    facts = collect()
    body = json.dumps(facts, indent=2, sort_keys=True)
    old = None
    if os.path.exists(OUT_JSON):
        with open(OUT_JSON) as f:
            try:
                old = json.load(f)
            except json.JSONDecodeError:
                old = None
    unchanged = old is not None and json.dumps(old.get("facts"), indent=2, sort_keys=True) == body
    if "--check" in sys.argv:
        sys.exit(0 if unchanged else 1)
    if unchanged and os.path.exists(OUT_MD):
        # Same facts: keep the old stamp, but still rewrite when the script's own wording changed.
        with open(OUT_MD) as f:
            if f.read() == render(facts, old.get("generated", "")):
                return
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    with open(OUT_JSON + ".tmp", "w") as f:
        json.dump({"generated": stamp, "facts": facts}, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    with open(OUT_MD + ".tmp", "w") as f:
        f.write(render(facts, stamp))
    os.replace(OUT_MD + ".tmp", OUT_MD)
    print(f"fleet-facts: wrote {OUT_MD} ({len(facts['projects'])} projects)")


if __name__ == "__main__":
    main()
