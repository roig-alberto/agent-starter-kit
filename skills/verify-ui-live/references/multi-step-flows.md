# Multi-step flows, gestures, write paths, worktrees (steps 0b, 0c, 0d)

## 0b. Multi-step flows - chrome-devtools-axi + committed e2e (uploads, click-throughs, commit)

`ui-check` is one-shot, single-page. For a flow with STEPS (login → upload a file →
click through a wizard → commit) use one of two, both headless on the box:

- **`chrome-devtools-axi`** - agent-driven, interactive, a **Bash CLI** (no MCP schema in
  context; screenshots go to a FILE you `Read` on demand). **Replaced the Playwright MCP
  2026-09-08** to cut per-session context: ~half the input tokens, cost a wash - the win is
  context/quota room, not money (evidence: `agent-tool-bench` `references/plugin-verdicts.md`).
  Installed `npm i -g chrome-devtools-axi` + symlinked to `~/.local/bin` (REBUILD manifest).
  Drive it: `chrome-devtools-axi start` → `open <url>` → `snapshot` (returns `@<uid>`s) →
  `click @<uid>` / `fill @<uid> <text>` / `type` / `press` / `upload @<uid> <path>` / `dialog` /
  `eval <js>` / `screenshot <path>` → `stop`. Reuses `/usr/bin/google-chrome`;
  `CHROME_DEVTOOLS_AXI_MCP_PATH` skips the ~30s npx bootstrap. **VERIFIED on the real Loop app
  2026-09-08:** start/open/snapshot/screenshot, AND the full auth-cookie login + an authenticated
  screenshot. Proven login recipe (Loop dev, single-password form):
  `open http://127.0.0.1:3015/login` → `snapshot` (find the "Contraseña" textbox uid) →
  `fill @<uid> "$(cat ~/.config/ui-check/<host:port>.pw)"` → **RE-SNAPSHOT** → `click @<fresh
  Entrar uid>` → redirects to `/`. **GOTCHA (cost one STALE_REF here): a `fill` re-renders the
  form and BUMPS axi's snapshot generation, so refs from before the fill are rejected
  (`STALE_REF … generation N, current N+1`). Re-snapshot after ANY DOM-changing action before the
  next `@uid`.** Redact the pw from output (`| sed "s/$PW/***/g"`), never echo it. Still
  UNPROVEN: self-signed dev certs (`CHROME_DEVTOOLS_AXI_CHROME_ARGS="--ignore-certificate-errors"`,
  Loop dev is http so untested). NOTE: `file://` is NOT blocked in axi (it launches its own
  Chrome; `open file:///…` navigates) - unlike the old Playwright MCP, so the "serve frames over
  HTTP" workaround is a choice, not a hard requirement.

  **Reverting to the Playwright MCP.** Re-add this block to `~/.claude.json` → `mcpServers`
  (then restart the session) and switch the recipes above back to its `browser_*` tools:
  ```json
  "playwright": { "type": "stdio", "command": "npx",
    "args": ["-y","@playwright/mcp@latest","--headless","--isolated","--ignore-https-errors"],
    "env": {} }
  ```
  `ui-check` (DOM measurement) and repo `e2e/*.e2e.py` (Playwright library) were never the MCP and
  are unaffected either way.
- **Committed Python e2e** - durable regression. A `e2e/*.e2e.py` run via ui-check's own
  Playwright runtime (`$HOME/.local/share/uv/tools/playwright/bin/python`). Login with
  `ctx.request.post(<login-url>, data={"password": <pw>})` reusing the `.pw` file (later API calls from `ctx.request`
  miss a `Secure` cookie on http://127.0.0.1: call them through `page.evaluate(fetch)`, see gotchas-and-perf.md); `set_input_files`
  for uploads; role/text locators for clicks (use `exact=True` - a substring name matches plurals).
  Lives in the repo, local-only (vitest is scoped to `lib/**`, so it won't run in `npm test`).
  Precedent: `finance-proj/e2e/traspaso-pairing.e2e.py` (2026-07-10) - upload→tag→link→unlink.

## 0c. Gestures and transient UI - the two things a naive check silently misses

- **Gestures (swipe rows, @dnd-kit, long-press): `browser_click` and `dragTo` NO-OP.** Dispatch
  synthetic `PointerEvent`s, and **match the dispatch target to where the gesture listens** - the
  ELEMENT for React `onPointerMove` props, **`document`** for @dnd-kit's post-pointerdown global
  listeners. Getting this backwards is a silent zero-movement failure (both directions cost a cycle:
  Aro 2026-07-13/14). **@dnd-kit cannot be driven in `ui-check`/plain headless Chromium at all** - use
  `chrome-devtools-axi` (`drag @<from> @<to>`, real Chrome input), or verify by render + persist-action + mirroring a proven impl.
- **Transient UI (toast, 5s optimistic Undo): a screenshot LIES** - it lands mid-slide-in
  (`opacity:0.02`, off-viewport `y`) or after auto-dismiss. Poll `getBoundingClientRect().y` +
  `getComputedStyle().opacity` inside ONE async `browser_evaluate` until settled; do the whole
  drive→wait→click-Undo in that single call, never across tool calls (the toast dies in the latency).
- **But a click and the action it ENABLES cannot share one `browser_evaluate`** - React hasn't
  re-rendered, so the CTA is still `disabled`/stale at click time and the click silently no-ops,
  looking exactly like a broken feature (closet 2026-07-20: nearly debugged a correct persistence
  path). One state-changing click per call; re-measure `{disabled}` between steps.

Full ready-to-paste recipes (thresholds, event fields, timings): `references/measurement-snippets.md`.

**Write/commit paths → an ISOLATED test DB, never the real one** (dev+prod share one
`db-1`, so a commit writes the rows the user sees). Full isolate-drive-drop recipe lives in
`testing` (stack-agnostic). Here, just point the browser flow (`chrome-devtools-axi` or the
`e2e/*.e2e.py`) at the throwaway app on `:3099`; Next makes an env `DATABASE_URL` win over `.env`.
Caudal 2026-07-10: proved the browser commit persists a shared `traspaso_pair_id`, real DB untouched.

## 0d. In an Agent Factory task worktree (no dev container, no tunnel) - verified 2026-10-13

An agent working a task from Agent Factory (`~/projects/agent-factory`) sits in a git worktree under
`~/.local/share/agent-factory*/worktrees/`, not in the app's checkout: the app's dev container does not see it.
To look at your own screen change there:

```sh
PORT=3039   # any free port; the factory uses 3030-3039 for its own previews, check `ss -ltn | grep :$PORT` first
npm run dev -- --port $PORT --webpack > /tmp/dev-$PORT.log 2>&1 &   # Next: --webpack (turbopack failed in a worktree)
until curl -s -o /dev/null http://127.0.0.1:$PORT/; do sleep 1; done
ui-check http://127.0.0.1:$PORT/books --wait load --width 390 --height 844 --shot /tmp/books.png   # then Read the PNG
kill %1   # stop your dev server
```

- Behind a login: `--login http://127.0.0.1:$PORT/api/auth/login` with `UI_CHECK_PW` set (ask, never guess it).
- The factory's **Verify step photographs the pages you name** on your closing line `SCREENS: /books, /books/1`
  (compulsory when your diff touches .tsx/.jsx/.css/.html...), and **fails Verify if a page does not render**
  (ui-check error or HTTP 4xx/5xx). So name real paths, and check the risky one yourself first.
- A Next build-error overlay can still answer `http=200` in dev: look at the PNG, not only the status.
