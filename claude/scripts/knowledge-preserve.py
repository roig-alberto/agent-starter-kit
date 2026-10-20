#!/usr/bin/env python3
"""Check that rewriting a skill lost no concrete knowledge.

Compares a skill directory at a git ref (default HEAD) with the working tree and lists
every code span, URL, and quoted trigger phrase that existed before and is gone now.
Prose may be reworded freely; these tokens carry the commands, paths, flags, error
strings and triggers, so each one must survive somewhere in the skill directory.

Usage: knowledge-preserve.py <skill-name> [git-ref]     exit 1 if anything was lost
       knowledge-preserve.py <new-skill> <git-ref> --from <old1,old2,...>
         for a merge: every token of the old skills at the ref must survive in the new skill
"""
import os
import re
import subprocess
import sys

SKILLS = os.environ.get("SKILLS_DIR") or os.path.expanduser("~/.agents/skills")  # SKILLS_DIR: a task worktree (Agent Factory)
CODE_RE = re.compile(r"`([^`\n]{3,})`")
URL_RE = re.compile(r"https?://[^\s)>\]`'\"]+")
QUOTE_RE = re.compile(r"[\"']([^\"'\n]{6,80})[\"']")


def norm(s):
    return re.sub(r"\s+", " ", s.replace("\u2014", "-").replace("\u2013", "-")).strip().lower()


def tokens(text, with_quotes):
    found = set(CODE_RE.findall(text)) | set(URL_RE.findall(text))
    if with_quotes:
        found |= set(QUOTE_RE.findall(text))
    return {t for t in found if len(norm(t)) >= 3}


def old_text(skill, ref):
    files = subprocess.run(["git", "-C", SKILLS, "ls-tree", "-r", "--name-only", ref, skill + "/"],
                           capture_output=True, text=True).stdout.split()
    out = {}
    for f in files:
        if f.endswith((".md", ".sh", ".py", ".ts", ".mjs", ".yaml", ".yml", ".json")):
            r = subprocess.run(["git", "-C", SKILLS, "show", f"{ref}:{f}"], capture_output=True, text=True)
            out[f] = r.stdout
    return out


def new_text(skill):
    out = []
    for root, _, files in os.walk(os.path.join(SKILLS, skill)):
        for f in files:
            if f.endswith((".md", ".sh", ".py", ".ts", ".mjs", ".yaml", ".yml", ".json")):
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    out.append(fh.read())
    return "\n".join(out)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    args = sys.argv[1:]
    sources = None
    if "--from" in args:
        i = args.index("--from")
        sources = [x for x in args[i + 1].split(",") if x]
        args = args[:i] + args[i + 2:]
    skill, ref = args[0], (args[1] if len(args) > 1 else "HEAD")
    old = {}
    for src in sources or [skill]:
        old.update(old_text(src, ref))
    if not old:
        sys.exit(f"{skill}: nothing at {ref}")
    new = norm(new_text(skill))
    lost = []
    for path, text in old.items():
        desc_only = text.split("\n---", 1)[0] if path.endswith("SKILL.md") else ""
        for t in sorted(tokens(text, with_quotes=False) | tokens(desc_only, with_quotes=True)):
            if norm(t) not in new:
                lost.append((path, t))
    for path, t in lost:
        print(f"LOST {path}: {t}")
    print(f"knowledge-preserve {skill}: {len(lost)} lost tokens")
    sys.exit(1 if lost else 0)


if __name__ == "__main__":
    main()
