// OpenCode adapter for ~/.claude/scripts/agent-guard.py (the shared pre-command guard).
// Installed as a link: ~/.config/opencode/plugins/agent-guard.ts -> this file.
// Two plugin shapes, so the guard loads on either OpenCode line:
// - 1.x (measured on 1.19.4, @opencode-ai/plugin PluginModule): a default export { id, server }; server(input)
//   returns hooks, and "tool.execute.before" gets (input: { tool }, output: { args }). 1.19.4 refused the 2.x-only
//   export with "must default export an object with server()", so the guard did not run (2026-11-06).
// - 2.x: a default export { id, setup }; setup registers hooks on ctx.tool and the shell tool is "shell".
//   Shape and throw behaviour taken from open-gsd/gsd-core ADR 5331 (measured on 2.0.27).
// A throw from the before-hook stops the call and shows the reason. A guard that cannot run lets the command
// through, like the other adapters.
import { spawnSync } from "node:child_process"

const GUARD = `${process.env.HOME}/.claude/scripts/agent-guard.py`

function check(command: unknown, cwd: string) {
  if (typeof command !== "string" || !command) return
  const r = spawnSync("python3", [GUARD, "--command", command, "--cwd", cwd], { encoding: "utf8" })
  if (r.status === 2) throw new Error(String(r.stderr).trim() || "agent-guard: blocked")
}

export default {
  id: "agent-guard",
  server: async (input: any) => {
    const cwd = input?.directory ?? process.env.PWD ?? ""
    return {
      "tool.execute.before": async (i: any, o: any) => {
        if (i?.tool !== "bash" && i?.tool !== "shell") return
        check(o?.args?.command, cwd)
      },
    }
  },
  setup: async (ctx: any) => {
    if (typeof ctx?.tool?.hook !== "function") return
    const cwd = ctx.location?.directory ?? ctx.directory ?? process.env.PWD ?? ""
    await ctx.tool.hook("execute.before", async (e: any) => {
      if (e?.tool !== "shell" && e?.tool !== "bash") return
      check(e?.input?.command, cwd)
    })
  },
}
