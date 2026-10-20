#!/usr/bin/env python3
"""Fail when ARCHITECTURE.md, GLOSSARY.md, CODEMAP.md or REVIEW.md names a repo path that does not exist.

Usage: check-doc-paths.py [repo-root]   (default: current directory). Exit 1 on any missing path.
A backticked token counts as a path when it contains a slash or ends in a file extension, and has no
placeholder (<, *, {, ~, $) or URL scheme.
"""
import os
import re
import sys

DOCS = ("ARCHITECTURE.md", "GLOSSARY.md", "CODEMAP.md", "REVIEW.md")
TOKEN = re.compile(r"`([^`\s]+)`")
EXT = re.compile(r"\.(ts|tsx|js|mjs|json|md|sql|py|sh|css|html|yml|yaml|toml)$")


def paths(text):
    for t in TOKEN.findall(text):
        t = t.rstrip(".,:;)")
        if any(c in t for c in "<*{~$") or "://" in t or t.startswith(("-", "@")):
            continue
        if "/" in t or EXT.search(t):
            yield t


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    missing, checked = [], 0
    for doc in DOCS:
        p = os.path.join(root, doc)
        if not os.path.exists(p):
            continue
        for t in sorted(set(paths(open(p, encoding="utf-8").read()))):
            checked += 1
            if not os.path.exists(os.path.join(root, t.lstrip("/"))):
                missing.append(f"{doc}: {t}")
    for m in missing:
        print(f"MISSING {m}")
    print(f"check-doc-paths: {checked} paths checked, {len(missing)} missing")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
