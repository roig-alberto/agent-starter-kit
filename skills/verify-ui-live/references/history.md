# verify-ui-live - history

## The tooling switch (2026-09-08)

> **Tooling note (2026-09-08): the former Playwright MCP was removed** (from `~/.claude.json`)
> and replaced by the **`chrome-devtools-axi` CLI** to cut per-session context (step 0b). Wherever
> this skill still says "Playwright MCP", `browser_*`, `set_input_files`, or `browser_run_code_unsafe`,
> read the axi equivalent (`eval`, `upload`, `screenshot`; browser-context JS only, same as before) - 
> most ENVIRONMENT gotchas (self-signed certs, Next-16 origins, safe-area) carry over - but NOT
> `file://` (axi navigates to it; the MCP blocked it). Auth-login + screenshot are now VERIFIED on
> Loop (step 0b); other axi flags are verify-on-first-use. **Revert recipe: step 0b.** `ui-check` and
> repo `e2e/*.e2e.py` use Playwright the *library*, were never the MCP, and are unaffected.
