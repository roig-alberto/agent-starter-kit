#!/usr/bin/env bash
# Claude Code statusline.
# Line 1: model | Context: N% used  [EFFORT:LEVEL]
# Line 2: ccusage usage  (session / today / block cost + burn rate + block time-left)
# Reads the statusLine JSON on stdin. Node bin dir is pinned so ccusage (and its
# `env node` shebang) resolve regardless of the launching shell's PATH.

CCDIR="$HOME/.local/lib/nodejs/node-v24.18.0-linux-x64/bin"
export PATH="$CCDIR:$PATH"

input=$(cat)

model=$(printf '%s' "$input" | jq -r '.model.display_name')
used=$(printf '%s' "$input" | jq -r '.context_window.used_percentage // empty')
effort=$(printf '%s' "$input" | jq -r '.effort.level // empty')

# ── Line 1: model + context ──────────────────────────────────────────────────
if [ -n "$used" ]; then
  printf '%s | Context: %.0f%% used' "$model" "$used"
else
  printf '%s' "$model"
fi

# ── Effort badge (live session value; reflects mid-session /effort) ───────────
# Absent when the model does not support reasoning effort.
if [ -n "$effort" ]; then
  E=$(printf '%s' "$effort" | tr '[:lower:]' '[:upper:]')
  printf ' \033[38;5;110m[EFFORT:%s]\033[0m' "$E"
fi

# ── Line 2: ccusage usage ────────────────────────────────────────────────────
# ccusage prints:  🤖 MODEL | 💰 COST | 🔥 BURN | 🧠 CTX
# Drop the leading model segment (already on line 1) and the trailing 🧠 context
# segment (line 1 shows the real context %), keep 💰 cost + 🔥 burn.
if command -v ccusage >/dev/null 2>&1; then
  # Strip .context_window before piping: ccusage 20.x parses it strictly and errors
  # on Claude Code's shape. We already show the real context % on line 1, so drop it.
  # ccusage re-parses every transcript JSONL on each call (~200MB, ~1000% CPU for
  # 1-2s). Cache its output per session for 30s; cost numbers lag by that much.
  sid=$(printf '%s' "$input" | jq -r '.session_id // empty')
  cache="$HOME/.cache/ccusage-statusline.${sid:-$PPID}"
  mkdir -p "$HOME/.cache"
  if [ -z "$(find "$cache" -newermt '-30 seconds' 2>/dev/null)" ]; then
    printf '%s' "$input" | jq -c 'del(.context_window)' 2>/dev/null \
      | ccusage statusline 2>/dev/null > "$cache.tmp" && mv "$cache.tmp" "$cache"
  fi
  usage=$(sed -E 's/ \| [^|]*🧠[^|]*$//; s/^[^|]*\| //' "$cache" 2>/dev/null)
  [ -n "$usage" ] && printf '\n%s' "$usage"
fi
