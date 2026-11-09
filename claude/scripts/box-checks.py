#!/usr/bin/env python3
"""The box's weekly plain-code checks, one subcommand each, for Agent Factory's "Box checks" loop (D180,
docs/RECURRING-CHECKS-PLAN.md phase 2). Any agent or person can run them; none uses a model.

Contract: print ONE JSON object {"problems": [{"key", "title", "fix"}], "info": "..."} and exit 0. A problem's key is
stable across runs (the loop files it once). A crash, a non-zero exit or other output is read by the loop as "this
check is broken", never as clean.

Usage: box-checks.py deploy-sync | guards | routing | harvest | project-docs | skill-usage | untracked-scripts | board-coverage
"""
import datetime, filecmp, json, os, re, subprocess, sys

HOME = os.path.expanduser("~")
DS = f"{HOME}/projects/dev-system"


def out(problems, info=""):
    print(json.dumps({"problems": problems, "info": info}))


def deploy_sync():
    # Canonical copy in dev-system -> the deployed copy. An edit on one side without the copy step runs stale code.
    pairs = [
        (f"{DS}/scripts/ui-check", "/usr/local/bin/ui-check"),
        (f"{DS}/scripts/restore-test.sh", "/usr/local/bin/restore-test.sh"),
        (f"{DS}/scripts/secrets-backup.sh", "/usr/local/bin/secrets-backup.sh"),
        (f"{DS}/host/tg-alert", "/usr/local/bin/tg-alert"),
        (f"{DS}/systemd/tg-alert@.service", "/etc/systemd/system/tg-alert@.service"),
        (f"{DS}/systemd/restore-test.service", "/etc/systemd/system/restore-test.service"),
        (f"{DS}/systemd/restore-test.timer", "/etc/systemd/system/restore-test.timer"),
        (f"{DS}/systemd/secrets-backup.service", "/etc/systemd/system/secrets-backup.service"),
        (f"{DS}/systemd/secrets-backup.timer", "/etc/systemd/system/secrets-backup.timer"),
        (f"{DS}/host/review-diff", f"{HOME}/.local/bin/review-diff"),
        # 2026-10-26 retro: the other host scripts drifted unseen (mem-watch). cf-reachability-check left with
        # Cloudflare on 2026-10-27 (every app on Tailscale only), so it has no pair.
        (f"{DS}/host/mem-watch.sh", "/usr/local/bin/mem-watch.sh"),
        (f"{DS}/host/docker-restart-alert.sh", "/usr/local/bin/docker-restart-alert.sh"),
        (f"{DS}/host/claude-spawner.py", "/usr/local/bin/claude-spawner.py"),
        (f"{DS}/host/docker-daemon.json", "/etc/docker/daemon.json"),
    ]
    problems = []
    for src, dst in pairs:
        if not os.path.isfile(src):
            problems.append({"key": dst, "title": f"Deploy sync: the source of {dst} is missing", "fix": f"Restore {src} in dev-system, or drop the pair from box-checks.py."})
        elif not os.path.isfile(dst):
            problems.append({"key": dst, "title": f"Deploy sync: {dst} is not deployed", "fix": f"Copy {src} to {dst} (sudo /bin/sh -c 'cp ...')."})
        elif not filecmp.cmp(src, dst, shallow=False):
            problems.append({"key": dst, "title": f"Deploy sync: {dst} differs from dev-system", "fix": f"Redeploy {src}, or back-port the hotfix from {dst} into dev-system."})
    out(problems, f"{len(pairs)} deployed copies compared")


def guards():
    r = subprocess.run(["bash", f"{HOME}/.claude/scripts/guards-test.sh"], capture_output=True, text=True, timeout=100)
    text = r.stdout + r.stderr
    last = text.strip().splitlines()[-1] if text.strip() else ""
    if r.returncode == 0:
        return out([], last)
    fails = [l for l in text.splitlines() if l.startswith("FAIL")][:10]
    out([{"key": "guards", "title": "The safety guards failed their samples", "fix": "Run bash ~/.claude/scripts/guards-test.sh and fix the guard:\n" + "\n".join(fails)}], last)


