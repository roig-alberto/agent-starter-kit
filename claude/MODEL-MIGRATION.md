# MODEL-MIGRATION.md - switching model or agent tool without losing the system

Written 2026-07-06. Covers: moving to a different Claude model, moving to a different
agent CLI entirely, and fixing the scheduled routine when auth breaks.

## What is portable vs Claude-Code-specific

| Piece | Portable? |
|---|---|
| Project repos + CLAUDE.md/AGENTS.md/FEATURES.md/plans | YES - plain git + markdown; AGENTS.md symlink is the cross-tool entry point |
| `claude-config` + `claude-skills` repos (rules, skills, memory, ENVIRONMENT) | Content YES (markdown); the LOADING is Claude-specific (see below) |
| dev-system (REBUILD, backups, timers) | YES - shell + systemd, agent-independent |
| `@import` in `~/.claude/CLAUDE.md`, skill auto-loading, the router, hooks (rtk rewrite, knowledge auto-push), auto-memory | NO - Claude Code features |
| Agent Factory loops (the quarterly Knowledge audit, the weekly skills review) | YES - the model is saved on each loop, switched in its Loops screen |

## Switching to a DIFFERENT CLAUDE MODEL (trivial)

Everything works unchanged - the whole system was built model-agnostic on purpose.
- Interactive default: `/model` in a session (persists), or `settings.json`.
- The scheduled audit runs on the model saved on Agent Factory's "Knowledge audit" loop (Sonnet) - change it in
  the loop's editor; it deliberately uses a cheap tier (the skill rails carry it).
- Read PROMPT-GUIDE.md Part 2b for which tier fits which task.

## Switching to a DIFFERENT AGENT TOOL (Codex, Gemini CLI, etc.)

Context is NOT lost - it all lives in git. The rewiring checklist:
1. **Projects**: nothing to do - the tool reads `AGENTS.md` (→ CLAUDE.md) per repo:
   Facts, Commands, conventions all there.
2. **Global rules**: the new tool won't read `~/.claude/CLAUDE.md`. Port RULES.md +
   ENVIRONMENT.md into its global-instructions mechanism (Codex: `~/.codex/AGENTS.md`
   or equivalent; check the tool's docs). They are plain markdown - copy, don't rewrite.
3. **Skills**: markdown playbooks - usable by any tool that can read files. Either
   port the RULES.md router into the new tool's instructions ("before task X read
   ~/.agents/skills/<name>/SKILL.md") or use the tool's native skill mechanism if any.
   Auto-triggering is lost; the router text is what replaces it.
4. **Memory**: `claude-config/projects/.../memory/*.md` - feed MEMORY.md + files into
   the new tool's context/instructions. Plain markdown.
5. **Scheduled audit**: pick the new agent's model on Agent Factory's "Knowledge audit" loop (the factory needs
   that agent's harness). The weekly checks are plain code and need nothing.
6. **Hooks** (rtk rewrite, knowledge auto-push): reimplement in the new tool's hook system or drop
   - they're optimizations, not load-bearing.
7. Run a `/skills-audit`-equivalent pass after switching - the audit protocol
   (skills/skills-audit/SKILL.md) is itself just markdown instructions.

## Scheduled audit: an agent login failure

The quarterly Knowledge audit runs in Agent Factory (the skills-audit timer and its 04:45 job were retired
2026-10-19). An auth error from the agent pauses the run as "login needed"; reconnect it in the factory's Settings >
Agents, then Run now on the loop (agent-factory D60, D61). The weekly Box checks use no model and never need a login.

## The actual migration drill (original 2026-07-06; shared path verified 2026-09-06)

```sh
gh repo clone <github-user>/claude-config ~/.claude
gh repo clone <github-user>/claude-skills ~/.agents/skills
ln -s ~/.agents/skills ~/.claude/skills
```
Fresh-clone drill confirmed complete: 8 config files, memory dir, all skills.
Re-verify ENVIRONMENT.md facts on any new host (`/skills-audit`).
