# `ui-check` in depth (step 0)

The box is a headless server; verification must not depend on a desktop browser.
`ui-check` (deployed `/usr/local/bin/ui-check`; source `dev-system/scripts/ui-check`;
Playwright + headless Chromium) renders the real page at phone width and prints ONE
line - ~30 tokens per check instead of a browser-tool conversation:

```bash
ui-check http://localhost:8080 --expect-title Armario --selector "#root"
# OK http=200 title='Mi Armario' overflow=0 sel[#root]=1x(390x844) color=... bg=...
# auth: pass NO password - ui-check auto-reads ~/.config/ui-check/<host:port>.pw
ui-check http://localhost:3007/today --login http://localhost:3007/api/auth/login \
  --selector ".hero-ring" --js "getComputedStyle(document.body).backgroundColor"
ui-check <url> --shot /tmp/x.png     # screenshot only when a human/gut-check needs it
# page holds an open SSE/WebSocket (live feed, agent stream)? default networkidle never settles:
# "ERROR load: Page.goto: Timeout 30000ms exceeded" -> add --wait load (waits load + 1 s)
ui-check <url> --wait load --shot /tmp/x.png
```

Checks built in: HTTP status, title substring, horizontal overflow at --width
(default 390), per-selector existence/size/color/bg, arbitrary --js (JSON out),
--cookie/--login for auth. **Exit 0/1/2/3 = pass / check-failed / usage-error /
load-error**, and every error prints to STDOUT (updated 2026-09-02 - usage errors
used to go to stderr and share exit 2 with load errors, so a mistyped flag read as
"the app is down"; see `references/gotchas-and-perf.md`). `--js` and long titles
truncate with a `(truncated, N chars)` marker and a `--full` escape hatch. Verified
live 2026-07-06 (closet, positive + negative + unreachable paths); exit/truncation
contract re-verified 2026-09-02.

**Console and requests (`--console`, 2026-10-17):** also listens to the browser and prints a second line,
`CONSOLE {"errors": [...], "warnings": [...]}`. Errors: uncaught page errors and failed page loads, fetch or XHR calls to
the page's own origin (4xx/5xx or no answer; `/favicon.ico` ignored). Warnings: console.error lines and other failed
requests. It reports them and does not fail the check; the caller decides (Agent Factory fails a screenshot on an error).

**Auth: never ask the user for the password.** `--login <url>` (password omitted)
auto-reads `~/.config/ui-check/<host:port>.pw`. One file per app, named by its host and port
(for example `localhost:3000.pw`).
Files present and the Aro login verified 2026-10-16 (`--login` landed on `/today`); Caudal and
closet dev logins are unverified since 2026-07-07: their files exist (2026-10-19) but the dev stacks were down. Backed up in the NAS secrets bundle
(`secrets-backup.sh` → `ui-check-secrets.tgz`), restored per REBUILD.md. Missing file
→ the command prints the exact `printf ... > ...pw` line; relay THAT to the user, don't
get stuck or fall back to asking. Per-app login endpoints in ENVIRONMENT.md. Do NOT
forge a cookie from `SESSION_SECRET` - the classifier blocks it; the login path is intended.

**A multi-route `--login` SWEEP trips the login rate limit - and it reads as the ROUTES being
broken.** `--login` re-authenticates on every invocation, so checking 8 routes = 8 logins; Loop's
login endpoint caps at **5 attempts/minute**, so routes 6+ come back 429 and the failures look like
those pages are down. **Grab ONE cookie once and reuse it across the sweep with `--cookie`** (login
on the first route, pass the cookie to the rest). (loop 2026-09-05: 3 routes mis-diagnosed as broken
before spotting the 429.)

**`--login` CANNOT authenticate a PROD container by IP** (`http://172.20.0.x:3000`) and
fails SILENTLY - the session cookie is `Secure`, and Chrome stores those only on a secure
origin (`localhost` qualifies, a bare IP over http does not). You get a rendered page
showing the LOGIN screen, which reads as "the app is fine". This is the normal case on
this fleet because prod is tunnel-only. Recipe + curl workaround in
`references/gotchas-and-perf.md`.

**In a browser-context eval (`chrome-devtools-axi eval`, like the old Playwright MCP) that trick is
unavailable: page JS has NO Node filesystem** - `require` is undefined and `await import('node:fs')` throws
`ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING`, so the code cannot read the `.pw` file itself.
Winner: log in with curl on the host (the password stays in a shell var, never in the
transcript), then inject the session cookie:

```bash
PW=$(cat ~/.config/ui-check/<host:port>.pw)
curl -si -X POST http://localhost:3008/api/login -H 'content-type: application/json' \
  -d "{\"password\":\"$PW\"}" | grep -i '^set-cookie'
# then, in the MCP: page.context().addCookies([{name,value,domain:'localhost',path:'/'}])
```

Two sub-gotchas: the `.pw` file is keyed by the EXACT host string, so `localhost:3008`
works while `127.0.0.1:3008` fails (or vice versa); and the login route differs per app
(recall is `/api/login`, NOT the `/api/auth/login` some fleet notes assume) - grep the
app's `app/api` instead of guessing. (recall 2026-07-21, ~5 min of failed auth attempts.)

**`--js` mechanics (two retry-costing traps, full detail in `references/gotchas-and-perf.md`):**
(1) a bare top-level `await` throws - wrap in `(async()=>{ … ; return JSON.stringify(x); })()`
and RETURN the promise (needed to wait for a Vaul/drawer animation); (2) the positional
`url` must come BEFORE the greedy `--login`, or it's swallowed. Also: `innerText` applies
CSS `text-transform`, so an `uppercase`-styled label fails `includes('Target')` (it's
`TARGET`) - assert on `textContent`.
