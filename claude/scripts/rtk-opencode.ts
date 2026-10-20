// OpenCode 2.x adapter for rtk (token-saving command rewrites), replacing the 1.x plugin `rtk init --opencode`
// writes: 2.x refuses that shape (a WARN in its log only), so it had stopped filtering anything.
// Installed as a link: ~/.config/opencode/plugins/rtk.ts -> this file. All rewrite logic stays in `rtk rewrite`.
// The safety guard (agent-guard.ts) runs earlier, on tool.execute.before, so it sees the command as the agent wrote it.
import { spawnSync } from "node:child_process"

export default {
  id: "rtk",
  setup: async (ctx: any) => {
    if (typeof ctx?.shell?.hook !== "function") return
    if (spawnSync("rtk", ["--version"]).status !== 0) return
    await ctx.shell.hook("create.before", async (e: any) => {
      if (typeof e?.command !== "string" || !e.command) return
      const r = spawnSync("rtk", ["rewrite", e.command], { encoding: "utf8" })
      const out = String(r.stdout ?? "").trim()
      if (out && out !== e.command) e.command = out
    })
  },
}