def routing():
    d = f"{HOME}/.agents/skills/agent-tool-bench/references/router-eval"
    r = subprocess.run(["python3", "word_rank.py"], cwd=d, capture_output=True, text=True, timeout=100)
    top = next((l for l in r.stdout.splitlines() if l.startswith("top-1")), None)
    if r.returncode != 0 or not top:
        return out([{"key": "routing", "title": "The routing score did not run", "fix": f"Run python3 word_rank.py in {d}: {(r.stderr or r.stdout).strip()[-300:]}"}])
    out([], top)  # a score, not a pass or fail: the audit reads it


def harvest():
    s = open(f"{HOME}/.claude/HARVEST.md", encoding="utf-8").read()
    pend, proc = s.split("## Processed", 1) if "## Processed" in s else (s, "")
    old = datetime.date.today() - datetime.timedelta(days=90)
    stale = [d for d in re.findall(r"^- \[x\] (\d{4}-\d{2}-\d{2})", proc, re.M) if datetime.date.fromisoformat(d) < old]
    pending = len(re.findall(r"^- \[ \]", pend, re.M))
    problems = [{"key": "stale", "title": f"HARVEST: {len(stale)} processed entries older than 90 days", "fix": "Run retro: it trims processed entries."}] if stale else []
    out(problems, f"{pending} pending, {len(s) // 1024} KB")


def project_docs():
    # RULES.md "Canonical project docs" for every own app FLEET.md lists, plus DESIGN_* and a verify-<app> skill once the
    # app has a UI. Packaged images and the apps ENVIRONMENT.md lists as not in use are skipped.
    if not os.path.isfile(f"{HOME}/.claude/FLEET.md"):  # a fresh machine: the fleet facts never ran yet
        return out([{"key": "no-fleet", "title": "Project docs: ~/.claude/FLEET.md does not exist yet", "fix": "Run python3 ~/.claude/scripts/fleet-facts.py (needs docker), then this check again."}])
    dirs = re.findall(r"^Dir `~/projects/([^`]+)`", open(f"{HOME}/.claude/FLEET.md").read(), re.M)
    env = open(f"{HOME}/.claude/ENVIRONMENT.md").read()
    exempt = set()
    if m := re.search(r"Packaged third-party images \(([^)]*)\)", env):
        exempt |= {x.strip() for x in m.group(1).split(",")}
    if m := re.search(r"Not in use: ([^(\n]+)", env):
        exempt |= {x.strip() for x in m.group(1).split(",")}
    always = ["CLAUDE.md", "AGENTS.md", "FEATURES.md", "IMPLEMENTATION_PLAN.md", "ARCHITECTURE.md", "GLOSSARY.md", "CODEMAP.md", "REVIEW.md"]
    problems, checked = [], 0
    for a in sorted(set(dirs) - exempt):
        d = f"{HOME}/projects/{a}"
        if not os.path.isdir(d):
            continue
        checked += 1
        miss = [f for f in always if not os.path.exists(f"{d}/{f}")]
        if os.path.exists(f"{d}/AGENTS.md") and not os.path.islink(f"{d}/AGENTS.md"):
            miss.append("AGENTS.md as a symlink to CLAUDE.md")
        pkgs = [f"{d}/package.json"] + [f"{d}/{x}/package.json" for x in os.listdir(d)]
        if any(re.search(r'"(react|next|vite|svelte|vue)"', open(p).read()) for p in pkgs if os.path.isfile(p)):
            miss += [f for f in ["DESIGN_BRIEF.md", "DESIGN_TOKENS.md"] if not os.path.exists(f"{d}/{f}")]
            sk = f"{d}/.claude/skills"
            if not (os.path.isdir(sk) and any(n.startswith("verify-") for n in os.listdir(sk))):
                miss.append(f".claude/skills/verify-{a}/ (skill create-verification-skill)")
        if miss:
            problems.append({"key": a, "title": f"{a}: missing {', '.join(miss)}", "fix": "Backfill them (skill architecture for ARCHITECTURE, GLOSSARY and CODEMAP)."})
    out(problems, f"{checked} apps checked")


