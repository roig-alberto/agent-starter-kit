#!/bin/bash
# One routing run: does this prompt load the expected skill? Writes <id>-<n>.jsonl and <id>-<n>.gitcheck here.
# Usage: ./run.sh <id> "<prompt>" <n>     (one at a time; each run is capped at 2 turns)
# Write-proofed: no Edit/Write/NotebookEdit/Bash/Agent, and it runs in an empty scratch git repo whose
# `git status` must stay empty. An earlier version without these guards edited real app code.
S="$(cd "$(dirname "$0")" && pwd)"
ID=$1; PROMPT=$2; N=$3
DIR=${ROUTER_EVAL_DIR:-/tmp/router-eval-repo}
[ -d "$DIR/.git" ] || { mkdir -p "$DIR" && git -C "$DIR" init -q; }
cd "$DIR"
timeout 600 claude -p "$PROMPT" \
  --disallowedTools Edit Write NotebookEdit Bash Agent \
  --max-turns 2 \
  --permission-mode bypassPermissions --model sonnet \
  --output-format stream-json --verbose < /dev/null 2>/dev/null > "$S/$ID-$N.jsonl"
git -C "$DIR" status --porcelain > "$S/$ID-$N.gitcheck"
