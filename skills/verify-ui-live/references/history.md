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

## 2026-10-27: native Ubuntu and Tailscale only

The host moved off WSL2 to native Ubuntu, and Cloudflare was removed (user: "everything in Tailscale"). The
pipeline used to rest on "one container serves two audiences": the Cloudflare tunnel origin pointed at the dev
container, so localhost was what the user saw. Section B was the dual-hostname pattern (2026-07-06):
`dev-<app>.example.com → web:3000` and `<app>.example.com → web-prod:3000`, both behind Access. Now every app's
tailnet hostname serves `web-prod`, and dev is localhost only.

Kept from the WSL era, for reference. Turbopack did not hot-reload across a `/mnt/c` bind mount:
`WATCHPACK_POLLING` is webpack-only, and Turbopack's watcher got no events across a Windows bind mount, so it
served stale cached modules. Verified on finance-proj (Next 15.5.20): the edit reached the container's file,
Turbopack logged "✓ Compiled", yet served OLD content. The old `/mnt/c` layout also paid slow I/O across the
Windows→Linux boundary and steady CPU from `WATCHPACK_POLLING: "true"` (Aro, 2026-07-03).

"Can't access it" case on finance-proj: `BASE_URL=caudal.example.com` was NXDOMAIN; the real host was
`budget.example.com`. HMR used to be checked through the tunnel (Cloudflare proxied the HMR WebSocket).

## 2026-10-27: headless gesture limits re-measured on the Ubuntu host

The old rule "@dnd-kit cannot be driven in ui-check/plain headless Chromium at all" did not survive a
test. On Shelf dev (@dnd-kit 6.3, distance 6, touch delay 180), Playwright 1.64: a stepped `page.mouse`
drag reordered and persisted in Chromium, Chrome 156 and WebKit, headless and visible (Xvfb); a CDP touch
drag with a 250 ms hold worked; `drag_to` failed in all of them. A clean test page with the same sensors
gave the same results, plus a working swipe row. A visible browser changed only WebGL (Intel Arc instead
of SwiftShader). Likely older cause: drags driven with `drag_to` or a single jump, read as a headless
limit (inferred, not reproduced).


## 2026-10-28: what looks clickable must be clickable

Idea from georgewangyu/georgeskills `frontend-e2e-evaluator-ops` (no license, so the rule is written here in our own
words): controls that look interactive but are inert, and links whose `href` is a label such as `N/A`, slip past
smoke checks that only test that text is visible.
