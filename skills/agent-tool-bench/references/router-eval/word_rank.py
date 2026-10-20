#!/usr/bin/env python3
"""Free routing check: does each fixture prompt rank its expected skill first by word overlap?

Port of addyosmani/agent-skills scripts/run-evals.js Tier 2 (MIT): tf-idf cosine between the prompt and
each skill's routing surface. Here the surface is the skill name (counted twice), its description, and
the situation text of every RULES.md router row that names it, because the router is always loaded.
No model, no tokens. It measures word overlap, not what a model picks; the real runs (run.sh) do that.

Usage: word_rank.py [--json out.json] [--min-rank1 PCT]     exit 1 when top-1 falls below PCT
"""
import glob
import json
import math
import os
import re
import sys
from collections import Counter

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS = os.environ.get("SKILLS_DIR") or os.path.expanduser("~/.agents/skills")  # SKILLS_DIR: a task worktree (Agent Factory)
RULES = os.path.expanduser("~/.claude/RULES.md")
STOP = set("a an and any are as at be before by for from in into is it its my need needs of on or our so that "
           "the them this to use want we when with you your help me i".split())


def stem(t):
    for suf in ("ally", "ing", "ed", "es", "al"):
        if len(t) > len(suf) + 3 and t.endswith(suf):
            t = t[: -len(suf)]
            break
    if len(t) > 3 and t.endswith("s") and not t.endswith("ss"):
        t = t[:-1]
    if len(t) > 4 and t.endswith("e"):
        t = t[:-1]
    if len(t) > 4 and t[-1] == t[-2] and t[-1] not in "aeiou":
        t = t[:-1]
    if len(t) > 3 and t.endswith("y"):
        t = t[:-1] + "i"
    return t


def tokenize(text):
    words = re.split(r"[\s-]+", re.sub(r"[^a-z0-9\s-]", " ", text.lower()))
    return [stem(w) for w in words if len(w) > 2 and w not in STOP]


def router_rows():
    rows = {}
    for line in open(RULES):
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        # A grouped row lists "`skill` when ... · `skill` when ..."; each skill gets its own segment.
        for seg in cells[-1].split(" · "):
            for name in re.findall(r"`([a-z0-9-]+)`", seg):
                rows.setdefault(name, []).append(cells[0] + " " + seg)
    return rows


def load_skills():
    rows = router_rows()
    docs = {}
    for path in sorted(glob.glob(os.path.join(SKILLS, "*", "SKILL.md"))):
        name = os.path.basename(os.path.dirname(path))
        if name == "synced":
            continue
        fm = yaml.safe_load(open(path).read().split("---")[1]) or {}
        name_tokens = tokenize(name.replace("-", " "))
        text = (fm.get("description") or "") + " " + " ".join(rows.get(name, []))
        docs[name] = Counter(name_tokens * 2 + tokenize(text))
    df = Counter(t for tf in docs.values() for t in tf)
    n = len(docs)
    idf = lambda t: math.log(1 + n / (1 + df.get(t, 0)))  # noqa: E731
    return docs, idf


def vec(tf, idf):
    return {t: f * idf(t) for t, f in tf.items()}


def cosine(a, b):
    dot = sum(w * b.get(t, 0) for t, w in a.items())
    na, nb = math.sqrt(sum(w * w for w in a.values())), math.sqrt(sum(w * w for w in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def load_fixtures():
    out = []
    for line in open(os.path.join(HERE, "fixtures.tsv")):
        if line.startswith("#") or not line.strip():
            continue
        fid, prompt, expected, source = line.rstrip("\n").split("\t")
        out.append({"id": fid, "prompt": prompt, "expected": expected.split("|"), "source": source})
    return out


def main():
    docs, idf = load_skills()
    vecs = {name: vec(tf, idf) for name, tf in docs.items()}
    results = []
    for fx in load_fixtures():
        pv = vec(Counter(tokenize(fx["prompt"])), idf)
        ranked = sorted(((cosine(pv, v), name) for name, v in vecs.items()), reverse=True)
        names = [name for _, name in ranked]
        rank = min((names.index(e) + 1 for e in fx["expected"] if e in names), default=None)
        results.append({**fx, "rank": rank, "top3": [(n, round(s, 3)) for s, n in ranked[:3]]})

    scored = [r for r in results if r["expected"] != ["none"]]
    top1 = sum(r["rank"] == 1 for r in scored)
    top3 = sum(r["rank"] is not None and r["rank"] <= 3 for r in scored)
    for r in results:
        mark = "neg " if r["expected"] == ["none"] else ("PASS" if r["rank"] == 1 else f"#{r['rank']}  ")
        tops = ", ".join(f"{n} {s}" for n, s in r["top3"])
        print(f"{mark} {r['id']:<17} expected {'|'.join(r['expected']):<36} top3: {tops}")

    pairs = []
    names = sorted(vecs)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            c = cosine(vecs[a], vecs[b])
            if c >= 0.5:
                pairs.append((round(c, 2), a, b))
    pct1, pct3 = 100 * top1 / len(scored), 100 * top3 / len(scored)
    print(f"\ntop-1 {top1}/{len(scored)} ({pct1:.0f}%), top-3 {top3}/{len(scored)} ({pct3:.0f}%), "
          f"{len(results) - len(scored)} negatives reported only, {len(vecs)} skills")
    for c, a, b in sorted(pairs, reverse=True):
        print(f"collision {c}: {a} ~ {b}")

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump({"top1": top1, "top3": top3, "scored": len(scored), "skills": len(vecs),
                   "collisions": pairs, "results": results}, open(out, "w"), indent=1)
    if "--min-rank1" in sys.argv:
        floor = float(sys.argv[sys.argv.index("--min-rank1") + 1])
        if pct1 < floor:
            print(f"FAIL: top-1 {pct1:.0f}% is below the baseline {floor:.0f}%")
            sys.exit(1)


if __name__ == "__main__":
    main()
