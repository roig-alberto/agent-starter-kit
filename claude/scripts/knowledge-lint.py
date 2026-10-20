#!/usr/bin/env python3
"""Mechanical checks for the agent-knowledge system (skills, RULES, ENVIRONMENT, memories, HARVEST).

Every rule here replaces a sentence an agent used to be trusted to obey. Errors block the
Stop-hook auto-push; warnings are printed only.

Usage: knowledge-lint.py [--quiet]     exit 0 clean, 1 errors
"""
import datetime as dt
import glob
import os
import re
import sys

import yaml

HOME = os.path.expanduser("~")
SKILLS = os.environ.get("SKILLS_DIR") or os.path.join(HOME, ".agents", "skills")  # SKILLS_DIR: a task worktree (Agent Factory)
CLAUDE = os.path.join(HOME, ".claude")
TOP_DOCS = ["RULES.md", "ENVIRONMENT.md", "RTK.md", "CLAUDE.md", "HARVEST.md", "INSTALL.md",
            "PROMPT-GUIDE.md", "MODEL-MIGRATION.md"]
DESC_MAX = 800
BODY_MAX = 150
STAMP_DAYS = 90
PENDING_DAYS = 30
# Docs that must point at FLEET.md instead of restating live facts.
NO_LIVE_FACTS = [os.path.join(CLAUDE, "RULES.md"), os.path.join(CLAUDE, "ENVIRONMENT.md"),
                 os.path.join(SKILLS, "fleet-ops", "references", "port-registry.md")]
PORT_MAP_RE = re.compile(r"\b\d{4,5}\s*(?:→|->)\s*\d{2,5}\b|\b(?:127\.0\.0\.1|0\.0\.0\.0):\d{4,5}\s*(?:→|->)")
DASH_RE = re.compile("[\u2013\u2014]")
STAMP_RE = re.compile(r"\b[Vv]erified[^0-9\n]{0,25}(20\d\d-\d\d-\d\d)")
REF_RE = re.compile(r"`(?:\.\./)?references/([A-Za-z0-9_./-]+\.md)`")
TODAY = dt.date.today()
# The skill validator's allowed frontmatter keys (knowledge-authoring scripts/quick_validate.py).
FM_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
# Agent-agnostic skills (user, 2026-10-16): wording that names one agent where any agent is meant.
AGENTS = r"(?:Claude|Codex|OpenCode)"
AGENT_GENERIC_RE = re.compile(
    rf"\b{AGENTS},? (?:and|or) {AGENTS}\b|\b{AGENTS}, {AGENTS}\b"
    r"|\bClaude (?:reads|will|should|would|can|cannot|can't|does|doesn't|must|sees|knows|tends|needs|wants)\b"
    r"|\b(?:tell|ask|let|make|lets|tells) Claude\b")

errors, warnings = [], []


def err(path, msg):
    errors.append(f"{path.replace(HOME, '~')}: {msg}")


def warn(path, msg):
    warnings.append(f"{path.replace(HOME, '~')}: {msg}")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    return text[4:end], text[end + 4:].lstrip("\n")


def knowledge_files():
    files = [os.path.join(CLAUDE, d) for d in TOP_DOCS if os.path.exists(os.path.join(CLAUDE, d))]
    files += glob.glob(os.path.join(SKILLS, "*", "**", "*.md"), recursive=True)
    files += glob.glob(os.path.join(CLAUDE, "projects", "*", "memory", "*.md"))
    return [f for f in files if "/synced/" not in f]


def check_text(path):
    text = read(path)
    if not text.strip():
        err(path, "empty file")
        return
    for n, line in enumerate(text.splitlines(), 1):
        if DASH_RE.search(line):
            err(path, f"line {n}: long dash (use a hyphen or a new sentence)")
    historical = os.path.basename(path) in ("history.md", "HISTORY.md", "HARVEST.md")
    for m in ([] if historical else STAMP_RE.finditer(text)):
        try:
            d = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if (TODAY - d).days > STAMP_DAYS:
            warn(path, f"stamp '{m.group(0)[:40]}' is {(TODAY - d).days} days old; re-verify")


