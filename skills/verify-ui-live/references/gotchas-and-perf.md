# verify-ui-live - deep gotchas & dev-server performance

Long-form versions of the gotchas summarized in SKILL.md. Each was learned the hard way;
dates mark when it was confirmed on this machine.

## Dev server gets slow as the app grows (expected, not a regression)

`next dev` compiles each route **on-demand on first visit**, so early on (few routes)
clicks are snappy, but as the module graph grows the first-hit compile balloons and
"clicking through screens" feels sluggish **even on localhost**. This is dev-mode
overhead, *not* a code perf bug - don't optimize components before ruling it out.

**Diagnose from container logs, not by guessing:**
`docker logs personal-dash-web-dev-1 --tail 120 | grep -iE "compil|GET|ms"`. The tell:

```
○ Compiling /objectives ...
✓ Compiled /objectives in 49.9s     ← first visit pays the compile
GET /objectives 200 in 50902ms      ← that click took 51s
GET /objectives 200 in 2616ms       ← same route again, already compiled → fast
```

First-visit spikes of 25-50s with warm repeats dropping to low seconds = on-demand
compilation, the normal dev tradeoff. Fixes, in order of leverage: **(1)** a production
build eliminates on-demand compilation entirely (best when the user just wants the app
to feel fast to *use*; costs the instant hot-reload loop); **(2)** keep the dev loop but
cut compile time - the repo must live on the WSL2 Linux filesystem, not `/mnt/c`.

**Historical (`/mnt/c` era, now done - apps live in `~/projects/*`):** the old layout
paid two extra taxes: the `./:/app` bind mount spanned the Windows→Linux boundary (slow
I/O reading thousands of module files) and `WATCHPACK_POLLING: "true"` polled
continuously (steady CPU). On WSL-native paths, native inotify works - omit polling.
Observed on Aro, 2026-07-03.

## Turbopack does not hot-reload across a /mnt/c bind mount

`WATCHPACK_POLLING` is **webpack-only**; Turbopack's watcher gets no events across a
Windows bind mount and has **no polling fallback**, so it serves stale cached modules
and hot-reload silently stops. Verified on finance-proj (Next 15.5.20): the edit reached
the container's file, Turbopack even logged "✓ Compiled", yet served OLD content on a
full navigation. On a Windows-mounted repo, prefer `next dev` (webpack). Irrelevant on
WSL-native paths.

## Screenshots time out during a hot-reload update (extension-era)

Moved to `chrome-extension-legacy.md` - extension-specific; ui-check screenshots
render a fresh page load, unaffected by HMR-in-flight.

## Confirm hot-reload end-to-end without a reload

Edit a visible string (e.g. an `<h1>`), wait ~6-8s for the recompile, then re-read that
element's `textContent` **in the same tab without navigating**. If it changed on its
own, HMR is live through the tunnel (Cloudflare proxies the HMR WebSocket). Revert the
marker - it should revert live too.

## File-upload flows (updated 2026-07-06)

Drive them headlessly: Playwright `set_input_files()` + fixture/on-disk export.
The old parked-tab workaround (extension-era) is archived in
`chrome-extension-legacy.md`.

## "Can't access it" → check DNS/host first

Before assuming a tunnel/app bug, confirm the public hostname actually **resolves** and
that `BASE_URL` matches the live host - a stale/typo'd host is
`DNS_PROBE_FINISHED_NXDOMAIN` and looks exactly like "can't access". Seen on
finance-proj: `BASE_URL=caudal.example.com` was NXDOMAIN; real host was
`budget.example.com`. Also verify the dashboard hostname targets the intended service
(`web:3000` dev vs `web-prod:3000`).

## A caching service worker silently breaks tunnel hot-reload

