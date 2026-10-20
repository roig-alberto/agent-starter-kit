#!/usr/bin/env python3
"""Score the real routing runs: did each fixture load an expected skill?

A fixture passes when the first skill it loaded is one of its expected skills, or, for "none", when it
loaded no skill. A run whose scratch repo is not clean afterwards is a harness failure, whatever it loaded.

Usage: score.py [n]      reads <id>-<n>.jsonl (default n=1) next to fixtures.tsv
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
N = sys.argv[1] if len(sys.argv) > 1 else "1"


def fired(path):
    out, cost = [], 0.0
    for line in open(path):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "assistant":
            for c in d.get("message", {}).get("content", []):
                if c.get("type") != "tool_use":
                    continue
                inp = c.get("input", {})
                if c.get("name") == "Skill":
                    out.append(inp.get("skill") or inp.get("command") or "?")
                m = re.search(r"skills/([a-z0-9-]+)/SKILL\.md", inp.get("file_path", ""))
                if c.get("name") == "Read" and m:
                    out.append(m.group(1))
        if d.get("type") == "result":
            cost = d.get("total_cost_usd") or 0.0
    return out, cost


rows, passed, total_cost = [], 0, 0.0
for line in open(os.path.join(HERE, "fixtures.tsv")):
    if line.startswith("#") or not line.strip():
        continue
    fid, prompt, expected, source = line.rstrip("\n").split("\t")
    run = os.path.join(HERE, f"{fid}-{N}.jsonl")
    if not os.path.exists(run):
        rows.append((fid, expected, "NOT RUN", "-"))
        continue
    got, cost = fired(run)
    total_cost += cost
    dirty = open(os.path.join(HERE, f"{fid}-{N}.gitcheck")).read().strip()
    exp = expected.split("|")
    ok = (got[:1] == [] and exp == ["none"]) or (bool(got) and got[0] in exp)
    verdict = "HARNESS-FAIL (wrote files)" if dirty else ("PASS" if ok else "FAIL")
    passed += verdict == "PASS"
    rows.append((fid, expected, ",".join(got) or "none", verdict))

for fid, expected, got, verdict in rows:
    print(f"{verdict:<6} {fid:<17} expected {expected:<38} loaded {got}")
ran = sum(r[3] != "-" for r in rows)
print(f"\npass {passed}/{ran} runs, cost ${total_cost:.2f} API-equivalent (Claude plan, not billed)")
