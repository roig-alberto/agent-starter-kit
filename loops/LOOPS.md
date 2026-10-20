# Recurring checks (the loops)

On the home box these run as loops in Agent Factory, a separate self-hosted app. Each finding goes to its Triage
inbox, and the user decides there. Without Agent Factory, run the plain-code checks from any scheduler and read their
JSON output. The model checks are prompts you can start in any agent.

## Enabled on the home box

| Loop | When | Model? | What it does | Run it by hand |
|---|---|---|---|---|
| Box checks | weekly, Sunday 07:30 | no | Six checks (table below). One finding per problem; a check that crashes reports itself as broken. | `python3 ~/.claude/scripts/box-checks.py <check>` |
| Fleet facts | hourly | no | Regenerates `~/.claude/FLEET.md` and `fleet.json` (containers, ports, volumes) and commits only those two files when they changed. Needs `docker`, `ss`, `git`. | `python3 ~/.claude/scripts/fleet-facts.py` |
| Main is red | on every main change, plus Sunday 06:00 | no | Runs each repo's own checks on the newest main commit. A failure becomes a finding. | your repo's test command on `main` |
| Skipped scheduled jobs | daily 08:00 | no | Reads the last day of each container's logs for node-cron's "missed execution" lines. A job that silently skipped looks healthy otherwise. | `docker logs --since 24h <c> 2>&1 \| grep -a "missed execution"` |
| Starter kit sync | weekly, Sunday 08:00 | yes, one tool-less turn | Runs this kit's `export.py`, then Sonnet reads the staged diff for personal data. Pushes only when the review answers CLEAN. A new file or repo nobody classified, a leak, a flag or a refused commit goes to Triage instead. | `python3 export.py` in the kit |
| Knowledge audit | quarterly (Jan, Apr, Jul, Oct, day 1) | yes | The `skills-audit` skill over a snapshot of skills, rules, memories and project docs, with secrets masked. Lists what is wrong now, most important first. | ask an agent: "run skills-audit" |

## Built but switched off

| Loop | When | Model? | What it does |
|---|---|---|---|
| Weekly skills review | Sunday 09:00 | yes | Reads the week's skill loads, corrections after a load, skill changes and HARVEST. Proposes at most 5 skill changes, each with its evidence. Superseded by the box checks plus the quarterly audit. |
| Weekly dependency check | Monday 07:00 | no | `npm outdated` (majors) and `npm audit` per repo. |
| FEATURES.md sync | on main change | no | New unticked FEATURES.md rows become findings. |
| Nightly code health | daily 03:00 | yes | Runs the checks, then reads the code for bugs, risky code and missing tests. At most 3 findings. |

## The six box checks

Each one prints one JSON object, `{"problems": [{"key", "title", "fix"}], "info": "..."}`, and exits 0. A problem's
`key` stays the same across runs, so a scheduler can report each problem once.

| Check | What it checks | Adapt on a new machine |
|---|---|---|
| `deploy-sync` | The copies of host scripts in `/usr/local/bin` and `/etc/systemd/system` still match their source in the infra repo. | The pairs list in `box-checks.py` is box-specific. Edit it or drop the check. |
| `guards` | `guards-test.sh` passes: the guards still block bare `sudo`, `git add -A` in an app repo, force pushes and agent trailers. | none |
| `routing` | The skill routing score (`agent-tool-bench/references/router-eval/word_rank.py`): how often the router picks the right skill for 60 sample prompts. Reported as a score, not a pass or fail. | The fixtures name the home box's skills. Re-score after you add or drop skills. |
| `harvest` | `HARVEST.md` has no processed entries older than 90 days. | none |
| `project-docs` | Each app that FLEET.md lists has the canonical docs (RULES.md, "Canonical project docs"). | Needs FLEET.md. |
| `skill-usage` | Lists skills unused for two recorded months, for `retro` to merge, sharpen or delete. | Starts empty on a new machine. |

## The model checks without Agent Factory

`loops/prompts/` holds each model check's prompt, exported from Agent Factory. Each `{{name}}` is a value the loop fills
in: for the knowledge audit, `{{index}}` is the list of files in a snapshot folder of your knowledge. Run one by hand with
any agent after replacing the placeholders, or simply ask an agent to "run skills-audit".

## Without Agent Factory: a crontab

RULES.md says recurring checks belong in Agent Factory, never in cron. On a machine without it, a crontab is the
fallback:

```cron
30 7 * * 0  for c in deploy-sync guards routing harvest project-docs skill-usage; do python3 ~/.claude/scripts/box-checks.py $c; done > ~/.claude/box-checks.last 2>&1
17 * * * *  cd ~/.claude && python3 scripts/fleet-facts.py && git commit -qm "fleet facts" -- FLEET.md fleet.json 2>/dev/null
```

If you take this route, change the "Recurring checks" rule in `~/.claude/RULES.md` to match.
