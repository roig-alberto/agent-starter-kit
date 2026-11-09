---
name: verify-ui-live
description: >-
  Verify a UI change by measuring the real DOM in a headless browser against the running dev container, and
  report each check as Pass, Fail or Unverified. Use when you make a visual, layout, styling, or component
  change and want to confirm it instead of guessing: "does it look right?", "is it live?", "check the UI",
  "Check the deployed against the wireframes", wanting to see a change on the phone, setting the pipeline up
  in a fresh project, or when a headless check can't drive or see the thing: "the click does nothing / the
  drag won't fire", a swipe-row or @dnd-kit gesture, a toast or Undo that "isn't there", a screenshot showing
  only the boot splash, an Agent Factory task worktree (section 0d). NOT for an app that has its own
  verify skill (use it) or for unit tests (use testing).
---

# Verify UI changes live

If the repo has a project skill `.claude/skills/verify-<app>/` (launch, doctor, drive, evidence,
cleanup, feature map), use it first; this skill is the generic fallback and the recipe for building one.

This skill confirms a UI change by measuring the real DOM in a headless browser on the box, instead of
eyeballing or guessing. The dev container hot-reloads on localhost, and the app's tailnet hostname serves
the prod container, so a dev measurement shows what the phone will see after the next prod rebuild. It prevents "looks fine"
claims that a computed style, an overflow check, or a phone-width render would have disproved. Live
ports, hostnames, and container names are in `~/.claude/FLEET.md`.

## Steps

0. **Measure with `ui-check` first.** It is headless Playwright plus Chromium, renders at phone width
   (390 by default), and prints one line, about 30 tokens per check:
   `ui-check <url> --selector "<sel>" --js "<expr>"`, `--login <login-url>` for auth, `--wait load` for a
   page with an open SSE or WebSocket, `--shot <png>` only when a human gut-check needs an image. Exit
   codes 0/1/2/3 mean pass, check-failed, usage-error, load-error. Details: `references/ui-check.md`.
0b. **Drive multi-step flows (login, upload, wizard, commit) with `chrome-devtools-axi` or a committed
   `e2e/*.e2e.py`.** axi is a Bash CLI: `start`, `open <url>`, `snapshot`, `click @<uid>`,
   `fill @<uid> <text>`, `upload @<uid> <path>`, `eval <js>`, `screenshot <path>`, `stop`. The e2e script
   runs on `$HOME/.local/share/uv/tools/playwright/bin/python`. Recipes and the Playwright MCP revert
   block: `references/multi-step-flows.md`.
0c. **Drive gestures with real stepped input and poll transient UI inside one async eval.** Playwright's
   `drag_to` jumps the pointer in one move, so @dnd-kit never activates; a `page.mouse` drag in small steps
   works headless in Chromium, Chrome and WebKit (measured on Shelf 2026-10-27). Inside `ui-check --js`
   there is no mouse, so dispatch `PointerEvent`s there. A screenshot of a toast lands mid-slide or after
   auto-dismiss (`references/multi-step-flows.md` 0c, `references/measurement-snippets.md`).
0d. **In an Agent Factory task worktree, run your own dev server.** Start `npm run dev -- --port $PORT --webpack`
   on a free port, `ui-check` it, Read the PNG, and kill the server. Name real paths on the closing
   `SCREENS: /books, /books/1` line, because the factory's Verify step photographs them and fails if one
   does not render (`references/multi-step-flows.md`).
1. **Measure, do not eyeball, at 360 to 390 px.** Use `getComputedStyle` and `scrollWidth` versus
   `clientWidth`; a screenshot cannot confirm a hex value or a 1px overflow. Snippets:
   `references/measurement-snippets.md`.
1b. **Building to a wireframe: read the wireframe SOURCE and compare computed values.** A divergence is a
   defect to fix, not a judgment call; screenshot only at the start, after big changes, and at sign-off.
1c. **Before calling a design implemented, run a side-by-side fidelity pass.** Open the frames with
   `chrome-devtools-axi open file:///<abs>/<frames>.html`, shoot one frame and the live screen at the same
   width, and compare state by state. Frames often live in the inbox folder (ENVIRONMENT.md), so look there first
   (`references/design-fidelity.md`).
2. **For "does the route render", an HTTP smoke check with a login cookie is enough** (curl, no browser).
2b. **After every driven flow, read the console and the network.** Run `chrome-devtools-axi console` and
   `chrome-devtools-axi network`; a console error or a failed request (4xx, 5xx, blocked) during the flow is a
   Fail even when the screen looks right. `ui-check` cannot see either, so a flow checked only with it leaves
   them Unverified.
3. **Report every check, failures first** (from owainlewis/blueprint `test`, MIT): one block per check, each
   `Check:` (the acceptance check or its ID), `Result: Pass / Fail / Unverified`, `Evidence:` (the command and
   its decisive output, or the screenshot path), `Gap:` (what remains unknown, or None). Never "looks fine"
   and never a check reworded to match what the code does.
   Done when: every check the change promised has a block, and Fail and Unverified ones come first.
4. **Tell the user where it is live, and SHOW it when asked.** A dev edit is live on localhost only; the
   phone sees it after a prod rebuild (a milestone action, so ask first), which you then check on the
   tailnet hostname from `~/.claude/FLEET.md`. To show it, capture with `ui-check --shot <file>.png` and `SendUserFile` the PNG, because a
   PNG you only `Read` reaches your context, not the user's.

Setting the pipeline up in a new project (a hot-reload dev container with `./:/app` plus anonymous
`/app/node_modules` and `/app/.next` volumes, and `ui-check`) is in
`references/pipeline-setup.md`, as is what needs action before a change is live (schema, new dependency).

