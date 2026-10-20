#!/usr/bin/env bash
# autopush-knowledge.sh - Stop-hook durability net.
#
# Why: a skill / rule / memory that lives ONLY on this box dies with it. The
# planned Windows+WSL2 -> Proxmox move (portability skill) demands every
# knowledge artifact already be in its GitHub repo. This commits+pushes any
# pending changes in the two knowledge repos at each turn end, so "created a
# skill" always implies "it is in the repo".
#
# Repos ("respective repo" per artifact):
#   ~/.agents/skills  -> <github-user>/claude-skills   (the skills themselves)
#   ~/.claude         -> <github-user>/claude-config   (RULES.md router line, memories, settings)
#
# Safety: never `git add -f`; refuse to commit obvious secrets; push is
# best-effort (a commit is kept locally and retried next turn if push fails).
# Runs async from the Stop hook, so it never blocks a turn.
#
# Usage: autopush-knowledge.sh [--dry-run]

set -uo pipefail
export GIT_TERMINAL_PROMPT=0   # never hang waiting for a credential prompt

# Agent Factory marks its agents (AGENT_FACTORY_RUN, server/taskenv.ts agentEnv): user hooks run inside factory
# Claude sessions, and a factory run must never commit or push the knowledge repos (it pushes its own merges).
[ -n "${AGENT_FACTORY_RUN:-}" ] && exit 0

DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

LOG="$HOME/.claude/skills-autopush.log"   # gitignored by claude-config's whitelist
stamp() { date '+%Y-%m-%d %H:%M:%S'; }
note()  { echo "[$(stamp)] $*" >>"$LOG"; }
# A problem that stops a repo from syncing also goes to Telegram, once a day per distinct message: this hook runs
# async, so a line in the log alone went unseen (an ABORT left dev-system unpushed for 30 min, 2026-10-16).
loud()  {
  note "$*"
  local seen="$HOME/.claude/.autopush-alerted" key; key="$(date +%F) $(printf '%s' "$*" | sha1sum | cut -c1-12)"
  grep -qxF "$key" "$seen" 2>/dev/null && return 0
  echo "$key" >>"$seen"
  sudo -n /usr/local/bin/tg-alert "knowledge auto-push: $*" >/dev/null 2>&1 || note "tg-alert failed"
}

# paths that must NEVER be committed (RULES.md secret rule). .env.example is fine.
SECRET_RE='(^|/)\.env($|\.)|(^|/)secrets/|nas_backup_key|nas_known_hosts|\.pw$|_key$'

sync_repo() {
  local dir="$1" label="$2"
  [ -d "$dir/.git" ] || return 0
  git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 0

  local changed
  changed="$(git -C "$dir" status --porcelain 2>/dev/null)"
  [ -z "$changed" ] && return 0

  # names of changed/untracked files (respecting .gitignore already)
  local names offenders
  names="$(printf '%s\n' "$changed" | sed 's/^...//; s/^.* -> //')"
  offenders="$(printf '%s\n' "$names" | grep -Ei "$SECRET_RE" | grep -Ev '\.env\.example$' || true)"

  if [ -n "$offenders" ]; then
    loud "$label ABORT: secret-like path(s) present, nothing pushed (see skills-autopush.log)"
    printf '  %s\n' $offenders >>"$LOG"
    return 0
  fi

  local n msg
  n="$(printf '%s\n' "$names" | grep -c .)"
  msg="auto-sync: $(printf '%s\n' "$names" | sed 's#/.*##' | sort -u | head -5 | paste -sd, - | sed 's/,/, /g')"

  if [ "$DRY" = 1 ]; then
    note "$label DRY-RUN would commit+push $n file(s): $msg"
    printf '  %s\n' $names >>"$LOG"
    return 0
  fi

  git -C "$dir" add -A || { note "$label add failed"; return 0; }
  git -C "$dir" commit -q -m "$msg" 2>>"$LOG" || { loud "$label commit failed (a commit hook refused it? see skills-autopush.log)"; return 0; }
}

