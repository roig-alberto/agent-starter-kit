#!/bin/bash
# After changing one skill: run only the fixtures that expect it (about $0.12 each), then score them.
# Usage: ./run-skill.sh <skill-name> [n]
S="$(cd "$(dirname "$0")" && pwd)"; SKILL=$1; N=${2:-1}
awk -F'\t' -v s="$SKILL" '!/^#/ && NF==4 { n=split($3,a,"|"); for(i=1;i<=n;i++) if(a[i]==s) print }' "$S/fixtures.tsv" |
while IFS=$'\t' read -r id prompt expected source; do "$S/run.sh" "$id" "$prompt" "$N"; "$S/fired.py" "$S/$id-$N.jsonl"; done
