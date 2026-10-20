# The axi harness

## Where it lives

`~/projects/axi` (a shallow clone of `kunchenguid/axi`, ~144M). Two harnesses:

- `bench-github/`: 17 read-only tasks against the public `openclaw/openclaw`. No browser, no daemon,
  cheapest. **Start here** when proving the pipeline works.
- `bench-browser/`: 14 browsing tasks; needs Chrome and a daemon lifecycle.

Re-clone: `gh repo clone kunchenguid/axi ~/projects/axi -- --depth 1`

## Setup (verified 2026-09-05)

The repo is a pnpm workspace, but **the bench dirs have no workspace-internal deps**, so plain npm works
and pnpm need not be installed:

```bash
cd ~/projects/axi/bench-github && npm install
npm run bench            # prints the command reference
```

Some conditions need their tool on PATH (`axi` needs `gh-axi`). **npm's global bin is NOT on PATH on this
box**: `npm i -g gh-axi` reports success and leaves nothing runnable. Symlink it:

```bash
npm i -g gh-axi
ln -sf "$(npm config get prefix)/bin/gh-axi" ~/.local/bin/gh-axi   # ~/.local/bin IS on PATH
```

## Running it

```bash
cd ~/projects/axi/bench-github
npm run bench -- matrix --condition cli,axi --task pr_then_checks \
                 --repeat 3 --agent claude --model claude-sonnet-5
npm run bench -- report
```

**`--agent claude` is mandatory. The default is `codex`.** Without it every run returns
`FAIL | 0 turns | $0.0000` in ~2s, and the artifact says *"The 'claude-sonnet-5' model is not supported
when using Codex with a ChatGPT account."* A 0-turn FAIL is this, not your tool.

Reads: `results/report.md`, `results/results.jsonl`, and per run
`results/<condition>/<task>/run<N>/{agent_output.txt,judge_output.txt,grade.json}`. **Read
`agent_output.txt` on any failure before believing the summary table.**

Correctness is LLM-judged (the judge runs on codex/`gpt-5.4-mini`, so codex auth must work even for a
claude run). A cheap arm that is WRONG is caught, not scored as a win.

## Adding a condition or a task

Both are declarative YAML, with no code:

- `config/conditions.yaml`: one arm, with `name`, `tool`, `agents_md` (instructions injected as
  CLAUDE.md), an optional `mcp_config`, an optional `command_policy`, and an optional daemon lifecycle
  (`daemon: none` is valid, so a non-browser tool needs no daemon).
- `config/tasks.yaml`: `id` + `prompt` + grading criteria.

Copy the nearest existing arm and edit it. Keep tasks READ-ONLY: the bundled 17 all are, and a benchmark
that files issues on someone's repo is an outward-facing write.

## Arm isolation is already handled; do not re-solve it

`runner.ts` spawns `claude --setting-sources ''`, so **your `~/.claude` settings do not apply inside a
run**: no rtk rewrite, no caveman prompt, no RULES.md. A `gh` baseline is genuinely raw `gh`, comparable
to the published tables.

Consequence: to benchmark something that lives IN those settings (caveman, a RULES.md rule), inject it
through the condition's `agents_md`, not by relying on the ambient config.
