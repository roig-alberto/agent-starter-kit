# Chrome-extension verification flow (LEGACY - not used in the current workflow)

Archived 2026-07-06. The box is driven over SSH / Claude Code Remote Control; no
desktop Chrome exists in the workflow, so the Claude-in-Chrome extension route is
unreachable. Primary path is `ui-check` (headless Playwright - see SKILL.md step 0).
Kept in case the workflow ever includes a linked desktop Chrome again.

## The flow

Load the Chrome MCP tools in one bulk call:

```
ToolSearch query: "select:mcp__claude-in-chrome__list_connected_browsers,mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__read_page"
```

Then `list_connected_browsers` (confirm one connected) → `navigate` (the user's
browser holds a valid session cookie, so auth-gated pages load) → `javascript_tool`
to measure. If ToolSearch finds no `mcp__claude-in-chrome__*` tools, the extension
isn't connected - it requires desktop Chrome RUNNING with the extension linked
(claude.ai/chrome).

## What it uniquely offered

- Measuring against the user's LOGGED-IN browser session (no app password handled).
- Co-debugging exactly what the user sees on THEIR screen (their cookies, zoom,
  extensions).

## The parked-tab upload trick (superseded by Playwright `set_input_files()`)

The extension's JS tool ran in an isolated world and could NOT attach files
(`file_upload` rejected repo/scratchpad paths; synthetic `change` events didn't
trigger React's `onChange`). Workaround: the USER picked the file once in their
connected browser and left the wizard PARKED on the target step; client-side wizards
keep parsed rows + step state in React state on that tab, so `javascript_tool` +
`screenshot` could then measure/iterate against that same tabId - and hot-reload
edits applied live to the parked state (measure → edit → re-measure without
re-uploading). **The one hard rule: never navigate/reload that tab** - a reload wipes
the in-memory upload (a stray navigation to `/investments` mid-session proved it,
2026-07-03, Caudal the broker wizard).

Extension-specific gotcha: full `screenshot` calls frequently errored
("renderer may be frozen") right after saving an edit - the HMR/RSC update in
flight, not a failure; read the DOM instead and screenshot once settled.
