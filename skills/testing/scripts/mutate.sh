#!/bin/sh
# mutate.sh: one mutation check. Replace an exact string in a file (literal, not a regex), run the test command
# under a 2 GB memory cap and a timeout, then restore the file. Exits 0 when the test went RED on the mutant (the
# test catches the bug), 1 when it stayed green, 2 when the mutation could not be applied or restored.
# Usage: mutate.sh <file> <exact-old> <exact-new> -- <test command...>
# Why: hand-written sed/perl mutations silently did not apply (regex syntax in code) and read as "weak test";
# unbounded test runs crashed the box twice (HARVEST 2026-10-25/26).
set -u
[ $# -ge 5 ] && [ "$4" = "--" ] || { echo "usage: mutate.sh <file> <exact-old> <exact-new> -- <test command...>" >&2; exit 2; }
f=$1 old=$2 new=$3; shift 4
backup=$(mktemp) && cp -p "$f" "$backup" || exit 2
restore() { cp -p "$backup" "$f" && rm -f "$backup"; }
trap restore EXIT INT TERM
python3 -I - "$f" "$old" "$new" <<'PY' || exit 2
import sys
p, old, new = sys.argv[1:]
s = open(p).read()
n = s.count(old)
if n != 1:
    sys.exit(f"mutation not applied: the old string occurs {n} times in {p} (needs exactly 1)")
open(p, "w").write(s.replace(old, new))
PY
cmp -s "$f" "$backup" && { echo "mutation not applied: file unchanged" >&2; exit 2; }
systemd-run --user --scope -q -p MemoryMax=2G timeout 120 "$@" >/dev/null 2>&1
code=$?
restore; trap - EXIT INT TERM
[ -f "$backup" ] && { echo "restore failed: $f" >&2; exit 2; }
if [ "$code" -eq 0 ]; then echo "SURVIVED: the test stayed green on the mutant ($f)"; exit 1; fi
echo "caught: the test went red on the mutant (exit $code)"; exit 0
