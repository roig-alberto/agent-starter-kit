#!/usr/bin/env python3
"""How often each skill in ~/.agents/skills was really used: Skill tool calls, SKILL.md reads and slash commands in
Claude Code transcripts, plus skill tool calls in OpenCode's database, over the last --days.

Why (2026-10-19): no audit measured usage; `plain` had never been used and nobody knew. Claude Code keeps only about
30 days of transcripts (default cleanupPeriodDays), so --record appends each month's counts to a ledger and a skill is
flagged only after --months recorded months in a row at zero. Router-eval runs live in /tmp folders and are left out.

Usage: skill-usage.py [--days 30] [--record] [--months 2]
Prints report lines for the monthly audit; the last line is `FLAGGED <n>`.
"""
import argparse, datetime, json, os, re, sqlite3

HOME = os.path.expanduser("~")
SKILLS = f"{HOME}/.agents/skills"
LEDGER = f"{HOME}/.claude/audit-reports/skill-usage.tsv"


def own_skills():
    return sorted(d for d in os.listdir(SKILLS) if os.path.isfile(f"{SKILLS}/{d}/SKILL.md"))


def claude_events(since):
    """(skill, iso date) per use; also the oldest transcript date seen."""
    root, out, oldest = f"{HOME}/.claude/projects", [], None
    read = re.compile(r"/skills/([^/]+)/SKILL\.md")
    cmd = re.compile(r"<command-name>/?([^<\s]+)")
    for proj in os.listdir(root) if os.path.isdir(root) else []:  # absent until the first Claude session
        if proj.startswith("-tmp"):  # router-eval and other synthetic runs
            continue
        for dp, _, files in os.walk(f"{root}/{proj}"):
            for f in files:
                if not f.endswith(".jsonl"):
                    continue
                with open(f"{dp}/{f}", errors="replace") as fh:
                    for line in fh:
                        m = re.search(r'"timestamp":"([^"]+)"', line)
                        if m and (oldest is None or m.group(1) < oldest):
                            oldest = m.group(1)
                        if not m or m.group(1) < since or ('"Skill"' not in line and "SKILL.md" not in line and "command-name" not in line):
                            continue
                        try:
                            r = json.loads(line)
                        except ValueError:
                            continue
                        c = (r.get("message") or {}).get("content")
                        if r.get("type") == "assistant" and isinstance(c, list):
                            for b in c:
                                if not isinstance(b, dict) or b.get("type") != "tool_use":
                                    continue
                                i = b.get("input") or {}
                                if b.get("name") == "Skill" and i.get("skill"):
                                    out.append(i["skill"].split(":")[-1])
                                elif b.get("name") == "Read" and (s := read.search(i.get("file_path") or "")):
                                    out.append(s.group(1))
                        elif r.get("type") == "user":
                            txt = c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else ""
                            if s := cmd.match(txt.lstrip()):
                                out.append(s.group(1))
    return out, oldest


def opencode_events(since_ms):
    db = f"{HOME}/.local/share/opencode/opencode.db"
    if not os.path.exists(db):
        return [], "not installed"
    out = []

    def walk(x):
        if isinstance(x, dict):
            if x.get("type") == "tool" and x.get("name") == "skill":
                sid = ((x.get("state") or {}).get("input") or {}).get("id")
                if sid:
                    out.append(sid)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    try:
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        for (data,) in c.execute("select data from session_message where time_created >= ? and data like '%\"name\":\"skill\"%'", (since_ms,)):
            try:
                walk(json.loads(data))
            except ValueError:
                pass
    except sqlite3.Error as e:
        return [], f"unreadable ({e})"
    return out, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--record", action="store_true", help="append this month's counts to the ledger (once per month)")
    ap.add_argument("--months", type=int, default=2, help="recorded months in a row at zero before a skill is flagged")
    a = ap.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc)
    since = now - datetime.timedelta(days=a.days)
    skills = own_skills()
    cl, oldest = claude_events(since.strftime("%Y-%m-%dT%H:%M:%S"))
    oc, oc_state = opencode_events(int(since.timestamp() * 1000))
    counts = {s: 0 for s in skills}
    for name in cl + oc:
        if name in counts:
            counts[name] += 1

    month = now.strftime("%Y-%m")
    rows = []
    if os.path.exists(LEDGER):
        rows = [l.rstrip("\n").split("\t") for l in open(LEDGER) if l.strip()]
    if a.record and not any(r[0] == month for r in rows):
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        with open(LEDGER, "a") as fh:
            for s in skills:
                fh.write(f"{month}\t{s}\t{counts[s]}\n")
        rows += [[month, s, str(counts[s])] for s in skills]

    months = sorted({r[0] for r in rows})[-a.months:]
    flagged = [s for s in skills if len(months) >= a.months and all(any(r[0] == m and r[1] == s and r[2] == "0" for r in rows) for m in months)]
    unused = [s for s in skills if counts[s] == 0]
    top = sorted(counts.items(), key=lambda x: -x[1])[:8]
    print(f"- window: last {a.days} days; Claude Code transcripts back to {(oldest or '?')[:10]}; OpenCode {oc_state}; {len(cl)} + {len(oc)} uses of any skill")
    print(f"- unused this window ({len(unused)}): {', '.join(unused) or 'none'}")
    print(f"- most used: {', '.join(f'{s} {n}' for s, n in top)}")
    print(f"- unused {a.months} recorded months in a row ({len(flagged)}): {', '.join(flagged) or 'none'} (retro decides: merge, sharpen the description, or delete)")
    print(f"FLAGGED {len(flagged)}")


if __name__ == "__main__":
    main()
