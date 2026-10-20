// OpenCode 2.x adapter for ~/.claude/scripts/agent-guard.py (the shared pre-command guard).
// Installed as a link: ~/.config/opencode/plugins/agent-guard.ts -> this file.
// 2.x wants a default export { id, setup }; setup registers hooks on ctx.tool, the shell tool
// is "shell", and a throw from an execute.before hook stops the call and shows the reason.
// Shape and throw behaviour taken from open-gsd/gsd-core ADR 5331 (measured on 2.0.27).
// A guard that cannot run lets the command through, like the other adapters.
import { spawnSync } from "node:child_process"

const GUARD = `${process.env.HOME}/.claude/scripts/agent-guard.py`

export default {
  id: "agent-guard",
  setup: async (ctx: any) => {
    if (typeof ctx?.tool?.hook !== "function") return
    const cwd = ctx.location?.directory ?? ctx.directory ?? process.env.PWD ?? ""
    await ctx.tool.hook("execute.before", async (e: any) => {
      if (e?.tool !== "shell" && e?.tool !== "bash") return
      const command = e?.input?.command
      if (typeof command !== "string" || !command) return
      const r = spawnSync("python3", [GUARD, "--command", command, "--cwd", cwd], { encoding: "utf8" })
      if (r.status === 2) throw new Error(String(r.stderr).trim() || "agent-guard: blocked")
    })
  },
}