def check_skill(skill_dir, skill_names):
    name = os.path.basename(skill_dir)
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(path):
        err(skill_dir, "no SKILL.md")
        return None
    fm_text, body = frontmatter(read(path))
    if fm_text is None:
        err(path, "missing YAML frontmatter")
        return None
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        err(path, f"frontmatter YAML error: {str(e).splitlines()[0]}")
        return None
    if fm.get("name") != name:
        err(path, f"frontmatter name '{fm.get('name')}' != directory '{name}'")
    for key in sorted(set(fm) - FM_KEYS):
        err(path, f"frontmatter key '{key}' fails the skill validator (allowed: {', '.join(sorted(FM_KEYS))})")
    desc = fm.get("description")
    if isinstance(desc, str) and re.search(r"[<>]", desc):
        err(path, "description contains < or >, which fails the skill validator")
    if isinstance(desc, str) and not re.search(r"\buse (when|whenever)\b", desc, re.I):
        err(path, "description has no 'Use when ...' (what it does, then Use when, then NOT for)")
    if isinstance(desc, str) and "NOT for" not in desc:
        err(path, "description has no 'NOT for X (use Y)' clause")
    if not isinstance(desc, str) or len(desc.strip()) < 40:
        err(path, "description missing or under 40 chars")
    elif len(desc) > DESC_MAX:
        err(path, f"description is {len(desc)} chars (max {DESC_MAX})")
    lines = body.count("\n") + 1
    if lines > BODY_MAX:
        err(path, f"body is {lines} lines (max {BODY_MAX}); move detail to references/")
    # references: local file, or a named sibling skill's file on the same line
    for n, line in enumerate(body.splitlines(), 1):
        for ref in REF_RE.findall(line):
            if os.path.exists(os.path.join(skill_dir, "references", ref)):
                continue
            owners = [s for s in skill_names if s != name and s in line
                      and os.path.exists(os.path.join(SKILLS, s, "references", ref))]
            if not owners:
                err(path, f"line {n}: references/{ref} does not exist (here or in a skill named on the line)")
    ref_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(ref_dir):
        corpus = ""
        for f in glob.glob(os.path.join(skill_dir, "**", "*"), recursive=True):
            if os.path.isfile(f) and f.endswith((".md", ".sh", ".py", ".ts", ".mjs")):
                corpus += read(f)
        for f in glob.glob(os.path.join(ref_dir, "**", "*.md"), recursive=True):
            base = os.path.basename(f)
            rel_dir = os.path.relpath(os.path.dirname(f), skill_dir)
            if corpus.count(base) - read(f).count(base) <= 0 and rel_dir not in corpus.replace(read(f), ""):
                err(f, "orphan: nothing in the skill points at this file")
    return fm


def check_agent_agnostic():
    """Skills name no specific agent where any agent is meant. History and verbatim copies are exempt."""
    for path in glob.glob(os.path.join(SKILLS, "*", "**", "*.md"), recursive=True):
        if "/synced/" in path or os.path.basename(path) == "history.md" or "/animate/references/" in path:
            continue
        text = read(path)
        if "verbatim" in "\n".join(text.splitlines()[:5]).lower():
            continue
        for n, line in enumerate(text.splitlines(), 1):
            m = AGENT_GENERIC_RE.search(line)
            if m:
                err(path, f"line {n}: '{m.group(0)}' names one agent where any agent is meant; write 'the agent'")


def check_routing_baseline():
    """Free routing check (router-eval word_rank.py): warn when top-1 falls below the saved baseline."""
    d = os.path.join(SKILLS, "agent-tool-bench", "references", "router-eval")
    if not os.path.exists(os.path.join(d, "baseline.json")):
        return
    import importlib.util
    import io
    import json
    from contextlib import redirect_stdout
    spec = importlib.util.spec_from_file_location("word_rank", os.path.join(d, "word_rank.py"))
    wr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wr)
    baseline = json.load(open(os.path.join(d, "baseline.json")))
    base = baseline["word_rank"]["top1_pct"]
    import hashlib
    rules = read(os.path.join(CLAUDE, "RULES.md"))
    router = rules[rules.find("## Scenario router"):]
    if baseline.get("router_sha") != hashlib.sha256(router.encode()).hexdigest()[:16]:
        warn(os.path.join(d, "baseline.json"), "the RULES.md router changed since the last full routing sweep; run "
             "the sweep (router-eval README, 'When to run what' 3), then record router_sha")
    argv, sys.argv = sys.argv, ["word_rank.py", "--min-rank1", str(base)]
    try:
        with redirect_stdout(io.StringIO()):
            wr.main()
    except SystemExit as e:
        if e.code:
            warn(os.path.join(d, "fixtures.tsv"), f"routing check: top-1 fell below the {base}% baseline; "
                 "run router-eval/word_rank.py, then run-skill.sh for the skill you changed")
    finally:
        sys.argv = argv