def skill_usage():
    r = subprocess.run(["python3", f"{HOME}/.claude/scripts/skill-usage.py", "--record"], capture_output=True, text=True, timeout=100)
    if r.returncode != 0:
        raise SystemExit(r.stderr or r.stdout)
    lines = r.stdout.splitlines()
    flagged = next((l for l in lines if l.startswith("- unused 2 recorded months")), "")
    names = flagged.split("):", 1)[1].split("(retro", 1)[0].strip() if "):" in flagged else "none"
    problems = [{"key": s.strip(), "title": f"Skill {s.strip()} unused for two months", "fix": "retro decides: merge it, sharpen its description, or delete it."} for s in names.split(",") if s.strip() and s.strip() != "none"]
    out(problems, next((l[2:] for l in lines if l.startswith("- most used")), ""))


def untracked_scripts():
    # 2026-10-26 retro (HARVEST 10-19): a .gitignore allowlist kept loop scripts out of git, so loops ran files that
    # were never pushed. Every file under ~/.claude/scripts must be tracked.
    r = subprocess.run(["git", "-C", f"{HOME}/.claude", "ls-files", "--others", "--exclude-standard", "--ignored", "scripts"], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
    files = [f for f in r.stdout.split() if "__pycache__" not in f]
    out([{"key": f, "title": f"~/.claude/{f} is not in git", "fix": "Whitelist it in ~/.claude/.gitignore so the auto-push carries it, or delete it."} for f in files], "scripts checked")


def board_coverage():
    # 2026-10-26 retro (HARVEST 10-19): an app off the board misses every loop (recall's missed reminders went unseen).
    # Every running compose project under ~/projects is a board repo, except the apps ENVIRONMENT.md marks unused or
    # packaged, and the host services.
    env = open(f"{HOME}/.claude/ENVIRONMENT.md").read()
    exempt = set()
    for pat in (r"Not in use: ([^(]+)", r"Packaged third-party images \(([^)]+)\)", r"\) are run by `fleet-ops`[^.]*\. ([a-z, -]+) and ([a-z-]+) are host"):
        for m in re.finditer(pat, env):
            exempt |= {w.strip() for g in m.groups() for w in re.split(r",| and ", g) if w.strip()}
    r = subprocess.run(["docker", "compose", "ls", "--format", "json"], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
    import sqlite3
    db = sqlite3.connect(f"file:{HOME}/.local/share/agent-factory/factory.db?mode=ro", uri=True)
    board = {os.path.realpath(p) for (p,) in db.execute("select path from repos where archived_at is null")}
    problems = []
    for proj in json.loads(r.stdout or "[]"):
        d = os.path.dirname(proj["ConfigFiles"].split(",")[0])
        repo = d if os.path.dirname(d) == f"{HOME}/projects" else os.path.dirname(d)
        name = os.path.basename(repo)
        if repo.startswith(f"{HOME}/projects/") and name not in exempt and proj["Name"] not in exempt and os.path.realpath(repo) not in board:
            problems.append({"key": name, "title": f"{name} runs but is not on the board, so no loop covers it", "fix": f"Add it in Agent Factory (Repos > Add), or mark it unused or packaged in ENVIRONMENT.md."})
    out(problems, f"{len(board)} board repos, exempt: {', '.join(sorted(exempt))}")


CHECKS = {"deploy-sync": deploy_sync, "guards": guards, "routing": routing, "harvest": harvest, "project-docs": project_docs, "skill-usage": skill_usage, "untracked-scripts": untracked_scripts, "board-coverage": board_coverage}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CHECKS:
        sys.exit(f"usage: box-checks.py {' | '.join(CHECKS)}")
    CHECKS[sys.argv[1]]()
