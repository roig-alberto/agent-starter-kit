# Measurement, wireframe matching, smoke checks, showing the user (steps 1 to 3)

## 1. Measurement principles (apply to every engine)

Phone-first apps must match wireframes exactly - **measure, don't eyeball**.
`getComputedStyle` / `scrollWidth` vs `clientWidth` give exact colors, spacing,
overflow; screenshots can't confirm a hex value or a 1px overflow (fine for a
settled-layout gut-check only). **Test at ~360-390px width** - most layout bugs only
appear at phone width. Ready-to-paste JS checks in
`references/measurement-snippets.md` (usable as `ui-check --js` payloads).
File-upload wizards: Playwright `set_input_files()` with an anonymized fixture (or an
on-disk export) drives the whole flow headlessly.

**In a dual-shell app (mobile + desktop branches toggled by CSS), `querySelector` lies - filter
to the VISIBLE match.** When one `{children}` is wrapped in two CSS-switched shells (the
`app-chrome.tsx` pattern), the desktop bar (`hidden … lg:block`) sits FIRST in the DOM, so at 390px
`querySelector('.thing')` returns the hidden desktop instance: `rect [0,0]`, reads as "the component
didn't render" when it's rendered perfectly. Always
`[...document.querySelectorAll('SEL')].filter(e => e.getBoundingClientRect().width > 0)`, never bare
`querySelector`. Corollary: counting the VISIBLE matches also proves you didn't duplicate the
component into both branches. (personal-dash 2026-07-23 - one wasted ui-check round, false negative
read as "didn't render".)

**Chrome-extension route: NOT used in this workflow** (the box is SSH/Remote-Control
driven; no desktop Chrome exists here). If the workflow ever changes, the old
extension flow + its parked-tab tricks are archived in
`references/chrome-extension-legacy.md`. **If ToolSearch finds NO `mcp__claude-in-chrome__*` tools**: the extension
isn't connected (needs desktop Chrome RUNNING with the extension linked - common when
driving via Remote Control from the phone). Don't fight it - use `ui-check`.

## 1b. Wireframe-matching loop (building to an exact design)

When wireframes exist they are the exact spec (new-app Phase 4 - pixel-close,
never reinterpret). The headless loop:

1. **Read the wireframe SOURCE** (`ui/*.html`/SVG), not a picture of it - exact hex,
   px, structure come free.
2. Iterate cheap: `ui-check <url> --selector <el> --js <check>` and compare the
   built page's computed values against the wireframe's stated ones (~30 tokens/pass).
3. Screenshot sparingly: `ui-check --shot /tmp/s.png --width 390` + Read costs
   ~1-2k tokens - take one at the start, after big changes, and for final sign-off,
   NOT per tweak.
4. Divergence from the wireframe = a defect to fix, not a judgment call. Watch the
   detail that carries quality: shadows, gradients, radii, spacing rhythm,
   empty/loading states (the repeatedly under-done list in new-app Phase 4).

## 1c. Side-by-side fidelity pass (design frame vs the running screen)

Comparing the live app against a REMEMBERED design catches nothing. Render the frame and the screen
in the same browser and compare them state by state; on recall (2026-07-13) this caught 3 real
drifts that reading the spec had missed (a reorder rule, a missing pass-marker, a wrong button
tone). Do this once per screen before calling a design implemented.

1. **Open the design frames** with `chrome-devtools-axi open file:///<abs>/<frames>.html` (axi
   allows `file://`; the old Playwright MCP blocked it). If a frame needs HTTP (fetch, modules),
   `python3 -m http.server <port>` in the frames dir (pick a FRESH port; a stale server from an
   earlier session may already hold the obvious one) and open `http://localhost:<port>/<frames>.html`. Web fonts load fine (the box has net), so typography is
   comparable rather than fallback-substituted.
2. **Screenshot ONE frame, not the whole sheet:** scroll it into view and crop to its box
   (`eval` its `getBoundingClientRect()`), or use `ui-check --shot` with a selector. Design
   tools emit frame ids that START WITH A DIGIT, which is an INVALID CSS selector (`#11-6a2` throws)
   - use an attribute selector: `[id="11-6a2"] > div[data-screen-label]`.
3. Shoot the live screen at the SAME width (390) and compare pairwise: spacing rhythm, tone/weight
   of each control, ordering rules, and every state the frame set covers (empty, loading, each
   filter). Anything measurable (hex, px) still goes through `--js`/computed styles - the images are
   for the things a measurement can't name.
4. Each divergence is a defect to fix or an explicitly recorded deviation, never a silent judgment
   call (§1b step 4).

Design frames often live OUTSIDE the repo - `<WINDOWS_HOME>/inbox/input-<feature>-<project>/`
(ENVIRONMENT.md); grep there before assuming a referenced wireframe doesn't exist.

## 2. HTTP smoke check (no browser)

"Does the route render / is my marker present". Pages are auth-gated - log in first:

```bash
J=/tmp/app.cookies
curl -s -c "$J" -X POST http://localhost:<hostport>/api/auth/login \
  -H 'Content-Type: application/json' -d '{"password":"<APP_PASSWORD>"}'
curl -s -b "$J" http://localhost:<hostport>/<route> -o /tmp/page.html -w "%{http_code}\n"
```

`<APP_PASSWORD>` comes from the user - never stored in this skill or committed. Client
sheet content (Vaul drawers) mounts on open - grep for it in the browser, not curl output.

## 3. Tell the user it's live

Same container is tunneled → once verified locally, it's already at the public
hostname. Tell the user to refresh. No deploy step.

**To SHOW the user, not just describe:** capture with `ui-check --shot <file>.png`,
then `SendUserFile` that PNG so it reaches them - `display: "render"` opens it inline
in the side panel, `status: "proactive"` pings their phone if they're away. Critical:
a shot you only `Read` yourself is NOT seen by the user (Read loads the image into YOUR
context, not theirs) - you must `SendUserFile` it. Do this when the user asks to see a
change ("show me", "send a screenshot", "does it look right?") or for a final visual
sign-off; keep measurements (not images) as the default verifier per the token rule above.
