#!/usr/bin/env bash
# skill-change-check.sh - the Verify step of an Agent Factory skills task (agent-factory docs/SYSTEM-AREA-PLAN.md
# phase 3). Runs in the task's worktree of ~/.agents/skills, never the main checkout:
#   1. knowledge-lint.py over the worktree's skills,
#   2. knowledge-preserve.py for each skill the branch changed, against the merge base (no lost commands, paths, URLs),
#   3. router-eval word_rank.py at the saved top-1 baseline.
# The router check keeps reading the live RULES.md, which already routes every existing skill.
#
# Usage: [SKILLS_DIR=<worktree>] skill-change-check.sh [<merge-base>]   default base: merge-base of HEAD and main
# Exit 1 when any check fails; each check prints its own lines.
set -uo pipefail
export SKILLS_DIR="${SKILLS_DIR:-$PWD}"
cd "$SKILLS_DIR" || exit 1
base="${1:-$(git merge-base HEAD main)}"
here="$(dirname "$(readlink -f "$0")")"
fail=0

echo "== lint"
python3 "$here/knowledge-lint.py" --quiet || fail=1

echo "== lost text since ${base:0:10}"
for s in $(git diff --name-only "$base" HEAD | awk -F/ 'NF > 1 { print $1 }' | sort -u); do
  git cat-file -e "$base:$s" 2>/dev/null || continue # a skill new on this branch has nothing to lose
  python3 "$here/knowledge-preserve.py" "$s" "$base" || fail=1
done

echo "== routing"
rr=agent-tool-bench/references/router-eval
floor="$(python3 -c "import json; print(json.load(open('$rr/baseline.json'))['word_rank']['top1_pct'])")"
python3 "$rr/word_rank.py" --min-rank1 "$floor" | tail -n 2 || fail=1

[ "$fail" = 0 ] && echo "skill-change-check: all passed" || echo "skill-change-check: FAILED"
exit "$fail"
