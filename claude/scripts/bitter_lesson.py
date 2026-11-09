#!/usr/bin/env python3
"""Keep bitter-lesson marks on rule lines honest (plan: ~/.claude/BITTER-LESSON-PLAN.md).

Each tracked rule line is marked "invariant" (keep for good) or "soft" (maybe temporary: a review date and a
"delete when" are required). A side file holds one table row per tracked line, keyed by the line's first
words, with the reason it exists.

- A skill folder (allowlist entry `skills/<name>`) puts a short inline tag such as `[bl: soft]` at the end of
  the line, and keeps its rows in `<folder>/BITTER_LESSON.md`.
- A plain file (any other entry, relative to ~/.claude, for example `RULES.md`) carries no tag text at all.
  Its rows live in `<name>.bitter-lesson.md` next to it, and each row key must still match exactly one line,
  so a reworded rule fails the check.

  bitter_lesson.py check    every allowlisted entry; exit 1 on errors, 0 with a notice when there is no allowlist
  bitter_lesson.py report   every soft row of the allowlisted entries, past review date first

Allowlist: ~/.claude/bitter-lesson.allowlist, one entry per line ('#' comments).

Adapted from georgewangyu/GeorgeCodingSkills skills/principles-bitter-lesson/scripts/bitter_lesson.py:
two tags instead of three, plain-file entries, the report reads the allowlist, no allowlist is not an error,
skill entries resolve against SKILLS_DIR, and the ablate mode is left out.

MIT License

Copyright (c) 2026 George Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse
import datetime
import os
import re
import sys
from pathlib import Path

# Tag name -> the side-file fields it requires.
TAGS = {"invariant": frozenset(), "soft": frozenset({"review", "delete-when"})}
ORDER = list(TAGS)
SOFT = ORDER[-1]

ROOT = Path(os.path.expanduser("~/.claude"))
SKILLS = Path(os.environ.get("SKILLS_DIR") or os.path.expanduser("~/.agents/skills"))
SIDECAR = "BITTER_LESSON.md"
ALLOWLIST = "bitter-lesson.allowlist"
COLUMNS = ("item", "tag", "why", "review", "delete-when", "ablation")
TAG = re.compile(r"\s*\[bl:\s*([^\]]*?)\s*\]")
FENCE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"`[^`]*`")  # tags inside inline code are mentions, not tags


def norm(text):
    text = re.sub(r"^\s*(#{1,6}|[-*+])\s+", "", text)
    return " ".join(text.replace("**", "").replace("`", "").replace("\\|", "|").split())


def starts_with_words(text, prefix):
    return bool(prefix) and (text == prefix or (text.startswith(prefix) and not text[len(prefix)].isalnum()))


def body_lines(text):
    """(line number, line) outside frontmatter and code fences."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        start = next((i + 1 for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
    out, in_fence = [], False
    for i in range(start, len(lines)):
        if FENCE.match(lines[i]):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((i + 1, lines[i]))
    return out


def tagged_items(text):
    """Every inline tag outside frontmatter, code fences and code spans: dicts(text, tag, line)."""
    items = []
    for number, line in body_lines(text):
        match = TAG.search(CODE_SPAN.sub("", line))
        if match:
            items.append({"text": norm(line.replace(match.group(0), "", 1)), "tag": match.group(1), "line": number})
    return items


def plain_items(text):
    """Every non-blank line of an untagged file, as candidate items for row keys."""
    return [{"text": norm(line), "tag": None, "line": n} for n, line in body_lines(text) if line.strip()]


def _cells(line):
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def parse_sidecar(text):
    """Row dicts from the first table whose header matches COLUMNS."""
    rows, in_table = [], False
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip().startswith("|"):
            if in_table:
                break
            continue
        cells = _cells(line)
        if not in_table:
            in_table = tuple(c.lower().replace(" ", "-") for c in cells) == COLUMNS
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        cells += [""] * (len(COLUMNS) - len(cells))
        row = dict(zip(COLUMNS, cells))
        row["line"] = number
        rows.append(row)
    return rows


def _date(value):
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def entry_paths(entry, root=ROOT, skills=SKILLS):
    """(rule file, side file, inline tags?) for one allowlist entry."""
    if entry.startswith("skills/"):
        folder = skills / entry.split("/", 1)[1]
        return folder / "SKILL.md", folder / SIDECAR, True
    path = root / entry
    return path, path.with_name(path.stem + ".bitter-lesson.md"), False


