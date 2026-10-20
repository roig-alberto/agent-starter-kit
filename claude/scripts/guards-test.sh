#!/usr/bin/env bash
# Samples for the safety guards: each rule must block one sample and pass another.
# Covers ~/.claude/scripts/agent-guard.py (pre-command guard) and ~/.claude/git-hooks/
# (commit-msg, pre-push) in a throwaway repo. Run: bash ~/.claude/scripts/guards-test.sh
# Dashes, the fake secret and the floor words are built at runtime, so this file passes its own hooks.
set -u
G=~/.claude/scripts/agent-guard.py
H=~/.claude/git-hooks
fail=0
ok() { printf 'ok   %s\n' "$1"; }
bad() { printf 'FAIL %s\n' "$1"; fail=1; }

guard() { # expect(block|pass) command [cwd]
  local want=$1 cmd=$2 cwd=${3:-/tmp} rc
  jq -n --arg c "$cmd" --arg d "$cwd" '{tool_name:"Bash",tool_input:{command:$c},cwd:$d}' | python3 "$G" 2>/dev/null
  rc=$?
  if { [ "$want" = block ] && [ $rc -eq 2 ]; } || { [ "$want" = pass ] && [ $rc -eq 0 ]; }; then ok "guard $want: $cmd"
  else bad "guard $want (rc $rc): $cmd"; fi
}

app=$(mktemp -d); git -C "$app" init -q
guard block "sudo systemctl restart x"
guard block "cd /tmp && sudo ls"
guard pass  "sudo /bin/sh -c 'systemctl restart x'"
guard pass  "echo 'never write sudo ls'"
guard block "sudo rtk ls"
guard block "rtk git add -A" "$app"
guard block "rtk proxy git push --force"
guard block "git add -A" "$app"
guard block "git add ." "$app"
guard pass  "git add src/a.ts" "$app"
guard pass  "git add -A" ~/.claude
guard block "cd $app && git add --all" ~/.claude
guard block "git push --force origin main"
guard block "git push -f"
guard block "git push origin +main"
guard pass  "git push -u origin main"
guard block "git reset --hard HEAD~1"
guard pass  "git reset --soft HEAD~1"
guard block "git clean -fd"
guard pass  "git clean -n"
guard block "git branch -D old"
guard pass  "git branch -d old"
guard block "git checkout ."
guard block "git restore -- ."
guard pass  "git checkout main"
guard block "git commit --no-verify -m x"
guard block "git -c core.hooksPath=/dev/null commit -m x"
guard pass  "git commit -m 'reset --hard is described here'"
printf 'not json' | python3 "$G" && ok "guard fails open on a bad payload" || bad "guard fails open on a bad payload"

# git hooks in a throwaway repo
r=$(mktemp -d); cd "$r" || exit 1
git init -q -b main; git config user.email t@t; git config user.name t; git config core.hooksPath "$H"
commit() { # expect(block|pass) label message [reason text a block must print]
  local err
  if err=$(git commit -q -m "$3" 2>&1 >/dev/null); then [ "$1" = pass ] && ok "commit pass: $2" || bad "commit should block: $2"
  elif [ "$1" = pass ]; then bad "commit should pass: $2: $err"
  elif [ -n "${4:-}" ] && ! grep -q -- "$4" <<<"$err"; then bad "commit blocked for another reason: $2: $err"
  else ok "commit block: $2"; fi
}
D=$'\u2014'
echo 'export const a = 1' > a.ts; mkdir -p src; printf 'test("x", () => {\n  expect(1).toBe(1)\n  expect(2).toBe(2)\n})\n' > src/a.test.ts
git add -A; commit pass "clean first commit" "start"
echo 'b' > b.txt; git add b.txt; commit block "agent trailer" $'add b\n\nCo-Authored-By: Claude <noreply@anthropic.com>' "agent trailer"
commit pass "same commit, no trailer" "add b"
echo "x $D y" > c.md; git add c.md; commit block "long dash in a file" "add c" "long dash added"
echo "x - y" > c.md; git add c.md; commit block "long dash in the message" "add c $D now" "message contains a long dash"
commit pass "no dashes" "add c"
key="gh""p_$(head -c 400 /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 36)"
echo "token = \"$key\"" > d.ts; git add d.ts; commit block "secret (gitleaks)" "add d" "found a secret"
echo 'export const d = 2' > d.ts; git add d.ts; commit pass "no secret" "add d"
echo "// @ts-""ignore" >> a.ts; git add a.ts; commit block "floor: silenced checker" "touch a" "silenced checker"
commit pass "floor: same with Floor-change line" $'touch a\n\nFloor-change: spec 3.2 dropped the strict type'
sed -i 's/test("x"/test.sk''ip("x"/' src/a.test.ts; git add src/a.test.ts; commit block "floor: skipped test" "skip" "test made easier"
git checkout -q HEAD -- src/a.test.ts; sed -i '/expect(2)/d' src/a.test.ts; git add src/a.test.ts; commit block "floor: assertion removed" "trim" "assertion(s) removed"
git checkout -q HEAD -- src/a.test.ts; git rm -q src/a.test.ts; commit block "floor: test file deleted" "drop test" "test file deleted"
git reset -q HEAD src/a.test.ts; git checkout -q HEAD -- src/a.test.ts
echo "the word eslint-""disable in prose" > e.md; git add e.md; commit pass "floor ignores docs" "doc"
gl=$(command -v gitleaks); PATH=/usr/bin:/bin; echo z > z.txt; git add z.txt
commit block "no gitleaks on PATH fails closed" "z" "not installed"; PATH=$(dirname "$gl"):$PATH

# pre-push: a non-fast-forward push is refused, a normal one passes
bare=$(mktemp -d); git init -q --bare "$bare"; git remote add o "$bare"
git push -q o main 2>/dev/null && ok "push pass: first push" || bad "push pass: first push"
git commit -q --allow-empty -m "one more"; git push -q o main 2>/dev/null && ok "push pass: fast-forward" || bad "push pass: fast-forward"
git reset -q --soft HEAD~1; git commit -q --allow-empty -m "rewritten"
git push -q -f o main 2>/dev/null && bad "push block: force push" || ok "push block: force push"
ALLOW_FORCE_PUSH=1 git push -q -f o main 2>/dev/null && ok "push pass: ALLOW_FORCE_PUSH=1" || bad "push pass: ALLOW_FORCE_PUSH=1"

cd /; rm -rf "$r" "$bare" "$app"
[ $fail -eq 0 ] && echo "guards-test: all passed" || { echo "guards-test: FAILURES"; exit 1; }