If the app's SW caches `_next/static` (cache-first / stale-while-revalidate), serving
the **dev** container through the tunnel makes it serve **old `next dev` chunks** (same
paths, new content) → stale UI that looks like "my changes aren't deploying".
Tell-tale: fresh on a just-loaded browser but stale on the installed PWA / another
device. Fix: keep the SW **no-cache** (install + push + share-target only, no `fetch`
cache - like Aro's `public/sw.js`); a cache-name bump + `activate` cleanup lets
installed clients self-heal. Diagnose with
`navigator.serviceWorker.getRegistrations()` + `caches.keys()` (a lingering
`*-shell-*` cache = the culprit).

**The fix is server-side, but an already-installed PWA won't pick it up on its own.**
A service worker persists on the device: after shipping the no-cache SW, the user's
installed PWA keeps running the old caching SW (browsers re-check `sw.js` roughly
daily), so they still see stale UI. First verify the container serves the good SW:
`curl -s http://localhost:<hostport>/sw.js` - no GET `caches.match` fetch handler.
If correct server-side, the remaining fix is device-side, one-time: remove and re-add
the PWA (or reload the site a couple of times / DevTools → Unregister). Confirmed on
finance-proj/Caudal, 2026-07-03.

**Speeding up prod WITHOUT reintroducing the dev-stale bug - gate the cache on the
`immutable` header, not on env.** Add cache-first for **`/_next/static/` only**, gating
`cache.put` on the response header `Cache-Control` containing **`immutable`**. Why this
is self-gating: a prod `next build` serves content-hashed chunks with
`Cache-Control: public, max-age=31536000, immutable` → cached, and a code change yields
a new URL, so a stale chunk is impossible. `next dev` serves unhashed files with
`no-store, must-revalidate` (no `immutable`) → gate skips → nothing cached in dev →
tunnel hot-reload stays fresh. One SW file works for both containers; no
`NODE_ENV`/hostname branch needed (the tunnel hostname is identical for dev and prod - 
the header can distinguish them, the hostname can't). **Verify against both live
containers before shipping:** grab an asset via
`wget -qO- http://localhost:3000/login | grep -oE '/_next/static/[^"]+\.js'`, then
`wget -S` it on the prod container (expect `immutable`) and the dev container (expect
`no-store`). Keep share-target/push handlers untouched; data stays online-only. Cache
name like `caudal-static-v1`; bump the suffix to purge old builds. Shipped on
finance-proj/Caudal 2026-07-04 (`public/sw.js` → `staticCacheFirst`).

## `ui-check --js` mechanics: async wrapper + argument order (2026-07-07)

Two traps hit while driving Aro's meal-plan scale sheets (both cost a retry):

**1. `await` needs an async IIFE wrapper.** `ui-check` passes your `--js` string to
Playwright `page.evaluate`, which wraps it as a **plain function body** - not a module,
not async. A bare top-level `await` (e.g. to wait for a Vaul drawer animation) throws
`SyntaxError: await is only valid in async functions and the top level bodies of
modules` before anything runs. Wrap it and RETURN the promise - `page.evaluate` awaits
a returned promise, so the resolved value still comes back:

```bash
# FAILS: bare await
--js "b.click(); await new Promise(r=>setTimeout(r,700)); return JSON.stringify(x)"
# WORKS: async IIFE, and you MUST return inside it
--js "(async()=>{ b.click(); await new Promise(r=>setTimeout(r,700)); return JSON.stringify(x); })()"
```

Forgetting the inner `return` -> resolves to `undefined` (empty result). Skip the
wrapper entirely for synchronous reads (`document.querySelector(...).textContent`) - a
bare expression is fine. A fixed `setTimeout` is a guess, not a signal; sturdier is to
poll for the expected element, but a fixed wait is acceptable for a one-off check.

**2. Positional `url` must come BEFORE `--login`.** `--login` is variadic/greedy
(`LOGIN_URL [PASSWORD] ...`), so it swallows a `url` placed after it ->
`error: the following arguments are required: url`. Put the page URL first, `--login`
last:

```bash
ui-check http://localhost:3007/nutrition/scale --width 390 --shot x.png \
  --js "..." --login http://localhost:3007/api/auth/login
```

**3. `--js` output is TRUNCATED, and chained `--login`s hit the app's own rate limit
(2026-07-21, Caudal).** A long JSON result comes back cut off, so an "enumerate everything"
payload is unreadable: return SHORT JSON (a count plus the top 3-5 entries) and split the
investigation across several calls. Those extra calls then trip the app's login limiter
(Caudal: 5/min) - reuse a `--cookie` for the follow-ups instead of `--login` each time.

**Reading `--js` string checks:** `innerText` returns text with CSS `text-transform`
applied, so an element styled `uppercase` (e.g. the `text-label` class) makes
`innerText.includes('Target')` return **false** - it's rendered `TARGET`. Match
case-insensitively or assert on `textContent` (raw, un-transformed) instead.

## `ui-check` error channel + exit codes: the silent-empty-stdout trap (fixed 2026-09-02)

**An agent-facing CLI that prints its errors to stderr hands the agent an empty stdout
and an ambiguous exit code - which the agent then misattributes.** `ui-check` used
argparse defaults, so a mistyped flag printed the usage block to **stderr** and exited
**2** - the same code it used for a page that failed to load. Both cases looked
identical to anything reading stdout:

| what happened | stdout | exit |
|---|---|---|
| typo'd `--selctor` | *(empty)* | 2 |
| app is down | `ERROR load: ...` | 2 |

An agent reading stdout concludes "the app is down" and goes off restarting a container
that was fine. Same family as the `sudo rtk` empty-file trap in RTK.md: a wrong answer
that looks like a real one.

Contract now (verified 2026-09-02, canonical `dev-system/scripts/ui-check` + deployed
copy both patched):

```
exit 0  pass
exit 1  a check failed          FAIL <parts> | <reasons>
exit 2  usage error             ERROR usage: <msg> + help: <valid flags>
exit 3  load/launch error       ERROR load: <first line>
```

Everything prints to **stdout**. Usage errors inline the valid flags so the agent
self-corrects in one turn instead of spending a round on `--help`. `--js` output and
long titles now truncate with `(truncated, N chars total; --full for all)` instead of
silently cutting at 200/40 chars - a bare `[:200]` on JSON hands back malformed data
the agent believes is complete.

**Generalize to every agent-facing CLI on this box** (`claude-spawner.py`, `tg-alert`,
the backup and check scripts): errors to stdout, one exit code per failure class, reject
unknown flags loudly with the valid set inlined, never truncate without a marker plus an
escape hatch, and state the zero explicitly (`overflow=0`, `sel[x]=MISSING`) so nothing
re-runs a command just to confirm an empty result meant "none". Distilled from
kunchenguid's AXI spec (principles 3-6) after it found this bug; the spec's TOON/npm/ESM
half doesn't apply to our Python one-liners.

## `ui-check --login` cannot authenticate a PROD container by IP (2026-08-24)

**The login POST returns 200, no `FAIL login` prints, and the page comes back rendered - 
showing the login screen.** Reads as "the app is healthy". Cause: the session cookie is
`Secure`, and Chrome only stores `Secure` cookies on a secure origin. `localhost`
counts; `http://172.20.0.x:3000` does not. This is the DEFAULT case when verifying prod
on this fleet, because prod is tunnel-only with no host port.

Two things that work - pull the cookie by hand, or verify against the dev container:

```bash
# A. extract the session token with curl, then send it as a header
TOK=$(curl -s -D- -o /dev/null -X POST http://<ip>:3000/api/login \
  -H 'content-type: application/json' -d "{\"password\":\"$PW\"}" \
  | grep -i '^set-cookie' | sed 's/.*caudal_session=\([^;]*\).*/\1/')
curl -H "Cookie: caudal_session=$TOK" http://<ip>:3000/<path>

# B. verify on the dev container over localhost, where --login works normally
ui-check http://localhost:3000/<path> --login http://localhost:3000/api/login
```

`curl -c cookie-jar` fails the same way - curl also refuses to store a `Secure` cookie
received over http. Cost when it bit: ~5 min of a false "the page loads fine".

## Two bugs a green headless check CANNOT see (both shipped)

**Orientation: a pixel-array parity test cannot catch a flipped canvas.** A WebGL preview built
with a full-screen triangle + `texelFetch(gl_FragCoord)` and `UNPACK_FLIP_Y_WEBGL=false` displays
every image VERTICALLY FLIPPED (the GL framebuffer is bottom-up) - yet `readPixels` reads it back
upright, so a parity test comparing `readPixels` against a server buffer passes **byte-exact**
while the on-screen canvas is upside-down. glow shipped this in P3 undetected because the grade
was position-INDEPENDENT; the P5 date stamp (position-driven) exposed it by landing top-right
instead of bottom-right.
- **Verify orientation with an ASYMMETRIC marker** - a red-top/blue-bottom PNG through the real
  upload path. Never trust a pixel-array parity test or symmetric content for orientation.
- **Fix DISPLAY-ONLY**: `-scale-y-100` on the canvas (and any `toDataURL` thumbnail), leaving the
  framebuffer GL-native so `readPixels == server` stays byte-exact. Do NOT set
  `UNPACK_FLIP_Y_WEBGL=true` - it inverts `texelFetch` row indexing and breaks parity and every
  position-driven effect. (glow, 2026-08-10)

**WebKit-only layout: `aspect-ratio` on a grid ITEM is not content height.** If the grid has
`max-height` + `overflow-y:auto`, WebKit distributes that max-height across the rows and the items
overflow and OVERLAP. Measured at 390px with 21 garments: the cell reported 111px while the row
was 37.14px = (320 − 6×10 gap) / 7. **Chromium paints it perfectly**, so Playwright-Chromium,
`ui-check` and `e2e/screens.py` all went green and the bug only appeared on the user's iPhone.
Fix: move the ratio to the PHOTO (`img { width:100%; aspect-ratio: … }`) so the item gets real
content height. (closet, 2026-07-29)

Both belong to the standing rule below: **headless cannot falsify a phone-reported rendering bug.**
Verify what headless CAN prove first, then spend the device round-trip.

## Never paste a password into a Playwright MCP call

The call and its arguments land in the transcript. Use `ui-check --login` (it reads the 0600 file
itself), or make the view reachable by URL. On caudal the deep link turned out to be the better
product anyway - a view worth verifying is usually a view worth linking. (2026-09-01)

## Headless WebGL2 parity gate (Playwright)

Driving real WebGL2 headlessly needs system Chrome with
`--use-gl=angle --use-angle=swiftshader --no-sandbox`, and the harness must be served over **HTTP**
(a tiny node http server) with `Content-Type: application/wasm` so `compileStreaming` works - 
`file://` fails. Reusable driver: glow's `scripts/parity/run-headless.mjs`.

Scope the gate by TRANSITIVITY rather than re-testing everything: once a shared spec is proven
identical to the GPU shader (maxErr 0), a new client-side path only needs a DECODE-parity gate
(browser `createImageBitmap` + black-flatten == `sharp .rotate()` + flatten) to guarantee client
output == server output. **Test only the new seam.** (glow, 2026-08-12)

## Next 16 dev verification traps (personal-dash, 2026-09-12, ~20 min)

- **`ui-check --shot` can capture the PWA BOOT SPLASH** while `--js` proves the page rendered (it
  races hydration). Trust the DOM eval; for a real pixel shot use `chrome-devtools-axi screenshot`.
- **Deleting a component file still in Turbopack's module graph 500s EVERY route** ("Failed to read
  source code") until the dev web container restarts. Stale cache, not a regression; prod builds clean.
- **`chrome-devtools-axi` opens at DESKTOP width.** `resize 390 844` before measuring phone layout.
  Log in first with `eval` + a `fetch('/api/auth/login', {method:'POST', ...})` from the page, then `open`.

## The one-line gotcha list (moved from SKILL.md)

- **Auth:** browser already has a session cookie; curl/`ui-check --login` must log in. Never hardcode the password. **Login path is app-specific** - Caudal is `/api/login`, the examples above use Aro's `/api/auth/login`; grep the app's `app/api` if a login 401s.
- **Same-container truth:** never spin up a second dev server - verify against the container the tunnel serves.
- **Screenshots**: `ui-check --shot` renders a fresh load (HMR-in-flight doesn't affect it) - but prefer measurements; images cost ~1-2k tokens to view.
- **Hot-reload E2E check:** edit a visible string, wait ~6-8s, re-read `textContent` in the same tab without navigating; revert after.
- **File-upload flows:** drive headlessly - Playwright `set_input_files()` with a fixture/on-disk export (ad-hoc script via Bash). The old parked-tab workaround is legacy (`references/chrome-extension-legacy.md`).
- **`ui-check` CANNOT verify a DB write.** Headless tears the browser down before an async Next
  server-action POST lands, so it only ever proves optimistic client state. Write-path E2E → Playwright
  MCP (needs `npx playwright install chrome` once; the MCP is pinned to the chrome channel). 2026-07-10, personal-dash, after two dead-end ui-check click attempts.
- **Next 16 dev: hydration silently DIES on any origin missing from `allowedDevOrigins`** (`next.config.ts`). SSR looks perfect but nothing is interactive - buttons take native focus yet have no React fiber/`__reactProps`. The only clue is a `ws://…/_next/webpack-hmr` handshake error in the console (easy to dismiss as HMR noise). Cause: the config listed only the tunnel host, so loading via `127.0.0.1:<port>` (the ui-check/Playwright path) was cross-origin-blocked. **List EVERY dev origin incl. `localhost` AND `127.0.0.1`** - fleet-wide for every Next-16 app verified at localhost. Cost ~15 min (recall, 2026-07-10).
- **Turbopack dev caches a failed resolution and emits stale `require is not defined`** after heavy hot-reloading (recall 2026-07-11: both detail pages 500'd after ~15 edits, looked like a real regression). Don't debug the code - `docker compose restart web` first when a page 500s with `require is not defined` or a stale "Can't resolve".
- **A boot splash steals your screenshots.** closet's `#splash` (hides on a `ready` event or a 7s fallback) sits over everything, and `wait_for_selector(".target")` fires early because the target is already ATTACHED behind it. Wait on the splash instead: `page.wait_for_selector("#splash", state="detached")`. (`elementFromPoint` checks also mis-fire - `#splash` is an id with an empty `className`.) Cost ~3 wasted iterations, 2026-07-13.
- **Self-signed HTTPS dev origins** (closet `https://localhost:5173`) fail headless Chrome with `ERR_CERT_AUTHORITY_INVALID`. For axi set `CHROME_DEVTOOLS_AXI_CHROME_ARGS="--ignore-certificate-errors"` BEFORE `start` (unproven here). Proven workaround: drive the uv-playwright interpreter directly with `chromium.launch(args=['--ignore-certificate-errors'])` + `new_context(ignore_https_errors=True)`. 2026-07-13.
- **"Can't access it":** check DNS/hostname + `BASE_URL` first (NXDOMAIN looks identical to a down app), then the tunnel's origin target.
- **Stale UI / "changes aren't deploying":** a caching service worker; keep the SW no-cache in dev, or gate caching on the `immutable` response header. Installed PWAs need a one-time re-add after the fix.
- **iOS:** HTTPS via Cloudflare is what enables PWA install + Web Push; `navigator.vibrate` unsupported - don't promise haptics.
- **You CAN screenshot - never tell the user you can't.** `ui-check --shot` and `chrome-devtools-axi screenshot <path>` both render on the box; use one and `SendUserFile` the PNG. The only real limit is a device-specific *rendering condition* headless Chromium can't reproduce (see next).
- **Safe-area insets don't exist headlessly.** Headless/desktop Chromium reports `env(safe-area-inset-*)` = **0**, so an iOS home-indicator / notch bug (a `viewport-fit=cover` fixed bottom bar mis-centering, etc.) will NOT show in a `ui-check`/Playwright screenshot - it looks fine there and only breaks on the real phone. To verify such a bug without the phone: **simulate the inset** by injecting the padding in the browser (`el.style.paddingBottom='34px'`) and assert the geometry (e.g. icon-block center == row center), then have the user confirm on the phone. Don't conclude "looks fine" from a headless shot for safe-area layout. (2026-07-11: recall bottom-nav centered on desktop, crammed on iPhone - this was why.)
- **A green headless measurement is NOT proof against a phone-reported bug - and it will argue with you.** WebKit-only paint bugs (a `fixed` bar that strands mid-document on a long page, or rides up under `backdrop-filter`) measure IDENTICALLY in Chromium before and after the fix, so the check passes in the broken state too. When the user reports it on-device, take the phone screenshot; treat headless as unable to falsify. Order of operations: verify what headless CAN prove (functional offline/SW install, precache contents, shell render, DOM geometry) BEFORE spending a device round-trip; then send the device-only cosmetics to the phone. Fixes + causes for these traps: `frontend-interaction-patterns` → `references/ios-layout-traps.md`. (2026-07-16 recall, 2026-07-20 superhuman-mvp.)

## Probes that lie (personal-dash, Aro, Shelf, 2026-09 and 2026-10)

- **`motion` animates through WAAPI**, so `el.style.transform` stays empty mid-flight. Probe
  `getComputedStyle(el).transform`, or a working animation reads as "never moved".
- **A date route may clamp its parameter.** Aro's `/nutrition?d=<future>` renders today, so a future-date probe shows
  today's data and looks like a stale build. Read the rendered date first, or probe only past or today dates.
- **Never `.remove()` a node React owns** (such as `#splash`) in a `ui-check --js` snippet: React's tree breaks and the
  next update throws `removeChild` errors that look like a component bug. Hide it with
  `style.setProperty('display','none')`.
- **Every page times out while `curl` works:** count server requests during the attempt
  (`rtk proxy docker logs <c> 2>&1 | grep -ac 'GET /'`). A request per frame is a client reload loop (a Next 16
  `turbopack.rules` entry for Tailwind did it in Shelf), not a slow page.
- **Playwright `ctx.request` does not send a `Secure` session cookie to `http://127.0.0.1`**, so API calls get 401 after
  a 200 login. Log in and call the API from the page with `page.evaluate(fetch)`.

## Slow tab switching in a force-dynamic Next 15 app (personal-dash)

Two costs stack: `staleTimes.dynamic` defaults to 0, and a `loading.tsx` skeleton adds a flat ~300 ms Suspense reveal.
Fix: full prefetch on the persistent nav links, `experimental.staleTimes: { dynamic: 30 }`, and re-prefetch the tabs
after `router.refresh()`, which wipes the prefetch cache.
