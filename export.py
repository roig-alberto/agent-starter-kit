#!/usr/bin/env python3
"""Rebuild claude/ and skills/ in this kit from the live agent setup (~/.claude and ~/.agents/skills), cleaned.

Run it on the home box whenever the setup changed: python3 export.py [--json]
Agent Factory's weekly "Starter kit sync" loop runs it with --json: {"files", "skills", "unclassified", "leaks"}.
It copies an allowlist, drops the box-only skills, replaces personal values with placeholders from a map kept OUTSIDE
this repo (~/.config/agent-starter-kit/redact.tsv, one literal "from<TAB>to" per line), overlays templates/, then
refuses to finish while any left-column value, a private IP or a secret (gitleaks) is still in the output.
"""
import fnmatch, glob, io, json, os, re, shutil, subprocess, sys, tarfile

HOME = os.path.expanduser("~")
KIT = os.path.dirname(os.path.abspath(__file__))
CLAUDE, SKILLS, FACTORY = f"{HOME}/.claude", f"{HOME}/.agents/skills", f"{HOME}/projects/agent-factory"
REDACT = f"{HOME}/.config/agent-starter-kit/redact.tsv"

CLAUDE_FILES = [".gitignore", "CLAUDE.md", "INSTRUCTIONS.md", "RULES.md", "RTK.md", "HISTORY.md", "PROMPT-GUIDE.md",
                "MODEL-MIGRATION.md", "settings.json", "statusline.sh", "git-hooks/*", "agents/*.md", "scripts/*"]
CLAUDE_SKIP = {"scripts/bootstrap-agent-brain.sh", "scripts/autopush-repos.conf"}  # the kit's install.sh and template replace them
# Every file tracked in ~/.claude is shared (CLAUDE_FILES) or private (here); a new one is reported until listed.
CLAUDE_PRIVATE = ["ENVIRONMENT.md", "HARVEST.md", "FLEET.md", "fleet.json", "HANDOFF.md", "INSTALL.md",
                  "SKILLS-REDO-PLAN.md", "review-log.tsv", "plugins/*", "projects/*/memory/*", "handoff/*", *CLAUDE_SKIP]
# Repos the knowledge auto-push syncs (scripts/autopush-repos.conf), by folder name: in the kit, or private.
REPOS_KNOWN = {".claude", "skills", "dev-system"}
# Skills that stay off the PUBLIC kit (user, 2026-10-20): your house and your phone console (personal), and the box's
# infrastructure skills (they map its security holes, vault access and exposed services).
DROP_SKILLS = ["home-assistant-fleet", "claude-spawner", "security", "backups-and-alerts", "fleet-ops"]
# Of those, the ones the kit ships as a fill-in template instead (user, 2026-10-20): templates-skills/<name>/.
TEMPLATE_SKILLS = ["fleet-ops"]
GONE = [k for k in DROP_SKILLS if k not in TEMPLATE_SKILLS]  # skills with no copy at all in the kit
# Reviewer eval cases that describe how a permission or trust bypass worked: private even after the fix.
PRIVATE_EVAL_CASES = ["agent-factory-deny-after-outside-read-ask", "agent-factory-redirect-write-escape",
                      "agent-factory-skill-read-traversal", "finance-import-client-reconcile",
                      "finance-lockguard-memory-clock"]  # how an app's lock can be outlasted
# Recorded agent transcripts and caches.
SKILL_SKIP = ["synced", *DROP_SKILLS, "**/__pycache__",
              "agent-tool-bench/references/router-eval/*.jsonl", "agent-tool-bench/references/router-eval/*.gitcheck",
              "frontend-design/references/ui-examples/*.png"]  # mockups that may hold real values (a weight, a trip); the .md describes them
# Router segments of the dropped skills, so RULES.md routes only to skills the kit ships.
RULES_DROP = [rf" · `{k}`[^·|]*?(?= ·| \|)" for k in GONE]
# From Agent Factory: the UI playbook (look and iPhone fixes; the motion half is skills/animate) and the model prompts of
# the loops (the code defaults; the app may hold an edited copy in Settings > Prompts).
LOOP_PROMPTS = {"SYSTEM_AUDIT": "knowledge-audit", "SYSTEM_REVIEW": "skills-review", "SYSTEM_KIT": "starter-kit-review", "LOOP": "repo-loop"}
# Own CLIs the skills call, kept in the infra repo (found by its folder name in autopush-repos.conf, so no path here).
BIN = {"host/review-diff": "review-diff", "scripts/ui-check": "ui-check"}
GENERATED = ["claude", "skills", "playbooks", "loops/prompts", "bin", "config"]  # config/: files for ~/.config  # rebuilt each run; everything else in the kit is hand-written
PRIVATE_IP = re.compile(r"\b(?:10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.(?!1\.)\d+\.\d+|100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d+\.\d+)\b")


