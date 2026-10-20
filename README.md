# Agent starter kit

A cleaned copy of a working coding-agent setup: the always-on rules and skill router, the skills, the hooks, the safety guards, the
knowledge linter and the recurring checks. Personal facts, memories and session history are left out. Machine facts
became `<placeholders>` to fill in.

## What is here

| Path | Installs to | Holds |
|---|---|---|
| `claude/RULES.md` | `~/.claude/` | The rules every session loads: verify before claiming, scope, reply style, git and secrets, and the **scenario router** that picks a skill per task. |
| `claude/CLAUDE.md`, `INSTRUCTIONS.md` | `~/.claude/` | The entry file for Claude Code, and the same text for Codex and OpenCode. Both import RTK, RULES and ENVIRONMENT. |
| `claude/ENVIRONMENT.md` | `~/.claude/` | **Template.** Your machine's paths, accounts and tools. |
| `claude/RTK.md`, `HISTORY.md`, `PROMPT-GUIDE.md`, `MODEL-MIGRATION.md` | `~/.claude/` | The rtk command-proxy rules, the evidence behind the rules, and two guides for the human. |
| `claude/HARVEST.md` | `~/.claude/` | **Template.** The inbox where lessons wait until `retro` turns them into skill changes. |
| `claude/settings.json` | `~/.claude/` | The hooks (below), the status line, auto mode and the ponytail plugin. |
| `claude/scripts/` | `~/.claude/scripts/` | The hook scripts, guards, linter and box checks (below). |
| `claude/git-hooks/` | `~/.claude/git-hooks/` | Global git hooks: `commit-msg` and `pre-push`. |
| `claude/agents/` | `~/.claude/agents/` | Three small subagents: builder, investigator and reviewer. |
| `bin/` | `~/.local/bin/` | Two own CLIs the skills call: `review-diff` (one-turn diff review) and `ui-check` (headless UI measurement). |
| `skills/` | `~/.agents/skills/` | The skills. Claude reaches them through the link `~/.claude/skills`; Codex reads `~/.agents/skills` natively. |
| `loops/LOOPS.md`, `loops/prompts/` | (read it) | Every recurring check: schedule, what it does, how to run it without Agent Factory; the model checks' prompts. |
| `playbooks/UI-PLAYBOOK.md` | (read it) | Every look and iPhone fix from Agent Factory with its purpose, values and code. The motion half is `skills/animate/references/ui-playbook/`. |
| `playbooks/OUTSIDE-SKILL-REPOS.md` | (read it) | The public skill repos this setup borrows ideas from (pstack is in `cursor/plugins`). |

### Hooks

| When | Script | What it does |
|---|---|---|
| Before every shell command | `rtk hook claude` | Rewrites dev commands through rtk, which filters their output to save tokens. |
| Before every shell command | `scripts/agent-guard.py` | Blocks bare `sudo`, `git add -A` in an app repo, destructive git and `--no-verify`. |
| At every turn end | `scripts/autopush-knowledge.sh` | Runs `knowledge-lint.py`, then commits and pushes the repos in `scripts/autopush-repos.conf`. A failing lint holds the push. |
| Every git commit and push | `git-hooks/commit-msg`, `pre-push` | gitleaks secret scan, no agent trailers, no long dashes, no force push, no weakened test (the floor guard). |

`bash ~/.claude/scripts/guards-test.sh` runs a sample against every guard.

## Prerequisites