# push if HEAD is ahead of upstream. Covers BOTH a fresh commit and one stranded
# by an earlier rejected push (a clean-but-ahead repo). On rejection, rebase onto
# the remote and retry once; abort the rebase on conflict so the tree is never
# left mid-rebase (the commit stays local, retried next turn).
push_repo() {
  local dir="$1" label="$2" ahead
  [ -d "$dir/.git" ] || return 0
  ahead="$(git -C "$dir" rev-list --count @{u}..HEAD 2>/dev/null || echo 0)"
  [ "$ahead" -gt 0 ] 2>/dev/null || return 0

  if git -C "$dir" push -q 2>>"$LOG"; then
    note "$label pushed ($ahead commit(s))"
  elif git -C "$dir" pull --rebase -q 2>>"$LOG" && git -C "$dir" push -q 2>>"$LOG"; then
    note "$label pushed after rebase"
  else
    git -C "$dir" rebase --abort 2>/dev/null
    note "$label push FAILED (kept local, retries next turn)"
  fi
}

# Repo list: one path per line in the conf file (# comments allowed, ~ / $HOME
# expanded). KNOWLEDGE/CONFIG repos ONLY - never app-code repos, whose deliberate
# branch -> PR -> commit-when-asked workflow this would wreck. Falls back to the two
# core knowledge repos if the conf is missing.
CONF="$HOME/.claude/scripts/autopush-repos.conf"
label_for() {
  local u; u="$(git -C "$1" remote get-url origin 2>/dev/null)"
  [ -n "$u" ] && basename "$u" .git || basename "$1"
}

REPOS=()
if [ -f "$CONF" ]; then
  while IFS= read -r line; do
    line="$(printf '%s' "$line" | sed 's/#.*//; s/^[[:space:]]*//; s/[[:space:]]*$//')"
    [ -z "$line" ] && continue
    eval line="$line"   # expand ~ and $HOME
    REPOS+=("$line")
  done < "$CONF"
else
  REPOS=("$HOME/.agents/skills" "$HOME/.claude")
fi

# A crashed git leaves an empty index.lock that silently blocks every later `git add`
# (claude-config sat uncommitted for 2 days that way). Clear one only when no git runs.
clear_stale_lock() {
  local lock="$1/.git/index.lock"
  [ -f "$lock" ] || return 0
  pgrep -x git >/dev/null 2>&1 && return 0
  [ -n "$(find "$lock" -mmin +5 2>/dev/null)" ] || return 0
  rm -f "$lock" && note "$(label_for "$1") removed stale index.lock"
}

# Gate: lint. On lint errors, commit nothing in the knowledge repos (broken knowledge never
# reaches GitHub); other repos still sync. The fleet facts (FLEET.md, fleet.json) are no longer
# generated here: Agent Factory's hourly "Fleet facts" loop regenerates and commits them (its D183).
python3 "$HOME/.claude/scripts/build-opencode-agents.py" 2>>"$LOG" || note "build-opencode-agents failed"
LINT_OUT="$(python3 "$HOME/.claude/scripts/knowledge-lint.py" --quiet 2>&1)"
LINT_OK=$?
printf '%s\n' "$LINT_OUT" > "$HOME/.claude/knowledge-lint.last"
GATED_RE="^($HOME/.agents/skills|$HOME/.claude)$"

for r in "${REPOS[@]}"; do
  clear_stale_lock "$r"
  if [ -f "$HOME/.claude/knowledge-hold" ] && [[ "$r" =~ $GATED_RE ]]; then
    note "$(label_for "$r") HELD: ~/.claude/knowledge-hold exists (agents still writing): $(head -c 120 "$HOME/.claude/knowledge-hold")"
    continue
  fi
  if [ "$LINT_OK" -ne 0 ] && [[ "$r" =~ $GATED_RE ]]; then
    loud "$(label_for "$r") HELD: knowledge-lint failed ($(tail -1 <<<"$LINT_OUT")); see ~/.claude/knowledge-lint.last"
    continue
  fi
  sync_repo "$r" "$(label_for "$r")"
done
[ "$DRY" = 1 ] && exit 0
for r in "${REPOS[@]}"; do push_repo "$r" "$(label_for "$r")"; done
exit 0