def check_entry(rule_file, sidecar, inline):
    """Error strings for one allowlisted rule file."""
    if not rule_file.is_file():
        return [f"{rule_file}: missing"]
    text = rule_file.read_text(encoding="utf-8")
    tagged = tagged_items(text)
    errors = []
    if inline:
        errors += [f"{rule_file}:{it['line']}: tag must be one of {ORDER}, got {it['tag']!r}"
                   for it in tagged if it["tag"] not in TAGS]
        if not tagged:
            errors.append(f"{rule_file}: no [bl: ...] tags")
        items = tagged
    else:
        errors += [f"{rule_file}:{it['line']}: no tag text in this file; its marks live in {sidecar.name}"
                   for it in tagged]
        items = plain_items(text)
    if not sidecar.is_file():
        return errors + [f"{sidecar}: missing"]
    rows = parse_sidecar(sidecar.read_text(encoding="utf-8"))
    if not rows:
        return errors + [f"{sidecar}: no table with columns {' | '.join(COLUMNS)}"]
    claimed = {}
    for row in rows:
        where, key, tag = f"{sidecar}:{row['line']}", row["item"], row["tag"]
        matched = [it for it in items if starts_with_words(it["text"], norm(key))]
        if not matched:
            errors.append(f"{where}: stale row, no line in {rule_file.name} starts with '{key}'")
        elif len(matched) > 1:
            errors.append(f"{where}: '{key}' matches {len(matched)} lines; add words")
        else:
            item = matched[0]
            if item["line"] in claimed:
                errors.append(f"{where}: '{key}' describes the same line as row {claimed[item['line']]}")
            claimed[item["line"]] = row["line"]
            if inline and item["tag"] != tag:
                errors.append(f"{where}: '{key}' is tagged {item['tag']!r} in {rule_file.name} but {tag!r} here")
        if tag not in TAGS:
            errors.append(f"{where}: tag must be one of {ORDER}, got {tag!r}")
            continue
        if not row["why"]:
            errors.append(f"{where}: '{key}' needs a why")
        if row["review"] and not _date(row["review"]):
            errors.append(f"{where}: review date {row['review']!r} is not YYYY-MM-DD")
        for field in sorted(TAGS[tag]):
            if not row[field]:
                errors.append(f"{where}: {tag} '{key}' needs {field}")
    if inline:
        for item in items:
            if item["line"] not in claimed:
                errors.append(f"{rule_file}:{item['line']}: tagged line '{item['text']}' has no row in {sidecar.name}")
    return errors


def read_allowlist(root=ROOT):
    """Allowlist entries, or None when the file does not exist."""
    path = root / ALLOWLIST
    if not path.is_file():
        return None
    entries = (line.split("#", 1)[0].strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [e for e in entries if e]


def check_all(root=ROOT, skills=SKILLS):
    """(entries, errors). entries is None when there is no allowlist."""
    entries = read_allowlist(root)
    if entries is None:
        return None, []
    errors = [e for entry in entries for e in check_entry(*entry_paths(entry, root, skills))]
    return entries, errors


def report_rows(root=ROOT, skills=SKILLS, today=None):
    """(entry, row, overdue) for every soft row of the allowlisted entries."""
    today = today or datetime.date.today()
    for entry in read_allowlist(root) or []:
        sidecar = entry_paths(entry, root, skills)[1]
        if not sidecar.is_file():
            continue
        for row in parse_sidecar(sidecar.read_text(encoding="utf-8")):
            if row["tag"] != SOFT:
                continue
            review = _date(row["review"])
            yield entry, row, bool(review and review <= today)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mode", choices=("check", "report"))
    ap.add_argument("--root", type=Path, default=ROOT, help="folder holding the allowlist (default ~/.claude)")
    ap.add_argument("--today", type=datetime.date.fromisoformat, default=datetime.date.today())
    a = ap.parse_args(argv)
    if a.mode == "check":
        entries, errors = check_all(a.root, SKILLS)
        if entries is None:
            print(f"bitter-lesson: no {a.root / ALLOWLIST}, check skipped")
            return 0
        for e in errors:
            print(e, file=sys.stderr)
        print(f"bitter-lesson check: {len(entries)} file(s), {len(errors)} error(s)")
        return 1 if errors else 0
    rows = sorted(report_rows(a.root, SKILLS, a.today), key=lambda r: (not r[2], r[1]["review"] or "9999"))
    overdue = sum(1 for _, _, o in rows if o)
    print(f"bitter-lesson report as of {a.today}: {len(rows)} soft line(s), {overdue} past review")
    print("| File | Line | Review | Delete when | Ablation |")
    print("|---|---|---|---|---|")
    for entry, row, is_overdue in rows:
        review = f"{row['review']} PAST" if is_overdue else row["review"]
        print(f"| {entry} | {row['item']} | {review} | {row['delete-when']} | {row['ablation']} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
