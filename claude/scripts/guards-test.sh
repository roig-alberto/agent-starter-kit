#!/usr/bin/env bash
# Samples for the safety guards: each rule must block one sample and pass another.
# Covers ~/.claude/scripts/agent-guard.py (pre-command guard) and ~/.claude/git-hooks/
# (commit-msg, pre-push) in a throwaway repo. Run: bash ~/.claude/scripts/guards-test.sh
# Dashes, the fake secret and the floor words are built at runtime, so this file passes its own hooks.
set -u
G=~/.claude/scripts/agent-guard.py
H=${GUARD_HOOKS:-~/.claude/git-hooks}
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
# a plain commit would take files another session staged (2026-10-26)
other=$(mktemp -d); git -C "$other" init -q; echo a > "$other/theirs.txt"; echo b > "$other/mine.txt"; git -C "$other" add theirs.txt
guard block "git commit -m x" "$other"
guard block "git add mine.txt && git commit -m x" "$other"
guard pass  "git commit -m x -- mine.txt" "$other"
guard pass  "git add theirs.txt mine.txt && git commit -m x" "$other"
guard pass  "git add src/a.ts && git commit -m x" "$app"
guard pass  "git commit -m x" ~/.claude
# a temporary index holds only the agent's hunks, so it may commit next to another session's staged files (2026-10-28)
guard pass  "GIT_INDEX_FILE=/tmp/idx git commit -m x" "$other"
guard pass  "export GIT_INDEX_FILE=/tmp/idx && git read-tree HEAD && git commit -m x" "$other"
guard block "GIT_INDEX_FILE=.git/index git commit -m x" "$other"
# -a stages the user's unstaged edits too (2026-10-28)
guard block "git commit -am x" "$app"
guard block "git commit --all -m x" "$app"
guard pass  "git commit -m '-a is described here' -- src/a.ts" "$app"
guard pass  "git commit -am x" ~/.claude
# -f stages what .gitignore keeps out (secrets, build output), in every repo (2026-10-28)
guard block "git add -f .env" "$app"
guard block "git add --force dist/x.js" ~/.claude
guard pass  "git add src/f.ts" "$app"
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
mkdir -p synced/s; echo "x $D y" > synced/s/SKILL.md; git add synced; commit pass "long dash in downloaded synced/ skill" "add synced"
key="gh""p_$(head -c 400 /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 36)"
echo "token = \"$key\"" > d.ts; git add d.ts; commit block "secret (gitleaks)" "add d" "found a secret"
echo 'export const d = 2' > d.ts; git add d.ts; commit pass "no secret" "add d"
echo "// @ts-""ignore" >> a.ts; git add a.ts; commit block "floor: silenced checker" "touch a" "silenced checker"
commit pass "floor: same with Floor-change line" $'touch a\n\nFloor-change: spec 3.2 dropped the strict type'
sed -i 's/test("x"/test.sk''ip("x"/' src/a.test.ts; git add src/a.test.ts; commit block "floor: skipped test" "skip" "test made easier"
git checkout -q HEAD -- src/a.test.ts; sed -i '/expect(2)/d' src/a.test.ts; git add src/a.test.ts; commit block "floor: assertion removed" "trim" "assertion(s) removed"
git checkout -q HEAD -- src/a.test.ts; git rm -q src/a.test.ts; commit block "floor: test file deleted" "drop test" "test file deleted"
git reset -q HEAD src/a.test.ts; git checkout -q HEAD -- src/a.test.ts
# a branch may take out an assertion it added itself; one that is on main still counts (2026-11-05, FACTORY-58)
git checkout -q -b feat; echo 'test("y", () => { expect(3).toBe(3) })' >> src/a.test.ts; git add src/a.test.ts; commit pass "floor: branch adds an assertion" "add y"
sed -i '/expect(3)/d' src/a.test.ts; git add src/a.test.ts; commit pass "floor: branch removes its own assertion" "drop y"
sed -i '/expect(2)/d' src/a.test.ts; git add src/a.test.ts; commit block "floor: branch removes an assertion that is on main" "trim" "assertion(s) removed"
git checkout -q HEAD -- src/a.test.ts; git checkout -q main
echo "the word eslint-""disable in prose" > e.md; git add e.md; commit pass "floor ignores docs" "doc"
# a secret file by name; templates and the folder's own .gitignore pass (2026-10-28)
echo 'A=1' > .env; git add .env; commit block "secret file .env" "env" "secret file staged"
git rm -q --cached .env; rm .env; echo 'A=' > .env.example; git add .env.example; commit pass ".env.example template" "env example"
mkdir -p secrets; echo k > secrets/key; git add secrets/key; commit block "file under secrets/" "key" "secret file staged"
git rm -q --cached secrets/key; rm secrets/key; printf '*\n!.gitignore\n' > secrets/.gitignore; git add secrets/.gitignore; commit pass "secrets/.gitignore" "ignore"
# a valid IBAN (checksum built here, so this file holds none); an invalid one is a synthetic fixture (2026-10-28)
iban=$(python3 -c 'import random; b="".join(random.choice("0123456789") for _ in range(20)); n=int("".join(str(int(c,36)) for c in b+"ES00")); print("ES%02d%s" % (98 - n % 97, b))')
echo "const iban = '$iban'" > f.ts; git add f.ts; commit block "valid IBAN in a file" "add f" "IBAN added"
commit block "valid IBAN in the message" "pay $iban" "contains an IBAN"
echo "const iban = '${iban:0:2}00${iban:4}'" > f.ts; git add f.ts; commit pass "invalid-checksum IBAN fixture" "add f"
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
