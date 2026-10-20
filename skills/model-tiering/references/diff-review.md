# Reviewing a diff with Claude

## Hand it the DIFF, never the repo

Use `review-diff` (a host script in `~/.local/bin`; the source and install note are in dev-system
`host/`):

```bash
review-diff [--base master] [--model sonnet] [--focus "money paths"] [--context FILE]...
```

It collects the diff plus untracked files (skipping generated blobs over 40KB) and calls `claude -p` with
`--tools "" --setting-sources "" --strict-mcp-config --mcp-config '{"mcpServers":{}}'`. Each `--context`
file (the plan or ticket, the repo's `AGENTS.md`, the same file as `CLAUDE.md`) is pasted before the diff.

## Per-turn context floors on this box

Measured with n=2-3, Haiku, and the same prompt:

- **36,938** tokens for a normal session;
- 31,915 with a credentials-only `CLAUDE_CONFIG_DIR` (about 13% less);
- **6,449** with the lean flags above (about 83% less).

An always-on MCP server is the cheapest thing to cut: `ha-mcp` cost **1,115 per turn** in every session
until it was moved to on-demand loading (ENVIRONMENT.md). The four claude.ai connectors cost only **128
per turn** together, so measure before removing something you use.

The finding format, the triage into Act on and Dismissed, and when to use an exploring reviewer instead
live in the `review` skill.

## Which model reviews (measured 2026-10-20)

On 17 real bugs from our repos (judge v2), Sonnet at medium caught 50%, Sonnet at high 53% and Opus at medium 59%;
Opus's lead is about the size of the run-to-run noise, at about 2.3x the cost. `review-diff` therefore defaults to Sonnet at medium. Full record:
`agent-tool-bench/references/plugin-verdicts.md`; rerun the eval (`agent-tool-bench/references/review-eval/`) when a
model alias moves.
