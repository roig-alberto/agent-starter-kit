#!/usr/bin/env bash
# Claude Code statusline: model | Context: N% used  [EFFORT:LEVEL]
# Reads the statusLine JSON on stdin. No ccusage: it re-parsed every transcript
# on each call and held the box at 100% CPU (removed 2026-10-21).

input=$(cat)

model=$(printf '%s' "$input" | jq -r '.model.display_name')
used=$(printf '%s' "$input" | jq -r '.context_window.used_percentage // empty')
effort=$(printf '%s' "$input" | jq -r '.effort.level // empty')

if [ -n "$used" ]; then
  printf '%s | Context: %.0f%% used' "$model" "$used"
else
  printf '%s' "$model"
fi

# Absent when the model does not support reasoning effort.
if [ -n "$effort" ]; then
  E=$(printf '%s' "$effort" | tr '[:lower:]' '[:upper:]')
  printf ' \033[38;5;110m[EFFORT:%s]\033[0m' "$E"
fi
