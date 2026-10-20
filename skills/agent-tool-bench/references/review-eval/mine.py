#!/usr/bin/env python3
"""Propose review-eval cases from a repo's history: fix commits, and the commit that introduced each bug.

Usage: mine.py <repo> [--since 1.year] [--max 30] [--max-chars 60000] > candidates.json
       mine.py --check          does it find the same introducing commit as the hand-made cases.json?

For each commit whose message says fix, bug, crash, regress or broke, it takes the lines the fix changed or deleted
in code files and runs `git blame` on them in the fix's parent. The commit that wrote most of those lines is the
candidate. A fix that only adds lines has nothing to blame and is skipped. Every candidate still needs a person:
read the fix, write `bug` in code terms, set `confidence` (5 proven by a test or the exact line, 3 probable), and
drop the ones that are not a reviewable bug (a config value, a vendor change). Only then copy it into cases.json.
An introducing commit bigger than --max-chars of diff is skipped: the hand-made cases are 8k to 57k, and a huge
commit buries the bug (review-diff truncates at REVIEW_MAX_CHARS).
"""
import collections, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = r"\b(fix|fixes|fixed|bug|crash|regress|broke|broken)"
NOT_CODE = re.compile(r"(\.(md|txt|json|lock|svg|png|jpe?g|snap)$|(^|/)(docs|drizzle|migrations)/|CHANGELOG)", re.I)


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout


def intro_for(repo, fix):
    """The commit that wrote most of the code lines this fix changed, with its share of them, or None."""
    votes, first = collections.Counter(), None
    for path in git(repo, "diff", "--name-only", f"{fix}^", fix).split():
        if NOT_CODE.search(path):
            continue
        for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))? ", git(repo, "diff", "-U0", f"{fix}^", fix, "--", path), re.M):
            start, count = int(m.group(1)), int(m.group(2) or 1)
            if count == 0:
                continue  # pure addition: nothing old to blame
            first = first or f"{path}:{start}"
            blame = git(repo, "blame", "-w", "--porcelain", "-L", f"{start},+{count}", f"{fix}^", "--", path)
            for sha in re.findall(r"^([0-9a-f]{40}) \d+ \d+", blame, re.M):
                votes[sha] += 1
    if not votes:
        return None
    sha, n = votes.most_common(1)[0]
    return sha, round(n / sum(votes.values()), 2), first


def mine(repo, since, limit, max_chars):
    repo = os.path.expanduser(repo)
    name = os.path.basename(os.path.abspath(repo))
    log = git(repo, "log", "--no-merges", f"--since={since}", "-i", "-E", f"--grep={FIX}", "--format=%H%x09%s")
    out = []
    for line in log.splitlines():
        fix, subject = line.split("\t", 1)
        found = intro_for(repo, fix)
        if not found or not git(repo, "rev-parse", "-q", "--verify", f"{found[0]}^"):
            continue  # nothing to blame, or the bug is in the root commit (no parent to diff against)
        intro, share, hint = found
        size = len(git(repo, "diff", f"{intro}^", intro))
        if size > max_chars:
            continue
        out.append({"id": f"{name}-{fix[:7]}", "repo": repo.replace(os.path.expanduser("~"), "~", 1),
                    "intro": intro, "fix": fix, "files": sorted({hint.split(":")[0]}), "line_hint": hint,
                    "bug": "", "keywords": [], "diff_chars": size,
                    "confidence": None, "fix_subject": subject, "blame_share": share})
        if len(out) >= limit:
            break
    return out


def check():
    """Compare with the hand-made cases: the share of fixes whose introducing commit it finds."""
    cases = [c for c in json.load(open(f"{HERE}/cases.json")) if os.path.isdir(os.path.expanduser(c["repo"]))]
    hit = 0
    for c in cases:
        found = intro_for(os.path.expanduser(c["repo"]), c["fix"])
        ok = bool(found) and found[0] == c["intro"]
        hit += ok
        print(f"{'same' if ok else 'DIFF'} {c['id']}: {found[0][:7] if found else 'none'} (hand: {c['intro'][:7]})")
    print(f"{hit}/{len(cases)} cases: the same introducing commit as the hand-made one")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--check"]:
        check()
    elif a and not a[0].startswith("--"):
        opt = lambda k, d: a[a.index(k) + 1] if k in a else d
        json.dump(mine(a[0], opt("--since", "1.year"), int(opt("--max", "30")), int(opt("--max-chars", "60000"))), sys.stdout, indent=1)
        print()
    else:
        sys.exit(__doc__)
