# Launch probe - phone readings without asking for screenshots

The probe sends the phone's viewport, safe-area, and dock numbers to the server log, so you can read them
yourself instead of asking for screenshots. It was first used in agent-factory 2026-10-13
(`web/src/lib/diag.ts`, `server/app.ts` `POST /api/diag`). It is temporary: remove both halves in the
commit that proves the fix.

## Client (call once before the app renders)

```ts
// TEMPORARY: iOS launch probe. Remove once the cause is known.
export function launchProbe() {
  const probe = document.createElement("div");
  probe.style.cssText =
    "position:fixed;top:0;left:0;width:0;height:0;visibility:hidden;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom) 0";
  document.body.append(probe);
  const read = (label: string) => {
    const vv = window.visualViewport;
    const dock = document.querySelector('nav[aria-label="Dock"]')?.getBoundingClientRect(); // your dock selector
    const cs = getComputedStyle(probe);
    void fetch("/api/diag", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        label,
        standalone: matchMedia("(display-mode: standalone)").matches,
        inner: [innerWidth, innerHeight],
        screen: [screen.width, screen.height],
        vv: vv && [Math.round(vv.width), Math.round(vv.height), Math.round(vv.offsetTop)],
        bodyH: Math.round(document.body.getBoundingClientRect().height),
        dvh: getComputedStyle(document.body).minHeight,
        safe: [cs.paddingTop, cs.paddingBottom],
        dockBottomGap: dock && Math.round(innerHeight - dock.bottom),
        dockTop: dock && Math.round(dock.top),
        scrollY: Math.round(scrollY),
        path: location.pathname,
        ua: navigator.userAgent,
      }),
    });
  };
  [0, 500, 2000].forEach((ms) => setTimeout(() => read(`launch+${ms}`), ms));
  addEventListener("scroll", () => read("first-scroll"), { once: true });
}
```

## Server (behind the app's auth; log only, capped)

Hono: `.post("/diag", async (c) => { console.log("DIAG", JSON.stringify(await c.req.json()).slice(0, 2000)); return c.json({ ok: true }); })`
Next.js: a route handler doing the same `console.log`. Never store it, never make it public.

## Reading it

```sh
journalctl -u <unit> --since "15 min ago" -q | grep -a DIAG | grep -v HeadlessChrome   # systemd service
rtk proxy docker logs <container> --since 15m 2>&1 | grep -a DIAG                       # container
```

Filter `standalone: true`, because browser-tab readings (Safari toolbars) are a different viewport. The
decisive reading from the first use is in `references/history.md`. Scroll a long page, because a page
that does not scroll never sends the `first-scroll` reading.
