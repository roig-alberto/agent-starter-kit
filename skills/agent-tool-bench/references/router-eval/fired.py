#!/usr/bin/env python3
"""Print which skills a run loaded: a Skill tool call, or a Read of a skills/<name>/SKILL.md file.

Usage: fired.py <id>-<n>.jsonl ...     prints: id  fired-skills  turns  cost
"""
import json
import re
import sys

for path in sys.argv[1:]:
    fired, turns, cost = [], "?", "?"
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
                    fired.append(inp.get("skill") or inp.get("command") or "?")
                m = re.search(r"skills/([a-z0-9-]+)/SKILL\.md", inp.get("file_path", ""))
                if c.get("name") == "Read" and m:
                    fired.append(m.group(1))
        if d.get("type") == "result":
            turns, cost = d.get("num_turns"), d.get("total_cost_usd")
    print(f"{path.rsplit('/', 1)[-1]:<26} fired={','.join(fired) or 'none':<32} turns={turns} cost={cost}")
