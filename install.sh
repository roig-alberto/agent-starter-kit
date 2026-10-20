#!/usr/bin/env bash
# Install the kit into this machine's home: claude/ -> ~/.claude, skills/ -> ~/.agents/skills.
# Never overwrites a file that already exists (it lists them); --force overwrites.
# Usage: bash install.sh [--force]
set -euo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
CP=(cp -rn); [ "${1:-}" = "--force" ] && CP=(cp -r)

for t in git python3 jq; do command -v "$t" >/dev/null || { echo "missing: $t"; exit 1; }; done
python3 -c 'import yaml' 2>/dev/null || { echo "missing: PyYAML (sudo apt install python3-yaml); knowledge-lint needs it"; exit 1; }
for t in rtk gitleaks gh; do command -v "$t" >/dev/null || echo "warning: $t not found (README, Prerequisites)"; done

mkdir -p "$HOME/.claude" "$HOME/.agents/skills"
if [ "${1:-}" != "--force" ]; then
  (cd "$KIT/claude" && find . -type f) | while read -r f; do if [ -e "$HOME/.claude/$f" ]; then echo "kept yours: ~/.claude/${f#./}"; fi; done
fi
"${CP[@]}" "$KIT/claude/." "$HOME/.claude/"
"${CP[@]}" "$KIT/skills/." "$HOME/.agents/skills/"
chmod +x "$HOME/.claude/scripts/"* "$HOME/.claude/git-hooks/"* "$HOME/.claude/statusline.sh"
[ -e "$HOME/.claude/skills" ] || ln -s "$HOME/.agents/skills" "$HOME/.claude/skills"

# Own CLIs the skills call (review-diff, ui-check). ui-check runs in the playwright uv tool's Python when it exists.
mkdir -p "$HOME/.local/bin"
for f in "$KIT/bin/"*; do
  dst="$HOME/.local/bin/$(basename "$f")"
  if [ -e "$dst" ] && [ "${1:-}" != "--force" ]; then echo "kept yours: $dst"; continue; fi
  install -m 755 "$f" "$dst"
done
py="$HOME/.local/share/uv/tools/playwright/bin/python"
[ -x "$py" ] && sed -i "1s|.*|#!$py|" "$HOME/.local/bin/ui-check"

# Global git hooks (secret scan, no agent trailers, no long dashes, no force push). Only when none are set.
cur="$(git config --global core.hooksPath || true)"
if [ -z "$cur" ]; then git config --global core.hooksPath "$HOME/.claude/git-hooks"
elif [ "$cur" != "$HOME/.claude/git-hooks" ]; then echo "warning: core.hooksPath is already $cur; the kit's git hooks are not active"; fi

# Files for ~/.config: the rtk config (the commands it leaves unfiltered, RTK.md).
mkdir -p "$HOME/.config"
"${CP[@]}" "$KIT/config/." "$HOME/.config/"

echo "installed. Next: fill in ~/.claude/ENVIRONMENT.md, then README.md 'After install'."