def check_router(skill_meta):
    rules = read(os.path.join(CLAUDE, "RULES.md"))
    for name, fm in skill_meta.items():
        if fm and fm.get("disable-model-invocation"):
            continue
        if f"`{name}`" not in rules:
            err(os.path.join(SKILLS, name, "SKILL.md"), "not routed: RULES.md never names this skill")
    known = set(skill_meta)
    section = rules.split("## Scenario router", 1)[-1]
    for token in sorted(set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", section))):
        if token in known or token in ROUTER_NON_SKILLS:
            continue
        err(os.path.join(CLAUDE, "RULES.md"), f"router names `{token}`, which is not a skill (add it to ROUTER_NON_SKILLS if intended)")


ROUTER_NON_SKILLS = {
    "cavecrew-builder", "cavecrew-investigator", "cavecrew-reviewer", "chrome-devtools-axi",
    "home-assistant-best-practices", "java-testing-drill", "live-coding", "mock-exam", "review-diff",
    "ui-check", "deep-research",
}


def check_live_facts():
    for path in NO_LIVE_FACTS:
        if not os.path.exists(path):
            continue
        for n, line in enumerate(read(path).splitlines(), 1):
            if PORT_MAP_RE.search(line):
                err(path, f"line {n}: restates a live port mapping; point at ~/.claude/FLEET.md instead")


def check_harvest():
    path = os.path.join(CLAUDE, "HARVEST.md")
    if not os.path.exists(path):
        return
    text = read(path)
    heads = re.findall(r"^## (.+)$", text, re.M)
    if heads.count("Pending") != 1 or heads.count("Processed") != 1 or len(heads) != 2:
        err(path, f"must have exactly '## Pending' and '## Processed'; found {heads}")
        return
    pending, processed = text.split("## Processed", 1)
    if re.search(r"^- \[ \]", processed, re.M):
        err(path, "unticked entry under ## Processed")
    if re.search(r"^- \[x\]", pending.split("## Pending", 1)[1], re.M):
        err(path, "ticked entry under ## Pending; move it to ## Processed")
    for m in re.finditer(r"^- \[ \] (20\d\d-\d\d-\d\d)", pending, re.M):
        age = (TODAY - dt.date.fromisoformat(m.group(1))).days
        if age > PENDING_DAYS:
            warn(path, f"pending entry from {m.group(1)} is {age} days old; encode or drop it")


def check_memories():
    for mdir in glob.glob(os.path.join(CLAUDE, "projects", "*", "memory")):
        files = {os.path.basename(f) for f in glob.glob(os.path.join(mdir, "*.md"))} - {"MEMORY.md"}
        if not files:
            continue
        index_path = os.path.join(mdir, "MEMORY.md")
        index = read(index_path) if os.path.exists(index_path) else ""
        linked = set(re.findall(r"\]\(([^)]+\.md)\)", index))
        for f in sorted(files - linked):
            err(os.path.join(mdir, f), "memory not listed in MEMORY.md")
        for f in sorted(linked - files):
            err(index_path, f"index points at missing {f}")


def main():
    skill_dirs = sorted(d for d in glob.glob(os.path.join(SKILLS, "*")) if os.path.isdir(d)
                        and os.path.basename(d) != "synced")
    names = [os.path.basename(d) for d in skill_dirs]
    meta = {os.path.basename(d): check_skill(d, names) for d in skill_dirs}
    for f in knowledge_files():
        check_text(f)
    check_router(meta)
    check_agent_agnostic()
    check_routing_baseline()
    check_live_facts()
    check_harvest()
    check_memories()
    quiet = "--quiet" in sys.argv
    for e in errors:
        print(f"ERROR {e}")
    if not quiet:
        for w in warnings:
            print(f"WARN  {w}")
    print(f"knowledge-lint: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