def unclassified():
    tracked = subprocess.run(["git", "-C", CLAUDE, "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    out = [f"~/.claude/{f}" for f in tracked if not any(fnmatch.fnmatch(f, p) for p in CLAUDE_FILES + CLAUDE_PRIVATE)]
    for line in open(f"{CLAUDE}/scripts/autopush-repos.conf", encoding="utf-8"):
        path = os.path.expanduser(os.path.expandvars(line.split("#")[0].strip()))
        if path and os.path.basename(path.rstrip("/")) not in REPOS_KNOWN:
            out.append(f"repo {os.path.basename(path.rstrip('/'))} (in autopush-repos.conf)")
    return out


def main():
    as_json = "--json" in sys.argv[1:]
    pairs = [l.rstrip("\n").split("\t") for l in open(REDACT, encoding="utf-8") if "\t" in l and not l.startswith("#")]
    for d in GENERATED:
        shutil.rmtree(f"{KIT}/{d}", ignore_errors=True)

    for pat in CLAUDE_FILES:
        for src in glob.glob(f"{CLAUDE}/{pat}"):
            rel = os.path.relpath(src, CLAUDE)
            if rel in CLAUDE_SKIP or not os.path.isfile(src):
                continue
            os.makedirs(os.path.dirname(f"{KIT}/claude/{rel}"), exist_ok=True)
            shutil.copy2(src, f"{KIT}/claude/{rel}")

    # The skills at HEAD: committed files only, never a half-edited working tree.
    tar = subprocess.run(["git", "-C", SKILLS, "archive", "HEAD"], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(f"{KIT}/skills", filter="data")
    for pat in SKILL_SKIP:
        for p in glob.glob(f"{KIT}/skills/{pat}", recursive=True):
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    # Agent Factory at HEAD, like the skills: committed text only.
    os.makedirs(f"{KIT}/playbooks")
    with open(f"{KIT}/playbooks/UI-PLAYBOOK.md", "w", encoding="utf-8") as f:
        f.write(subprocess.run(["git", "-C", FACTORY, "show", "HEAD:docs/UI-PLAYBOOK.md"], capture_output=True, text=True, check=True).stdout)
    js = f"import('{FACTORY}/server/prompts.ts').then((m) => console.log(JSON.stringify({{{', '.join(f'{k}: m.{k}' for k in LOOP_PROMPTS)}}})))"
    texts = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True, cwd=FACTORY).stdout)
    up = json.loads(subprocess.run(["node", "-e", f"import('{FACTORY}/server/system/snapshot.ts').then((m) => console.log(JSON.stringify(m.UPSTREAM)))"], capture_output=True, text=True, check=True, cwd=FACTORY).stdout)
    with open(f"{KIT}/playbooks/OUTSIDE-SKILL-REPOS.md", "w", encoding="utf-8") as f:
        f.write("<!-- Generated by export.py from Agent Factory server/system/snapshot.ts (UPSTREAM). -->\n\n# Outside skill repos\n\n"
                "Public skill and agent-tool repos this setup borrows ideas from (adapted, never copied; pstack is in cursor/plugins).\n"
                "Agent Factory's weekly skills review (built, switched off now) reads their new commits for ideas. They are not copied here.\n\n"
                + "".join(f"- [{r}](https://github.com/{r})\n" for r in up))
    os.makedirs(f"{KIT}/loops/prompts")
    for k, name in LOOP_PROMPTS.items():
        with open(f"{KIT}/loops/prompts/{name}.md", "w", encoding="utf-8") as f:
            f.write(f"<!-- Generated by export.py from Agent Factory server/prompts.ts ({k}). {{{{name}}}} marks a value the loop fills in. -->\n\n{texts[k]}\n")

    os.makedirs(f"{KIT}/config/rtk")  # the commands rtk leaves unfiltered (RTK.md)
    shutil.copy2(f"{HOME}/.config/rtk/config.toml", f"{KIT}/config/rtk/config.toml")
    conf = [os.path.expanduser(os.path.expandvars(l.split("#")[0].strip())) for l in open(f"{CLAUDE}/scripts/autopush-repos.conf", encoding="utf-8")]
    infra = next(p for p in conf if p and os.path.basename(p.rstrip("/")) == "dev-system")
    os.makedirs(f"{KIT}/bin")
    for src, name in BIN.items():
        text = subprocess.run(["git", "-C", infra, "show", f"HEAD:{src}"], capture_output=True, text=True, check=True).stdout
        if name == "ui-check":  # its shebang is this box's playwright venv; install.sh points it at the new machine's
            text = "#!/usr/bin/env python3\n" + text.split("\n", 1)[1]
        with open(f"{KIT}/bin/{name}", "w", encoding="utf-8") as f:
            f.write(text)

    # The evals: the router fixtures that expect a dropped skill, and the private bypass cases, leave with them.
    fx = f"{KIT}/skills/agent-tool-bench/references/router-eval/fixtures.tsv"
    rows = open(fx, encoding="utf-8").read().split("\n")
    open(fx, "w", encoding="utf-8").write("\n".join(r for r in rows if r.startswith("#") or len(r.split("\t")) != 4 or not set(r.split("\t")[2].split("|")) & set(DROP_SKILLS)))
    ev = f"{KIT}/skills/agent-tool-bench/references/review-eval"
    cases = [c for c in json.load(open(f"{ev}/cases.json")) if c["id"] not in PRIVATE_EVAL_CASES]
    json.dump(cases, open(f"{ev}/cases.json", "w"), indent=1)
    split = json.load(open(f"{ev}/split.json"))
    for part in ("train", "test"):
        split[part] = [c for c in split[part] if c not in PRIVATE_EVAL_CASES]
    json.dump(split, open(f"{ev}/split.json", "w"), indent=1)
    labels = json.load(open(f"{ev}/labels.json"))
    labels["runs"] = {k: v for k, v in labels["runs"].items() if k.split("/", 1)[1].rsplit("-", 1)[0] not in PRIVATE_EVAL_CASES}
    json.dump(labels, open(f"{ev}/labels.json", "w"), indent=1)
    readme = open(f"{ev}/README.md", encoding="utf-8").read().replace("| 17 real cases from our repos:", f"| {len(cases)} real cases from our repos (5 more that describe security bypasses stay private):")
    open(f"{ev}/README.md", "w", encoding="utf-8").write(readme)

    rules = f"{KIT}/claude/RULES.md"
    text = open(rules, encoding="utf-8").read()
    for pat in RULES_DROP:
        text = re.sub(pat, "", text)
    # Prose pointers to dropped skills, reworded so nothing names a skill the kit does not ship.
    for old, new in [(" See `security`.", "")]:
        text = text.replace(old, new)
    open(rules, "w", encoding="utf-8").write(text)

    files = [p for d in GENERATED for p in glob.glob(f"{KIT}/{d}/**/*", recursive=True, include_hidden=True) if os.path.isfile(p)]
    for p in files:
        try:
            s = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue  # images
        t = s
        for a, b in pairs:
            t = t.replace(a, b)
        t = t.replace("\u2014", "-").replace("\u2013", "-")  # the commit hook refuses long dashes
        for k in GONE:  # a pointer to a skill the public kit leaves out says so
            t = t.replace(f"`{k}`", f"`{k}` (not in this kit)")
        t = re.sub(r"\(not in this kit\) `(references/[^`]+)`", r"(not in this kit) \1", t)  # its files are gone too
        if t != s:
            open(p, "w", encoding="utf-8").write(t)

    shutil.copytree(f"{KIT}/templates", f"{KIT}/claude", dirs_exist_ok=True)
    shutil.copytree(f"{KIT}/templates-skills", f"{KIT}/skills", dirs_exist_ok=True)  # fill-in skills (fleet-ops)

    leaks = []
    for p in glob.glob(f"{KIT}/**/*", recursive=True, include_hidden=True):
        if not os.path.isfile(p) or "/.git/" in p or p == os.path.abspath(__file__):
            continue
        try:
            s = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        rel = os.path.relpath(p, KIT)
        leaks += [f"{rel}: redact.tsv value {a[:3]}..." for a, _ in pairs if a in s]  # never echo the value itself
        leaks += [f"{rel}: private IP {m}" for m in sorted(set(PRIVATE_IP.findall(s))) if not m.endswith(".0")]  # .0 = a network range, not a host
    g = subprocess.run(["gitleaks", "dir", "--no-banner", "--redact", KIT], capture_output=True, text=True)
    if g.returncode:
        leaks.append(f"gitleaks found secrets:\n{g.stdout}{g.stderr}")
    leaks, new, skills = sorted(set(leaks)), unclassified(), len(os.listdir(f"{KIT}/skills"))
    if as_json:
        return print(json.dumps({"files": len(files), "skills": skills, "unclassified": new, "leaks": leaks}))
    for f in new:
        print(f"unclassified: {f}: add it to CLAUDE_FILES (shared) or CLAUDE_PRIVATE / REPOS_KNOWN (private) in export.py")
    if leaks:
        sys.exit("LEAKS, fix redact.tsv or the allowlist and re-run:\n" + "\n".join(leaks))
    print(f"exported {len(files)} files, {skills} skills, leak scan clean")


if __name__ == "__main__":
    main()
