# The phone shell checklist (apply at scaffold time, all of it)

Each line names the failure it prevents. The exit artifact is every box ticked in the app's first UI
commit. This is step 1 of `SKILL.md`.

- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`
- [ ] **`apple-mobile-web-app-status-bar-style` = `default`, never `black-translucent`.** On iOS 26
      standalone, black-translucent gives a full-screen web view whose layout viewport is short by the top
      inset (measurements in `references/history.md`). Every `position:fixed; bottom:*` bar floats that
      many px up until the first scroll. With `default` the page starts below the status bar and iOS
      paints that strip from `theme-color` (set it to the page background). Next.js:
      `appleWebApp: { statusBarStyle: "default" }`. Changing it needs a PWA **reinstall**.
- [ ] `theme-color` = the app background colour, because it IS the status bar colour under `default`.
- [ ] Body sized with `min-height: 100dvh`; never `height: 100%` on html/body/#root as the size that fixed
      bars depend on, because short pages strand the dock (`frontend-interaction-patterns`
      `references/ios-layout-traps.md` section 2).
- [ ] Safe-area spacing defined ONCE as CSS variables and used everywhere:
      `--top-space: calc(env(safe-area-inset-top) + 14px)` (headers) and
      `--dock-bottom: max(30px, calc(env(safe-area-inset-bottom) + 10px))` (dock, bottom toasts).
      Reference: agent-factory `web/src/styles.css`.
- [ ] Dock: `position: fixed; bottom: var(--dock-bottom)`, an opaque background, **no `backdrop-filter`**
      on the fixed element (it rides with scroll, ios-layout-traps section 4), and
      `transform: translateZ(0)` (stranding mid-fling, ios-layout-traps section 5). Page content gets
      `padding-bottom: calc(var(--dock-bottom) + <dock height> + gap)` from the SHELL, not per screen.
- [ ] `ResumeReseat` mounted once (copy: Shelf `components/pwa/resume-reseat.tsx`, from Aro). It heals the
      dock stranded mid-screen after the keyboard closes.
- [ ] Sheets with inputs follow `frontend-interaction-patterns` `references/sheets.md` (no autoFocus, vaul
      `repositionInputs={false}`, a fixed-height frame with an inner scroll).
- [ ] The launch probe from `references/launch-probe.md` is ready to paste. Do not leave it running.