The Claude Code CLI, logged in (`claude`; some scripts call `claude -p`), `git`, `python3` with PyYAML (`sudo apt install python3-yaml`), `jq`, the `gh` CLI, Node with npm, and
[uv](https://docs.astral.sh/uv/). Optional: `docker` and `ss` for `fleet-facts.py`; Codex or OpenCode if you use them.

## Tools and plugins

`install.sh` installs only this kit's own files. Install the tools yourself; each line is the command used on the home
box (version in brackets). The npm tools are linked into `~/.local/bin`, which the hooks and skills expect on `PATH`.

| Tool | Needed for | Install |
|---|---|---|
| rtk (0.43.0) | the shell hook in `settings.json`; every command runs through it | `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh \| sh`, then check `rtk gain` works (another tool is also called rtk) |
| gitleaks (8.30.1) | the git hooks block every commit without it | download the release from [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks/releases), check its checksum, `install -m 755 gitleaks ~/.local/bin/` |
| playwright (1.61.0) | `ui-check`, the headless UI checks most UI skills use | `uv tool install playwright && playwright install --with-deps chromium`, then re-run `install.sh` so `ui-check` uses that Python |
| chrome-devtools-axi | multi-step browser flows (`verify-ui-live`) | `npm i -g chrome-devtools-axi && ln -sf "$(npm config get prefix)/bin/chrome-devtools-axi" ~/.local/bin/` |
| graft (0.16.0) | the router's "how does this code work" row | `npm i -g @nanonets/graft && ln -sf "$(npm config get prefix)/bin/graft" ~/.local/bin/`; per repo `graft build`, never `graft init` |
| ccusage | line 2 of the status line (cost and burn rate) | `npm i -g ccusage` |
| markitdown (0.1.7) | reading PDF, docx, xlsx or pptx files | `uv tool install markitdown` |
| review-diff, ui-check | the `review` skill and the UI verification skills | shipped in `bin/`; `install.sh` copies them to `~/.local/bin` |

| tg-alert (optional) | phone alerts from the turn-end hook when a push is held | not shipped: a Telegram script in the home box's infra repo. Without it the hook only logs to `~/.claude/skills-autopush.log` |

Two skills come from Anthropic, not from this kit: `skill-creator` (used by `knowledge-authoring`) and `deep-research`
(used by `research-decision`). They appear in Claude when the account has them; without them, those steps are skipped.

| Plugin | What it does | Install |
|---|---|---|
| ponytail | "lazy senior dev" mode: the smallest change that works | declared in `settings.json`; or `claude plugin marketplace add DietrichGebert/ponytail && claude plugin install ponytail@ponytail` |
| caveman | terse "caveman" replies and the `cavecrew` skills | `claude plugin marketplace add JuliusBrussee/caveman && claude plugin install caveman@caveman` (the three cavecrew subagents are already in `claude/agents/`) |

## Install

```sh
gh repo clone <github-user>/agent-starter-kit && cd agent-starter-kit
bash install.sh            # never overwrites your files; it lists the ones it kept. --force overwrites
```

It also sets `git config --global core.hooksPath ~/.claude/git-hooks` when no hooks path is set, and copies `config/` into
`~/.config` (the rtk config).

## After install

1. Fill in `~/.claude/ENVIRONMENT.md`. RULES.md tells the agent to read facts there instead of guessing them.
2. Put both folders in their own **private** repos, so the turn-end hook can push them:
   ```sh
   cd ~/.claude && git init -q && git add -A && git commit -qm "agent config" && gh repo create <config-repo> --private --source=. --push
   cd ~/.agents/skills && git init -q && git add -A && git commit -qm "skills" && gh repo create <skills-repo> --private --source=. --push
   ```
   The `.gitignore` in `~/.claude` is an allowlist: only config, rules, scripts and memories are tracked, never
   transcripts or credentials.
3. Check the wiring: `bash ~/.claude/scripts/guards-test.sh` ends with "all passed", and
   `python3 ~/.claude/scripts/knowledge-lint.py` reports 0 errors. Two routing warnings are expected until you
   re-score the router (`loops/LOOPS.md`, check `routing`).
4. Codex: `ln -sf ~/.claude/INSTRUCTIONS.md ~/.codex/AGENTS.md`. OpenCode: `python3 ~/.claude/scripts/build-opencode-agents.py`
   builds its AGENTS.md, and `ln -sf ~/.claude/scripts/agent-guard-opencode.ts ~/.config/opencode/plugins/agent-guard.ts`
   adds the guard.
5. Set up the recurring checks from `loops/LOOPS.md`.

## Adapting it

- **`skills/fleet-ops/` is a template**: the shape and the general rules of the original box's ports, tunnels, RAM
  and disk skill, with every machine fact as a `<placeholder>` and an "Example:" of what the original wrote there.
  Fill it in for your box, or delete it.
- The rules and a few skills (`portability`, `new-app`) still describe a self-hosted Docker box with a NAS,
  Cloudflare tunnels, Tailscale and Telegram alerts. Keep the patterns and replace the specifics, or delete what you
  do not run. A pointer marked "(not in this kit)" names a skill that stayed on the original box.
- When you add, rename or drop a skill, update the router table at the end of `RULES.md`. `knowledge-lint.py`
  fails while the router names a skill that does not exist, or a skill that the router never names.
- Left out on purpose, because this repo is public: the original box's infrastructure skills (`security`,
  `backups-and-alerts`, and the real `fleet-ops`: they map its security model, vault, backups and exposed services),
  two skills tied to one house and one phone console (`home-assistant-fleet`, `claude-spawner`), memories, the
  HARVEST inbox, FLEET.md, session transcripts, the four liked-UI mockup images (`frontend-design` keeps their written
  description), five reviewer-eval cases that describe security bypasses, and the infra repo (rebuild runbook, backup
  scripts, systemd units).

## Refreshing the kit (home box only)

`python3 export.py` rebuilds `claude/`, `skills/`, `bin/`, `playbooks/` and `loops/prompts/` from the live setup and Agent Factory. It reads the personal-value map from
`~/.config/agent-starter-kit/redact.tsv`, which stays outside this repo. It refuses to finish while any mapped value,
a private IP address or a gitleaks finding is left in the output. On the home box, Agent Factory's weekly "Starter kit sync" loop runs it and pushes once a model review of the diff finds no personal data and no security weak spot of the box (`loops/LOOPS.md`). Hand-written files live in `templates/` and
`templates-skills/` and overlay the export.