## Rules

- **Measure the dev container on localhost while building, and the prod container through its tailnet
  hostname after a rebuild; never start a second dev server.** The tailnet hostname serves `web-prod`, so
  a dev pass alone does not prove what the phone shows today. The box is on the tailnet and reaches it.
- **Never ask the user for the app password.** `--login <url>` with the password omitted reads
  `~/.config/ui-check/<host:port>.pw`; if it is missing, relay the `printf ... > ...pw` line the command
  prints. Do NOT forge a cookie from `SESSION_SECRET`.
- **On a multi-route sweep, log in once and reuse the cookie with `--cookie`.** `--login` re-authenticates
  per call, and a 5-per-minute login limit turns routes 6 and later into 429s that look like broken pages.
- **Write and commit paths run against an ISOLATED test DB, never the real one.** Dev and prod share one
  database; point the browser flow at the throwaway app on `:3099` from `testing`.
- **One state-changing click per eval call; re-measure `{disabled}` between steps.** React has not
  re-rendered inside the same call, so the enabled action is still stale and the click silently no-ops.
- **In a dual-shell app, filter to the VISIBLE match.** Use
  `[...document.querySelectorAll('SEL')].filter(e => e.getBoundingClientRect().width > 0)`, because a bare
  `querySelector` returns the hidden desktop instance at `rect [0,0]`.
- **Check that what looks clickable is clickable.** A chip, card, row or icon styled like a button must be a
  `button`, a link or a form control, or lose the button look; every `href` must be a URL or a route, never a label
  (`[...document.querySelectorAll('a[href]')].filter(a => !/^(https?:|\/|#|mailto:)/.test(a.getAttribute('href')))`
  lists the bad ones). Each one found becomes a regression check.
- **Prefer measurements to images.** A screenshot costs about 1-2k tokens to view.
- **You CAN screenshot; never tell the user you cannot.** Both `ui-check --shot` and
  `chrome-devtools-axi screenshot <path>` render on the box.
- **A green headless check is NOT proof against a phone-reported bug.** Headless reports
  `env(safe-area-inset-*)` = 0 and WebKit-only paint bugs measure identically before and after the fix;
  verify what headless can prove, then ask for a device re-test.

## Gotchas

- **`ERROR load: Page.goto: Timeout 30000ms exceeded` on a live-feed page.** networkidle never settles;
  add `--wait load`.
- **`--js` throws on a top-level `await`, or the URL is ignored.** Wrap it in
  `(async()=>{ … ; return JSON.stringify(x); })()` and put the positional `url` BEFORE the greedy `--login`.
- **A text assertion fails on an uppercase label.** `innerText` applies `text-transform`; assert on
  `textContent`.
- **`--login` against a prod container by IP shows the login screen.** The cookie is `Secure`; use the
  tailnet HTTPS hostname or the curl workaround in `references/gotchas-and-perf.md`.
- **Browser-context eval cannot read the `.pw` file (`ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`).** Log in
  with curl on the host and inject the cookie; the `.pw` file is keyed by the EXACT host string, and the
  login route differs per app, so grep the app's `app/api`.
- **axi rejects a ref with `STALE_REF … generation N, current N+1`.** A `fill` re-rendered the form;
  re-snapshot after any DOM-changing action.
- **`ui-check` click "works" but nothing is saved.** It tears down before an async server-action POST
  lands; drive write paths with axi or an e2e script.
- **SSR looks perfect but nothing is interactive, with a `ws://…/_next/webpack-hmr` handshake error.** The
  origin is missing from `allowedDevOrigins`; list `localhost` AND `127.0.0.1`.
- **A page 500s with `require is not defined` or a stale "Can't resolve" after many edits.** Turbopack
  cached a failed resolution; `docker compose restart web` before debugging code.
- **Screenshots show only the boot splash.** Wait with `page.wait_for_selector("#splash", state="detached")`.
- **`ERR_CERT_AUTHORITY_INVALID` on a self-signed dev origin.** Launch with
  `--ignore-certificate-errors` and `ignore_https_errors=True`.
- **A design frame id like `#11-6a2` throws as a selector.** Use `[id="11-6a2"]`.
- **"Can't access it".** Check the hostname against FLEET.md and `BASE_URL` first (NXDOMAIN looks like a
  down app), then `tailscale serve status` inside the app's sidecar for the serve target.
- **`ui-check: command not found` or no Chromium on a rebuilt host.** Install the browser tools with the
  steps in dev-system `REBUILD.md`; never hand-roll a different install.
- **"Changes aren't deploying".** A caching service worker; keep it no-cache in dev, and re-add an
  installed PWA once after the fix.
- **A Next build-error overlay answers `http=200`.** Look at the PNG, not only the status.

## References

- `references/ui-check.md`: step 0 in full, with auth, the rate-limit sweep, and `--js` mechanics.
- `references/multi-step-flows.md`: steps 0b to 0d, axi login recipe, MCP revert block, gestures, worktrees.
- `references/design-fidelity.md`: steps 1 to 3, wireframe matching, the fidelity pass, smoke check, showing the user.
- `references/measurement-snippets.md`: ready-to-paste JS for overflow, styles, gestures, transient UI.
- `references/gotchas-and-perf.md`: every gotcha in full, dev-server performance, the iOS headless limits.
- `references/pipeline-setup.md`: building the pipeline in a new project, and dev server versus prod build.
- `references/chrome-extension-legacy.md`: the archived Chrome-extension flow; not used in this workflow.
- `references/history.md`: the 2026-09-08 switch from the Playwright MCP to axi.
