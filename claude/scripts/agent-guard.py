#!/usr/bin/env python3
"""Pre-command guard for every agent's shell tool (Claude Code, Codex, OpenCode).

Blocks the shell mistakes git hooks cannot see: a bare sudo (the rtk hook breaks it
silently), `git add -A` in an app repo, destructive git, and skipping the git hooks.

Input: a PreToolUse JSON payload on stdin (Claude Code and Codex: .tool_input.command,
.cwd), or `--command <cmd> [--cwd <dir>]` (the OpenCode plugin).
Output: exit 0 to allow; exit 2 with the reason on stderr to deny.
A broken payload fails open (exit 0), so a bad hook never blocks every command.
Samples: ~/.claude/scripts/guards-test.sh.
"""
import json
import os
import shlex
import subprocess
import sys

HOME = os.path.expanduser("~")
CONF = os.path.join(HOME, ".claude/scripts/autopush-repos.conf")
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "\n", "|&", ";;"}
SHELLS = {"sh", "bash", "/bin/sh", "/bin/bash", "/usr/bin/sh", "/usr/bin/bash"}


def tokens(cmd):
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()\n")
    lex.whitespace = " \t"
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:  # unbalanced quotes: fall back to a plain split
        return cmd.replace("\n", " \n ").replace(";", " ; ").replace("&&", " && ").split(" ")


def commands(cmd):
    """Split into simple commands; drop leading VAR=value words."""
    out, cur = [], []
    for t in tokens(cmd):
        if t in SEPARATORS or t == "$":
            if cur:
                out.append(cur)
            cur = []
        elif t:
            cur.append(t)
    if cur:
        out.append(cur)
    cleaned = []
    for c in out:
        while c and "=" in c[0] and not c[0].startswith("-") and c[0].split("=")[0].isidentifier():
            c = c[1:]
        if c:
            cleaned.append(c)
    return cleaned


def knowledge_repos():
    repos = set()
    try:
        for line in open(CONF):
            path = line.split("#")[0].strip()
            if path:
                repos.add(os.path.realpath(os.path.expandvars(path)))
    except OSError:
        pass
    return repos


def toplevel(d):
    try:
        r = subprocess.run(["git", "-C", d, "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=5)
        return os.path.realpath(r.stdout.strip()) if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def short_flags(args):
    return "".join(a[1:] for a in args if a.startswith("-") and not a.startswith("--"))


def check_git(args, where):
    """args: everything after `git`. Returns a deny reason or None."""
    i, target = 0, where
    while i < len(args) and args[i].startswith("-"):
        a = args[i]
        if a == "-C" and i + 1 < len(args):
            target = os.path.join(where, os.path.expanduser(args[i + 1]))
            i += 2
            continue
        if a == "-c" and i + 1 < len(args):
            if args[i + 1].lower().startswith("core.hookspath"):
                return "git -c core.hooksPath=... skips the safety git hooks."
            i += 2
            continue
        i += 1
    if i >= len(args):
        return None
    sub, rest = args[i], args[i + 1:]
    if "--no-verify" in rest or (sub == "commit" and "-n" in rest):
        return f"git {sub} --no-verify skips the safety git hooks. Fix what the hook reports instead."
    if sub == "push":
        if any(a.startswith("--force") or a == "--mirror" for a in rest) or "f" in short_flags(rest) \
                or any(a.startswith("+") for a in rest):
            return "Force push is blocked: it can discard commits on the remote. Ask the user to run it."
    if sub == "reset" and "--hard" in rest:
        return "git reset --hard discards uncommitted work. Use git stash, or ask the user."
    if sub == "clean" and ("--force" in rest or "f" in short_flags(rest)):
        return "git clean -f deletes untracked files. List them with git clean -n and ask the user."
    if sub == "branch" and ("D" in short_flags(rest) or ("--delete" in rest and "--force" in rest)):
        return "git branch -D deletes an unmerged branch. Use git branch -d, or ask the user."
    if sub in ("checkout", "restore") and "." in rest:
        return f"git {sub} . discards every uncommitted change. Name the files, or ask the user."
    if sub == "add" and ({"-A", "--all", ".", ":/"} & set(rest) or "A" in short_flags(rest)):
        top = toplevel(target)
        if top is None or top not in knowledge_repos():
            return ("git add -A / git add . would stage the user's other uncommitted work. "
                    "Stage your own files by explicit path.")
    return None


def check(cmd, cwd):
    where = cwd or os.getcwd()
    for c in commands(cmd):
        if c[0] == "rtk":  # OpenCode's rtk plugin may rewrite the command before this guard sees it
            c = c[2:] if c[1:2] == ["proxy"] else c[1:]
            if not c:
                continue
        word = os.path.basename(c[0]) if c[0].endswith("/git") else c[0]
        if word in ("command", "exec", "time", "nohup") and len(c) > 1:
            c, word = c[1:], c[1]
        if word == "cd" and len(c) > 1:
            where = os.path.join(where, os.path.expanduser(c[1]))
        elif word == "sudo":
            rest = [a for a in c[1:] if not a.startswith("-")]
            if not (len(rest) >= 1 and rest[0] in SHELLS and "-c" in c):
                return ("Bare sudo is blocked: the rtk hook rewrites it to `sudo rtk <cmd>`, which fails "
                        "silently. Write sudo /bin/sh -c '<cmd>'.")
        elif word == "git":
            reason = check_git(c[1:], where)
            if reason:
                return reason
    return None


def main():
    argv = sys.argv[1:]
    if "--command" in argv:
        cmd = argv[argv.index("--command") + 1] if argv.index("--command") + 1 < len(argv) else ""
        cwd = argv[argv.index("--cwd") + 1] if "--cwd" in argv and argv.index("--cwd") + 1 < len(argv) else None
    else:
        try:
            payload = json.load(sys.stdin)
            cmd = payload.get("tool_input", {}).get("command") or ""
            cwd = payload.get("cwd")
        except (ValueError, AttributeError):
            return 0
    if not isinstance(cmd, str) or not cmd:
        return 0
    reason = check(cmd, cwd)
    if reason:
        print(f"agent-guard: {reason}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
