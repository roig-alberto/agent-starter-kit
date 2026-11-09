"""Tests for bitter_lesson.py. Run: python3 -m unittest discover -s ~/.claude/scripts -p 'test_bitter_lesson.py'

Adapted from georgewangyu/GeorgeCodingSkills skills/principles-bitter-lesson/tests (MIT, notice in
bitter_lesson.py).
"""
import datetime
import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_spec = importlib.util.spec_from_file_location("bitter_lesson", Path(__file__).resolve().parent / "bitter_lesson.py")
bl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bl)

KEEP, SOFT = bl.ORDER

SKILL = f"""---
name: demo
description: mentions [bl: {SOFT}] in frontmatter, which is ignored
---

# Demo

Tags look like `[bl: {SOFT}]` in prose, which is a mention.

1. **Push back when warranted.** You are not a yes-machine. [bl: {SOFT}]

```
## Example [bl: {SOFT}]
```

2. **Verify.** Run the tests. [bl: {KEEP}]
"""

RULES = """# Rules

- Never write `sudo <cmd>`. The hook breaks it.
- Run each verification once. Re-run only after a change.
"""

HEADER = "| Item | Tag | Why | Review | Delete when | Ablation |\n|---|---|---|---|---|---|\n"
SKILL_ROWS = [
    ("1. Push back", SOFT, "coaching", "2027-01-26", "an eval shows no change", ""),
    ("2. Verify", KEEP, "feedback signal", "", "", ""),
]
RULES_ROWS = [
    ("Never write sudo", KEEP, "box fact", "", "", ""),
    ("Run each verification once", SOFT, "coaching", "2027-01-26", "an eval shows no change", ""),
]


def sidecar(rows):
    return "# Bitter lesson\n\n" + HEADER + "".join(f"| {' | '.join(r)} |\n" for r in rows)


class BitterLessonTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.skills = Path(tempfile.mkdtemp())
        self.skill = self.skills / "demo"
        self.skill.mkdir()
        (self.root / bl.ALLOWLIST).write_text("# ratchet\nskills/demo\nRULES.md\n")
        self.write()

    def write(self, skill=SKILL, skill_rows=SKILL_ROWS, rules=RULES, rules_rows=RULES_ROWS):
        (self.skill / "SKILL.md").write_text(skill)
        (self.skill / bl.SIDECAR).write_text(sidecar(skill_rows))
        (self.root / "RULES.md").write_text(rules)
        (self.root / "RULES.bitter-lesson.md").write_text(sidecar(rules_rows))

    def errors(self):
        return bl.check_all(self.root, self.skills)[1]

    def run_main(self, *args):
        out, err = io.StringIO(), io.StringIO()
        old = bl.SKILLS
        bl.SKILLS = self.skills
        try:
            with redirect_stdout(out), redirect_stderr(err):
                code = bl.main([*args, "--root", str(self.root)])
        finally:
            bl.SKILLS = old
        return code, out.getvalue(), err.getvalue()

    def test_tags_skip_frontmatter_fences_and_code_spans(self):
        self.assertEqual([(i["text"], i["tag"]) for i in bl.tagged_items(SKILL)], [
            ("1. Push back when warranted. You are not a yes-machine.", SOFT), ("2. Verify. Run the tests.", KEEP)])

    def test_check_passes_when_tags_and_rows_match(self):
        self.assertEqual(self.errors(), [])

    def test_tagged_skill_line_without_row_fails(self):
        self.write(skill_rows=SKILL_ROWS[1:])
        self.assertEqual(len(self.errors()), 1)
        self.assertIn("has no row", self.errors()[0])

    def test_reworded_rule_line_makes_its_row_stale(self):
        self.write(rules=RULES.replace("Run each verification once", "Run every check one time"))
        self.assertEqual(len(self.errors()), 1)
        self.assertIn("stale row", self.errors()[0])

    def test_plain_file_must_not_carry_tag_text(self):
        self.write(rules=RULES.replace("after a change.", f"after a change. [bl: {SOFT}]"))
        self.assertTrue(any("no tag text in this file" in e for e in self.errors()))

    def test_tag_mismatch_unknown_tag_and_required_fields(self):
        self.write(skill=SKILL.replace(f"[bl: {KEEP}]", "[bl: strong]"),
                   rules_rows=[RULES_ROWS[0], ("Run each verification once", SOFT, "", "next week", "", "")])
        errs = " ".join(self.errors())
        self.assertIn("got 'strong'", errs)
        self.assertIn("is tagged 'strong' in SKILL.md but 'invariant' here", errs)
        self.assertIn("needs a why", errs)
        self.assertIn("is not YYYY-MM-DD", errs)
        self.assertIn("needs delete-when", errs)

    def test_ambiguous_and_duplicate_rows(self):
        self.write(rules=RULES + "- Run a lint too.\n",
                   rules_rows=RULES_ROWS + [("Run", KEEP, "x", "", "", ""), ("Never write sudo <cmd>", KEEP, "x", "", "", "")])
        errs = " ".join(self.errors())
        self.assertIn("matches 2 lines", errs)
        self.assertIn("describes the same line", errs)

    def test_no_allowlist_skips_with_notice(self):
        (self.root / bl.ALLOWLIST).unlink()
        self.assertEqual(bl.check_all(self.root, self.skills), (None, []))
        code, out, _ = self.run_main("check")
        self.assertEqual(code, 0)
        self.assertIn("check skipped", out)

    def test_main_check_exit_codes(self):
        self.assertEqual(self.run_main("check")[0], 0)
        self.write(skill_rows=SKILL_ROWS[1:])
        self.assertEqual(self.run_main("check")[0], 1)

    def test_report_lists_soft_rows_from_every_entry_past_review_first(self):
        self.write(rules_rows=[RULES_ROWS[0], ("Run each verification once", SOFT, "c", "2026-01-01", "x", "")])
        rows = list(bl.report_rows(self.root, self.skills, datetime.date(2026, 10, 27)))
        self.assertEqual(sorted(r["item"] for _, r, _ in rows), ["1. Push back", "Run each verification once"])
        code, out, _ = self.run_main("report", "--today", "2026-10-27")
        self.assertIn("2 soft line(s), 1 past review", out)
        self.assertLess(out.index("Run each verification once"), out.index("1. Push back"))


if __name__ == "__main__":
    unittest.main()
